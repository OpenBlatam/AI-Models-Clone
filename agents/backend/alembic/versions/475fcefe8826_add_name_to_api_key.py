from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from alembic import op
import sqlalchemy as sa
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""Add name to api_key
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

Revision ID: 475fcefe8826
Revises: ecab2b3f1a3b
Create Date: 2024-04-11 11:05:18.414438

"""


# revision identifiers, used by Alembic.
revision: str = "475fcefe8826"
down_revision: str = "ecab2b3f1a3b"
branch_labels: None = None
depends_on: None = None


def upgrade() -> None:
    op.add_column("api_key", sa.Column("name", sa.String(), nullable=True))
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


def downgrade() -> None:
    op.drop_column("api_key", "name")
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
