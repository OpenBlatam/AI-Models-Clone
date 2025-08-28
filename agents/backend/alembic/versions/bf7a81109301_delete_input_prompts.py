from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from alembic import op
import sqlalchemy as sa
import fastapi_users_db_sqlalchemy
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""delete_input_prompts

Revision ID: bf7a81109301
Revises: f7a894b06d02
Create Date: 2024-12-09 12:00:49.884228

"""



# revision identifiers, used by Alembic.
revision = "bf7a81109301"
down_revision = "f7a894b06d02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table("inputprompt__user")
    op.drop_table("inputprompt")


def downgrade() -> None:
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
