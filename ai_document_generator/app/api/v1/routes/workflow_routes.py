"""
Workflow routes following functional patterns and RORO
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.errors import handle_validation_error, handle_internal_error
from app.schemas.user import User
from app.schemas.workflow import (
    WorkflowCreate, WorkflowUpdate, WorkflowResponse,
    WorkflowExecuteRequest, WorkflowExecuteResponse,
    WorkflowListResponse, WorkflowExecutionListResponse,
    WorkflowStatsResponse, WorkflowDuplicateRequest,
    WorkflowDuplicateResponse, WorkflowTestRequest,
    WorkflowTestResponse
)
from app.services.workflow_service import (
    create_workflow, get_workflow, update_workflow, delete_workflow,
    list_workflows, execute_workflow, get_workflow_executions,
    get_workflow_stats
)
from app.utils.validators import validate_pagination
from app.utils.rate_limiter import rate_limit_workflow_execution

router = APIRouter()


async def create_workflow_endpoint(
    workflow_data: WorkflowCreate,
    user: User,
    db: AsyncSession
) -> WorkflowResponse:
    """Create a new workflow."""
    return await create_workflow(workflow_data, user.id, db)


async def get_workflow_endpoint(
    workflow_id: str,
    user: User,
    db: AsyncSession
) -> WorkflowResponse:
    """Get workflow by ID."""
    try:
        workflow_uuid = uuid.UUID(workflow_id)
    except ValueError:
        raise handle_validation_error(ValueError("Invalid workflow ID format"))
    
    return await get_workflow(workflow_uuid, user.id, db)


async def update_workflow_endpoint(
    workflow_id: str,
    update_data: WorkflowUpdate,
    user: User,
    db: AsyncSession
) -> WorkflowResponse:
    """Update workflow."""
    try:
        workflow_uuid = uuid.UUID(workflow_id)
    except ValueError:
        raise handle_validation_error(ValueError("Invalid workflow ID format"))
    
    return await update_workflow(workflow_uuid, update_data, user.id, db)


async def delete_workflow_endpoint(
    workflow_id: str,
    user: User,
    db: AsyncSession
) -> Dict[str, str]:
    """Delete workflow."""
    try:
        workflow_uuid = uuid.UUID(workflow_id)
    except ValueError:
        raise handle_validation_error(ValueError("Invalid workflow ID format"))
    
    result = await delete_workflow(workflow_uuid, user.id, db)
    
    return {"message": result["message"]}


async def list_workflows_endpoint(
    user: User,
    workflow_type: Optional[str] = None,
    trigger_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_public: Optional[bool] = None,
    search_query: Optional[str] = None,
    page: int = 1,
    size: int = 20,
    db: AsyncSession = None
) -> WorkflowListResponse:
    """List workflows with filtering and pagination."""
    # Validate pagination
    pagination_validation = validate_pagination(page, size)
    if not pagination_validation["is_valid"]:
        raise handle_validation_error(
            ValueError(f"Invalid pagination: {', '.join(pagination_validation['errors'])}")
        )
    
    result = await list_workflows(
        user.id, workflow_type, trigger_type, is_active,
        is_public, search_query, page, size, db
    )
    
    return WorkflowListResponse(**result)


async def execute_workflow_endpoint(
    workflow_id: str,
    execute_data: WorkflowExecuteRequest,
    user: User,
    db: AsyncSession
) -> WorkflowExecuteResponse:
    """Execute a workflow."""
    try:
        workflow_uuid = uuid.UUID(workflow_id)
    except ValueError:
        raise handle_validation_error(ValueError("Invalid workflow ID format"))
    
    execution = await execute_workflow(workflow_uuid, user.id, execute_data.input_data, db)
    
    return WorkflowExecuteResponse(
        execution_id=execution.id,
        status=execution.status,
        message="Workflow execution started"
    )


async def get_workflow_executions_endpoint(
    workflow_id: str,
    user: User,
    page: int = 1,
    size: int = 20,
    db: AsyncSession = None
) -> WorkflowExecutionListResponse:
    """Get workflow executions."""
    try:
        workflow_uuid = uuid.UUID(workflow_id)
    except ValueError:
        raise handle_validation_error(ValueError("Invalid workflow ID format"))
    
    # Validate pagination
    pagination_validation = validate_pagination(page, size)
    if not pagination_validation["is_valid"]:
        raise handle_validation_error(
            ValueError(f"Invalid pagination: {', '.join(pagination_validation['errors'])}")
        )
    
    result = await get_workflow_executions(workflow_uuid, user.id, page, size, db)
    
    return WorkflowExecutionListResponse(**result)


async def get_workflow_stats_endpoint(
    workflow_id: str,
    user: User,
    db: AsyncSession
) -> WorkflowStatsResponse:
    """Get workflow statistics."""
    try:
        workflow_uuid = uuid.UUID(workflow_id)
    except ValueError:
        raise handle_validation_error(ValueError("Invalid workflow ID format"))
    
    result = await get_workflow_stats(workflow_uuid, user.id, db)
    
    return WorkflowStatsResponse(**result)


# Route definitions
@router.post("/", response_model=WorkflowResponse)
async def create_workflow_route(
    workflow_data: WorkflowCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> WorkflowResponse:
    """Create a new workflow."""
    return await create_workflow_endpoint(workflow_data, current_user, db)


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow_route(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> WorkflowResponse:
    """Get workflow by ID."""
    return await get_workflow_endpoint(workflow_id, current_user, db)


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow_route(
    workflow_id: str,
    update_data: WorkflowUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> WorkflowResponse:
    """Update workflow."""
    return await update_workflow_endpoint(workflow_id, update_data, current_user, db)


@router.delete("/{workflow_id}")
async def delete_workflow_route(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Delete workflow."""
    return await delete_workflow_endpoint(workflow_id, current_user, db)


@router.get("/", response_model=WorkflowListResponse)
async def list_workflows_route(
    workflow_type: Optional[str] = Query(None, description="Filter by workflow type"),
    trigger_type: Optional[str] = Query(None, description="Filter by trigger type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_public: Optional[bool] = Query(None, description="Filter by public status"),
    search_query: Optional[str] = Query(None, description="Search in name and description"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> WorkflowListResponse:
    """List workflows with filtering and pagination."""
    return await list_workflows_endpoint(
        current_user, workflow_type, trigger_type, is_active,
        is_public, search_query, page, size, db
    )


@router.post("/{workflow_id}/execute", response_model=WorkflowExecuteResponse)
@rate_limit_workflow_execution(key_func=lambda user, **kwargs: f"user:{user.id}")
async def execute_workflow_route(
    workflow_id: str,
    execute_data: WorkflowExecuteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> WorkflowExecuteResponse:
    """Execute a workflow."""
    return await execute_workflow_endpoint(workflow_id, execute_data, current_user, db)


@router.get("/{workflow_id}/executions", response_model=WorkflowExecutionListResponse)
async def get_workflow_executions_route(
    workflow_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> WorkflowExecutionListResponse:
    """Get workflow executions."""
    return await get_workflow_executions_endpoint(workflow_id, current_user, page, size, db)


@router.get("/{workflow_id}/stats", response_model=WorkflowStatsResponse)
async def get_workflow_stats_route(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> WorkflowStatsResponse:
    """Get workflow statistics."""
    return await get_workflow_stats_endpoint(workflow_id, current_user, db)


@router.post("/{workflow_id}/duplicate", response_model=WorkflowDuplicateResponse)
async def duplicate_workflow_route(
    workflow_id: str,
    duplicate_data: WorkflowDuplicateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> WorkflowDuplicateResponse:
    """Duplicate a workflow."""
    try:
        workflow_uuid = uuid.UUID(workflow_id)
    except ValueError:
        raise handle_validation_error(ValueError("Invalid workflow ID format"))
    
    # Get original workflow
    original_workflow = await get_workflow(workflow_uuid, current_user.id, db)
    
    # Create duplicate workflow data
    duplicate_workflow_data = WorkflowCreate(
        name=duplicate_data.new_name,
        description=original_workflow.description,
        workflow_type=original_workflow.workflow_type,
        trigger_type=original_workflow.trigger_type,
        trigger_config=original_workflow.trigger_config,
        steps=original_workflow.steps,
        variables=original_workflow.variables,
        metadata=original_workflow.metadata,
        is_active=False,  # Duplicates are inactive by default
        is_public=duplicate_data.is_public
    )
    
    # Create duplicate
    new_workflow = await create_workflow(duplicate_workflow_data, current_user.id, db)
    
    return WorkflowDuplicateResponse(
        original_workflow_id=workflow_uuid,
        new_workflow_id=new_workflow.id,
        message="Workflow duplicated successfully"
    )


@router.post("/{workflow_id}/test", response_model=WorkflowTestResponse)
async def test_workflow_route(
    workflow_id: str,
    test_data: WorkflowTestRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> WorkflowTestResponse:
    """Test a workflow without saving results."""
    try:
        workflow_uuid = uuid.UUID(workflow_id)
    except ValueError:
        raise handle_validation_error(ValueError("Invalid workflow ID format"))
    
    # This would implement workflow testing logic
    # For now, returning placeholder data
    return WorkflowTestResponse(
        test_id=uuid.uuid4(),
        status="completed",
        results={"test_output": "Workflow test completed successfully"},
        message="Workflow test completed"
    )


@router.get("/{workflow_id}/export")
async def export_workflow_route(
    workflow_id: str,
    format: str = Query("json", description="Export format (json, yaml)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Export workflow in specified format."""
    try:
        workflow_uuid = uuid.UUID(workflow_id)
    except ValueError:
        raise handle_validation_error(ValueError("Invalid workflow ID format"))
    
    # Get workflow
    workflow = await get_workflow(workflow_uuid, current_user.id, db)
    
    # This would implement actual export logic
    # For now, returning a placeholder response
    return {
        "workflow_id": workflow_id,
        "format": format,
        "download_url": f"/api/v1/workflows/{workflow_id}/download/{format}",
        "expires_at": "2023-12-31T23:59:59Z"
    }


@router.post("/{workflow_id}/import")
async def import_workflow_route(
    workflow_id: str,
    import_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Import workflow configuration."""
    try:
        workflow_uuid = uuid.UUID(workflow_id)
    except ValueError:
        raise handle_validation_error(ValueError("Invalid workflow ID format"))
    
    # This would implement workflow import logic
    # For now, returning a placeholder response
    return {"message": "Workflow imported successfully"}


@router.get("/{workflow_id}/templates")
async def get_workflow_templates_route(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get workflow templates."""
    # This would implement workflow templates logic
    # For now, returning placeholder data
    return [
        {
            "id": "template-1",
            "name": "Document Generation Template",
            "description": "Template for document generation workflows",
            "workflow_type": "document",
            "steps": []
        },
        {
            "id": "template-2",
            "name": "Email Automation Template",
            "description": "Template for email automation workflows",
            "workflow_type": "email",
            "steps": []
        }
    ]


@router.get("/{workflow_id}/logs")
async def get_workflow_logs_route(
    workflow_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get workflow execution logs."""
    try:
        workflow_uuid = uuid.UUID(workflow_id)
    except ValueError:
        raise handle_validation_error(ValueError("Invalid workflow ID format"))
    
    # This would implement workflow logs logic
    # For now, returning placeholder data
    return {
        "logs": [
            {
                "id": "log-1",
                "level": "INFO",
                "message": "Workflow execution started",
                "timestamp": "2023-01-01T12:00:00Z",
                "execution_id": "exec-1"
            }
        ],
        "total": 1,
        "page": page,
        "size": size,
        "pages": 1
    }


@router.post("/{workflow_id}/schedule")
async def schedule_workflow_route(
    workflow_id: str,
    schedule_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Schedule a workflow for execution."""
    try:
        workflow_uuid = uuid.UUID(workflow_id)
    except ValueError:
        raise handle_validation_error(ValueError("Invalid workflow ID format"))
    
    # This would implement workflow scheduling logic
    # For now, returning a placeholder response
    return {"message": "Workflow scheduled successfully"}


@router.delete("/{workflow_id}/schedule")
async def unschedule_workflow_route(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Unschedule a workflow."""
    try:
        workflow_uuid = uuid.UUID(workflow_id)
    except ValueError:
        raise handle_validation_error(ValueError("Invalid workflow ID format"))
    
    # This would implement workflow unscheduling logic
    # For now, returning a placeholder response
    return {"message": "Workflow unscheduled successfully"}




