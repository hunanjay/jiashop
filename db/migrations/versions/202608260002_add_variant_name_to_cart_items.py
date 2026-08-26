"""Add variant_name to cart_items table

Revision ID: 202608260002
Revises: 202608260001
Create Date: 2026-08-26 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '202608260002'
down_revision = '202608260001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    if 'cart_items' in inspector.get_table_names():
        columns = [c['name'] for c in inspector.get_columns('cart_items')]
        if 'variant_name' not in columns:
            op.add_column(
                'cart_items',
                sa.Column('variant_name', sa.String(length=200), nullable=False, server_default=''),
            )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    if 'cart_items' in inspector.get_table_names():
        columns = [c['name'] for c in inspector.get_columns('cart_items')]
        if 'variant_name' in columns:
            op.drop_column('cart_items', 'variant_name')
