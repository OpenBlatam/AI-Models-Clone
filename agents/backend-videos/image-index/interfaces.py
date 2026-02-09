from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
import abc
from dataclasses import dataclass
from datetime import datetime
from typing import Any


from typing import Any, List, Dict, Optional
import logging
import asyncio
@dataclass(frozen=True)
class ImageInsertionRecord:
    image_id: str
    already_existed: bool


@dataclass
class IndexBatchParams:
    """
    Information necessary for efficiently indexing a batch of documents
    """

    image_id_to_previous_chunk_cnt: dict[str, int | None]
    image_id_to_new_chunk_cnt: dict[str, int]
    tenant_id: str
    large_chunks_enabled: bool

