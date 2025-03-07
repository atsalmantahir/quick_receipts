from flask_restx import Namespace, Resource, fields
from flask import request, abort
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from app.models import Receipt, User
from app import db
import os
from datetime import datetime
from google.cloud import documentai
from google.api_core.client_options import ClientOptions

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


@api.route('/<int:receipt_id>')
class ReceiptDetailController(Resource):
    def get(self, receipt_id):
        """
        Get a receipt by ID
        """
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
        """
        Delete a receipt by ID
        """
        receipt = Receipt.query.get(receipt_id)
        if not receipt:
            abort(404, description="Receipt not found")

        try:
            # Delete the file from the uploads folder
            upload_folder = os.path.join(self.app.root_path, 'uploads', 'receipts')
            file_path = os.path.join(upload_folder, receipt.receipt_image_url)
            if os.path.exists(file_path):
                os.remove(file_path)

            # Delete the receipt from the database
            db.session.delete(receipt)
            db.session.commit()
            return {'message': 'Receipt deleted successfully'}, 200

        except Exception as e:
            db.session.rollback()
            self.app.logger.error(f"Error deleting receipt: {str(e)}")
            return {'message': 'Failed to delete receipt'}, 500


@api.route('/<int:receipt_id>/ocr')
class PerformOCRController(Resource):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api=api, *args, **kwargs)
        # Access the app object from the API object
        self.app = api.app

        # Set the environment variable for Google Cloud credentials
        credentials_path = os.path.join(self.app.root_path, 'config', 'quick-receipts-450104-ed1765c72967.json')
        print(f"Credentials path: {credentials_path}")  # Debugging
        if not os.path.exists(credentials_path):
            raise FileNotFoundError(f"Credentials file not found at: {credentials_path}")
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

    def post(self, receipt_id):
        """
        Perform OCR on a receipt image using Google Document AI
        """
        receipt = Receipt.query.get(receipt_id)
        if not receipt:
            abort(404, description="Receipt not found")

        try:
            # Get the file path from the receipt image URL
            upload_folder = os.path.join(self.app.root_path, 'uploads', 'receipts')
            file_path = os.path.join(upload_folder, receipt.receipt_image_url)

            # Check if the file exists
            if not os.path.exists(file_path):
                abort(404, description="Receipt image file not found")

            # Perform OCR using Google Document AI
            ocr_results = self.perform_ocr_with_document_ai(file_path)

            return {
                'message': 'OCR completed successfully',
                'receipt_id': receipt_id,
                'ocr_results': ocr_results,
            }, 200
        except Exception as e:
            return {'message': f"Failed to perform OCR, {e}"}, 500

    def perform_ocr_with_document_ai(self, file_path):
        """
        Perform OCR using Google Document AI
        """
        # Google Document AI configuration
        project_id = 'quick-receipts-450104'  # Replace with your Google Cloud project ID
        location = 'us'  # Replace with your processor location
        processor_id = 'f9f60237ff49ce2d'  # Replace with your processor ID

        # Determine mime_type based on the file extension
        if file_path.endswith('.pdf'):
            mime_type = 'application/pdf'
        elif file_path.endswith('.png'):
            mime_type = 'image/png'
        else:
            raise ValueError("Unsupported file type. Only PDF and PNG files are supported.")

        # Process the document using Google Document AI
        document = self.online_process(project_id, location, processor_id, file_path, mime_type)

        # Extract entities from the document
        entities_data = self.extract_entities(document)

        # Format the OCR results to match the expected structure
        ocr_results = []
        for entity in entities_data:
            ocr_results.append({
                'type': entity['type'],
                'text_value': entity['text_value'],
                'normalized_value': entity['normalized_value'] or '',
                'confidence': entity['confidence']})

        return ocr_results

    def online_process(self, project_id: str, location: str, processor_id: str, file_path: str, mime_type: str):
        """
        Process a document using Google Document AI
        """
        opts = {"api_endpoint": f"{location}-documentai.googleapis.com"}
        documentai_client = documentai.DocumentProcessorServiceClient(client_options=opts)
        resource_name = documentai_client.processor_path(project_id, location, processor_id)

        with open(file_path, "rb") as image:
            image_content = image.read()

        raw_document = documentai.RawDocument(content=image_content, mime_type=mime_type)
        request = documentai.ProcessRequest(name=resource_name, raw_document=raw_document)
        result = documentai_client.process_document(request=request)
        return result.document

    def extract_entities(self, document):
        """
        Extract entities from the Document AI response
        """
        entities_data = []
        for entity in document.entities:
            entity_data = {
                "type": entity.type_,
                "text_value": entity.text_anchor.content or entity.mention_text,
                "normalized_value": entity.normalized_value.text if entity.normalized_value else None,
            }
            entities_data.append(entity_data)

            # Extract Nested Entities (if any)
            for prop in entity.properties:
                nested_entity_data = {
                    "type": prop.type_,
                    "text_value": prop.text_anchor.content or prop.mention_text,
                    "normalized_value": prop.normalized_value.text if prop.normalized_value else None,
                }
                entities_data.append(nested_entity_data)

        return entities_data