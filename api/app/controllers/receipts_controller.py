import cv2
import os
import numpy as np
from flask_restx import Namespace, Resource, fields
from flask import request, abort
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from app.models import Receipt, User, OcrBase, OcrDetails
from app import db
import tempfile
from datetime import datetime
from google.cloud import documentai
from pdf2image import convert_from_path


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

def extract_receipts_from_image(image_path):
    """Enhanced receipt extraction using contour detection"""
    image = cv2.imread(image_path)
    return detect_receipt_contours(image)


def four_point_transform(image, pts):
    """Perspective transform with error handling"""
    try:
        rect = pts.reshape(4, 2).astype("float32")  # Ensure float32 type
        
        # Order points: top-left, top-right, bottom-right, bottom-left
        rect_ordered = np.zeros((4, 2), dtype="float32")
        s = rect.sum(axis=1)
        rect_ordered[0] = rect[np.argmin(s)]  # Top-left
        rect_ordered[2] = rect[np.argmax(s)]  # Bottom-right
        
        diff = np.diff(rect, axis=1)
        rect_ordered[1] = rect[np.argmin(diff)]  # Top-right
        rect_ordered[3] = rect[np.argmax(diff)]  # Bottom-left

        # Validate dimensions
        (tl, tr, br, bl) = rect_ordered
        widthA = np.linalg.norm(br - bl)
        widthB = np.linalg.norm(tr - tl)
        maxWidth = max(int(widthA), int(widthB))

        heightA = np.linalg.norm(tr - br)
        heightB = np.linalg.norm(tl - bl)
        maxHeight = max(int(heightA), int(heightB))

        if maxWidth <= 0 or maxHeight <= 0:
            return None

        # Create destination matrix
        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype="float32")

        M = cv2.getPerspectiveTransform(rect_ordered, dst)
        warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
        return warped
    except:
        return None  # Skip invalid contours

def detect_receipt_contours(image):
    """Improved contour detection from the first code"""
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Edge detection using Canny
    edged = cv2.Canny(blurred, 50, 200)
    
    # Find contours
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter and sort contours by area (descending)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]  # Get top 10 largest
    receipts = []
    min_receipt_area = 50000  # Minimum area threshold

    for contour in contours:
        # Approximate the contour
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        
        # Check if contour is quadrilateral and sufficiently large
        if len(approx) == 4 and cv2.contourArea(contour) > min_receipt_area:
            # Validate aspect ratio
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / float(h)
            
            if 0.2 <= aspect_ratio <= 5:  # Valid aspect ratio range
                # Crop receipt
                receipt = image[y:y+h, x:x+w]
                receipts.append(receipt)

    return receipts

# --- Modified Segment Function ---

def segment_receipts(image):
    """
    Enhanced receipt segmentation using:
    1. Edge detection
    2. Contour analysis
    3. Perspective correction
    """
    receipts = detect_receipt_contours(image)
    
    # Fallback to grid segmentation if no contours found
    if not receipts:
        return grid_segment_receipts(image, rows=2, cols=3)
        
    return receipts

def grid_segment_receipts(image, rows, cols):
    """
    Splits the image into a grid of rows and columns for receipt detection.
    This approach assumes a regular grid structure where receipts are evenly spaced.
    """
    height, width, _ = image.shape
    cell_height = height // rows
    cell_width = width // cols
    
    receipt_images = []
    
    for i in range(rows):
        for j in range(cols):
            y1 = i * cell_height
            y2 = (i + 1) * cell_height
            x1 = j * cell_width
            x2 = (j + 1) * cell_width
            
            # Crop each cell region
            receipt_image = image[y1:y2, x1:x2]
            receipt_images.append(receipt_image)
    
    return receipt_images

def convert_pdf_to_images(pdf_path):
    """
    Convert a PDF to a list of images (one per page).
    """
    return convert_from_path(pdf_path)

@api.route('/')
class ReceiptController(Resource):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api=api, *args, **kwargs)
        self.app = api.app

    @api.expect(upload_parser)
    def post(self):
        args = upload_parser.parse_args()
        file = args['receipt_image']

        if file.filename == '':
            return {'message': 'No selected file'}, 400

        filename = secure_filename(file.filename)
        file_extension = filename.lower().rsplit('.', 1)[-1]

        if file_extension not in ['png', 'jpg', 'jpeg', 'pdf']:
            return {'message': 'Unsupported file type. Only PDF, PNG, JPG, and JPEG are supported'}, 400

        upload_folder = os.path.join(self.app.root_path, 'uploads', 'receipts')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        file_path = os.path.join(upload_folder, filename)

        try:
            file.save(file_path)
        except Exception as e:
            self.app.logger.error(f"Error saving file: {str(e)}")
            return {'message': f"Failed to save file {str(e)}"}, 500

        try:
            receipt_images = []

            if file_extension in ['png', 'jpg', 'jpeg']:
                image = cv2.imread(file_path)
                
                # Try segmentation using contours first
                receipt_images = segment_receipts(image)
                
                # If the segmentation isn't sufficient, use grid-based segmentation
                if not receipt_images:
                    receipt_images = grid_segment_receipts(image, rows=2, cols=3)  # Adjust grid size as needed

            elif file_extension == 'pdf':
                pdf_images = convert_pdf_to_images(file_path)
                for pdf_image in pdf_images:
                    temp_pdf_path = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
                    pdf_image.save(temp_pdf_path)
                    image = cv2.imread(temp_pdf_path.name)
                    receipt_images.extend(segment_receipts(image))  # Try contour segmentation

            # Save the extracted receipts into the database
            saved_receipts = []
            for i, receipt_image in enumerate(receipt_images):
                base_filename, ext = os.path.splitext(filename)
                extracted_filename = f"{base_filename}_{i+1}.jpg"
                extracted_image_path = os.path.join(upload_folder, extracted_filename)
                cv2.imwrite(extracted_image_path, receipt_image)

                # Store each receipt entry in the database
                user_id = 8  # Replace with actual user ID
                receipt_date = datetime.now()
                total_amount = 99.99  # Placeholder total amount

                new_receipt = Receipt(
                    user_id=user_id,
                    receipt_date=receipt_date,
                    total_amount=total_amount,
                    receipt_image_url=extracted_filename,
                    is_ocr_extracted=0  # Skip OCR
                )
                db.session.add(new_receipt)
                db.session.commit()

                saved_receipts.append(extracted_filename)

            return {
                'message': 'Receipts processed and saved successfully',
                'saved_receipts': saved_receipts
            }, 201

        except Exception as e:
            self.app.logger.error(f"Error processing receipt: {str(e)}")
            return {'message': f"Failed to process receipt: {str(e)}"}, 500

    def get(self):
        receipts = Receipt.query.all()
        return [{
            'receipt_id': receipt.receipt_id, 
            'user_id': receipt.user_id,
            'receipt_image_url': receipt.receipt_image_url,
            'is_ocr_extracted': receipt.is_ocr_extracted,
            'total_amount': str(receipt.total_amount)} for receipt in receipts], 200


    def perform_ocr_with_document_ai(self, file_path):
        """
        Perform OCR using Google Document AI
        """
        project_id = 'quick-receipts-450104'  # Replace with your Google Cloud project ID
        location = 'us'  # Replace with your processor location
        processor_id = 'f9f60237ff49ce2d'  # Replace with your processor ID

        # Determine mime_type based on the file extension
        if file_path.endswith('.pdf'):
            mime_type = 'application/pdf'
        elif file_path.endswith('.png'):
            mime_type = 'image/png'
        elif file_path.lower().endswith(('.jpg', '.jpeg')):
            mime_type = 'image/jpeg'  # Correct MIME type for JPEG images
        else:
            raise ValueError("Unsupported file type. Only PDF, PNG and JPG files are supported.")

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
                "confidence": entity.confidence if hasattr(entity, 'confidence') else 0.0
            }
            entities_data.append(entity_data)

            # Extract Nested Entities (if any)
            for prop in entity.properties:
                nested_entity_data = {
                    "type": prop.type_,
                    "text_value": prop.text_anchor.content or prop.mention_text,
                    "normalized_value": prop.normalized_value.text if prop.normalized_value else None,
                    "confidence": prop.confidence if hasattr(prop, 'confidence') else 0.0
                }
                entities_data.append(nested_entity_data)

        return entities_data

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
        self.app = api.app
        credentials_path = os.path.join(self.app.root_path, 'config', 'quick-receipts-450104-ed1765c72967.json')
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

            # Create OcrBase entry
            user_id = 8  # Replace with the actual user ID from the session or request
            ocr_base = OcrBase(
                receipt_id=receipt_id,
                created_by=user_id,
                modified_by=user_id
            )
            db.session.add(ocr_base)
            db.session.commit()

            # Create OcrDetails entries
            for result in ocr_results:
                ocr_detail = OcrDetails(
                    ocr_base_id=ocr_base.ocr_base_id,
                    field_type=result['type'],
                    text_value=result['text_value'],
                    normalized_value=result['normalized_value'],
                    confidence=result['confidence']
                )
                db.session.add(ocr_detail)

            # Update the Receipt table to mark OCR as extracted
            receipt.is_ocr_extracted = True
            db.session.commit()

            return {
                'message': 'OCR completed successfully',
                'receipt_id': receipt_id,
                'ocr_results': ocr_results,
            }, 200
        except Exception as e:
            db.session.rollback()
            self.app.logger.error(f"Error performing OCR: {str(e)}")
            return {'message': f"Failed to perform OCR, {str(e)}"}, 500

    def get(self, receipt_id):
        """
        Get the OCR base and associated OCR details for a receipt
        """
        receipt = Receipt.query.get(receipt_id)
        if not receipt:
            abort(404, description="Receipt not found")

        # Retrieve the OCR base record for the receipt
        ocr_base = OcrBase.query.filter_by(receipt_id=receipt_id).first()
        if not ocr_base:
            return {'message': 'OCR data not found for this receipt'}, 404

        # Retrieve the associated OCR details
        ocr_details = OcrDetails.query.filter_by(ocr_base_id=ocr_base.ocr_base_id).all()

        # Prepare the response data
        ocr_details_data = [{
            'field_type': detail.field_type,
            'text_value': detail.text_value,
            'normalized_value': detail.normalized_value,
            'confidence': detail.confidence
        } for detail in ocr_details]

        response_data = {
            'ocr_base': {
                'ocr_base_id': ocr_base.ocr_base_id,
                'receipt_id': ocr_base.receipt_id,
                'created_by': ocr_base.created_by,
                # 'created_at': ocr_base.created_at.isoformat(),
                'modified_by': ocr_base.modified_by
                # 'modified_at': ocr_base.modified_at.isoformat()
            },
            'ocr_details': ocr_details_data
        }

        return response_data, 200
    
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
        elif file_path.lower().endswith(('.jpg', '.jpeg')):
            mime_type = 'image/jpeg'  # Correct MIME type for JPEG images
        else:
            raise ValueError("Unsupported file type. Only PDF, JPG and PNG files are supported.")

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
                "confidence": entity.confidence if hasattr(entity, 'confidence') else 0.0  # Add confidence with a default value
            }
            entities_data.append(entity_data)

            # Extract Nested Entities (if any)
            for prop in entity.properties:
                nested_entity_data = {
                    "type": prop.type_,
                    "text_value": prop.text_anchor.content or prop.mention_text,
                    "normalized_value": prop.normalized_value.text if prop.normalized_value else None,
                    "confidence": prop.confidence if hasattr(prop, 'confidence') else 0.0  # Add confidence with a default value
                }
                entities_data.append(nested_entity_data)

        return entities_data