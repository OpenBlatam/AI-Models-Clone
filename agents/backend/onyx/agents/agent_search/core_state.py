from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from operator import add
from typing import Annotated

from pydantic import BaseModel


from typing import Any, List, Dict, Optional
import logging
import asyncio
class CoreState(BaseModel):
    """
    This is the core state that is shared across all subgraphs.
    """

    log_messages: Annotated[list[str], add] = []


class SubgraphCoreState(BaseModel):
    """
    This is the core state that is shared across all subgraphs.
    """

    log_messages: Annotated[list[str], add] = []
