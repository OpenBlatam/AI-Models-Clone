from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from typing import Dict, Any
from pydantic import BaseModel, Field
import hashlib
import secrets

from typing import Any, List, Dict, Optional
import logging
import asyncio
__all__ = ["HashConfig", "TokenConfig", "generate_sha256", "generate_random_token"]

class HashConfig(BaseModel):
    data: str = Field(..., description="Data to hash")

def generate_sha256sh(*, config: HashConfig) -> Dict[str, Any]:
    """Generates SHA256 hash of data (RORO, Pydantic, type hints)."""
    hash_hex: str = hashlib.sha256(config.data.encode()).hexdigest()
    return {"hash": hash_hex}

class TokenConfig(BaseModel):
    length: int = Field(default=32, description="Length of random token")

def generate_random_token(*, config: TokenConfig) -> Dict[str, Any]:
    """Generates random token (RORO, Pydantic, type hints)."""
    token: str = secrets.token_hex(config.length)
    return {"token": token} 