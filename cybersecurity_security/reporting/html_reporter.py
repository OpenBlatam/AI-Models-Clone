"""
HTML Reporter

Provides HTML-based reporting with modern styling and interactive elements.
"""

import asyncio
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, validator
from enum import Enum
import time
from datetime import datetime
import json
import base64

class HTMLReportTemplate(str, Enum):
    """Enumeration of HTML report templates."""
    MODERN = "modern"
    CLASSIC = "classic"
    DARK = "dark"
    MINIMAL = "minimal"

class HTMLReportRequest(BaseModel):
    """Pydantic model for HTML report request."""
    scan_results: Optional[Dict[str, Any]] = Field(None, description="Scan results to report")
    vulnerability_data: Optional[List[Dict[str, Any]]] = Field(None, description="Vulnerability data")
    enumeration_data: Optional[Dict[str, Any]] = Field(None, description="Enumeration results")
    attack_data: Optional[Dict[str, Any]] = Field(None, description="Attack results")
    template: HTMLReportTemplate = Field(default=HTMLReportTemplate.MODERN, description="HTML template")
    include_charts: bool = Field(default=True, description="Include interactive charts")
    include_timeline: bool = Field(default=True, description="Include timeline")
    include_recommendations: bool = Field(default=True, description="Include recommendations")
    custom_css: Optional[str] = Field(None, description="Custom CSS styles")
    custom_js: Optional[str] = Field(None, description="Custom JavaScript")
    
    @validator('scan_results', 'vulnerability_data', 'enumeration_data', 'attack_data')
    def validate_data(cls, v):
        if v is not None and not v:
            raise ValueError("Data cannot be empty if provided")
        return v

class HTMLReportResult(BaseModel):
    """Pydantic model for HTML report result."""
    report_generated: bool
    html_content: str
    report_size: int
    report_duration: float
    report_completed_at: float
    sections_included: List[str]

# HTML Templates
MODERN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Security Assessment Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 0; text-align: center; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.2em; opacity: 0.9; }
        .section { margin: 30px 0; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .section h2 { color: #667eea; margin-bottom: 20px; border-bottom: 2px solid #667eea; padding-bottom: 10px; }
        .summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }
        .summary-card { background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }
        .summary-card h3 { color: #667eea; margin-bottom: 10px; }
        .summary-card .number { font-size: 2em; font-weight: bold; }
        .critical { color: #dc3545; }
        .high { color: #fd7e14; }
        .medium { color: #ffc107; }
        .low { color: #28a745; }
        .vulnerability-item { background: #f8f9fa; margin: 10px 0; padding: 15px; border-radius: 8px; border-left: 4px solid #667eea; }
        .vulnerability-item.critical { border-left-color: #dc3545; }
        .vulnerability-item.high { border-left-color: #fd7e14; }
        .vulnerability-item.medium { border-left-color: #ffc107; }
        .vulnerability-item.low { border-left-color: #28a745; }
        .chart-container { position: relative; height: 400px; margin: 20px 0; }
        .timeline { position: relative; padding: 20px 0; }
        .timeline-item { display: flex; margin: 20px 0; }
        .timeline-marker { width: 20px; height: 20px; background: #667eea; border-radius: 50%; margin-right: 20px; }
        .timeline-content { flex: 1; }
        .recommendations { background: #e3f2fd; padding: 20px; border-radius: 8px; }
        .recommendation-item { margin: 10px 0; padding: 10px; background: white; border-radius: 5px; }
        .footer { text-align: center; padding: 20px; color: #666; border-top: 1px solid #eee; margin-top: 40px; }
        @media (max-width: 768px) { .summary-grid { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1>🔒 Security Assessment Report</h1>
            <p>Comprehensive security analysis and vulnerability assessment</p>
            <p>Generated on {timestamp}</p>
        </div>
    </div>
    
    <div class="container">
        {content}
    </div>
    
    <div class="footer">
        <p>This report was generated by the Cybersecurity Security Toolkit</p>
        <p>For authorized security testing purposes only</p>
    </div>
</body>
</html>
"""

async def generate_html_report_async(data: HTMLReportRequest) -> HTMLReportResult:
    """Generate comprehensive HTML report asynchronously."""
    start_time = time.time()
    sections_included = []
    
    # Generate report content
    content_parts = []
    
    # Executive Summary
    if any([data.scan_results, data.vulnerability_data, data.enumeration_data, data.attack_data]):
        sections_included.append("executive_summary")
        summary_section = await create_executive_summary(
            data.scan_results, data.vulnerability_data, data.enumeration_data, data.attack_data
        )
        content_parts.append(summary_section)
    
    # Scan Results
    if data.scan_results:
        sections_included.append("scan_results")
        scan_section = await create_scan_summary(data.scan_results, data.include_charts)
        content_parts.append(scan_section)
    
    # Vulnerability Details
    if data.vulnerability_data:
        sections_included.append("vulnerability_details")
        vuln_section = await create_vulnerability_table(data.vulnerability_data)
        content_parts.append(vuln_section)
    
    # Enumeration Results
    if data.enumeration_data:
        sections_included.append("enumeration_results")
        enum_section = await create_enumeration_summary(data.enumeration_data)
        content_parts.append(enum_section)
    
    # Attack Results
    if data.attack_data:
        sections_included.append("attack_results")
        attack_section = await create_attack_summary(data.attack_data)
        content_parts.append(attack_section)
    
    # Technical Details
    if data.include_timeline:
        sections_included.append("technical_details")
        tech_section = await create_technical_details(
            data.scan_results, data.vulnerability_data, data.enumeration_data, data.attack_data
        )
        content_parts.append(tech_section)
    
    # Recommendations
    if data.include_recommendations and data.vulnerability_data:
        sections_included.append("recommendations")
        rec_section = await create_recommendations_section(data.vulnerability_data)
        content_parts.append(rec_section)
    
    # Generate HTML
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = "\n".join(content_parts)
    
    html_content = MODERN_TEMPLATE.format(
        timestamp=timestamp,
        content=content
    )
    
    # Add custom CSS/JS if provided
    if data.custom_css:
        html_content = html_content.replace("</style>", f"{data.custom_css}\n</style>")
    
    if data.custom_js:
        html_content = html_content.replace("</body>", f"<script>{data.custom_js}</script>\n</body>")
    
    report_duration = time.time() - start_time
    
    return HTMLReportResult(
        report_generated=True,
        html_content=html_content,
        report_size=len(html_content),
        report_duration=report_duration,
        report_completed_at=time.time(),
        sections_included=sections_included
    )

async def create_executive_summary(
    scan_results: Optional[Dict[str, Any]] = None,
    vulnerability_data: Optional[List[Dict[str, Any]]] = None,
    enumeration_data: Optional[Dict[str, Any]] = None,
    attack_data: Optional[Dict[str, Any]] = None
) -> str:
    """Create executive summary section."""
    summary_parts = []
    summary_parts.append('<div class="section">')
    summary_parts.append('<h2>📊 Executive Summary</h2>')
    
    # Summary grid
    summary_parts.append('<div class="summary-grid">')
    
    # Scan summary
    if scan_results:
        scans = scan_results.get("scans", [])
        successful_scans = len([s for s in scans if s.get("success", False)])
        summary_parts.append(f'''
            <div class="summary-card">
                <h3>🔍 Scans Completed</h3>
                <div class="number">{successful_scans}/{len(scans)}</div>
                <p>Successful scans</p>
            </div>
        ''')
    
    # Vulnerability summary
    if vulnerability_data:
        total_vulns = len(vulnerability_data)
        critical_vulns = len([v for v in vulnerability_data if v.get("severity") == "critical"])
        high_vulns = len([v for v in vulnerability_data if v.get("severity") == "high"])
        
        summary_parts.append(f'''
            <div class="summary-card">
                <h3>🚨 Vulnerabilities</h3>
                <div class="number">{total_vulns}</div>
                <p>Total findings</p>
                <p><span class="critical">{critical_vulns} Critical</span> | <span class="high">{high_vulns} High</span></p>
            </div>
        ''')
    
    # Enumeration summary
    if enumeration_data:
        enum_count = len(enumeration_data)
        summary_parts.append(f'''
            <div class="summary-card">
                <h3>🔍 Enumeration</h3>
                <div class="number">{enum_count}</div>
                <p>Services enumerated</p>
            </div>
        ''')
    
    # Attack summary
    if attack_data:
        successful_attacks = sum(
            1 for results in attack_data.values() 
            if isinstance(results, dict) and results.get("successful_attempts", 0) > 0
        )
        summary_parts.append(f'''
            <div class="summary-card">
                <h3>⚔️ Attacks</h3>
                <div class="number">{successful_attacks}/{len(attack_data)}</div>
                <p>Successful attempts</p>
            </div>
        ''')
    
    summary_parts.append('</div>')
    
    # Risk assessment
    risk_level = "LOW"
    risk_color = "low"
    if vulnerability_data:
        critical_count = len([v for v in vulnerability_data if v.get("severity") == "critical"])
        high_count = len([v for v in vulnerability_data if v.get("severity") == "high"])
        
        if critical_count > 0:
            risk_level = "CRITICAL"
            risk_color = "critical"
        elif high_count > 2:
            risk_level = "HIGH"
            risk_color = "high"
        elif high_count > 0 or len(vulnerability_data) > 5:
            risk_level = "MEDIUM"
            risk_color = "medium"
    
    summary_parts.append(f'''
        <div style="text-align: center; margin: 20px 0;">
            <h3>Overall Risk Level</h3>
            <div class="number {risk_color}">{risk_level}</div>
        </div>
    ''')
    
    summary_parts.append('</div>')
    return "\n".join(summary_parts)

async def create_vulnerability_table(vulnerability_data: List[Dict[str, Any]]) -> str:
    """Create vulnerability details table."""
    vuln_parts = []
    vuln_parts.append('<div class="section">')
    vuln_parts.append('<h2>🚨 Vulnerability Details</h2>')
    
    for vuln in vulnerability_data:
        severity = vuln.get("severity", "unknown")
        title = vuln.get("title", "Unknown Vulnerability")
        description = vuln.get("description", "No description available")
        cvss_score = vuln.get("cvss_score", "N/A")
        affected_component = vuln.get("affected_component", "Unknown")
        recommendation = vuln.get("recommendation", "No recommendation available")
        
        vuln_parts.append(f'''
            <div class="vulnerability-item {severity}">
                <h3>{title}</h3>
                <p><strong>Severity:</strong> <span class="{severity}">{severity.upper()}</span></p>
                <p><strong>CVSS Score:</strong> {cvss_score}</p>
                <p><strong>Affected Component:</strong> {affected_component}</p>
                <p><strong>Description:</strong> {description}</p>
                <p><strong>Recommendation:</strong> {recommendation}</p>
            </div>
        ''')
    
    vuln_parts.append('</div>')
    return "\n".join(vuln_parts)

async def create_scan_summary(scan_results: Dict[str, Any], include_charts: bool = True) -> str:
    """Create scan results summary."""
    scan_parts = []
    scan_parts.append('<div class="section">')
    scan_parts.append('<h2>🔍 Scan Results</h2>')
    
    scans = scan_results.get("scans", [])
    for scan in scans:
        scan_type = scan.get("type", "Unknown")
        success = scan.get("success", False)
        target = scan.get("target", "Unknown")
        duration = scan.get("duration", 0)
        findings = scan.get("findings", [])
        
        status_class = "success" if success else "failed"
        status_text = "SUCCESS" if success else "FAILED"
        
        scan_parts.append(f'''
            <div class="vulnerability-item">
                <h3>{scan_type} Scan</h3>
                <p><strong>Target:</strong> {target}</p>
                <p><strong>Status:</strong> <span class="{status_class}">{status_text}</span></p>
                <p><strong>Duration:</strong> {duration:.2f}s</p>
                <p><strong>Findings:</strong> {len(findings)}</p>
            </div>
        ''')
    
    if include_charts and scans:
        # Add chart for scan results
        scan_parts.append('''
            <div class="chart-container">
                <canvas id="scanChart"></canvas>
            </div>
            <script>
                const scanCtx = document.getElementById('scanChart').getContext('2d');
                new Chart(scanCtx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Successful', 'Failed'],
                        datasets: [{
                            data: [''' + str(len([s for s in scans if s.get("success", False)])) + ''', ''' + str(len([s for s in scans if not s.get("success", False)])) + '''],
                            backgroundColor: ['#28a745', '#dc3545']
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false
                    }
                });
            </script>
        ''')
    
    scan_parts.append('</div>')
    return "\n".join(scan_parts)

async def create_enumeration_summary(enumeration_data: Dict[str, Any]) -> str:
    """Create enumeration results summary."""
    enum_parts = []
    enum_parts.append('<div class="section">')
    enum_parts.append('<h2>🔍 Enumeration Results</h2>')
    
    for enum_type, results in enumeration_data.items():
        enum_parts.append(f'<h3>{enum_type.upper()} Enumeration</h3>')
        
        if isinstance(results, dict):
            if "records" in results:
                records = results["records"]
                enum_parts.append(f'<p><strong>Records Found:</strong> {len(records)}</p>')
                
                if records:
                    enum_parts.append('<ul>')
                    for record in records[:10]:  # Show first 10 records
                        enum_parts.append(f'<li>{record}</li>')
                    if len(records) > 10:
                        enum_parts.append(f'<li>... and {len(records) - 10} more</li>')
                    enum_parts.append('</ul>')
            
            if "duration" in results:
                enum_parts.append(f'<p><strong>Duration:</strong> {results["duration"]:.2f}s</p>')
    
    enum_parts.append('</div>')
    return "\n".join(enum_parts)

async def create_attack_summary(attack_data: Dict[str, Any]) -> str:
    """Create attack results summary."""
    attack_parts = []
    attack_parts.append('<div class="section">')
    attack_parts.append('<h2>⚔️ Attack Results</h2>')
    
    for attack_type, results in attack_data.items():
        attack_parts.append(f'<h3>{attack_type.upper()} Attack</h3>')
        
        if isinstance(results, dict):
            successful_attempts = results.get("successful_attempts", 0)
            total_attempts = results.get("total_attempts", 0)
            duration = results.get("duration", 0)
            
            success_rate = (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0
            
            attack_parts.append(f'''
                <p><strong>Success Rate:</strong> {successful_attempts}/{total_attempts} ({success_rate:.1f}%)</p>
                <p><strong>Duration:</strong> {duration:.2f}s</p>
            ''')
            
            if "successful_credentials" in results:
                creds = results["successful_credentials"]
                if creds:
                    attack_parts.append(f'<p><strong>Credentials Found:</strong> {len(creds)}</p>')
                    attack_parts.append('<ul>')
                    for cred in creds[:5]:  # Show first 5 credentials
                        attack_parts.append(f'<li>{cred.get("username", "unknown")}:{cred.get("password", "unknown")}</li>')
                    if len(creds) > 5:
                        attack_parts.append(f'<li>... and {len(creds) - 5} more</li>')
                    attack_parts.append('</ul>')
    
    attack_parts.append('</div>')
    return "\n".join(attack_parts)

async def create_technical_details(
    scan_results: Optional[Dict[str, Any]] = None,
    vulnerability_data: Optional[List[Dict[str, Any]]] = None,
    enumeration_data: Optional[Dict[str, Any]] = None,
    attack_data: Optional[Dict[str, Any]] = None
) -> str:
    """Create technical details section."""
    tech_parts = []
    tech_parts.append('<div class="section">')
    tech_parts.append('<h2>🔧 Technical Details</h2>')
    
    tech_parts.append('<div class="timeline">')
    
    # Add timeline items based on available data
    if scan_results:
        tech_parts.append('''
            <div class="timeline-item">
                <div class="timeline-marker"></div>
                <div class="timeline-content">
                    <h4>Security Scans</h4>
                    <p>Port scanning, vulnerability scanning, and web application scanning completed</p>
                </div>
            </div>
        ''')
    
    if vulnerability_data:
        tech_parts.append('''
            <div class="timeline-item">
                <div class="timeline-marker"></div>
                <div class="timeline-content">
                    <h4>Vulnerability Assessment</h4>
                    <p>Comprehensive vulnerability analysis and risk assessment performed</p>
                </div>
            </div>
        ''')
    
    if enumeration_data:
        tech_parts.append('''
            <div class="timeline-item">
                <div class="timeline-marker"></div>
                <div class="timeline-content">
                    <h4>Service Enumeration</h4>
                    <p>DNS, SMB, SSH, and other service enumeration completed</p>
                </div>
            </div>
        ''')
    
    if attack_data:
        tech_parts.append('''
            <div class="timeline-item">
                <div class="timeline-marker"></div>
                <div class="timeline-content">
                    <h4>Penetration Testing</h4>
                    <p>Brute force attacks and exploit testing performed</p>
                </div>
            </div>
        ''')
    
    tech_parts.append('</div>')
    tech_parts.append('</div>')
    return "\n".join(tech_parts)

async def create_recommendations_section(vulnerability_data: List[Dict[str, Any]]) -> str:
    """Create recommendations section."""
    rec_parts = []
    rec_parts.append('<div class="section">')
    rec_parts.append('<h2>💡 Recommendations</h2>')
    
    rec_parts.append('<div class="recommendations">')
    
    # Group recommendations by severity
    recommendations = {}
    for vuln in vulnerability_data:
        severity = vuln.get("severity", "unknown")
        recommendation = vuln.get("recommendation", "No recommendation available")
        
        if severity not in recommendations:
            recommendations[severity] = []
        
        if recommendation not in recommendations[severity]:
            recommendations[severity].append(recommendation)
    
    # Sort by severity priority
    severity_order = ["critical", "high", "medium", "low"]
    
    for severity in severity_order:
        if severity in recommendations:
            rec_parts.append(f'<h3 class="{severity}">{severity.upper()} Priority</h3>')
            
            for recommendation in recommendations[severity]:
                rec_parts.append(f'''
                    <div class="recommendation-item">
                        <p>{recommendation}</p>
                    </div>
                ''')
    
    rec_parts.append('</div>')
    rec_parts.append('</div>')
    return "\n".join(rec_parts) 