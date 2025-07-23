"""
Network Helpers

Provides network utility functions for security operations.
"""

import asyncio
import socket
import httpx
import time
import json
from functools import lru_cache
from typing import Any, Dict, List, Optional

# DNS cache with LRU
@lru_cache(maxsize=1024)
def resolve_hostname(hostname: str) -> str:
    return socket.gethostbyname(hostname)

async def async_resolve_hostname(hostname: str) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, resolve_hostname, hostname)

# Async HTTP client with connection pooling (dependency injection ready)
class HTTPClientPool:
    def __init__(self, max_connections: int = 100, max_keepalive: int = 20):
        self.client = httpx.AsyncClient(limits=httpx.Limits(max_connections=max_connections, max_keepalive_connections=max_keepalive))
    async def get(self, url: str, **kwargs):
        return await self.client.get(url, **kwargs)
    async def post(self, url: str, **kwargs):
        return await self.client.post(url, **kwargs)
    async def close(self):
        await self.client.aclose()

# Rate limiter (token bucket)
class RateLimiter:
    def __init__(self, rate_per_sec: float, burst: int = 1):
        self.rate = rate_per_sec
        self.burst = burst
        self.tokens = burst
        self.last = time.monotonic()
    async def acquire(self):
        now = time.monotonic()
        elapsed = now - self.last
        self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
        if self.tokens < 1:
            await asyncio.sleep((1 - self.tokens) / self.rate)
            self.tokens = 0
        else:
            self.tokens -= 1
        self.last = time.monotonic()

# Structured JSON logger
class JsonLogger:
    def __init__(self, name: str):
        self.name = name
    def log(self, level: str, message: str, **kwargs):
        log_record = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
            "level": level,
            "logger": self.name,
            "message": message,
        }
        log_record.update(kwargs)
        print(json.dumps(log_record))

logger = JsonLogger("network_helpers")

# Async batch HTTP fetch with rate limiting and logging
def chunked(lst: List[Any], size: int):
    for i in range(0, len(lst), size):
        yield lst[i:i+size]

async def batch_fetch(urls: List[str], client: HTTPClientPool, rate_limiter: Optional[RateLimiter] = None, batch_size: int = 50):
    results = []
    for batch in chunked(urls, batch_size):
        tasks = []
        for url in batch:
            if rate_limiter:
                await rate_limiter.acquire()
            tasks.append(client.get(url, timeout=10))
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        for url, resp in zip(batch, responses):
            if isinstance(resp, Exception):
                logger.log("ERROR", "HTTP fetch failed", url=url, error=str(resp))
                results.append({"url": url, "error": str(resp)})
            else:
                logger.log("INFO", "HTTP fetch succeeded", url=url, status=resp.status_code)
                results.append({"url": url, "status": resp.status_code, "body": resp.text})
        await asyncio.sleep(1)
    return results

# Async DNS scan example with caching and logging
async def async_dns_scan(hosts: List[str]):
    results = []
    for host in hosts:
        try:
            ip = await async_resolve_hostname(host)
            logger.log("INFO", "DNS resolved", host=host, ip=ip)
            results.append({"host": host, "ip": ip})
        except Exception as e:
            logger.log("ERROR", "DNS resolve failed", host=host, error=str(e))
            results.append({"host": host, "error": str(e)})
    return results 