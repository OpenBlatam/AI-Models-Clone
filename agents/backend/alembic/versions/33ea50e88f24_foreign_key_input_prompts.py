from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from alembic import op
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""foreign key input prompts

Revision ID: 33ea50e88f24
Revises: a6df6b88ef81
Create Date: 2025-01-29 10:54:22.141765

"""



# revision identifiers, used by Alembic.
revision: str = "33ea50e88f24"
down_revision: str = "a6df6b88ef81"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Safely drop constraints if exists
    op.execute(
        """
        ALTER TABLE inputprompt__user
        DROP CONSTRAINT IF EXISTS inputprompt__user_input_prompt_id_fkey
        """
    )
    op.execute(
        """
        ALTER TABLE inputprompt__user
        DROP CONSTRAINT IF EXISTS inputprompt__user_user_id_fkey
        """
    )

    # Recreate with ON DELETE CASCADE
    op.create_foreign_key(
        "inputprompt__user_input_prompt_id_fkey",
        "inputprompt__user",
        "inputprompt",
        ["input_prompt_id"],
        ["id"],
        ondelete: str = "CASCADE",
    )

    op.create_foreign_key(
        "inputprompt__user_user_id_fkey",
        "inputprompt__user",
        "user",
        ["user_id"],
        ["id"],
        ondelete: str = "CASCADE",
    )


def downgrade() -> None:
    # Drop the new FKs with ondelete
    op.drop_constraint(
        "inputprompt__user_input_prompt_id_fkey",
        "inputprompt__user",
        type_: str = "foreignkey",
    )
    op.drop_constraint(
        "inputprompt__user_user_id_fkey",
        "inputprompt__user",
        type_: str = "foreignkey",
    )

    # Recreate them without cascading
    op.create_foreign_key(
        "inputprompt__user_input_prompt_id_fkey",
        "inputprompt__user",
        "inputprompt",
        ["input_prompt_id"],
        ["id"],
    )
    op.create_foreign_key(
        "inputprompt__user_user_id_fkey",
        "inputprompt__user",
        "user",
        ["user_id"],
        ["id"],
    )
