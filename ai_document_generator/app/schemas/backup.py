"""
Backup schemas for Pydantic validation
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator
import uuid


class BackupCreate(BaseModel):
    """Schema for backup creation request."""
    name: str = Field(..., min_length=1, max_length=200)
    backup_type: str = Field(..., regex="^(full|incremental|differential)$")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Backup name cannot be empty')
        return v.strip()
    
    @validator('backup_type')
    def validate_backup_type(cls, v):
        allowed_types = ['full', 'incremental', 'differential']
        if v not in allowed_types:
            raise ValueError(f'Invalid backup type. Allowed: {", ".join(allowed_types)}')
        return v


class BackupResponse(BaseModel):
    """Schema for backup response."""
    id: uuid.UUID
    name: str
    backup_type: str
    backup_path: str
    size: int
    checksum: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_by: uuid.UUID
    is_deleted: bool
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class BackupJobResponse(BaseModel):
    """Schema for backup job response."""
    id: uuid.UUID
    backup_id: uuid.UUID
    job_type: str
    status: str
    progress: int
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class BackupScheduleResponse(BaseModel):
    """Schema for backup schedule response."""
    id: uuid.UUID
    name: str
    backup_type: str
    schedule_cron: str
    is_active: bool
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    run_count: int
    success_count: int
    failure_count: int
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BackupRestoreRequest(BaseModel):
    """Schema for backup restore request."""
    restore_schema: bool = True
    restore_data: bool = True
    restore_files: bool = True
    restore_configuration: bool = False
    force_restore: bool = False
    
    @validator('force_restore')
    def validate_force_restore(cls, v, values):
        if v and not any([values.get('restore_schema'), values.get('restore_data'), values.get('restore_files')]):
            raise ValueError('At least one restore option must be selected when force_restore is True')
        return v


class BackupRestoreResponse(BaseModel):
    """Schema for backup restore response."""
    job_id: uuid.UUID
    status: str
    message: str = "Backup restore started"


class BackupScheduleCreate(BaseModel):
    """Schema for backup schedule creation request."""
    name: str = Field(..., min_length=1, max_length=200)
    backup_type: str = Field(..., regex="^(full|incremental|differential)$")
    schedule_cron: str = Field(..., min_length=1, max_length=100)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Schedule name cannot be empty')
        return v.strip()
    
    @validator('backup_type')
    def validate_backup_type(cls, v):
        allowed_types = ['full', 'incremental', 'differential']
        if v not in allowed_types:
            raise ValueError(f'Invalid backup type. Allowed: {", ".join(allowed_types)}')
        return v
    
    @validator('schedule_cron')
    def validate_schedule_cron(cls, v):
        # Basic cron validation (5 fields: minute hour day month weekday)
        parts = v.strip().split()
        if len(parts) != 5:
            raise ValueError('Cron expression must have exactly 5 fields')
        return v


class BackupScheduleUpdate(BaseModel):
    """Schema for backup schedule update request."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    backup_type: Optional[str] = Field(None, regex="^(full|incremental|differential)$")
    schedule_cron: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Schedule name cannot be empty')
        return v.strip() if v else v
    
    @validator('backup_type')
    def validate_backup_type(cls, v):
        if v is not None:
            allowed_types = ['full', 'incremental', 'differential']
            if v not in allowed_types:
                raise ValueError(f'Invalid backup type. Allowed: {", ".join(allowed_types)}')
        return v
    
    @validator('schedule_cron')
    def validate_schedule_cron(cls, v):
        if v is not None:
            # Basic cron validation (5 fields: minute hour day month weekday)
            parts = v.strip().split()
            if len(parts) != 5:
                raise ValueError('Cron expression must have exactly 5 fields')
        return v


class BackupSearch(BaseModel):
    """Schema for backup search request."""
    query: Optional[str] = None
    backup_type: Optional[str] = None
    status: Optional[str] = None
    created_by: Optional[uuid.UUID] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)


class BackupListResponse(BaseModel):
    """Schema for backup list response."""
    backups: List[BackupResponse]
    total: int
    page: int
    size: int
    pages: int


class BackupJobListResponse(BaseModel):
    """Schema for backup job list response."""
    jobs: List[BackupJobResponse]
    total: int
    page: int
    size: int
    pages: int


class BackupScheduleListResponse(BaseModel):
    """Schema for backup schedule list response."""
    schedules: List[BackupScheduleResponse]
    total: int
    page: int
    size: int
    pages: int


class BackupStatsResponse(BaseModel):
    """Schema for backup statistics response."""
    total_backups: int
    total_size: int
    backups_by_type: Dict[str, int]
    backups_by_status: Dict[str, int]
    recent_backups: List[BackupResponse]
    storage_usage: Dict[str, Any]


class BackupTestRequest(BaseModel):
    """Schema for backup test request."""
    backup_type: str = Field(..., regex="^(full|incremental|differential)$")
    test_mode: bool = True


class BackupTestResponse(BaseModel):
    """Schema for backup test response."""
    test_id: uuid.UUID
    status: str
    results: Dict[str, Any] = Field(default_factory=dict)
    message: str = "Backup test completed"


class BackupValidationRequest(BaseModel):
    """Schema for backup validation request."""
    validate_checksum: bool = True
    validate_integrity: bool = True
    validate_completeness: bool = True


class BackupValidationResponse(BaseModel):
    """Schema for backup validation response."""
    is_valid: bool
    checksum_valid: bool
    integrity_valid: bool
    completeness_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    message: str


class BackupExportRequest(BaseModel):
    """Schema for backup export request."""
    format: str = Field(..., regex="^(json|yaml|xml)$")
    include_metadata: bool = True
    include_jobs: bool = False


class BackupExportResponse(BaseModel):
    """Schema for backup export response."""
    export_id: uuid.UUID
    format: str
    download_url: str
    expires_at: datetime
    message: str = "Backup exported successfully"


class BackupImportRequest(BaseModel):
    """Schema for backup import request."""
    backup_data: Dict[str, Any]
    overwrite_existing: bool = False
    validate_import: bool = True


class BackupImportResponse(BaseModel):
    """Schema for backup import response."""
    import_id: uuid.UUID
    status: str
    imported_backups: List[uuid.UUID] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    message: str = "Backup import completed"




