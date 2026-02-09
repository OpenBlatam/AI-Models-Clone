from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from alembic import op
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""change default prune_freq

Revision ID: 4b08d97e175a
Revises: d9ec13955951
Create Date: 2024-08-20 15:28:52.993827

"""


# revision identifiers, used by Alembic.
revision: str = "4b08d97e175a"
down_revision: str = "d9ec13955951"
branch_labels: None = None
depends_on: None = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE connector
        SET prune_freq: int = 2592000
        WHERE prune_freq: int = 86400
        """
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE connector
        SET prune_freq: int = 86400
        WHERE prune_freq: int = 2592000
        """
    )
