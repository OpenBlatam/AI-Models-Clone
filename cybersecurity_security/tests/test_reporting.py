"""
Tests for Reporting Module

Tests console, HTML, JSON, and report aggregation functionality.
"""

import pytest
import asyncio
import json
from unittest.mock import patch, MagicMock
from cybersecurity_security.reporting import (
    # Console Reporter
    ConsoleReportRequest, ConsoleReportResult, ConsoleReportLevel,
    generate_console_report_async, print_security_summary,
    print_vulnerability_details, print_scan_results,
    print_enumeration_results, print_attack_results,
    
    # HTML Reporter
    HTMLReportRequest, HTMLReportResult, HTMLReportTemplate,
    generate_html_report_async, create_vulnerability_table,
    create_scan_summary, create_executive_summary,
    create_technical_details, create_recommendations_section,
    
    # JSON Reporter
    JSONReportRequest, JSONReportResult, JSONReportFormat,
    generate_json_report_async, export_scan_data,
    export_vulnerability_data, export_enumeration_data,
    export_attack_data, create_structured_report,
    
    # Report Aggregator
    ReportAggregatorRequest, ReportAggregatorResult, ReportType,
    aggregate_reports_async, combine_scan_results,
    merge_vulnerability_data, create_comprehensive_report,
    generate_executive_summary
)

class TestConsoleReporter:
    """Test suite for console reporter."""
    
    def test_console_report_request_creation(self):
        """Test ConsoleReportRequest creation."""
        request = ConsoleReportRequest(
            scan_results={"scans": []},
            vulnerability_data=[],
            report_level=ConsoleReportLevel.INFO,
            include_details=True,
            color_output=True
        )
        assert request.report_level == ConsoleReportLevel.INFO
        assert request.include_details is True
        assert request.color_output is True
    
    @pytest.mark.asyncio
    async def test_generate_console_report_async(self):
        """Test console report generation."""
        request = ConsoleReportRequest(
            scan_results={
                "scans": [
                    {"type": "port_scan", "target": "localhost", "success": True, "duration": 5.0}
                ]
            },
            vulnerability_data=[
                {"title": "SQL Injection", "severity": "high", "description": "Test vuln"}
            ],
            report_level=ConsoleReportLevel.INFO,
            include_details=True,
            color_output=False
        )
        
        result = await generate_console_report_async(request)
        
        assert result.report_generated is True
        assert len(result.report_content) > 0
        assert "SECURITY ASSESSMENT REPORT" in result.report_content
        assert "scan_results" in result.sections_processed
    
    @pytest.mark.asyncio
    async def test_print_security_summary(self):
        """Test security summary printing."""
        scan_results = {
            "scans": [
                {"type": "port_scan", "success": True},
                {"type": "vuln_scan", "success": False}
            ]
        }
        
        vulnerability_data = [
            {"severity": "critical"},
            {"severity": "high"},
            {"severity": "medium"}
        ]
        
        summary = await print_security_summary(
            scan_results, vulnerability_data, {}, {},
            color_output=False
        )
        
        assert "SECURITY SUMMARY" in summary
        assert "1/2 successful" in summary  # 1 successful scan out of 2
    
    @pytest.mark.asyncio
    async def test_print_vulnerability_details(self):
        """Test vulnerability details printing."""
        vulnerability_data = [
            {
                "title": "SQL Injection",
                "severity": "high",
                "description": "SQL injection vulnerability",
                "cvss_score": 8.5,
                "affected_component": "login.php",
                "recommendation": "Use prepared statements"
            }
        ]
        
        vuln_details = await print_vulnerability_details(
            vulnerability_data, color_output=False, include_details=True
        )
        
        assert "VULNERABILITY DETAILS" in vuln_details
        assert "SQL Injection" in vuln_details
        assert "HIGH" in vuln_details
    
    @pytest.mark.asyncio
    async def test_print_scan_results(self):
        """Test scan results printing."""
        scan_results = {
            "scans": [
                {
                    "type": "port_scan",
                    "target": "192.168.1.1",
                    "success": True,
                    "duration": 10.0,
                    "findings": ["port 80 open", "port 443 open"],
                    "ports": [80, 443]
                }
            ]
        }
        
        scan_output = await print_scan_results(
            scan_results, color_output=False, include_details=True
        )
        
        assert "SCAN RESULTS" in scan_output
        assert "port_scan" in scan_output
        assert "192.168.1.1" in scan_output

class TestHTMLReporter:
    """Test suite for HTML reporter."""
    
    def test_html_report_request_creation(self):
        """Test HTMLReportRequest creation."""
        request = HTMLReportRequest(
            scan_results={"scans": []},
            vulnerability_data=[],
            template=HTMLReportTemplate.MODERN,
            include_charts=True,
            include_timeline=True
        )
        assert request.template == HTMLReportTemplate.MODERN
        assert request.include_charts is True
        assert request.include_timeline is True
    
    @pytest.mark.asyncio
    async def test_generate_html_report_async(self):
        """Test HTML report generation."""
        request = HTMLReportRequest(
            scan_results={
                "scans": [
                    {"type": "port_scan", "target": "localhost", "success": True}
                ]
            },
            vulnerability_data=[
                {"title": "XSS", "severity": "medium", "description": "XSS vulnerability"}
            ],
            template=HTMLReportTemplate.MODERN,
            include_charts=True
        )
        
        result = await generate_html_report_async(request)
        
        assert result.report_generated is True
        assert len(result.html_content) > 0
        assert "<!DOCTYPE html>" in result.html_content
        assert "Security Assessment Report" in result.html_content
        assert "executive_summary" in result.sections_included
    
    @pytest.mark.asyncio
    async def test_create_executive_summary(self):
        """Test executive summary creation."""
        scan_results = {
            "scans": [
                {"type": "port_scan", "success": True},
                {"type": "vuln_scan", "success": True}
            ]
        }
        
        vulnerability_data = [
            {"severity": "critical"},
            {"severity": "high"}
        ]
        
        summary = await create_executive_summary(
            scan_results, vulnerability_data, {}, {}
        )
        
        assert "Executive Summary" in summary
        assert "2/2" in summary  # 2 successful scans
        assert "2" in summary  # 2 vulnerabilities
    
    @pytest.mark.asyncio
    async def test_create_vulnerability_table(self):
        """Test vulnerability table creation."""
        vulnerability_data = [
            {
                "title": "SQL Injection",
                "severity": "high",
                "description": "SQL injection vulnerability",
                "cvss_score": 8.5,
                "affected_component": "login.php",
                "recommendation": "Use prepared statements"
            }
        ]
        
        table = await create_vulnerability_table(vulnerability_data)
        
        assert "Vulnerability Details" in table
        assert "SQL Injection" in table
        assert "high" in table.lower()
    
    @pytest.mark.asyncio
    async def test_create_scan_summary(self):
        """Test scan summary creation."""
        scan_results = {
            "scans": [
                {
                    "type": "port_scan",
                    "target": "192.168.1.1",
                    "success": True,
                    "duration": 10.0,
                    "findings": ["port 80 open"]
                }
            ]
        }
        
        summary = await create_scan_summary(scan_results, include_charts=True)
        
        assert "Scan Results" in summary
        assert "port_scan" in summary
        assert "192.168.1.1" in summary

class TestJSONReporter:
    """Test suite for JSON reporter."""
    
    def test_json_report_request_creation(self):
        """Test JSONReportRequest creation."""
        request = JSONReportRequest(
            scan_results={"scans": []},
            vulnerability_data=[],
            format=JSONReportFormat.DETAILED,
            include_metadata=True,
            include_statistics=True
        )
        assert request.format == JSONReportFormat.DETAILED
        assert request.include_metadata is True
        assert request.include_statistics is True
    
    @pytest.mark.asyncio
    async def test_generate_json_report_async(self):
        """Test JSON report generation."""
        request = JSONReportRequest(
            scan_results={
                "scans": [
                    {"type": "port_scan", "target": "localhost", "success": True}
                ]
            },
            vulnerability_data=[
                {"title": "XSS", "severity": "medium", "description": "XSS vulnerability"}
            ],
            format=JSONReportFormat.DETAILED,
            include_metadata=True
        )
        
        result = await generate_json_report_async(request)
        
        assert result.report_generated is True
        assert len(result.json_content) > 0
        
        # Parse JSON to verify structure
        report_data = json.loads(result.json_content)
        assert "report_metadata" in report_data
        assert "summary" in report_data
        assert "scan_results" in report_data
    
    @pytest.mark.asyncio
    async def test_export_scan_data(self):
        """Test scan data export."""
        scan_results = {
            "scans": [
                {
                    "type": "port_scan",
                    "target": "192.168.1.1",
                    "success": True,
                    "duration": 10.0,
                    "findings": ["port 80 open"]
                }
            ]
        }
        
        # Test detailed format
        detailed_data = await export_scan_data(scan_results, JSONReportFormat.DETAILED)
        assert "scans" in detailed_data
        assert "scan_metadata" in detailed_data
        assert detailed_data["scan_metadata"]["total_scans"] == 1
        
        # Test compact format
        compact_data = await export_scan_data(scan_results, JSONReportFormat.COMPACT)
        assert "scans" in compact_data
        assert "total_scans" in compact_data
        assert compact_data["total_scans"] == 1
        
        # Test minimal format
        minimal_data = await export_scan_data(scan_results, JSONReportFormat.MINIMAL)
        assert "total_scans" in minimal_data
        assert "successful_scans" in minimal_data
        assert minimal_data["total_scans"] == 1
    
    @pytest.mark.asyncio
    async def test_export_vulnerability_data(self):
        """Test vulnerability data export."""
        vulnerability_data = [
            {
                "title": "SQL Injection",
                "severity": "high",
                "cvss_score": 8.5,
                "affected_component": "login.php",
                "description": "SQL injection vulnerability"
            },
            {
                "title": "XSS",
                "severity": "medium",
                "cvss_score": 6.0,
                "affected_component": "search.php",
                "description": "XSS vulnerability"
            }
        ]
        
        # Test detailed format
        detailed_data = await export_vulnerability_data(vulnerability_data, JSONReportFormat.DETAILED)
        assert "vulnerabilities" in detailed_data
        assert "vulnerability_metadata" in detailed_data
        assert detailed_data["vulnerability_metadata"]["total_vulnerabilities"] == 2
        
        # Test compact format
        compact_data = await export_vulnerability_data(vulnerability_data, JSONReportFormat.COMPACT)
        assert "vulnerabilities" in compact_data
        assert "total_count" in compact_data
        assert compact_data["total_count"] == 2
        
        # Test minimal format
        minimal_data = await export_vulnerability_data(vulnerability_data, JSONReportFormat.MINIMAL)
        assert "total_vulnerabilities" in minimal_data
        assert "severity_distribution" in minimal_data
        assert minimal_data["total_vulnerabilities"] == 2
    
    @pytest.mark.asyncio
    async def test_create_structured_report(self):
        """Test structured report creation."""
        scan_results = {
            "scans": [
                {"type": "port_scan", "target": "localhost", "success": True}
            ]
        }
        
        vulnerability_data = [
            {"title": "XSS", "severity": "medium", "description": "XSS vulnerability"}
        ]
        
        report = await create_structured_report(
            scan_results, vulnerability_data, {}, {},
            format=JSONReportFormat.DETAILED
        )
        
        assert "report_header" in report
        assert "executive_summary" in report
        assert "detailed_findings" in report
        assert "statistics" in report
        assert "recommendations" in report

class TestReportAggregator:
    """Test suite for report aggregator."""
    
    def test_report_aggregator_request_creation(self):
        """Test ReportAggregatorRequest creation."""
        request = ReportAggregatorRequest(
            console_report={"content": "test"},
            html_report={"content": "test"},
            json_report={"content": "test"},
            output_format=ReportType.COMPREHENSIVE,
            include_raw_data=True,
            generate_timeline=True
        )
        assert request.output_format == ReportType.COMPREHENSIVE
        assert request.include_raw_data is True
        assert request.generate_timeline is True
    
    @pytest.mark.asyncio
    async def test_aggregate_reports_async(self):
        """Test report aggregation."""
        request = ReportAggregatorRequest(
            scan_results={
                "scans": [
                    {"type": "port_scan", "target": "localhost", "success": True}
                ]
            },
            vulnerability_data=[
                {"title": "XSS", "severity": "medium", "description": "XSS vulnerability"}
            ],
            output_format=ReportType.COMPREHENSIVE,
            include_raw_data=True
        )
        
        result = await aggregate_reports_async(request)
        
        assert result.aggregation_successful is True
        assert len(result.aggregated_report) > 0
        assert "metadata" in result.aggregated_report
        assert "executive_summary" in result.aggregated_report
        assert "scan_results" in result.reports_combined
        assert "vulnerability_data" in result.reports_combined
    
    @pytest.mark.asyncio
    async def test_combine_scan_results(self):
        """Test scan results combination."""
        scan_results = {
            "scans": [
                {
                    "type": "port_scan",
                    "target": "192.168.1.1",
                    "success": True,
                    "duration": 10.0,
                    "findings": ["port 80 open"]
                },
                {
                    "type": "vuln_scan",
                    "target": "192.168.1.1",
                    "success": False,
                    "duration": 15.0,
                    "findings": []
                }
            ]
        }
        
        combined = await combine_scan_results(scan_results)
        
        assert combined["total_scans"] == 2
        assert combined["successful_scans"] == 1
        assert combined["failed_scans"] == 1
        assert "port_scan" in combined["scan_types"]
        assert "vuln_scan" in combined["scan_types"]
    
    @pytest.mark.asyncio
    async def test_merge_vulnerability_data(self):
        """Test vulnerability data merging."""
        vulnerability_data = [
            {
                "title": "SQL Injection",
                "severity": "high",
                "cvss_score": 8.5,
                "affected_component": "login.php"
            },
            {
                "title": "XSS",
                "severity": "medium",
                "cvss_score": 6.0,
                "affected_component": "search.php"
            },
            {
                "title": "CSRF",
                "severity": "low",
                "cvss_score": 3.0,
                "affected_component": "profile.php"
            }
        ]
        
        merged = await merge_vulnerability_data(vulnerability_data)
        
        assert merged["total_vulnerabilities"] == 3
        assert merged["severity_distribution"]["high"] == 1
        assert merged["severity_distribution"]["medium"] == 1
        assert merged["severity_distribution"]["low"] == 1
        assert "login.php" in merged["affected_components"]
        assert merged["risk_assessment"]["overall_risk_level"] == "MEDIUM"
    
    @pytest.mark.asyncio
    async def test_generate_executive_summary(self):
        """Test executive summary generation."""
        scan_results = {
            "scans": [
                {"type": "port_scan", "success": True},
                {"type": "vuln_scan", "success": True}
            ]
        }
        
        vulnerability_data = [
            {"severity": "critical"},
            {"severity": "high"}
        ]
        
        summary = await generate_executive_summary(
            scan_results, vulnerability_data, {}, {}
        )
        
        assert "assessment_overview" in summary
        assert "performance_summary" in summary
        assert "security_posture" in summary
        assert summary["assessment_overview"]["total_operations"] == 4
        assert summary["assessment_overview"]["overall_risk_level"] == "CRITICAL"
    
    @pytest.mark.asyncio
    async def test_create_comprehensive_report(self):
        """Test comprehensive report creation."""
        vulnerability_data = [
            {"title": "SQL Injection", "severity": "high", "type": "injection"},
            {"title": "XSS", "severity": "medium", "type": "xss"}
        ]
        
        attack_data = {
            "ssh_brute_force": {
                "successful_attempts": 1,
                "total_attempts": 10,
                "successful_credentials": [{"username": "admin", "password": "password"}]
            }
        }
        
        report = await create_comprehensive_report(
            {}, vulnerability_data, {}, attack_data
        )
        
        assert "detailed_analysis" in report
        assert "trends_and_patterns" in report
        assert "action_items" in report
        assert len(report["action_items"]) > 0

class TestReportingIntegration:
    """Integration tests for reporting modules."""
    
    @pytest.mark.asyncio
    async def test_multiple_report_formats(self):
        """Test generating multiple report formats."""
        # Sample data
        scan_results = {
            "scans": [
                {"type": "port_scan", "target": "localhost", "success": True, "duration": 5.0}
            ]
        }
        
        vulnerability_data = [
            {"title": "XSS", "severity": "medium", "description": "XSS vulnerability"}
        ]
        
        # Generate console report
        console_request = ConsoleReportRequest(
            scan_results=scan_results,
            vulnerability_data=vulnerability_data,
            color_output=False
        )
        console_result = await generate_console_report_async(console_request)
        
        # Generate HTML report
        html_request = HTMLReportRequest(
            scan_results=scan_results,
            vulnerability_data=vulnerability_data
        )
        html_result = await generate_html_report_async(html_request)
        
        # Generate JSON report
        json_request = JSONReportRequest(
            scan_results=scan_results,
            vulnerability_data=vulnerability_data
        )
        json_result = await generate_json_report_async(json_request)
        
        # Verify all reports were generated
        assert console_result.report_generated is True
        assert html_result.report_generated is True
        assert json_result.report_generated is True
        
        # Verify content
        assert "SECURITY ASSESSMENT REPORT" in console_result.report_content
        assert "<!DOCTYPE html>" in html_result.html_content
        assert "report_metadata" in json.loads(json_result.json_content)
    
    @pytest.mark.asyncio
    async def test_report_aggregation_workflow(self):
        """Test complete report aggregation workflow."""
        # Sample data
        scan_results = {
            "scans": [
                {"type": "port_scan", "target": "localhost", "success": True, "duration": 5.0}
            ]
        }
        
        vulnerability_data = [
            {"title": "XSS", "severity": "medium", "description": "XSS vulnerability"}
        ]
        
        # Aggregate reports
        request = ReportAggregatorRequest(
            scan_results=scan_results,
            vulnerability_data=vulnerability_data,
            output_format=ReportType.COMPREHENSIVE,
            include_raw_data=True
        )
        
        result = await aggregate_reports_async(request)
        
        # Verify aggregation
        assert result.aggregation_successful is True
        assert "executive_summary" in result.aggregated_report
        assert "detailed_findings" in result.aggregated_report
        assert "raw_data" in result.aggregated_report
        
        # Verify data sections
        assert "scan_results" in result.reports_combined
        assert "vulnerability_data" in result.reports_combined 