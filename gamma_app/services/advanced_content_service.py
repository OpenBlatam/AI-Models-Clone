"""
Advanced Content Service with Multi-Format Support and Content Management
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, BinaryIO
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import mimetypes
from pathlib import Path
import aiofiles
from PIL import Image
import magic

from ..utils.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class ContentType(Enum):
    """Types of content"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    PRESENTATION = "presentation"
    SPREADSHEET = "spreadsheet"
    PDF = "pdf"
    ARCHIVE = "archive"
    CODE = "code"
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"
    XML = "xml"
    CSV = "csv"
    UNKNOWN = "unknown"

class ContentStatus(Enum):
    """Content status"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DELETED = "deleted"
    PROCESSING = "processing"
    ERROR = "error"

class ContentAccess(Enum):
    """Content access levels"""
    PUBLIC = "public"
    PRIVATE = "private"
    RESTRICTED = "restricted"
    INTERNAL = "internal"

@dataclass
class ContentMetadata:
    """Content metadata"""
    title: str
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    author: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    version: int = 1
    language: str = "en"
    category: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    custom_fields: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ContentItem:
    """Content item structure"""
    id: str
    content_type: ContentType
    status: ContentStatus
    access: ContentAccess
    metadata: ContentMetadata
    file_path: Optional[str] = None
    file_size: int = 0
    mime_type: Optional[str] = None
    checksum: Optional[str] = None
    thumbnail_path: Optional[str] = None
    preview_path: Optional[str] = None
    processing_status: Optional[str] = None
    error_message: Optional[str] = None
    related_content: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)

@dataclass
class ContentSearchResult:
    """Content search result"""
    content_id: str
    title: str
    description: Optional[str]
    content_type: ContentType
    relevance_score: float
    highlights: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ContentVersion:
    """Content version"""
    version: int
    content_id: str
    created_at: datetime
    author: str
    changes: str
    file_path: str
    file_size: int
    checksum: str

class AdvancedContentService:
    """Advanced Content Service with Multi-Format Support"""
    
    def __init__(self):
        self.content_items = {}
        self.content_versions = {}
        self.content_index = {}
        self.content_cache = {}
        self.upload_queue = asyncio.Queue()
        self.processing_queue = asyncio.Queue()
        
        # Initialize content directories
        self._initialize_directories()
        
        # Start background tasks
        self._start_background_tasks()
        
        logger.info("Advanced Content Service initialized")
    
    def _initialize_directories(self):
        """Initialize content storage directories"""
        try:
            base_dir = Path("gamma_app/content")
            directories = [
                "uploads",
                "processed",
                "thumbnails",
                "previews",
                "versions",
                "temp"
            ]
            
            for directory in directories:
                dir_path = base_dir / directory
                dir_path.mkdir(parents=True, exist_ok=True)
            
            logger.info("Content directories initialized")
            
        except Exception as e:
            logger.error(f"Error initializing directories: {e}")
    
    def _start_background_tasks(self):
        """Start background processing tasks"""
        try:
            # Start upload processor
            asyncio.create_task(self._process_uploads())
            
            # Start content processor
            asyncio.create_task(self._process_content())
            
            logger.info("Background tasks started")
            
        except Exception as e:
            logger.error(f"Error starting background tasks: {e}")
    
    async def _process_uploads(self):
        """Process uploaded files"""
        try:
            while True:
                try:
                    upload_task = await asyncio.wait_for(self.upload_queue.get(), timeout=1.0)
                    await self._handle_upload(upload_task)
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error processing upload: {e}")
                    
        except Exception as e:
            logger.error(f"Error in upload processor: {e}")
    
    async def _process_content(self):
        """Process content items"""
        try:
            while True:
                try:
                    content_task = await asyncio.wait_for(self.processing_queue.get(), timeout=1.0)
                    await self._handle_content_processing(content_task)
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error processing content: {e}")
                    
        except Exception as e:
            logger.error(f"Error in content processor: {e}")
    
    async def _handle_upload(self, upload_task: Dict[str, Any]):
        """Handle file upload"""
        try:
            content_id = upload_task['content_id']
            file_data = upload_task['file_data']
            metadata = upload_task['metadata']
            
            # Save file
            file_path = await self._save_file(content_id, file_data)
            
            # Detect content type
            content_type = await self._detect_content_type(file_path)
            
            # Calculate checksum
            checksum = await self._calculate_checksum(file_path)
            
            # Create content item
            content_item = ContentItem(
                id=content_id,
                content_type=content_type,
                status=ContentStatus.PROCESSING,
                access=ContentAccess.PRIVATE,
                metadata=metadata,
                file_path=file_path,
                file_size=len(file_data),
                checksum=checksum
            )
            
            # Store content item
            self.content_items[content_id] = content_item
            
            # Add to processing queue
            await self.processing_queue.put({
                'content_id': content_id,
                'action': 'process'
            })
            
            logger.info(f"Upload processed: {content_id}")
            
        except Exception as e:
            logger.error(f"Error handling upload: {e}")
    
    async def _handle_content_processing(self, processing_task: Dict[str, Any]):
        """Handle content processing"""
        try:
            content_id = processing_task['content_id']
            action = processing_task['action']
            
            if content_id not in self.content_items:
                logger.error(f"Content item not found: {content_id}")
                return
            
            content_item = self.content_items[content_id]
            
            if action == 'process':
                await self._process_content_item(content_item)
            elif action == 'generate_thumbnail':
                await self._generate_thumbnail(content_item)
            elif action == 'generate_preview':
                await self._generate_preview(content_item)
            elif action == 'extract_metadata':
                await self._extract_metadata(content_item)
            
        except Exception as e:
            logger.error(f"Error handling content processing: {e}")
    
    async def _process_content_item(self, content_item: ContentItem):
        """Process a content item"""
        try:
            # Update status
            content_item.status = ContentStatus.PROCESSING
            content_item.processing_status = "Processing content"
            
            # Generate thumbnail if applicable
            if content_item.content_type in [ContentType.IMAGE, ContentType.VIDEO, ContentType.PDF]:
                await self.processing_queue.put({
                    'content_id': content_item.id,
                    'action': 'generate_thumbnail'
                })
            
            # Generate preview if applicable
            if content_item.content_type in [ContentType.DOCUMENT, ContentType.PDF, ContentType.PRESENTATION]:
                await self.processing_queue.put({
                    'content_id': content_item.id,
                    'action': 'generate_preview'
                })
            
            # Extract metadata
            await self.processing_queue.put({
                'content_id': content_item.id,
                'action': 'extract_metadata'
            })
            
            # Update status
            content_item.status = ContentStatus.DRAFT
            content_item.processing_status = None
            
            logger.info(f"Content processed: {content_item.id}")
            
        except Exception as e:
            logger.error(f"Error processing content item: {e}")
            content_item.status = ContentStatus.ERROR
            content_item.error_message = str(e)
    
    async def _generate_thumbnail(self, content_item: ContentItem):
        """Generate thumbnail for content"""
        try:
            if not content_item.file_path:
                return
            
            thumbnail_path = f"gamma_app/content/thumbnails/{content_item.id}.jpg"
            
            if content_item.content_type == ContentType.IMAGE:
                # Generate image thumbnail
                with Image.open(content_item.file_path) as img:
                    img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                    img.save(thumbnail_path, "JPEG", quality=85)
            
            elif content_item.content_type == ContentType.VIDEO:
                # Generate video thumbnail (placeholder)
                # In a real implementation, you would use ffmpeg or similar
                pass
            
            elif content_item.content_type == ContentType.PDF:
                # Generate PDF thumbnail (placeholder)
                # In a real implementation, you would use pdf2image or similar
                pass
            
            content_item.thumbnail_path = thumbnail_path
            logger.info(f"Thumbnail generated: {content_item.id}")
            
        except Exception as e:
            logger.error(f"Error generating thumbnail: {e}")
    
    async def _generate_preview(self, content_item: ContentItem):
        """Generate preview for content"""
        try:
            if not content_item.file_path:
                return
            
            preview_path = f"gamma_app/content/previews/{content_item.id}.html"
            
            # Generate HTML preview based on content type
            if content_item.content_type == ContentType.DOCUMENT:
                # Generate document preview
                preview_html = f"""
                <div class="content-preview">
                    <h2>{content_item.metadata.title}</h2>
                    <p>Document preview for {content_item.id}</p>
                    <p>File size: {content_item.file_size} bytes</p>
                </div>
                """
            elif content_item.content_type == ContentType.PDF:
                # Generate PDF preview
                preview_html = f"""
                <div class="content-preview">
                    <h2>{content_item.metadata.title}</h2>
                    <p>PDF preview for {content_item.id}</p>
                    <p>File size: {content_item.file_size} bytes</p>
                </div>
                """
            else:
                preview_html = f"""
                <div class="content-preview">
                    <h2>{content_item.metadata.title}</h2>
                    <p>Preview for {content_item.content_type.value}</p>
                </div>
                """
            
            # Save preview
            async with aiofiles.open(preview_path, 'w', encoding='utf-8') as f:
                await f.write(preview_html)
            
            content_item.preview_path = preview_path
            logger.info(f"Preview generated: {content_item.id}")
            
        except Exception as e:
            logger.error(f"Error generating preview: {e}")
    
    async def _extract_metadata(self, content_item: ContentItem):
        """Extract metadata from content"""
        try:
            if not content_item.file_path:
                return
            
            # Extract basic metadata
            if content_item.content_type == ContentType.IMAGE:
                with Image.open(content_item.file_path) as img:
                    content_item.metadata.custom_fields.update({
                        'width': img.width,
                        'height': img.height,
                        'format': img.format,
                        'mode': img.mode
                    })
            
            elif content_item.content_type == ContentType.DOCUMENT:
                # Extract document metadata (placeholder)
                content_item.metadata.custom_fields.update({
                    'word_count': 0,  # Would extract from document
                    'page_count': 0,  # Would extract from document
                    'language': 'en'  # Would detect language
                })
            
            # Update metadata
            content_item.metadata.updated_at = datetime.utcnow()
            
            logger.info(f"Metadata extracted: {content_item.id}")
            
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
    
    async def _save_file(self, content_id: str, file_data: bytes) -> str:
        """Save file to storage"""
        try:
            file_path = f"gamma_app/content/uploads/{content_id}"
            
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_data)
            
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            raise
    
    async def _detect_content_type(self, file_path: str) -> ContentType:
        """Detect content type from file"""
        try:
            # Get MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            
            if not mime_type:
                # Use python-magic for more accurate detection
                try:
                    mime_type = magic.from_file(file_path, mime=True)
                except:
                    mime_type = "application/octet-stream"
            
            # Map MIME type to content type
            if mime_type.startswith('text/'):
                if mime_type == 'text/markdown':
                    return ContentType.MARKDOWN
                elif mime_type == 'text/html':
                    return ContentType.HTML
                elif mime_type == 'text/csv':
                    return ContentType.CSV
                else:
                    return ContentType.TEXT
            
            elif mime_type.startswith('image/'):
                return ContentType.IMAGE
            
            elif mime_type.startswith('video/'):
                return ContentType.VIDEO
            
            elif mime_type.startswith('audio/'):
                return ContentType.AUDIO
            
            elif mime_type == 'application/pdf':
                return ContentType.PDF
            
            elif mime_type in ['application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
                return ContentType.DOCUMENT
            
            elif mime_type in ['application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation']:
                return ContentType.PRESENTATION
            
            elif mime_type in ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']:
                return ContentType.SPREADSHEET
            
            elif mime_type in ['application/zip', 'application/x-rar-compressed', 'application/x-7z-compressed']:
                return ContentType.ARCHIVE
            
            elif mime_type in ['application/json']:
                return ContentType.JSON
            
            elif mime_type in ['application/xml', 'text/xml']:
                return ContentType.XML
            
            elif mime_type.startswith('text/x-') or mime_type.startswith('application/x-'):
                return ContentType.CODE
            
            else:
                return ContentType.UNKNOWN
                
        except Exception as e:
            logger.error(f"Error detecting content type: {e}")
            return ContentType.UNKNOWN
    
    async def _calculate_checksum(self, file_path: str) -> str:
        """Calculate file checksum"""
        try:
            hash_md5 = hashlib.md5()
            
            async with aiofiles.open(file_path, 'rb') as f:
                while chunk := await f.read(8192):
                    hash_md5.update(chunk)
            
            return hash_md5.hexdigest()
            
        except Exception as e:
            logger.error(f"Error calculating checksum: {e}")
            return ""
    
    async def upload_content(self, file_data: bytes, metadata: ContentMetadata, 
                           access: ContentAccess = ContentAccess.PRIVATE) -> str:
        """Upload content"""
        try:
            # Generate content ID
            content_id = str(uuid.uuid4())
            
            # Add to upload queue
            await self.upload_queue.put({
                'content_id': content_id,
                'file_data': file_data,
                'metadata': metadata,
                'access': access
            })
            
            logger.info(f"Content queued for upload: {content_id}")
            
            return content_id
            
        except Exception as e:
            logger.error(f"Error uploading content: {e}")
            raise
    
    async def get_content(self, content_id: str) -> Optional[ContentItem]:
        """Get content item"""
        try:
            return self.content_items.get(content_id)
            
        except Exception as e:
            logger.error(f"Error getting content: {e}")
            return None
    
    async def update_content(self, content_id: str, updates: Dict[str, Any]) -> bool:
        """Update content item"""
        try:
            if content_id not in self.content_items:
                return False
            
            content_item = self.content_items[content_id]
            
            # Update fields
            for key, value in updates.items():
                if hasattr(content_item, key):
                    setattr(content_item, key, value)
                elif hasattr(content_item.metadata, key):
                    setattr(content_item.metadata, key, value)
            
            # Update timestamp
            content_item.metadata.updated_at = datetime.utcnow()
            content_item.metadata.version += 1
            
            # Create version
            await self._create_version(content_item)
            
            logger.info(f"Content updated: {content_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating content: {e}")
            return False
    
    async def _create_version(self, content_item: ContentItem):
        """Create content version"""
        try:
            version = ContentVersion(
                version=content_item.metadata.version,
                content_id=content_item.id,
                created_at=datetime.utcnow(),
                author=content_item.metadata.author or "system",
                changes="Content updated",
                file_path=content_item.file_path or "",
                file_size=content_item.file_size,
                checksum=content_item.checksum or ""
            )
            
            if content_item.id not in self.content_versions:
                self.content_versions[content_item.id] = []
            
            self.content_versions[content_item.id].append(version)
            
        except Exception as e:
            logger.error(f"Error creating version: {e}")
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete content item"""
        try:
            if content_id not in self.content_items:
                return False
            
            content_item = self.content_items[content_id]
            
            # Mark as deleted
            content_item.status = ContentStatus.DELETED
            
            # Remove from index
            if content_id in self.content_index:
                del self.content_index[content_id]
            
            logger.info(f"Content deleted: {content_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting content: {e}")
            return False
    
    async def search_content(self, query: str, content_type: Optional[ContentType] = None,
                           limit: int = 20) -> List[ContentSearchResult]:
        """Search content"""
        try:
            results = []
            query_lower = query.lower()
            
            for content_id, content_item in self.content_items.items():
                if content_item.status == ContentStatus.DELETED:
                    continue
                
                if content_type and content_item.content_type != content_type:
                    continue
                
                # Calculate relevance score
                relevance_score = 0.0
                highlights = []
                
                # Check title
                if query_lower in content_item.metadata.title.lower():
                    relevance_score += 0.5
                    highlights.append(f"Title: {content_item.metadata.title}")
                
                # Check description
                if content_item.metadata.description and query_lower in content_item.metadata.description.lower():
                    relevance_score += 0.3
                    highlights.append(f"Description: {content_item.metadata.description}")
                
                # Check tags
                for tag in content_item.metadata.tags:
                    if query_lower in tag.lower():
                        relevance_score += 0.2
                        highlights.append(f"Tag: {tag}")
                
                # Check keywords
                for keyword in content_item.metadata.keywords:
                    if query_lower in keyword.lower():
                        relevance_score += 0.1
                        highlights.append(f"Keyword: {keyword}")
                
                if relevance_score > 0:
                    result = ContentSearchResult(
                        content_id=content_id,
                        title=content_item.metadata.title,
                        description=content_item.metadata.description,
                        content_type=content_item.content_type,
                        relevance_score=relevance_score,
                        highlights=highlights,
                        metadata={
                            'author': content_item.metadata.author,
                            'created_at': content_item.metadata.created_at.isoformat(),
                            'tags': content_item.metadata.tags,
                            'status': content_item.status.value
                        }
                    )
                    results.append(result)
            
            # Sort by relevance score
            results.sort(key=lambda x: x.relevance_score, reverse=True)
            
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Error searching content: {e}")
            return []
    
    async def get_content_versions(self, content_id: str) -> List[ContentVersion]:
        """Get content versions"""
        try:
            return self.content_versions.get(content_id, [])
            
        except Exception as e:
            logger.error(f"Error getting content versions: {e}")
            return []
    
    async def restore_version(self, content_id: str, version: int) -> bool:
        """Restore content to specific version"""
        try:
            if content_id not in self.content_versions:
                return False
            
            versions = self.content_versions[content_id]
            target_version = next((v for v in versions if v.version == version), None)
            
            if not target_version:
                return False
            
            # Restore content
            content_item = self.content_items[content_id]
            content_item.file_path = target_version.file_path
            content_item.file_size = target_version.file_size
            content_item.checksum = target_version.checksum
            content_item.metadata.version = version
            content_item.metadata.updated_at = datetime.utcnow()
            
            logger.info(f"Content restored to version {version}: {content_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error restoring version: {e}")
            return False
    
    async def get_content_statistics(self) -> Dict[str, Any]:
        """Get content statistics"""
        try:
            stats = {
                'total_content': len(self.content_items),
                'by_type': {},
                'by_status': {},
                'by_access': {},
                'total_size': 0,
                'average_size': 0
            }
            
            total_size = 0
            
            for content_item in self.content_items.values():
                # Count by type
                content_type = content_item.content_type.value
                stats['by_type'][content_type] = stats['by_type'].get(content_type, 0) + 1
                
                # Count by status
                status = content_item.status.value
                stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
                
                # Count by access
                access = content_item.access.value
                stats['by_access'][access] = stats['by_access'].get(access, 0) + 1
                
                # Sum file sizes
                total_size += content_item.file_size
            
            stats['total_size'] = total_size
            stats['average_size'] = total_size / len(self.content_items) if self.content_items else 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting content statistics: {e}")
            return {}
    
    async def export_content(self, content_id: str, format: str = "json") -> str:
        """Export content"""
        try:
            content_item = self.content_items.get(content_id)
            if not content_item:
                return ""
            
            if format.lower() == "json":
                export_data = {
                    'id': content_item.id,
                    'content_type': content_item.content_type.value,
                    'status': content_item.status.value,
                    'access': content_item.access.value,
                    'metadata': {
                        'title': content_item.metadata.title,
                        'description': content_item.metadata.description,
                        'tags': content_item.metadata.tags,
                        'author': content_item.metadata.author,
                        'created_at': content_item.metadata.created_at.isoformat(),
                        'updated_at': content_item.metadata.updated_at.isoformat(),
                        'version': content_item.metadata.version,
                        'language': content_item.metadata.language,
                        'category': content_item.metadata.category,
                        'keywords': content_item.metadata.keywords,
                        'custom_fields': content_item.metadata.custom_fields
                    },
                    'file_info': {
                        'file_size': content_item.file_size,
                        'mime_type': content_item.mime_type,
                        'checksum': content_item.checksum,
                        'thumbnail_path': content_item.thumbnail_path,
                        'preview_path': content_item.preview_path
                    },
                    'versions': len(self.content_versions.get(content_id, [])),
                    'related_content': content_item.related_content,
                    'dependencies': content_item.dependencies
                }
                
                return json.dumps(export_data, indent=2)
            
            else:
                raise ValueError(f"Unsupported export format: {format}")
            
        except Exception as e:
            logger.error(f"Error exporting content: {e}")
            return ""
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get service status"""
        try:
            status = {
                'service': 'Advanced Content Service',
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'content': {
                    'total_items': len(self.content_items),
                    'upload_queue_size': self.upload_queue.qsize(),
                    'processing_queue_size': self.processing_queue.qsize()
                },
                'storage': {
                    'total_versions': sum(len(versions) for versions in self.content_versions.values()),
                    'cache_size': len(self.content_cache)
                }
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting service status: {e}")
            return {
                'service': 'Advanced Content Service',
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }


























