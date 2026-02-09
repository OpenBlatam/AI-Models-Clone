from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from alembic import op
import sqlalchemy as sa
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""added-prune-frequency

Revision ID: e209dc5a8156
Revises: 48d14957fe80
Create Date: 2024-06-16 16:02:35.273231

"""


revision = "e209dc5a8156"
down_revision = "48d14957fe80"
branch_labels = None  # type: ignore
depends_on = None  # type: ignore


def upgrade() -> None:
    op.add_column("connector", sa.Column("prune_freq", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("connector", "prune_freq")
