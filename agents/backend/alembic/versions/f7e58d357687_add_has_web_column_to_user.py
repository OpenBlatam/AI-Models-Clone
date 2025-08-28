from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from alembic import op
import sqlalchemy as sa
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""add has_web_login column to user

Revision ID: f7e58d357687
Revises: ba98eba0f66a
Create Date: 2024-09-07 20:20:54.522620

"""


# revision identifiers, used by Alembic.
revision = "f7e58d357687"
down_revision = "ba98eba0f66a"
branch_labels: None = None
depends_on: None = None


def upgrade() -> None:
    op.add_column(
        "user",
        sa.Column("has_web_login", sa.Boolean(), nullable=False, server_default="true"),
    )


def downgrade() -> None:
    op.drop_column("user", "has_web_login")
