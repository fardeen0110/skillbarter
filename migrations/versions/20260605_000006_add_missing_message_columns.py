"""add missing message columns to messages table

Revision ID: 20260605_000006
Revises: 20260517_000004
Create Date: 2026-06-05
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260605_000006"
down_revision = "20260517_000004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # These columns exist in backend/models.py Message.
    # The production DB is missing them (runtime error: UndefinedColumn: message_type).
    op.add_column("messages", sa.Column("message_type", sa.String(length=20), nullable=False, server_default="text"))
    op.add_column("messages", sa.Column("attachment_filename", sa.String(length=255), nullable=True))
    op.add_column("messages", sa.Column("attachment_content_type", sa.String(length=120), nullable=True))
    op.add_column("messages", sa.Column("attachment_data", sa.LargeBinary(), nullable=True))
    op.add_column("messages", sa.Column("attachment_storage_path", sa.String(length=255), nullable=True))
    op.add_column("messages", sa.Column("attachment_public_url", sa.String(length=500), nullable=True))
    op.add_column("messages", sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("messages", sa.Column("read_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("messages", "read_at")
    op.drop_column("messages", "delivered_at")
    op.drop_column("messages", "attachment_public_url")
    op.drop_column("messages", "attachment_storage_path")
    op.drop_column("messages", "attachment_data")
    op.drop_column("messages", "attachment_content_type")
    op.drop_column("messages", "attachment_filename")
    op.drop_column("messages", "message_type")

