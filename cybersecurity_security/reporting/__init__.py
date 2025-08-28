from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from .console_reporter import (
from .html_reporter import (
from .json_reporter import (
from .report_aggregator import (
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
Security Reporting Module

Provides comprehensive reporting capabilities for security assessment results.
Supports console, HTML, and JSON output formats.
"""

    ConsoleReportRequest,
    ConsoleReportResult,
    ConsoleReportLevel,
    generate_console_report_async,
    print_security_summary,
    print_vulnerability_details,
    print_scan_results,
    print_enumeration_results,
    print_attack_results
)

    HTMLReportRequest,
    HTMLReportResult,
    HTMLReportTemplate,
    generate_html_report_async,
    create_vulnerability_table,
    create_scan_summary,
    create_executive_summary,
    create_technical_details,
    create_recommendations_section
)

    JSONReportRequest,
    JSONReportResult,
    JSONReportFormat,
    generate_json_report_async,
    export_scan_data,
    export_vulnerability_data,
    export_enumeration_data,
    export_attack_data,
    create_structured_report
)

    ReportAggregatorRequest,
    ReportAggregatorResult,
    ReportType,
    aggregate_reports_async,
    combine_scan_results,
    merge_vulnerability_data,
    create_comprehensive_report,
    generate_executive_summary
)

__all__ = [
    # Console Reporter
    "ConsoleReportRequest",
    "ConsoleReportResult",
    "ConsoleReportLevel",
    "generate_console_report_async",
    "print_security_summary",
    "print_vulnerability_details",
    "print_scan_results",
    "print_enumeration_results",
    "print_attack_results",
    
    # HTML Reporter
    "HTMLReportRequest",
    "HTMLReportResult",
    "HTMLReportTemplate",
    "generate_html_report_async",
    "create_vulnerability_table",
    "create_scan_summary",
    "create_executive_summary",
    "create_technical_details",
    "create_recommendations_section",
    
    # JSON Reporter
    "JSONReportRequest",
    "JSONReportResult",
    "JSONReportFormat",
    "generate_json_report_async",
    "export_scan_data",
    "export_vulnerability_data",
    "export_enumeration_data",
    "export_attack_data",
    "create_structured_report",
    
    # Report Aggregator
    "ReportAggregatorRequest",
    "ReportAggregatorResult",
    "ReportType",
    "aggregate_reports_async",
    "combine_scan_results",
    "merge_vulnerability_data",
    "create_comprehensive_report",
    "generate_executive_summary"
] 