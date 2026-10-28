"""align student schema

Revision ID: ea936fee8ae0
Revises: 0b19cd5bb3f8
Create Date: 2026-10-28 20:00:49.479238

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ea936fee8ae0"
down_revision: str | Sequence[str] | None = "0b19cd5bb3f8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("students") as batch_op:
        batch_op.alter_column(
            "full_name",
            existing_type=sa.VARCHAR(length=20),
            type_=sa.String(length=120),
            existing_nullable=False,
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("students") as batch_op:
        batch_op.alter_column(
            "full_name",
            existing_type=sa.String(length=120),
            type_=sa.VARCHAR(length=20),
            existing_nullable=False,
        )
