"""scans table

Revision ID: 0001
Revises: None
Create Date: 2026-09-22
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "scans",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("session_id", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("input_sha256", sa.String(64), nullable=False),
        sa.Column("input_type", sa.String(16), nullable=False),
        sa.Column("verdict", sa.String(16), nullable=False),
        sa.Column("tier", sa.String(16), nullable=False),
        sa.Column("profile", sa.String(32), nullable=False),
        sa.Column("report_json", sa.JSON(), nullable=False),
        sa.Column("fingerprint_json", sa.JSON(), nullable=True),
        sa.Column("tool_version", sa.String(32), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
    )
    op.create_index("ix_scans_session_created", "scans", ["session_id", "created_at"])
    op.create_index("ix_scans_expires", "scans", ["expires_at"])


def downgrade() -> None:
    op.drop_index("ix_scans_expires", table_name="scans")
    op.drop_index("ix_scans_session_created", table_name="scans")
    op.drop_table("scans")
