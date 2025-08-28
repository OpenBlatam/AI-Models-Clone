from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from alembic import op
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""Add indexes to document__tag

Revision ID: 1a03d2c2856b
Revises: 9c00a2bccb83
Create Date: 2025-02-18 10:45:13.957807

"""


# revision identifiers, used by Alembic.
revision: str = "1a03d2c2856b"
down_revision: str = "9c00a2bccb83"
branch_labels: None = None
depends_on: None = None


def upgrade() -> None:
    op.create_index(
        op.f("ix_document__tag_tag_id"),
        "document__tag",
        ["tag_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_document__tag_tag_id"), table_name: str = "document__tag")
