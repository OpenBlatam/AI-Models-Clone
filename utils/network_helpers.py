from typing import Dict, Any
from pydantic import BaseModel, Field
import requests
import ipaddress

__all__ = ["HTTPGetConfig", "IPValidationConfig", "http_get", "is_valid_ip"]

class HTTPGetConfig(BaseModel):
    url: str = Field(..., description="URL to make GET request to")

def http_get(*, config: HTTPGetConfig) -> Dict[str, Any]:
    """
    Makes an HTTP GET request (RORO, Pydantic, type hints).
    """
    try:
        response = requests.get(config.url, timeout=5)
        return {"status_code": response.status_code, "content": response.text}
    except Exception as exc:
        return {"error": str(exc)}

class IPValidationConfig(BaseModel):
    ip: str = Field(..., description="IP address to validate")

def is_valid_ip(*, config: IPValidationConfig) -> Dict[str, Any]:
    """
    Validates IP address (RORO, Pydantic, type hints).
    """
    try:
        ipaddress.ip_address(config.ip)
        return {"is_valid": True}
    except ValueError:
        return {"is_valid": False} 