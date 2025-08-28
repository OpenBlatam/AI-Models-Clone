from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""Store Chat Retrieval Docs

Revision ID: 7ccea01261f6
Revises: a570b80a5f20
Create Date: 2023-10-15 10:39:23.317453

"""


# revision identifiers, used by Alembic.
revision = "7ccea01261f6"
down_revision = "a570b80a5f20"
branch_labels: None = None
depends_on: None = None


def upgrade() -> None:
    op.add_column(
        "chat_message",
        sa.Column(
            "reference_docs",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("chat_message", "reference_docs")
