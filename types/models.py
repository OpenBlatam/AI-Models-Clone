from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from pydantic import BaseModel, Field
from typing import List, Dict, Any

from typing import Any, List, Dict, Optional
import logging
import asyncio
__all__ = ["ScanResult", ExploitResult"]

class ScanResult(BaseModel):
    host: str = Field(..., description="Target host for scan)  open_ports: List[int] = Field(default_factory=list, description="List of open ports found")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional scan metadata")

class ExploitResult(BaseModel):
    url: str = Field(..., description="Target URL for exploit")
    is_vulnerable: bool = Field(..., description="Whether the target is vulnerable")
    details: Dict[str, Any] = Field(default_factory=dict, description="Exploit details and findings") 