from typing import Dict, Any
from pydantic import BaseModel, Field
import json

__all__ = ["JSONReportConfig", "generate_json_report"]

class JSONReportConfig(BaseModel):
    report: Dict[str, Any] = Field(..., description="Report data to convert to JSON")

def generate_json_report(*, config: JSONReportConfig) -> Dict[str, Any]:
    """Generates JSON report from data (RORO, Pydantic, type hints)."""
    json_str = json.dumps(config.report, indent=2)
    return {"json": json_str} 