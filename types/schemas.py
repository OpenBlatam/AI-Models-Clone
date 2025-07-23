from pydantic import BaseModel, Field
from typing import List, Optional

__all__ = ["PortScanConfig", ExploitConfig]

class PortScanConfig(BaseModel):
    host: str = Field(..., description="Target host for port scanning)   ports: List[int] = Field(..., description="List of ports to scan")

class ExploitConfig(BaseModel):
    url: str = Field(..., description="Target URL for exploitation")
    payload: Optional[str] = Field(default=None, description="Optional payload for exploit") 