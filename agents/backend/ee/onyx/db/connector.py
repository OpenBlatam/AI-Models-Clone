from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from sqlalchemy import distinct
from sqlalchemy.orm import Session

from onyx.configs.constants import DocumentSource
from onyx.db.models import Connector
from onyx.utils.logger import setup_logger

from typing import Any, List, Dict, Optional
import logging
import asyncio
logger = setup_logger()


async async def fetch_sources_with_connectors(db_session: Session) -> list[DocumentSource]:
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    sources = db_session.query(distinct(Connector.source)).all()  # type: ignore

    document_sources = [source[0] for source in sources]

    return document_sources
