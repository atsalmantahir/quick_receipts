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

# Define allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

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
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api.route('/')
class ReceiptController(Resource):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api=api, *args, **kwargs)
        # Access the app object from the API object
        self.app = api.app

    @api.expect(upload_parser)
    def post(self):
        args = upload_parser.parse_args()
        file = args['receipt_image']

        if file.filename == '':
            return {'message': 'No selected file'}, 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Use the app's root path to construct the upload folder
            upload_folder = os.path.join(self.app.root_path, 'uploads', 'receipts')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            file_path = os.path.join(upload_folder, filename)

            # Log the file path for debugging
            self.app.logger.info(f"Saving file to: {file_path}")

            try:
                file.save(file_path)
            except Exception as e:
                self.app.logger.error(f"Error saving file: {str(e)}")
                return {'message': f"Failed to save file {str(e)}"}, 500
        else:
            return {'message': 'Invalid file type'}, 400

        try:
            user_id = 8
            receipt_date = datetime.now()
            total_amount = 99.99

            new_receipt = Receipt(
                user_id=user_id,
                receipt_date=receipt_date,
                total_amount=total_amount,
                receipt_image_url=filename,
            )

            db.session.add(new_receipt)
            db.session.commit()
            return {'message': 'Receipt created successfully', 'receipt_id': new_receipt.receipt_id}, 201

        except Exception as e:
            db.session.rollback()
            self.app.logger.error(f"Database error: {str(e)}")
            return {'message': 'Database error'}, 500

    def options(self):
        # Handle preflight request
        return {}, 200

    def get(self):
        receipts = Receipt.query.all()
        return [{
            'receipt_id': receipt.receipt_id, 
            'user_id': receipt.user_id,
            'receipt_image_url': receipt.receipt_image_url,
            'total_amount': str(receipt.total_amount)} for receipt in receipts], 200