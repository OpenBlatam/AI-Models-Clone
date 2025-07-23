from typing import Dict, Any, List
from pydantic import BaseModel, Field
import dns.resolver

__all__ = ["DNSConfig", "enumerate_dns"]

class DNSConfig(BaseModel):
    domain: str = Field(..., description="Domain to enumerate")
    record_types: List[str] = Field(default_factory=lambda: ["A", "AAAA", "MX", "NS", "TXT"], description="DNS record types")

def enumerate_dns(*, config: DNSConfig) -> Dict[str, Any]:
    """Enumerate DNS records for a domain (RORO, Pydantic, type hints)."""
    results: Dict[str, List[str]] = {}
    for record_type in config.record_types:
        try:
            answers = dns.resolver.resolve(config.domain, record_type)
            results[record_type] = [r.to_text() for r in answers]
        except Exception:
            results[record_type] = []
    return {"domain": config.domain, "records": results} 