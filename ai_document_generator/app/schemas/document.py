"""
Document schemas for API validation and serialization
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
import uuid

from app.models.document import DocumentStatus, DocumentType


class DocumentBase(BaseModel):
    """Base document schema with common fields."""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    document_type: DocumentType = DocumentType.TEXT
    tags: List[str] = Field(default_factory=list)
    settings: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentCreate(DocumentBase):
    """Schema for creating a new document."""
    content: str = Field(default="")
    template_id: Optional[uuid.UUID] = None
    organization_id: uuid.UUID
    
    # Collaboration settings
    is_public: bool = False
    allow_comments: bool = True
    allow_editing: bool = True
    allow_sharing: bool = True


class DocumentUpdate(BaseModel):
    """Schema for updating document information."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    content: Optional[str] = None
    document_type: Optional[DocumentType] = None
    status: Optional[DocumentStatus] = None
    tags: Optional[List[str]] = None
    settings: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    # Collaboration settings
    is_public: Optional[bool] = None
    allow_comments: Optional[bool] = None
    allow_editing: Optional[bool] = None
    allow_sharing: Optional[bool] = None


class DocumentInDB(DocumentBase):
    """Schema for document data in database."""
    id: uuid.UUID
    organization_id: uuid.UUID
    owner_id: uuid.UUID
    template_id: Optional[uuid.UUID] = None
    status: DocumentStatus
    content: str
    content_html: Optional[str] = None
    content_json: Optional[Dict[str, Any]] = None
    
    # Collaboration settings
    is_public: bool
    allow_comments: bool
    allow_editing: bool
    allow_sharing: bool
    
    # Statistics
    view_count: int
    edit_count: int
    share_count: int
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Document(DocumentInDB):
    """Schema for document response."""
    pass


class DocumentWithRelations(Document):
    """Schema for document with related data."""
    owner: Optional["User"] = None
    organization: Optional["Organization"] = None
    template: Optional["DocumentTemplate"] = None
    collaborators: List["Collaboration"] = []
    comments: List["DocumentComment"] = []
    versions: List["DocumentVersion"] = []


class DocumentVersionBase(BaseModel):
    """Base schema for document version."""
    version_number: int
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    changes: Dict[str, Any] = Field(default_factory=dict)


class DocumentVersionCreate(DocumentVersionBase):
    """Schema for creating document version."""
    content: str
    content_html: Optional[str] = None
    content_json: Optional[Dict[str, Any]] = None


class DocumentVersion(DocumentVersionBase):
    """Schema for document version response."""
    id: uuid.UUID
    document_id: uuid.UUID
    content: str
    content_html: Optional[str] = None
    content_json: Optional[Dict[str, Any]] = None
    created_by: uuid.UUID
    is_current: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class DocumentVersionWithCreator(DocumentVersion):
    """Schema for document version with creator information."""
    creator: Optional["User"] = None


class DocumentCommentBase(BaseModel):
    """Base schema for document comment."""
    content: str = Field(..., min_length=1)
    position: Optional[Dict[str, Any]] = None


class DocumentCommentCreate(DocumentCommentBase):
    """Schema for creating document comment."""
    parent_id: Optional[uuid.UUID] = None


class DocumentCommentUpdate(BaseModel):
    """Schema for updating document comment."""
    content: Optional[str] = Field(None, min_length=1)
    is_resolved: Optional[bool] = None


class DocumentComment(DocumentCommentBase):
    """Schema for document comment response."""
    id: uuid.UUID
    document_id: uuid.UUID
    author_id: uuid.UUID
    parent_id: Optional[uuid.UUID] = None
    is_resolved: bool
    resolved_by: Optional[uuid.UUID] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DocumentCommentWithAuthor(DocumentComment):
    """Schema for document comment with author information."""
    author: Optional["User"] = None
    resolver: Optional["User"] = None
    replies: List["DocumentComment"] = []


class DocumentShareBase(BaseModel):
    """Base schema for document sharing."""
    permission: str = Field(..., regex="^(view|comment|edit)$")
    expires_at: Optional[datetime] = None


class DocumentShareCreate(DocumentShareBase):
    """Schema for creating document share."""
    shared_with: Optional[uuid.UUID] = None
    shared_with_email: Optional[str] = None


class DocumentShareUpdate(BaseModel):
    """Schema for updating document share."""
    permission: Optional[str] = Field(None, regex="^(view|comment|edit)$")
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None


class DocumentShare(DocumentShareBase):
    """Schema for document share response."""
    id: uuid.UUID
    document_id: uuid.UUID
    shared_by: uuid.UUID
    shared_with: Optional[uuid.UUID] = None
    shared_with_email: Optional[str] = None
    token: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DocumentShareWithUsers(DocumentShare):
    """Schema for document share with user information."""
    sharer: Optional["User"] = None
    recipient: Optional["User"] = None


class DocumentTemplateBase(BaseModel):
    """Base schema for document template."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: str = Field(..., min_length=1, max_length=100)
    content: str
    variables: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentTemplateCreate(DocumentTemplateBase):
    """Schema for creating document template."""
    is_public: bool = False


class DocumentTemplateUpdate(BaseModel):
    """Schema for updating document template."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    content: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None
    is_active: Optional[bool] = None


class DocumentTemplate(DocumentTemplateBase):
    """Schema for document template response."""
    id: uuid.UUID
    organization_id: uuid.UUID
    is_public: bool
    is_active: bool
    usage_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DocumentTemplateWithOrg(DocumentTemplate):
    """Schema for document template with organization information."""
    organization: Optional["Organization"] = None


class DocumentListResponse(BaseModel):
    """Schema for document list response."""
    items: List[Document]
    total: int
    page: int
    size: int
    pages: int


class DocumentSearchRequest(BaseModel):
    """Schema for document search request."""
    query: Optional[str] = None
    document_type: Optional[DocumentType] = None
    status: Optional[DocumentStatus] = None
    tags: Optional[List[str]] = None
    owner_id: Optional[uuid.UUID] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)
    sort_by: str = Field(default="updated_at")
    sort_order: str = Field(default="desc", regex="^(asc|desc)$")


# Update forward references
DocumentWithRelations.model_rebuild()
DocumentVersionWithCreator.model_rebuild()
DocumentCommentWithAuthor.model_rebuild()
DocumentShareWithUsers.model_rebuild()
DocumentTemplateWithOrg.model_rebuild()




