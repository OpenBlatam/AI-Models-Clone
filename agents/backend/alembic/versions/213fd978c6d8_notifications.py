from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from alembic import op
import sqlalchemy as sa
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""notifications

Revision ID: 213fd978c6d8
Revises: 5fc1f54cc252
Create Date: 2024-08-10 11:13:36.070790

"""


# revision identifiers, used by Alembic.
revision: str = "213fd978c6d8"
down_revision: str = "5fc1f54cc252"
branch_labels: None = None
depends_on: None = None


def upgrade() -> None:
    op.create_table(
        "notification",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "notif_type",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.UUID(),
            nullable=True,
        ),
        sa.Column("dismissed", sa.Boolean(), nullable=False),
        sa.Column("last_shown", sa.DateTime(timezone=True), nullable=False),
        sa.Column("first_shown", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("notification")
