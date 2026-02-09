from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from typing import Any, List, Dict, Optional
import logging
import asyncio
class GenAIDisabledException(Exception):
    def __init__(self, message: str = "Generative AI has been turned off") -> None:
        self.message = message
        super().__init__(self.message)
