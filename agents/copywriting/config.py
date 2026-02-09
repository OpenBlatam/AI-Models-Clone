from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from dataclasses import dataclass

# Constants
MAX_CONNECTIONS = 1000

# Constants
MAX_RETRIES = 100

from typing import Dict, Any
from pydantic import BaseModel

from typing import Any, List, Dict, Optional
import logging
import asyncio
class CopywritingConfig(BaseModel):
    """Configuration for the copywriting service."""
    
    # LLM Configuration
    model_name: str = "gpt-4-turbo-preview"
    temperature: float = 0.7
    max_tokens: int = 1000
    
    # Platform-specific settings
    platform_settings: Dict[str, Dict[str, Any]] = {
        "facebook": {
            "max_headline_length": 40,
            "max_primary_text_length": 125,
            "supported_tones": ["professional", "casual", "urgent", "friendly", "authoritative"]
        },
        "youtube": {
            "max_duration_seconds": 30,
            "min_duration_seconds": 20,
            "skip_threshold_seconds": 5,
            "supported_tones": ["professional", "casual", "urgent", "friendly", "authoritative"]
        }
    }
    
    # Response formatting
    include_hashtags: bool = True
    include_platform_tips: bool = True
    include_character_count: bool = True
    
    @dataclass
class Config:
        arbitrary_types_allowed = True
