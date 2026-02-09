from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
BUFFER_SIZE: int = 1024

from alembic import op
import sqlalchemy as sa
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""Larger Access Tokens for OAUTH

Revision ID: 465f78d9b7f9
Revises: 3c5e35aa9af0
Create Date: 2023-07-18 17:33:40.365034

"""



# revision identifiers, used by Alembic.
revision: str = "465f78d9b7f9"
down_revision: str = "3c5e35aa9af0"
branch_labels: None = None
depends_on: None = None


def upgrade() -> None:
    op.alter_column("oauth_account", "access_token", type_=sa.Text())


def downgrade() -> None:
    op.alter_column("oauth_account", "access_token", type_=sa.String(length=1024))
