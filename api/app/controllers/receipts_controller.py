import os
import cv2
import numpy as np
from flask_restx import Namespace, Resource
from flask import request, abort
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from datetime import datetime
import tempfile

from app import db
from app.models import Receipt, OcrBase, OcrDetails
from pdf2image import convert_from_path
from google.cloud import documentai
from app.utils.ocr_utils import perform_ocr_with_document_ai

api = Namespace('receipts', description="Receipt operations")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

upload_parser = api.parser()
upload_parser.add_argument(
    'receipt_image',
    location='files',
    type=FileStorage,
    required=True,
    help='Receipt image file (png, jpg, jpeg, gif, pdf)'
)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def detect_receipt_contours(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 200)
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

    receipts = []
    min_area = 50000

    for contour in contours:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        if len(approx) == 4 and cv2.contourArea(contour) > min_area:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / float(h)
            if 0.2 <= aspect_ratio <= 5:
                receipt = image[y:y+h, x:x+w]
                receipts.append(receipt)

    return receipts

def segment_receipts(image):
    receipts = detect_receipt_contours(image)
    return receipts or grid_segment_receipts(image, rows=2, cols=3)

def grid_segment_receipts(image, rows, cols):
    height, width, _ = image.shape
    cell_height = height // rows
    cell_width = width // cols

    return [
        image[i * cell_height:(i + 1) * cell_height, j * cell_width:(j + 1) * cell_width]
        for i in range(rows) for j in range(cols)
    ]

def convert_pdf_to_images(pdf_path):
    return convert_from_path(pdf_path)


# ---------------- Controller ---------------- #

@api.route('/')
class ReceiptController(Resource):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api=api, *args, **kwargs)
        self.app = api.app

    @api.expect(upload_parser)
    def post(self):
        args = upload_parser.parse_args()
        file = args['receipt_image']
        if not file or file.filename == '':
            return {'message': 'No selected file'}, 400

        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[-1].lower()

        if file_extension not in ALLOWED_EXTENSIONS:
            return {'message': 'Unsupported file type'}, 400

        upload_folder = os.path.join(self.app.root_path, 'uploads', 'receipts')
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)

        try:
            file.save(file_path)
        except Exception as e:
            return {'message': f"Failed to save file: {str(e)}"}, 500

        try:
            receipt_images = []
            if file_extension in ['png', 'jpg', 'jpeg']:
                image = cv2.imread(file_path)
                receipt_images = segment_receipts(image)
            elif file_extension == 'pdf':
                pdf_images = convert_pdf_to_images(file_path)
                for pdf_image in pdf_images:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_img:
                        pdf_image.save(temp_img.name)
                        image = cv2.imread(temp_img.name)
                        receipt_images.extend(segment_receipts(image))

            saved_receipts = []
            for i, receipt_img in enumerate(receipt_images):
                base_filename, _ = os.path.splitext(filename)
                extracted_filename = f"{base_filename}_{i+1}.jpg"
                extracted_path = os.path.join(upload_folder, extracted_filename)
                cv2.imwrite(extracted_path, receipt_img)

                new_receipt = Receipt(
                    user_id=3,  # TODO: Replace with actual user
                    receipt_date=datetime.now(),
                    total_amount=99.99,
                    receipt_image_url=extracted_filename,
                    is_ocr_extracted=0
                )
                db.session.add(new_receipt)
                db.session.commit()

                saved_receipts.append(extracted_filename)

            return {
                'message': 'Receipts processed and saved successfully',
                'saved_receipts': saved_receipts
            }, 201

        except Exception as e:
            db.session.rollback()
            return {'message': f"Failed to process receipt: {str(e)}"}, 500

    def get(self):
        # Extract pagination params from query string
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # Query with ordering by updated_at then created_at (both descending)
        paginated = Receipt.query.order_by(
            Receipt.updated_at.desc(),
            Receipt.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)

        results = [{
            'receipt_id': r.receipt_id,
            'user_id': r.user_id,
            'receipt_image_url': r.receipt_image_url,
            'is_ocr_extracted': r.is_ocr_extracted,
            'confidence_score': r.confidence_score,
            'total_amount': str(r.total_amount),
            'created_at': r.created_at.isoformat(),
            'updated_at': r.updated_at.isoformat()
        } for r in paginated.items]

        return {
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': paginated.page,
            'per_page': paginated.per_page,
            'receipts': results
        }, 200


@api.route('/<int:receipt_id>')
class ReceiptDetailController(Resource):
    def get(self, receipt_id):
        receipt = Receipt.query.get(receipt_id)
        if not receipt:
            abort(404, description="Receipt not found")

        return {
            'receipt_id': receipt.receipt_id,
            'user_id': receipt.user_id,
            'receipt_image_url': receipt.receipt_image_url,
            'total_amount': str(receipt.total_amount),
            'receipt_date': receipt.receipt_date.isoformat(),
        }, 200

    def delete(self, receipt_id):
        receipt = Receipt.query.get(receipt_id)
        if not receipt:
            abort(404, description="Receipt not found")

        upload_folder = os.path.join(self.api.app.root_path, 'uploads', 'receipts')
        file_path = os.path.join(upload_folder, receipt.receipt_image_url)
        if os.path.exists(file_path):
            os.remove(file_path)

        db.session.delete(receipt)
        db.session.commit()
        return {'message': 'Receipt deleted successfully'}, 200


@api.route('/<int:receipt_id>/flag')
class FlagReceipt(Resource):
    def post(self, receipt_id):
        receipt = Receipt.query.get_or_404(receipt_id)
        receipt.is_flagged = True
        db.session.commit()
        return {'message': 'Receipt flagged for review'}


@api.route('/flagged')
class FlaggedReceipts(Resource):
    def get(self):
        flagged = Receipt.query.filter_by(is_flagged=True).all()
        return [{
            'receipt_id': r.receipt_id,
            'confidence': r.confidence_score,
            'image_url': r.receipt_image_url
        } for r in flagged]


@api.route('/<int:receipt_id>/ocr')
class PerformOCRController(Resource):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api=api, *args, **kwargs)
        self.app = api.app
        credentials_path = os.path.join(self.app.root_path, 'config', 'quick-receipts-450104-ed1765c72967.json')
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

    def post(self, receipt_id):
        receipt = Receipt.query.get(receipt_id)
        if not receipt:
            abort(404, description="Receipt not found")

        upload_folder = os.path.join(self.app.root_path, 'uploads', 'receipts')
        file_path = os.path.join(upload_folder, receipt.receipt_image_url)

        if not os.path.exists(file_path):
            abort(404, description="Receipt image file not found")

        ocr_data = perform_ocr_with_document_ai(file_path)

        receipt.confidence_score = ocr_data['avg_confidence']
        receipt.is_flagged = ocr_data['avg_confidence'] < 0.95
        receipt.is_ocr_extracted = True
        if ocr_data['total_amount'] is not None:
            receipt.total_amount = ocr_data['total_amount']

        # Save OCR results to the database using the utility function
        self.save_ocr_data(receipt_id, ocr_data)
        db.session.commit()

        return {
            'message': 'OCR completed successfully',
            'receipt_id': receipt_id,
            'confidence': receipt.confidence_score,
            'is_flagged': receipt.is_flagged,
            'ocr_results': ocr_data['ocr_results'],
        }, 200

    def get(self, receipt_id):
        receipt = Receipt.query.get(receipt_id)
        if not receipt:
            abort(404, description="Receipt not found")

        ocr_base = OcrBase.query.filter_by(receipt_id=receipt_id).first()
        if not ocr_base:
            return {'message': 'OCR data not found'}, 404

        ocr_details = OcrDetails.query.filter_by(ocr_base_id=ocr_base.ocr_base_id).all()
        return {
            'ocr_base': {
                'ocr_base_id': ocr_base.ocr_base_id,
                'receipt_id': ocr_base.receipt_id,
                'created_by': ocr_base.created_by,
                'modified_by': ocr_base.modified_by
            },
            'ocr_details': [{
                'field_type': d.field_type,
                'text_value': d.text_value,
                'normalized_value': d.normalized_value,
                'confidence': d.confidence
            } for d in ocr_details]
        }, 200

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
