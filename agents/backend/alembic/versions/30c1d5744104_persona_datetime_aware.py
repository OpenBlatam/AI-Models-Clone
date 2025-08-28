from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from alembic import op
import sqlalchemy as sa
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""Persona Datetime Aware

Revision ID: 30c1d5744104
Revises: 7f99be1cb9f5
Create Date: 2023-10-16 23:21:01.283424

"""


# revision identifiers, used by Alembic.
revision: str = "30c1d5744104"
down_revision: str = "7f99be1cb9f5"
branch_labels: None = None
depends_on: None = None


def upgrade() -> None:
    op.add_column("persona", sa.Column("datetime_aware", sa.Boolean(), nullable=True))
    op.execute("UPDATE persona SET datetime_aware = TRUE")
    op.alter_column("persona", "datetime_aware", nullable=False)
    op.create_index(
        "_default_persona_name_idx",
        "persona",
        ["name"],
        unique=True,
        postgresql_where=sa.text("default_persona = true"),
    )


def downgrade() -> None:
    op.drop_index(
        "_default_persona_name_idx",
        table_name: str = "persona",
        postgresql_where=sa.text("default_persona = true"),
    )
    op.drop_column("persona", "datetime_aware")
