from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from alembic import op
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
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""Add api_key table
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

Revision ID: 79acd316403a
Revises: 904e5138fffb
Create Date: 2024-01-11 17:56:37.934381

"""


# revision identifiers, used by Alembic.
revision = "79acd316403a"
down_revision = "904e5138fffb"
branch_labels: None = None
depends_on: None = None


def upgrade() -> None:
    op.create_table(
        "api_key",
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
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("hashed_api_key", sa.String(), nullable=False),
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
        sa.Column("api_key_display", sa.String(), nullable=False),
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
        sa.Column(
            "owner_id",
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
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("api_key_display"),
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
        sa.UniqueConstraint("hashed_api_key"),
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
    )


def downgrade() -> None:
    op.drop_table("api_key")
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
