import cv2
import os
import numpy as np
from flask_restx import Namespace, Resource, fields
from flask import request, abort
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from app.models import Receipt, OcrBase, OcrDetails
from app import db
import tempfile
from datetime import datetime
from google.cloud import documentai
from pdf2image import convert_from_path

api = Namespace('receipts', description="Receipt operations")

# Parser for file upload
upload_parser = api.parser()
upload_parser.add_argument(
    'receipt_image',
    location='files',
    type=FileStorage,
    required=True,
    help='Receipt image file (png, jpg, jpeg, gif, pdf)'
)
upload_parser.add_argument(
    'debug',
    location='args',
    type=bool,
    required=False,
    default=False,
    help='Enable debug mode for segmentation (saves annotated image and crops)'
)

def detect_receipt_contours(image):
    """Improved contour detection with area and aspect ratio filtering"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 200)
    
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
    
    receipts = []
    min_receipt_area = 50000

    for contour in contours:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        
        if len(approx) == 4 and cv2.contourArea(contour) > min_receipt_area:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / float(h)
            
            if 0.2 <= aspect_ratio <= 5:
                receipts.append(image[y:y+h, x:x+w])

    return receipts

def grid_segment_receipts(image, rows, cols):
    """Grid-based segmentation for fallback processing"""
    h, w = image.shape[:2]
    return [
        image[i*h//rows:(i+1)*h//rows, j*w//cols:(j+1)*w//cols]
        for i in range(rows)
        for j in range(cols)
    ]

def segment_receipts(image):
    """Segment receipts using contour detection and fallback to grid segmentation."""
    receipts = detect_receipt_contours(image)
    return receipts if receipts else grid_segment_receipts(image, 2, 3)

def debug_segmentation(image, filename, upload_folder):
    """
    Debug segmentation: performs receipt detection similar to your Jupyter code,
    draws bounding boxes on the original image, saves the annotated image and
    each cropped receipt in a dedicated debug output folder.
    """
    # Create a copy for annotation
    annotated = image.copy()
    
    # Preprocessing: convert to grayscale, blur and edge detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 200)
    
    # Find and sort contours
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
    
    receipts = []
    min_receipt_area = 50000
    count = 0
    
    # Create a debug output folder based on the filename
    base_name = os.path.splitext(filename)[0]
    debug_folder = os.path.join(upload_folder, 'debug_' + base_name)
    os.makedirs(debug_folder, exist_ok=True)
    
    # Process each contour
    for i, contour in enumerate(contours):
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        area = cv2.contourArea(contour)
        if len(approx) == 4 and area > min_receipt_area:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / float(h)
            if 0.2 <= aspect_ratio <= 5:
                count += 1
                # Draw rectangle on the annotated image
                cv2.rectangle(annotated, (x, y), (x+w, y+h), (0, 255, 0), 3)
                # Crop the receipt and add to list
                receipt_crop = image[y:y+h, x:x+w]
                receipts.append(receipt_crop)
                # Save cropped receipt image
                crop_filename = os.path.join(debug_folder, f'receipt-{count}.jpg')
                cv2.imwrite(crop_filename, receipt_crop)
    
    # Save the annotated image
    annotated_filename = os.path.join(debug_folder, f'{base_name}_annotated.jpg')
    cv2.imwrite(annotated_filename, annotated)
    
    # If no receipts are detected, fallback to grid segmentation
    if not receipts:
        receipts = grid_segment_receipts(image, 2, 3)
    
    return receipts

def convert_pdf_to_images(pdf_path):
    """PDF to image conversion with automatic tempfile cleanup"""
    # Adjust poppler_path if needed
    with tempfile.NamedTemporaryFile(delete=False) as temp_pdf:
        return convert_from_path(pdf_path, poppler_path=r'C:\Program Files\poppler-23.11.0\Library\bin')

@api.route('/')
class ReceiptController(Resource):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api=api, *args, **kwargs)
        self.app = api.app

    @api.expect(upload_parser)
    def post(self):
        args = upload_parser.parse_args()
        file = args['receipt_image']
        debug_mode = args.get('debug', False)

        if not file.filename:
            return {'message': 'No selected file'}, 400

        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[-1].lower()

        if file_extension not in {'png', 'jpg', 'jpeg', 'pdf'}:
            return {'message': 'Unsupported file type'}, 400

        upload_folder = os.path.join(self.app.root_path, 'uploads', 'receipts')
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)

        try:
            file.save(file_path)
            receipt_images = []

            if file_extension == 'pdf':
                for page in convert_pdf_to_images(file_path):
                    temp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
                    page.save(temp_img.name)
                    # Read image and segment (use debug segmentation if requested)
                    img = cv2.imread(temp_img.name)
                    if debug_mode:
                        receipt_images.extend(debug_segmentation(img, filename, upload_folder))
                    else:
                        receipt_images.extend(segment_receipts(img))
                    os.unlink(temp_img.name)
            else:
                img = cv2.imread(file_path)
                if debug_mode:
                    receipt_images = debug_segmentation(img, filename, upload_folder)
                else:
                    receipt_images = segment_receipts(img)

            saved_receipts = []
            for i, img in enumerate(receipt_images):
                ext = filename.rsplit('.', 1)[-1]
                new_filename = f"{filename.rsplit('.', 1)[0]}_{i+1}.{ext}"
                cv2.imwrite(os.path.join(upload_folder, new_filename), img)
                
                receipt = Receipt(
                    user_id=8,
                    receipt_date=datetime.now(),
                    total_amount=99.99,
                    receipt_image_url=new_filename,
                    is_ocr_extracted=False
                )
                db.session.add(receipt)
                saved_receipts.append(new_filename)

            db.session.commit()
            return {'message': 'Receipts processed', 'saved_receipts': saved_receipts}, 201

        except Exception as e:
            self.app.logger.error(f"Processing error: {str(e)}")
            return {'message': f"Processing failed: {str(e)}"}, 500

    def get(self):
        receipts = Receipt.query.all()
        return [{
            'receipt_id': receipt.receipt_id, 
            'user_id': receipt.user_id,
            'receipt_image_url': receipt.receipt_image_url,
            'is_ocr_extracted': receipt.is_ocr_extracted,
            'total_amount': str(receipt.total_amount)
        } for receipt in receipts], 200

@api.route('/<int:receipt_id>')
class ReceiptDetailController(Resource):
    def get(self, receipt_id):
        receipt = Receipt.query.get(receipt_id) or abort(404, "Receipt not found")
        return {
            'receipt_id': receipt.receipt_id,
            'user_id': receipt.user_id,
            'image_url': receipt.receipt_image_url,
            'total': str(receipt.total_amount),
            'date': receipt.receipt_date.isoformat()
        }, 200

    def delete(self, receipt_id):
        receipt = Receipt.query.get(receipt_id) or abort(404, "Receipt not found")
        
        try:
            file_path = os.path.join(
                self.app.root_path, 'uploads', 'receipts', receipt.receipt_image_url
            )
            if os.path.exists(file_path):
                os.remove(file_path)
            
            db.session.delete(receipt)
            db.session.commit()
            return {'message': 'Receipt deleted'}, 200
        except Exception as e:
            db.session.rollback()
            self.app.logger.error(f"Deletion error: {str(e)}")
            return {'message': 'Deletion failed'}, 500

@api.route('/<int:receipt_id>/ocr')
class PerformOCRController(Resource):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api=api, *args, **kwargs)
        self.app = api.app
        cred_path = os.path.join(self.app.root_path, 'config', 'quick-receipts-credentials.json')
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path

    def post(self, receipt_id):
        receipt = Receipt.query.get(receipt_id) or abort(404, "Receipt not found")
        file_path = os.path.join(self.app.root_path, 'uploads', 'receipts', receipt.receipt_image_url)

        if not os.path.exists(file_path):
            abort(404, "Image file missing")

        try:
            ocr_results = self._process_ocr(file_path)
            ocr_base = OcrBase(
                receipt_id=receipt_id,
                created_by=8,
                modified_by=8
            )
            db.session.add(ocr_base)
            db.session.flush()

            db.session.bulk_insert_mappings(OcrDetails, [{
                'ocr_base_id': ocr_base.ocr_base_id,
                'field_type': r['type'],
                'text_value': r['text_value'],
                'normalized_value': r['normalized_value'],
                'confidence': r['confidence']
            } for r in ocr_results])

            receipt.is_ocr_extracted = True
            db.session.commit()
            return {'message': 'OCR completed', 'results': ocr_results}, 200

        except Exception as e:
            db.session.rollback()
            self.app.logger.error(f"OCR error: {str(e)}")
            return {'message': f"OCR failed: {str(e)}"}, 500

    def get(self, receipt_id):
        ocr_base = OcrBase.query.filter_by(receipt_id=receipt_id).first() or abort(404, "OCR data missing")
        details = OcrDetails.query.filter_by(ocr_base_id=ocr_base.ocr_base_id).all()
        
        return {
            'ocr_base': {
                'id': ocr_base.ocr_base_id,
                'created_by': ocr_base.created_by,
                'modified_by': ocr_base.modified_by
            },
            'details': [{
                'type': d.field_type,
                'text': d.text_value,
                'normalized': d.normalized_value,
                'confidence': d.confidence
            } for d in details]
        }, 200

    def _process_ocr(self, file_path):
        """Centralized OCR processing method"""
        doc = self._google_docai_process(file_path)
        return [self._parse_entity(e) for e in doc.entities] + [
            self._parse_entity(p) 
            for e in doc.entities 
            for p in e.properties
        ]

    def _google_docai_process(self, file_path):
        """Document AI processing wrapper"""
        client = documentai.DocumentProcessorServiceClient(client_options={
            'api_endpoint': 'us-documentai.googleapis.com'
        })
        
        with open(file_path, "rb") as f:
            return client.process_document(
                request=documentai.ProcessRequest(
                    name=client.processor_path('quick-receipts-450104', 'us', 'f9f60237ff49ce2d'),
                    raw_document=documentai.RawDocument(
                        content=f.read(),
                        mime_type=self._get_mime_type(file_path)
                    )
                )
            ).document

    def _get_mime_type(self, path):
        """Determine MIME type from file extension"""
        return {
            'pdf': 'application/pdf',
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg'
        }.get(path.split('.')[-1].lower(), 'application/octet-stream')

    def _parse_entity(self, entity):
        """Standardized entity parsing"""
        return {
            'type': entity.type_,
            'text_value': entity.text_anchor.content or entity.mention_text,
            'normalized_value': entity.normalized_value.text if entity.normalized_value else None,
            'confidence': entity.confidence
        }
