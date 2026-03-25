"""Add cart_items table

Revision ID: 202603250001
Revises: 202603210005h
Create Date: 2026-03-25 20:20:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "202603250001"
down_revision = "202603210005h"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    if not inspector.has_table("cart_items"):
        op.create_table(
            "cart_items",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("cart_token", sa.String(length=64), nullable=False),
            sa.Column("product_id", sa.String(length=36), nullable=False),
            sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        )
        op.create_index("ix_cart_items_cart_token", "cart_items", ["cart_token"], unique=False)


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    if inspector.has_table("cart_items"):
        op.drop_index("ix_cart_items_cart_token", table_name="cart_items")
        op.drop_table("cart_items")
