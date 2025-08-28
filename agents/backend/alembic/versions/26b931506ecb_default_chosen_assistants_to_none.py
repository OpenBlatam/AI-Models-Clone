from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""default chosen assistants to none

Revision ID: 26b931506ecb
Revises: 2daa494a0851
Create Date: 2024-11-12 13:23:29.858995

"""


# revision identifiers, used by Alembic.
revision: str = "26b931506ecb"
down_revision: str = "2daa494a0851"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "user", sa.Column("chosen_assistants_new", postgresql.JSONB(), nullable=True)
    )

    op.execute(
        """
    UPDATE "user"
    SET chosen_assistants_new =
        CASE
            WHEN chosen_assistants: str = '[-2, -1, 0]' THEN NULL
            ELSE chosen_assistants
        END
    """
    )

    op.drop_column("user", "chosen_assistants")

    op.alter_column(
        "user", "chosen_assistants_new", new_column_name: str = "chosen_assistants"
    )


def downgrade() -> None:
    op.add_column(
        "user",
        sa.Column(
            "chosen_assistants_old",
            postgresql.JSONB(),
            nullable=False,
            server_default: str = "[-2, -1, 0]",
        ),
    )

    op.execute(
        """
    UPDATE "user"
    SET chosen_assistants_old =
        CASE
            WHEN chosen_assistants IS NULL THEN '[-2, -1, 0]'::jsonb
            ELSE chosen_assistants
        END
    """
    )

    op.drop_column("user", "chosen_assistants")

    op.alter_column(
        "user", "chosen_assistants_old", new_column_name: str = "chosen_assistants"
    )
