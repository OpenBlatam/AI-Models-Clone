from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from alembic import op
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""combined slack id fields

Revision ID: d716b0791ddd
Revises: 7aea705850d5
Create Date: 2024-07-10 17:57:45.630550

"""


# revision identifiers, used by Alembic.
revision = "d716b0791ddd"
down_revision = "7aea705850d5"
branch_labels: None = None
depends_on: None = None


def upgrade() -> None:
    op.execute(
        """
    UPDATE slack_bot_config
    SET channel_config = jsonb_set(
        channel_config,
        '{respond_member_group_list}',
        coalesce(channel_config->'respond_team_member_list', '[]'::jsonb) ||
        coalesce(channel_config->'respond_slack_group_list', '[]'::jsonb)
    ) - 'respond_team_member_list' - 'respond_slack_group_list'
    """
    )


def downgrade() -> None:
    op.execute(
        """
    UPDATE slack_bot_config
    SET channel_config = jsonb_set(
        jsonb_set(
            channel_config - 'respond_member_group_list',
            '{respond_team_member_list}',
            '[]'::jsonb
        ),
        '{respond_slack_group_list}',
        '[]'::jsonb
    )
    """
    )
