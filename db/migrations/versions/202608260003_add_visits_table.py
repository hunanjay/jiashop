"""Add visits table

Revision ID: 202608260003
Revises: 202608260002
Create Date: 2026-08-26 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '202608260003'
down_revision = '202608260002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    if 'visits' not in inspector.get_table_names():
        op.create_table(
            'visits',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('device_id', sa.String(length=64), nullable=False),
            sa.Column('path', sa.String(length=255)),
            sa.Column('ip', sa.String(length=45)),
            sa.Column('user_agent', sa.String(length=255)),
            sa.Column('created_at', sa.DateTime()),
        )
        op.create_index('ix_visits_device_id', 'visits', ['device_id'])
        op.create_index('ix_visits_created_at', 'visits', ['created_at'])


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    if 'visits' in inspector.get_table_names():
        op.drop_table('visits')
