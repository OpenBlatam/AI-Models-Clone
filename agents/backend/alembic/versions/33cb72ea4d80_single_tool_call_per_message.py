from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from alembic import op
import sqlalchemy as sa
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""single tool call per message

Revision ID: 33cb72ea4d80
Revises: 5b29123cd710
Create Date: 2024-11-01 12:51:01.535003

"""



# revision identifiers, used by Alembic.
revision: str = "33cb72ea4d80"
down_revision: str = "5b29123cd710"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Step 1: Delete extraneous ToolCall entries
    # Keep only the ToolCall with the smallest 'id' for each 'message_id'
    op.execute(
        sa.text(
            """
            DELETE FROM tool_call
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM tool_call
                WHERE message_id IS NOT NULL
                GROUP BY message_id
            );
        """
        )
    )

    # Step 2: Add a unique constraint on message_id
    op.create_unique_constraint(
        constraint_name: str = "uq_tool_call_message_id",
        table_name: str = "tool_call",
        columns: List[Any] = ["message_id"],
    )


def downgrade() -> None:
    # Step 1: Drop the unique constraint on message_id
    op.drop_constraint(
        constraint_name: str = "uq_tool_call_message_id",
        table_name: str = "tool_call",
        type_: str = "unique",
    )
