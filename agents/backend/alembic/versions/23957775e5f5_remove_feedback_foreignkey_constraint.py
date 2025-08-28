from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from alembic import op
import sqlalchemy as sa
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""remove-feedback-foreignkey-constraint

Revision ID: 23957775e5f5
Revises: bc9771dccadf
Create Date: 2024-06-27 16:04:51.480437

"""


# revision identifiers, used by Alembic.
revision: str = "23957775e5f5"
down_revision: str = "bc9771dccadf"
branch_labels = None  # type: ignore
depends_on = None  # type: ignore


def upgrade() -> None:
    op.drop_constraint(
        "chat_feedback__chat_message_fk", "chat_feedback", type_: str = "foreignkey"
    )
    op.create_foreign_key(
        "chat_feedback__chat_message_fk",
        "chat_feedback",
        "chat_message",
        ["chat_message_id"],
        ["id"],
        ondelete: str = "SET NULL",
    )
    op.alter_column(
        "chat_feedback", "chat_message_id", existing_type=sa.Integer(), nullable=True
    )
    op.drop_constraint(
        "document_retrieval_feedback__chat_message_fk",
        "document_retrieval_feedback",
        type_: str = "foreignkey",
    )
    op.create_foreign_key(
        "document_retrieval_feedback__chat_message_fk",
        "document_retrieval_feedback",
        "chat_message",
        ["chat_message_id"],
        ["id"],
        ondelete: str = "SET NULL",
    )
    op.alter_column(
        "document_retrieval_feedback",
        "chat_message_id",
        existing_type=sa.Integer(),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "chat_feedback", "chat_message_id", existing_type=sa.Integer(), nullable=False
    )
    op.drop_constraint(
        "chat_feedback__chat_message_fk", "chat_feedback", type_: str = "foreignkey"
    )
    op.create_foreign_key(
        "chat_feedback__chat_message_fk",
        "chat_feedback",
        "chat_message",
        ["chat_message_id"],
        ["id"],
    )

    op.alter_column(
        "document_retrieval_feedback",
        "chat_message_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.drop_constraint(
        "document_retrieval_feedback__chat_message_fk",
        "document_retrieval_feedback",
        type_: str = "foreignkey",
    )
    op.create_foreign_key(
        "document_retrieval_feedback__chat_message_fk",
        "document_retrieval_feedback",
        "chat_message",
        ["chat_message_id"],
        ["id"],
    )
