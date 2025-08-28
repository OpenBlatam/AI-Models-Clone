from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
    from alembic import op
    from alembic import op
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""force lowercase all users

Revision ID: f11b408e39d3
Revises: 3bd4c84fe72f
Create Date: 2025-02-26 17:04:55.683500

"""

# revision identifiers, used by Alembic.
revision = "f11b408e39d3"
down_revision = "3bd4c84fe72f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1) Convert all existing user emails to lowercase

    op.execute(
        """
        UPDATE "user"
        SET email = LOWER(email)
        """
    )

    # 2) Add a check constraint to ensure emails are always lowercase
    op.create_check_constraint("ensure_lowercase_email", "user", "email = LOWER(email)")


def downgrade() -> None:
    # Drop the check constraint

    op.drop_constraint("ensure_lowercase_email", "user", type_="check")
