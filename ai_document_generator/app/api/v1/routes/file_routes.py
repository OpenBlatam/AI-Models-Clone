"""
File routes following functional patterns and RORO
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.errors import handle_validation_error, handle_internal_error
from app.schemas.user import User
from app.schemas.file import (
    FileResponse, FileUploadResponse, FileDeleteResponse,
    FileDownloadResponse, FileMetadata, FileShareRequest,
    FileShareResponse, FileUpdate, FileListResponse,
    FileVersionListResponse, FileShareListResponse
)
from app.services.file_service import (
    upload_file, get_file, download_file, delete_file,
    list_files, get_file_versions, share_file,
    get_file_metadata
)
from app.utils.validators import validate_pagination
from app.utils.rate_limiter import rate_limit_file_upload

router = APIRouter()


async def upload_file_endpoint(
    file: UploadFile,
    user: User,
    document_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    is_public: bool = False,
    db: AsyncSession = None
) -> FileUploadResponse:
    """Upload a file to the system."""
    # Convert document_id to UUID if provided
    doc_uuid = None
    if document_id:
        try:
            doc_uuid = uuid.UUID(document_id)
        except ValueError:
            raise handle_validation_error(ValueError("Invalid document ID format"))
    
    # Upload file
    file_response = await upload_file(
        file.file, file.filename, user.id, doc_uuid, metadata, db
    )
    
    return FileUploadResponse(
        file=file_response,
        message="File uploaded successfully"
    )


async def get_file_endpoint(
    file_id: str,
    user: User,
    db: AsyncSession
) -> FileResponse:
    """Get file information by ID."""
    try:
        file_uuid = uuid.UUID(file_id)
    except ValueError:
        raise handle_validation_error(ValueError("Invalid file ID format"))
    
    return await get_file(file_uuid, user.id, db)


async def download_file_endpoint(
    file_id: str,
    user: User,
    db: AsyncSession
) -> FileDownloadResponse:
    """Get file download information."""
    try:
        file_uuid = uuid.UUID(file_id)
    except ValueError:
        raise handle_validation_error(ValueError("Invalid file ID format"))
    
    download_info = await download_file(file_uuid, user.id, db)
    
    return FileDownloadResponse(**download_info)


async def delete_file_endpoint(
    file_id: str,
    user: User,
    db: AsyncSession
) -> FileDeleteResponse:
    """Delete a file."""
    try:
        file_uuid = uuid.UUID(file_id)
    except ValueError:
        raise handle_validation_error(ValueError("Invalid file ID format"))
    
    result = await delete_file(file_uuid, user.id, db)
    
    return FileDeleteResponse(message=result["message"])


async def list_files_endpoint(
    user: User,
    document_id: Optional[str] = None,
    file_type: Optional[str] = None,
    page: int = 1,
    size: int = 20,
    db: AsyncSession = None
) -> FileListResponse:
    """List files with filtering and pagination."""
    # Validate pagination
    pagination_validation = validate_pagination(page, size)
    if not pagination_validation["is_valid"]:
        raise handle_validation_error(
            ValueError(f"Invalid pagination: {', '.join(pagination_validation['errors'])}")
        )
    
    # Convert document_id to UUID if provided
    doc_uuid = None
    if document_id:
        try:
            doc_uuid = uuid.UUID(document_id)
        except ValueError:
            raise handle_validation_error(ValueError("Invalid document ID format"))
    
    result = await list_files(user.id, doc_uuid, file_type, page, size, db)
    
    return FileListResponse(**result)


async def get_file_versions_endpoint(
    file_id: str,
    user: User,
    page: int = 1,
    size: int = 20,
    db: AsyncSession = None
) -> FileVersionListResponse:
    """Get file versions."""
    try:
        file_uuid = uuid.UUID(file_id)
    except ValueError:
        raise handle_validation_error(ValueError("Invalid file ID format"))
    
    # Validate pagination
    pagination_validation = validate_pagination(page, size)
    if not pagination_validation["is_valid"]:
        raise handle_validation_error(
            ValueError(f"Invalid pagination: {', '.join(pagination_validation['errors'])}")
        )
    
    result = await get_file_versions(file_uuid, user.id, page, size, db)
    
    return FileVersionListResponse(**result)


async def share_file_endpoint(
    file_id: str,
    share_data: FileShareRequest,
    user: User,
    db: AsyncSession
) -> FileShareResponse:
    """Share file with user or organization."""
    try:
        file_uuid = uuid.UUID(file_id)
    except ValueError:
        raise handle_validation_error(ValueError("Invalid file ID format"))
    
    return await share_file(file_uuid, user.id, share_data.dict(), db)


async def get_file_metadata_endpoint(
    file_id: str,
    user: User,
    db: AsyncSession
) -> FileMetadata:
    """Get detailed file metadata."""
    try:
        file_uuid = uuid.UUID(file_id)
    except ValueError:
        raise handle_validation_error(ValueError("Invalid file ID format"))
    
    return await get_file_metadata(file_uuid, user.id, db)


# Route definitions
@router.post("/upload", response_model=FileUploadResponse)
@rate_limit_file_upload(key_func=lambda user, **kwargs: f"user:{user.id}")
async def upload_file_route(
    file: UploadFile = File(...),
    document_id: Optional[str] = Form(None),
    metadata: Optional[str] = Form(None),
    is_public: bool = Form(False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> FileUploadResponse:
    """Upload a file to the system."""
    # Parse metadata if provided
    parsed_metadata = None
    if metadata:
        try:
            import json
            parsed_metadata = json.loads(metadata)
        except json.JSONDecodeError:
            raise handle_validation_error(ValueError("Invalid metadata JSON format"))
    
    return await upload_file_endpoint(file, current_user, document_id, parsed_metadata, is_public, db)


@router.get("/{file_id}", response_model=FileResponse)
async def get_file_route(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> FileResponse:
    """Get file information by ID."""
    return await get_file_endpoint(file_id, current_user, db)


@router.get("/{file_id}/download", response_model=FileDownloadResponse)
async def download_file_route(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> FileDownloadResponse:
    """Get file download information."""
    return await download_file_endpoint(file_id, current_user, db)


@router.delete("/{file_id}", response_model=FileDeleteResponse)
async def delete_file_route(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> FileDeleteResponse:
    """Delete a file."""
    return await delete_file_endpoint(file_id, current_user, db)


@router.get("/", response_model=FileListResponse)
async def list_files_route(
    document_id: Optional[str] = Query(None, description="Filter by document ID"),
    file_type: Optional[str] = Query(None, description="Filter by file type"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> FileListResponse:
    """List files with filtering and pagination."""
    return await list_files_endpoint(current_user, document_id, file_type, page, size, db)


@router.get("/{file_id}/versions", response_model=FileVersionListResponse)
async def get_file_versions_route(
    file_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> FileVersionListResponse:
    """Get file versions."""
    return await get_file_versions_endpoint(file_id, current_user, page, size, db)


@router.post("/{file_id}/share", response_model=FileShareResponse)
async def share_file_route(
    file_id: str,
    share_data: FileShareRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> FileShareResponse:
    """Share file with user or organization."""
    return await share_file_endpoint(file_id, share_data, current_user, db)


@router.get("/{file_id}/metadata", response_model=FileMetadata)
async def get_file_metadata_route(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> FileMetadata:
    """Get detailed file metadata."""
    return await get_file_metadata_endpoint(file_id, current_user, db)


@router.get("/{file_id}/shares", response_model=FileShareListResponse)
async def get_file_shares_route(
    file_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> FileShareListResponse:
    """Get file shares."""
    # This would be implemented in file_service.py
    # For now, returning empty list
    return FileShareListResponse(
        shares=[],
        total=0,
        page=page,
        size=size,
        pages=0
    )


@router.put("/{file_id}", response_model=FileResponse)
async def update_file_route(
    file_id: str,
    update_data: FileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> FileResponse:
    """Update file metadata."""
    # This would be implemented in file_service.py
    # For now, returning the current file
    return await get_file_endpoint(file_id, current_user, db)


@router.get("/{file_id}/stats", response_model=Dict[str, Any])
async def get_file_stats_route(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get file statistics."""
    # This would implement file statistics logic
    # For now, returning placeholder data
    return {
        "file_id": file_id,
        "download_count": 0,
        "view_count": 0,
        "share_count": 0,
        "last_accessed": None,
        "access_log": []
    }


@router.post("/{file_id}/duplicate", response_model=FileResponse)
async def duplicate_file_route(
    file_id: str,
    new_filename: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> FileResponse:
    """Duplicate a file."""
    # Get original file
    original_file = await get_file_endpoint(file_id, current_user, db)
    
    # This would implement file duplication logic
    # For now, returning the original file
    return original_file


@router.get("/stats/overview", response_model=Dict[str, Any])
async def get_files_overview_route(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get files overview statistics."""
    # This would implement files overview logic
    # For now, returning placeholder data
    return {
        "total_files": 0,
        "total_size": 0,
        "files_by_type": {},
        "recent_uploads": [],
        "storage_usage": {
            "used": 0,
            "available": 0,
            "percentage": 0
        }
    }


@router.post("/bulk/upload", response_model=List[FileUploadResponse])
async def bulk_upload_files_route(
    files: List[UploadFile] = File(...),
    document_id: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[FileUploadResponse]:
    """Upload multiple files at once."""
    results = []
    
    for file in files:
        try:
            result = await upload_file_endpoint(file, current_user, document_id, None, False, db)
            results.append(result)
        except Exception as e:
            # Continue with other files even if one fails
            logger.error(f"Failed to upload file {file.filename}: {e}")
            continue
    
    return results


@router.delete("/bulk/delete", response_model=Dict[str, Any])
async def bulk_delete_files_route(
    file_ids: List[str],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Delete multiple files at once."""
    deleted_count = 0
    failed_count = 0
    
    for file_id in file_ids:
        try:
            await delete_file_endpoint(file_id, current_user, db)
            deleted_count += 1
        except Exception as e:
            logger.error(f"Failed to delete file {file_id}: {e}")
            failed_count += 1
    
    return {
        "deleted_count": deleted_count,
        "failed_count": failed_count,
        "total_requested": len(file_ids)
    }




