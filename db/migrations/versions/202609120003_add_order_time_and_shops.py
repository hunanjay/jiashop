"""Add order_time to commission_records and shops table

Revision ID: 202609120003
Revises: 202609120002
Create Date: 2026-09-12 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '202609120003'
down_revision = '202609120002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    columns = [c['name'] for c in inspector.get_columns('commission_records')]
    if 'order_time' not in columns:
        op.add_column('commission_records', sa.Column('order_time', sa.DateTime()))

    if 'shops' not in inspector.get_table_names():
        op.create_table(
            'shops',
            sa.Column('id', sa.String(length=36), primary_key=True),
            sa.Column('name', sa.String(length=120), nullable=False),
            sa.Column('owner_id', sa.String(length=36), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('created_at', sa.DateTime()),
            sa.UniqueConstraint('owner_id', 'name', name='uq_shops_owner_name'),
        )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    if 'shops' in inspector.get_table_names():
        op.drop_table('shops')

    columns = [c['name'] for c in inspector.get_columns('commission_records')]
    if 'order_time' in columns:
        op.drop_column('commission_records', 'order_time')
