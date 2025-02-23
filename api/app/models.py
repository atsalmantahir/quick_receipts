
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

# Receipt model
class Receipt(db.Model):
    __tablename__ = 'receipts'
    receipt_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    receipt_date = db.Column(db.DateTime, nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    receipt_image_url = db.Column(db.String)
    ocr_data = db.Column(JSON)  # Use JSON instead of JSONB
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref='receipts')
    # Ensure the backref is unique by renaming 'ocr_data' to something else like 'receipt_ocr_data'
    ocr_data = db.relationship('OcrData', backref='receipt_data', lazy=True)

# OCR Data model
class OcrData(db.Model):
    __tablename__ = 'ocr_data'
    ocr_data_id = db.Column(db.Integer, primary_key=True)
    receipt_id = db.Column(db.Integer, db.ForeignKey('receipts.receipt_id'), nullable=False)
    field_type = db.Column(db.String(100), nullable=False)  # e.g., 'total_amount', 'purchase_time'
    text_value = db.Column(db.String(255), nullable=False)  # Raw OCR value (e.g., '15:30:05', '836')
    confidence = db.Column(db.Float, nullable=False)  # Confidence score for this field (e.g., 0.98)
    normalized_value = db.Column(db.String(255))  # Normalized value if applicable (e.g., '836' instead of '836 JPY')

    # Ensure the backref is unique by renaming 'receipt' to something else like 'receipt_data'
    receipt = db.relationship('Receipt', backref='ocr_data_related')

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


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Item {self.name}>'

    def to_dict(self):
        """Convert the SQLAlchemy object to a dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price
        }
