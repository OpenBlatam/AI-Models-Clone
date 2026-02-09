from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
import requests
import time
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, validator
import asyncio
import aiohttp
from typing import Any, List, Dict, Optional
import logging
"""
Security Testing Framework

Provides security testing and penetration testing capabilities.
"""


class SecurityTestRequest(BaseModel):
    """Pydantic model for security test request."""
    base_url: str = Field(..., description="Base URL to test")
    test_endpoints: List[str] = Field(default_factory=list, description="Endpoints to test")
    test_types: List[str] = Field(default_factory=lambda: ["sql_injection", "xss"], description="Types of tests to run")
    
    @validator('base_url')
    def validate_url(cls, v) -> bool:
        if not v.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        return v

class SecurityTestResult(BaseModel):
    """Pydantic model for security test result."""
    base_url: str
    tests_run: int
    tests_passed: int
    tests_failed: int
    security_vulnerabilities: List[Dict[str, Any]] = Field(default_factory=list)
    test_duration: float
    risk_score: float
    risk_level: str

class PenetrationTestRequest(BaseModel):
    """Pydantic model for penetration test request."""
    target_url: str = Field(..., description="Target URL to test")
    test_types: List[str] = Field(default_factory=lambda: ["sql_injection", "xss", "csrf"])
    max_concurrent_requests: int = Field(default=10, ge=1, le=50)
    
    @validator('target_url')
    def validate_target_url(cls, v) -> Optional[Dict[str, Any]]:
        if not v.startswith(('http://', 'https://')):
            raise ValueError("Target URL must start with http:// or https://")
        return v

class PenetrationTestResult(BaseModel):
    """Pydantic model for penetration test result."""
    target_url: str
    test_types: List[str]
    vulnerabilities_found: List[Dict[str, Any]] = Field(default_factory=list)
    risk_assessment: Dict[str, Any] = Field(default_factory=dict)
    test_duration: float
    requests_made: int

async def run_security_tests_async(data: SecurityTestRequest) -> SecurityTestResult:
    """Run security tests asynchronously (I/O-bound)."""
    base_url = data.base_url
    test_endpoints = data.test_endpoints or ["/api/users", "/api/admin"]
    test_types = data.test_types
    
    test_results = SecurityTestResult(
        base_url=base_url,
        tests_run=0,
        tests_passed=0,
        tests_failed=0,
        test_duration=0.0,
        risk_score=0.0,
        risk_level="LOW"
    )
    
    start_time = time.time()
    
    # SQL Injection tests
    if "sql_injection" in test_types:
        sql_injection_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --"
        ]
        
        async with aiohttp.ClientSession() as session:
            for endpoint in test_endpoints:
                for payload in sql_injection_payloads:
                    test_results.tests_run += 1
                    
                    try:
                        async with session.post(
                            f"{base_url}{endpoint}", 
                            json={"query": payload}, 
                            timeout=aiohttp.ClientTimeout(total=5)
                        ) as response:
                            response_text = await response.text()
                            
                            if response.status == 500 or "error" in response_text.lower():
                                test_results.security_vulnerabilities.append({
                                    "type": "sql_injection",
                                    "endpoint": endpoint,
                                    "payload": payload,
                                    "response_code": response.status
                                })
                                test_results.tests_failed += 1
                            else:
                                test_results.tests_passed += 1
                                
                    except Exception as e:
                        test_results.tests_failed += 1
                        test_results.security_vulnerabilities.append({
                            "type": "connection_error",
                            "endpoint": endpoint,
                            "error": str(e)
                        })
    
    test_results.test_duration = time.time() - start_time
    
    # Calculate risk score
    high_vulns = len([v for v in test_results.security_vulnerabilities if v.get("type") == "sql_injection"])
    test_results.risk_score = high_vulns * 3
    test_results.risk_level = "CRITICAL" if test_results.risk_score > 10 else "HIGH" if test_results.risk_score > 5 else "MEDIUM" if test_results.risk_score > 2 else "LOW"
    
    return test_results

async def run_penetration_test_async(data: PenetrationTestRequest) -> PenetrationTestResult:
    """Run penetration test asynchronously (I/O-bound)."""
    target_url = data.target_url
    test_types = data.test_types
    max_concurrent = data.max_concurrent_requests
    
    penetration_results = PenetrationTestResult(
        target_url=target_url,
        test_types=test_types,
        test_duration=0.0,
        requests_made=0
    )
    
    start_time = time.time()
    
    # XSS tests
    if "xss" in test_types:
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>"
        ]
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def test_xss_payload(payload: str) -> Optional[Dict[str, Any]]:
            async with semaphore:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f"{target_url}/search?q={payload}") as response:
                            response_text = await response.text()
                            penetration_results.requests_made += 1
                            
                            if payload in response_text:
                                return {
                                    "type": "xss",
                                    "payload": payload,
                                    "severity": "high"
                                }
                except Exception as e:
                    return {
                        "type": "connection_error",
                        "error": str(e),
                        "severity": "info"
                    }
                return None
        
        # Run XSS tests concurrently
        tasks = [test_xss_payload(payload) for payload in xss_payloads]
        results = await asyncio.gather(*tasks)
        
        for result in results:
            if result:
                penetration_results.vulnerabilities_found.append(result)
    
    penetration_results.test_duration = time.time() - start_time
    
    # Calculate risk assessment
    high_vulns = len([v for v in penetration_results.vulnerabilities_found if v["severity"] == "high"])
    medium_vulns = len([v for v in penetration_results.vulnerabilities_found if v["severity"] == "medium"])
    
    risk_score = high_vulns * 3 + medium_vulns * 1
    penetration_results.risk_assessment = {
        "risk_score": risk_score,
        "risk_level": "CRITICAL" if risk_score > 10 else "HIGH" if risk_score > 5 else "MEDIUM" if risk_score > 2 else "LOW"
    }
    
    return penetration_results 