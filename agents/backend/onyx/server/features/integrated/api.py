"""
Integrated API Models - Onyx Integration
Enhanced models for integrated API with advanced features.
"""
from typing import Dict, List, Optional, Union, Any, TypeVar, Generic
from datetime import datetime
from pydantic import Field, validator, root_validator
from ...utils.base_model import OnyxBaseModel

T = TypeVar('T')

class DocumentRequest(OnyxBaseModel):
    """Enhanced document processing request."""
    
    document_url: Optional[str] = None
    document_content: Optional[str] = None
    document_type: str = Field(default="text")
    language: str = Field(default="en")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Configure indexing
    index_fields = ["document_type", "language"]
    search_fields = ["document_content"]
    
    @root_validator
    def validate_document_source(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that either URL or content is provided."""
        if not values.get("document_url") and not values.get("document_content"):
            raise ValueError("Either document_url or document_content must be provided")
        return values
    
    @validator("document_type")
    def validate_document_type(cls, v: str) -> str:
        """Validate document type."""
        allowed_types = ["text", "pdf", "doc", "docx", "html"]
        if v not in allowed_types:
            raise ValueError(f"Document type must be one of: {', '.join(allowed_types)}")
        return v
    
    @validator("language")
    def validate_language(cls, v: str) -> str:
        """Validate language code."""
        if len(v) != 2:
            raise ValueError("Language must be a 2-letter code")
        return v.lower()

class AdsRequest(OnyxBaseModel):
    """Enhanced ads generation request."""
    
    ads_type: str
    target_audience: str
    platform: str
    brand_voice: Optional[Dict[str, Any]] = None
    content_guidelines: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Configure indexing
    index_fields = ["ads_type", "platform", "target_audience"]
    search_fields = ["content_guidelines"]
    
    @validator("ads_type")
    def validate_ads_type(cls, v: str) -> str:
        """Validate ads type."""
        allowed_types = ["social", "display", "search", "video"]
        if v not in allowed_types:
            raise ValueError(f"Ads type must be one of: {', '.join(allowed_types)}")
        return v
    
    @validator("platform")
    def validate_platform(cls, v: str) -> str:
        """Validate platform."""
        allowed_platforms = ["facebook", "instagram", "twitter", "linkedin", "google"]
        if v not in allowed_platforms:
            raise ValueError(f"Platform must be one of: {', '.join(allowed_platforms)}")
        return v

class ChatRequest(OnyxBaseModel):
    """Enhanced chat request."""
    
    chat_message: str
    context: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Configure indexing
    index_fields = ["user_id", "session_id"]
    search_fields = ["chat_message"]
    
    @validator("chat_message")
    def validate_message(cls, v: str) -> str:
        """Validate chat message."""
        if not v.strip():
            raise ValueError("Chat message cannot be empty")
        return v.strip()

class FileRequest(OnyxBaseModel):
    """Enhanced file processing request."""
    
    file_url: Optional[str] = None
    file_content: Optional[bytes] = None
    file_type: str
    file_name: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Configure indexing
    index_fields = ["file_type", "file_name"]
    search_fields = ["file_name"]
    
    @root_validator
    def validate_file_source(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that either URL or content is provided."""
        if not values.get("file_url") and not values.get("file_content"):
            raise ValueError("Either file_url or file_content must be provided")
        return values
    
    @validator("file_type")
    def validate_file_type(cls, v: str) -> str:
        """Validate file type."""
        allowed_types = ["image", "video", "audio", "document"]
        if v not in allowed_types:
            raise ValueError(f"File type must be one of: {', '.join(allowed_types)}")
        return v

class NLPRequest(OnyxBaseModel):
    """Enhanced NLP request."""
    
    text: str
    nlp_task: str
    language: str = Field(default="en")
    options: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Configure indexing
    index_fields = ["nlp_task", "language"]
    search_fields = ["text"]
    
    @validator("nlp_task")
    def validate_nlp_task(cls, v: str) -> str:
        """Validate NLP task."""
        allowed_tasks = ["sentiment", "classification", "extraction", "summarization"]
        if v not in allowed_tasks:
            raise ValueError(f"NLP task must be one of: {', '.join(allowed_tasks)}")
        return v
    
    @validator("language")
    def validate_language(cls, v: str) -> str:
        """Validate language code."""
        if len(v) != 2:
            raise ValueError("Language must be a 2-letter code")
        return v.lower()

class AgentRequest(OnyxBaseModel):
    """Enhanced agent request."""
    
    agent_task: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    context: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Configure indexing
    index_fields = ["agent_task"]
    search_fields = ["parameters"]
    
    @validator("agent_task")
    def validate_agent_task(cls, v: str) -> str:
        """Validate agent task."""
        if not v.strip():
            raise ValueError("Agent task cannot be empty")
        return v.strip()

class IntegratedRequest(OnyxBaseModel):
    """Enhanced integrated request."""
    
    document_request: Optional[DocumentRequest] = None
    ads_request: Optional[AdsRequest] = None
    chat_request: Optional[ChatRequest] = None
    file_request: Optional[FileRequest] = None
    nlp_request: Optional[NLPRequest] = None
    agent_request: Optional[AgentRequest] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Configure indexing
    index_fields = ["id"]
    search_fields = ["metadata"]
    
    @root_validator
    def validate_request_types(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that at least one request type is provided."""
        request_types = [
            "document_request",
            "ads_request",
            "chat_request",
            "file_request",
            "nlp_request",
            "agent_request"
        ]
        if not any(values.get(rt) for rt in request_types):
            raise ValueError("At least one request type must be provided")
        return values

class IntegratedResponse(OnyxBaseModel, Generic[T]):
    """Enhanced integrated response."""
    
    request_id: str
    status: str
    result: T
    metadata: Dict[str, Any] = Field(default_factory=dict)
    performance_metrics: Dict[str, float] = Field(default_factory=dict)
    
    # Configure indexing
    index_fields = ["request_id", "status"]
    search_fields = ["metadata"]
    
    @validator("status")
    def validate_status(cls, v: str) -> str:
        """Validate status."""
        allowed_statuses = ["success", "error", "processing"]
        if v not in allowed_statuses:
            raise ValueError(f"Status must be one of: {', '.join(allowed_statuses)}")
        return v

# Example usage:
"""
# Create document request
doc_request = DocumentRequest(
    document_url="https://example.com/doc.pdf",
    document_type="pdf",
    language="en"
)

# Create ads request
ads_request = AdsRequest(
    ads_type="social",
    target_audience="Tech Professionals",
    platform="linkedin",
    brand_voice={
        "tone": "professional",
        "style": "formal"
    }
)

# Create chat request
chat_request = ChatRequest(
    chat_message="Hello, how can I help you?",
    user_id="user123",
    session_id="session456"
)

# Create integrated request
integrated_request = IntegratedRequest(
    document_request=doc_request,
    ads_request=ads_request,
    chat_request=chat_request,
    metadata={"priority": "high"}
)

# Index request
redis_indexer = RedisIndexer()
integrated_request.index(redis_indexer)

# Create response
response = IntegratedResponse(
    request_id="req123",
    status="success",
    result={
        "document": {"processed": True},
        "ads": {"generated": True},
        "chat": {"response": "I can help you with that!"}
    }
)

# Index response
response.index(redis_indexer)
""" 