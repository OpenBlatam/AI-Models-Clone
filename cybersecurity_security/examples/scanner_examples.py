"""
Scanner Examples

Demonstrates how to use the comprehensive scanner modules.
"""

import asyncio
import time
from typing import Dict, Any

# Import scanner modules
from ..scanners import (
    # Port Scanner
    PortScanRequest, PortRangeScanRequest, scan_port_async, scan_port_range_async,
    
    # Vulnerability Scanner
    VulnerabilityScanRequest, VulnerabilityType, scan_vulnerabilities_async,
    
    # Web Scanner
    WebScanRequest, WebVulnerabilityType, scan_web_application_async
)

async def run_port_scanner_examples() -> Dict[str, Any]:
    """Run port scanner examples."""
    print("🔍 Running Port Scanner Examples...")
    
    results = {}
    
    # 1. Single port scan
    print("1. Testing Single Port Scan...")
    port_request = PortScanRequest(
        target_host="localhost",
        port=80,
        timeout=2.0
    )
    port_result = await scan_port_async(port_request)
    results["single_port"] = port_result
    print(f"   Port {port_result.port} is {'open' if port_result.is_open else 'closed'}")
    
    # 2. Port range scan
    print("2. Testing Port Range Scan...")
    range_request = PortRangeScanRequest(
        target_host="localhost",
        start_port=80,
        end_port=90,
        max_workers=5,
        timeout=2.0
    )
    range_result = await scan_port_range_async(range_request)
    results["port_range"] = range_result
    print(f"   Found {range_result.open_port_count} open ports out of {range_result.total_ports_scanned}")
    
    return results

async def run_vulnerability_scanner_examples() -> Dict[str, Any]:
    """Run vulnerability scanner examples."""
    print("🛡️ Running Vulnerability Scanner Examples...")
    
    results = {}
    
    # 1. SQL Injection scan
    print("1. Testing SQL Injection Scan...")
    sql_request = VulnerabilityScanRequest(
        target_url="http://localhost:8000",
        scan_types=[VulnerabilityType.SQL_INJECTION],
        max_concurrent_requests=5,
        timeout=10.0
    )
    sql_result = await scan_vulnerabilities_async(sql_request)
    results["sql_injection"] = sql_result
    print(f"   SQL Injection scan completed: {sql_result.risk_level} risk")
    
    # 2. XSS scan
    print("2. Testing XSS Scan...")
    xss_request = VulnerabilityScanRequest(
        target_url="http://localhost:8000",
        scan_types=[VulnerabilityType.XSS],
        max_concurrent_requests=5,
        timeout=10.0
    )
    xss_result = await scan_vulnerabilities_async(xss_request)
    results["xss"] = xss_result
    print(f"   XSS scan completed: {xss_result.risk_level} risk")
    
    # 3. Comprehensive vulnerability scan
    print("3. Testing Comprehensive Vulnerability Scan...")
    comprehensive_request = VulnerabilityScanRequest(
        target_url="http://localhost:8000",
        scan_types=[
            VulnerabilityType.SQL_INJECTION,
            VulnerabilityType.XSS,
            VulnerabilityType.CSRF,
            VulnerabilityType.FILE_INCLUSION
        ],
        max_concurrent_requests=10,
        timeout=15.0
    )
    comprehensive_result = await scan_vulnerabilities_async(comprehensive_request)
    results["comprehensive"] = comprehensive_result
    print(f"   Comprehensive scan completed: {comprehensive_result.risk_level} risk")
    print(f"   Found {len(comprehensive_result.vulnerabilities_found)} vulnerabilities")
    
    return results

async def run_web_scanner_examples() -> Dict[str, Any]:
    """Run web scanner examples."""
    print("🌐 Running Web Scanner Examples...")
    
    results = {}
    
    # 1. Directory enumeration
    print("1. Testing Directory Enumeration...")
    dir_request = WebScanRequest(
        target_url="http://localhost:8000",
        scan_types=[WebVulnerabilityType.DIRECTORY_ENUMERATION],
        common_directories=["admin", "login", "config", "backup"],
        max_concurrent_requests=5,
        timeout=10.0
    )
    dir_result = await scan_web_application_async(dir_request)
    results["directory_enumeration"] = dir_result
    print(f"   Directory enumeration completed: {len(dir_result.discovered_directories)} directories found")
    
    # 2. Security headers scan
    print("2. Testing Security Headers Scan...")
    headers_request = WebScanRequest(
        target_url="http://localhost:8000",
        scan_types=[WebVulnerabilityType.INSECURE_HEADERS],
        max_concurrent_requests=5,
        timeout=10.0
    )
    headers_result = await scan_web_application_async(headers_request)
    results["security_headers"] = headers_result
    print(f"   Security headers scan completed: {len(headers_result.security_headers)} headers analyzed")
    
    # 3. Robots.txt and sitemap scan
    print("3. Testing Robots.txt and Sitemap Scan...")
    info_request = WebScanRequest(
        target_url="http://localhost:8000",
        scan_types=[
            WebVulnerabilityType.ROBOTS_TXT_EXPOSURE,
            WebVulnerabilityType.SITEMAP_EXPOSURE
        ],
        max_concurrent_requests=5,
        timeout=10.0
    )
    info_result = await scan_web_application_async(info_request)
    results["information_disclosure"] = info_result
    print(f"   Information disclosure scan completed: {len(info_result.vulnerabilities_found)} issues found")
    
    # 4. SSL certificate scan (for HTTPS)
    print("4. Testing SSL Certificate Scan...")
    ssl_request = WebScanRequest(
        target_url="https://example.com",  # Using HTTPS for SSL test
        scan_types=[WebVulnerabilityType.SSL_CERTIFICATE_ISSUES],
        max_concurrent_requests=5,
        timeout=10.0
    )
    ssl_result = await scan_web_application_async(ssl_request)
    results["ssl_certificate"] = ssl_result
    print(f"   SSL certificate scan completed: {ssl_result.risk_level} risk")
    
    # 5. Comprehensive web scan
    print("5. Testing Comprehensive Web Scan...")
    comprehensive_request = WebScanRequest(
        target_url="http://localhost:8000",
        scan_types=list(WebVulnerabilityType),
        common_directories=["admin", "login", "config", "backup", "api", "docs"],
        max_concurrent_requests=10,
        timeout=20.0
    )
    comprehensive_result = await scan_web_application_async(comprehensive_request)
    results["comprehensive_web"] = comprehensive_result
    print(f"   Comprehensive web scan completed: {comprehensive_result.risk_level} risk")
    print(f"   Found {len(comprehensive_result.vulnerabilities_found)} vulnerabilities")
    print(f"   Discovered {len(comprehensive_result.discovered_directories)} directories")
    
    return results

async def run_integrated_scanner_examples() -> Dict[str, Any]:
    """Run integrated scanner examples combining all scanner types."""
    print("🔗 Running Integrated Scanner Examples...")
    
    results = {}
    
    # Target for comprehensive security assessment
    target_url = "http://localhost:8000"
    target_host = "localhost"
    
    print(f"Performing comprehensive security assessment on {target_url}")
    
    # Run all scanner types concurrently
    port_results, vuln_results, web_results = await asyncio.gather(
        run_port_scanner_examples(),
        run_vulnerability_scanner_examples(),
        run_web_scanner_examples(),
        return_exceptions=True
    )
    
    # Compile comprehensive report
    comprehensive_report = {
        "target_url": target_url,
        "target_host": target_host,
        "assessment_timestamp": time.time(),
        "port_scan_results": port_results if not isinstance(port_results, Exception) else {"error": str(port_results)},
        "vulnerability_scan_results": vuln_results if not isinstance(vuln_results, Exception) else {"error": str(vuln_results)},
        "web_scan_results": web_results if not isinstance(web_results, Exception) else {"error": str(web_results)},
        "overall_risk_assessment": {
            "port_risk": "LOW",  # Default, would be calculated from results
            "vulnerability_risk": "LOW",  # Default, would be calculated from results
            "web_risk": "LOW",  # Default, would be calculated from results
            "overall_risk": "LOW"
        }
    }
    
    # Calculate overall risk (simplified)
    risk_scores = []
    if not isinstance(port_results, Exception):
        risk_scores.append(1)  # Simplified scoring
    if not isinstance(vuln_results, Exception):
        risk_scores.append(2)  # Vulnerability scans are higher risk
    if not isinstance(web_results, Exception):
        risk_scores.append(1)  # Simplified scoring
    
    if risk_scores:
        avg_risk = sum(risk_scores) / len(risk_scores)
        if avg_risk > 2:
            comprehensive_report["overall_risk_assessment"]["overall_risk"] = "HIGH"
        elif avg_risk > 1:
            comprehensive_report["overall_risk_assessment"]["overall_risk"] = "MEDIUM"
    
    results["comprehensive_assessment"] = comprehensive_report
    print(f"   Comprehensive assessment completed: {comprehensive_report['overall_risk_assessment']['overall_risk']} risk")
    
    return results

async def main():
    """Main function to run all scanner examples."""
    print("🔒 Cybersecurity Scanner Toolkit Examples")
    print("=" * 60)
    
    try:
        # Run individual scanner examples
        print("\n📡 Port Scanner Examples")
        print("-" * 30)
        port_results = await run_port_scanner_examples()
        
        print("\n🛡️ Vulnerability Scanner Examples")
        print("-" * 30)
        vuln_results = await run_vulnerability_scanner_examples()
        
        print("\n🌐 Web Scanner Examples")
        print("-" * 30)
        web_results = await run_web_scanner_examples()
        
        print("\n🔗 Integrated Scanner Examples")
        print("-" * 30)
        integrated_results = await run_integrated_scanner_examples()
        
        print("\n" + "=" * 60)
        print("✅ All scanner examples completed successfully!")
        
        # Summary
        print("\n📊 Scanner Summary:")
        print(f"   Port scans: {len(port_results)} completed")
        print(f"   Vulnerability scans: {len(vuln_results)} completed")
        print(f"   Web scans: {len(web_results)} completed")
        print(f"   Integrated assessments: {len(integrated_results)} completed")
        
        # Risk summary
        if "comprehensive_assessment" in integrated_results:
            overall_risk = integrated_results["comprehensive_assessment"]["overall_risk_assessment"]["overall_risk"]
            print(f"   Overall risk level: {overall_risk}")
        
    except Exception as e:
        print(f"❌ Error running scanner examples: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 