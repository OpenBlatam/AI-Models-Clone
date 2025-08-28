from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from dataclasses import dataclass

from typing import Dict, Any
from pydantic import BaseModel

from typing import Any, List, Dict, Optional
import logging
import asyncio
class CopywritingConfig(BaseModel):
    """Configuration for the copywriting service."""
    timeout: int = 10
    max_retries: int = 3
    default_tone: str = "professional"
    default_platform: str = "general"
    
    @dataclass
class Config:
        extra = "allow"

def get_copywriting_config() -> Dict[str, Any]:
    """Get the copywriting service configuration."""
    return CopywritingConfig().model_dump()
