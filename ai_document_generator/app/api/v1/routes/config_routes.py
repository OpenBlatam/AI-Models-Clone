"""
Configuration routes following functional patterns
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user
from app.core.errors import handle_validation_error, handle_internal_error
from app.models.user import User
from app.schemas.config import (
    ConfigCreate, ConfigResponse, ConfigUpdate, ConfigListResponse,
    ConfigSearchRequest, ConfigValidationResponse, ConfigExportRequest,
    ConfigExportResponse, ConfigImportRequest, ConfigImportResponse,
    ConfigEnvironmentListResponse, ConfigStatsResponse, ConfigCacheRequest,
    ConfigCacheResponse, ConfigHistoryResponse
)
from app.services.config_service import (
    get_config, set_config, delete_config, list_configs, get_config_history,
    export_configs, import_configs, validate_configs, get_environments,
    get_config_stats, reload_config_cache
)

router = APIRouter()


@router.get("/{key}", response_model=Any)
async def get_config_value(
    key: str,
    environment: str = Query("default", description="Configuration environment"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get configuration value."""
    try:
        value = await get_config(key, environment, user.id, db)
        if value is None:
            raise HTTPException(status_code=404, detail="Configuration not found")
        return {"key": key, "value": value, "environment": environment}
    
    except HTTPException:
        raise
    except Exception as e:
        raise handle_internal_error(f"Failed to get config: {str(e)}")


@router.post("/", response_model=ConfigResponse)
async def create_config(
    config_data: ConfigCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ConfigResponse:
    """Create or update configuration."""
    try:
        return await set_config(
            key=config_data.key,
            value=config_data.value,
            value_type=config_data.value_type,
            environment=config_data.environment,
            description=config_data.description,
            is_sensitive=config_data.is_sensitive,
            user_id=user.id,
            db=db
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise handle_internal_error(f"Failed to create config: {str(e)}")


@router.put("/{key}", response_model=ConfigResponse)
async def update_config(
    key: str,
    config_data: ConfigUpdate,
    environment: str = Query("default", description="Configuration environment"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ConfigResponse:
    """Update configuration."""
    try:
        # Get existing config to preserve unchanged fields
        existing_value = await get_config(key, environment, user.id, db)
        if existing_value is None:
            raise HTTPException(status_code=404, detail="Configuration not found")
        
        # Update only provided fields
        update_data = config_data.dict(exclude_unset=True)
        
        return await set_config(
            key=key,
            value=update_data.get("value", existing_value),
            value_type=update_data.get("value_type", "string"),
            environment=environment,
            description=update_data.get("description"),
            is_sensitive=update_data.get("is_sensitive", False),
            user_id=user.id,
            db=db
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise handle_internal_error(f"Failed to update config: {str(e)}")


@router.delete("/{key}")
async def delete_config_value(
    key: str,
    environment: str = Query("default", description="Configuration environment"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Delete configuration."""
    try:
        return await delete_config(key, environment, user.id, db)
    
    except HTTPException:
        raise
    except Exception as e:
        raise handle_internal_error(f"Failed to delete config: {str(e)}")


@router.get("/", response_model=ConfigListResponse)
async def list_configurations(
    environment: Optional[str] = Query(None, description="Filter by environment"),
    search: Optional[str] = Query(None, description="Search in key or description"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Page size"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ConfigListResponse:
    """List configurations with filtering and pagination."""
    try:
        result = await list_configs(environment, search, page, size, db)
        return ConfigListResponse(**result)
    
    except Exception as e:
        raise handle_internal_error(f"Failed to list configs: {str(e)}")


@router.get("/{key}/history", response_model=ConfigHistoryResponse)
async def get_configuration_history(
    key: str,
    environment: str = Query("default", description="Configuration environment"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ConfigHistoryResponse:
    """Get configuration history."""
    try:
        result = await get_config_history(key, environment, page, size, db)
        return ConfigHistoryResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        raise handle_internal_error(f"Failed to get config history: {str(e)}")


@router.post("/export", response_model=ConfigExportResponse)
async def export_configurations(
    export_request: ConfigExportRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ConfigExportResponse:
    """Export configurations."""
    try:
        result = await export_configs(
            environment=export_request.environment,
            format=export_request.format,
            include_sensitive=export_request.include_sensitive,
            db=db
        )
        
        return ConfigExportResponse(
            export_filename=result["export_filename"],
            export_path=result["export_path"],
            total_configs=result["total_configs"],
            format=result["format"],
            download_url=f"/api/v1/configs/download/{result['export_filename']}",
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
    
    except Exception as e:
        raise handle_internal_error(f"Failed to export configs: {str(e)}")


@router.post("/import", response_model=ConfigImportResponse)
async def import_configurations(
    import_request: ConfigImportRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ConfigImportResponse:
    """Import configurations."""
    try:
        result = await import_configs(
            config_data=import_request.config_data,
            environment=import_request.environment,
            overwrite=import_request.overwrite,
            user_id=user.id,
            db=db
        )
        
        return ConfigImportResponse(**result)
    
    except Exception as e:
        raise handle_internal_error(f"Failed to import configs: {str(e)}")


@router.post("/validate", response_model=ConfigValidationResponse)
async def validate_configurations(
    environment: str = Query("default", description="Configuration environment"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ConfigValidationResponse:
    """Validate all configurations."""
    try:
        return await validate_configs(environment, db)
    
    except Exception as e:
        raise handle_internal_error(f"Failed to validate configs: {str(e)}")


@router.get("/environments/", response_model=ConfigEnvironmentListResponse)
async def list_environments(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ConfigEnvironmentListResponse:
    """List all environments."""
    try:
        environments = await get_environments(db)
        return ConfigEnvironmentListResponse(
            environments=environments,
            total=len(environments)
        )
    
    except Exception as e:
        raise handle_internal_error(f"Failed to list environments: {str(e)}")


@router.get("/stats/", response_model=ConfigStatsResponse)
async def get_configuration_stats(
    environment: Optional[str] = Query(None, description="Filter by environment"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ConfigStatsResponse:
    """Get configuration statistics."""
    try:
        stats = await get_config_stats(environment, db)
        return ConfigStatsResponse(**stats)
    
    except Exception as e:
        raise handle_internal_error(f"Failed to get config stats: {str(e)}")


@router.post("/cache/reload", response_model=ConfigCacheResponse)
async def reload_configuration_cache(
    cache_request: ConfigCacheRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ConfigCacheResponse:
    """Reload configuration cache."""
    try:
        result = await reload_config_cache(cache_request.environment)
        return ConfigCacheResponse(
            message=result["message"],
            environment=cache_request.environment
        )
    
    except Exception as e:
        raise handle_internal_error(f"Failed to reload config cache: {str(e)}")


@router.get("/download/{filename}")
async def download_configuration_export(
    filename: str,
    user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """Download configuration export file."""
    try:
        # Validate filename
        if not filename.endswith(('.json', '.yaml', '.yml')):
            raise HTTPException(status_code=400, detail="Invalid file format")
        
        # Check if file exists
        file_path = os.path.join("exports", filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Export file not found")
        
        # Check file age (expire after 24 hours)
        file_age = time.time() - os.path.getmtime(file_path)
        if file_age > 86400:  # 24 hours
            os.remove(file_path)
            raise HTTPException(status_code=410, detail="Export file has expired")
        
        return {
            "download_url": f"/api/v1/configs/download/{filename}",
            "filename": filename,
            "expires_at": datetime.fromtimestamp(os.path.getmtime(file_path) + 86400).isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise handle_internal_error(f"Failed to download export: {str(e)}")


@router.post("/bulk", response_model=Dict[str, Any])
async def bulk_update_configurations(
    configs: List[Dict[str, Any]],
    environment: str = Query("default", description="Configuration environment"),
    overwrite: bool = Query(False, description="Overwrite existing configurations"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Bulk update configurations."""
    try:
        updated_count = 0
        created_count = 0
        failed_count = 0
        errors = []
        
        for config_data in configs:
            try:
                # Validate required fields
                if "key" not in config_data or "value" not in config_data:
                    errors.append(f"Missing required fields: {config_data}")
                    failed_count += 1
                    continue
                
                # Check if config exists
                existing_value = await get_config(config_data["key"], environment, user.id, db)
                
                if existing_value is not None and not overwrite:
                    failed_count += 1
                    continue
                
                # Set config
                await set_config(
                    key=config_data["key"],
                    value=config_data["value"],
                    value_type=config_data.get("value_type", "string"),
                    environment=environment,
                    description=config_data.get("description"),
                    is_sensitive=config_data.get("is_sensitive", False),
                    user_id=user.id,
                    db=db
                )
                
                if existing_value is not None:
                    updated_count += 1
                else:
                    created_count += 1
                
            except Exception as e:
                errors.append(f"Failed to update {config_data.get('key', 'unknown')}: {str(e)}")
                failed_count += 1
        
        return {
            "updated_count": updated_count,
            "created_count": created_count,
            "failed_count": failed_count,
            "errors": errors,
            "total_processed": len(configs)
        }
    
    except Exception as e:
        raise handle_internal_error(f"Failed to bulk update configs: {str(e)}")


@router.get("/search/", response_model=ConfigListResponse)
async def search_configurations(
    search_request: ConfigSearchRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ConfigListResponse:
    """Search configurations with advanced filtering."""
    try:
        result = await list_configs(
            environment=search_request.environment,
            search=search_request.search,
            page=search_request.page,
            size=search_request.size,
            db=db
        )
        return ConfigListResponse(**result)
    
    except Exception as e:
        raise handle_internal_error(f"Failed to search configs: {str(e)}")


@router.get("/health/", response_model=Dict[str, Any])
async def configuration_health_check(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Configuration system health check."""
    try:
        # Check database connectivity
        db_healthy = True
        try:
            await db.execute(text("SELECT 1"))
        except Exception:
            db_healthy = False
        
        # Check cache status
        from app.services.config_service import _config_cache
        cache_size = len(_config_cache)
        
        # Get basic stats
        stats = await get_config_stats(db=db)
        
        return {
            "status": "healthy" if db_healthy else "unhealthy",
            "database_healthy": db_healthy,
            "cache_size": cache_size,
            "total_configs": stats.get("total_configs", 0),
            "environments": len(stats.get("environment_stats", {})),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }




