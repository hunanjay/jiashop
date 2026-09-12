"""Add commission_records table

Revision ID: 202609120001
Revises: 202608260003
Create Date: 2026-09-12 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '202609120001'
down_revision = '202608260003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    if 'commission_records' not in inspector.get_table_names():
        op.create_table(
            'commission_records',
            sa.Column('id', sa.String(length=36), primary_key=True),
            sa.Column('shop_name', sa.String(length=120), nullable=False),
            sa.Column('product_name', sa.String(length=120), nullable=False),
            sa.Column('product_image', sa.Text()),
            sa.Column('order_no', sa.String(length=100), nullable=False),
            sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
            sa.Column('amount', sa.Float(), nullable=False),
            sa.Column('commission', sa.Float(), nullable=False),
            sa.Column('owner_id', sa.String(length=36), sa.ForeignKey('users.id')),
            sa.Column('created_at', sa.DateTime()),
            sa.Column('updated_at', sa.DateTime()),
        )
        op.create_index('ix_commission_records_owner_id', 'commission_records', ['owner_id'])


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    if 'commission_records' in inspector.get_table_names():
        op.drop_table('commission_records')
