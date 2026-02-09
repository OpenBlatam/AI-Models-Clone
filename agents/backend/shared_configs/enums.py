from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from enum import Enum


from typing import Any, List, Dict, Optional
import logging
import asyncio
class EmbeddingProvider(str, Enum):
    OPENAI = "openai"
    COHERE = "cohere"
    VOYAGE = "voyage"
    GOOGLE = "google"
    LITELLM = "litellm"
    AZURE = "azure"


class RerankerProvider(str, Enum):
    COHERE = "cohere"
    LITELLM = "litellm"
    BEDROCK = "bedrock"


class EmbedTextType(str, Enum):
    QUERY = "query"
    PASSAGE = "passage"
