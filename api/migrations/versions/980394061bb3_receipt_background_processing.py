"""receipt background processing

Revision ID: 980394061bb3
Revises: a5b8d3d3d52d
Create Date: 2025-04-14 02:22:17.853851

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '980394061bb3'
down_revision = 'a5b8d3d3d52d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('receipts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('ocr_status', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('ocr_attempts', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('last_ocr_attempt', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('ocr_error_message', sa.Text(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('receipts', schema=None) as batch_op:
        batch_op.drop_column('ocr_error_message')
        batch_op.drop_column('last_ocr_attempt')
        batch_op.drop_column('ocr_attempts')
        batch_op.drop_column('ocr_status')

    # ### end Alembic commands ###
