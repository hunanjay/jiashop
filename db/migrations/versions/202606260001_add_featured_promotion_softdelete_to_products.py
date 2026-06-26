"""add is_featured, is_promotion, deleted_at to products

Revision ID: 202606260001
Revises: 202606240002
Branch Labels: None
Depends On: None

"""
from alembic import op
import sqlalchemy as sa


revision = '202606260001'
down_revision = '202606240002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('products', sa.Column('is_featured', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('products', sa.Column('is_promotion', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('products', sa.Column('deleted_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column('products', 'deleted_at')
    op.drop_column('products', 'is_promotion')
    op.drop_column('products', 'is_featured')
