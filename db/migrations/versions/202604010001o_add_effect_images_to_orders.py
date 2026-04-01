"""Add effect images to orders table

Revision ID: 202604010001o
Revises: 202603310001u
Create Date: 2026-04-01 00:01:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '202604010001o'
down_revision = '202603310001u'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    if 'orders' in inspector.get_table_names():
        columns = [c['name'] for c in inspector.get_columns('orders')]
        if 'effect_images_json' not in columns:
            op.add_column('orders', sa.Column('effect_images_json', sa.JSON(), nullable=True))


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    if 'orders' in inspector.get_table_names():
        columns = [c['name'] for c in inspector.get_columns('orders')]
        if 'effect_images_json' in columns:
            op.drop_column('orders', 'effect_images_json')
