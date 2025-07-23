"""
DNS Enumerator

Provides comprehensive DNS enumeration capabilities including record lookup, subdomain enumeration, and zone transfers.
"""

import asyncio
import aiohttp
import dns.resolver
import dns.zone
import dns.query
import socket
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, validator
from enum import Enum
import time

class DNSRecordType(str, Enum):
    """Enumeration of DNS record types."""
    A = "A"
    AAAA = "AAAA"
    CNAME = "CNAME"
    MX = "MX"
    NS = "NS"
    PTR = "PTR"
    SOA = "SOA"
    SRV = "SRV"
    TXT = "TXT"
    ANY = "ANY"

class DNSEnumerationRequest(BaseModel):
    """Pydantic model for DNS enumeration request."""
    target_domain: str = Field(..., description="Target domain to enumerate")
    record_types: List[DNSRecordType] = Field(default_factory=lambda: [DNSRecordType.A, DNSRecordType.MX, DNSRecordType.NS], description="DNS record types to query")
    nameservers: List[str] = Field(default_factory=list, description="Custom nameservers to use")
    timeout: float = Field(default=10.0, ge=1.0, le=60.0, description="Query timeout in seconds")
    max_concurrent_queries: int = Field(default=10, ge=1, le=50, description="Maximum concurrent DNS queries")
    
    @validator('target_domain')
    def validate_domain(cls, v):
        if not v or '.' not in v:
            raise ValueError("Invalid domain format")
        return v.lower()

class DNSRecord(BaseModel):
    """Pydantic model for DNS record."""
    record_type: DNSRecordType
    name: str
    value: str
    ttl: Optional[int] = None
    priority: Optional[int] = None

class DNSEnumerationResult(BaseModel):
    """Pydantic model for DNS enumeration result."""
    target_domain: str
    records_found: List[DNSRecord]
    nameservers: List[str]
    enumeration_duration: float
    total_queries: int
    successful_queries: int
    failed_queries: int
    enumeration_completed_at: float

class SubdomainEnumerationRequest(BaseModel):
    """Pydantic model for subdomain enumeration request."""
    target_domain: str = Field(..., description="Target domain for subdomain enumeration")
    wordlist: List[str] = Field(default_factory=list, description="Custom wordlist for subdomain enumeration")
    use_common_wordlist: bool = Field(default=True, description="Use common subdomain wordlist")
    max_concurrent_requests: int = Field(default=20, ge=1, le=100, description="Maximum concurrent requests")
    timeout: float = Field(default=5.0, ge=1.0, le=30.0, description="Request timeout in seconds")
    
    @validator('target_domain')
    def validate_domain(cls, v):
        if not v or '.' not in v:
            raise ValueError("Invalid domain format")
        return v.lower()

class SubdomainEnumerationResult(BaseModel):
    """Pydantic model for subdomain enumeration result."""
    target_domain: str
    discovered_subdomains: List[str]
    total_subdomains_checked: int
    enumeration_duration: float
    enumeration_completed_at: float

# Common subdomain wordlist
COMMON_SUBDOMAINS = [
    "www", "mail", "ftp", "admin", "blog", "api", "dev", "test", "stage", "prod",
    "app", "cdn", "dns", "ns1", "ns2", "mx", "smtp", "pop", "imap", "webmail",
    "remote", "vpn", "ssh", "telnet", "database", "db", "mysql", "postgres",
    "redis", "cache", "static", "media", "files", "upload", "download",
    "secure", "ssl", "cert", "auth", "login", "portal", "dashboard",
    "support", "help", "docs", "wiki", "forum", "chat", "irc", "git",
    "svn", "jenkins", "ci", "build", "deploy", "monitor", "nagios",
    "zabbix", "grafana", "kibana", "elasticsearch", "logstash", "redis",
    "memcached", "rabbitmq", "kafka", "zookeeper", "etcd", "consul",
    "vault", "ldap", "kerberos", "radius", "tacacs", "syslog", "ntp",
    "dhcp", "dns", "bind", "powerdns", "unbound", "dnsmasq"
]

async def enumerate_dns_records_async(data: DNSEnumerationRequest) -> DNSEnumerationResult:
    """Enumerate DNS records asynchronously."""
    target_domain = data.target_domain
    record_types = data.record_types
    nameservers = data.nameservers
    timeout = data.timeout
    max_concurrent = data.max_concurrent_queries
    
    start_time = time.time()
    all_records = []
    total_queries = 0
    successful_queries = 0
    failed_queries = 0
    
    # Configure DNS resolver
    resolver = dns.resolver.Resolver()
    if nameservers:
        resolver.nameservers = nameservers
    resolver.timeout = timeout
    resolver.lifetime = timeout
    
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def query_dns_record(record_type: DNSRecordType) -> List[DNSRecord]:
        async with semaphore:
            nonlocal total_queries, successful_queries, failed_queries
            
            try:
                total_queries += 1
                
                # Run DNS query in thread pool
                loop = asyncio.get_event_loop()
                answers = await loop.run_in_executor(
                    None,
                    lambda: resolver.resolve(target_domain, record_type.value)
                )
                
                successful_queries += 1
                records = []
                
                for answer in answers:
                    record = DNSRecord(
                        record_type=record_type,
                        name=target_domain,
                        value=str(answer),
                        ttl=getattr(answer, 'ttl', None)
                    )
                    
                    # Handle MX records with priority
                    if record_type == DNSRecordType.MX:
                        record.priority = answer.preference
                        record.value = str(answer.exchange)
                    
                    records.append(record)
                
                return records
                
            except Exception as e:
                failed_queries += 1
                print(f"DNS query failed for {record_type.value}: {e}")
                return []
    
    # Create tasks for all record types
    tasks = [query_dns_record(record_type) for record_type in record_types]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Collect all records
    for result in results:
        if isinstance(result, list):
            all_records.extend(result)
    
    enumeration_duration = time.time() - start_time
    
    return DNSEnumerationResult(
        target_domain=target_domain,
        records_found=all_records,
        nameservers=nameservers or ["8.8.8.8", "8.8.4.4"],  # Default to Google DNS
        enumeration_duration=enumeration_duration,
        total_queries=total_queries,
        successful_queries=successful_queries,
        failed_queries=failed_queries,
        enumeration_completed_at=time.time()
    )

async def enumerate_dns_subdomains_async(data: SubdomainEnumerationRequest) -> SubdomainEnumerationResult:
    """Enumerate subdomains asynchronously."""
    target_domain = data.target_domain
    wordlist = data.wordlist
    use_common_wordlist = data.use_common_wordlist
    max_concurrent = data.max_concurrent_requests
    timeout = data.timeout
    
    start_time = time.time()
    
    # Combine wordlists
    if use_common_wordlist:
        wordlist = list(set(wordlist + COMMON_SUBDOMAINS))
    
    discovered_subdomains = []
    total_checked = 0
    
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def check_subdomain(subdomain: str) -> Optional[str]:
        async with semaphore:
            nonlocal total_checked
            
            try:
                full_domain = f"{subdomain}.{target_domain}"
                total_checked += 1
                
                # Run DNS query in thread pool
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None,
                    lambda: socket.gethostbyname(full_domain)
                )
                
                return full_domain
                
            except socket.gaierror:
                return None
            except Exception as e:
                print(f"Error checking subdomain {subdomain}: {e}")
                return None
    
    # Create tasks for all subdomains
    tasks = [check_subdomain(subdomain) for subdomain in wordlist]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Collect discovered subdomains
    for result in results:
        if isinstance(result, str):
            discovered_subdomains.append(result)
    
    enumeration_duration = time.time() - start_time
    
    return SubdomainEnumerationResult(
        target_domain=target_domain,
        discovered_subdomains=discovered_subdomains,
        total_subdomains_checked=total_checked,
        enumeration_duration=enumeration_duration,
        enumeration_completed_at=time.time()
    )

async def perform_dns_zone_transfer_async(data: DNSEnumerationRequest) -> DNSEnumerationResult:
    """Attempt DNS zone transfer asynchronously."""
    target_domain = data.target_domain
    nameservers = data.nameservers
    timeout = data.timeout
    
    start_time = time.time()
    zone_records = []
    total_queries = 0
    successful_queries = 0
    failed_queries = 0
    
    # Get nameservers if not provided
    if not nameservers:
        try:
            loop = asyncio.get_event_loop()
            ns_answers = await loop.run_in_executor(
                None,
                lambda: dns.resolver.resolve(target_domain, 'NS')
            )
            nameservers = [str(ns) for ns in ns_answers]
        except Exception as e:
            print(f"Failed to get nameservers: {e}")
            nameservers = ["8.8.8.8"]
    
    async def attempt_zone_transfer(nameserver: str) -> List[DNSRecord]:
        nonlocal total_queries, successful_queries, failed_queries
        
        try:
            total_queries += 1
            
            # Attempt zone transfer
            loop = asyncio.get_event_loop()
            zone = await loop.run_in_executor(
                None,
                lambda: dns.zone.from_xfr(dns.query.xfr(nameserver, target_domain, timeout=timeout))
            )
            
            successful_queries += 1
            records = []
            
            for name, node in zone.nodes.items():
                for rdataset in node.rdatasets:
                    for rdata in rdataset:
                        record = DNSRecord(
                            record_type=DNSRecordType(rdataset.rdtype.name),
                            name=str(name),
                            value=str(rdata),
                            ttl=rdataset.ttl
                        )
                        records.append(record)
            
            return records
            
        except Exception as e:
            failed_queries += 1
            print(f"Zone transfer failed for {nameserver}: {e}")
            return []
    
    # Attempt zone transfer on all nameservers
    tasks = [attempt_zone_transfer(ns) for ns in nameservers]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Collect all records
    for result in results:
        if isinstance(result, list):
            zone_records.extend(result)
    
    enumeration_duration = time.time() - start_time
    
    return DNSEnumerationResult(
        target_domain=target_domain,
        records_found=zone_records,
        nameservers=nameservers,
        enumeration_duration=enumeration_duration,
        total_queries=total_queries,
        successful_queries=successful_queries,
        failed_queries=failed_queries,
        enumeration_completed_at=time.time()
    )

async def check_dns_brute_force_async(data: SubdomainEnumerationRequest) -> SubdomainEnumerationResult:
    """Perform DNS brute force enumeration asynchronously."""
    # This is essentially the same as subdomain enumeration but with a larger wordlist
    return await enumerate_dns_subdomains_async(data) 