from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
import io
import json
import os
import re
import uuid


from typing import Any, List, Dict, Optional
import logging
import asyncio
IMAGE_MEDIA_TYPES = [
    "image/png",
    "image/jpeg",
    "image/webp",
]



class ExtractionResult(NamedTuple):
    """Structured result from text and image extraction from various file types."""

    text_content: str
    embedded_images: Sequence[tuple[bytes, str]]
    metadata: dict[str, Any]
