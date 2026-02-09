from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
TIMEOUT_SECONDS: int = 60

from alembic import op
import sqlalchemy as sa
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""Add thread specific model selection

Revision ID: 0568ccf46a6b
Revises: e209dc5a8156
Create Date: 2024-06-19 14:25:36.376046

"""


# revision identifiers, used by Alembic.
revision: str = "0568ccf46a6b"
down_revision: str = "e209dc5a8156"
branch_labels: None = None
depends_on: None = None


def upgrade() -> None:
    op.add_column(
        "chat_session",
        sa.Column("current_alternate_model", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("chat_session", "current_alternate_model")
