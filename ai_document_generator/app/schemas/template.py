"""
Template schemas for Pydantic validation
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator
import uuid


class TemplateVariable(BaseModel):
    """Schema for template variable definition."""
    name: str = Field(..., min_length=1, max_length=50)
    type: str = Field(..., regex="^(text|number|date|boolean|select|multiselect)$")
    label: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    required: bool = False
    default_value: Optional[Any] = None
    options: Optional[List[str]] = None  # For select/multiselect types
    validation: Optional[Dict[str, Any]] = None  # Custom validation rules


class TemplateCreate(BaseModel):
    """Schema for template creation request."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    content: str = Field(..., min_length=1)
    template_type: str = Field(..., min_length=1, max_length=50)
    category_id: Optional[uuid.UUID] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    variables: Optional[List[TemplateVariable]] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    is_public: bool = False
    is_featured: bool = False
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Template name cannot be empty')
        return v.strip()
    
    @validator('content')
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError('Template content cannot be empty')
        return v.strip()
    
    @validator('tags')
    def validate_tags(cls, v):
        if v:
            # Remove duplicates and empty tags
            v = list(set(tag.strip() for tag in v if tag.strip()))
            if len(v) > 10:
                raise ValueError('Maximum 10 tags allowed')
        return v or []


class TemplateUpdate(BaseModel):
    """Schema for template update request."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    content: Optional[str] = Field(None, min_length=1)
    template_type: Optional[str] = Field(None, min_length=1, max_length=50)
    category_id: Optional[uuid.UUID] = None
    tags: Optional[List[str]] = None
    variables: Optional[List[TemplateVariable]] = None
    metadata: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None
    is_featured: Optional[bool] = None
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Template name cannot be empty')
        return v.strip() if v else v
    
    @validator('content')
    def validate_content(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Template content cannot be empty')
        return v.strip() if v else v
    
    @validator('tags')
    def validate_tags(cls, v):
        if v is not None:
            # Remove duplicates and empty tags
            v = list(set(tag.strip() for tag in v if tag.strip()))
            if len(v) > 10:
                raise ValueError('Maximum 10 tags allowed')
        return v


class TemplateResponse(BaseModel):
    """Schema for template response."""
    id: uuid.UUID
    name: str
    slug: str
    description: Optional[str] = None
    content: str
    template_type: str
    category_id: Optional[uuid.UUID] = None
    tags: List[str] = Field(default_factory=list)
    variables: List[TemplateVariable] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    is_public: bool
    is_featured: bool
    usage_count: int = 0
    created_by: uuid.UUID
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TemplateCategoryResponse(BaseModel):
    """Schema for template category response."""
    id: uuid.UUID
    name: str
    slug: str
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TemplateUsageResponse(BaseModel):
    """Schema for template usage response."""
    id: uuid.UUID
    template_id: uuid.UUID
    used_by: uuid.UUID
    variables_used: Dict[str, Any] = Field(default_factory=dict)
    document_id: Optional[uuid.UUID] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class TemplateUseRequest(BaseModel):
    """Schema for template usage request."""
    variables: Dict[str, Any] = Field(default_factory=dict)
    document_id: Optional[uuid.UUID] = None


class TemplateUseResponse(BaseModel):
    """Schema for template usage response."""
    template_id: uuid.UUID
    processed_content: str
    variables_used: Dict[str, Any] = Field(default_factory=dict)
    message: str = "Template processed successfully"


class TemplateSearch(BaseModel):
    """Schema for template search request."""
    query: Optional[str] = None
    template_type: Optional[str] = None
    category_id: Optional[uuid.UUID] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None
    is_featured: Optional[bool] = None
    created_by: Optional[uuid.UUID] = None
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)


class TemplateListResponse(BaseModel):
    """Schema for template list response."""
    templates: List[TemplateResponse]
    total: int
    page: int
    size: int
    pages: int


class TemplateStatsResponse(BaseModel):
    """Schema for template statistics response."""
    template_id: uuid.UUID
    total_uses: int
    unique_users: int
    usage_by_date: Dict[str, int]
    variable_usage: Dict[str, Dict[str, int]]
    recent_uses: List[Dict[str, Any]]


class TemplateCategoryCreate(BaseModel):
    """Schema for template category creation request."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, regex="^#[0-9A-Fa-f]{6}$")
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Category name cannot be empty')
        return v.strip()


class TemplateCategoryUpdate(BaseModel):
    """Schema for template category update request."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, regex="^#[0-9A-Fa-f]{6}$")
    is_active: Optional[bool] = None
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Category name cannot be empty')
        return v.strip() if v else v


class TemplatePreviewRequest(BaseModel):
    """Schema for template preview request."""
    variables: Dict[str, Any] = Field(default_factory=dict)


class TemplatePreviewResponse(BaseModel):
    """Schema for template preview response."""
    processed_content: str
    variables_used: Dict[str, Any] = Field(default_factory=dict)
    missing_variables: List[str] = Field(default_factory=list)


class TemplateDuplicateRequest(BaseModel):
    """Schema for template duplication request."""
    new_name: str = Field(..., min_length=1, max_length=200)
    is_public: bool = False
    
    @validator('new_name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Template name cannot be empty')
        return v.strip()


class TemplateDuplicateResponse(BaseModel):
    """Schema for template duplication response."""
    original_template_id: uuid.UUID
    new_template_id: uuid.UUID
    message: str = "Template duplicated successfully"




