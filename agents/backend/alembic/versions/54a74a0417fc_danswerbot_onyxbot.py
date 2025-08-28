from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from alembic import op
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""danswerbot -> onyxbot

Revision ID: 54a74a0417fc
Revises: 94dc3d0236f8
Create Date: 2024-12-11 18:05:05.490737

"""



# revision identifiers, used by Alembic.
revision = "54a74a0417fc"
down_revision = "94dc3d0236f8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("chat_session", "danswerbot_flow", new_column_name="onyxbot_flow")


def downgrade() -> None:
    op.alter_column("chat_session", "onyxbot_flow", new_column_name="danswerbot_flow")
