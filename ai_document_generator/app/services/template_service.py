"""
Template service following functional patterns
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
from app.models.template import Template, TemplateCategory, TemplateUsage
from app.schemas.template import (
    TemplateCreate, TemplateUpdate, TemplateResponse,
    TemplateCategoryResponse, TemplateUsageResponse
)
from app.utils.validators import validate_template_content, validate_template_name
from app.utils.helpers import generate_template_slug, sanitize_template_content
from app.utils.cache import cache_template_data, get_cached_template_data, invalidate_template_cache

logger = get_logger(__name__)


async def create_template(
    template_data: TemplateCreate,
    user_id: str,
    db: AsyncSession
) -> TemplateResponse:
    """Create a new template."""
    try:
        # Validate template name
        name_validation = validate_template_name(template_data.name)
        if not name_validation["is_valid"]:
            raise handle_validation_error(
                ValueError(f"Invalid template name: {', '.join(name_validation['errors'])}")
            )
        
        # Validate template content
        content_validation = validate_template_content(template_data.content)
        if not content_validation["is_valid"]:
            raise handle_validation_error(
                ValueError(f"Invalid template content: {', '.join(content_validation['errors'])}")
            )
        
        # Generate template slug
        template_slug = generate_template_slug(template_data.name)
        
        # Check if slug already exists
        existing_template = await get_template_by_slug(template_slug, db)
        if existing_template:
            raise handle_conflict_error("Template with this name already exists")
        
        # Create template
        template = Template(
            name=template_data.name,
            slug=template_slug,
            description=template_data.description,
            content=template_data.content,
            template_type=template_data.template_type,
            category_id=template_data.category_id,
            tags=template_data.tags or [],
            variables=template_data.variables or [],
            metadata=template_data.metadata or {},
            is_public=template_data.is_public,
            is_featured=template_data.is_featured,
            created_by=user_id,
            created_at=datetime.utcnow()
        )
        
        db.add(template)
        await db.commit()
        await db.refresh(template)
        
        # Cache template data
        cache_template_data(str(template.id), template)
        
        logger.info(f"Template created: {template.id} by user {user_id}")
        
        return TemplateResponse.from_orm(template)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create template: {e}")
        raise handle_internal_error(f"Failed to create template: {str(e)}")


async def get_template(
    template_id: str,
    user_id: str,
    db: AsyncSession
) -> TemplateResponse:
    """Get template by ID."""
    try:
        # Check cache first
        cached_template = get_cached_template_data(template_id)
        if cached_template:
            return TemplateResponse.from_orm(cached_template)
        
        # Get from database
        query = select(Template).where(Template.id == template_id)
        result = await db.execute(query)
        template = result.scalar_one_or_none()
        
        if not template:
            raise handle_not_found_error("Template", template_id)
        
        # Check access permissions
        has_access = await check_template_access(template, user_id, db)
        if not has_access:
            raise handle_forbidden_error("Access denied to template")
        
        # Cache template data
        cache_template_data(template_id, template)
        
        return TemplateResponse.from_orm(template)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get template: {e}")
        raise handle_internal_error(f"Failed to get template: {str(e)}")


async def get_template_by_slug(
    slug: str,
    db: AsyncSession
) -> Optional[Template]:
    """Get template by slug."""
    try:
        query = select(Template).where(Template.slug == slug)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    except Exception as e:
        logger.error(f"Failed to get template by slug: {e}")
        return None


async def update_template(
    template_id: str,
    update_data: TemplateUpdate,
    user_id: str,
    db: AsyncSession
) -> TemplateResponse:
    """Update template."""
    try:
        # Get template
        query = select(Template).where(Template.id == template_id)
        result = await db.execute(query)
        template = result.scalar_one_or_none()
        
        if not template:
            raise handle_not_found_error("Template", template_id)
        
        # Check edit permissions
        can_edit = await check_template_edit_permission(template, user_id, db)
        if not can_edit:
            raise handle_forbidden_error("No edit permission for template")
        
        # Update fields
        if update_data.name is not None:
            name_validation = validate_template_name(update_data.name)
            if not name_validation["is_valid"]:
                raise ValueError(f"Invalid template name: {', '.join(name_validation['errors'])}")
            template.name = update_data.name
            template.slug = generate_template_slug(update_data.name)
        
        if update_data.description is not None:
            template.description = update_data.description
        
        if update_data.content is not None:
            content_validation = validate_template_content(update_data.content)
            if not content_validation["is_valid"]:
                raise ValueError(f"Invalid template content: {', '.join(content_validation['errors'])}")
            template.content = update_data.content
        
        if update_data.template_type is not None:
            template.template_type = update_data.template_type
        
        if update_data.category_id is not None:
            template.category_id = update_data.category_id
        
        if update_data.tags is not None:
            template.tags = update_data.tags
        
        if update_data.variables is not None:
            template.variables = update_data.variables
        
        if update_data.metadata is not None:
            template.metadata = update_data.metadata
        
        if update_data.is_public is not None:
            template.is_public = update_data.is_public
        
        if update_data.is_featured is not None:
            template.is_featured = update_data.is_featured
        
        template.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(template)
        
        # Invalidate cache
        invalidate_template_cache(template_id)
        
        logger.info(f"Template updated: {template_id} by user {user_id}")
        
        return TemplateResponse.from_orm(template)
    
    except HTTPException:
        raise
    except ValueError as e:
        raise handle_validation_error(e)
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to update template: {e}")
        raise handle_internal_error(f"Failed to update template: {str(e)}")


async def delete_template(
    template_id: str,
    user_id: str,
    db: AsyncSession
) -> Dict[str, str]:
    """Delete template."""
    try:
        # Get template
        query = select(Template).where(Template.id == template_id)
        result = await db.execute(query)
        template = result.scalar_one_or_none()
        
        if not template:
            raise handle_not_found_error("Template", template_id)
        
        # Check delete permissions (only creator can delete)
        if template.created_by != user_id:
            raise handle_forbidden_error("Only template creator can delete")
        
        # Soft delete
        template.is_deleted = True
        template.deleted_at = datetime.utcnow()
        template.deleted_by = user_id
        
        await db.commit()
        
        # Invalidate cache
        invalidate_template_cache(template_id)
        
        logger.info(f"Template deleted: {template_id} by user {user_id}")
        
        return {"message": "Template deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to delete template: {e}")
        raise handle_internal_error(f"Failed to delete template: {str(e)}")


async def list_templates(
    user_id: str,
    category_id: Optional[str] = None,
    template_type: Optional[str] = None,
    is_public: Optional[bool] = None,
    is_featured: Optional[bool] = None,
    search_query: Optional[str] = None,
    page: int = 1,
    size: int = 20,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """List templates with filtering and pagination."""
    try:
        # Build query
        query = select(Template).where(Template.is_deleted == False)
        
        # Apply filters
        if category_id:
            query = query.where(Template.category_id == category_id)
        
        if template_type:
            query = query.where(Template.template_type == template_type)
        
        if is_public is not None:
            query = query.where(Template.is_public == is_public)
        
        if is_featured is not None:
            query = query.where(Template.is_featured == is_featured)
        
        if search_query:
            search_filter = or_(
                Template.name.ilike(f"%{search_query}%"),
                Template.description.ilike(f"%{search_query}%"),
                Template.content.ilike(f"%{search_query}%"),
                Template.tags.contains([search_query])
            )
            query = query.where(search_filter)
        
        # Apply access control
        access_filter = or_(
            Template.created_by == user_id,
            Template.is_public == True
        )
        query = query.where(access_filter)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(desc(Template.updated_at)).offset((page - 1) * size).limit(size)
        
        # Execute query
        result = await db.execute(query)
        templates = result.scalars().all()
        
        # Convert to response format
        template_responses = [TemplateResponse.from_orm(template) for template in templates]
        
        return {
            "templates": template_responses,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
    
    except Exception as e:
        logger.error(f"Failed to list templates: {e}")
        raise handle_internal_error(f"Failed to list templates: {str(e)}")


async def use_template(
    template_id: str,
    user_id: str,
    variables: Dict[str, Any],
    db: AsyncSession
) -> Dict[str, Any]:
    """Use a template to create a document."""
    try:
        # Get template
        template = await get_template(template_id, user_id, db)
        
        # Validate variables
        template_variables = template.variables or []
        for var in template_variables:
            if var.get("required", False) and var["name"] not in variables:
                raise handle_validation_error(
                    ValueError(f"Required variable '{var['name']}' is missing")
                )
        
        # Process template content with variables
        processed_content = process_template_content(template.content, variables)
        
        # Record template usage
        usage = TemplateUsage(
            template_id=template_id,
            used_by=user_id,
            variables_used=variables,
            created_at=datetime.utcnow()
        )
        
        db.add(usage)
        await db.commit()
        
        # Update template usage count
        template.usage_count = (template.usage_count or 0) + 1
        await db.commit()
        
        logger.info(f"Template used: {template_id} by user {user_id}")
        
        return {
            "template_id": template_id,
            "processed_content": processed_content,
            "variables_used": variables,
            "message": "Template processed successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to use template: {e}")
        raise handle_internal_error(f"Failed to use template: {str(e)}")


async def get_template_categories(
    db: AsyncSession
) -> List[TemplateCategoryResponse]:
    """Get all template categories."""
    try:
        query = select(TemplateCategory).where(TemplateCategory.is_active == True)
        result = await db.execute(query)
        categories = result.scalars().all()
        
        return [TemplateCategoryResponse.from_orm(category) for category in categories]
    
    except Exception as e:
        logger.error(f"Failed to get template categories: {e}")
        raise handle_internal_error(f"Failed to get template categories: {str(e)}")


async def get_template_usage_stats(
    template_id: str,
    user_id: str,
    db: AsyncSession
) -> Dict[str, Any]:
    """Get template usage statistics."""
    try:
        # Check template access
        template = await get_template(template_id, user_id, db)
        
        # Get usage statistics
        usage_query = select(TemplateUsage).where(TemplateUsage.template_id == template_id)
        usage_result = await db.execute(usage_query)
        usages = usage_result.scalars().all()
        
        # Calculate stats
        total_uses = len(usages)
        unique_users = len(set(usage.used_by for usage in usages))
        
        # Usage by date
        usage_by_date = {}
        for usage in usages:
            date = usage.created_at.date()
            if date not in usage_by_date:
                usage_by_date[date] = 0
            usage_by_date[date] += 1
        
        # Most common variables
        variable_usage = {}
        for usage in usages:
            for var_name, var_value in usage.variables_used.items():
                if var_name not in variable_usage:
                    variable_usage[var_name] = {}
                if var_value not in variable_usage[var_name]:
                    variable_usage[var_name][var_value] = 0
                variable_usage[var_name][var_value] += 1
        
        return {
            "template_id": template_id,
            "total_uses": total_uses,
            "unique_users": unique_users,
            "usage_by_date": usage_by_date,
            "variable_usage": variable_usage,
            "recent_uses": [
                {
                    "used_by": usage.used_by,
                    "created_at": usage.created_at.isoformat(),
                    "variables_used": usage.variables_used
                }
                for usage in usages[-10:]  # Last 10 uses
            ]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get template usage stats: {e}")
        raise handle_internal_error(f"Failed to get template usage stats: {str(e)}")


# Helper functions
def process_template_content(content: str, variables: Dict[str, Any]) -> str:
    """Process template content with variables."""
    processed_content = content
    
    for var_name, var_value in variables.items():
        placeholder = f"{{{{{var_name}}}}}"
        processed_content = processed_content.replace(placeholder, str(var_value))
    
    return processed_content


async def check_template_access(
    template: Template,
    user_id: str,
    db: AsyncSession
) -> bool:
    """Check if user has access to template."""
    # Creator has access
    if template.created_by == user_id:
        return True
    
    # Public templates
    if template.is_public:
        return True
    
    return False


async def check_template_edit_permission(
    template: Template,
    user_id: str,
    db: AsyncSession
) -> bool:
    """Check if user can edit template."""
    # Only creator can edit
    if template.created_by == user_id:
        return True
    
    return False


async def get_featured_templates(
    limit: int = 10,
    db: AsyncSession = None
) -> List[TemplateResponse]:
    """Get featured templates."""
    try:
        query = select(Template).where(
            and_(
                Template.is_featured == True,
                Template.is_public == True,
                Template.is_deleted == False
            )
        ).order_by(desc(Template.usage_count)).limit(limit)
        
        result = await db.execute(query)
        templates = result.scalars().all()
        
        return [TemplateResponse.from_orm(template) for template in templates]
    
    except Exception as e:
        logger.error(f"Failed to get featured templates: {e}")
        return []


async def search_templates(
    query: str,
    user_id: str,
    page: int = 1,
    size: int = 20,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """Search templates by name, description, or content."""
    try:
        # Build search query
        search_filter = or_(
            Template.name.ilike(f"%{query}%"),
            Template.description.ilike(f"%{query}%"),
            Template.content.ilike(f"%{query}%"),
            Template.tags.contains([query])
        )
        
        base_query = select(Template).where(
            and_(
                search_filter,
                Template.is_deleted == False,
                or_(
                    Template.created_by == user_id,
                    Template.is_public == True
                )
            )
        )
        
        # Get total count
        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # Apply pagination and ordering
        base_query = base_query.order_by(desc(Template.usage_count)).offset((page - 1) * size).limit(size)
        
        result = await db.execute(base_query)
        templates = result.scalars().all()
        
        template_responses = [TemplateResponse.from_orm(template) for template in templates]
        
        return {
            "templates": template_responses,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size,
            "query": query
        }
    
    except Exception as e:
        logger.error(f"Failed to search templates: {e}")
        raise handle_internal_error(f"Failed to search templates: {str(e)}")




