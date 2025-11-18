"""
Configuration schemas for Pydantic validation
"""
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
import uuid


class ConfigCreate(BaseModel):
    """Schema for configuration creation request."""
    key: str = Field(..., min_length=1, max_length=200)
    value: Union[str, int, float, bool, dict, list] = Field(...)
    value_type: str = Field(..., regex="^(string|integer|float|boolean|json|yaml)$")
    environment: str = Field("default", min_length=1, max_length=50)
    description: Optional[str] = None
    is_sensitive: bool = False
    
    @validator('key')
    def validate_key(cls, v):
        if not v or not v.strip():
            raise ValueError('Config key cannot be empty')
        # Check for valid key format (alphanumeric, underscore, dot)
        import re
        if not re.match(r'^[a-zA-Z0-9_.-]+$', v):
            raise ValueError('Config key can only contain alphanumeric characters, underscores, dots, and hyphens')
        return v.strip()
    
    @validator('value_type')
    def validate_value_type(cls, v, values):
        if 'value' in values:
            value = values['value']
            if v == "boolean" and not isinstance(value, bool):
                raise ValueError('Value must be boolean for boolean type')
            elif v == "integer" and not isinstance(value, int):
                raise ValueError('Value must be integer for integer type')
            elif v == "float" and not isinstance(value, (int, float)):
                raise ValueError('Value must be float for float type')
            elif v == "json" and not isinstance(value, (dict, list)):
                raise ValueError('Value must be dict or list for json type')
        return v


class ConfigUpdate(BaseModel):
    """Schema for configuration update request."""
    value: Optional[Union[str, int, float, bool, dict, list]] = None
    value_type: Optional[str] = Field(None, regex="^(string|integer|float|boolean|json|yaml)$")
    description: Optional[str] = None
    is_sensitive: Optional[bool] = None
    
    @validator('value_type')
    def validate_value_type(cls, v, values):
        if v and 'value' in values and values['value'] is not None:
            value = values['value']
            if v == "boolean" and not isinstance(value, bool):
                raise ValueError('Value must be boolean for boolean type')
            elif v == "integer" and not isinstance(value, int):
                raise ValueError('Value must be integer for integer type')
            elif v == "float" and not isinstance(value, (int, float)):
                raise ValueError('Value must be float for float type')
            elif v == "json" and not isinstance(value, (dict, list)):
                raise ValueError('Value must be dict or list for json type')
        return v


class ConfigResponse(BaseModel):
    """Schema for configuration response."""
    id: uuid.UUID
    key: str
    value: str  # Always returned as string for security
    value_type: str
    environment: str
    description: Optional[str] = None
    is_sensitive: bool
    is_active: bool
    created_by: Optional[uuid.UUID] = None
    updated_by: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ConfigVersionResponse(BaseModel):
    """Schema for configuration version response."""
    id: uuid.UUID
    config_id: uuid.UUID
    value: str
    value_type: str
    created_by: Optional[uuid.UUID] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConfigEnvironmentResponse(BaseModel):
    """Schema for configuration environment response."""
    name: str
    config_count: int
    last_updated: Optional[datetime] = None


class ConfigSearchRequest(BaseModel):
    """Schema for configuration search request."""
    environment: Optional[str] = None
    search: Optional[str] = None
    value_type: Optional[str] = None
    is_sensitive: Optional[bool] = None
    page: int = Field(1, ge=1)
    size: int = Field(50, ge=1, le=100)


class ConfigValidationResponse(BaseModel):
    """Schema for configuration validation response."""
    is_valid: bool
    valid_count: int
    invalid_count: int
    warning_count: int
    results: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)
    environment: str


class ConfigExportRequest(BaseModel):
    """Schema for configuration export request."""
    environment: str = "default"
    format: str = Field(..., regex="^(json|yaml)$")
    include_sensitive: bool = False


class ConfigExportResponse(BaseModel):
    """Schema for configuration export response."""
    export_filename: str
    export_path: str
    total_configs: int
    format: str
    download_url: str
    expires_at: datetime


class ConfigImportRequest(BaseModel):
    """Schema for configuration import request."""
    config_data: Dict[str, Any] = Field(..., min_items=1)
    environment: str = "default"
    overwrite: bool = False


class ConfigImportResponse(BaseModel):
    """Schema for configuration import response."""
    imported_count: int
    skipped_count: int
    errors: List[str] = Field(default_factory=list)
    total_processed: int


class ConfigBulkUpdateRequest(BaseModel):
    """Schema for bulk configuration update request."""
    configs: List[Dict[str, Any]] = Field(..., min_items=1)
    environment: str = "default"
    overwrite: bool = False


class ConfigBulkUpdateResponse(BaseModel):
    """Schema for bulk configuration update response."""
    updated_count: int
    created_count: int
    failed_count: int
    errors: List[str] = Field(default_factory=list)
    total_processed: int


class ConfigStatsResponse(BaseModel):
    """Schema for configuration statistics response."""
    total_configs: int
    type_stats: Dict[str, int] = Field(default_factory=dict)
    environment_stats: Dict[str, int] = Field(default_factory=dict)
    sensitive_count: int
    cache_size: int


class ConfigListResponse(BaseModel):
    """Schema for configuration list response."""
    configs: List[ConfigResponse]
    total: int
    page: int
    size: int
    pages: int


class ConfigHistoryResponse(BaseModel):
    """Schema for configuration history response."""
    config_key: str
    environment: str
    versions: List[ConfigVersionResponse]
    total: int


class ConfigEnvironmentCreate(BaseModel):
    """Schema for configuration environment creation request."""
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Environment name cannot be empty')
        # Check for valid name format (alphanumeric, underscore, hyphen)
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Environment name can only contain alphanumeric characters, underscores, and hyphens')
        return v.strip()


class ConfigEnvironmentUpdate(BaseModel):
    """Schema for configuration environment update request."""
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ConfigEnvironmentListResponse(BaseModel):
    """Schema for configuration environment list response."""
    environments: List[ConfigEnvironmentResponse]
    total: int


class ConfigCacheRequest(BaseModel):
    """Schema for configuration cache request."""
    environment: Optional[str] = None
    action: str = Field(..., regex="^(reload|clear|stats)$")


class ConfigCacheResponse(BaseModel):
    """Schema for configuration cache response."""
    message: str
    cache_size: Optional[int] = None
    environment: Optional[str] = None


class ConfigTemplateRequest(BaseModel):
    """Schema for configuration template request."""
    template_name: str = Field(..., min_length=1, max_length=100)
    environment: str = "default"
    variables: Dict[str, Any] = Field(default_factory=dict)


class ConfigTemplateResponse(BaseModel):
    """Schema for configuration template response."""
    template_name: str
    environment: str
    applied_configs: List[str] = Field(default_factory=list)
    skipped_configs: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)


class ConfigBackupRequest(BaseModel):
    """Schema for configuration backup request."""
    environment: str = "default"
    include_sensitive: bool = False
    backup_name: Optional[str] = None


class ConfigBackupResponse(BaseModel):
    """Schema for configuration backup response."""
    backup_id: uuid.UUID
    backup_name: str
    environment: str
    config_count: int
    created_at: datetime


class ConfigRestoreRequest(BaseModel):
    """Schema for configuration restore request."""
    backup_id: uuid.UUID
    environment: str = "default"
    overwrite: bool = False


class ConfigRestoreResponse(BaseModel):
    """Schema for configuration restore response."""
    restore_id: uuid.UUID
    backup_id: uuid.UUID
    environment: str
    restored_count: int
    skipped_count: int
    errors: List[str] = Field(default_factory=list)
    created_at: datetime




