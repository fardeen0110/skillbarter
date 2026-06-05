"""compatibility migration for messages columns used by dashboard

Revision ID: 20260605_000005
Revises: 20260517_000004
Create Date: 2026-06-05
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260605_000005"
down_revision = "20260517_000004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # No-op placeholder.
    # Kept intentionally empty to avoid further DB changes in case
    # the missing columns were already added elsewhere.
    pass


def downgrade() -> None:
    pass

