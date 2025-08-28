from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
TIMEOUT_SECONDS = 60

from alembic import op
import sqlalchemy as sa
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""add indexing trigger to cc_pair

Revision ID: abe7378b8217
Revises: 6d562f86c78b
Create Date: 2024-11-26 19:09:53.481171

"""


# revision identifiers, used by Alembic.
revision = "abe7378b8217"
down_revision = "93560ba1b118"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "connector_credential_pair",
        sa.Column(
            "indexing_trigger",
            sa.Enum("UPDATE", "REINDEX", name="indexingmode", native_enum=False),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("connector_credential_pair", "indexing_trigger")
