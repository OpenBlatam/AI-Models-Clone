from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from pydantic import BaseModel

from onyx.auth.schemas import UserRole


from typing import Any, List, Dict, Optional
import logging
import asyncio
class APIKeyArgs(BaseModel):
    name: str | None = None
    role: UserRole = UserRole.BASIC
