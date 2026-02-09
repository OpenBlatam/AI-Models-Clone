"""
Network optimization service following functional patterns
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, text
import uuid
import asyncio
import aiohttp
import time
import json
import gzip
import brotli
import ssl
import socket
from urllib.parse import urlparse
import psutil
import subprocess

from app.core.logging import get_logger
from app.core.errors import handle_validation_error, handle_internal_error
from app.models.network import NetworkOptimization, NetworkStats, NetworkAlert
from app.schemas.network import (
    NetworkOptimizationResponse, NetworkStatsResponse, NetworkAlertResponse,
    NetworkAnalysisResponse, NetworkPerformanceResponse, CDNOptimizationResponse
)
from app.utils.validators import validate_url, validate_network_config
from app.utils.helpers import calculate_network_latency, format_bandwidth
from app.utils.cache import cache_network_data, get_cached_network_data

logger = get_logger(__name__)

# Network monitoring data
_network_stats: Dict[str, Dict[str, Any]] = {}
_network_alerts: List[Dict[str, Any]] = []


async def analyze_network_performance(
    target_urls: Optional[List[str]] = None,
    db: AsyncSession = None
) -> NetworkAnalysisResponse:
    """Analyze network performance."""
    try:
        if not target_urls:
            target_urls = [
                "https://api.openai.com",
                "https://api.anthropic.com",
                "https://api.deepseek.com",
                "https://www.google.com"
            ]
        
        network_tests = []
        
        for url in target_urls:
            test_result = await perform_network_test(url)
            network_tests.append(test_result)
        
        # Calculate overall metrics
        total_tests = len(network_tests)
        successful_tests = len([t for t in network_tests if t["success"]])
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        avg_latency = sum(t["latency_ms"] for t in network_tests if t["success"]) / successful_tests if successful_tests > 0 else 0
        avg_bandwidth = sum(t["bandwidth_mbps"] for t in network_tests if t["success"]) / successful_tests if successful_tests > 0 else 0
        
        # Analyze network issues
        network_issues = []
        
        if success_rate < 95:
            network_issues.append("Low network connectivity success rate")
        
        if avg_latency > 500:
            network_issues.append("High network latency detected")
        
        if avg_bandwidth < 10:
            network_issues.append("Low bandwidth detected")
        
        # Check for DNS issues
        dns_issues = await check_dns_performance()
        if dns_issues:
            network_issues.extend(dns_issues)
        
        return NetworkAnalysisResponse(
            success_rate=round(success_rate, 2),
            average_latency_ms=round(avg_latency, 2),
            average_bandwidth_mbps=round(avg_bandwidth, 2),
            total_tests=total_tests,
            successful_tests=successful_tests,
            network_tests=network_tests,
            network_issues=network_issues,
            analyzed_at=datetime.utcnow()
        )
    
    except Exception as e:
        logger.error(f"Failed to analyze network performance: {e}")
        raise handle_internal_error(f"Failed to analyze network performance: {str(e)}")


async def perform_network_test(
    url: str,
    timeout: int = 10
) -> Dict[str, Any]:
    """Perform network test for a specific URL."""
    try:
        start_time = time.time()
        
        # Parse URL
        parsed_url = urlparse(url)
        host = parsed_url.hostname
        port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
        
        # Test DNS resolution
        dns_start = time.time()
        try:
            ip_address = socket.gethostbyname(host)
            dns_time = (time.time() - dns_start) * 1000
        except socket.gaierror:
            dns_time = None
            ip_address = None
        
        # Test TCP connection
        tcp_start = time.time()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            tcp_time = (time.time() - tcp_start) * 1000
            tcp_success = result == 0
        except Exception:
            tcp_time = None
            tcp_success = False
        
        # Test HTTP request
        http_start = time.time()
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                async with session.get(url) as response:
                    http_time = (time.time() - http_start) * 1000
                    http_success = response.status < 400
                    content_length = response.headers.get('content-length', 0)
                    content_length = int(content_length) if content_length else 0
        except Exception:
            http_time = None
            http_success = False
            content_length = 0
        
        # Calculate bandwidth (simplified)
        total_time = time.time() - start_time
        bandwidth_mbps = (content_length * 8 / 1024 / 1024 / total_time) if total_time > 0 and content_length > 0 else 0
        
        # Calculate overall latency
        latency_ms = dns_time or 0 + tcp_time or 0 + http_time or 0
        
        # Determine overall success
        success = dns_time is not None and tcp_success and http_success
        
        return {
            "url": url,
            "host": host,
            "ip_address": ip_address,
            "success": success,
            "latency_ms": round(latency_ms, 2),
            "dns_time_ms": round(dns_time, 2) if dns_time else None,
            "tcp_time_ms": round(tcp_time, 2) if tcp_time else None,
            "http_time_ms": round(http_time, 2) if http_time else None,
            "bandwidth_mbps": round(bandwidth_mbps, 2),
            "content_length_bytes": content_length,
            "tested_at": datetime.utcnow()
        }
    
    except Exception as e:
        logger.error(f"Failed to perform network test for {url}: {e}")
        return {
            "url": url,
            "success": False,
            "error": str(e),
            "tested_at": datetime.utcnow()
        }


async def check_dns_performance() -> List[str]:
    """Check DNS performance."""
    try:
        dns_issues = []
        
        # Test DNS resolution for common domains
        test_domains = [
            "google.com",
            "cloudflare.com",
            "amazonaws.com",
            "openai.com"
        ]
        
        for domain in test_domains:
            start_time = time.time()
            try:
                socket.gethostbyname(domain)
                dns_time = (time.time() - start_time) * 1000
                
                if dns_time > 1000:  # DNS resolution taking more than 1 second
                    dns_issues.append(f"Slow DNS resolution for {domain}: {dns_time:.2f}ms")
            except socket.gaierror:
                dns_issues.append(f"DNS resolution failed for {domain}")
        
        return dns_issues
    
    except Exception as e:
        logger.error(f"Failed to check DNS performance: {e}")
        return [f"Failed to check DNS performance: {str(e)}"]


async def optimize_network_connections(
    db: AsyncSession
) -> NetworkOptimizationResponse:
    """Optimize network connections."""
    try:
        optimizations = []
        
        # Analyze current network configuration
        network_config = await analyze_network_configuration()
        
        # Optimize TCP settings
        tcp_optimizations = await optimize_tcp_settings(network_config)
        optimizations.extend(tcp_optimizations)
        
        # Optimize DNS settings
        dns_optimizations = await optimize_dns_settings(network_config)
        optimizations.extend(dns_optimizations)
        
        # Optimize HTTP settings
        http_optimizations = await optimize_http_settings(network_config)
        optimizations.extend(http_optimizations)
        
        # Optimize SSL/TLS settings
        ssl_optimizations = await optimize_ssl_settings(network_config)
        optimizations.extend(ssl_optimizations)
        
        return NetworkOptimizationResponse(
            optimizations=optimizations,
            total_optimizations=len(optimizations),
            network_config=network_config,
            optimized_at=datetime.utcnow()
        )
    
    except Exception as e:
        logger.error(f"Failed to optimize network connections: {e}")
        raise handle_internal_error(f"Failed to optimize network connections: {str(e)}")


async def analyze_network_configuration() -> Dict[str, Any]:
    """Analyze current network configuration."""
    try:
        config = {}
        
        # Get network interfaces
        network_interfaces = psutil.net_if_addrs()
        config["interfaces"] = {
            name: {
                "addresses": [addr.address for addr in addrs],
                "family": [addr.family.name for addr in addrs]
            }
            for name, addrs in network_interfaces.items()
        }
        
        # Get network statistics
        network_stats = psutil.net_io_counters()
        config["network_stats"] = {
            "bytes_sent": network_stats.bytes_sent,
            "bytes_recv": network_stats.bytes_recv,
            "packets_sent": network_stats.packets_sent,
            "packets_recv": network_stats.packets_recv,
            "errin": network_stats.errin,
            "errout": network_stats.errout,
            "dropin": network_stats.dropin,
            "dropout": network_stats.dropout
        }
        
        # Get network connections
        connections = psutil.net_connections()
        config["connections"] = {
            "total": len(connections),
            "tcp": len([c for c in connections if c.type == socket.SOCK_STREAM]),
            "udp": len([c for c in connections if c.type == socket.SOCK_DGRAM]),
            "established": len([c for c in connections if c.status == "ESTABLISHED"]),
            "listening": len([c for c in connections if c.status == "LISTEN"])
        }
        
        # Get DNS configuration
        try:
            with open('/etc/resolv.conf', 'r') as f:
                dns_config = f.read()
            config["dns_config"] = dns_config
        except Exception:
            config["dns_config"] = "Unable to read DNS configuration"
        
        return config
    
    except Exception as e:
        logger.error(f"Failed to analyze network configuration: {e}")
        return {"error": str(e)}


async def optimize_tcp_settings(
    network_config: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Optimize TCP settings."""
    try:
        optimizations = []
        
        # Check TCP window scaling
        optimizations.append({
            "type": "tcp_optimization",
            "setting": "tcp_window_scaling",
            "current_value": "unknown",
            "recommended_value": "enabled",
            "description": "Enable TCP window scaling for better performance on high-latency connections"
        })
        
        # Check TCP congestion control
        optimizations.append({
            "type": "tcp_optimization",
            "setting": "tcp_congestion_control",
            "current_value": "unknown",
            "recommended_value": "bbr",
            "description": "Use BBR congestion control algorithm for better throughput"
        })
        
        # Check TCP keepalive
        optimizations.append({
            "type": "tcp_optimization",
            "setting": "tcp_keepalive",
            "current_value": "unknown",
            "recommended_value": "enabled",
            "description": "Enable TCP keepalive to detect dead connections"
        })
        
        return optimizations
    
    except Exception as e:
        logger.error(f"Failed to optimize TCP settings: {e}")
        return []


async def optimize_dns_settings(
    network_config: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Optimize DNS settings."""
    try:
        optimizations = []
        
        # Check DNS servers
        dns_config = network_config.get("dns_config", "")
        if "8.8.8.8" not in dns_config and "1.1.1.1" not in dns_config:
            optimizations.append({
                "type": "dns_optimization",
                "setting": "dns_servers",
                "current_value": "default",
                "recommended_value": "8.8.8.8, 1.1.1.1",
                "description": "Use fast DNS servers like Google DNS or Cloudflare DNS"
            })
        
        # Check DNS cache
        optimizations.append({
            "type": "dns_optimization",
            "setting": "dns_cache",
            "current_value": "unknown",
            "recommended_value": "enabled",
            "description": "Enable DNS caching to reduce resolution time"
        })
        
        return optimizations
    
    except Exception as e:
        logger.error(f"Failed to optimize DNS settings: {e}")
        return []


async def optimize_http_settings(
    network_config: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Optimize HTTP settings."""
    try:
        optimizations = []
        
        # HTTP/2 support
        optimizations.append({
            "type": "http_optimization",
            "setting": "http2_support",
            "current_value": "unknown",
            "recommended_value": "enabled",
            "description": "Enable HTTP/2 for better performance and multiplexing"
        })
        
        # HTTP keep-alive
        optimizations.append({
            "type": "http_optimization",
            "setting": "http_keepalive",
            "current_value": "unknown",
            "recommended_value": "enabled",
            "description": "Enable HTTP keep-alive to reuse connections"
        })
        
        # Compression
        optimizations.append({
            "type": "http_optimization",
            "setting": "compression",
            "current_value": "unknown",
            "recommended_value": "gzip, brotli",
            "description": "Enable compression to reduce bandwidth usage"
        })
        
        return optimizations
    
    except Exception as e:
        logger.error(f"Failed to optimize HTTP settings: {e}")
        return []


async def optimize_ssl_settings(
    network_config: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Optimize SSL/TLS settings."""
    try:
        optimizations = []
        
        # TLS version
        optimizations.append({
            "type": "ssl_optimization",
            "setting": "tls_version",
            "current_value": "unknown",
            "recommended_value": "TLS 1.3",
            "description": "Use TLS 1.3 for better performance and security"
        })
        
        # Cipher suites
        optimizations.append({
            "type": "ssl_optimization",
            "setting": "cipher_suites",
            "current_value": "unknown",
            "recommended_value": "ECDHE-RSA-AES256-GCM-SHA384",
            "description": "Use modern cipher suites for better performance"
        })
        
        # Session resumption
        optimizations.append({
            "type": "ssl_optimization",
            "setting": "session_resumption",
            "current_value": "unknown",
            "recommended_value": "enabled",
            "description": "Enable SSL session resumption to reduce handshake overhead"
        })
        
        return optimizations
    
    except Exception as e:
        logger.error(f"Failed to optimize SSL settings: {e}")
        return []


async def implement_cdn_optimization(
    cdn_config: Dict[str, Any],
    db: AsyncSession
) -> CDNOptimizationResponse:
    """Implement CDN optimization."""
    try:
        optimizations = []
        
        # Analyze current CDN configuration
        cdn_analysis = await analyze_cdn_performance(cdn_config)
        
        # Optimize CDN settings
        if cdn_analysis.get("cache_hit_rate", 0) < 80:
            optimizations.append({
                "type": "cdn_optimization",
                "setting": "cache_ttl",
                "current_value": cdn_config.get("cache_ttl", "unknown"),
                "recommended_value": "3600",
                "description": "Increase cache TTL to improve hit rate"
            })
        
        if cdn_analysis.get("compression_ratio", 0) < 0.7:
            optimizations.append({
                "type": "cdn_optimization",
                "setting": "compression",
                "current_value": cdn_config.get("compression", "unknown"),
                "recommended_value": "gzip, brotli",
                "description": "Enable compression to reduce bandwidth usage"
            })
        
        if cdn_analysis.get("edge_locations", 0) < 10:
            optimizations.append({
                "type": "cdn_optimization",
                "setting": "edge_locations",
                "current_value": cdn_config.get("edge_locations", "unknown"),
                "recommended_value": "global",
                "description": "Use global edge locations for better performance"
            })
        
        return CDNOptimizationResponse(
            optimizations=optimizations,
            total_optimizations=len(optimizations),
            cdn_analysis=cdn_analysis,
            optimized_at=datetime.utcnow()
        )
    
    except Exception as e:
        logger.error(f"Failed to implement CDN optimization: {e}")
        raise handle_internal_error(f"Failed to implement CDN optimization: {str(e)}")


async def analyze_cdn_performance(
    cdn_config: Dict[str, Any]
) -> Dict[str, Any]:
    """Analyze CDN performance."""
    try:
        # This would implement actual CDN analysis
        # For now, returning placeholder data
        return {
            "cache_hit_rate": 75.5,
            "compression_ratio": 0.65,
            "edge_locations": 5,
            "bandwidth_saved_mbps": 100.5,
            "latency_reduction_ms": 50.2
        }
    
    except Exception as e:
        logger.error(f"Failed to analyze CDN performance: {e}")
        return {}


async def monitor_network_health(
    db: AsyncSession
) -> NetworkStatsResponse:
    """Monitor network health in real-time."""
    try:
        # Get network statistics
        network_stats = psutil.net_io_counters()
        
        # Get network connections
        connections = psutil.net_connections()
        
        # Calculate network metrics
        total_connections = len(connections)
        established_connections = len([c for c in connections if c.status == "ESTABLISHED"])
        listening_connections = len([c for c in connections if c.status == "LISTEN"])
        
        # Calculate bandwidth usage
        bandwidth_sent_mbps = network_stats.bytes_sent / 1024 / 1024
        bandwidth_recv_mbps = network_stats.bytes_recv / 1024 / 1024
        
        # Check for network issues
        network_issues = []
        
        if network_stats.errin > 0 or network_stats.errout > 0:
            network_issues.append("Network errors detected")
        
        if network_stats.dropin > 0 or network_stats.dropout > 0:
            network_issues.append("Network packet drops detected")
        
        if established_connections > total_connections * 0.9:
            network_issues.append("High connection utilization")
        
        # Determine health status
        if len(network_issues) == 0:
            status = "healthy"
        elif len(network_issues) <= 2:
            status = "warning"
        else:
            status = "critical"
        
        return NetworkStatsResponse(
            status=status,
            total_connections=total_connections,
            established_connections=established_connections,
            listening_connections=listening_connections,
            bandwidth_sent_mbps=round(bandwidth_sent_mbps, 2),
            bandwidth_recv_mbps=round(bandwidth_recv_mbps, 2),
            network_errors=network_stats.errin + network_stats.errout,
            packet_drops=network_stats.dropin + network_stats.dropout,
            network_issues=network_issues,
            monitored_at=datetime.utcnow()
        )
    
    except Exception as e:
        logger.error(f"Failed to monitor network health: {e}")
        return NetworkStatsResponse(
            status="unknown",
            total_connections=0,
            established_connections=0,
            listening_connections=0,
            bandwidth_sent_mbps=0,
            bandwidth_recv_mbps=0,
            network_errors=0,
            packet_drops=0,
            network_issues=[f"Failed to monitor: {str(e)}"],
            monitored_at=datetime.utcnow()
        )


async def create_network_performance_report(
    db: AsyncSession
) -> NetworkPerformanceResponse:
    """Create comprehensive network performance report."""
    try:
        # Analyze network performance
        network_analysis = await analyze_network_performance()
        
        # Monitor network health
        network_health = await monitor_network_health(db)
        
        # Get network optimizations
        network_optimizations = await optimize_network_connections(db)
        
        # Calculate performance score
        performance_score = 100
        
        if network_analysis.success_rate < 95:
            performance_score -= 20
        
        if network_analysis.average_latency_ms > 500:
            performance_score -= 15
        
        if network_analysis.average_bandwidth_mbps < 10:
            performance_score -= 10
        
        if len(network_analysis.network_issues) > 0:
            performance_score -= len(network_analysis.network_issues) * 5
        
        performance_score = max(0, performance_score)
        
        # Generate recommendations
        recommendations = []
        
        if network_analysis.success_rate < 95:
            recommendations.append("Network connectivity issues detected. Check DNS and routing.")
        
        if network_analysis.average_latency_ms > 500:
            recommendations.append("High latency detected. Consider CDN or closer servers.")
        
        if network_analysis.average_bandwidth_mbps < 10:
            recommendations.append("Low bandwidth detected. Consider upgrading connection.")
        
        if len(network_optimizations.optimizations) > 0:
            recommendations.append(f"Found {len(network_optimizations.optimizations)} network optimization opportunities.")
        
        return NetworkPerformanceResponse(
            performance_score=performance_score,
            network_analysis=network_analysis,
            network_health=network_health,
            network_optimizations=network_optimizations,
            recommendations=recommendations,
            generated_at=datetime.utcnow()
        )
    
    except Exception as e:
        logger.error(f"Failed to create network performance report: {e}")
        raise handle_internal_error(f"Failed to create network performance report: {str(e)}")


async def test_network_connectivity(
    target_hosts: List[str],
    timeout: int = 5
) -> Dict[str, Any]:
    """Test network connectivity to target hosts."""
    try:
        results = []
        
        for host in target_hosts:
            start_time = time.time()
            try:
                # Test ping (simplified)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                result = sock.connect_ex((host, 80))
                sock.close()
                
                success = result == 0
                latency = (time.time() - start_time) * 1000
                
                results.append({
                    "host": host,
                    "success": success,
                    "latency_ms": round(latency, 2),
                    "tested_at": datetime.utcnow()
                })
            
            except Exception as e:
                results.append({
                    "host": host,
                    "success": False,
                    "error": str(e),
                    "tested_at": datetime.utcnow()
                })
        
        # Calculate overall connectivity
        successful_tests = len([r for r in results if r["success"]])
        total_tests = len(results)
        connectivity_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        return {
            "connectivity_rate": round(connectivity_rate, 2),
            "successful_tests": successful_tests,
            "total_tests": total_tests,
            "results": results,
            "tested_at": datetime.utcnow()
        }
    
    except Exception as e:
        logger.error(f"Failed to test network connectivity: {e}")
        return {
            "connectivity_rate": 0,
            "successful_tests": 0,
            "total_tests": len(target_hosts),
            "results": [],
            "error": str(e),
            "tested_at": datetime.utcnow()
        }




