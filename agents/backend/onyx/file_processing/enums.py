from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from enum import Enum


from typing import Any, List, Dict, Optional
import logging
import asyncio
class HtmlBasedConnectorTransformLinksStrategy(str, Enum):
    # remove links entirely
    STRIP = "strip"
    # turn HTML links into markdown links
    MARKDOWN = "markdown"
