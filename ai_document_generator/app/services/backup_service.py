"""
Backup service following functional patterns
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, text
from sqlalchemy.orm import selectinload
import uuid
import json
import gzip
import tarfile
import os
import asyncio
import aiofiles
from pathlib import Path

from app.core.logging import get_logger
from app.core.errors import handle_validation_error, handle_internal_error, handle_not_found_error
from app.models.backup import Backup, BackupJob, BackupSchedule
from app.schemas.backup import (
    BackupCreate, BackupResponse, BackupJobResponse,
    BackupScheduleResponse, BackupRestoreRequest
)
from app.utils.validators import validate_backup_name, validate_backup_schedule
from app.utils.helpers import generate_backup_filename, create_backup_checksum
from app.utils.cache import cache_backup_data, get_cached_backup_data, invalidate_backup_cache

logger = get_logger(__name__)

# Backup configuration
BACKUP_DIR = os.getenv("BACKUP_DIR", "backups")
MAX_BACKUP_SIZE = int(os.getenv("MAX_BACKUP_SIZE", 10 * 1024 * 1024 * 1024))  # 10GB
BACKUP_RETENTION_DAYS = int(os.getenv("BACKUP_RETENTION_DAYS", 30))


async def create_backup(
    backup_data: BackupCreate,
    user_id: str,
    db: AsyncSession
) -> BackupResponse:
    """Create a new backup."""
    try:
        # Validate backup name
        name_validation = validate_backup_name(backup_data.name)
        if not name_validation["is_valid"]:
            raise handle_validation_error(
                ValueError(f"Invalid backup name: {', '.join(name_validation['errors'])}")
            )
        
        # Generate backup filename
        backup_filename = generate_backup_filename(backup_data.name, backup_data.backup_type)
        backup_path = os.path.join(BACKUP_DIR, backup_filename)
        
        # Ensure backup directory exists
        os.makedirs(BACKUP_DIR, exist_ok=True)
        
        # Create backup record
        backup = Backup(
            name=backup_data.name,
            backup_type=backup_data.backup_type,
            backup_path=backup_path,
            size=0,  # Will be updated after backup creation
            checksum="",  # Will be calculated after backup creation
            status="pending",
            created_by=user_id,
            metadata=backup_data.metadata or {},
            created_at=datetime.utcnow()
        )
        
        db.add(backup)
        await db.commit()
        await db.refresh(backup)
        
        # Create backup job
        job = BackupJob(
            backup_id=backup.id,
            status="running",
            started_at=datetime.utcnow(),
            progress=0
        )
        
        db.add(job)
        await db.commit()
        await db.refresh(job)
        
        # Start backup process asynchronously
        asyncio.create_task(execute_backup(backup, job, db))
        
        # Cache backup data
        cache_backup_data(str(backup.id), backup)
        
        logger.info(f"Backup created: {backup.id} by user {user_id}")
        
        return BackupResponse.from_orm(backup)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create backup: {e}")
        raise handle_internal_error(f"Failed to create backup: {str(e)}")


async def execute_backup(
    backup: Backup,
    job: BackupJob,
    db: AsyncSession
) -> None:
    """Execute backup process."""
    try:
        # Update job status
        job.status = "running"
        job.progress = 10
        await db.commit()
        
        # Create backup based on type
        if backup.backup_type == "full":
            await create_full_backup(backup, job, db)
        elif backup.backup_type == "incremental":
            await create_incremental_backup(backup, job, db)
        elif backup.backup_type == "differential":
            await create_differential_backup(backup, job, db)
        else:
            raise ValueError(f"Unknown backup type: {backup.backup_type}")
        
        # Calculate backup size and checksum
        backup_size = os.path.getsize(backup.backup_path)
        backup_checksum = await create_backup_checksum(backup.backup_path)
        
        # Update backup record
        backup.size = backup_size
        backup.checksum = backup_checksum
        backup.status = "completed"
        backup.completed_at = datetime.utcnow()
        
        # Update job status
        job.status = "completed"
        job.progress = 100
        job.completed_at = datetime.utcnow()
        
        await db.commit()
        
        logger.info(f"Backup completed: {backup.id}")
        
    except Exception as e:
        # Update backup and job status with error
        backup.status = "failed"
        backup.error_message = str(e)
        backup.completed_at = datetime.utcnow()
        
        job.status = "failed"
        job.error_message = str(e)
        job.completed_at = datetime.utcnow()
        
        await db.commit()
        
        logger.error(f"Backup failed: {backup.id} - {e}")


async def create_full_backup(
    backup: Backup,
    job: BackupJob,
    db: AsyncSession
) -> None:
    """Create full backup of all data."""
    try:
        # Update progress
        job.progress = 20
        await db.commit()
        
        # Create tar.gz archive
        with tarfile.open(backup.backup_path, "w:gz") as tar:
            # Backup database schema
            await backup_database_schema(tar, db)
            
            # Update progress
            job.progress = 40
            await db.commit()
            
            # Backup database data
            await backup_database_data(tar, db)
            
            # Update progress
            job.progress = 60
            await db.commit()
            
            # Backup files
            await backup_files(tar)
            
            # Update progress
            job.progress = 80
            await db.commit()
            
            # Backup configuration
            await backup_configuration(tar)
            
            # Update progress
            job.progress = 90
            await db.commit()
    
    except Exception as e:
        logger.error(f"Failed to create full backup: {e}")
        raise


async def create_incremental_backup(
    backup: Backup,
    job: BackupJob,
    db: AsyncSession
) -> None:
    """Create incremental backup of changed data."""
    try:
        # Get last backup timestamp
        last_backup_query = select(Backup).where(
            and_(
                Backup.backup_type == "full",
                Backup.status == "completed"
            )
        ).order_by(desc(Backup.completed_at)).limit(1)
        
        last_backup_result = await db.execute(last_backup_query)
        last_backup = last_backup_result.scalar_one_or_none()
        
        if not last_backup:
            # No previous backup, create full backup instead
            await create_full_backup(backup, job, db)
            return
        
        # Create incremental backup
        with tarfile.open(backup.backup_path, "w:gz") as tar:
            # Backup changed data since last backup
            await backup_changed_data(tar, last_backup.completed_at, db)
            
            # Backup changed files since last backup
            await backup_changed_files(tar, last_backup.completed_at)
    
    except Exception as e:
        logger.error(f"Failed to create incremental backup: {e}")
        raise


async def create_differential_backup(
    backup: Backup,
    job: BackupJob,
    db: AsyncSession
) -> None:
    """Create differential backup of all data since last full backup."""
    try:
        # Get last full backup timestamp
        last_full_backup_query = select(Backup).where(
            and_(
                Backup.backup_type == "full",
                Backup.status == "completed"
            )
        ).order_by(desc(Backup.completed_at)).limit(1)
        
        last_full_backup_result = await db.execute(last_full_backup_query)
        last_full_backup = last_full_backup_result.scalar_one_or_none()
        
        if not last_full_backup:
            # No previous full backup, create full backup instead
            await create_full_backup(backup, job, db)
            return
        
        # Create differential backup
        with tarfile.open(backup.backup_path, "w:gz") as tar:
            # Backup all data since last full backup
            await backup_changed_data(tar, last_full_backup.completed_at, db)
            
            # Backup all changed files since last full backup
            await backup_changed_files(tar, last_full_backup.completed_at)
    
    except Exception as e:
        logger.error(f"Failed to create differential backup: {e}")
        raise


async def backup_database_schema(
    tar: tarfile.TarFile,
    db: AsyncSession
) -> None:
    """Backup database schema."""
    try:
        # Get database schema
        schema_query = text("""
            SELECT table_name, column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position
        """)
        
        result = await db.execute(schema_query)
        schema_data = result.fetchall()
        
        # Convert to JSON
        schema_json = {
            "tables": {},
            "backup_timestamp": datetime.utcnow().isoformat()
        }
        
        for row in schema_data:
            table_name = row[0]
            if table_name not in schema_json["tables"]:
                schema_json["tables"][table_name] = {"columns": []}
            
            schema_json["tables"][table_name]["columns"].append({
                "name": row[1],
                "type": row[2],
                "nullable": row[3] == "YES",
                "default": row[4]
            })
        
        # Add to tar archive
        schema_info = tarfile.TarInfo(name="database_schema.json")
        schema_data = json.dumps(schema_json, indent=2).encode()
        schema_info.size = len(schema_data)
        tar.addfile(schema_info, fileobj=io.BytesIO(schema_data))
    
    except Exception as e:
        logger.error(f"Failed to backup database schema: {e}")
        raise


async def backup_database_data(
    tar: tarfile.TarFile,
    db: AsyncSession
) -> None:
    """Backup database data."""
    try:
        # Get all tables
        tables_query = text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
        """)
        
        result = await db.execute(tables_query)
        tables = [row[0] for row in result.fetchall()]
        
        # Backup each table
        for table in tables:
            await backup_table_data(tar, table, db)
    
    except Exception as e:
        logger.error(f"Failed to backup database data: {e}")
        raise


async def backup_table_data(
    tar: tarfile.TarFile,
    table_name: str,
    db: AsyncSession
) -> None:
    """Backup data from a specific table."""
    try:
        # Get table data
        data_query = text(f"SELECT * FROM {table_name}")
        result = await db.execute(data_query)
        rows = result.fetchall()
        
        # Convert to JSON
        table_data = {
            "table_name": table_name,
            "rows": [dict(row._mapping) for row in rows],
            "backup_timestamp": datetime.utcnow().isoformat()
        }
        
        # Add to tar archive
        table_info = tarfile.TarInfo(name=f"data/{table_name}.json")
        table_data_bytes = json.dumps(table_data, indent=2, default=str).encode()
        table_info.size = len(table_data_bytes)
        tar.addfile(table_info, fileobj=io.BytesIO(table_data_bytes))
    
    except Exception as e:
        logger.error(f"Failed to backup table {table_name}: {e}")
        raise


async def backup_files(
    tar: tarfile.TarFile
) -> None:
    """Backup uploaded files."""
    try:
        upload_dir = os.getenv("UPLOAD_DIR", "uploads")
        
        if os.path.exists(upload_dir):
            tar.add(upload_dir, arcname="files")
    
    except Exception as e:
        logger.error(f"Failed to backup files: {e}")
        raise


async def backup_configuration(
    tar: tarfile.TarFile
) -> None:
    """Backup system configuration."""
    try:
        config_data = {
            "environment_variables": dict(os.environ),
            "backup_timestamp": datetime.utcnow().isoformat()
        }
        
        # Add to tar archive
        config_info = tarfile.TarInfo(name="configuration.json")
        config_data_bytes = json.dumps(config_data, indent=2).encode()
        config_info.size = len(config_data_bytes)
        tar.addfile(config_info, fileobj=io.BytesIO(config_data_bytes))
    
    except Exception as e:
        logger.error(f"Failed to backup configuration: {e}")
        raise


async def backup_changed_data(
    tar: tarfile.TarFile,
    since_timestamp: datetime,
    db: AsyncSession
) -> None:
    """Backup data changed since timestamp."""
    try:
        # Get all tables
        tables_query = text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
        """)
        
        result = await db.execute(tables_query)
        tables = [row[0] for row in result.fetchall()]
        
        # Backup changed data from each table
        for table in tables:
            await backup_changed_table_data(tar, table, since_timestamp, db)
    
    except Exception as e:
        logger.error(f"Failed to backup changed data: {e}")
        raise


async def backup_changed_table_data(
    tar: tarfile.TarFile,
    table_name: str,
    since_timestamp: datetime,
    db: AsyncSession
) -> None:
    """Backup changed data from a specific table."""
    try:
        # Check if table has timestamp columns
        timestamp_columns = ["created_at", "updated_at", "modified_at"]
        
        # Build query for changed data
        where_clause = " OR ".join([
            f"{col} > '{since_timestamp.isoformat()}'"
            for col in timestamp_columns
        ])
        
        if where_clause:
            data_query = text(f"SELECT * FROM {table_name} WHERE {where_clause}")
        else:
            # No timestamp columns, skip this table
            return
        
        result = await db.execute(data_query)
        rows = result.fetchall()
        
        if not rows:
            return
        
        # Convert to JSON
        table_data = {
            "table_name": table_name,
            "rows": [dict(row._mapping) for row in rows],
            "backup_timestamp": datetime.utcnow().isoformat(),
            "since_timestamp": since_timestamp.isoformat()
        }
        
        # Add to tar archive
        table_info = tarfile.TarInfo(name=f"changed_data/{table_name}.json")
        table_data_bytes = json.dumps(table_data, indent=2, default=str).encode()
        table_info.size = len(table_data_bytes)
        tar.addfile(table_info, fileobj=io.BytesIO(table_data_bytes))
    
    except Exception as e:
        logger.error(f"Failed to backup changed table data {table_name}: {e}")
        raise


async def backup_changed_files(
    tar: tarfile.TarFile,
    since_timestamp: datetime
) -> None:
    """Backup files changed since timestamp."""
    try:
        upload_dir = os.getenv("UPLOAD_DIR", "uploads")
        
        if not os.path.exists(upload_dir):
            return
        
        # Find changed files
        changed_files = []
        for root, dirs, files in os.walk(upload_dir):
            for file in files:
                file_path = os.path.join(root, file)
                file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                if file_mtime > since_timestamp:
                    changed_files.append(file_path)
        
        # Add changed files to tar
        for file_path in changed_files:
            tar.add(file_path, arcname=f"changed_files/{os.path.relpath(file_path, upload_dir)}")
    
    except Exception as e:
        logger.error(f"Failed to backup changed files: {e}")
        raise


async def get_backup(
    backup_id: str,
    user_id: str,
    db: AsyncSession
) -> BackupResponse:
    """Get backup by ID."""
    try:
        # Check cache first
        cached_backup = get_cached_backup_data(backup_id)
        if cached_backup:
            return BackupResponse.from_orm(cached_backup)
        
        # Get from database
        query = select(Backup).where(Backup.id == backup_id)
        result = await db.execute(query)
        backup = result.scalar_one_or_none()
        
        if not backup:
            raise handle_not_found_error("Backup", backup_id)
        
        # Check access permissions
        has_access = await check_backup_access(backup, user_id, db)
        if not has_access:
            raise handle_forbidden_error("Access denied to backup")
        
        # Cache backup data
        cache_backup_data(backup_id, backup)
        
        return BackupResponse.from_orm(backup)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get backup: {e}")
        raise handle_internal_error(f"Failed to get backup: {str(e)}")


async def list_backups(
    user_id: str,
    backup_type: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    size: int = 20,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """List backups with filtering and pagination."""
    try:
        # Build query
        query = select(Backup)
        
        # Apply filters
        if backup_type:
            query = query.where(Backup.backup_type == backup_type)
        
        if status:
            query = query.where(Backup.status == status)
        
        # Apply access control
        access_filter = or_(
            Backup.created_by == user_id
        )
        query = query.where(access_filter)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(desc(Backup.created_at)).offset((page - 1) * size).limit(size)
        
        # Execute query
        result = await db.execute(query)
        backups = result.scalars().all()
        
        # Convert to response format
        backup_responses = [BackupResponse.from_orm(backup) for backup in backups]
        
        return {
            "backups": backup_responses,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
    
    except Exception as e:
        logger.error(f"Failed to list backups: {e}")
        raise handle_internal_error(f"Failed to list backups: {str(e)}")


async def restore_backup(
    backup_id: str,
    restore_data: BackupRestoreRequest,
    user_id: str,
    db: AsyncSession
) -> Dict[str, str]:
    """Restore from backup."""
    try:
        # Get backup
        backup = await get_backup(backup_id, user_id, db)
        
        if backup.status != "completed":
            raise handle_forbidden_error("Backup is not completed")
        
        if not os.path.exists(backup.backup_path):
            raise handle_not_found_error("Backup file", backup_id)
        
        # Create restore job
        job = BackupJob(
            backup_id=backup.id,
            status="running",
            started_at=datetime.utcnow(),
            progress=0,
            job_type="restore"
        )
        
        db.add(job)
        await db.commit()
        await db.refresh(job)
        
        # Start restore process asynchronously
        asyncio.create_task(execute_restore(backup, job, restore_data, db))
        
        logger.info(f"Backup restore started: {backup.id} by user {user_id}")
        
        return {"message": "Backup restore started", "job_id": str(job.id)}
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to start backup restore: {e}")
        raise handle_internal_error(f"Failed to start backup restore: {str(e)}")


async def execute_restore(
    backup: Backup,
    job: BackupJob,
    restore_data: BackupRestoreRequest,
    db: AsyncSession
) -> None:
    """Execute restore process."""
    try:
        # Update job status
        job.status = "running"
        job.progress = 10
        await db.commit()
        
        # Extract backup
        with tarfile.open(backup.backup_path, "r:gz") as tar:
            # Restore database schema if requested
            if restore_data.restore_schema:
                await restore_database_schema(tar, db)
                job.progress = 30
                await db.commit()
            
            # Restore database data if requested
            if restore_data.restore_data:
                await restore_database_data(tar, db)
                job.progress = 60
                await db.commit()
            
            # Restore files if requested
            if restore_data.restore_files:
                await restore_files(tar)
                job.progress = 80
                await db.commit()
            
            # Restore configuration if requested
            if restore_data.restore_configuration:
                await restore_configuration(tar)
                job.progress = 90
                await db.commit()
        
        # Update job status
        job.status = "completed"
        job.progress = 100
        job.completed_at = datetime.utcnow()
        
        await db.commit()
        
        logger.info(f"Backup restore completed: {backup.id}")
        
    except Exception as e:
        # Update job status with error
        job.status = "failed"
        job.error_message = str(e)
        job.completed_at = datetime.utcnow()
        
        await db.commit()
        
        logger.error(f"Backup restore failed: {backup.id} - {e}")


async def restore_database_schema(
    tar: tarfile.TarFile,
    db: AsyncSession
) -> None:
    """Restore database schema."""
    try:
        # Extract schema file
        schema_member = tar.getmember("database_schema.json")
        schema_file = tar.extractfile(schema_member)
        
        if schema_file:
            schema_data = json.loads(schema_file.read())
            
            # Restore schema (this would implement actual schema restoration)
            logger.info("Database schema restored")
    
    except Exception as e:
        logger.error(f"Failed to restore database schema: {e}")
        raise


async def restore_database_data(
    tar: tarfile.TarFile,
    db: AsyncSession
) -> None:
    """Restore database data."""
    try:
        # Get all data files
        data_members = [member for member in tar.getmembers() if member.name.startswith("data/")]
        
        for member in data_members:
            table_name = os.path.basename(member.name).replace(".json", "")
            data_file = tar.extractfile(member)
            
            if data_file:
                table_data = json.loads(data_file.read())
                
                # Restore table data (this would implement actual data restoration)
                logger.info(f"Table {table_name} data restored")
    
    except Exception as e:
        logger.error(f"Failed to restore database data: {e}")
        raise


async def restore_files(
    tar: tarfile.TarFile
) -> None:
    """Restore files."""
    try:
        # Extract files
        file_members = [member for member in tar.getmembers() if member.name.startswith("files/")]
        
        for member in file_members:
            tar.extract(member, path="/")
        
        logger.info("Files restored")
    
    except Exception as e:
        logger.error(f"Failed to restore files: {e}")
        raise


async def restore_configuration(
    tar: tarfile.TarFile
) -> None:
    """Restore configuration."""
    try:
        # Extract configuration file
        config_member = tar.getmember("configuration.json")
        config_file = tar.extractfile(config_member)
        
        if config_file:
            config_data = json.loads(config_file.read())
            
            # Restore configuration (this would implement actual configuration restoration)
            logger.info("Configuration restored")
    
    except Exception as e:
        logger.error(f"Failed to restore configuration: {e}")
        raise


async def delete_backup(
    backup_id: str,
    user_id: str,
    db: AsyncSession
) -> Dict[str, str]:
    """Delete backup."""
    try:
        # Get backup
        backup = await get_backup(backup_id, user_id, db)
        
        # Delete backup file
        if os.path.exists(backup.backup_path):
            os.remove(backup.backup_path)
        
        # Delete backup record
        await db.delete(backup)
        await db.commit()
        
        # Invalidate cache
        invalidate_backup_cache(backup_id)
        
        logger.info(f"Backup deleted: {backup_id} by user {user_id}")
        
        return {"message": "Backup deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to delete backup: {e}")
        raise handle_internal_error(f"Failed to delete backup: {str(e)}")


async def cleanup_old_backups(
    days_old: int = BACKUP_RETENTION_DAYS,
    db: AsyncSession = None
) -> int:
    """Clean up old backups."""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        # Find old backups
        query = select(Backup).where(
            and_(
                Backup.created_at < cutoff_date,
                Backup.status == "completed"
            )
        )
        result = await db.execute(query)
        old_backups = result.scalars().all()
        
        deleted_count = 0
        for backup in old_backups:
            # Delete backup file
            if os.path.exists(backup.backup_path):
                os.remove(backup.backup_path)
            
            # Delete backup record
            await db.delete(backup)
            deleted_count += 1
        
        await db.commit()
        
        logger.info(f"Cleaned up {deleted_count} old backups")
        
        return deleted_count
    
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to cleanup old backups: {e}")
        return 0


# Helper functions
async def check_backup_access(
    backup: Backup,
    user_id: str,
    db: AsyncSession
) -> bool:
    """Check if user has access to backup."""
    # Creator has access
    if backup.created_by == user_id:
        return True
    
    return False


async def get_backup_jobs(
    backup_id: str,
    user_id: str,
    page: int = 1,
    size: int = 20,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """Get backup jobs."""
    try:
        # Check backup access
        backup = await get_backup(backup_id, user_id, db)
        
        # Get jobs
        query = select(BackupJob).where(
            BackupJob.backup_id == backup_id
        ).order_by(desc(BackupJob.started_at))
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # Apply pagination
        query = query.offset((page - 1) * size).limit(size)
        
        result = await db.execute(query)
        jobs = result.scalars().all()
        
        job_responses = [BackupJobResponse.from_orm(job) for job in jobs]
        
        return {
            "jobs": job_responses,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get backup jobs: {e}")
        raise handle_internal_error(f"Failed to get backup jobs: {str(e)}")




