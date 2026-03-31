"""Single consolidated schema migration

Revision ID: 202603210005h
Revises:
Create Date: 2026-03-21 15:40:00.000000
"""

from datetime import datetime
import uuid

from alembic import op
import sqlalchemy as sa
from werkzeug.security import generate_password_hash


revision = "202603210005h"
down_revision = None
branch_labels = None
depends_on = None


DEFAULT_ROLES = ["Guest", "User", "Admin", "SuperAdmin"]
DEFAULT_ADMIN = {
    "username": "superadmin",
    "email": "loganjian@outlook.com",
    "phone": "13341398479",
    "password": "superadmin123",
}


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    if not inspector.has_table("roles"):
        op.create_table(
            "roles",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("name", sa.String(length=50), nullable=False, unique=True),
        )

    if not inspector.has_table("users"):
        op.create_table(
            "users",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("username", sa.String(length=80), nullable=False, unique=True),
            sa.Column("email", sa.String(length=120), nullable=False, unique=True),
            sa.Column("phone", sa.String(length=30), nullable=True, unique=True),
            sa.Column("password_hash", sa.String(length=255), nullable=False),
            sa.Column("role_id", sa.Integer(), nullable=False),
            sa.Column("session_id", sa.String(length=36), nullable=True, unique=True),
            sa.Column("access_token", sa.Text(), nullable=True),
            sa.Column("access_token_expires_at", sa.DateTime(), nullable=True),
            sa.Column("refresh_token", sa.Text(), nullable=True),
            sa.Column("refresh_token_expires_at", sa.DateTime(), nullable=True),
            sa.Column("last_login_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["role_id"], ["roles.id"]),
            sa.PrimaryKeyConstraint("id"),
        )

    if not inspector.has_table("audit_logs"):
        op.create_table(
            "audit_logs",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.String(length=36), nullable=True),
            sa.Column("action", sa.String(length=255), nullable=False),
            sa.Column("resource_id", sa.String(length=100), nullable=True),
            sa.Column("timestamp", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        )

    if not inspector.has_table("products"):
        op.create_table(
            "products",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("price", sa.Float(), nullable=False),
            sa.Column("stock", sa.Integer(), nullable=False),
            sa.Column("status", sa.String(length=20), nullable=False),
            sa.Column("image_url", sa.Text(), nullable=True),
            sa.Column("category", sa.String(length=50), nullable=True),
            sa.Column("customization_json", sa.JSON(), nullable=True),
            sa.Column("owner_id", sa.String(length=36), nullable=True),
            sa.Column("sales_count", sa.Integer(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )

    if not inspector.has_table("product_categories"):
        op.create_table(
            "product_categories",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("name", sa.String(length=100), nullable=False, unique=True),
            sa.Column("active", sa.Boolean(), nullable=False),
            sa.Column("sort_order", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
        )

    if not inspector.has_table("customers"):
        op.create_table(
            "customers",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("company_name", sa.String(length=120), nullable=False),
            sa.Column("purchaser", sa.String(length=80), nullable=True),
            sa.Column("phone", sa.String(length=30), nullable=True),
            sa.Column("shipping_address", sa.String(length=255), nullable=True),
            sa.Column("owner_id", sa.String(length=36), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )

    if not inspector.has_table("orders"):
        op.create_table(
            "orders",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("customer_name", sa.String(length=100), nullable=False),
            sa.Column("items_json", sa.JSON(), nullable=False),
            sa.Column("status", sa.String(length=20), nullable=True),
            sa.Column("total_price", sa.Float(), nullable=False),
            sa.Column("customer_id", sa.String(length=36), nullable=True),
            sa.Column("customer_phone", sa.String(length=30), nullable=True),
            sa.Column("shipping_address", sa.String(length=255), nullable=True),
            sa.Column("custom_logo_url", sa.Text(), nullable=True),
            sa.Column("design_file_url", sa.Text(), nullable=True),
            sa.Column("remarks", sa.Text(), nullable=True),
            sa.Column("owner_id", sa.String(length=36), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
            sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )

    roles_table = sa.table(
        "roles",
        sa.column("id", sa.Integer()),
        sa.column("name", sa.String(length=50)),
    )
    users_table = sa.table(
        "users",
        sa.column("id", sa.String(length=36)),
        sa.column("username", sa.String(length=80)),
        sa.column("email", sa.String(length=120)),
        sa.column("phone", sa.String(length=30)),
        sa.column("password_hash", sa.String(length=255)),
        sa.column("role_id", sa.Integer()),
        sa.column("session_id", sa.String(length=36)),
        sa.column("access_token", sa.Text()),
        sa.column("access_token_expires_at", sa.DateTime()),
        sa.column("refresh_token", sa.Text()),
        sa.column("refresh_token_expires_at", sa.DateTime()),
        sa.column("last_login_at", sa.DateTime()),
        sa.column("created_at", sa.DateTime()),
    )

    existing_roles = {
        row[0]
        for row in conn.execute(sa.select(roles_table.c.name))
    }
    missing_roles = [{"name": role_name} for role_name in DEFAULT_ROLES if role_name not in existing_roles]
    if missing_roles:
        conn.execute(roles_table.insert(), missing_roles)

    admin_role_id = conn.execute(
        sa.select(roles_table.c.id).where(roles_table.c.name == "Admin")
    ).scalar_one()

    admin_password_hash = generate_password_hash(DEFAULT_ADMIN["password"], method="pbkdf2:sha256")
    admin_row = conn.execute(
        sa.select(users_table.c.id, users_table.c.role_id).where(users_table.c.username == DEFAULT_ADMIN["username"])
    ).first()

    if admin_row is None:
        conn.execute(
            users_table.insert(),
            {
                "id": str(uuid.uuid4()),
                "username": DEFAULT_ADMIN["username"],
                "email": DEFAULT_ADMIN["email"],
                "phone": DEFAULT_ADMIN["phone"],
                "password_hash": admin_password_hash,
                "role_id": admin_role_id,
                "session_id": None,
                "access_token": None,
                "access_token_expires_at": None,
                "refresh_token": None,
                "refresh_token_expires_at": None,
                "last_login_at": None,
                "created_at": datetime.utcnow(),
            },
        )
    elif admin_row.role_id != admin_role_id:
        conn.execute(
            users_table.update()
            .where(users_table.c.username == DEFAULT_ADMIN["username"])
            .values(role_id=admin_role_id)
        )


def downgrade() -> None:
    op.drop_table("orders")
    op.drop_table("customers")
    op.drop_table("product_categories")
    op.drop_table("products")
    op.drop_table("audit_logs")
    op.drop_table("users")
    op.drop_table("roles")
