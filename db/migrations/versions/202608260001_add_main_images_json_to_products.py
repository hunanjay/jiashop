"""Add main_images_json to products table

Revision ID: 202608260001
Revises: 202606260001
Create Date: 2026-08-26 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '202608260001'
down_revision = '202606260001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    if 'products' in inspector.get_table_names():
        columns = [c['name'] for c in inspector.get_columns('products')]
        if 'main_images_json' not in columns:
            op.add_column('products', sa.Column('main_images_json', sa.JSON(), nullable=True))


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    if 'products' in inspector.get_table_names():
        columns = [c['name'] for c in inspector.get_columns('products')]
        if 'main_images_json' in columns:
            op.drop_column('products', 'main_images_json')
