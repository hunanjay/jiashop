"""Initial migration

Revision ID: initial_001
Revises:
Create Date: 2026-03-20 23:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = "202603202350a"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("image_url", sa.String(length=255), nullable=True),
        sa.Column("category", sa.String(length=50), nullable=True),
        sa.Column("customization_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "orders",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("customer_name", sa.String(length=100), nullable=False),
        sa.Column("items_json", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=True),
        sa.Column("total_price", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("orders")
    op.drop_table("products")
