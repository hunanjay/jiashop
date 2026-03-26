"""Add images_json to products table

Revision ID: 202603260001
Revises: 202603250001
Create Date: 2026-03-26 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '202603260001'
down_revision = '202603250001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Add images_json column to products table if it doesn't exist
    if 'products' in inspector.get_table_names():
        columns = [c['name'] for c in inspector.get_columns('products')]
        if 'images_json' not in columns:
            op.add_column('products', sa.Column('images_json', sa.JSON(), nullable=True))


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    if 'products' in inspector.get_table_names():
        columns = [c['name'] for c in inspector.get_columns('products')]
        if 'images_json' in columns:
            op.drop_column('products', 'images_json')
