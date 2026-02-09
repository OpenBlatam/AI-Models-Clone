"""
Workflow schemas for Pydantic validation
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator
import uuid


class WorkflowStep(BaseModel):
    """Schema for workflow step definition."""
    name: str = Field(..., min_length=1, max_length=100)
    type: str = Field(..., min_length=1, max_length=50)
    config: Dict[str, Any] = Field(..., min_items=1)
    order: int = Field(..., ge=1)
    conditions: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Step name cannot be empty')
        return v.strip()
    
    @validator('type')
    def validate_type(cls, v):
        allowed_types = [
            'ai_generation', 'document_creation', 'notification',
            'data_transformation', 'conditional', 'loop', 'webhook',
            'email', 'file_upload', 'data_validation'
        ]
        if v not in allowed_types:
            raise ValueError(f'Invalid step type. Allowed: {", ".join(allowed_types)}')
        return v


class WorkflowCondition(BaseModel):
    """Schema for workflow condition definition."""
    field: str = Field(..., min_length=1, max_length=100)
    operator: str = Field(..., regex="^(equals|not_equals|greater_than|less_than|contains|not_contains|is_empty|is_not_empty)$")
    value: Any = None
    
    @validator('field')
    def validate_field(cls, v):
        if not v or not v.strip():
            raise ValueError('Condition field cannot be empty')
        return v.strip()


class WorkflowCreate(BaseModel):
    """Schema for workflow creation request."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    workflow_type: str = Field(..., min_length=1, max_length=50)
    trigger_type: str = Field(..., min_length=1, max_length=50)
    trigger_config: Optional[Dict[str, Any]] = Field(default_factory=dict)
    steps: List[WorkflowStep] = Field(..., min_items=1)
    variables: Optional[Dict[str, Any]] = Field(default_factory=dict)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    is_active: bool = True
    is_public: bool = False
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Workflow name cannot be empty')
        return v.strip()
    
    @validator('workflow_type')
    def validate_workflow_type(cls, v):
        allowed_types = ['document', 'email', 'automation', 'notification', 'data_processing']
        if v not in allowed_types:
            raise ValueError(f'Invalid workflow type. Allowed: {", ".join(allowed_types)}')
        return v
    
    @validator('trigger_type')
    def validate_trigger_type(cls, v):
        allowed_types = ['manual', 'scheduled', 'webhook', 'event', 'api']
        if v not in allowed_types:
            raise ValueError(f'Invalid trigger type. Allowed: {", ".join(allowed_types)}')
        return v
    
    @validator('steps')
    def validate_steps(cls, v):
        if not v:
            raise ValueError('Workflow must have at least one step')
        
        # Check for unique step names
        step_names = [step.name for step in v]
        if len(step_names) != len(set(step_names)):
            raise ValueError('Step names must be unique')
        
        # Check for unique step orders
        step_orders = [step.order for step in v]
        if len(step_orders) != len(set(step_orders)):
            raise ValueError('Step orders must be unique')
        
        return v


class WorkflowUpdate(BaseModel):
    """Schema for workflow update request."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    workflow_type: Optional[str] = Field(None, min_length=1, max_length=50)
    trigger_type: Optional[str] = Field(None, min_length=1, max_length=50)
    trigger_config: Optional[Dict[str, Any]] = None
    steps: Optional[List[WorkflowStep]] = None
    variables: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    is_public: Optional[bool] = None
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Workflow name cannot be empty')
        return v.strip() if v else v
    
    @validator('workflow_type')
    def validate_workflow_type(cls, v):
        if v is not None:
            allowed_types = ['document', 'email', 'automation', 'notification', 'data_processing']
            if v not in allowed_types:
                raise ValueError(f'Invalid workflow type. Allowed: {", ".join(allowed_types)}')
        return v
    
    @validator('trigger_type')
    def validate_trigger_type(cls, v):
        if v is not None:
            allowed_types = ['manual', 'scheduled', 'webhook', 'event', 'api']
            if v not in allowed_types:
                raise ValueError(f'Invalid trigger type. Allowed: {", ".join(allowed_types)}')
        return v


class WorkflowResponse(BaseModel):
    """Schema for workflow response."""
    id: uuid.UUID
    name: str
    slug: str
    description: Optional[str] = None
    workflow_type: str
    trigger_type: str
    trigger_config: Dict[str, Any] = Field(default_factory=dict)
    steps: List[WorkflowStep] = Field(default_factory=list)
    variables: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool
    is_public: bool
    execution_count: int = 0
    created_by: uuid.UUID
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WorkflowStepResponse(BaseModel):
    """Schema for workflow step response."""
    id: uuid.UUID
    workflow_id: uuid.UUID
    step_name: str
    step_type: str
    step_config: Dict[str, Any] = Field(default_factory=dict)
    step_order: int
    conditions: List[Dict[str, Any]] = Field(default_factory=list)
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WorkflowExecutionResponse(BaseModel):
    """Schema for workflow execution response."""
    id: uuid.UUID
    workflow_id: uuid.UUID
    executed_by: uuid.UUID
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_data: Dict[str, Any] = Field(default_factory=dict)
    status: str
    current_step: int
    total_steps: int
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class WorkflowTriggerResponse(BaseModel):
    """Schema for workflow trigger response."""
    id: uuid.UUID
    workflow_id: uuid.UUID
    trigger_type: str
    trigger_config: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WorkflowExecuteRequest(BaseModel):
    """Schema for workflow execution request."""
    input_data: Dict[str, Any] = Field(default_factory=dict)
    async_execution: bool = False


class WorkflowExecuteResponse(BaseModel):
    """Schema for workflow execution response."""
    execution_id: uuid.UUID
    status: str
    message: str = "Workflow execution started"


class WorkflowSearch(BaseModel):
    """Schema for workflow search request."""
    query: Optional[str] = None
    workflow_type: Optional[str] = None
    trigger_type: Optional[str] = None
    is_active: Optional[bool] = None
    is_public: Optional[bool] = None
    created_by: Optional[uuid.UUID] = None
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)


class WorkflowListResponse(BaseModel):
    """Schema for workflow list response."""
    workflows: List[WorkflowResponse]
    total: int
    page: int
    size: int
    pages: int


class WorkflowExecutionListResponse(BaseModel):
    """Schema for workflow execution list response."""
    executions: List[WorkflowExecutionResponse]
    total: int
    page: int
    size: int
    pages: int


class WorkflowStatsResponse(BaseModel):
    """Schema for workflow statistics response."""
    workflow_id: uuid.UUID
    total_executions: int
    successful_executions: int
    failed_executions: int
    running_executions: int
    success_rate: float
    average_execution_time: float
    execution_by_date: Dict[str, Dict[str, int]]
    recent_executions: List[Dict[str, Any]]


class WorkflowTemplate(BaseModel):
    """Schema for workflow template."""
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    workflow_type: str = Field(..., min_length=1, max_length=50)
    trigger_type: str = Field(..., min_length=1, max_length=50)
    steps: List[WorkflowStep] = Field(..., min_items=1)
    variables: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    is_public: bool = True


class WorkflowDuplicateRequest(BaseModel):
    """Schema for workflow duplication request."""
    new_name: str = Field(..., min_length=1, max_length=200)
    is_public: bool = False
    
    @validator('new_name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Workflow name cannot be empty')
        return v.strip()


class WorkflowDuplicateResponse(BaseModel):
    """Schema for workflow duplication response."""
    original_workflow_id: uuid.UUID
    new_workflow_id: uuid.UUID
    message: str = "Workflow duplicated successfully"


class WorkflowTestRequest(BaseModel):
    """Schema for workflow test request."""
    input_data: Dict[str, Any] = Field(default_factory=dict)
    test_mode: bool = True


class WorkflowTestResponse(BaseModel):
    """Schema for workflow test response."""
    test_id: uuid.UUID
    status: str
    results: Dict[str, Any] = Field(default_factory=dict)
    message: str = "Workflow test completed"




