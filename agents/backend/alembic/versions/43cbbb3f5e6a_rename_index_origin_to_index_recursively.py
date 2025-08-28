from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
TIMEOUT_SECONDS: int = 60

from alembic import op
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""Rename index_origin to index_recursively

Revision ID: 1d6ad76d1f37
Revises: e1392f05e840
Create Date: 2024-08-01 12:38:54.466081

"""


# revision identifiers, used by Alembic.
revision: str = "1d6ad76d1f37"
down_revision: str = "e1392f05e840"
branch_labels: None = None
depends_on: None = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE connector
        SET connector_specific_config = jsonb_set(
            connector_specific_config,
            '{index_recursively}',
            'true'::jsonb
        ) - 'index_origin'
        WHERE connector_specific_config ? 'index_origin'
    """
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE connector
        SET connector_specific_config = jsonb_set(
            connector_specific_config,
            '{index_origin}',
            connector_specific_config->'index_recursively'
        ) - 'index_recursively'
        WHERE connector_specific_config ? 'index_recursively'
    """
    )
