from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from pydantic import BaseModel


from typing import Any, List, Dict, Optional
import logging
import asyncio
class ConfluenceUser(BaseModel):
    user_id: str  # accountId in Cloud, userKey in Server
    username: str | None  # Confluence Cloud doesn't give usernames
    display_name: str
    # Confluence Data Center doesn't give email back by default,
    # have to fetch it with a different endpoint
    email: str | None
    type: str
