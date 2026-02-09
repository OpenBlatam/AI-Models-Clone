from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
import hashlib

from fastapi import Request

from onyx.configs.constants import SESSION_KEY


from typing import Any, List, Dict, Optional
import logging
import asyncio
def encrypt_string(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def extract_hashed_cookie(request: Request) -> str | None:
    session_cookie = request.cookies.get(SESSION_KEY)
    return encrypt_string(session_cookie) if session_cookie else None
