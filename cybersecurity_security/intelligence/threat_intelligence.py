from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
import ipaddress
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, validator
import asyncio
import aiohttp
            import socket
from typing import Any, List, Dict, Optional
import logging
"""
Threat Intelligence

Provides threat intelligence and reputation checking capabilities.
"""


class IPReputationRequest(BaseModel):
    """Pydantic model for IP reputation request."""
    ip_address: str = Field(..., description="IP address to check")
    api_key: Optional[str] = Field(None, description="API key for external services")
    
    @validator('ip_address')
    def validate_ip_address(cls, v) -> bool:
        try:
            ipaddress.ip_address(v)
            return v
        except ValueError:
            raise ValueError("Invalid IP address format")

class IPReputationResult(BaseModel):
    """Pydantic model for IP reputation result."""
    ip_address: str
    is_private: bool
    is_loopback: bool
    threat_sources: Dict[str, Any] = Field(default_factory=dict)
    reputation_score: Optional[float] = None
    country_code: Optional[str] = None

class DomainReputationRequest(BaseModel):
    """Pydantic model for domain reputation request."""
    domain: str = Field(..., description="Domain to check")
    
    @validator('domain')
    def validate_domain(cls, v) -> bool:
        if not v or '.' not in v:
            raise ValueError("Invalid domain format")
        return v.lower()

class DomainReputationResult(BaseModel):
    """Pydantic model for domain reputation result."""
    domain: str
    checks: Dict[str, Any] = Field(default_factory=dict)
    reputation_score: Optional[float] = None
    is_suspicious: bool = False

async def check_ip_reputation_async(data: IPReputationRequest) -> IPReputationResult:
    """Check IP reputation asynchronously (I/O-bound)."""
    ip_address = data.ip_address
    api_key = data.api_key
    
    try:
        ip_obj = ipaddress.ip_address(ip_address)
        
        reputation_data = IPReputationResult(
            ip_address=ip_address,
            is_private=ip_obj.is_private,
            is_loopback=ip_obj.is_loopback,
            threat_sources={}
        )
        
        # Check against external threat intelligence APIs
        if api_key:
            async with aiohttp.ClientSession() as session:
                # Example: Check against AbuseIPDB
                url = "https://api.abuseipdb.com/api/v2/check"
                headers = {
                    "Key": api_key,
                    "Accept": "application/json"
                }
                params = {
                    "ipAddress": ip_address,
                    "maxAgeInDays": 90
                }
                
                try:
                    async with session.get(url, headers=headers, params=params) as response:
                        if response.status == 200:
                            result = await response.json()
                            reputation_data.threat_sources["abuseipdb"] = {
                                "abuse_confidence_score": result["data"]["abuseConfidenceScore"],
                                "country_code": result["data"]["countryCode"],
                                "usage_type": result["data"]["usageType"]
                            }
                            reputation_data.reputation_score = result["data"]["abuseConfidenceScore"]
                            reputation_data.country_code = result["data"]["countryCode"]
                except Exception as e:
                    reputation_data.threat_sources["abuseipdb"] = {"error": str(e)}
        
        return reputation_data
    
    except ValueError:
        return IPReputationResult(
            ip_address=ip_address,
            is_private=False,
            is_loopback=False,
            threat_sources={"error": "Invalid IP address format"}
        )

async def check_domain_reputation_async(data: DomainReputationRequest) -> DomainReputationResult:
    """Check domain reputation asynchronously (I/O-bound)."""
    domain = data.domain
    
    reputation_data = DomainReputationResult(domain=domain)
    
    async with aiohttp.ClientSession() as session:
        # DNS resolution check
        try:
            # Run DNS resolution in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            ip_address = await loop.run_in_executor(None, socket.gethostbyname, domain)
            reputation_data.checks["dns_resolution"] = {
                "resolved": True,
                "ip_address": ip_address
            }
        except socket.gaierror:
            reputation_data.checks["dns_resolution"] = {
                "resolved": False,
                "error": "Domain not found"
            }
            reputation_data.is_suspicious = True
        
        # Check for malicious indicators
        malicious_indicators = [
            "malware", "phishing", "spam", "botnet", "c2", "command"
        ]
        
        suspicious_count = sum(1 for indicator in malicious_indicators if indicator in domain.lower())
        reputation_data.reputation_score = suspicious_count / len(malicious_indicators)
        reputation_data.is_suspicious = reputation_data.reputation_score > 0.3
    
    return reputation_data 