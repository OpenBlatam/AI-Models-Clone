"""
File schemas for Pydantic validation
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator
import uuid


class FileUpload(BaseModel):
    """Schema for file upload request."""
    filename: str = Field(..., min_length=1, max_length=255)
    file_type: Optional[str] = Field(None, max_length=50)
    document_id: Optional[uuid.UUID] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    is_public: bool = False
    
    @validator('filename')
    def validate_filename(cls, v):
        if not v or not v.strip():
            raise ValueError('Filename cannot be empty')
        if '..' in v or '/' in v or '\\' in v:
            raise ValueError('Filename contains invalid characters')
        return v.strip()


class FileResponse(BaseModel):
    """Schema for file response."""
    id: uuid.UUID
    original_filename: str
    secure_filename: str
    file_size: int
    file_type: str
    mime_type: str
    file_hash: str
    document_id: Optional[uuid.UUID] = None
    uploaded_by: uuid.UUID
    metadata: Dict[str, Any] = Field(default_factory=dict)
    is_public: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FileVersionResponse(BaseModel):
    """Schema for file version response."""
    id: uuid.UUID
    file_id: uuid.UUID
    version_number: int
    file_path: str
    version_note: Optional[str] = None
    created_by: uuid.UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class FileShareResponse(BaseModel):
    """Schema for file share response."""
    id: uuid.UUID
    file_id: uuid.UUID
    shared_by: uuid.UUID
    shared_with: uuid.UUID
    permission: str
    expires_at: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FileMetadata(BaseModel):
    """Schema for detailed file metadata."""
    file_id: uuid.UUID
    original_filename: str
    file_size: int
    file_type: str
    mime_type: str
    file_hash: str
    created_at: datetime
    updated_at: datetime
    versions_count: int
    shares_count: int
    is_public: bool
    metadata: Dict[str, Any] = Field(default_factory=dict)
    file_stats: Optional[Dict[str, Any]] = None


class FileShareRequest(BaseModel):
    """Schema for file share request."""
    shared_with: uuid.UUID
    permission: str = Field(..., regex="^(read|write|admin)$")
    expires_at: Optional[datetime] = None
    
    @validator('permission')
    def validate_permission(cls, v):
        if v not in ['read', 'write', 'admin']:
            raise ValueError('Permission must be read, write, or admin')
        return v


class FileUpdate(BaseModel):
    """Schema for file update request."""
    metadata: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None


class FileSearch(BaseModel):
    """Schema for file search request."""
    query: Optional[str] = None
    file_type: Optional[str] = None
    document_id: Optional[uuid.UUID] = None
    uploaded_by: Optional[uuid.UUID] = None
    is_public: Optional[bool] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)


class FileListResponse(BaseModel):
    """Schema for file list response."""
    files: List[FileResponse]
    total: int
    page: int
    size: int
    pages: int


class FileVersionListResponse(BaseModel):
    """Schema for file version list response."""
    versions: List[FileVersionResponse]
    total: int
    page: int
    size: int
    pages: int


class FileShareListResponse(BaseModel):
    """Schema for file share list response."""
    shares: List[FileShareResponse]
    total: int
    page: int
    size: int
    pages: int


class FileDownloadResponse(BaseModel):
    """Schema for file download response."""
    file_id: uuid.UUID
    filename: str
    file_size: int
    mime_type: str
    download_url: str
    expires_at: datetime


class FileUploadResponse(BaseModel):
    """Schema for file upload response."""
    file: FileResponse
    upload_url: Optional[str] = None
    message: str = "File uploaded successfully"


class FileDeleteResponse(BaseModel):
    """Schema for file delete response."""
    message: str = "File deleted successfully"


class FileStatsResponse(BaseModel):
    """Schema for file statistics response."""
    total_files: int
    total_size: int
    files_by_type: Dict[str, int]
    files_by_user: Dict[str, int]
    recent_uploads: List[FileResponse]
    storage_usage: Dict[str, Any]




