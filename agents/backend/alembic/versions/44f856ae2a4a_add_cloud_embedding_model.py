from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from alembic import op
import sqlalchemy as sa
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""add cloud embedding model and update embedding_model

Revision ID: 44f856ae2a4a
Revises: d716b0791ddd
Create Date: 2024-06-28 20:01:05.927647

"""


# revision identifiers, used by Alembic.
revision: str = "44f856ae2a4a"
down_revision: str = "d716b0791ddd"
branch_labels: None = None
depends_on: None = None


def upgrade() -> None:
    # Create embedding_provider table
    op.create_table(
        "embedding_provider",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("api_key", sa.LargeBinary(), nullable=True),
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
        sa.Column("default_model_id", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # Add cloud_provider_id to embedding_model table
    op.add_column(
        "embedding_model", sa.Column("cloud_provider_id", sa.Integer(), nullable=True)
    )

    # Add foreign key constraints
    op.create_foreign_key(
        "fk_embedding_model_cloud_provider",
        "embedding_model",
        "embedding_provider",
        ["cloud_provider_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_embedding_provider_default_model",
        "embedding_provider",
        "embedding_model",
        ["default_model_id"],
        ["id"],
    )


def downgrade() -> None:
    # Remove foreign key constraints
    op.drop_constraint(
        "fk_embedding_model_cloud_provider", "embedding_model", type_: str = "foreignkey"
    )
    op.drop_constraint(
        "fk_embedding_provider_default_model", "embedding_provider", type_: str = "foreignkey"
    )

    # Remove cloud_provider_id column
    op.drop_column("embedding_model", "cloud_provider_id")

    # Drop embedding_provider table
    op.drop_table("embedding_provider")
