from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from alembic import op
import sqlalchemy as sa
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""add shortcut option for users

Revision ID: 027381bce97c
Revises: 6fc7886d665d
Create Date: 2025-01-14 12:14:00.814390

"""



# revision identifiers, used by Alembic.
revision: str = "027381bce97c"
down_revision: str = "6fc7886d665d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "user",
        sa.Column(
            "shortcut_enabled", sa.Boolean(), nullable=False, server_default="false"
        ),
    )


def downgrade() -> None:
    op.drop_column("user", "shortcut_enabled")
