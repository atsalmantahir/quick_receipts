
from datetime import datetime
from app import db
from sqlalchemy.dialects.postgresql import JSON

# Role model
class Role(db.Model):
    __tablename__ = 'roles'
    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    permissions = db.relationship('RolePermission', backref='role', lazy=True)

# RolePermission model
class RolePermission(db.Model):
    __tablename__ = 'role_permissions'
    role_permission_id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'), nullable=False)
    permission = db.Column(db.String(100), nullable=False)

# User model
class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'))

    role = db.relationship('Role', backref='users')

# Subscription model
class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    subscription_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    plan_type = db.Column(db.String(50), nullable=False)  # 'free_trial', 'monthly', 'yearly'
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    user = db.relationship('User', backref='subscriptions')
 
# Batch Model
class Batch(db.Model):
    __tablename__ = 'batches'  # Explicit table name (prevents conflicts)
    batch_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    status = db.Column(db.String(20), default='uploaded')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    receipts = db.relationship('Receipt', backref='batch')  # Now works

# Receipt Model (Fixed)
class Receipt(db.Model):
    __tablename__ = 'receipts'
    receipt_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    
    # ✅ Correct foreign key (matches Batch's table name)
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.batch_id'))  # Reference 'batches'
    
    confidence_score = db.Column(db.Float)
    is_flagged = db.Column(db.Boolean, default=False)
    receipt_date = db.Column(db.DateTime, nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    receipt_image_url = db.Column(db.String)
    is_ocr_extracted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # NEW fields for background processing
    ocr_status = db.Column(db.String(20), default='pending')  # 'pending', 'processing', 'done', 'failed'
    ocr_attempts = db.Column(db.Integer, default=0)
    last_ocr_attempt = db.Column(db.DateTime)
    ocr_error_message = db.Column(db.Text, nullable=True)

    user = db.relationship('User', backref='receipts')

class OcrBase(db.Model):
    __tablename__ = 'ocr_base'
    ocr_base_id = db.Column(db.Integer, primary_key=True)
    receipt_id = db.Column(db.Integer, db.ForeignKey('receipts.receipt_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    modified_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    modified_by = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

    receipt = db.relationship('Receipt', backref='ocr_bases')

class OcrDetails(db.Model):
    __tablename__ = 'ocr_details'
    ocr_details_id = db.Column(db.Integer, primary_key=True)
    ocr_base_id = db.Column(db.Integer, db.ForeignKey('ocr_base.ocr_base_id'), nullable=False)
    field_type = db.Column(db.String(100), nullable=False)  # e.g., 'total_amount', 'purchase_time'
    text_value = db.Column(db.String(255), nullable=False)  # Raw OCR value (e.g., '15:30:05', '836')
    normalized_value = db.Column(db.String(255))  # Normalized value if applicable (e.g., '836' instead of '836 JPY')
    confidence = db.Column(db.Float, nullable=False)  # Confidence score for this field (e.g., 0.98)

    ocr_base = db.relationship('OcrBase', backref='ocr_details')

# AuditLog model
class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    audit_log_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    action = db.Column(db.String(255), nullable=False)
    action_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(JSON)  # Use JSON instead of JSONB

    user = db.relationship('User', backref='audit_logs')

# Transaction model
class Transaction(db.Model):
    __tablename__ = 'transactions'
    transaction_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    receipt_id = db.Column(db.Integer, db.ForeignKey('receipts.receipt_id'))
    stripe_transaction_id = db.Column(db.String(255), unique=True, nullable=False)
    payment_status = db.Column(db.String(50))
    payment_method = db.Column(db.String(100))
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    transaction_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref='transactions')
    receipt = db.relationship('Receipt', backref='transactions')
