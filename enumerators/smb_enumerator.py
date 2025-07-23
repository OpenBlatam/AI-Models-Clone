from typing import Dict, Any, List
from pydantic import BaseModel, Field
from smb.SMBConnection import SMBConnection

__all__ = ["SMBConfig", "enumerate_smb"]

class SMBConfig(BaseModel):
    host: str = Field(..., description="SMB host to enumerate")
    username: str = Field(default="", description="Username for SMB authentication")
    password: str = Field(default="", description="Password for SMB authentication")
    client_name: str = Field(default="smbclient", description="Client name")
    server_name: str = Field(default=None, description="Server name (defaults to host)")

    def get_server_name(self) -> str:
        return self.server_name or self.host

def enumerate_smb(*, config: SMBConfig) -> Dict[str, Any]:
    """Enumerate SMB shares for a host (RORO, Pydantic, type hints)."""
    shares: List[str] = []
    try:
        conn = SMBConnection(
            config.username, config.password, config.client_name, config.get_server_name(), use_ntlm_v2=True
        )
        is_connected = conn.connect(config.host, 139)
        if is_connected:
            shares = [share.name for share in conn.listShares()]
        conn.close()
    except Exception:
        pass
    return {"host": config.host, "shares": shares} 