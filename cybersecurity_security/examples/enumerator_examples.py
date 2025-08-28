from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
TIMEOUT_SECONDS = 60

import asyncio
import time
from typing import Dict, Any
from ..enumerators import (
from typing import Any, List, Dict, Optional
import logging
"""
Enumerator Examples

Demonstrates how to use the comprehensive enumerator modules.
"""


# Import enumerator modules
    # DNS Enumerator
    DNSEnumerationRequest, DNSRecordType, enumerate_dns_records_async,
    SubdomainEnumerationRequest, enumerate_dns_subdomains_async,
    perform_dns_zone_transfer_async,
    
    # SMB Enumerator
    SMBEnumerationRequest, enumerate_smb_async,
    
    # SSH Enumerator
    SSHEnumerationRequest, enumerate_ssh_async
)

async def run_dns_enumerator_examples() -> Dict[str, Any]:
    """Run DNS enumerator examples."""
    print("🌐 Running DNS Enumerator Examples...")
    
    results = {}
    
    # 1. DNS record enumeration
    print("1. Testing DNS Record Enumeration...")
    dns_request = DNSEnumerationRequest(
        target_domain="example.com",
        record_types=[
            DNSRecordType.A,
            DNSRecordType.MX,
            DNSRecordType.NS,
            DNSRecordType.TXT
        ],
        nameservers=["8.8.8.8", "8.8.4.4"],
        timeout=10.0
    )
    dns_result = await enumerate_dns_records_async(dns_request)
    results["dns_records"] = dns_result
    print(f"   Found {len(dns_result.records_found)} DNS records")
    print(f"   Successful queries: {dns_result.successful_queries}")
    
    # 2. Subdomain enumeration
    print("2. Testing Subdomain Enumeration...")
    subdomain_request = SubdomainEnumerationRequest(
        target_domain="example.com",
        wordlist=["www", "mail", "ftp", "admin", "api", "dev", "test"],
        use_common_wordlist=True,
        max_concurrent_requests=10,
        timeout=5.0
    )
    subdomain_result = await enumerate_dns_subdomains_async(subdomain_request)
    results["subdomains"] = subdomain_result
    print(f"   Discovered {len(subdomain_result.discovered_subdomains)} subdomains")
    print(f"   Checked {subdomain_result.total_subdomains_checked} subdomains")
    
    # 3. DNS zone transfer attempt
    print("3. Testing DNS Zone Transfer...")
    zone_request = DNSEnumerationRequest(
        target_domain="example.com",
        record_types=[DNSRecordType.ANY],
        timeout=10.0
    )
    zone_result = await perform_dns_zone_transfer_async(zone_request)
    results["zone_transfer"] = zone_result
    print(f"   Zone transfer found {len(zone_result.records_found)} records")
    print(f"   Zone transfer successful: {zone_result.successful_queries > 0}")
    
    return results

async def run_smb_enumerator_examples() -> Dict[str, Any]:
    """Run SMB enumerator examples."""
    print("💾 Running SMB Enumerator Examples...")
    
    results = {}
    
    # 1. SMB share enumeration
    print("1. Testing SMB Share Enumeration...")
    smb_request = SMBEnumerationRequest(
        target_host="localhost",  # Use localhost for testing
        target_port=445,
        username=None,  # Anonymous enumeration
        password=None,
        domain=None,
        timeout=10.0,
        max_concurrent_connections=5
    )
    smb_result = await enumerate_smb_async(smb_request)
    results["smb_enumeration"] = smb_result
    print(f"   Found {len(smb_result.shares_found)} SMB shares")
    print(f"   Found {len(smb_result.users_found)} SMB users")
    print(f"   Null sessions allowed: {smb_result.null_session_allowed}")
    
    # 2. SMB security assessment
    print("2. Testing SMB Security Assessment...")
    security_info = {
        "shares": [share.share_name for share in smb_result.shares_found],
        "users": [user.username for user in smb_result.users_found],
        "policies": len(smb_result.policies_found),
        "null_session_vulnerability": smb_result.null_session_allowed,
        "total_connections": smb_result.total_connections,
        "successful_connections": smb_result.successful_connections
    }
    results["smb_security"] = security_info
    print(f"   Security assessment completed")
    print(f"   Vulnerabilities found: {smb_result.null_session_allowed}")
    
    return results

async def run_ssh_enumerator_examples() -> Dict[str, Any]:
    """Run SSH enumerator examples."""
    print("🔐 Running SSH Enumerator Examples...")
    
    results = {}
    
    # 1. SSH version and server information
    print("1. Testing SSH Version Enumeration...")
    ssh_request = SSHEnumerationRequest(
        target_host="localhost",  # Use localhost for testing
        target_port=22,
        timeout=10.0,
        perform_brute_force=False,  # Disable brute force for safety
        username_list=[],
        password_list=[],
        max_concurrent_connections=5
    )
    ssh_result = await enumerate_ssh_async(ssh_request)
    results["ssh_enumeration"] = ssh_result
    print(f"   SSH protocol version: {ssh_result.server_info.protocol_version}")
    print(f"   SSH software version: {ssh_result.server_info.software_version}")
    print(f"   SSH banner: {ssh_result.server_info.banner}")
    
    # 2. SSH algorithm analysis
    print("2. Testing SSH Algorithm Analysis...")
    algorithm_analysis = ssh_result.security_assessment.get("algorithm_analysis", {})
    if isinstance(algorithm_analysis, dict):
        for category, info in algorithm_analysis.items():
            if isinstance(info, dict):
                supported = len(info.get("supported", []))
                weak = len(info.get("weak", []))
                strong = len(info.get("strong", []))
                print(f"   {category.upper()}: {supported} supported, {weak} weak, {strong} strong")
    
    # 3. SSH security assessment
    print("3. Testing SSH Security Assessment...")
    security_assessment = ssh_result.security_assessment
    weak_algorithms = security_assessment.get("weak_algorithms_found", 0)
    strong_algorithms = security_assessment.get("strong_algorithms_found", 0)
    recommendations = security_assessment.get("recommendations", [])
    
    results["ssh_security"] = {
        "weak_algorithms": weak_algorithms,
        "strong_algorithms": strong_algorithms,
        "recommendations": recommendations,
        "total_connections": ssh_result.total_connections,
        "successful_connections": ssh_result.successful_connections
    }
    
    print(f"   Weak algorithms found: {weak_algorithms}")
    print(f"   Strong algorithms found: {strong_algorithms}")
    print(f"   Security recommendations: {len(recommendations)}")
    
    return results

async def run_integrated_enumerator_examples() -> Dict[str, Any]:
    """Run integrated enumerator examples combining all enumerator types."""
    print("🔗 Running Integrated Enumerator Examples...")
    
    results = {}
    
    # Target for comprehensive enumeration
    target_host = "localhost"
    target_domain = "example.com"
    
    print(f"Performing comprehensive enumeration on {target_host}")
    
    # Run all enumerator types concurrently
    dns_results, smb_results, ssh_results = await asyncio.gather(
        run_dns_enumerator_examples(),
        run_smb_enumerator_examples(),
        run_ssh_enumerator_examples(),
        return_exceptions=True
    )
    
    # Compile comprehensive report
    comprehensive_report = {
        "target_host": target_host,
        "target_domain": target_domain,
        "enumeration_timestamp": time.time(),
        "dns_enumeration_results": dns_results if not isinstance(dns_results, Exception) else {"error": str(dns_results)},
        "smb_enumeration_results": smb_results if not isinstance(smb_results, Exception) else {"error": str(smb_results)},
        "ssh_enumeration_results": ssh_results if not isinstance(ssh_results, Exception) else {"error": str(ssh_results)},
        "overall_security_assessment": {
            "dns_security": "LOW",  # Default, would be calculated from results
            "smb_security": "LOW",  # Default, would be calculated from results
            "ssh_security": "LOW",  # Default, would be calculated from results
            "overall_security": "LOW"
        }
    }
    
    # Calculate overall security (simplified)
    security_scores = []
    
    if not isinstance(dns_results, Exception):
        dns_records = dns_results.get("dns_records", {})
        if hasattr(dns_records, 'successful_queries'):
            security_scores.append(1 if dns_records.successful_queries > 0 else 0)
    
    if not isinstance(smb_results, Exception):
        smb_enum = smb_results.get("smb_enumeration", {})
        if hasattr(smb_enum, 'null_session_allowed'):
            security_scores.append(2 if smb_enum.null_session_allowed else 1)
    
    if not isinstance(ssh_results, Exception):
        ssh_enum = ssh_results.get("ssh_enumeration", {})
        security_assessment = ssh_enum.security_assessment if hasattr(ssh_enum, 'security_assessment') else {}
        weak_algs = security_assessment.get("weak_algorithms_found", 0)
        security_scores.append(3 if weak_algs > 0 else 1)
    
    if security_scores:
        avg_security = sum(security_scores) / len(security_scores)
        if avg_security > 2:
            comprehensive_report["overall_security_assessment"]["overall_security"] = "HIGH"
        elif avg_security > 1:
            comprehensive_report["overall_security_assessment"]["overall_security"] = "MEDIUM"
    
    results["comprehensive_enumeration"] = comprehensive_report
    print(f"   Comprehensive enumeration completed: {comprehensive_report['overall_security_assessment']['overall_security']} security risk")
    
    return results

async def run_advanced_enumerator_examples() -> Dict[str, Any]:
    """Run advanced enumerator examples with custom configurations."""
    print("🚀 Running Advanced Enumerator Examples...")
    
    results = {}
    
    # 1. Custom DNS enumeration with specific record types
    print("1. Testing Custom DNS Enumeration...")
    custom_dns_request = DNSEnumerationRequest(
        target_domain="google.com",
        record_types=[
            DNSRecordType.A,
            DNSRecordType.AAAA,
            DNSRecordType.MX,
            DNSRecordType.NS,
            DNSRecordType.SOA,
            DNSRecordType.TXT,
            DNSRecordType.SRV
        ],
        nameservers=["8.8.8.8"],
        timeout=15.0,
        max_concurrent_queries=20
    )
    custom_dns_result = await enumerate_dns_records_async(custom_dns_request)
    results["custom_dns"] = custom_dns_result
    print(f"   Custom DNS enumeration found {len(custom_dns_result.records_found)} records")
    
    # 2. Comprehensive subdomain enumeration
    print("2. Testing Comprehensive Subdomain Enumeration...")
    comprehensive_subdomain_request = SubdomainEnumerationRequest(
        target_domain="example.com",
        wordlist=[
            "www", "mail", "ftp", "admin", "api", "dev", "test", "stage", "prod",
            "cdn", "static", "media", "files", "upload", "download", "secure",
            "vpn", "remote", "ssh", "telnet", "database", "db", "mysql", "redis"
        ],
        use_common_wordlist=True,
        max_concurrent_requests=30,
        timeout=10.0
    )
    comprehensive_subdomain_result = await enumerate_dns_subdomains_async(comprehensive_subdomain_request)
    results["comprehensive_subdomains"] = comprehensive_subdomain_result
    print(f"   Comprehensive subdomain enumeration found {len(comprehensive_subdomain_result.discovered_subdomains)} subdomains")
    
    # 3. Multi-target enumeration
    print("3. Testing Multi-Target Enumeration...")
    targets = ["localhost", "127.0.0.1"]
    
    multi_target_results = {}
    for target in targets:
        # SMB enumeration for each target
        smb_request = SMBEnumerationRequest(
            target_host=target,
            target_port=445,
            timeout=5.0
        )
        smb_result = await enumerate_smb_async(smb_request)
        multi_target_results[target] = {
            "shares": len(smb_result.shares_found),
            "users": len(smb_result.users_found),
            "null_session": smb_result.null_session_allowed
        }
    
    results["multi_target"] = multi_target_results
    print(f"   Multi-target enumeration completed for {len(targets)} targets")
    
    return results

async def main():
    """Main function to run all enumerator examples."""
    print("🔍 Cybersecurity Enumerator Toolkit Examples")
    print("=" * 60)
    
    try:
        # Run individual enumerator examples
        print("\n🌐 DNS Enumerator Examples")
        print("-" * 30)
        dns_results = await run_dns_enumerator_examples()
        
        print("\n💾 SMB Enumerator Examples")
        print("-" * 30)
        smb_results = await run_smb_enumerator_examples()
        
        print("\n🔐 SSH Enumerator Examples")
        print("-" * 30)
        ssh_results = await run_ssh_enumerator_examples()
        
        print("\n🔗 Integrated Enumerator Examples")
        print("-" * 30)
        integrated_results = await run_integrated_enumerator_examples()
        
        print("\n🚀 Advanced Enumerator Examples")
        print("-" * 30)
        advanced_results = await run_advanced_enumerator_examples()
        
        print("\n" + "=" * 60)
        print("✅ All enumerator examples completed successfully!")
        
        # Summary
        print("\n📊 Enumerator Summary:")
        print(f"   DNS enumerations: {len(dns_results)} completed")
        print(f"   SMB enumerations: {len(smb_results)} completed")
        print(f"   SSH enumerations: {len(ssh_results)} completed")
        print(f"   Integrated assessments: {len(integrated_results)} completed")
        print(f"   Advanced enumerations: {len(advanced_results)} completed")
        
        # Security summary
        if "comprehensive_enumeration" in integrated_results:
            overall_security = integrated_results["comprehensive_enumeration"]["overall_security_assessment"]["overall_security"]
            print(f"   Overall security risk: {overall_security}")
        
    except Exception as e:
        print(f"❌ Error running enumerator examples: {e}")
        raise

match __name__:
    case "__main__":
    asyncio.run(main()) 