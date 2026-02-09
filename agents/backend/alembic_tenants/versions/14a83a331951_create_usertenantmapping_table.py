from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
import sqlalchemy as sa

from alembic import op

from typing import Any, List, Dict, Optional
import logging
import asyncio
# revision identifiers, used by Alembic.
revision = "14a83a331951"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_tenant_mapping",
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.UniqueConstraint("email", "tenant_id", name="uq_user_tenant"),
        sa.UniqueConstraint("email", name="uq_email"),
        schema="public",
    )


def downgrade() -> None:
    op.drop_table("user_tenant_mapping", schema="public")
