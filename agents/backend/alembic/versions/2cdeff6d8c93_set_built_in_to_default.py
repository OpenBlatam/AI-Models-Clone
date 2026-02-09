from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from alembic import op
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""set built in to default

Revision ID: 2cdeff6d8c93
Revises: f5437cc136c5
Create Date: 2025-02-11 14:57:51.308775

"""



# revision identifiers, used by Alembic.
revision: str = "2cdeff6d8c93"
down_revision: str = "f5437cc136c5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Prior to this migration / point in the codebase history,
    # built in personas were implicitly treated as default personas (with no option to change this)
    # This migration makes that explicit
    op.execute(
        """
        UPDATE persona
        SET is_default_persona = TRUE
        WHERE builtin_persona = TRUE
    """
    )


def downgrade() -> None:
    pass
