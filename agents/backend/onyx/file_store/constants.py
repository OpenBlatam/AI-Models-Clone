from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
BUFFER_SIZE = 1024

from typing import Any, List, Dict, Optional
import logging
import asyncio
MAX_IN_MEMORY_SIZE = 30 * 1024 * 1024  # 30MB
STANDARD_CHUNK_SIZE = 10 * 1024 * 1024  # 10MB chunks
