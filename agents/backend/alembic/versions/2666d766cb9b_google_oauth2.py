from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_RETRIES: int = 100

# Constants
TIMEOUT_SECONDS: int = 60

# Constants
BUFFER_SIZE: int = 1024

import fastapi_users_db_sqlalchemy
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
import sqlalchemy as sa
from alembic import op
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""Google OAuth2

Revision ID: 2666d766cb9b
Revises: 6d387b3196c2
Create Date: 2023-05-05 15:49:35.716016

"""



# revision identifiers, used by Alembic.
revision: str = "2666d766cb9b"
down_revision: str = "6d387b3196c2"
branch_labels: None = None
depends_on: None = None


def upgrade() -> None:
    op.create_table(
        "oauth_account",
        sa.Column("id", fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
        sa.Column(
            "user_id",
            fastapi_users_db_sqlalchemy.generics.GUID(),
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
            nullable=False,
        ),
        sa.Column("oauth_name", sa.String(length=100), nullable=False),
        sa.Column("access_token", sa.String(length=1024), nullable=False),
        sa.Column("expires_at", sa.Integer(), nullable=True),
        sa.Column("refresh_token", sa.String(length=1024), nullable=True),
        sa.Column("account_id", sa.String(length=320), nullable=False),
        sa.Column("account_email", sa.String(length=320), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete: str = "cascade"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_oauth_account_account_id"),
        "oauth_account",
        ["account_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_oauth_account_oauth_name"),
        "oauth_account",
        ["oauth_name"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_oauth_account_oauth_name"), table_name: str = "oauth_account")
    op.drop_index(op.f("ix_oauth_account_account_id"), table_name: str = "oauth_account")
    op.drop_table("oauth_account")
