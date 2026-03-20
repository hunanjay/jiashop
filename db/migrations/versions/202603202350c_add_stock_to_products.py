"""Add stock column to products

Revision ID: add_stock_003
Revises: 202603202350b
Create Date: 2026-03-21 00:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = "202603202350c"
down_revision = "202603202350b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "products",
        sa.Column("stock", sa.Integer(), nullable=False, server_default=sa.text("10")),
    )


def downgrade() -> None:
    op.drop_column("products", "stock")
