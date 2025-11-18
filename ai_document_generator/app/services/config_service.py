"""
Configuration service following functional patterns
"""
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, text
from sqlalchemy.orm import selectinload
import uuid
import json
import yaml
import os
import asyncio
from pathlib import Path

from app.core.logging import get_logger
from app.core.errors import handle_validation_error, handle_internal_error, handle_not_found_error
from app.models.config import Config, ConfigVersion, ConfigEnvironment
from app.schemas.config import (
    ConfigCreate, ConfigResponse, ConfigUpdate, ConfigVersionResponse,
    ConfigEnvironmentResponse, ConfigSearchRequest, ConfigValidationResponse
)
from app.utils.validators import validate_config_key, validate_config_value
from app.utils.helpers import generate_config_hash, parse_config_value
from app.utils.cache import cache_config_data, get_cached_config_data, invalidate_config_cache

logger = get_logger(__name__)

# Configuration cache
_config_cache: Dict[str, Any] = {}
_config_cache_ttl: Dict[str, datetime] = {}
CACHE_TTL_SECONDS = 300  # 5 minutes


async def get_config(
    key: str,
    environment: str = "default",
    user_id: Optional[str] = None,
    db: AsyncSession = None
) -> Any:
    """Get configuration value with caching."""
    try:
        cache_key = f"{environment}:{key}"
        
        # Check cache first
        if cache_key in _config_cache:
            if datetime.utcnow() < _config_cache_ttl.get(cache_key, datetime.min):
                return _config_cache[cache_key]
            else:
                # Cache expired, remove it
                _config_cache.pop(cache_key, None)
                _config_cache_ttl.pop(cache_key, None)
        
        # Get from database
        query = select(Config).where(
            and_(
                Config.key == key,
                Config.environment == environment,
                Config.is_active == True
            )
        ).order_by(desc(Config.created_at))
        
        result = await db.execute(query)
        config = result.scalar_one_or_none()
        
        if not config:
            # Try to get default value
            default_config = await get_default_config(key, db)
            if default_config:
                value = parse_config_value(default_config.value, default_config.value_type)
                # Cache default value
                _config_cache[cache_key] = value
                _config_cache_ttl[cache_key] = datetime.utcnow() + timedelta(seconds=CACHE_TTL_SECONDS)
                return value
            
            # Return environment variable if available
            env_value = os.getenv(key.upper())
            if env_value:
                return parse_config_value(env_value, "string")
            
            return None
        
        # Parse and cache value
        value = parse_config_value(config.value, config.value_type)
        _config_cache[cache_key] = value
        _config_cache_ttl[cache_key] = datetime.utcnow() + timedelta(seconds=CACHE_TTL_SECONDS)
        
        # Log config access
        await log_config_access(key, environment, user_id, db)
        
        return value
    
    except Exception as e:
        logger.error(f"Failed to get config {key}: {e}")
        return None


async def set_config(
    key: str,
    value: Any,
    value_type: str = "string",
    environment: str = "default",
    description: Optional[str] = None,
    is_sensitive: bool = False,
    user_id: str = None,
    db: AsyncSession = None
) -> ConfigResponse:
    """Set configuration value."""
    try:
        # Validate config key
        key_validation = validate_config_key(key)
        if not key_validation["is_valid"]:
            raise handle_validation_error(
                ValueError(f"Invalid config key: {', '.join(key_validation['errors'])}")
            )
        
        # Validate config value
        value_validation = validate_config_value(value, value_type)
        if not value_validation["is_valid"]:
            raise handle_validation_error(
                ValueError(f"Invalid config value: {', '.join(value_validation['errors'])}")
            )
        
        # Serialize value based on type
        serialized_value = serialize_config_value(value, value_type)
        
        # Deactivate existing config
        existing_query = select(Config).where(
            and_(
                Config.key == key,
                Config.environment == environment,
                Config.is_active == True
            )
        )
        existing_result = await db.execute(existing_query)
        existing_configs = existing_result.scalars().all()
        
        for existing_config in existing_configs:
            existing_config.is_active = False
            existing_config.updated_at = datetime.utcnow()
            existing_config.updated_by = user_id
        
        # Create new config
        config = Config(
            key=key,
            value=serialized_value,
            value_type=value_type,
            environment=environment,
            description=description,
            is_sensitive=is_sensitive,
            created_by=user_id,
            created_at=datetime.utcnow()
        )
        
        db.add(config)
        await db.commit()
        await db.refresh(config)
        
        # Create version record
        version = ConfigVersion(
            config_id=config.id,
            value=serialized_value,
            value_type=value_type,
            created_by=user_id,
            created_at=datetime.utcnow()
        )
        
        db.add(version)
        await db.commit()
        
        # Invalidate cache
        cache_key = f"{environment}:{key}"
        _config_cache.pop(cache_key, None)
        _config_cache_ttl.pop(cache_key, None)
        invalidate_config_cache(cache_key)
        
        # Log config change
        await log_config_change(key, environment, "set", user_id, db)
        
        logger.info(f"Config set: {key} = {value} (type: {value_type})")
        
        return ConfigResponse.from_orm(config)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to set config: {e}")
        raise handle_internal_error(f"Failed to set config: {str(e)}")


async def delete_config(
    key: str,
    environment: str = "default",
    user_id: str = None,
    db: AsyncSession = None
) -> Dict[str, str]:
    """Delete configuration."""
    try:
        # Find active config
        query = select(Config).where(
            and_(
                Config.key == key,
                Config.environment == environment,
                Config.is_active == True
            )
        )
        
        result = await db.execute(query)
        config = result.scalar_one_or_none()
        
        if not config:
            raise handle_not_found_error("Config", f"{key}@{environment}")
        
        # Deactivate config
        config.is_active = False
        config.updated_at = datetime.utcnow()
        config.updated_by = user_id
        
        await db.commit()
        
        # Invalidate cache
        cache_key = f"{environment}:{key}"
        _config_cache.pop(cache_key, None)
        _config_cache_ttl.pop(cache_key, None)
        invalidate_config_cache(cache_key)
        
        # Log config change
        await log_config_change(key, environment, "delete", user_id, db)
        
        logger.info(f"Config deleted: {key}@{environment}")
        
        return {"message": "Configuration deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to delete config: {e}")
        raise handle_internal_error(f"Failed to delete config: {str(e)}")


async def list_configs(
    environment: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    size: int = 50,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """List configurations with filtering and pagination."""
    try:
        # Build query
        query = select(Config).where(Config.is_active == True)
        
        # Apply filters
        if environment:
            query = query.where(Config.environment == environment)
        
        if search:
            search_filter = or_(
                Config.key.ilike(f"%{search}%"),
                Config.description.ilike(f"%{search}%")
            )
            query = query.where(search_filter)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(Config.key, Config.environment).offset((page - 1) * size).limit(size)
        
        # Execute query
        result = await db.execute(query)
        configs = result.scalars().all()
        
        # Convert to response format
        config_responses = [ConfigResponse.from_orm(config) for config in configs]
        
        return {
            "configs": config_responses,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
    
    except Exception as e:
        logger.error(f"Failed to list configs: {e}")
        raise handle_internal_error(f"Failed to list configs: {str(e)}")


async def get_config_history(
    key: str,
    environment: str = "default",
    page: int = 1,
    size: int = 20,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """Get configuration history."""
    try:
        # Get config
        config_query = select(Config).where(
            and_(
                Config.key == key,
                Config.environment == environment
            )
        ).order_by(desc(Config.created_at))
        
        config_result = await db.execute(config_query)
        configs = config_result.scalars().all()
        
        if not configs:
            raise handle_not_found_error("Config", f"{key}@{environment}")
        
        # Get versions for all configs
        config_ids = [config.id for config in configs]
        
        versions_query = select(ConfigVersion).where(
            ConfigVersion.config_id.in_(config_ids)
        ).order_by(desc(ConfigVersion.created_at))
        
        versions_result = await db.execute(versions_query)
        versions = versions_result.scalars().all()
        
        # Convert to response format
        version_responses = [ConfigVersionResponse.from_orm(version) for version in versions]
        
        return {
            "config_key": key,
            "environment": environment,
            "versions": version_responses,
            "total": len(version_responses)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get config history: {e}")
        raise handle_internal_error(f"Failed to get config history: {str(e)}")


async def export_configs(
    environment: str = "default",
    format: str = "json",
    include_sensitive: bool = False,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """Export configurations."""
    try:
        # Get configs
        query = select(Config).where(
            and_(
                Config.environment == environment,
                Config.is_active == True
            )
        )
        
        if not include_sensitive:
            query = query.where(Config.is_sensitive == False)
        
        result = await db.execute(query)
        configs = result.scalars().all()
        
        # Convert to export format
        export_data = {}
        for config in configs:
            value = parse_config_value(config.value, config.value_type)
            if config.is_sensitive and not include_sensitive:
                value = "***REDACTED***"
            export_data[config.key] = value
        
        # Generate export file
        export_filename = f"config_{environment}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{format}"
        export_path = os.path.join("exports", export_filename)
        
        # Ensure export directory exists
        os.makedirs("exports", exist_ok=True)
        
        # Write export file
        if format == "json":
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
        elif format == "yaml":
            with open(export_path, 'w') as f:
                yaml.dump(export_data, f, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported export format: {format}")
        
        return {
            "export_filename": export_filename,
            "export_path": export_path,
            "total_configs": len(configs),
            "format": format
        }
    
    except Exception as e:
        logger.error(f"Failed to export configs: {e}")
        raise handle_internal_error(f"Failed to export configs: {str(e)}")


async def import_configs(
    config_data: Dict[str, Any],
    environment: str = "default",
    overwrite: bool = False,
    user_id: str = None,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """Import configurations."""
    try:
        imported_count = 0
        skipped_count = 0
        errors = []
        
        for key, value in config_data.items():
            try:
                # Check if config exists
                existing_query = select(Config).where(
                    and_(
                        Config.key == key,
                        Config.environment == environment,
                        Config.is_active == True
                    )
                )
                
                existing_result = await db.execute(existing_query)
                existing_config = existing_result.scalar_one_or_none()
                
                if existing_config and not overwrite:
                    skipped_count += 1
                    continue
                
                # Determine value type
                value_type = determine_value_type(value)
                
                # Set config
                await set_config(
                    key=key,
                    value=value,
                    value_type=value_type,
                    environment=environment,
                    user_id=user_id,
                    db=db
                )
                
                imported_count += 1
                
            except Exception as e:
                errors.append(f"Failed to import {key}: {str(e)}")
        
        return {
            "imported_count": imported_count,
            "skipped_count": skipped_count,
            "errors": errors,
            "total_processed": len(config_data)
        }
    
    except Exception as e:
        logger.error(f"Failed to import configs: {e}")
        raise handle_internal_error(f"Failed to import configs: {str(e)}")


async def validate_configs(
    environment: str = "default",
    db: AsyncSession = None
) -> ConfigValidationResponse:
    """Validate all configurations."""
    try:
        # Get all configs
        query = select(Config).where(
            and_(
                Config.environment == environment,
                Config.is_active == True
            )
        )
        
        result = await db.execute(query)
        configs = result.scalars().all()
        
        validation_results = {
            "valid": [],
            "invalid": [],
            "warnings": []
        }
        
        for config in configs:
            try:
                # Validate value
                value_validation = validate_config_value(config.value, config.value_type)
                
                if value_validation["is_valid"]:
                    validation_results["valid"].append({
                        "key": config.key,
                        "value_type": config.value_type,
                        "message": "Valid"
                    })
                else:
                    validation_results["invalid"].append({
                        "key": config.key,
                        "value_type": config.value_type,
                        "errors": value_validation["errors"]
                    })
                
                # Check for warnings
                if config.is_sensitive and not config.description:
                    validation_results["warnings"].append({
                        "key": config.key,
                        "message": "Sensitive config without description"
                    })
                
            except Exception as e:
                validation_results["invalid"].append({
                    "key": config.key,
                    "errors": [str(e)]
                })
        
        is_valid = len(validation_results["invalid"]) == 0
        
        return ConfigValidationResponse(
            is_valid=is_valid,
            valid_count=len(validation_results["valid"]),
            invalid_count=len(validation_results["invalid"]),
            warning_count=len(validation_results["warnings"]),
            results=validation_results,
            environment=environment
        )
    
    except Exception as e:
        logger.error(f"Failed to validate configs: {e}")
        raise handle_internal_error(f"Failed to validate configs: {str(e)}")


async def get_environments(
    db: AsyncSession = None
) -> List[ConfigEnvironmentResponse]:
    """Get all environments."""
    try:
        # Get unique environments
        query = select(Config.environment, func.count(Config.id).label('config_count')).where(
            Config.is_active == True
        ).group_by(Config.environment)
        
        result = await db.execute(query)
        environments = result.fetchall()
        
        environment_responses = []
        for env_name, config_count in environments:
            # Get last updated
            last_updated_query = select(func.max(Config.updated_at)).where(
                and_(
                    Config.environment == env_name,
                    Config.is_active == True
                )
            )
            last_updated_result = await db.execute(last_updated_query)
            last_updated = last_updated_result.scalar()
            
            environment_responses.append(ConfigEnvironmentResponse(
                name=env_name,
                config_count=config_count,
                last_updated=last_updated
            ))
        
        return environment_responses
    
    except Exception as e:
        logger.error(f"Failed to get environments: {e}")
        raise handle_internal_error(f"Failed to get environments: {str(e)}")


# Helper functions
async def get_default_config(
    key: str,
    db: AsyncSession
) -> Optional[Config]:
    """Get default configuration."""
    try:
        query = select(Config).where(
            and_(
                Config.key == key,
                Config.environment == "default",
                Config.is_active == True
            )
        )
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    except Exception:
        return None


def serialize_config_value(
    value: Any,
    value_type: str
) -> str:
    """Serialize configuration value."""
    if value_type == "json":
        return json.dumps(value)
    elif value_type == "yaml":
        return yaml.dump(value, default_flow_style=False)
    elif value_type == "boolean":
        return str(bool(value)).lower()
    else:
        return str(value)


def determine_value_type(
    value: Any
) -> str:
    """Determine configuration value type."""
    if isinstance(value, bool):
        return "boolean"
    elif isinstance(value, int):
        return "integer"
    elif isinstance(value, float):
        return "float"
    elif isinstance(value, (dict, list)):
        return "json"
    else:
        return "string"


async def log_config_access(
    key: str,
    environment: str,
    user_id: Optional[str],
    db: AsyncSession
) -> None:
    """Log configuration access."""
    try:
        # This would implement actual logging
        logger.debug(f"Config accessed: {key}@{environment} by {user_id}")
    except Exception:
        pass


async def log_config_change(
    key: str,
    environment: str,
    action: str,
    user_id: Optional[str],
    db: AsyncSession
) -> None:
    """Log configuration change."""
    try:
        # This would implement actual logging
        logger.info(f"Config {action}: {key}@{environment} by {user_id}")
    except Exception:
        pass


async def reload_config_cache(
    environment: Optional[str] = None
) -> Dict[str, str]:
    """Reload configuration cache."""
    try:
        if environment:
            # Clear specific environment cache
            keys_to_remove = [key for key in _config_cache.keys() if key.startswith(f"{environment}:")]
            for key in keys_to_remove:
                _config_cache.pop(key, None)
                _config_cache_ttl.pop(key, None)
        else:
            # Clear all cache
            _config_cache.clear()
            _config_cache_ttl.clear()
        
        return {"message": "Configuration cache reloaded successfully"}
    
    except Exception as e:
        logger.error(f"Failed to reload config cache: {e}")
        return {"error": str(e)}


async def get_config_stats(
    environment: Optional[str] = None,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """Get configuration statistics."""
    try:
        # Build base query
        base_query = select(Config).where(Config.is_active == True)
        
        if environment:
            base_query = base_query.where(Config.environment == environment)
        
        # Get total count
        total_query = select(func.count()).select_from(base_query.subquery())
        total_result = await db.execute(total_query)
        total_configs = total_result.scalar()
        
        # Get configs by type
        type_query = select(
            Config.value_type,
            func.count(Config.id).label('count')
        ).select_from(base_query.subquery()).group_by(Config.value_type)
        
        type_result = await db.execute(type_query)
        type_stats = {row[0]: row[1] for row in type_result.fetchall()}
        
        # Get configs by environment
        env_query = select(
            Config.environment,
            func.count(Config.id).label('count')
        ).select_from(base_query.subquery()).group_by(Config.environment)
        
        env_result = await db.execute(env_query)
        env_stats = {row[0]: row[1] for row in env_result.fetchall()}
        
        # Get sensitive configs count
        sensitive_query = select(func.count()).select_from(base_query.subquery()).where(
            Config.is_sensitive == True
        )
        sensitive_result = await db.execute(sensitive_query)
        sensitive_count = sensitive_result.scalar()
        
        return {
            "total_configs": total_configs,
            "type_stats": type_stats,
            "environment_stats": env_stats,
            "sensitive_count": sensitive_count,
            "cache_size": len(_config_cache)
        }
    
    except Exception as e:
        logger.error(f"Failed to get config stats: {e}")
        return {}




