from flask_restx import Namespace, Resource, fields
from flask import request
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from app.models import Receipt, User
from app import db
import os
from datetime import datetime

# Create a namespace for receipts
api = Namespace('receipts', description="Receipt operations")

# Define the upload folder and allowed file extensions
UPLOAD_FOLDER = 'uploads/receipts'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Parser for file upload
upload_parser = api.parser()
upload_parser.add_argument(
    'receipt_image',
    location='files',
    type=FileStorage,
    required=True,
    help='Receipt image file (png, jpg, jpeg, gif, pdf)'
)

def allowed_file(filename):
    """
    Check if the file has an allowed extension.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api.route('/')
class ReceiptController(Resource):
    @api.expect(upload_parser)
    def post(self):
        """
        Create a new receipt by uploading a file.
        """
        args = upload_parser.parse_args()
        file = args['receipt_image']  # This is a FileStorage instance

        # Debugging: Print the file details
        print("Received file:", file.filename)
        print("Content-Type:", file.content_type)

        # Check if a file is selected
        if file.filename == '':
            return {'message': 'No selected file'}, 400

        # Validate the file extension
        if file and allowed_file(file.filename):
            # Secure the filename and save it to the server
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            try:
                file.save(file_path)
            except Exception as e:
                return {'message': f'Error saving file: {str(e)}'}, 500
        else:
            return {'message': 'Invalid file type'}, 400

        # Automatically generate other fields server-side
        try:
            # Assuming user_id 1 for this example
            user_id = 8
            receipt_date = datetime.now()  # Set current date and time
            total_amount = 99.99  # Set a fixed value for now, or you can calculate it later (maybe from OCR)

            # Create the new receipt entry in the database
            new_receipt = Receipt(
                user_id=user_id,
                receipt_date=receipt_date,
                total_amount=total_amount,
                receipt_image_url=filename,
            )

            # Create an OcrData instance and associate it with the receipt
            # ocr_data = OcrData(
            #     field_type="total_amount",
            #     text_value="99.99",
            #     confidence=0.98,
            #     normalized_value="99.99"
            # )
            # new_receipt.ocr_data_related.append(ocr_data)  # Use the correct backref name

            db.session.add(new_receipt)
            db.session.commit()
            return {'message': 'Receipt created successfully', 'receipt_id': new_receipt.receipt_id}, 201

        except Exception as e:
            db.session.rollback()
            return {'message': f'Error saving receipt: {str(e)}'}, 500

    def get(self):
        """
        Retrieve all receipts.
        """
        receipts = Receipt.query.all()
        return [{'receipt_id': receipt.receipt_id, 'user_id': receipt.user_id, 'total_amount': receipt.total_amount} for receipt in receipts], 200