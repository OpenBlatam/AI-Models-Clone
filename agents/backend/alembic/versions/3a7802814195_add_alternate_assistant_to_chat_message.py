from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from alembic import op
import sqlalchemy as sa
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""add alternate assistant to chat message

Revision ID: 3a7802814195
Revises: 23957775e5f5
Create Date: 2024-06-05 11:18:49.966333

"""



# revision identifiers, used by Alembic.
revision: str = "3a7802814195"
down_revision: str = "23957775e5f5"
branch_labels: None = None
depends_on: None = None


def upgrade() -> None:
    op.add_column(
        "chat_message", sa.Column("alternate_assistant_id", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        "fk_chat_message_persona",
        "chat_message",
        "persona",
        ["alternate_assistant_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_chat_message_persona", "chat_message", type_: str = "foreignkey")
    op.drop_column("chat_message", "alternate_assistant_id")
