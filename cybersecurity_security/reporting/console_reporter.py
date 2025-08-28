from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_RETRIES = 100

# Constants
TIMEOUT_SECONDS = 60

import asyncio
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, validator
from enum import Enum
import time
from datetime import datetime
import json
from typing import Any, List, Dict, Optional
import logging
"""
Console Reporter

Provides console-based reporting with colored output and structured formatting.
"""


# Color codes for console output
class Colors:
    """ANSI color codes for console output."""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class ConsoleReportLevel(str, Enum):
    """Enumeration of console report levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    SUCCESS = "success"

class ConsoleReportRequest(BaseModel):
    """Pydantic model for console report request."""
    scan_results: Optional[Dict[str, Any]] = Field(None, description="Scan results to report")
    vulnerability_data: Optional[List[Dict[str, Any]]] = Field(None, description="Vulnerability data")
    enumeration_data: Optional[Dict[str, Any]] = Field(None, description="Enumeration results")
    attack_data: Optional[Dict[str, Any]] = Field(None, description="Attack results")
    report_level: ConsoleReportLevel = Field(default=ConsoleReportLevel.INFO, description="Report level")
    include_details: bool = Field(default=True, description="Include detailed information")
    color_output: bool = Field(default=True, description="Enable colored output")
    timestamp: bool = Field(default=True, description="Include timestamps")
    
    @validator('scan_results', 'vulnerability_data', 'enumeration_data', 'attack_data')
    def validate_data(cls, v) -> bool:
        if v is not None and not v:
            raise ValueError("Data cannot be empty if provided")
        return v

class ConsoleReportResult(BaseModel):
    """Pydantic model for console report result."""
    report_generated: bool
    report_content: str
    report_length: int
    report_duration: float
    report_completed_at: float
    sections_processed: List[str]

def colorize(text: str, color: str, enabled: bool = True) -> str:
    """Add color to text if enabled."""
    if enabled:
        return f"{color}{text}{Colors.END}"
    return text

def format_timestamp(timestamp: float) -> str:
    """Format timestamp for display."""
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

async def generate_console_report_async(data: ConsoleReportRequest) -> ConsoleReportResult:
    """Generate comprehensive console report asynchronously."""
    start_time = time.time()
    report_content = []
    sections_processed = []
    
    # Header
    if data.timestamp:
        report_content.append(colorize(f"[{format_timestamp(time.time())}] ", Colors.CYAN, data.color_output))
    
    report_content.append(colorize("🔒 SECURITY ASSESSMENT REPORT", Colors.BOLD + Colors.BLUE, data.color_output))
    report_content.append("\n" + "=" * 60 + "\n")
    
    # Process scan results
    if data.scan_results:
        sections_processed.append("scan_results")
        scan_section = await print_scan_results(data.scan_results, data.color_output, data.include_details)
        report_content.append(scan_section)
    
    # Process vulnerability data
    if data.vulnerability_data:
        sections_processed.append("vulnerability_data")
        vuln_section = await print_vulnerability_details(data.vulnerability_data, data.color_output, data.include_details)
        report_content.append(vuln_section)
    
    # Process enumeration data
    if data.enumeration_data:
        sections_processed.append("enumeration_data")
        enum_section = await print_enumeration_results(data.enumeration_data, data.color_output, data.include_details)
        report_content.append(enum_section)
    
    # Process attack data
    if data.attack_data:
        sections_processed.append("attack_data")
        attack_section = await print_attack_results(data.attack_data, data.color_output, data.include_details)
        report_content.append(attack_section)
    
    # Summary
    summary_section = await print_security_summary(
        data.scan_results, data.vulnerability_data, data.enumeration_data, data.attack_data,
        data.color_output
    )
    report_content.append(summary_section)
    
    # Footer
    report_content.append("\n" + "=" * 60)
    if data.timestamp:
        report_content.append(colorize(f"Report generated at: {format_timestamp(time.time())}", Colors.CYAN, data.color_output))
    
    report_content_str = "\n".join(report_content)
    report_duration = time.time() - start_time
    
    return ConsoleReportResult(
        report_generated=True,
        report_content=report_content_str,
        report_length=len(report_content_str),
        report_duration=report_duration,
        report_completed_at=time.time(),
        sections_processed=sections_processed
    )

async def print_security_summary(
    scan_results: Optional[Dict[str, Any]] = None,
    vulnerability_data: Optional[List[Dict[str, Any]]] = None,
    enumeration_data: Optional[Dict[str, Any]] = None,
    attack_data: Optional[Dict[str, Any]] = None,
    color_output: bool = True
) -> str:
    """Print security assessment summary."""
    summary_parts = []
    summary_parts.append(colorize("\n📊 SECURITY SUMMARY", Colors.BOLD + Colors.MAGENTA, color_output))
    summary_parts.append("-" * 40)
    
    # Scan summary
    if scan_results:
        total_scans = len(scan_results.get("scans", []))
        successful_scans = len([s for s in scan_results.get("scans", []) if s.get("success", False)])
        summary_parts.append(f"🔍 Scans: {successful_scans}/{total_scans} successful")
    
    # Vulnerability summary
    if vulnerability_data:
        total_vulns = len(vulnerability_data)
        critical_vulns = len([v for v in vulnerability_data if v.get("severity") == "critical"])
        high_vulns = len([v for v in vulnerability_data if v.get("severity") == "high"])
        medium_vulns = len([v for v in vulnerability_data if v.get("severity") == "medium"])
        low_vulns = len([v for v in vulnerability_data if v.get("severity") == "low"])
        
        summary_parts.append(f"🚨 Vulnerabilities: {total_vulns} total")
        if critical_vulns > 0:
            summary_parts.append(f"   {colorize(f'Critical: {critical_vulns}', Colors.RED, color_output)}")
        if high_vulns > 0:
            summary_parts.append(f"   {colorize(f'High: {high_vulns}', Colors.YELLOW, color_output)}")
        if medium_vulns > 0:
            summary_parts.append(f"   {colorize(f'Medium: {medium_vulns}', Colors.BLUE, color_output)}")
        if low_vulns > 0:
            summary_parts.append(f"   {colorize(f'Low: {low_vulns}', Colors.GREEN, color_output)}")
    
    # Enumeration summary
    if enumeration_data:
        enum_types = list(enumeration_data.keys())
        summary_parts.append(f"🔍 Enumeration: {len(enum_types)} types completed")
        for enum_type in enum_types:
            summary_parts.append(f"   - {enum_type}")
    
    # Attack summary
    if attack_data:
        attack_types = list(attack_data.keys())
        successful_attacks = 0
        for attack_type, results in attack_data.items():
            if isinstance(results, dict) and results.get("successful_attempts", 0) > 0:
                successful_attacks += 1
        
        summary_parts.append(f"⚔️ Attacks: {successful_attacks}/{len(attack_types)} successful")
    
    # Overall risk assessment
    risk_level = "LOW"
    if vulnerability_data:
        critical_count = len([v for v in vulnerability_data if v.get("severity") == "critical"])
        high_count = len([v for v in vulnerability_data if v.get("severity") == "high"])
        
        if critical_count > 0:
            risk_level = "CRITICAL"
        elif high_count > 2:
            risk_level = "HIGH"
        elif high_count > 0 or len(vulnerability_data) > 5:
            risk_level = "MEDIUM"
    
    risk_color = Colors.GREEN if risk_level == "LOW" else Colors.YELLOW if risk_level == "MEDIUM" else Colors.RED
    summary_parts.append(f"\n🎯 Overall Risk Level: {colorize(risk_level, risk_color, color_output)}")
    
    return "\n".join(summary_parts)

async def print_vulnerability_details(
    vulnerability_data: List[Dict[str, Any]],
    color_output: bool = True,
    include_details: bool = True
) -> str:
    """Print detailed vulnerability information."""
    vuln_parts = []
    vuln_parts.append(colorize("\n🚨 VULNERABILITY DETAILS", Colors.BOLD + Colors.RED, color_output))
    vuln_parts.append("-" * 40)
    
    for i, vuln in enumerate(vulnerability_data, 1):
        severity = vuln.get("severity", "unknown")
        title = vuln.get("title", "Unknown Vulnerability")
        description = vuln.get("description", "No description available")
        
        # Color code severity
        if severity == "critical":
            severity_color = Colors.RED
        elif severity == "high":
            severity_color = Colors.YELLOW
        elif severity == "medium":
            severity_color = Colors.BLUE
        else:
            severity_color = Colors.GREEN
        
        vuln_parts.append(f"{i}. {colorize(f'[{severity.upper()}]', severity_color, color_output)} {title}")
        
        if include_details:
            vuln_parts.append(f"   Description: {description}")
            
            # Additional details
            if "cvss_score" in vuln:
                vuln_parts.append(f"   CVSS Score: {vuln['cvss_score']}")
            
            if "affected_component" in vuln:
                vuln_parts.append(f"   Affected: {vuln['affected_component']}")
            
            if "recommendation" in vuln:
                vuln_parts.append(f"   Recommendation: {vuln['recommendation']}")
            
            vuln_parts.append("")
    
    return "\n".join(vuln_parts)

async def print_scan_results(
    scan_results: Dict[str, Any],
    color_output: bool = True,
    include_details: bool = True
) -> str:
    """Print scan results."""
    scan_parts = []
    scan_parts.append(colorize("\n🔍 SCAN RESULTS", Colors.BOLD + Colors.BLUE, color_output))
    scan_parts.append("-" * 40)
    
    scans = scan_results.get("scans", [])
    for scan in scans:
        scan_type = scan.get("type", "Unknown")
        success = scan.get("success", False)
        target = scan.get("target", "Unknown")
        
        status_color = Colors.GREEN if success else Colors.RED
        status_text = "SUCCESS" if success else "FAILED"
        
        scan_parts.append(f"📡 {scan_type}: {colorize(status_text, status_color, color_output)}")
        scan_parts.append(f"   Target: {target}")
        
        if include_details:
            if "duration" in scan:
                scan_parts.append(f"   Duration: {scan['duration']:.2f}s")
            
            if "findings" in scan:
                findings_count = len(scan["findings"])
                scan_parts.append(f"   Findings: {findings_count}")
            
            if "ports" in scan:
                open_ports = scan["ports"]
                scan_parts.append(f"   Open Ports: {', '.join(map(str, open_ports))}")
        
        scan_parts.append("")
    
    return "\n".join(scan_parts)

async def print_enumeration_results(
    enumeration_data: Dict[str, Any],
    color_output: bool = True,
    include_details: bool = True
) -> str:
    """Print enumeration results."""
    enum_parts = []
    enum_parts.append(colorize("\n🔍 ENUMERATION RESULTS", Colors.BOLD + Colors.CYAN, color_output))
    enum_parts.append("-" * 40)
    
    for enum_type, results in enumeration_data.items():
        enum_parts.append(f"📋 {enum_type.upper()} Enumeration:")
        
        if isinstance(results, dict):
            if "records" in results:
                records = results["records"]
                enum_parts.append(f"   Records Found: {len(records)}")
                
                if include_details and records:
                    for record in records[:5]:  # Show first 5 records
                        enum_parts.append(f"     - {record}")
                    
                    if len(records) > 5:
                        enum_parts.append(f"     ... and {len(records) - 5} more")
            
            if "duration" in results:
                enum_parts.append(f"   Duration: {results['duration']:.2f}s")
        
        enum_parts.append("")
    
    return "\n".join(enum_parts)

async def print_attack_results(
    attack_data: Dict[str, Any],
    color_output: bool = True,
    include_details: bool = True
) -> str:
    """Print attack results."""
    attack_parts = []
    attack_parts.append(colorize("\n⚔️ ATTACK RESULTS", Colors.BOLD + Colors.MAGENTA, color_output))
    attack_parts.append("-" * 40)
    
    for attack_type, results in attack_data.items():
        attack_parts.append(f"🎯 {attack_type.upper()} Attack:")
        
        if isinstance(results, dict):
            successful_attempts = results.get("successful_attempts", 0)
            total_attempts = results.get("total_attempts", 0)
            
            success_rate = (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0
            
            if successful_attempts > 0:
                attack_parts.append(f"   {colorize('SUCCESSFUL', Colors.RED, color_output)}: {successful_attempts}/{total_attempts} ({success_rate:.1f}%)")
            else:
                attack_parts.append(f"   {colorize('FAILED', Colors.GREEN, color_output)}: {successful_attempts}/{total_attempts} ({success_rate:.1f}%)")
            
            if include_details:
                if "successful_credentials" in results:
                    creds = results["successful_credentials"]
                    if creds:
                        attack_parts.append(f"   Credentials Found: {len(creds)}")
                        for cred in creds[:3]:  # Show first 3 credentials
                            attack_parts.append(f"     - {cred.get('username', 'unknown')}:{cred.get('password', 'unknown')}")
                
                if "duration" in results:
                    attack_parts.append(f"   Duration: {results['duration']:.2f}s")
        
        attack_parts.append("")
    
    return "\n".join(attack_parts) 