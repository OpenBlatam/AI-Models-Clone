"""
Advanced Copywriting Cache - Intelligent Caching for AI Content Generation.

Specialized caching system optimized for copywriting operations with
semantic similarity detection, template caching, and performance optimization.
"""

import asyncio
import time
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
import json

import structlog
from pydantic import BaseModel
import numpy as np

# High-performance imports
from .optimization import FastSerializer, FastHasher
from .cache import CacheManager, get_cache_manager
from .copywriting_model import ContentRequest, GeneratedContent, ContentType, ContentTone

# Try to import similarity detection libraries
try:
    from sentence_transformers import SentenceTransformer
    import faiss
    SEMANTIC_SIMILARITY_AVAILABLE = True
except ImportError:
    SEMANTIC_SIMILARITY_AVAILABLE = False

logger = structlog.get_logger(__name__)


@dataclass
class CacheEntry:
    """Enhanced cache entry for copywriting content."""
    content_id: str
    request_hash: str
    content: str
    generated_content: GeneratedContent
    similarity_embedding: Optional[np.ndarray]
    access_count: int
    last_accessed: datetime
    creation_time: datetime
    tags: List[str]


class SemanticSimilarityEngine:
    """Semantic similarity detection for copywriting requests."""
    
    def __init__(self):
        self.model = None
        self.index = None
        self.embeddings_cache = {}
        
        if SEMANTIC_SIMILARITY_AVAILABLE:
            try:
                # Use a lightweight but effective model
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                self.index = faiss.IndexFlatIP(384)  # Inner product similarity
                logger.info("Semantic similarity engine initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize semantic similarity: {e}")
                SEMANTIC_SIMILARITY_AVAILABLE = False
    
    async def get_embedding(self, text: str) -> Optional[np.ndarray]:
        """Get semantic embedding for text."""
        if not self.model:
            return None
        
        # Check cache first
        text_hash = FastHasher.hash_fast(text)
        if text_hash in self.embeddings_cache:
            return self.embeddings_cache[text_hash]
        
        try:
            # Generate embedding in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None, 
                lambda: self.model.encode([text], convert_to_numpy=True)[0]
            )
            
            # Normalize for cosine similarity
            embedding = embedding / np.linalg.norm(embedding)
            
            # Cache the result
            self.embeddings_cache[text_hash] = embedding
            
            return embedding
            
        except Exception as e:
            logger.warning(f"Failed to generate embedding: {e}")
            return None
    
    async def find_similar_requests(
        self, 
        request_text: str, 
        cached_embeddings: List[Tuple[str, np.ndarray]], 
        threshold: float = 0.8
    ) -> List[Tuple[str, float]]:
        """Find semantically similar cached requests."""
        if not self.model or not cached_embeddings:
            return []
        
        query_embedding = await self.get_embedding(request_text)
        if query_embedding is None:
            return []
        
        similarities = []
        for cache_id, cached_embedding in cached_embeddings:
            try:
                # Calculate cosine similarity
                similarity = np.dot(query_embedding, cached_embedding)
                if similarity >= threshold:
                    similarities.append((cache_id, float(similarity)))
            except Exception as e:
                logger.warning(f"Similarity calculation failed: {e}")
                continue
        
        # Sort by similarity score (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities


class CopywritingCacheConfig(BaseModel):
    """Configuration for copywriting cache."""
    max_cache_size: int = 10000
    ttl_hours: int = 24
    semantic_similarity_threshold: float = 0.85
    enable_semantic_cache: bool = True
    enable_template_cache: bool = True
    enable_performance_cache: bool = True
    cache_compression: bool = True
    auto_cleanup_interval_hours: int = 6


class AdvancedCopywritingCache:
    """Advanced caching system for copywriting operations."""
    
    def __init__(self, config: Optional[CopywritingCacheConfig] = None):
        self.config = config or CopywritingCacheConfig()
        self.cache_entries: Dict[str, CacheEntry] = {}
        self.semantic_engine = SemanticSimilarityEngine() if self.config.enable_semantic_cache else None
        self.template_cache: Dict[str, Any] = {}
        self.performance_cache: Dict[str, List[float]] = {}
        self._lock = asyncio.Lock()
        
        # Start background cleanup task
        self._cleanup_task = None
        if self.config.auto_cleanup_interval_hours > 0:
            self._start_cleanup_task()
    
    def _start_cleanup_task(self):
        """Start background cache cleanup task."""
        async def cleanup_loop():
            while True:
                try:
                    await asyncio.sleep(self.config.auto_cleanup_interval_hours * 3600)
                    await self.cleanup_expired_entries()
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.warning(f"Cache cleanup failed: {e}")
        
        self._cleanup_task = asyncio.create_task(cleanup_loop())
    
    async def get_cached_content(self, request: ContentRequest) -> Optional[GeneratedContent]:
        """Get cached content with intelligent matching."""
        # Generate request signature
        request_signature = self._generate_request_signature(request)
        
        # Check exact match first
        async with self._lock:
            if request_signature in self.cache_entries:
                entry = self.cache_entries[request_signature]
                entry.access_count += 1
                entry.last_accessed = datetime.now(timezone.utc)
                
                logger.debug("Cache hit (exact match)", request_hash=request_signature)
                return entry.generated_content
        
        # Check semantic similarity if enabled
        if self.semantic_engine and self.config.enable_semantic_cache:
            similar_content = await self._find_similar_cached_content(request)
            if similar_content:
                logger.debug("Cache hit (semantic match)", 
                           similarity_score=similar_content[1])
                return similar_content[0]
        
        return None
    
    async def cache_content(self, request: ContentRequest, generated_content: GeneratedContent):
        """Cache generated content with metadata."""
        request_signature = self._generate_request_signature(request)
        
        # Generate semantic embedding if available
        similarity_embedding = None
        if self.semantic_engine:
            request_text = self._request_to_text(request)
            similarity_embedding = await self.semantic_engine.get_embedding(request_text)
        
        # Create cache entry
        entry = CacheEntry(
            content_id=generated_content.id,
            request_hash=request_signature,
            content=generated_content.content,
            generated_content=generated_content,
            similarity_embedding=similarity_embedding,
            access_count=1,
            last_accessed=datetime.now(timezone.utc),
            creation_time=datetime.now(timezone.utc),
            tags=self._generate_tags(request)
        )
        
        async with self._lock:
            # Check cache size limit
            if len(self.cache_entries) >= self.config.max_cache_size:
                await self._evict_least_used()
            
            self.cache_entries[request_signature] = entry
        
        # Track performance
        await self._track_performance(request, generated_content)
        
        logger.debug("Content cached", request_hash=request_signature, 
                    content_length=len(generated_content.content))
    
    async def _find_similar_cached_content(self, request: ContentRequest) -> Optional[Tuple[GeneratedContent, float]]:
        """Find semantically similar cached content."""
        if not self.semantic_engine:
            return None
        
        request_text = self._request_to_text(request)
        
        # Get all cached embeddings for this content type and tone
        cached_embeddings = []
        async with self._lock:
            for entry in self.cache_entries.values():
                if (entry.similarity_embedding is not None and
                    entry.generated_content.content_type == request.content_type and
                    entry.generated_content.tone == request.tone):
                    cached_embeddings.append((entry.request_hash, entry.similarity_embedding))
        
        if not cached_embeddings:
            return None
        
        # Find similar requests
        similar_requests = await self.semantic_engine.find_similar_requests(
            request_text, cached_embeddings, self.config.semantic_similarity_threshold
        )
        
        if similar_requests:
            # Return the most similar cached content
            best_match_hash, similarity_score = similar_requests[0]
            async with self._lock:
                if best_match_hash in self.cache_entries:
                    entry = self.cache_entries[best_match_hash]
                    entry.access_count += 1
                    entry.last_accessed = datetime.now(timezone.utc)
                    return (entry.generated_content, similarity_score)
        
        return None
    
    def _generate_request_signature(self, request: ContentRequest) -> str:
        """Generate unique signature for request."""
        # Create deterministic hash from request parameters
        request_data = {
            "content_type": request.content_type.value,
            "tone": request.tone.value,
            "language": request.language.value,
            "target_audience": request.target_audience.lower().strip(),
            "key_message": request.key_message.lower().strip(),
            "keywords": sorted([kw.lower().strip() for kw in request.keywords]),
            "call_to_action": request.call_to_action.lower().strip() if request.call_to_action else None,
            "max_length": request.max_length,
            "include_hashtags": request.include_hashtags,
            "include_emojis": request.include_emojis
        }
        
        request_json = FastSerializer.serialize_json(request_data)
        return FastHasher.hash_fast(request_json)
    
    def _request_to_text(self, request: ContentRequest) -> str:
        """Convert request to text for semantic analysis."""
        parts = [
            request.target_audience,
            request.key_message,
            " ".join(request.keywords),
        ]
        
        if request.call_to_action:
            parts.append(request.call_to_action)
        
        return " ".join(filter(None, parts))
    
    def _generate_tags(self, request: ContentRequest) -> List[str]:
        """Generate tags for cache entry."""
        tags = [
            request.content_type.value,
            request.tone.value,
            request.language.value
        ]
        
        # Add keyword-based tags
        tags.extend(request.keywords[:5])  # Limit to 5 keywords
        
        return tags
    
    async def _track_performance(self, request: ContentRequest, generated_content: GeneratedContent):
        """Track performance metrics for optimization."""
        if not self.config.enable_performance_cache:
            return
        
        content_type = request.content_type.value
        tone = request.tone.value
        key = f"{content_type}_{tone}"
        
        if key not in self.performance_cache:
            self.performance_cache[key] = []
        
        # Track generation time and quality metrics
        metrics = [generated_content.generation_time_ms]
        
        if generated_content.metrics:
            metrics.extend([
                generated_content.metrics.readability_score,
                generated_content.metrics.engagement_prediction * 100,  # Scale to similar range
                generated_content.confidence_score * 100
            ])
        
        self.performance_cache[key].extend(metrics)
        
        # Keep only recent metrics (last 1000 entries)
        if len(self.performance_cache[key]) > 1000:
            self.performance_cache[key] = self.performance_cache[key][-1000:]
    
    async def _evict_least_used(self):
        """Evict least recently used entries."""
        if not self.cache_entries:
            return
        
        # Sort by access count and last accessed time
        sorted_entries = sorted(
            self.cache_entries.items(),
            key=lambda x: (x[1].access_count, x[1].last_accessed)
        )
        
        # Remove 10% of entries
        entries_to_remove = max(1, len(sorted_entries) // 10)
        
        for i in range(entries_to_remove):
            entry_key = sorted_entries[i][0]
            del self.cache_entries[entry_key]
        
        logger.info(f"Evicted {entries_to_remove} cache entries")
    
    async def cleanup_expired_entries(self):
        """Clean up expired cache entries."""
        current_time = datetime.now(timezone.utc)
        ttl_delta = timedelta(hours=self.config.ttl_hours)
        
        expired_keys = []
        
        async with self._lock:
            for key, entry in self.cache_entries.items():
                if current_time - entry.creation_time > ttl_delta:
                    expired_keys.append(key)
        
        if expired_keys:
            async with self._lock:
                for key in expired_keys:
                    del self.cache_entries[key]
            
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        async with self._lock:
            total_entries = len(self.cache_entries)
            total_access_count = sum(entry.access_count for entry in self.cache_entries.values())
            
            if total_entries > 0:
                avg_access_count = total_access_count / total_entries
                
                # Calculate hit ratio (approximate)
                recent_entries = [e for e in self.cache_entries.values() 
                                if e.access_count > 1]  # Entries that were accessed more than once
                hit_ratio = len(recent_entries) / total_entries if total_entries > 0 else 0
            else:
                avg_access_count = 0
                hit_ratio = 0
        
        # Performance statistics
        performance_stats = {}
        for key, metrics in self.performance_cache.items():
            if metrics:
                performance_stats[key] = {
                    "avg_generation_time": np.mean(metrics),
                    "p95_generation_time": np.percentile(metrics, 95),
                    "total_generations": len(metrics)
                }
        
        return {
            "total_entries": total_entries,
            "total_access_count": total_access_count,
            "average_access_count": avg_access_count,
            "estimated_hit_ratio": hit_ratio,
            "semantic_similarity_enabled": self.semantic_engine is not None,
            "performance_stats": performance_stats,
            "config": self.config.dict()
        }
    
    async def clear_cache(self):
        """Clear all cache entries."""
        async with self._lock:
            self.cache_entries.clear()
            self.template_cache.clear()
            self.performance_cache.clear()
        
        logger.info("Cache cleared")
    
    async def shutdown(self):
        """Shutdown cache and cleanup resources."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        await self.clear_cache()


# Global cache instance
_copywriting_cache: Optional[AdvancedCopywritingCache] = None


async def get_copywriting_cache(config: Optional[CopywritingCacheConfig] = None) -> AdvancedCopywritingCache:
    """Get or create global copywriting cache."""
    global _copywriting_cache
    
    if _copywriting_cache is None:
        _copywriting_cache = AdvancedCopywritingCache(config)
    
    return _copywriting_cache


async def shutdown_copywriting_cache():
    """Shutdown global copywriting cache."""
    global _copywriting_cache
    
    if _copywriting_cache:
        await _copywriting_cache.shutdown()
        _copywriting_cache = None


# Export components
__all__ = [
    "AdvancedCopywritingCache",
    "CopywritingCacheConfig",
    "SemanticSimilarityEngine",
    "CacheEntry",
    "get_copywriting_cache",
    "shutdown_copywriting_cache"
] 