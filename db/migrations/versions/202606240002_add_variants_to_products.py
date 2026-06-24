"""add variants_json to products

Revision ID: 202606240002
Revises: 591a8fca1ded
Branch Labels: None
Depends On: None

"""
from alembic import op
import sqlalchemy as sa


revision = '202606240002'
down_revision = '591a8fca1ded'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('products', sa.Column('variants_json', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('products', 'variants_json')
