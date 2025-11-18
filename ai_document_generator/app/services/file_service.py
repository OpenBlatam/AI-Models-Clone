"""
File service following functional patterns
"""
from typing import Dict, Any, List, Optional, BinaryIO
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, text
from sqlalchemy.orm import selectinload
import uuid
import os
import mimetypes
import hashlib
import aiofiles
from pathlib import Path

from app.core.logging import get_logger
from app.core.errors import handle_validation_error, handle_internal_error, handle_not_found_error
from app.models.file import File, FileVersion, FileShare
from app.schemas.file import (
    FileUpload, FileResponse, FileVersionResponse,
    FileShareResponse, FileMetadata
)
from app.utils.validators import validate_file_type, validate_file_size, validate_filename
from app.utils.helpers import generate_secure_filename, get_file_hash, sanitize_filename
from app.utils.cache import cache_file_data, get_cached_file_data, invalidate_file_cache

logger = get_logger(__name__)

# File storage configuration
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 100 * 1024 * 1024))  # 100MB
ALLOWED_EXTENSIONS = {
    'image': ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'],
    'document': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'],
    'spreadsheet': ['.xls', '.xlsx', '.csv', '.ods'],
    'presentation': ['.ppt', '.pptx', '.odp'],
    'archive': ['.zip', '.rar', '.7z', '.tar', '.gz'],
    'code': ['.py', '.js', '.html', '.css', '.json', '.xml', '.yaml', '.yml']
}


async def upload_file(
    file_data: BinaryIO,
    filename: str,
    user_id: str,
    document_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    db: AsyncSession = None
) -> FileResponse:
    """Upload a file to the system."""
    try:
        # Validate filename
        filename_validation = validate_filename(filename)
        if not filename_validation["is_valid"]:
            raise handle_validation_error(
                ValueError(f"Invalid filename: {', '.join(filename_validation['errors'])}")
            )
        
        # Get file size
        file_data.seek(0, 2)  # Seek to end
        file_size = file_data.tell()
        file_data.seek(0)  # Reset to beginning
        
        # Validate file size
        size_validation = validate_file_size(file_size)
        if not size_validation["is_valid"]:
            raise handle_validation_error(
                ValueError(f"File too large: {', '.join(size_validation['errors'])}")
            )
        
        # Get file type
        file_type = get_file_type(filename)
        type_validation = validate_file_type(file_type)
        if not type_validation["is_valid"]:
            raise handle_validation_error(
                ValueError(f"File type not allowed: {', '.join(type_validation['errors'])}")
            )
        
        # Generate secure filename and path
        secure_filename = generate_secure_filename(filename)
        file_hash = await get_file_hash(file_data)
        file_path = create_file_path(secure_filename, file_hash)
        
        # Ensure upload directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save file to disk
        async with aiofiles.open(file_path, 'wb') as f:
            file_data.seek(0)
            content = await file_data.read()
            await f.write(content)
        
        # Create file record
        file_record = File(
            original_filename=filename,
            secure_filename=secure_filename,
            file_path=file_path,
            file_size=file_size,
            file_type=file_type,
            mime_type=mimetypes.guess_type(filename)[0] or 'application/octet-stream',
            file_hash=file_hash,
            document_id=document_id,
            uploaded_by=user_id,
            metadata=metadata or {},
            is_public=False,
            created_at=datetime.utcnow()
        )
        
        db.add(file_record)
        await db.commit()
        await db.refresh(file_record)
        
        # Create initial version
        await create_file_version(file_record.id, user_id, "Initial upload", file_path, db)
        
        # Cache file data
        cache_file_data(str(file_record.id), file_record)
        
        logger.info(f"File uploaded: {file_record.id} by user {user_id}")
        
        return FileResponse.from_orm(file_record)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        # Clean up file if database operation failed
        if 'file_path' in locals():
            try:
                os.remove(file_path)
            except:
                pass
        logger.error(f"Failed to upload file: {e}")
        raise handle_internal_error(f"Failed to upload file: {str(e)}")


async def get_file(
    file_id: str,
    user_id: str,
    db: AsyncSession
) -> FileResponse:
    """Get file information by ID."""
    try:
        # Check cache first
        cached_file = get_cached_file_data(file_id)
        if cached_file:
            return FileResponse.from_orm(cached_file)
        
        # Get from database
        query = select(File).where(File.id == file_id)
        result = await db.execute(query)
        file_record = result.scalar_one_or_none()
        
        if not file_record:
            raise handle_not_found_error("File", file_id)
        
        # Check access permissions
        has_access = await check_file_access(file_record, user_id, db)
        if not has_access:
            raise handle_forbidden_error("Access denied to file")
        
        # Cache file data
        cache_file_data(file_id, file_record)
        
        return FileResponse.from_orm(file_record)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get file: {e}")
        raise handle_internal_error(f"Failed to get file: {str(e)}")


async def download_file(
    file_id: str,
    user_id: str,
    db: AsyncSession
) -> Dict[str, Any]:
    """Get file download information."""
    try:
        # Get file record
        file_record = await get_file(file_id, user_id, db)
        
        # Check if file exists on disk
        if not os.path.exists(file_record.file_path):
            raise handle_not_found_error("File", file_id)
        
        # Generate download URL (in real implementation, this would be a signed URL)
        download_url = f"/api/v1/files/{file_id}/download"
        
        return {
            "file_id": file_id,
            "filename": file_record.original_filename,
            "file_size": file_record.file_size,
            "mime_type": file_record.mime_type,
            "download_url": download_url,
            "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get file download info: {e}")
        raise handle_internal_error(f"Failed to get file download info: {str(e)}")


async def delete_file(
    file_id: str,
    user_id: str,
    db: AsyncSession
) -> Dict[str, str]:
    """Delete a file."""
    try:
        # Get file record
        query = select(File).where(File.id == file_id)
        result = await db.execute(query)
        file_record = result.scalar_one_or_none()
        
        if not file_record:
            raise handle_not_found_error("File", file_id)
        
        # Check delete permissions (only uploader can delete)
        if file_record.uploaded_by != user_id:
            raise handle_forbidden_error("Only file uploader can delete")
        
        # Delete file from disk
        try:
            if os.path.exists(file_record.file_path):
                os.remove(file_record.file_path)
        except Exception as e:
            logger.warning(f"Failed to delete file from disk: {e}")
        
        # Delete file record
        await db.delete(file_record)
        await db.commit()
        
        # Invalidate cache
        invalidate_file_cache(file_id)
        
        logger.info(f"File deleted: {file_id} by user {user_id}")
        
        return {"message": "File deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to delete file: {e}")
        raise handle_internal_error(f"Failed to delete file: {str(e)}")


async def list_files(
    user_id: str,
    document_id: Optional[str] = None,
    file_type: Optional[str] = None,
    page: int = 1,
    size: int = 20,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """List files with filtering and pagination."""
    try:
        # Build query
        query = select(File)
        
        # Apply filters
        if document_id:
            query = query.where(File.document_id == document_id)
        
        if file_type:
            query = query.where(File.file_type == file_type)
        
        # Apply access control
        access_filter = or_(
            File.uploaded_by == user_id,
            File.is_public == True,
            File.document_id.in_(
                select(Document.id).where(
                    or_(
                        Document.owner_id == user_id,
                        Document.is_public == True
                    )
                )
            )
        )
        query = query.where(access_filter)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(desc(File.created_at)).offset((page - 1) * size).limit(size)
        
        # Execute query
        result = await db.execute(query)
        files = result.scalars().all()
        
        # Convert to response format
        file_responses = [FileResponse.from_orm(file) for file in files]
        
        return {
            "files": file_responses,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
    
    except Exception as e:
        logger.error(f"Failed to list files: {e}")
        raise handle_internal_error(f"Failed to list files: {str(e)}")


async def create_file_version(
    file_id: str,
    user_id: str,
    version_note: str,
    file_path: str,
    db: AsyncSession
) -> FileVersionResponse:
    """Create a new file version."""
    try:
        # Get current version number
        version_query = select(func.max(FileVersion.version_number)).where(
            FileVersion.file_id == file_id
        )
        version_result = await db.execute(version_query)
        current_version = version_result.scalar() or 0
        
        # Create new version
        version = FileVersion(
            file_id=file_id,
            version_number=current_version + 1,
            file_path=file_path,
            version_note=version_note,
            created_by=user_id,
            created_at=datetime.utcnow()
        )
        
        db.add(version)
        await db.commit()
        await db.refresh(version)
        
        return FileVersionResponse.from_orm(version)
    
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create file version: {e}")
        raise handle_internal_error(f"Failed to create file version: {str(e)}")


async def get_file_versions(
    file_id: str,
    user_id: str,
    page: int = 1,
    size: int = 20,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """Get file versions."""
    try:
        # Check file access
        file_record = await get_file(file_id, user_id, db)
        
        # Get versions
        query = select(FileVersion).where(
            FileVersion.file_id == file_id
        ).order_by(desc(FileVersion.version_number))
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # Apply pagination
        query = query.offset((page - 1) * size).limit(size)
        
        result = await db.execute(query)
        versions = result.scalars().all()
        
        version_responses = [FileVersionResponse.from_orm(version) for version in versions]
        
        return {
            "versions": version_responses,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get file versions: {e}")
        raise handle_internal_error(f"Failed to get file versions: {str(e)}")


async def share_file(
    file_id: str,
    user_id: str,
    share_data: Dict[str, Any],
    db: AsyncSession
) -> FileShareResponse:
    """Share file with user or organization."""
    try:
        # Check file access and ownership
        file_record = await get_file(file_id, user_id, db)
        
        if file_record.uploaded_by != user_id:
            raise handle_forbidden_error("Only file uploader can share")
        
        # Create share
        share = FileShare(
            file_id=file_id,
            shared_by=user_id,
            shared_with=share_data["shared_with"],
            permission=share_data["permission"],
            expires_at=share_data.get("expires_at"),
            created_at=datetime.utcnow()
        )
        
        db.add(share)
        await db.commit()
        await db.refresh(share)
        
        return FileShareResponse.from_orm(share)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to share file: {e}")
        raise handle_internal_error(f"Failed to share file: {str(e)}")


async def get_file_metadata(
    file_id: str,
    user_id: str,
    db: AsyncSession
) -> FileMetadata:
    """Get detailed file metadata."""
    try:
        # Get file record
        file_record = await get_file(file_id, user_id, db)
        
        # Get file stats
        file_stats = os.stat(file_record.file_path) if os.path.exists(file_record.file_path) else None
        
        # Get file versions count
        versions_query = select(func.count(FileVersion.id)).where(FileVersion.file_id == file_id)
        versions_result = await db.execute(versions_query)
        versions_count = versions_result.scalar()
        
        # Get shares count
        shares_query = select(func.count(FileShare.id)).where(
            and_(
                FileShare.file_id == file_id,
                FileShare.is_active == True
            )
        )
        shares_result = await db.execute(shares_query)
        shares_count = shares_result.scalar()
        
        return FileMetadata(
            file_id=file_id,
            original_filename=file_record.original_filename,
            file_size=file_record.file_size,
            file_type=file_record.file_type,
            mime_type=file_record.mime_type,
            file_hash=file_record.file_hash,
            created_at=file_record.created_at,
            updated_at=file_record.updated_at,
            versions_count=versions_count,
            shares_count=shares_count,
            is_public=file_record.is_public,
            metadata=file_record.metadata,
            file_stats={
                "exists": file_stats is not None,
                "size": file_stats.st_size if file_stats else 0,
                "modified": datetime.fromtimestamp(file_stats.st_mtime) if file_stats else None
            } if file_stats else None
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get file metadata: {e}")
        raise handle_internal_error(f"Failed to get file metadata: {str(e)}")


# Helper functions
def get_file_type(filename: str) -> str:
    """Determine file type from extension."""
    ext = Path(filename).suffix.lower()
    
    for file_type, extensions in ALLOWED_EXTENSIONS.items():
        if ext in extensions:
            return file_type
    
    return 'other'


def create_file_path(filename: str, file_hash: str) -> str:
    """Create secure file path."""
    # Use hash to create directory structure
    hash_dir = file_hash[:2]
    return os.path.join(UPLOAD_DIR, hash_dir, filename)


async def get_file_hash(file_data: BinaryIO) -> str:
    """Calculate file hash."""
    file_data.seek(0)
    content = await file_data.read()
    file_data.seek(0)
    return hashlib.sha256(content).hexdigest()


async def check_file_access(
    file_record: File,
    user_id: str,
    db: AsyncSession
) -> bool:
    """Check if user has access to file."""
    # Uploader has access
    if file_record.uploaded_by == user_id:
        return True
    
    # Public files
    if file_record.is_public:
        return True
    
    # Document access
    if file_record.document_id:
        from app.services.document_service import check_document_access
        doc_query = select(Document).where(Document.id == file_record.document_id)
        doc_result = await db.execute(doc_query)
        document = doc_result.scalar_one_or_none()
        
        if document:
            return await check_document_access(document, user_id, db)
    
    # Shared files
    share_query = select(FileShare).where(
        and_(
            FileShare.file_id == file_record.id,
            FileShare.shared_with == user_id,
            FileShare.is_active == True
        )
    )
    share_result = await db.execute(share_query)
    if share_result.scalar_one_or_none():
        return True
    
    return False


async def cleanup_orphaned_files(
    days_old: int = 7,
    db: AsyncSession = None
) -> int:
    """Clean up orphaned files (files without references)."""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        # Find orphaned files
        query = select(File).where(
            and_(
                File.created_at < cutoff_date,
                File.document_id.is_(None),
                File.is_public == False
            )
        )
        result = await db.execute(query)
        orphaned_files = result.scalars().all()
        
        deleted_count = 0
        for file_record in orphaned_files:
            # Delete file from disk
            try:
                if os.path.exists(file_record.file_path):
                    os.remove(file_record.file_path)
            except Exception as e:
                logger.warning(f"Failed to delete orphaned file from disk: {e}")
            
            # Delete file record
            await db.delete(file_record)
            deleted_count += 1
        
        await db.commit()
        
        logger.info(f"Cleaned up {deleted_count} orphaned files")
        
        return deleted_count
    
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to cleanup orphaned files: {e}")
        return 0




