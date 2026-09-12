"""Add platform to commission_records

Revision ID: 202609120002
Revises: 202609120001
Create Date: 2026-09-12 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '202609120002'
down_revision = '202609120001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('commission_records')]

    if 'platform' not in columns:
        op.add_column(
            'commission_records',
            sa.Column('platform', sa.String(length=20), nullable=False, server_default='淘宝'),
        )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('commission_records')]

    if 'platform' in columns:
        op.drop_column('commission_records', 'platform')
