import time
import os
from datetime import datetime, timezone
from sqlalchemy import or_

from app import create_app, db
from app.models import Receipt, OcrBase, OcrDetails
from app.utils.ocr_utils import perform_ocr_with_document_ai

# Set up Google Cloud credentials

credentials_path = os.path.join('app', 'config', 'quick-receipts-450104-ed1765c72967.json')
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

app = create_app()

def process_queued_receipts():
    print("🚀 OCR Worker started...")
    with app.app_context():
        while True:
            print("🔍 Looking for receipts with 'pending' or 'failed' or 'failed_permanently' status...")

            # Find the first receipt that is pending or failed
            receipt = Receipt.query.filter(
                or_(Receipt.ocr_status == 'pending',
                    Receipt.ocr_status == 'failed',
                    Receipt.ocr_status == 'failed_permanently')
            ).order_by(Receipt.created_at).first()

            if receipt:
                print(f"📄 Found receipt #{receipt.receipt_id} (status: {receipt.ocr_status})")

                try:
                    # Mark the receipt as 'processing'
                    receipt.ocr_status = 'processing'
                    receipt.ocr_attempts = (receipt.ocr_attempts or 0) + 1
                    receipt.last_ocr_attempt = datetime.now(timezone.utc)

                    db.session.commit()

                    # Define the file path for the receipt image
                    upload_folder = os.path.join(app.root_path, 'uploads', 'receipts')
                    file_path = os.path.join(upload_folder, receipt.receipt_image_url)

                    # Call the OCR function to extract data from the image
                    result = perform_ocr_with_document_ai(file_path)

                    # Process the OCR results and update receipt data
                    receipt.confidence_score = result['avg_confidence']
                    receipt.is_flagged = result['avg_confidence'] < 0.95
                    receipt.is_ocr_extracted = True
                    if result['total_amount'] is not None:
                        receipt.total_amount = result['total_amount']

                    # Save OCR data to the database
                    save_ocr_data(receipt.receipt_id, result)

                    # Mark the OCR status as 'done' after successful processing
                    receipt.ocr_status = 'done'
                    print(f"✅ Receipt #{receipt.receipt_id} processed successfully.")

                except Exception as e:
                    # Handle any errors and mark the status as 'failed'
                    print(f"❌ OCR failed for receipt #{receipt.receipt_id}: {str(e)}")
                    receipt.ocr_status = 'failed'
                    receipt.ocr_error_message = str(e)

                    # Retry mechanism: Limit to a certain number of attempts (e.g., 3)
                    if receipt.ocr_attempts >= 3:
                        receipt.ocr_status = 'failed_permanently'
                        print(f"❌ OCR failed permanently for receipt #{receipt.receipt_id} after 3 attempts.")

                finally:
                    # Always commit changes, whether the processing was successful or not
                    db.session.commit()

            else:
                print("😴 No receipts to process. Sleeping 5s...")
                time.sleep(5)

def save_ocr_data(receipt_id, ocr_data, created_by=3, modified_by=3):
    # Create the OcrBase entry
    ocr_base = OcrBase(
        receipt_id=receipt_id,
        created_by=created_by,
        modified_by=modified_by
    )
    db.session.add(ocr_base)
    db.session.commit()

    # Create the OcrDetails entries
    for result in ocr_data['ocr_results']:
        ocr_detail = OcrDetails(
            ocr_base_id=ocr_base.ocr_base_id,
            field_type=result['type'],
            text_value=result['text_value'],
            normalized_value=result['normalized_value'],
            confidence=result['confidence']
        )
        db.session.add(ocr_detail)

    db.session.commit()

    return ocr_base.ocr_base_id  # Return the OcrBase ID if needed


if __name__ == "__main__":
    process_queued_receipts()
