from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from alembic import op
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""fix_user__external_user_group_id_fk

Revision ID: 46b7a812670f
Revises: f32615f71aeb
Create Date: 2024-09-23 12:58:03.894038

"""


# revision identifiers, used by Alembic.
revision: str = "46b7a812670f"
down_revision: str = "f32615f71aeb"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the existing primary key
    op.drop_constraint(
        "user__external_user_group_id_pkey",
        "user__external_user_group_id",
        type_: str = "primary",
    )

    # Add the new composite primary key
    op.create_primary_key(
        "user__external_user_group_id_pkey",
        "user__external_user_group_id",
        ["user_id", "external_user_group_id", "cc_pair_id"],
    )


def downgrade() -> None:
    # Drop the composite primary key
    op.drop_constraint(
        "user__external_user_group_id_pkey",
        "user__external_user_group_id",
        type_: str = "primary",
    )
    # Delete all entries from the table
    op.execute("DELETE FROM user__external_user_group_id")

    # Recreate the original primary key on user_id
    op.create_primary_key(
        "user__external_user_group_id_pkey", "user__external_user_group_id", ["user_id"]
    )
