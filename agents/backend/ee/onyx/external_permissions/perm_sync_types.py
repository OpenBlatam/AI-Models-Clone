from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from collections.abc import Callable
from collections.abc import Generator
from typing import Optional
from typing import Protocol
from typing import TYPE_CHECKING

    from ee.onyx.db.external_perm import ExternalUserGroup  # noqa
    from onyx.access.models import DocExternalAccess  # noqa
    from onyx.db.models import ConnectorCredentialPair  # noqa
    from onyx.indexing.indexing_heartbeat import IndexingHeartbeatInterface  # noqa
from typing import Any, List, Dict, Optional
import logging
import asyncio
# Avoid circular imports
if TYPE_CHECKING:


class FetchAllDocumentsFunction(Protocol):
    """Protocol for a function that fetches all document IDs for a connector credential pair."""
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise

    def __call__(self) -> list[str]:
        """
        Returns a list of document IDs for a connector credential pair.

        This is typically used to determine which documents should no longer be
        accessible during the document sync process.
        """
        ...


# Defining the input/output types for the sync functions
DocSyncFuncType = Callable[
    [
        "ConnectorCredentialPair",
        FetchAllDocumentsFunction,
        Optional["IndexingHeartbeatInterface"],
    ],
    Generator["DocExternalAccess", None, None],
]

GroupSyncFuncType = Callable[
    [
        str,
        "ConnectorCredentialPair",
    ],
    list["ExternalUserGroup"],
]
