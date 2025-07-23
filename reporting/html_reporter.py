from typing import Dict, Any
from pydantic import BaseModel, Field

__all__ = ["HTMLReportConfig", "generate_html_report"]

class HTMLReportConfig(BaseModel):
    report: Dict[str, Any] = Field(..., description="Report data to convert to HTML")

def generate_html_report(*, config: HTMLReportConfig) -> Dict[str, Any]:
    """Generates HTML report from data (RORO, Pydantic, type hints)."""
    html = "<html><body><h1>Report</h1><ul>"
    for key, value in config.report.items():
        html += f"<li><b>{key}</b>: {value}</li>"
    html += "</ul></body></html>"
    return {"html": html} 