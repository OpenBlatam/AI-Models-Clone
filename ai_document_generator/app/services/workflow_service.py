"""
Workflow service following functional patterns
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, text
from sqlalchemy.orm import selectinload
import uuid
import json

from app.core.logging import get_logger
from app.core.errors import handle_validation_error, handle_internal_error, handle_not_found_error
from app.models.workflow import Workflow, WorkflowStep, WorkflowExecution, WorkflowTrigger
from app.schemas.workflow import (
    WorkflowCreate, WorkflowUpdate, WorkflowResponse,
    WorkflowStepResponse, WorkflowExecutionResponse,
    WorkflowTriggerResponse
)
from app.utils.validators import validate_workflow_name, validate_workflow_steps
from app.utils.helpers import generate_workflow_slug, validate_workflow_logic
from app.utils.cache import cache_workflow_data, get_cached_workflow_data, invalidate_workflow_cache

logger = get_logger(__name__)


async def create_workflow(
    workflow_data: WorkflowCreate,
    user_id: str,
    db: AsyncSession
) -> WorkflowResponse:
    """Create a new workflow."""
    try:
        # Validate workflow name
        name_validation = validate_workflow_name(workflow_data.name)
        if not name_validation["is_valid"]:
            raise handle_validation_error(
                ValueError(f"Invalid workflow name: {', '.join(name_validation['errors'])}")
            )
        
        # Validate workflow steps
        steps_validation = validate_workflow_steps(workflow_data.steps)
        if not steps_validation["is_valid"]:
            raise handle_validation_error(
                ValueError(f"Invalid workflow steps: {', '.join(steps_validation['errors'])}")
            )
        
        # Generate workflow slug
        workflow_slug = generate_workflow_slug(workflow_data.name)
        
        # Check if slug already exists
        existing_workflow = await get_workflow_by_slug(workflow_slug, db)
        if existing_workflow:
            raise handle_conflict_error("Workflow with this name already exists")
        
        # Create workflow
        workflow = Workflow(
            name=workflow_data.name,
            slug=workflow_slug,
            description=workflow_data.description,
            workflow_type=workflow_data.workflow_type,
            trigger_type=workflow_data.trigger_type,
            trigger_config=workflow_data.trigger_config or {},
            steps=workflow_data.steps,
            variables=workflow_data.variables or {},
            metadata=workflow_data.metadata or {},
            is_active=workflow_data.is_active,
            is_public=workflow_data.is_public,
            created_by=user_id,
            created_at=datetime.utcnow()
        )
        
        db.add(workflow)
        await db.commit()
        await db.refresh(workflow)
        
        # Create workflow steps
        for step_data in workflow_data.steps:
            step = WorkflowStep(
                workflow_id=workflow.id,
                step_name=step_data["name"],
                step_type=step_data["type"],
                step_config=step_data["config"],
                step_order=step_data["order"],
                conditions=step_data.get("conditions", []),
                created_at=datetime.utcnow()
            )
            db.add(step)
        
        await db.commit()
        
        # Cache workflow data
        cache_workflow_data(str(workflow.id), workflow)
        
        logger.info(f"Workflow created: {workflow.id} by user {user_id}")
        
        return WorkflowResponse.from_orm(workflow)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create workflow: {e}")
        raise handle_internal_error(f"Failed to create workflow: {str(e)}")


async def get_workflow(
    workflow_id: str,
    user_id: str,
    db: AsyncSession
) -> WorkflowResponse:
    """Get workflow by ID."""
    try:
        # Check cache first
        cached_workflow = get_cached_workflow_data(workflow_id)
        if cached_workflow:
            return WorkflowResponse.from_orm(cached_workflow)
        
        # Get from database
        query = select(Workflow).where(Workflow.id == workflow_id)
        result = await db.execute(query)
        workflow = result.scalar_one_or_none()
        
        if not workflow:
            raise handle_not_found_error("Workflow", workflow_id)
        
        # Check access permissions
        has_access = await check_workflow_access(workflow, user_id, db)
        if not has_access:
            raise handle_forbidden_error("Access denied to workflow")
        
        # Cache workflow data
        cache_workflow_data(workflow_id, workflow)
        
        return WorkflowResponse.from_orm(workflow)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflow: {e}")
        raise handle_internal_error(f"Failed to get workflow: {str(e)}")


async def get_workflow_by_slug(
    slug: str,
    db: AsyncSession
) -> Optional[Workflow]:
    """Get workflow by slug."""
    try:
        query = select(Workflow).where(Workflow.slug == slug)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    except Exception as e:
        logger.error(f"Failed to get workflow by slug: {e}")
        return None


async def update_workflow(
    workflow_id: str,
    update_data: WorkflowUpdate,
    user_id: str,
    db: AsyncSession
) -> WorkflowResponse:
    """Update workflow."""
    try:
        # Get workflow
        query = select(Workflow).where(Workflow.id == workflow_id)
        result = await db.execute(query)
        workflow = result.scalar_one_or_none()
        
        if not workflow:
            raise handle_not_found_error("Workflow", workflow_id)
        
        # Check edit permissions
        can_edit = await check_workflow_edit_permission(workflow, user_id, db)
        if not can_edit:
            raise handle_forbidden_error("No edit permission for workflow")
        
        # Update fields
        if update_data.name is not None:
            name_validation = validate_workflow_name(update_data.name)
            if not name_validation["is_valid"]:
                raise ValueError(f"Invalid workflow name: {', '.join(name_validation['errors'])}")
            workflow.name = update_data.name
            workflow.slug = generate_workflow_slug(update_data.name)
        
        if update_data.description is not None:
            workflow.description = update_data.description
        
        if update_data.workflow_type is not None:
            workflow.workflow_type = update_data.workflow_type
        
        if update_data.trigger_type is not None:
            workflow.trigger_type = update_data.trigger_type
        
        if update_data.trigger_config is not None:
            workflow.trigger_config = update_data.trigger_config
        
        if update_data.steps is not None:
            steps_validation = validate_workflow_steps(update_data.steps)
            if not steps_validation["is_valid"]:
                raise ValueError(f"Invalid workflow steps: {', '.join(steps_validation['errors'])}")
            workflow.steps = update_data.steps
        
        if update_data.variables is not None:
            workflow.variables = update_data.variables
        
        if update_data.metadata is not None:
            workflow.metadata = update_data.metadata
        
        if update_data.is_active is not None:
            workflow.is_active = update_data.is_active
        
        if update_data.is_public is not None:
            workflow.is_public = update_data.is_public
        
        workflow.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(workflow)
        
        # Invalidate cache
        invalidate_workflow_cache(workflow_id)
        
        logger.info(f"Workflow updated: {workflow_id} by user {user_id}")
        
        return WorkflowResponse.from_orm(workflow)
    
    except HTTPException:
        raise
    except ValueError as e:
        raise handle_validation_error(e)
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to update workflow: {e}")
        raise handle_internal_error(f"Failed to update workflow: {str(e)}")


async def delete_workflow(
    workflow_id: str,
    user_id: str,
    db: AsyncSession
) -> Dict[str, str]:
    """Delete workflow."""
    try:
        # Get workflow
        query = select(Workflow).where(Workflow.id == workflow_id)
        result = await db.execute(query)
        workflow = result.scalar_one_or_none()
        
        if not workflow:
            raise handle_not_found_error("Workflow", workflow_id)
        
        # Check delete permissions (only creator can delete)
        if workflow.created_by != user_id:
            raise handle_forbidden_error("Only workflow creator can delete")
        
        # Soft delete
        workflow.is_deleted = True
        workflow.deleted_at = datetime.utcnow()
        workflow.deleted_by = user_id
        
        await db.commit()
        
        # Invalidate cache
        invalidate_workflow_cache(workflow_id)
        
        logger.info(f"Workflow deleted: {workflow_id} by user {user_id}")
        
        return {"message": "Workflow deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to delete workflow: {e}")
        raise handle_internal_error(f"Failed to delete workflow: {str(e)}")


async def list_workflows(
    user_id: str,
    workflow_type: Optional[str] = None,
    trigger_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_public: Optional[bool] = None,
    search_query: Optional[str] = None,
    page: int = 1,
    size: int = 20,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """List workflows with filtering and pagination."""
    try:
        # Build query
        query = select(Workflow).where(Workflow.is_deleted == False)
        
        # Apply filters
        if workflow_type:
            query = query.where(Workflow.workflow_type == workflow_type)
        
        if trigger_type:
            query = query.where(Workflow.trigger_type == trigger_type)
        
        if is_active is not None:
            query = query.where(Workflow.is_active == is_active)
        
        if is_public is not None:
            query = query.where(Workflow.is_public == is_public)
        
        if search_query:
            search_filter = or_(
                Workflow.name.ilike(f"%{search_query}%"),
                Workflow.description.ilike(f"%{search_query}%")
            )
            query = query.where(search_filter)
        
        # Apply access control
        access_filter = or_(
            Workflow.created_by == user_id,
            Workflow.is_public == True
        )
        query = query.where(access_filter)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(desc(Workflow.updated_at)).offset((page - 1) * size).limit(size)
        
        # Execute query
        result = await db.execute(query)
        workflows = result.scalars().all()
        
        # Convert to response format
        workflow_responses = [WorkflowResponse.from_orm(workflow) for workflow in workflows]
        
        return {
            "workflows": workflow_responses,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
    
    except Exception as e:
        logger.error(f"Failed to list workflows: {e}")
        raise handle_internal_error(f"Failed to list workflows: {str(e)}")


async def execute_workflow(
    workflow_id: str,
    user_id: str,
    input_data: Dict[str, Any],
    db: AsyncSession
) -> WorkflowExecutionResponse:
    """Execute a workflow."""
    try:
        # Get workflow
        workflow = await get_workflow(workflow_id, user_id, db)
        
        if not workflow.is_active:
            raise handle_forbidden_error("Workflow is not active")
        
        # Create execution record
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            executed_by=user_id,
            input_data=input_data,
            status="running",
            current_step=0,
            total_steps=len(workflow.steps),
            started_at=datetime.utcnow()
        )
        
        db.add(execution)
        await db.commit()
        await db.refresh(execution)
        
        # Execute workflow steps
        try:
            result = await execute_workflow_steps(workflow, execution, input_data, db)
            
            # Update execution status
            execution.status = "completed"
            execution.completed_at = datetime.utcnow()
            execution.output_data = result
            execution.error_message = None
            
        except Exception as e:
            # Update execution status with error
            execution.status = "failed"
            execution.completed_at = datetime.utcnow()
            execution.error_message = str(e)
            logger.error(f"Workflow execution failed: {e}")
        
        await db.commit()
        
        logger.info(f"Workflow executed: {workflow_id} by user {user_id}")
        
        return WorkflowExecutionResponse.from_orm(execution)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to execute workflow: {e}")
        raise handle_internal_error(f"Failed to execute workflow: {str(e)}")


async def execute_workflow_steps(
    workflow: Workflow,
    execution: WorkflowExecution,
    input_data: Dict[str, Any],
    db: AsyncSession
) -> Dict[str, Any]:
    """Execute workflow steps."""
    result_data = input_data.copy()
    
    for step in workflow.steps:
        # Check step conditions
        if not evaluate_step_conditions(step.get("conditions", []), result_data):
            continue
        
        # Execute step
        step_result = await execute_workflow_step(step, result_data, db)
        
        # Merge result into data
        result_data.update(step_result)
        
        # Update execution progress
        execution.current_step += 1
        await db.commit()
    
    return result_data


async def execute_workflow_step(
    step: Dict[str, Any],
    data: Dict[str, Any],
    db: AsyncSession
) -> Dict[str, Any]:
    """Execute a single workflow step."""
    step_type = step["type"]
    step_config = step["config"]
    
    if step_type == "ai_generation":
        return await execute_ai_generation_step(step_config, data, db)
    elif step_type == "document_creation":
        return await execute_document_creation_step(step_config, data, db)
    elif step_type == "notification":
        return await execute_notification_step(step_config, data, db)
    elif step_type == "data_transformation":
        return await execute_data_transformation_step(step_config, data, db)
    elif step_type == "conditional":
        return await execute_conditional_step(step_config, data, db)
    elif step_type == "loop":
        return await execute_loop_step(step_config, data, db)
    else:
        raise ValueError(f"Unknown step type: {step_type}")


async def execute_ai_generation_step(
    config: Dict[str, Any],
    data: Dict[str, Any],
    db: AsyncSession
) -> Dict[str, Any]:
    """Execute AI generation step."""
    # This would integrate with the AI service
    # For now, returning placeholder data
    return {
        "ai_generated_content": f"Generated content for: {config.get('prompt', 'default')}",
        "ai_provider": config.get("provider", "openai"),
        "ai_model": config.get("model", "gpt-4")
    }


async def execute_document_creation_step(
    config: Dict[str, Any],
    data: Dict[str, Any],
    db: AsyncSession
) -> Dict[str, Any]:
    """Execute document creation step."""
    # This would integrate with the document service
    # For now, returning placeholder data
    return {
        "document_id": str(uuid.uuid4()),
        "document_title": config.get("title", "Generated Document"),
        "document_content": data.get("content", "")
    }


async def execute_notification_step(
    config: Dict[str, Any],
    data: Dict[str, Any],
    db: AsyncSession
) -> Dict[str, Any]:
    """Execute notification step."""
    # This would integrate with the notification service
    # For now, returning placeholder data
    return {
        "notification_sent": True,
        "notification_type": config.get("type", "email"),
        "recipients": config.get("recipients", [])
    }


async def execute_data_transformation_step(
    config: Dict[str, Any],
    data: Dict[str, Any],
    db: AsyncSession
) -> Dict[str, Any]:
    """Execute data transformation step."""
    # This would implement data transformation logic
    # For now, returning placeholder data
    return {
        "transformed_data": data,
        "transformation_applied": config.get("transformation", "none")
    }


async def execute_conditional_step(
    config: Dict[str, Any],
    data: Dict[str, Any],
    db: AsyncSession
) -> Dict[str, Any]:
    """Execute conditional step."""
    condition = config.get("condition", {})
    condition_met = evaluate_condition(condition, data)
    
    if condition_met:
        return await execute_workflow_steps(config.get("true_steps", []), data, db)
    else:
        return await execute_workflow_steps(config.get("false_steps", []), data, db)


async def execute_loop_step(
    config: Dict[str, Any],
    data: Dict[str, Any],
    db: AsyncSession
) -> Dict[str, Any]:
    """Execute loop step."""
    loop_data = data.get(config.get("loop_over", "items"), [])
    results = []
    
    for item in loop_data:
        item_data = data.copy()
        item_data[config.get("item_variable", "item")] = item
        
        result = await execute_workflow_steps(config.get("steps", []), item_data, db)
        results.append(result)
    
    return {
        "loop_results": results,
        "loop_count": len(results)
    }


def evaluate_step_conditions(
    conditions: List[Dict[str, Any]],
    data: Dict[str, Any]
) -> bool:
    """Evaluate step conditions."""
    if not conditions:
        return True
    
    for condition in conditions:
        if not evaluate_condition(condition, data):
            return False
    
    return True


def evaluate_condition(
    condition: Dict[str, Any],
    data: Dict[str, Any]
) -> bool:
    """Evaluate a single condition."""
    field = condition.get("field")
    operator = condition.get("operator")
    value = condition.get("value")
    
    if field not in data:
        return False
    
    field_value = data[field]
    
    if operator == "equals":
        return field_value == value
    elif operator == "not_equals":
        return field_value != value
    elif operator == "greater_than":
        return field_value > value
    elif operator == "less_than":
        return field_value < value
    elif operator == "contains":
        return value in str(field_value)
    elif operator == "not_contains":
        return value not in str(field_value)
    elif operator == "is_empty":
        return not field_value or field_value == ""
    elif operator == "is_not_empty":
        return field_value and field_value != ""
    else:
        return False


async def get_workflow_executions(
    workflow_id: str,
    user_id: str,
    page: int = 1,
    size: int = 20,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """Get workflow executions."""
    try:
        # Check workflow access
        workflow = await get_workflow(workflow_id, user_id, db)
        
        # Get executions
        query = select(WorkflowExecution).where(
            WorkflowExecution.workflow_id == workflow_id
        ).order_by(desc(WorkflowExecution.started_at))
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # Apply pagination
        query = query.offset((page - 1) * size).limit(size)
        
        result = await db.execute(query)
        executions = result.scalars().all()
        
        execution_responses = [WorkflowExecutionResponse.from_orm(execution) for execution in executions]
        
        return {
            "executions": execution_responses,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflow executions: {e}")
        raise handle_internal_error(f"Failed to get workflow executions: {str(e)}")


async def get_workflow_stats(
    workflow_id: str,
    user_id: str,
    db: AsyncSession
) -> Dict[str, Any]:
    """Get workflow statistics."""
    try:
        # Check workflow access
        workflow = await get_workflow(workflow_id, user_id, db)
        
        # Get execution statistics
        executions_query = select(WorkflowExecution).where(
            WorkflowExecution.workflow_id == workflow_id
        )
        executions_result = await db.execute(executions_query)
        executions = executions_result.scalars().all()
        
        # Calculate stats
        total_executions = len(executions)
        successful_executions = len([e for e in executions if e.status == "completed"])
        failed_executions = len([e for e in executions if e.status == "failed"])
        running_executions = len([e for e in executions if e.status == "running"])
        
        # Execution by date
        execution_by_date = {}
        for execution in executions:
            date = execution.started_at.date()
            if date not in execution_by_date:
                execution_by_date[date] = {"total": 0, "successful": 0, "failed": 0}
            execution_by_date[date]["total"] += 1
            if execution.status == "completed":
                execution_by_date[date]["successful"] += 1
            elif execution.status == "failed":
                execution_by_date[date]["failed"] += 1
        
        # Average execution time
        completed_executions = [e for e in executions if e.status == "completed" and e.completed_at]
        avg_execution_time = 0
        if completed_executions:
            total_time = sum(
                (e.completed_at - e.started_at).total_seconds()
                for e in completed_executions
            )
            avg_execution_time = total_time / len(completed_executions)
        
        return {
            "workflow_id": workflow_id,
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "failed_executions": failed_executions,
            "running_executions": running_executions,
            "success_rate": successful_executions / total_executions if total_executions > 0 else 0,
            "average_execution_time": avg_execution_time,
            "execution_by_date": execution_by_date,
            "recent_executions": [
                {
                    "id": str(execution.id),
                    "status": execution.status,
                    "started_at": execution.started_at.isoformat(),
                    "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
                    "error_message": execution.error_message
                }
                for execution in executions[-10:]  # Last 10 executions
            ]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflow stats: {e}")
        raise handle_internal_error(f"Failed to get workflow stats: {str(e)}")


# Helper functions
async def check_workflow_access(
    workflow: Workflow,
    user_id: str,
    db: AsyncSession
) -> bool:
    """Check if user has access to workflow."""
    # Creator has access
    if workflow.created_by == user_id:
        return True
    
    # Public workflows
    if workflow.is_public:
        return True
    
    return False


async def check_workflow_edit_permission(
    workflow: Workflow,
    user_id: str,
    db: AsyncSession
) -> bool:
    """Check if user can edit workflow."""
    # Only creator can edit
    if workflow.created_by == user_id:
        return True
    
    return False




