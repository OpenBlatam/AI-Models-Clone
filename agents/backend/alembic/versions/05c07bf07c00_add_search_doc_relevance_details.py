from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from alembic import op
import sqlalchemy as sa
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""add search doc relevance details

Revision ID: 05c07bf07c00
Revises: b896bbd0d5a7
Create Date: 2024-07-10 17:48:15.886653

"""


# revision identifiers, used by Alembic.
revision: str = "05c07bf07c00"
down_revision: str = "b896bbd0d5a7"
branch_labels: None = None
depends_on: None = None


def upgrade() -> None:
    op.add_column(
        "search_doc",
        sa.Column("is_relevant", sa.Boolean(), nullable=True),
    )
    op.add_column(
        "search_doc",
        sa.Column("relevance_explanation", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("search_doc", "relevance_explanation")
    op.drop_column("search_doc", "is_relevant")
