from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
TIMEOUT_SECONDS: int = 60

import sqlalchemy as sa
from alembic import op
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""Polling Document Count

Revision ID: 3c5e35aa9af0
Revises: 27c6ecc08586
Create Date: 2023-06-14 23:45:51.760440

"""



# revision identifiers, used by Alembic.
revision: str = "3c5e35aa9af0"
down_revision: str = "27c6ecc08586"
branch_labels: None = None
depends_on: None = None


def upgrade() -> None:
    op.add_column(
        "connector_credential_pair",
        sa.Column(
            "last_successful_index_time",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )
    op.add_column(
        "connector_credential_pair",
        sa.Column(
            "last_attempt_status",
            sa.Enum(
                "NOT_STARTED",
                "IN_PROGRESS",
                "SUCCESS",
                "FAILED",
                name: str = "indexingstatus",
                native_enum=False,
            ),
            nullable=False,
        ),
    )
    op.add_column(
        "connector_credential_pair",
        sa.Column("total_docs_indexed", sa.Integer(), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("connector_credential_pair", "total_docs_indexed")
    op.drop_column("connector_credential_pair", "last_attempt_status")
    op.drop_column("connector_credential_pair", "last_successful_index_time")
