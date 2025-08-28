from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_RETRIES = 100

# Constants
TIMEOUT_SECONDS = 60

import asyncio
import time
from typing import Dict, Any
from ..reporting import (
from typing import Any, List, Dict, Optional
import logging
"""
Reporting Examples

Demonstrates how to use the comprehensive reporting modules.
"""


# Import reporting modules
    # Console Reporter
    ConsoleReportRequest, ConsoleReportLevel, generate_console_report_async,
    
    # HTML Reporter
    HTMLReportRequest, HTMLReportTemplate, generate_html_report_async,
    
    # JSON Reporter
    JSONReportRequest, JSONReportFormat, generate_json_report_async,
    
    # Report Aggregator
    ReportAggregatorRequest, ReportType, aggregate_reports_async
)

async def run_console_reporting_examples() -> Dict[str, Any]:
    """Run console reporting examples."""
    print("📝 Running Console Reporting Examples...")
    
    results = {}
    
    # 1. Basic console report
    print("1. Testing Basic Console Report...")
    console_request = ConsoleReportRequest(
        scan_results={
            "scans": [
                {
                    "type": "port_scan",
                    "target": "192.168.1.1",
                    "success": True,
                    "duration": 10.5,
                    "findings": ["Port 80 open", "Port 443 open"],
                    "ports": [80, 443]
                },
                {
                    "type": "vulnerability_scan",
                    "target": "192.168.1.1",
                    "success": True,
                    "duration": 25.0,
                    "findings": ["SQL injection vulnerability", "XSS vulnerability"]
                }
            ]
        },
        vulnerability_data=[
            {
                "title": "SQL Injection",
                "severity": "high",
                "description": "SQL injection vulnerability in login form",
                "cvss_score": 8.5,
                "affected_component": "login.php",
                "recommendation": "Use prepared statements"
            },
            {
                "title": "Cross-Site Scripting (XSS)",
                "severity": "medium",
                "description": "Reflected XSS in search functionality",
                "cvss_score": 6.1,
                "affected_component": "search.php",
                "recommendation": "Implement input validation and output encoding"
            }
        ],
        report_level=ConsoleReportLevel.INFO,
        include_details=True,
        color_output=False,
        timestamp=True
    )
    
    console_result = await generate_console_report_async(console_request)
    results["basic_console_report"] = console_result
    print(f"   Console report generated: {console_result.report_generated}")
    print(f"   Report length: {console_result.report_length} characters")
    
    # 2. Detailed console report with all data types
    print("2. Testing Detailed Console Report...")
    detailed_console_request = ConsoleReportRequest(
        scan_results={
            "scans": [
                {"type": "port_scan", "target": "192.168.1.1", "success": True, "duration": 5.0}
            ]
        },
        vulnerability_data=[
            {"title": "Critical Vulnerability", "severity": "critical", "description": "Critical issue"}
        ],
        enumeration_data={
            "dns_enumeration": {
                "records": ["A: 192.168.1.1", "MX: mail.example.com"],
                "success": True,
                "duration": 3.0
            },
            "smb_enumeration": {
                "records": ["Share: ADMIN$", "Share: C$"],
                "success": True,
                "duration": 8.0
            }
        },
        attack_data={
            "ssh_brute_force": {
                "successful_attempts": 1,
                "total_attempts": 10,
                "successful_credentials": [{"username": "admin", "password": "password"}],
                "duration": 15.0
            },
            "http_brute_force": {
                "successful_attempts": 0,
                "total_attempts": 20,
                "successful_credentials": [],
                "duration": 12.0
            }
        },
        report_level=ConsoleReportLevel.INFO,
        include_details=True,
        color_output=False
    )
    
    detailed_console_result = await generate_console_report_async(detailed_console_request)
    results["detailed_console_report"] = detailed_console_result
    print(f"   Detailed console report generated: {detailed_console_result.report_generated}")
    print(f"   Sections processed: {len(detailed_console_result.sections_processed)}")
    
    return results

async def run_html_reporting_examples() -> Dict[str, Any]:
    """Run HTML reporting examples."""
    print("🌐 Running HTML Reporting Examples...")
    
    results = {}
    
    # 1. Basic HTML report
    print("1. Testing Basic HTML Report...")
    html_request = HTMLReportRequest(
        scan_results={
            "scans": [
                {
                    "type": "port_scan",
                    "target": "192.168.1.1",
                    "success": True,
                    "duration": 10.5,
                    "findings": ["Port 80 open", "Port 443 open"],
                    "ports": [80, 443]
                }
            ]
        },
        vulnerability_data=[
            {
                "title": "SQL Injection",
                "severity": "high",
                "description": "SQL injection vulnerability in login form",
                "cvss_score": 8.5,
                "affected_component": "login.php",
                "recommendation": "Use prepared statements"
            }
        ],
        template=HTMLReportTemplate.MODERN,
        include_charts=True,
        include_timeline=True,
        include_recommendations=True
    )
    
    html_result = await generate_html_report_async(html_request)
    results["basic_html_report"] = html_result
    print(f"   HTML report generated: {html_result.report_generated}")
    print(f"   Report size: {html_result.report_size} bytes")
    print(f"   Sections included: {len(html_result.sections_included)}")
    
    # 2. Comprehensive HTML report
    print("2. Testing Comprehensive HTML Report...")
    comprehensive_html_request = HTMLReportRequest(
        scan_results={
            "scans": [
                {"type": "port_scan", "target": "192.168.1.1", "success": True, "duration": 5.0},
                {"type": "vulnerability_scan", "target": "192.168.1.1", "success": True, "duration": 15.0},
                {"type": "web_scan", "target": "192.168.1.1", "success": False, "duration": 8.0}
            ]
        },
        vulnerability_data=[
            {"title": "Critical RCE", "severity": "critical", "description": "Remote code execution", "cvss_score": 9.8},
            {"title": "SQL Injection", "severity": "high", "description": "SQL injection", "cvss_score": 8.5},
            {"title": "XSS", "severity": "medium", "description": "Cross-site scripting", "cvss_score": 6.1},
            {"title": "Information Disclosure", "severity": "low", "description": "Info disclosure", "cvss_score": 3.0}
        ],
        enumeration_data={
            "dns_enumeration": {"records": ["A: 192.168.1.1"], "success": True, "duration": 3.0},
            "smb_enumeration": {"records": ["Share: ADMIN$"], "success": True, "duration": 8.0},
            "ssh_enumeration": {"records": ["SSH-2.0-OpenSSH_8.2"], "success": True, "duration": 2.0}
        },
        attack_data={
            "ssh_brute_force": {
                "successful_attempts": 1,
                "total_attempts": 10,
                "successful_credentials": [{"username": "admin", "password": "password"}],
                "duration": 15.0
            }
        },
        template=HTMLReportTemplate.MODERN,
        include_charts=True,
        include_timeline=True,
        include_recommendations=True,
        custom_css="""
            .custom-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
            .custom-card { border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        """
    )
    
    comprehensive_html_result = await generate_html_report_async(comprehensive_html_request)
    results["comprehensive_html_report"] = comprehensive_html_result
    print(f"   Comprehensive HTML report generated: {comprehensive_html_result.report_generated}")
    print(f"   Report size: {comprehensive_html_result.report_size} bytes")
    
    return results

async def run_json_reporting_examples() -> Dict[str, Any]:
    """Run JSON reporting examples."""
    print("📊 Running JSON Reporting Examples...")
    
    results = {}
    
    # 1. Detailed JSON report
    print("1. Testing Detailed JSON Report...")
    json_request = JSONReportRequest(
        scan_results={
            "scans": [
                {
                    "type": "port_scan",
                    "target": "192.168.1.1",
                    "success": True,
                    "duration": 10.5,
                    "findings": ["Port 80 open", "Port 443 open"],
                    "ports": [80, 443]
                }
            ]
        },
        vulnerability_data=[
            {
                "title": "SQL Injection",
                "severity": "high",
                "description": "SQL injection vulnerability in login form",
                "cvss_score": 8.5,
                "affected_component": "login.php",
                "recommendation": "Use prepared statements"
            }
        ],
        format=JSONReportFormat.DETAILED,
        include_metadata=True,
        include_timestamps=True,
        include_statistics=True
    )
    
    json_result = await generate_json_report_async(json_request)
    results["detailed_json_report"] = json_result
    print(f"   Detailed JSON report generated: {json_result.report_generated}")
    print(f"   Report size: {json_result.report_size} bytes")
    print(f"   Data sections: {len(json_result.data_sections)}")
    
    # 2. Compact JSON report
    print("2. Testing Compact JSON Report...")
    compact_json_request = JSONReportRequest(
        scan_results={
            "scans": [
                {"type": "port_scan", "target": "192.168.1.1", "success": True, "duration": 5.0},
                {"type": "vulnerability_scan", "target": "192.168.1.1", "success": True, "duration": 15.0}
            ]
        },
        vulnerability_data=[
            {"title": "XSS", "severity": "medium", "description": "XSS vulnerability", "cvss_score": 6.1},
            {"title": "CSRF", "severity": "low", "description": "CSRF vulnerability", "cvss_score": 3.0}
        ],
        format=JSONReportFormat.COMPACT,
        include_metadata=True,
        include_statistics=False
    )
    
    compact_json_result = await generate_json_report_async(compact_json_request)
    results["compact_json_report"] = compact_json_result
    print(f"   Compact JSON report generated: {compact_json_result.report_generated}")
    print(f"   Report size: {compact_json_result.report_size} bytes")
    
    # 3. Minimal JSON report
    print("3. Testing Minimal JSON Report...")
    minimal_json_request = JSONReportRequest(
        scan_results={
            "scans": [
                {"type": "port_scan", "target": "192.168.1.1", "success": True, "duration": 5.0}
            ]
        },
        vulnerability_data=[
            {"title": "Critical Vulnerability", "severity": "critical", "description": "Critical issue"}
        ],
        format=JSONReportFormat.MINIMAL,
        include_metadata=False,
        include_statistics=False
    )
    
    minimal_json_result = await generate_json_report_async(minimal_json_request)
    results["minimal_json_report"] = minimal_json_result
    print(f"   Minimal JSON report generated: {minimal_json_result.report_generated}")
    print(f"   Report size: {minimal_json_result.report_size} bytes")
    
    return results

async def run_report_aggregation_examples() -> Dict[str, Any]:
    """Run report aggregation examples."""
    print("🔗 Running Report Aggregation Examples...")
    
    results = {}
    
    # 1. Basic report aggregation
    print("1. Testing Basic Report Aggregation...")
    aggregation_request = ReportAggregatorRequest(
        scan_results={
            "scans": [
                {
                    "type": "port_scan",
                    "target": "192.168.1.1",
                    "success": True,
                    "duration": 10.5,
                    "findings": ["Port 80 open", "Port 443 open"],
                    "ports": [80, 443]
                }
            ]
        },
        vulnerability_data=[
            {
                "title": "SQL Injection",
                "severity": "high",
                "description": "SQL injection vulnerability in login form",
                "cvss_score": 8.5,
                "affected_component": "login.php",
                "recommendation": "Use prepared statements"
            }
        ],
        output_format=ReportType.COMPREHENSIVE,
        include_raw_data=True,
        generate_timeline=True
    )
    
    aggregation_result = await aggregate_reports_async(aggregation_request)
    results["basic_aggregation"] = aggregation_result
    print(f"   Basic aggregation successful: {aggregation_result.aggregation_successful}")
    print(f"   Reports combined: {len(aggregation_result.reports_combined)}")
    print(f"   Report size: {aggregation_result.report_size} bytes")
    
    # 2. Comprehensive report aggregation
    print("2. Testing Comprehensive Report Aggregation...")
    comprehensive_aggregation_request = ReportAggregatorRequest(
        scan_results={
            "scans": [
                {"type": "port_scan", "target": "192.168.1.1", "success": True, "duration": 5.0},
                {"type": "vulnerability_scan", "target": "192.168.1.1", "success": True, "duration": 15.0},
                {"type": "web_scan", "target": "192.168.1.1", "success": False, "duration": 8.0}
            ]
        },
        vulnerability_data=[
            {"title": "Critical RCE", "severity": "critical", "description": "Remote code execution", "cvss_score": 9.8},
            {"title": "SQL Injection", "severity": "high", "description": "SQL injection", "cvss_score": 8.5},
            {"title": "XSS", "severity": "medium", "description": "Cross-site scripting", "cvss_score": 6.1},
            {"title": "Information Disclosure", "severity": "low", "description": "Info disclosure", "cvss_score": 3.0}
        ],
        enumeration_data={
            "dns_enumeration": {"records": ["A: 192.168.1.1"], "success": True, "duration": 3.0},
            "smb_enumeration": {"records": ["Share: ADMIN$"], "success": True, "duration": 8.0},
            "ssh_enumeration": {"records": ["SSH-2.0-OpenSSH_8.2"], "success": True, "duration": 2.0}
        },
        attack_data={
            "ssh_brute_force": {
                "successful_attempts": 1,
                "total_attempts": 10,
                "successful_credentials": [{"username": "admin", "password": "password"}],
                "duration": 15.0
            },
            "http_brute_force": {
                "successful_attempts": 0,
                "total_attempts": 20,
                "successful_credentials": [],
                "duration": 12.0
            }
        },
        output_format=ReportType.COMPREHENSIVE,
        include_raw_data=True,
        generate_timeline=True
    )
    
    comprehensive_aggregation_result = await aggregate_reports_async(comprehensive_aggregation_request)
    results["comprehensive_aggregation"] = comprehensive_aggregation_result
    print(f"   Comprehensive aggregation successful: {comprehensive_aggregation_result.aggregation_successful}")
    print(f"   Reports combined: {len(comprehensive_aggregation_result.reports_combined)}")
    print(f"   Report size: {comprehensive_aggregation_result.report_size} bytes")
    
    return results

async def run_integrated_reporting_examples() -> Dict[str, Any]:
    """Run integrated reporting examples combining all report types."""
    print("🔄 Running Integrated Reporting Examples...")
    
    results = {}
    
    # Sample comprehensive data
    comprehensive_data = {
        "scan_results": {
            "scans": [
                {"type": "port_scan", "target": "192.168.1.1", "success": True, "duration": 5.0},
                {"type": "vulnerability_scan", "target": "192.168.1.1", "success": True, "duration": 15.0},
                {"type": "web_scan", "target": "192.168.1.1", "success": True, "duration": 8.0}
            ]
        },
        "vulnerability_data": [
            {"title": "Critical RCE", "severity": "critical", "description": "Remote code execution", "cvss_score": 9.8},
            {"title": "SQL Injection", "severity": "high", "description": "SQL injection", "cvss_score": 8.5},
            {"title": "XSS", "severity": "medium", "description": "Cross-site scripting", "cvss_score": 6.1}
        ],
        "enumeration_data": {
            "dns_enumeration": {"records": ["A: 192.168.1.1"], "success": True, "duration": 3.0},
            "smb_enumeration": {"records": ["Share: ADMIN$"], "success": True, "duration": 8.0}
        },
        "attack_data": {
            "ssh_brute_force": {
                "successful_attempts": 1,
                "total_attempts": 10,
                "successful_credentials": [{"username": "admin", "password": "password"}],
                "duration": 15.0
            }
        }
    }
    
    print("Generating all report types with comprehensive data...")
    
    # Generate all report types concurrently
    console_result, html_result, json_result, aggregation_result = await asyncio.gather(
        generate_console_report_async(ConsoleReportRequest(
            scan_results=comprehensive_data["scan_results"],
            vulnerability_data=comprehensive_data["vulnerability_data"],
            enumeration_data=comprehensive_data["enumeration_data"],
            attack_data=comprehensive_data["attack_data"],
            color_output=False
        )),
        generate_html_report_async(HTMLReportRequest(
            scan_results=comprehensive_data["scan_results"],
            vulnerability_data=comprehensive_data["vulnerability_data"],
            enumeration_data=comprehensive_data["enumeration_data"],
            attack_data=comprehensive_data["attack_data"]
        )),
        generate_json_report_async(JSONReportRequest(
            scan_results=comprehensive_data["scan_results"],
            vulnerability_data=comprehensive_data["vulnerability_data"],
            enumeration_data=comprehensive_data["enumeration_data"],
            attack_data=comprehensive_data["attack_data"]
        )),
        aggregate_reports_async(ReportAggregatorRequest(
            scan_results=comprehensive_data["scan_results"],
            vulnerability_data=comprehensive_data["vulnerability_data"],
            enumeration_data=comprehensive_data["enumeration_data"],
            attack_data=comprehensive_data["attack_data"],
            output_format=ReportType.COMPREHENSIVE
        )),
        return_exceptions=True
    )
    
    # Compile results
    results["integrated_reporting"] = {
        "console_report": console_result if not isinstance(console_result, Exception) else {"error": str(console_result)},
        "html_report": html_result if not isinstance(html_result, Exception) else {"error": str(html_result)},
        "json_report": json_result if not isinstance(json_result, Exception) else {"error": str(json_result)},
        "aggregation_report": aggregation_result if not isinstance(aggregation_result, Exception) else {"error": str(aggregation_result)}
    }
    
    # Summary
    successful_reports = 0
    total_reports = 4
    
    for report_type, result in results["integrated_reporting"].items():
        if "error" not in result:
            successful_reports += 1
            print(f"   ✅ {report_type}: Generated successfully")
        else:
            print(f"   ❌ {report_type}: {result['error']}")
    
    print(f"   📊 Success rate: {successful_reports}/{total_reports} reports generated successfully")
    
    return results

async def main():
    """Main function to run all reporting examples."""
    print("📋 Cybersecurity Reporting Toolkit Examples")
    print("=" * 60)
    print("📝 Comprehensive reporting capabilities demonstration")
    print("=" * 60)
    
    try:
        # Run individual reporting examples
        print("\n📝 Console Reporting Examples")
        print("-" * 30)
        console_results = await run_console_reporting_examples()
        
        print("\n🌐 HTML Reporting Examples")
        print("-" * 30)
        html_results = await run_html_reporting_examples()
        
        print("\n📊 JSON Reporting Examples")
        print("-" * 30)
        json_results = await run_json_reporting_examples()
        
        print("\n🔗 Report Aggregation Examples")
        print("-" * 30)
        aggregation_results = await run_report_aggregation_examples()
        
        print("\n🔄 Integrated Reporting Examples")
        print("-" * 30)
        integrated_results = await run_integrated_reporting_examples()
        
        print("\n" + "=" * 60)
        print("✅ All reporting examples completed successfully!")
        
        # Summary
        print("\n📊 Reporting Summary:")
        print(f"   Console reports: {len(console_results)} generated")
        print(f"   HTML reports: {len(html_results)} generated")
        print(f"   JSON reports: {len(json_results)} generated")
        print(f"   Aggregation reports: {len(aggregation_results)} generated")
        print(f"   Integrated reports: {len(integrated_results)} generated")
        
        # Performance summary
        total_reports = sum([
            len(console_results),
            len(html_results),
            len(json_results),
            len(aggregation_results),
            len(integrated_results)
        ])
        
        print(f"   Total reports generated: {total_reports}")
        
        # Sample output sizes
        if console_results:
            sample_console = list(console_results.values())[0]
            if hasattr(sample_console, 'report_length'):
                print(f"   Sample console report size: {sample_console.report_length} characters")
        
        if html_results:
            sample_html = list(html_results.values())[0]
            if hasattr(sample_html, 'report_size'):
                print(f"   Sample HTML report size: {sample_html.report_size} bytes")
        
        if json_results:
            sample_json = list(json_results.values())[0]
            if hasattr(sample_json, 'report_size'):
                print(f"   Sample JSON report size: {sample_json.report_size} bytes")
        
        print("\n📋 Report Types Available:")
        print("   • Console reports with colored output")
        print("   • HTML reports with interactive charts")
        print("   • JSON reports with structured data")
        print("   • Comprehensive report aggregation")
        print("   • Multiple output formats and templates")
        
        print("\n🎯 Use Cases:")
        print("   • Security assessment documentation")
        print("   • Executive presentations")
        print("   • Technical analysis reports")
        print("   • Compliance reporting")
        print("   • Integration with other security tools")
        
    except Exception as e:
        print(f"❌ Error running reporting examples: {e}")
        raise

match __name__:
    case "__main__":
    asyncio.run(main()) 