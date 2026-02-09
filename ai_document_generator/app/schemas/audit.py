"""
Audit schemas for Pydantic validation
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator
import uuid


class AuditLogResponse(BaseModel):
    """Schema for audit log response."""
    id: uuid.UUID
    event_type: str
    user_id: uuid.UUID
    resource_type: str
    resource_id: str
    action: str
    details: Dict[str, Any] = Field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True


class AuditEventResponse(BaseModel):
    """Schema for audit event response."""
    id: uuid.UUID
    event_type: str
    user_id: Optional[uuid.UUID] = None
    event_data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime
    
    class Config:
        from_attributes = True


class AuditTrailResponse(BaseModel):
    """Schema for audit trail response."""
    id: uuid.UUID
    resource_type: str
    resource_id: str
    action: str
    old_values: Dict[str, Any] = Field(default_factory=dict)
    new_values: Dict[str, Any] = Field(default_factory=dict)
    changed_fields: List[str] = Field(default_factory=list)
    user_id: uuid.UUID
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True


class AuditSearchRequest(BaseModel):
    """Schema for audit search request."""
    query: Optional[str] = None
    event_type: Optional[str] = None
    user_id: Optional[uuid.UUID] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    action: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    ip_address: Optional[str] = None
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)
    
    @validator('date_from', 'date_to')
    def validate_dates(cls, v, values):
        if v and values.get('date_from') and values.get('date_to'):
            if values['date_from'] > values['date_to']:
                raise ValueError('date_from must be before date_to')
        return v


class AuditStatsResponse(BaseModel):
    """Schema for audit statistics response."""
    total_logs: int
    event_type_stats: Dict[str, int] = Field(default_factory=dict)
    action_stats: Dict[str, int] = Field(default_factory=dict)
    resource_type_stats: Dict[str, int] = Field(default_factory=dict)
    user_stats: Dict[str, int] = Field(default_factory=dict)
    date_stats: Dict[str, int] = Field(default_factory=dict)
    recent_logs: List[AuditLogResponse] = Field(default_factory=list)
    period_start: datetime
    period_end: datetime


class AuditExportRequest(BaseModel):
    """Schema for audit export request."""
    format: str = Field(..., regex="^(json|csv|xml)$")
    search_params: AuditSearchRequest
    include_details: bool = True
    include_metadata: bool = True


class AuditExportResponse(BaseModel):
    """Schema for audit export response."""
    export_filename: str
    export_path: str
    total_records: int
    format: str
    download_url: str
    expires_at: datetime


class AuditReportRequest(BaseModel):
    """Schema for audit report request."""
    report_type: str = Field(..., regex="^(summary|detailed|security|compliance)$")
    date_from: datetime
    date_to: datetime
    include_charts: bool = True
    include_recommendations: bool = True


class AuditReportResponse(BaseModel):
    """Schema for audit report response."""
    report_id: uuid.UUID
    report_type: str
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    summary: Dict[str, Any] = Field(default_factory=dict)
    charts: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)
    download_url: str
    expires_at: datetime


class AuditAlertRequest(BaseModel):
    """Schema for audit alert request."""
    alert_type: str = Field(..., regex="^(security|compliance|anomaly|threshold)$")
    conditions: Dict[str, Any] = Field(..., min_items=1)
    severity: str = Field(..., regex="^(low|medium|high|critical)$")
    is_active: bool = True
    notification_methods: List[str] = Field(default_factory=list)


class AuditAlertResponse(BaseModel):
    """Schema for audit alert response."""
    id: uuid.UUID
    alert_type: str
    conditions: Dict[str, Any] = Field(default_factory=dict)
    severity: str
    is_active: bool
    notification_methods: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class AuditComplianceRequest(BaseModel):
    """Schema for audit compliance request."""
    compliance_standard: str = Field(..., regex="^(GDPR|HIPAA|SOX|PCI-DSS|ISO27001)$")
    date_from: datetime
    date_to: datetime
    include_recommendations: bool = True


class AuditComplianceResponse(BaseModel):
    """Schema for audit compliance response."""
    compliance_standard: str
    compliance_score: float = Field(..., ge=0, le=100)
    compliance_status: str = Field(..., regex="^(compliant|non-compliant|partial)$")
    violations: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    report_url: str
    generated_at: datetime


class AuditDashboardResponse(BaseModel):
    """Schema for audit dashboard response."""
    total_events: int
    events_today: int
    events_this_week: int
    events_this_month: int
    top_actions: List[Dict[str, Any]] = Field(default_factory=list)
    top_users: List[Dict[str, Any]] = Field(default_factory=list)
    top_resources: List[Dict[str, Any]] = Field(default_factory=list)
    security_events: int
    compliance_score: float
    recent_events: List[AuditLogResponse] = Field(default_factory=list)
    alerts: List[Dict[str, Any]] = Field(default_factory=list)


class AuditLogCreate(BaseModel):
    """Schema for creating audit log entry."""
    event_type: str = Field(..., min_length=1, max_length=50)
    resource_type: str = Field(..., min_length=1, max_length=50)
    resource_id: str = Field(..., min_length=1, max_length=100)
    action: str = Field(..., min_length=1, max_length=100)
    details: Dict[str, Any] = Field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AuditEventCreate(BaseModel):
    """Schema for creating audit event."""
    event_type: str = Field(..., min_length=1, max_length=50)
    event_data: Dict[str, Any] = Field(default_factory=dict)


class AuditTrailCreate(BaseModel):
    """Schema for creating audit trail entry."""
    resource_type: str = Field(..., min_length=1, max_length=50)
    resource_id: str = Field(..., min_length=1, max_length=100)
    action: str = Field(..., min_length=1, max_length=100)
    old_values: Dict[str, Any] = Field(default_factory=dict)
    new_values: Dict[str, Any] = Field(default_factory=dict)
    changed_fields: List[str] = Field(default_factory=list)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AuditLogListResponse(BaseModel):
    """Schema for audit log list response."""
    audit_logs: List[AuditLogResponse]
    total: int
    page: int
    size: int
    pages: int


class AuditEventListResponse(BaseModel):
    """Schema for audit event list response."""
    audit_events: List[AuditEventResponse]
    total: int
    page: int
    size: int
    pages: int


class AuditTrailListResponse(BaseModel):
    """Schema for audit trail list response."""
    audit_trail: List[AuditTrailResponse]
    total: int
    page: int
    size: int
    pages: int




