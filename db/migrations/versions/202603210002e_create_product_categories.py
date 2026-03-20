"""Create product_categories table

Revision ID: 202603210002e
Revises: 202603210001d
Create Date: 2026-03-21 11:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "202603210002e"
down_revision = "202603210001d"
branch_labels = None
depends_on = None


DEFAULT_CATEGORIES = [
    ("Awards", 1),
    ("Stationery", 2),
    ("Corporate Gifts", 3),
    ("Accessories", 4),
    ("Other", 5),
]


def upgrade() -> None:
    op.create_table(
        "product_categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False, unique=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    conn = op.get_bind()
    existing_categories = conn.execute(
        sa.text(
            """
            SELECT DISTINCT category
            FROM products
            WHERE category IS NOT NULL AND TRIM(category) <> ''
            ORDER BY category
            """
        )
    ).fetchall()

    seeded = {}
    for name, sort_order in DEFAULT_CATEGORIES:
        normalized = " ".join((name or "").strip().split())
        if normalized and normalized.lower() not in seeded:
            conn.execute(
                sa.text(
                    """
                    INSERT INTO product_categories (name, active, sort_order, created_at)
                    VALUES (:name, :active, :sort_order, CURRENT_TIMESTAMP)
                    """
                ),
                {"name": normalized, "active": True, "sort_order": sort_order},
            )
            seeded[normalized.lower()] = True

    for (category_name,) in existing_categories:
        normalized = " ".join((category_name or "").strip().split())
        if normalized and normalized.lower() not in seeded:
            conn.execute(
                sa.text(
                    """
                    INSERT INTO product_categories (name, active, sort_order, created_at)
                    VALUES (:name, :active, :sort_order, CURRENT_TIMESTAMP)
                    """
                ),
                {"name": normalized, "active": True, "sort_order": 99},
            )
            seeded[normalized.lower()] = True


def downgrade() -> None:
    op.drop_table("product_categories")
