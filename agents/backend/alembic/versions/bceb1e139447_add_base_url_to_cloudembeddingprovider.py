from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from alembic import op
import sqlalchemy as sa
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""Add base_url to CloudEmbeddingProvider

Revision ID: bceb1e139447
Revises: a3795dce87be
Create Date: 2024-08-28 17:00:52.554580

"""



# revision identifiers, used by Alembic.
revision = "bceb1e139447"
down_revision = "a3795dce87be"
branch_labels: None = None
depends_on: None = None


def upgrade() -> None:
    op.add_column(
        "embedding_provider", sa.Column("api_url", sa.String(), nullable=True)
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
    op.drop_column("embedding_provider", "api_url")
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
