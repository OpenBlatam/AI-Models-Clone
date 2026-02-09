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
Report Aggregator

Provides functionality to aggregate and combine multiple report types.
"""


class ReportType(str, Enum):
    """Enumeration of report types."""
    CONSOLE = "console"
    HTML = "html"
    JSON = "json"
    COMPREHENSIVE = "comprehensive"

class ReportAggregatorRequest(BaseModel):
    """Pydantic model for report aggregator request."""
    console_report: Optional[Dict[str, Any]] = Field(None, description="Console report data")
    html_report: Optional[Dict[str, Any]] = Field(None, description="HTML report data")
    json_report: Optional[Dict[str, Any]] = Field(None, description="JSON report data")
    scan_results: Optional[Dict[str, Any]] = Field(None, description="Raw scan results")
    vulnerability_data: Optional[List[Dict[str, Any]]] = Field(None, description="Raw vulnerability data")
    enumeration_data: Optional[Dict[str, Any]] = Field(None, description="Raw enumeration data")
    attack_data: Optional[Dict[str, Any]] = Field(None, description="Raw attack data")
    output_format: ReportType = Field(default=ReportType.COMPREHENSIVE, description="Output format")
    include_raw_data: bool = Field(default=False, description="Include raw data in output")
    generate_timeline: bool = Field(default=True, description="Generate timeline")
    
    @validator('console_report', 'html_report', 'json_report')
    def validate_reports(cls, v) -> bool:
        if v is not None and not v:
            raise ValueError("Report data cannot be empty if provided")
        return v

class ReportAggregatorResult(BaseModel):
    """Pydantic model for report aggregator result."""
    aggregation_successful: bool
    aggregated_report: Dict[str, Any]
    report_size: int
    aggregation_duration: float
    aggregation_completed_at: float
    reports_combined: List[str]
    output_format: ReportType

async def aggregate_reports_async(data: ReportAggregatorRequest) -> ReportAggregatorResult:
    """Aggregate multiple reports into a comprehensive report."""
    start_time = time.time()
    reports_combined = []
    
    # Initialize aggregated report
    aggregated_report = {
        "metadata": {
            "aggregation_timestamp": datetime.now().isoformat(),
            "output_format": data.output_format.value,
            "reports_combined": []
        },
        "executive_summary": {},
        "detailed_findings": {},
        "statistics": {},
        "timeline": {},
        "recommendations": []
    }
    
    # Combine scan results
    if data.scan_results:
        reports_combined.append("scan_results")
        scan_summary = await combine_scan_results(data.scan_results)
        aggregated_report["detailed_findings"]["scans"] = scan_summary
    
    # Combine vulnerability data
    if data.vulnerability_data:
        reports_combined.append("vulnerability_data")
        vuln_summary = await merge_vulnerability_data(data.vulnerability_data)
        aggregated_report["detailed_findings"]["vulnerabilities"] = vuln_summary
    
    # Combine enumeration data
    if data.enumeration_data:
        reports_combined.append("enumeration_data")
        enum_summary = await combine_enumeration_data(data.enumeration_data)
        aggregated_report["detailed_findings"]["enumeration"] = enum_summary
    
    # Combine attack data
    if data.attack_data:
        reports_combined.append("attack_data")
        attack_summary = await combine_attack_data(data.attack_data)
        aggregated_report["detailed_findings"]["attacks"] = attack_summary
    
    # Generate executive summary
    executive_summary = await generate_executive_summary(
        data.scan_results, data.vulnerability_data, data.enumeration_data, data.attack_data
    )
    aggregated_report["executive_summary"] = executive_summary
    
    # Generate comprehensive report
    if data.output_format == ReportType.COMPREHENSIVE:
        comprehensive_report = await create_comprehensive_report(
            data.scan_results, data.vulnerability_data, data.enumeration_data, data.attack_data
        )
        aggregated_report.update(comprehensive_report)
    
    # Generate timeline
    if data.generate_timeline:
        timeline = await create_timeline(
            data.scan_results, data.vulnerability_data, data.enumeration_data, data.attack_data
        )
        aggregated_report["timeline"] = timeline
    
    # Include raw data if requested
    if data.include_raw_data:
        aggregated_report["raw_data"] = {
            "scan_results": data.scan_results,
            "vulnerability_data": data.vulnerability_data,
            "enumeration_data": data.enumeration_data,
            "attack_data": data.attack_data
        }
    
    # Update metadata
    aggregated_report["metadata"]["reports_combined"] = reports_combined
    
    aggregation_duration = time.time() - start_time
    
    return ReportAggregatorResult(
        aggregation_successful=True,
        aggregated_report=aggregated_report,
        report_size=len(json.dumps(aggregated_report)),
        aggregation_duration=aggregation_duration,
        aggregation_completed_at=time.time(),
        reports_combined=reports_combined,
        output_format=data.output_format
    )

async def combine_scan_results(scan_results: Dict[str, Any]) -> Dict[str, Any]:
    """Combine and analyze scan results."""
    scans = scan_results.get("scans", [])
    
    combined_results = {
        "total_scans": len(scans),
        "successful_scans": len([s for s in scans if s.get("success", False)]),
        "failed_scans": len([s for s in scans if not s.get("success", False)]),
        "scan_types": {},
        "targets": {},
        "findings_summary": {},
        "performance_metrics": {}
    }
    
    # Analyze scan types
    for scan in scans:
        scan_type = scan.get("type", "unknown")
        combined_results["scan_types"][scan_type] = combined_results["scan_types"].get(scan_type, 0) + 1
        
        target = scan.get("target", "unknown")
        combined_results["targets"][target] = combined_results["targets"].get(target, 0) + 1
    
    # Calculate performance metrics
    durations = [s.get("duration", 0) for s in scans if s.get("duration")]
    if durations:
        combined_results["performance_metrics"] = {
            "average_duration": sum(durations) / len(durations),
            "min_duration": min(durations),
            "max_duration": max(durations),
            "total_duration": sum(durations)
        }
    
    # Analyze findings
    all_findings = []
    for scan in scans:
        findings = scan.get("findings", [])
        all_findings.extend(findings)
    
    combined_results["findings_summary"] = {
        "total_findings": len(all_findings),
        "findings_by_type": {}
    }
    
    # Group findings by type
    for finding in all_findings:
        finding_type = finding.get("type", "unknown")
        combined_results["findings_summary"]["findings_by_type"][finding_type] = \
            combined_results["findings_summary"]["findings_by_type"].get(finding_type, 0) + 1
    
    return combined_results

async def merge_vulnerability_data(vulnerability_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge and analyze vulnerability data."""
    merged_data = {
        "total_vulnerabilities": len(vulnerability_data),
        "severity_distribution": {},
        "cvss_score_analysis": {},
        "affected_components": {},
        "vulnerability_types": {},
        "risk_assessment": {}
    }
    
    # Analyze severity distribution
    for vuln in vulnerability_data:
        severity = vuln.get("severity", "unknown")
        merged_data["severity_distribution"][severity] = \
            merged_data["severity_distribution"].get(severity, 0) + 1
    
    # Analyze CVSS scores
    cvss_scores = []
    for vuln in vulnerability_data:
        cvss_score = vuln.get("cvss_score")
        if cvss_score and isinstance(cvss_score, (int, float)):
            cvss_scores.append(cvss_score)
    
    if cvss_scores:
        merged_data["cvss_score_analysis"] = {
            "average_score": sum(cvss_scores) / len(cvss_scores),
            "highest_score": max(cvss_scores),
            "lowest_score": min(cvss_scores),
            "score_distribution": {
                "critical": len([s for s in cvss_scores if s >= 9.0]),
                "high": len([s for s in cvss_scores if 7.0 <= s < 9.0]),
                "medium": len([s for s in cvss_scores if 4.0 <= s < 7.0]),
                "low": len([s for s in cvss_scores if s < 4.0])
            }
        }
    
    # Analyze affected components
    for vuln in vulnerability_data:
        component = vuln.get("affected_component", "unknown")
        merged_data["affected_components"][component] = \
            merged_data["affected_components"].get(component, 0) + 1
    
    # Analyze vulnerability types
    for vuln in vulnerability_data:
        vuln_type = vuln.get("type", "unknown")
        merged_data["vulnerability_types"][vuln_type] = \
            merged_data["vulnerability_types"].get(vuln_type, 0) + 1
    
    # Risk assessment
    critical_count = merged_data["severity_distribution"].get("critical", 0)
    high_count = merged_data["severity_distribution"].get("high", 0)
    
    if critical_count > 0:
        risk_level = "CRITICAL"
    elif high_count > 2:
        risk_level = "HIGH"
    elif high_count > 0 or len(vulnerability_data) > 5:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
    
    merged_data["risk_assessment"] = {
        "overall_risk_level": risk_level,
        "critical_vulnerabilities": critical_count,
        "high_vulnerabilities": high_count,
        "total_high_risk": critical_count + high_count
    }
    
    return merged_data

async def combine_enumeration_data(enumeration_data: Dict[str, Any]) -> Dict[str, Any]:
    """Combine and analyze enumeration data."""
    combined_data = {
        "enumeration_types": list(enumeration_data.keys()),
        "total_records": 0,
        "successful_enumerations": 0,
        "performance_metrics": {},
        "record_distribution": {}
    }
    
    durations = []
    
    for enum_type, results in enumeration_data.items():
        if isinstance(results, dict):
            records = results.get("records", [])
            combined_data["total_records"] += len(records)
            combined_data["record_distribution"][enum_type] = len(records)
            
            if results.get("success", False):
                combined_data["successful_enumerations"] += 1
            
            if "duration" in results:
                durations.append(results["duration"])
    
    # Calculate performance metrics
    if durations:
        combined_data["performance_metrics"] = {
            "average_duration": sum(durations) / len(durations),
            "min_duration": min(durations),
            "max_duration": max(durations),
            "total_duration": sum(durations)
        }
    
    return combined_data

async def combine_attack_data(attack_data: Dict[str, Any]) -> Dict[str, Any]:
    """Combine and analyze attack data."""
    combined_data = {
        "attack_types": list(attack_data.keys()),
        "total_attacks": len(attack_data),
        "successful_attacks": 0,
        "total_attempts": 0,
        "successful_attempts": 0,
        "credentials_found": 0,
        "performance_metrics": {},
        "attack_distribution": {}
    }
    
    durations = []
    
    for attack_type, results in attack_data.items():
        if isinstance(results, dict):
            total_attempts = results.get("total_attempts", 0)
            successful_attempts = results.get("successful_attempts", 0)
            credentials = len(results.get("successful_credentials", []))
            
            combined_data["total_attempts"] += total_attempts
            combined_data["successful_attempts"] += successful_attempts
            combined_data["credentials_found"] += credentials
            
            if successful_attempts > 0:
                combined_data["successful_attacks"] += 1
            
            combined_data["attack_distribution"][attack_type] = {
                "total_attempts": total_attempts,
                "successful_attempts": successful_attempts,
                "success_rate": (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0,
                "credentials_found": credentials
            }
            
            if "duration" in results:
                durations.append(results["duration"])
    
    # Calculate performance metrics
    if durations:
        combined_data["performance_metrics"] = {
            "average_duration": sum(durations) / len(durations),
            "min_duration": min(durations),
            "max_duration": max(durations),
            "total_duration": sum(durations)
        }
    
    # Calculate overall success rate
    combined_data["overall_success_rate"] = \
        (combined_data["successful_attempts"] / combined_data["total_attempts"] * 100) if combined_data["total_attempts"] > 0 else 0
    
    return combined_data

async def generate_executive_summary(
    scan_results: Optional[Dict[str, Any]] = None,
    vulnerability_data: Optional[List[Dict[str, Any]]] = None,
    enumeration_data: Optional[Dict[str, Any]] = None,
    attack_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Generate comprehensive executive summary."""
    summary = {
        "assessment_overview": {
            "total_operations": 0,
            "overall_risk_level": "LOW",
            "key_findings": [],
            "critical_issues": 0,
            "high_priority_issues": 0
        },
        "performance_summary": {
            "total_duration": 0,
            "operations_per_second": 0,
            "success_rate": 0
        },
        "security_posture": {
            "vulnerability_score": 0,
            "attack_resistance": 0,
            "overall_security_grade": "A"
        }
    }
    
    # Calculate total operations
    total_ops = 0
    if scan_results:
        total_ops += len(scan_results.get("scans", []))
    if vulnerability_data:
        total_ops += len(vulnerability_data)
    if enumeration_data:
        total_ops += len(enumeration_data)
    if attack_data:
        total_ops += len(attack_data)
    
    summary["assessment_overview"]["total_operations"] = total_ops
    
    # Analyze vulnerabilities
    if vulnerability_data:
        critical_count = len([v for v in vulnerability_data if v.get("severity") == "critical"])
        high_count = len([v for v in vulnerability_data if v.get("severity") == "high"])
        
        summary["assessment_overview"]["critical_issues"] = critical_count
        summary["assessment_overview"]["high_priority_issues"] = high_count
        
        # Determine risk level
        if critical_count > 0:
            summary["assessment_overview"]["overall_risk_level"] = "CRITICAL"
        elif high_count > 2:
            summary["assessment_overview"]["overall_risk_level"] = "HIGH"
        elif high_count > 0 or len(vulnerability_data) > 5:
            summary["assessment_overview"]["overall_risk_level"] = "MEDIUM"
    
    # Calculate security posture
    if vulnerability_data:
        total_vulns = len(vulnerability_data)
        critical_vulns = len([v for v in vulnerability_data if v.get("severity") == "critical"])
        high_vulns = len([v for v in vulnerability_data if v.get("severity") == "high"])
        
        # Vulnerability score (0-100, lower is better)
        vuln_score = (critical_vulns * 25 + high_vulns * 10 + (total_vulns - critical_vulns - high_vulns) * 2)
        summary["security_posture"]["vulnerability_score"] = min(vuln_score, 100)
    
    # Attack resistance score
    if attack_data:
        successful_attacks = sum(
            1 for results in attack_data.values() 
            if isinstance(results, dict) and results.get("successful_attempts", 0) > 0
        )
        
        attack_resistance = max(0, 100 - (successful_attacks / len(attack_data) * 100))
        summary["security_posture"]["attack_resistance"] = attack_resistance
    
    # Overall security grade
    vuln_score = summary["security_posture"]["vulnerability_score"]
    attack_resistance = summary["security_posture"]["attack_resistance"]
    
    overall_score = (100 - vuln_score + attack_resistance) / 2
    
    if overall_score >= 90:
        grade = "A"
    elif overall_score >= 80:
        grade = "B"
    elif overall_score >= 70:
        grade = "C"
    elif overall_score >= 60:
        grade = "D"
    else:
        grade = "F"
    
    summary["security_posture"]["overall_security_grade"] = grade
    
    return summary

async def create_comprehensive_report(
    scan_results: Optional[Dict[str, Any]] = None,
    vulnerability_data: Optional[List[Dict[str, Any]]] = None,
    enumeration_data: Optional[Dict[str, Any]] = None,
    attack_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a comprehensive report with all data."""
    comprehensive_report = {
        "detailed_analysis": {},
        "trends_and_patterns": {},
        "comparative_analysis": {},
        "action_items": []
    }
    
    # Detailed analysis
    if vulnerability_data:
        comprehensive_report["detailed_analysis"]["vulnerability_analysis"] = {
            "most_common_vulnerabilities": await find_most_common_vulnerabilities(vulnerability_data),
            "severity_trends": await analyze_severity_trends(vulnerability_data),
            "component_analysis": await analyze_component_vulnerabilities(vulnerability_data)
        }
    
    if attack_data:
        comprehensive_report["detailed_analysis"]["attack_analysis"] = {
            "most_successful_attacks": await find_most_successful_attacks(attack_data),
            "attack_patterns": await analyze_attack_patterns(attack_data),
            "credential_analysis": await analyze_credential_findings(attack_data)
        }
    
    # Generate action items
    action_items = await generate_action_items(
        scan_results, vulnerability_data, enumeration_data, attack_data
    )
    comprehensive_report["action_items"] = action_items
    
    return comprehensive_report

async def create_timeline(
    scan_results: Optional[Dict[str, Any]] = None,
    vulnerability_data: Optional[List[Dict[str, Any]]] = None,
    enumeration_data: Optional[Dict[str, Any]] = None,
    attack_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create timeline of assessment activities."""
    timeline = {
        "assessment_phases": [],
        "key_events": [],
        "milestones": []
    }
    
    # Assessment phases
    phases = []
    
    if scan_results:
        phases.append({
            "phase": "Reconnaissance",
            "description": "Port scanning and service enumeration",
            "activities": len(scan_results.get("scans", [])),
            "duration": sum(s.get("duration", 0) for s in scan_results.get("scans", []))
        })
    
    if vulnerability_data:
        phases.append({
            "phase": "Vulnerability Assessment",
            "description": "Vulnerability scanning and analysis",
            "activities": len(vulnerability_data),
            "duration": 0  # Would need timing data from vulnerability scans
        })
    
    if enumeration_data:
        phases.append({
            "phase": "Service Enumeration",
            "description": "Detailed service and protocol enumeration",
            "activities": len(enumeration_data),
            "duration": sum(r.get("duration", 0) for r in enumeration_data.values() if isinstance(r, dict))
        })
    
    if attack_data:
        phases.append({
            "phase": "Penetration Testing",
            "description": "Brute force and exploit testing",
            "activities": len(attack_data),
            "duration": sum(r.get("duration", 0) for r in attack_data.values() if isinstance(r, dict))
        })
    
    timeline["assessment_phases"] = phases
    
    return timeline

async def find_most_common_vulnerabilities(vulnerability_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Find most common vulnerability types."""
    vuln_counts = {}
    
    for vuln in vulnerability_data:
        vuln_type = vuln.get("type", "unknown")
        vuln_counts[vuln_type] = vuln_counts.get(vuln_type, 0) + 1
    
    # Sort by count
    sorted_vulns = sorted(vuln_counts.items(), key=lambda x: x[1], reverse=True)
    
    return [{"type": vuln_type, "count": count} for vuln_type, count in sorted_vulns[:5]]

async def analyze_severity_trends(vulnerability_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze severity trends in vulnerabilities."""
    severity_counts = {}
    
    for vuln in vulnerability_data:
        severity = vuln.get("severity", "unknown")
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    return {
        "severity_distribution": severity_counts,
        "risk_level": "HIGH" if severity_counts.get("critical", 0) > 0 else "MEDIUM" if severity_counts.get("high", 0) > 2 else "LOW"
    }

async def analyze_component_vulnerabilities(vulnerability_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze vulnerabilities by affected component."""
    component_vulns = {}
    
    for vuln in vulnerability_data:
        component = vuln.get("affected_component", "unknown")
        severity = vuln.get("severity", "unknown")
        
        if component not in component_vulns:
            component_vulns[component] = {"total": 0, "critical": 0, "high": 0, "medium": 0, "low": 0}
        
        component_vulns[component]["total"] += 1
        component_vulns[component][severity] += 1
    
    return component_vulns

async def find_most_successful_attacks(attack_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Find most successful attack types."""
    attack_success = []
    
    for attack_type, results in attack_data.items():
        if isinstance(results, dict):
            successful_attempts = results.get("successful_attempts", 0)
            total_attempts = results.get("total_attempts", 0)
            success_rate = (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0
            
            attack_success.append({
                "attack_type": attack_type,
                "success_rate": success_rate,
                "successful_attempts": successful_attempts,
                "total_attempts": total_attempts
            })
    
    # Sort by success rate
    attack_success.sort(key=lambda x: x["success_rate"], reverse=True)
    return attack_success[:5]

async def analyze_attack_patterns(attack_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze patterns in attack results."""
    patterns = {
        "total_attack_types": len(attack_data),
        "successful_attack_types": 0,
        "average_success_rate": 0,
        "most_common_credentials": []
    }
    
    total_success_rate = 0
    all_credentials = []
    
    for attack_type, results in attack_data.items():
        if isinstance(results, dict):
            successful_attempts = results.get("successful_attempts", 0)
            total_attempts = results.get("total_attempts", 0)
            
            if successful_attempts > 0:
                patterns["successful_attack_types"] += 1
            
            success_rate = (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0
            total_success_rate += success_rate
            
            # Collect credentials
            credentials = results.get("successful_credentials", [])
            all_credentials.extend(credentials)
    
    if attack_data:
        patterns["average_success_rate"] = total_success_rate / len(attack_data)
    
    # Find most common credentials
    credential_counts = {}
    for cred in all_credentials:
        cred_str = f"{cred.get('username', 'unknown')}:{cred.get('password', 'unknown')}"
        credential_counts[cred_str] = credential_counts.get(cred_str, 0) + 1
    
    sorted_creds = sorted(credential_counts.items(), key=lambda x: x[1], reverse=True)
    patterns["most_common_credentials"] = [{"credential": cred, "count": count} for cred, count in sorted_creds[:5]]
    
    return patterns

async def analyze_credential_findings(attack_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze credential findings from attacks."""
    credential_analysis = {
        "total_credentials_found": 0,
        "credentials_by_attack_type": {},
        "weak_password_patterns": [],
        "default_credentials": []
    }
    
    for attack_type, results in attack_data.items():
        if isinstance(results, dict):
            credentials = results.get("successful_credentials", [])
            credential_analysis["total_credentials_found"] += len(credentials)
            credential_analysis["credentials_by_attack_type"][attack_type] = len(credentials)
    
    return credential_analysis

async def generate_action_items(
    scan_results: Optional[Dict[str, Any]] = None,
    vulnerability_data: Optional[List[Dict[str, Any]]] = None,
    enumeration_data: Optional[Dict[str, Any]] = None,
    attack_data: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """Generate actionable items based on findings."""
    action_items = []
    
    # Critical vulnerabilities
    if vulnerability_data:
        critical_vulns = [v for v in vulnerability_data if v.get("severity") == "critical"]
        if critical_vulns:
            action_items.append({
                "priority": "IMMEDIATE",
                "category": "Critical Vulnerabilities",
                "description": f"Address {len(critical_vulns)} critical vulnerabilities immediately",
                "recommendations": [
                    "Patch critical vulnerabilities within 24 hours",
                    "Implement emergency security controls",
                    "Conduct immediate security review"
                ]
            })
    
    # Successful attacks
    if attack_data:
        successful_attacks = sum(
            1 for results in attack_data.values() 
            if isinstance(results, dict) and results.get("successful_attempts", 0) > 0
        )
        
        if successful_attacks > 0:
            action_items.append({
                "priority": "HIGH",
                "category": "Attack Resistance",
                "description": f"Strengthen defenses against {successful_attacks} successful attack types",
                "recommendations": [
                    "Implement stronger authentication mechanisms",
                    "Enable multi-factor authentication",
                    "Review and update access controls"
                ]
            })
    
    # Open ports and services
    if scan_results:
        open_ports = set()
        for scan in scan_results.get("scans", []):
            ports = scan.get("ports", [])
            open_ports.update(ports)
        
        if len(open_ports) > 10:
            action_items.append({
                "priority": "MEDIUM",
                "category": "Network Security",
                "description": f"Reduce attack surface by closing unnecessary ports ({len(open_ports)} open ports)",
                "recommendations": [
                    "Review and close unnecessary services",
                    "Implement firewall rules",
                    "Use port knocking for sensitive services"
                ]
            })
    
    return action_items 