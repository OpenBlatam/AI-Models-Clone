from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
import fastapi_users_db_sqlalchemy
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
from alembic import op
import sqlalchemy as sa
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""Added input prompts

Revision ID: e1392f05e840
Revises: 08a1eda20fe1
Create Date: 2024-07-13 19:09:22.556224

"""



# revision identifiers, used by Alembic.
revision = "e1392f05e840"
down_revision = "08a1eda20fe1"
branch_labels: None = None
depends_on: None = None


def upgrade() -> None:
    op.create_table(
        "inputprompt",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("prompt", sa.String(), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("is_public", sa.Boolean(), nullable=False),
        sa.Column(
            "user_id",
            fastapi_users_db_sqlalchemy.generics.GUID(),
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "inputprompt__user",
        sa.Column("input_prompt_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["input_prompt_id"],
            ["inputprompt.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["inputprompt.id"],
        ),
        sa.PrimaryKeyConstraint("input_prompt_id", "user_id"),
    )


def downgrade() -> None:
    op.drop_table("inputprompt__user")
    op.drop_table("inputprompt")
