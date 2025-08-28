from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from typing import Any, List, Dict, Optional
import logging
import asyncio
class ModelServerRateLimitError(Exception):
    """
    Exception raised for rate limiting errors from the model server.
    """
