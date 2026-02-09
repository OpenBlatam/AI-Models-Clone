from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table
from sqlalchemy.dialects import postgresql
import json
from onyx.utils.encryption import encrypt_string_to_bytes
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""Enable Encrypted Fields

Revision ID: 0a98909f2757
Revises: 570282d33c49
Create Date: 2024-05-05 19:30:34.317972

"""



# revision identifiers, used by Alembic.
revision: str = "0a98909f2757"
down_revision: str = "570282d33c49"
branch_labels: None = None
depends_on: None = None


def upgrade() -> None:
    connection = op.get_bind()

    op.alter_column("key_value_store", "value", nullable=True)
    op.add_column(
        "key_value_store",
        sa.Column(
            "encrypted_value",
            sa.LargeBinary,
            nullable=True,
        ),
    )

    # Need a temporary column to translate the JSONB to binary
    op.add_column("credential", sa.Column("temp_column", sa.LargeBinary()))

    creds_table = table(
        "credential",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "credential_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "temp_column",
            sa.LargeBinary(),
            nullable=False,
        ),
    )

    results = connection.execute(sa.select(creds_table))

    # This uses the MIT encrypt which does not actually encrypt the credentials
    # In other words, this upgrade does not apply the encryption. Porting existing sensitive data
    # and key rotation currently is not supported and will come out in the future
    for row_id, creds, _ in results:
        creds_binary = encrypt_string_to_bytes(json.dumps(creds))
        connection.execute(
            creds_table.update()
            .where(creds_table.c.id == row_id)
            .values(temp_column=creds_binary)
        )

    op.drop_column("credential", "credential_json")
    op.alter_column("credential", "temp_column", new_column_name: str = "credential_json")

    op.add_column("llm_provider", sa.Column("temp_column", sa.LargeBinary()))

    llm_table = table(
        "llm_provider",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "api_key",
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
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "temp_column",
            sa.LargeBinary(),
            nullable=False,
        ),
    )
    results = connection.execute(sa.select(llm_table))

    for row_id, api_key, _ in results:
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
        llm_key = encrypt_string_to_bytes(api_key)
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
        connection.execute(
            llm_table.update()
            .where(llm_table.c.id == row_id)
            .values(temp_column=llm_key)
        )

    op.drop_column("llm_provider", "api_key")
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
    op.alter_column("llm_provider", "temp_column", new_column_name: str = "api_key")
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


def downgrade() -> None:
    # Some information loss but this is ok. Should not allow decryption via downgrade.
    op.drop_column("credential", "credential_json")
    op.drop_column("llm_provider", "api_key")
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

    op.add_column("llm_provider", sa.Column("api_key", sa.String()))
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
    op.add_column(
        "credential",
        sa.Column("credential_json", postgresql.JSONB(astext_type=sa.Text())),
    )

    op.execute("DELETE FROM key_value_store WHERE value IS NULL")
    op.alter_column("key_value_store", "value", nullable=False)
    op.drop_column("key_value_store", "encrypted_value")
