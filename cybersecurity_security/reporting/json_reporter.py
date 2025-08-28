from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_RETRIES = 100

import asyncio
import json
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, validator
from enum import Enum
import time
from datetime import datetime
import base64
from typing import Any, List, Dict, Optional
import logging
"""
JSON Reporter

Provides JSON-based reporting with structured data export capabilities.
"""


class JSONReportFormat(str, Enum):
    """Enumeration of JSON report formats."""
    COMPACT = "compact"
    PRETTY = "pretty"
    DETAILED = "detailed"
    MINIMAL = "minimal"

class JSONReportRequest(BaseModel):
    """Pydantic model for JSON report request."""
    scan_results: Optional[Dict[str, Any]] = Field(None, description="Scan results to report")
    vulnerability_data: Optional[List[Dict[str, Any]]] = Field(None, description="Vulnerability data")
    enumeration_data: Optional[Dict[str, Any]] = Field(None, description="Enumeration results")
    attack_data: Optional[Dict[str, Any]] = Field(None, description="Attack results")
    format: JSONReportFormat = Field(default=JSONReportFormat.DETAILED, description="JSON format")
    include_metadata: bool = Field(default=True, description="Include metadata")
    include_timestamps: bool = Field(default=True, description="Include timestamps")
    include_statistics: bool = Field(default=True, description="Include statistics")
    export_format: str = Field(default="json", regex="^(json|csv|xml)$", description="Export format")
    
    @validator('scan_results', 'vulnerability_data', 'enumeration_data', 'attack_data')
    def validate_data(cls, v) -> bool:
        if v is not None and not v:
            raise ValueError("Data cannot be empty if provided")
        return v

class JSONReportResult(BaseModel):
    """Pydantic model for JSON report result."""
    report_generated: bool
    json_content: str
    report_size: int
    report_duration: float
    report_completed_at: float
    data_sections: List[str]
    export_format: str

async def generate_json_report_async(data: JSONReportRequest) -> JSONReportResult:
    """Generate comprehensive JSON report asynchronously."""
    start_time = time.time()
    data_sections = []
    
    # Initialize report structure
    report = {
        "report_metadata": {},
        "summary": {},
        "scan_results": {},
        "vulnerabilities": {},
        "enumeration": {},
        "attacks": {},
        "statistics": {},
        "recommendations": []
    }
    
    # Add metadata
    if data.include_metadata:
        data_sections.append("metadata")
        report["report_metadata"] = {
            "report_type": "security_assessment",
            "generated_at": datetime.now().isoformat(),
            "tool_version": "1.0.0",
            "format": data.format.value,
            "export_format": data.export_format
        }
    
    # Process scan results
    if data.scan_results:
        data_sections.append("scan_results")
        scan_data = await export_scan_data(data.scan_results, data.format)
        report["scan_results"] = scan_data
    
    # Process vulnerability data
    if data.vulnerability_data:
        data_sections.append("vulnerabilities")
        vuln_data = await export_vulnerability_data(data.vulnerability_data, data.format)
        report["vulnerabilities"] = vuln_data
    
    # Process enumeration data
    if data.enumeration_data:
        data_sections.append("enumeration")
        enum_data = await export_enumeration_data(data.enumeration_data, data.format)
        report["enumeration"] = enum_data
    
    # Process attack data
    if data.attack_data:
        data_sections.append("attacks")
        attack_data = await export_attack_data(data.attack_data, data.format)
        report["attacks"] = attack_data
    
    # Generate summary
    summary = await create_structured_summary(
        data.scan_results, data.vulnerability_data, data.enumeration_data, data.attack_data
    )
    report["summary"] = summary
    
    # Generate statistics
    if data.include_statistics:
        data_sections.append("statistics")
        stats = await create_statistics(
            data.scan_results, data.vulnerability_data, data.enumeration_data, data.attack_data
        )
        report["statistics"] = stats
    
    # Generate recommendations
    if data.vulnerability_data:
        data_sections.append("recommendations")
        recommendations = await create_recommendations(data.vulnerability_data)
        report["recommendations"] = recommendations
    
    # Convert to JSON
    if data.format == JSONReportFormat.PRETTY:
        json_content = json.dumps(report, indent=2, ensure_ascii=False)
    else:
        json_content = json.dumps(report, ensure_ascii=False)
    
    report_duration = time.time() - start_time
    
    return JSONReportResult(
        report_generated=True,
        json_content=json_content,
        report_size=len(json_content),
        report_duration=report_duration,
        report_completed_at=time.time(),
        data_sections=data_sections,
        export_format=data.export_format
    )

async def export_scan_data(scan_results: Dict[str, Any], format: JSONReportFormat) -> Dict[str, Any]:
    """Export scan results data."""
    if format == JSONReportFormat.MINIMAL:
        return {
            "total_scans": len(scan_results.get("scans", [])),
            "successful_scans": len([s for s in scan_results.get("scans", []) if s.get("success", False)]),
            "scan_types": list(set(s.get("type", "unknown") for s in scan_results.get("scans", [])))
        }
    
    elif format == JSONReportFormat.COMPACT:
        scans = []
        for scan in scan_results.get("scans", []):
            scans.append({
                "type": scan.get("type"),
                "target": scan.get("target"),
                "success": scan.get("success"),
                "duration": scan.get("duration"),
                "findings_count": len(scan.get("findings", []))
            })
        
        return {
            "scans": scans,
            "total_scans": len(scans),
            "successful_scans": len([s for s in scans if s["success"]])
        }
    
    else:  # DETAILED
        return {
            "scans": scan_results.get("scans", []),
            "scan_metadata": {
                "total_scans": len(scan_results.get("scans", [])),
                "successful_scans": len([s for s in scan_results.get("scans", []) if s.get("success", False)]),
                "failed_scans": len([s for s in scan_results.get("scans", []) if not s.get("success", False)]),
                "scan_types": list(set(s.get("type", "unknown") for s in scan_results.get("scans", []))),
                "targets": list(set(s.get("target", "unknown") for s in scan_results.get("scans", [])))
            }
        }

async def export_vulnerability_data(vulnerability_data: List[Dict[str, Any]], format: JSONReportFormat) -> Dict[str, Any]:
    """Export vulnerability data."""
    if format == JSONReportFormat.MINIMAL:
        severity_counts = {}
        for vuln in vulnerability_data:
            severity = vuln.get("severity", "unknown")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            "total_vulnerabilities": len(vulnerability_data),
            "severity_distribution": severity_counts
        }
    
    elif format == JSONReportFormat.COMPACT:
        vulns = []
        for vuln in vulnerability_data:
            vulns.append({
                "title": vuln.get("title"),
                "severity": vuln.get("severity"),
                "cvss_score": vuln.get("cvss_score"),
                "affected_component": vuln.get("affected_component")
            })
        
        return {
            "vulnerabilities": vulns,
            "total_count": len(vulns)
        }
    
    else:  # DETAILED
        return {
            "vulnerabilities": vulnerability_data,
            "vulnerability_metadata": {
                "total_vulnerabilities": len(vulnerability_data),
                "severity_distribution": {
                    "critical": len([v for v in vulnerability_data if v.get("severity") == "critical"]),
                    "high": len([v for v in vulnerability_data if v.get("severity") == "high"]),
                    "medium": len([v for v in vulnerability_data if v.get("severity") == "medium"]),
                    "low": len([v for v in vulnerability_data if v.get("severity") == "low"])
                },
                "cvss_score_distribution": {
                    "9.0-10.0": len([v for v in vulnerability_data if v.get("cvss_score", 0) >= 9.0]),
                    "7.0-8.9": len([v for v in vulnerability_data if 7.0 <= v.get("cvss_score", 0) < 9.0]),
                    "4.0-6.9": len([v for v in vulnerability_data if 4.0 <= v.get("cvss_score", 0) < 7.0]),
                    "0.1-3.9": len([v for v in vulnerability_data if 0.1 <= v.get("cvss_score", 0) < 4.0])
                }
            }
        }

async def export_enumeration_data(enumeration_data: Dict[str, Any], format: JSONReportFormat) -> Dict[str, Any]:
    """Export enumeration data."""
    if format == JSONReportFormat.MINIMAL:
        return {
            "enumeration_types": list(enumeration_data.keys()),
            "total_records": sum(
                len(results.get("records", [])) 
                for results in enumeration_data.values() 
                if isinstance(results, dict)
            )
        }
    
    elif format == JSONReportFormat.COMPACT:
        enum_results = {}
        for enum_type, results in enumeration_data.items():
            if isinstance(results, dict):
                enum_results[enum_type] = {
                    "record_count": len(results.get("records", [])),
                    "duration": results.get("duration"),
                    "success": results.get("success", False)
                }
        
        return {
            "enumeration_results": enum_results,
            "total_types": len(enum_results)
        }
    
    else:  # DETAILED
        return {
            "enumeration_data": enumeration_data,
            "enumeration_metadata": {
                "enumeration_types": list(enumeration_data.keys()),
                "total_records": sum(
                    len(results.get("records", [])) 
                    for results in enumeration_data.values() 
                    if isinstance(results, dict)
                ),
                "successful_enumerations": sum(
                    1 for results in enumeration_data.values() 
                    if isinstance(results, dict) and results.get("success", False)
                )
            }
        }

async def export_attack_data(attack_data: Dict[str, Any], format: JSONReportFormat) -> Dict[str, Any]:
    """Export attack data."""
    if format == JSONReportFormat.MINIMAL:
        successful_attacks = sum(
            1 for results in attack_data.values() 
            if isinstance(results, dict) and results.get("successful_attempts", 0) > 0
        )
        
        return {
            "attack_types": list(attack_data.keys()),
            "successful_attacks": successful_attacks,
            "total_attacks": len(attack_data)
        }
    
    elif format == JSONReportFormat.COMPACT:
        attack_results = {}
        for attack_type, results in attack_data.items():
            if isinstance(results, dict):
                attack_results[attack_type] = {
                    "successful_attempts": results.get("successful_attempts", 0),
                    "total_attempts": results.get("total_attempts", 0),
                    "duration": results.get("duration"),
                    "credentials_found": len(results.get("successful_credentials", []))
                }
        
        return {
            "attack_results": attack_results,
            "total_attack_types": len(attack_results)
        }
    
    else:  # DETAILED
        return {
            "attack_data": attack_data,
            "attack_metadata": {
                "attack_types": list(attack_data.keys()),
                "total_attacks": len(attack_data),
                "successful_attacks": sum(
                    1 for results in attack_data.values() 
                    if isinstance(results, dict) and results.get("successful_attempts", 0) > 0
                ),
                "total_credentials_found": sum(
                    len(results.get("successful_credentials", []))
                    for results in attack_data.values()
                    if isinstance(results, dict)
                )
            }
        }

async def create_structured_summary(
    scan_results: Optional[Dict[str, Any]] = None,
    vulnerability_data: Optional[List[Dict[str, Any]]] = None,
    enumeration_data: Optional[Dict[str, Any]] = None,
    attack_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create structured summary."""
    summary = {
        "assessment_overview": {
            "total_findings": 0,
            "risk_level": "LOW",
            "assessment_completed": True
        },
        "key_metrics": {}
    }
    
    # Calculate total findings
    total_findings = 0
    
    if scan_results:
        scans = scan_results.get("scans", [])
        total_findings += len(scans)
        summary["key_metrics"]["scans"] = {
            "total": len(scans),
            "successful": len([s for s in scans if s.get("success", False)]),
            "failed": len([s for s in scans if not s.get("success", False)])
        }
    
    if vulnerability_data:
        total_findings += len(vulnerability_data)
        summary["key_metrics"]["vulnerabilities"] = {
            "total": len(vulnerability_data),
            "critical": len([v for v in vulnerability_data if v.get("severity") == "critical"]),
            "high": len([v for v in vulnerability_data if v.get("severity") == "high"]),
            "medium": len([v for v in vulnerability_data if v.get("severity") == "medium"]),
            "low": len([v for v in vulnerability_data if v.get("severity") == "low"])
        }
    
    if enumeration_data:
        total_findings += len(enumeration_data)
        summary["key_metrics"]["enumeration"] = {
            "types": len(enumeration_data),
            "total_records": sum(
                len(results.get("records", [])) 
                for results in enumeration_data.values() 
                if isinstance(results, dict)
            )
        }
    
    if attack_data:
        total_findings += len(attack_data)
        successful_attacks = sum(
            1 for results in attack_data.values() 
            if isinstance(results, dict) and results.get("successful_attempts", 0) > 0
        )
        summary["key_metrics"]["attacks"] = {
            "total": len(attack_data),
            "successful": successful_attacks,
            "success_rate": (successful_attacks / len(attack_data) * 100) if attack_data else 0
        }
    
    summary["assessment_overview"]["total_findings"] = total_findings
    
    # Determine risk level
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
    
    summary["assessment_overview"]["risk_level"] = risk_level
    
    return summary

async def create_statistics(
    scan_results: Optional[Dict[str, Any]] = None,
    vulnerability_data: Optional[List[Dict[str, Any]]] = None,
    enumeration_data: Optional[Dict[str, Any]] = None,
    attack_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create detailed statistics."""
    stats = {
        "scan_statistics": {},
        "vulnerability_statistics": {},
        "enumeration_statistics": {},
        "attack_statistics": {},
        "overall_statistics": {}
    }
    
    # Scan statistics
    if scan_results:
        scans = scan_results.get("scans", [])
        scan_types = {}
        for scan in scans:
            scan_type = scan.get("type", "unknown")
            scan_types[scan_type] = scan_types.get(scan_type, 0) + 1
        
        stats["scan_statistics"] = {
            "total_scans": len(scans),
            "scan_types": scan_types,
            "average_duration": sum(s.get("duration", 0) for s in scans) / len(scans) if scans else 0,
            "success_rate": (len([s for s in scans if s.get("success", False)]) / len(scans) * 100) if scans else 0
        }
    
    # Vulnerability statistics
    if vulnerability_data:
        severity_dist = {}
        cvss_scores = []
        for vuln in vulnerability_data:
            severity = vuln.get("severity", "unknown")
            severity_dist[severity] = severity_dist.get(severity, 0) + 1
            
            cvss_score = vuln.get("cvss_score")
            if cvss_score and isinstance(cvss_score, (int, float)):
                cvss_scores.append(cvss_score)
        
        stats["vulnerability_statistics"] = {
            "total_vulnerabilities": len(vulnerability_data),
            "severity_distribution": severity_dist,
            "average_cvss_score": sum(cvss_scores) / len(cvss_scores) if cvss_scores else 0,
            "highest_cvss_score": max(cvss_scores) if cvss_scores else 0,
            "lowest_cvss_score": min(cvss_scores) if cvss_scores else 0
        }
    
    # Enumeration statistics
    if enumeration_data:
        total_records = 0
        enum_durations = []
        for results in enumeration_data.values():
            if isinstance(results, dict):
                total_records += len(results.get("records", []))
                if "duration" in results:
                    enum_durations.append(results["duration"])
        
        stats["enumeration_statistics"] = {
            "enumeration_types": len(enumeration_data),
            "total_records": total_records,
            "average_duration": sum(enum_durations) / len(enum_durations) if enum_durations else 0
        }
    
    # Attack statistics
    if attack_data:
        total_attempts = 0
        successful_attempts = 0
        attack_durations = []
        total_credentials = 0
        
        for results in attack_data.values():
            if isinstance(results, dict):
                total_attempts += results.get("total_attempts", 0)
                successful_attempts += results.get("successful_attempts", 0)
                total_credentials += len(results.get("successful_credentials", []))
                
                if "duration" in results:
                    attack_durations.append(results["duration"])
        
        stats["attack_statistics"] = {
            "attack_types": len(attack_data),
            "total_attempts": total_attempts,
            "successful_attempts": successful_attempts,
            "success_rate": (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0,
            "total_credentials_found": total_credentials,
            "average_duration": sum(attack_durations) / len(attack_durations) if attack_durations else 0
        }
    
    # Overall statistics
    stats["overall_statistics"] = {
        "total_operations": (
            len(scan_results.get("scans", []) if scan_results else []) +
            len(vulnerability_data or []) +
            len(enumeration_data or {}) +
            len(attack_data or {})
        ),
        "assessment_completion_time": time.time(),
        "data_points_analyzed": sum([
            len(scan_results.get("scans", []) if scan_results else []),
            len(vulnerability_data or []),
            sum(len(results.get("records", [])) for results in (enumeration_data or {}).values() if isinstance(results, dict)),
            sum(results.get("total_attempts", 0) for results in (attack_data or {}).values() if isinstance(results, dict))
        ])
    }
    
    return stats

async def create_recommendations(vulnerability_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create structured recommendations."""
    recommendations = []
    
    # Group vulnerabilities by severity
    vuln_by_severity = {}
    for vuln in vulnerability_data:
        severity = vuln.get("severity", "unknown")
        if severity not in vuln_by_severity:
            vuln_by_severity[severity] = []
        vuln_by_severity[severity].append(vuln)
    
    # Create recommendations for each severity level
    severity_order = ["critical", "high", "medium", "low"]
    
    for severity in severity_order:
        if severity in vuln_by_severity:
            vulns = vuln_by_severity[severity]
            
            # Collect unique recommendations
            unique_recommendations = set()
            for vuln in vulns:
                rec = vuln.get("recommendation")
                if rec:
                    unique_recommendations.add(rec)
            
            recommendations.append({
                "severity": severity,
                "vulnerability_count": len(vulns),
                "recommendations": list(unique_recommendations),
                "priority": "immediate" if severity in ["critical", "high"] else "high" if severity == "medium" else "medium"
            })
    
    return recommendations

async def create_structured_report(
    scan_results: Optional[Dict[str, Any]] = None,
    vulnerability_data: Optional[List[Dict[str, Any]]] = None,
    enumeration_data: Optional[Dict[str, Any]] = None,
    attack_data: Optional[Dict[str, Any]] = None,
    format: JSONReportFormat = JSONReportFormat.DETAILED
) -> Dict[str, Any]:
    """Create a complete structured report."""
    report = {
        "report_header": {
            "title": "Security Assessment Report",
            "generated_at": datetime.now().isoformat(),
            "format": format.value,
            "version": "1.0.0"
        },
        "executive_summary": await create_structured_summary(scan_results, vulnerability_data, enumeration_data, attack_data),
        "detailed_findings": {
            "scans": await export_scan_data(scan_results, format) if scan_results else {},
            "vulnerabilities": await export_vulnerability_data(vulnerability_data, format) if vulnerability_data else {},
            "enumeration": await export_enumeration_data(enumeration_data, format) if enumeration_data else {},
            "attacks": await export_attack_data(attack_data, format) if attack_data else {}
        },
        "statistics": await create_statistics(scan_results, vulnerability_data, enumeration_data, attack_data),
        "recommendations": await create_recommendations(vulnerability_data) if vulnerability_data else []
    }
    
    return report 