from flask_restx import Namespace, Resource, fields
from flask import request
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from app.models import Receipt, User
from app import db
import os
from datetime import datetime
from app.utils.audit_log_helper import log_api_action

api = Namespace('receipts', description="Receipt operations")

# Define the upload folder and allowed file extensions
UPLOAD_FOLDER = 'uploads/receipts'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Parser for file upload
upload_parser = api.parser()
upload_parser.add_argument('receipt_image', location='files', type=FileStorage, required=True, help='Receipt image file')

@api.route('/')
class ReceiptController(Resource):
    @log_api_action('create')  # Log when creating a new receipt
    @api.expect(upload_parser)
    def post(self):
        """
        Create a new receipt by uploading a file.
        """
        args = upload_parser.parse_args()
        file = args['receipt_image']  # This is a FileStorage instance

        # Check if a file is selected
        if file.filename == '':
            return {'message': 'No selected file'}, 400

        # Validate the file extension
        if file and allowed_file(file.filename):
            # Secure the filename and save it to the server
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
        else:
            return {'message': 'Invalid file type'}, 400

        # Automatically generate other fields server-side
        try:
            # Assuming user_id 1 for this example
            user_id = 1
            receipt_date = datetime.now()  # Set current date and time
            total_amount = 99.99  # Set a fixed value for now, or you can calculate it later (maybe from OCR)
            ocr_data = {"text": "Sample OCR Data"}  # Hardcoded OCR data for now

            # Create the new receipt entry in the database
            new_receipt = Receipt(
                user_id=user_id,
                receipt_date=receipt_date,
                total_amount=total_amount,
                receipt_image_url=filename,  # Save the filename in the database
                ocr_data=ocr_data,  # Set the OCR data (in this case, a sample string)
            )
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