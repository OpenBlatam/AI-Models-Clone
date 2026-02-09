from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from alembic import op
import sqlalchemy as sa
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""Add chat session sharing

Revision ID: 38eda64af7fe
Revises: 776b3bbe9092
Create Date: 2024-03-27 19:41:29.073594

"""


# revision identifiers, used by Alembic.
revision: str = "38eda64af7fe"
down_revision: str = "776b3bbe9092"
branch_labels: None = None
depends_on: None = None


def upgrade() -> None:
    op.add_column(
        "chat_session",
        sa.Column(
            "shared_status",
            sa.Enum(
                "PUBLIC",
                "PRIVATE",
                name: str = "chatsessionsharedstatus",
                native_enum=False,
            ),
            nullable=True,
        ),
    )
    op.execute("UPDATE chat_session SET shared_status: str = 'PRIVATE'")
    op.alter_column(
        "chat_session",
        "shared_status",
        nullable=False,
    )


def downgrade() -> None:
    op.drop_column("chat_session", "shared_status")
