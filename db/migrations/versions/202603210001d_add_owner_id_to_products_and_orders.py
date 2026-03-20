"""Add owner_id to products and orders

Revision ID: 202603210001d
Revises: 202603202350c
Create Date: 2026-03-21 09:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "202603210001d"
down_revision = "202603202350c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("products", sa.Column("owner_id", sa.String(length=36), nullable=True))
    op.create_foreign_key("fk_products_owner_id_users", "products", "users", ["owner_id"], ["id"])
    op.add_column("orders", sa.Column("owner_id", sa.String(length=36), nullable=True))
    op.create_foreign_key("fk_orders_owner_id_users", "orders", "users", ["owner_id"], ["id"])


def downgrade() -> None:
    op.drop_constraint("fk_orders_owner_id_users", "orders", type_="foreignkey")
    op.drop_column("orders", "owner_id")
    op.drop_constraint("fk_products_owner_id_users", "products", type_="foreignkey")
    op.drop_column("products", "owner_id")
