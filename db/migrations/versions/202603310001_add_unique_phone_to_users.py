"""Add unique constraint to users.phone

Revision ID: 202603310001u
Revises: 202603210005h
Create Date: 2026-03-31 00:01:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "202603310001u"
down_revision = "202603260001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    if not inspector.has_table("users"):
        return

    existing_constraints = {constraint.get("name") for constraint in inspector.get_unique_constraints("users")}
    if "uq_users_phone" in existing_constraints:
        return

    with op.batch_alter_table("users") as batch_op:
        batch_op.create_unique_constraint("uq_users_phone", ["phone"])


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    if not inspector.has_table("users"):
        return

    existing_constraints = {constraint.get("name") for constraint in inspector.get_unique_constraints("users")}
    if "uq_users_phone" not in existing_constraints:
        return

    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_constraint("uq_users_phone", type_="unique")
