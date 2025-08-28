from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from alembic import op
import sqlalchemy as sa
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""add chunk count to document

Revision ID: 2955778aa44c
Revises: c0aab6edb6dd
Create Date: 2025-01-04 11:39:43.268612

"""



# revision identifiers, used by Alembic.
revision: str = "2955778aa44c"
down_revision: str = "c0aab6edb6dd"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("document", sa.Column("chunk_count", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("document", "chunk_count")
