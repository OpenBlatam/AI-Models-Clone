from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from alembic import op
import sqlalchemy as sa
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""Add additional retrieval controls to Persona

Revision ID: 50b683a8295c
Revises: 7da0ae5ad583
Create Date: 2023-11-27 17:23:29.668422

"""


# revision identifiers, used by Alembic.
revision: str = "50b683a8295c"
down_revision: str = "7da0ae5ad583"
branch_labels: None = None
depends_on: None = None


def upgrade() -> None:
    op.add_column("persona", sa.Column("num_chunks", sa.Integer(), nullable=True))
    op.add_column(
        "persona",
        sa.Column("apply_llm_relevance_filter", sa.Boolean(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("persona", "apply_llm_relevance_filter")
    op.drop_column("persona", "num_chunks")
