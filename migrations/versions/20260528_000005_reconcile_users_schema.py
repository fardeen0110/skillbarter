"""reconcile users schema for production

Revision ID: 20260528_000005
Revises: 20260517_000004
Create Date: 2026-05-28 00:00:05
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260528_000005"
down_revision = "20260517_000004"
branch_labels = None
depends_on = None


def _column_names(table_name: str) -> set[str]:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    user_columns = _column_names("users")

    if "is_verified" not in user_columns:
        op.add_column(
            "users",
            sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        )

    if "is_admin" not in user_columns:
        op.add_column(
            "users",
            sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        )

    if "last_active_at" not in user_columns:
        op.add_column(
            "users",
            sa.Column(
                "last_active_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
        )


def downgrade() -> None:
    user_columns = _column_names("users")

    if "last_active_at" in user_columns:
        op.drop_column("users", "last_active_at")

    if "is_admin" in user_columns:
        op.drop_column("users", "is_admin")

    if "is_verified" in user_columns:
        op.drop_column("users", "is_verified")
