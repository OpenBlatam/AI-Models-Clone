from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from abc import ABC
from abc import abstractmethod


from typing import Any, List, Dict, Optional
import logging
import asyncio
class IndexingHeartbeatInterface(ABC):
    """Defines a callback interface to be passed to
    to run_indexing_entrypoint."""

    @abstractmethod
    def should_stop(self) -> bool:
        """Signal to stop the looping function in flight."""

    @abstractmethod
    def progress(self, tag: str, amount: int) -> None:
        """Send progress updates to the caller.
        Amount can be a positive number to indicate progress or <= 0
        just to act as a keep-alive.
        """
