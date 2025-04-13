# controllers/batch_controller.py
from flask_restx import Namespace, Resource, fields
from flask import request, current_app
from app.models import Batch, Receipt, db
import os
import uuid
from .receipt_controller import process_single_file  # Reuse your existing logic

api = Namespace('batches', description='Batch operations')

upload_parser = api.parser()
upload_parser.add_argument('files', location='files', type=FileStorage, required=True, action='append')

@api.route('/')
class BatchController(Resource):
    @api.expect(upload_parser)
    def post(self):
        """Upload and process a batch of receipts"""
        args = upload_parser.parse_args()
        uploaded_files = args.get('files')

        # Create batch record
        new_batch = Batch(user_id=8)  # Hardcoded user for example
        db.session.add(new_batch)
        db.session.commit()

        # Process files asynchronously (use Celery in production)
        for file in uploaded_files:
            filename = f"batch_{new_batch.batch_id}_{secure_filename(file.filename)}"
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Process each file (reuse your existing code)
            receipts = process_single_file(file_path, new_batch.batch_id)
            
            # Update batch status
            new_batch.status = 'processing'
            db.session.commit()

        new_batch.status = 'completed'
        db.session.commit()

        return {'batch_id': new_batch.batch_id, 'status': new_batch.status}, 201

@api.route('/<int:batch_id>/export')
class BatchExport(Resource):
    def get(self, batch_id):
        """Export batch to Yayoi-compatible CSV"""
        batch = Batch.query.get_or_404(batch_id)
        receipts = Receipt.query.filter_by(batch_id=batch_id).all()

        # Generate CSV with ShiftJIS encoding
        csv_data = "Date,Amount (JPY),Vendor,Status\n"
        for receipt in receipts:
            date = receipt.receipt_date.strftime("%Y/%m/%d")
            amount = str(receipt.total_amount)
            status = "⚠️ CHECK" if receipt.is_flagged else "✅ OK"
            csv_data += f"{date},{amount},{receipt.vendor},{status}\n"

        # Use UTF-8 with BOM for Japanese Excel
        csv_data = '\ufeff' + csv_data
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename=batch_{batch_id}.csv"}
        )