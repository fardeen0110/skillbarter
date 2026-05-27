"""add storage urls

Revision ID: 20260517_000004
Revises: 20260517_000003
Create Date: 2026-05-17 00:00:04
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260517_000004"
down_revision = "20260517_000003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("user_profiles", sa.Column("avatar_storage_path", sa.String(length=255), nullable=True))
    op.add_column("user_profiles", sa.Column("avatar_public_url", sa.String(length=500), nullable=True))
    op.add_column("messages", sa.Column("attachment_storage_path", sa.String(length=255), nullable=True))
    op.add_column("messages", sa.Column("attachment_public_url", sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column("messages", "attachment_public_url")
    op.drop_column("messages", "attachment_storage_path")
    op.drop_column("user_profiles", "avatar_public_url")
    op.drop_column("user_profiles", "avatar_storage_path")
