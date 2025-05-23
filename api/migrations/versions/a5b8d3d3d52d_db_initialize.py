"""db initialize

Revision ID: a5b8d3d3d52d
Revises: 
Create Date: 2025-04-11 23:05:02.349943

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a5b8d3d3d52d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('roles',
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.Column('role_name', sa.String(length=50), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('role_id'),
    sa.UniqueConstraint('role_name')
    )
    op.create_table('role_permissions',
    sa.Column('role_permission_id', sa.Integer(), nullable=False),
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.Column('permission', sa.String(length=100), nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['roles.role_id'], ),
    sa.PrimaryKeyConstraint('role_permission_id')
    )
    op.create_table('users',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('first_name', sa.String(length=100), nullable=True),
    sa.Column('last_name', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('last_login', sa.DateTime(), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['roles.role_id'], ),
    sa.PrimaryKeyConstraint('user_id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('audit_logs',
    sa.Column('audit_log_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('action', sa.String(length=255), nullable=False),
    sa.Column('action_timestamp', sa.DateTime(), nullable=True),
    sa.Column('details', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('audit_log_id')
    )
    op.create_table('batches',
    sa.Column('batch_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('batch_id')
    )
    op.create_table('subscriptions',
    sa.Column('subscription_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('plan_type', sa.String(length=50), nullable=False),
    sa.Column('start_date', sa.DateTime(), nullable=False),
    sa.Column('end_date', sa.DateTime(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('subscription_id')
    )
    op.create_table('receipts',
    sa.Column('receipt_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('batch_id', sa.Integer(), nullable=True),
    sa.Column('confidence_score', sa.Float(), nullable=True),
    sa.Column('is_flagged', sa.Boolean(), nullable=True),
    sa.Column('receipt_date', sa.DateTime(), nullable=False),
    sa.Column('total_amount', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('receipt_image_url', sa.String(), nullable=True),
    sa.Column('is_ocr_extracted', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['batch_id'], ['batches.batch_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('receipt_id')
    )
    op.create_table('ocr_base',
    sa.Column('ocr_base_id', sa.Integer(), nullable=False),
    sa.Column('receipt_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=False),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('modified_by', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['users.user_id'], ),
    sa.ForeignKeyConstraint(['modified_by'], ['users.user_id'], ),
    sa.ForeignKeyConstraint(['receipt_id'], ['receipts.receipt_id'], ),
    sa.PrimaryKeyConstraint('ocr_base_id')
    )
    op.create_table('transactions',
    sa.Column('transaction_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('receipt_id', sa.Integer(), nullable=True),
    sa.Column('stripe_transaction_id', sa.String(length=255), nullable=False),
    sa.Column('payment_status', sa.String(length=50), nullable=True),
    sa.Column('payment_method', sa.String(length=100), nullable=True),
    sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('transaction_date', sa.DateTime(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['receipt_id'], ['receipts.receipt_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('transaction_id'),
    sa.UniqueConstraint('stripe_transaction_id')
    )
    op.create_table('ocr_details',
    sa.Column('ocr_details_id', sa.Integer(), nullable=False),
    sa.Column('ocr_base_id', sa.Integer(), nullable=False),
    sa.Column('field_type', sa.String(length=100), nullable=False),
    sa.Column('text_value', sa.String(length=255), nullable=False),
    sa.Column('normalized_value', sa.String(length=255), nullable=True),
    sa.Column('confidence', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['ocr_base_id'], ['ocr_base.ocr_base_id'], ),
    sa.PrimaryKeyConstraint('ocr_details_id')
    )
    op.drop_table('batch')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('batch',
    sa.Column('batch_id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('status', sa.VARCHAR(length=20), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('batch_id', name='batch_pkey')
    )
    op.drop_table('ocr_details')
    op.drop_table('transactions')
    op.drop_table('ocr_base')
    op.drop_table('receipts')
    op.drop_table('subscriptions')
    op.drop_table('batches')
    op.drop_table('audit_logs')
    op.drop_table('users')
    op.drop_table('role_permissions')
    op.drop_table('roles')
    # ### end Alembic commands ###
