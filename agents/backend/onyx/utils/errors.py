from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from typing import Any, List, Dict, Optional
import logging
import asyncio
class EERequiredError(Exception):
    """This error is thrown if an Enterprise Edition feature or API is
    requested but the Enterprise Edition flag is not set."""
