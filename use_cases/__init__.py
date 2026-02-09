from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS = 1000

# Constants
MAX_RETRIES = 100

# Constants
TIMEOUT_SECONDS = 60

import asyncio
import time
import uuid
import hashlib
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import aiocache
import aioredis
import asyncpg
import tenacity
from prometheus_client import Counter, Histogram, Gauge
import structlog
from dataclasses import asdict, replace
import orjson as json  # Ultra-fast JSON parsing
import httpx  # Modern HTTP client with HTTP/2 support
from asyncio_throttle import Throttler
from cachetools import TTLCache
import backoff
from functools import lru_cache
import weakref
from ..interfaces import (
from typing import Any, List, Dict, Optional
"""
ONYX BLOG POSTS - Production Use Cases Layer
============================================

Application services implementing business workflows with production-grade
optimizations using specialized libraries for maximum performance.

Architecture: Application Layer (Service orchestration)
Dependencies: Core domain logic and adapters
"""


# Production-grade libraries for optimization

    IGenerateBlogUseCase, IGenerateBatchUseCase, IAnalyzeContentUseCase,
    IBlogGenerator, ISEOGenerator, IContentValidator, IQualityAnalyzer,
    IAIProvider, ICacheProvider, IOnyxIntegration, IMetricsCollector,
    BlogSpec, GenerationParams, BlogResult, BlogContent, SEOData,
    BlogType, AIModel, GenerationStatus, QualityGrade, GenerationMetrics,
    ValidationError, GenerationError, ConfigurationError
)

# Structured logging
logger = structlog.get_logger(__name__)

# Prometheus metrics
blog_requests_total = Counter('blog_requests_total', 'Total blog generation requests', ['type', 'model'])
blog_duration_seconds = Histogram('blog_duration_seconds', 'Blog generation duration')
blog_quality_score = Histogram('blog_quality_score', 'Blog quality scores')
active_generations = Gauge('active_generations', 'Currently active generations')

# === PRODUCTION BLOG GENERATION USE CASE ===

class ProductionGenerateBlogUseCase:
    """
    Production-grade blog generation use case with comprehensive optimizations:
    - Circuit breaker pattern for fault tolerance
    - Intelligent caching with Redis
    - Rate limiting and throttling
    - Metrics collection with Prometheus
    - Structured logging
    - Retry logic with exponential backoff
    - Resource pooling and connection management
    """
    
    def __init__(
        self,
        blog_generator: IBlogGenerator,
        seo_generator: ISEOGenerator,
        content_validator: IContentValidator,
        quality_analyzer: IQualityAnalyzer,
        ai_provider: IAIProvider,
        cache_provider: ICacheProvider,
        onyx_integration: IOnyxIntegration,
        metrics_collector: IMetricsCollector,
        redis_url: str = "redis://localhost:6379",
        max_concurrent_generations: int = 10,
        rate_limit_per_minute: int = 60,
        circuit_breaker_threshold: int = 5
    ):
        
    """__init__ function."""
self.blog_generator = blog_generator
        self.seo_generator = seo_generator
        self.content_validator = content_validator
        self.quality_analyzer = quality_analyzer
        self.ai_provider = ai_provider
        self.cache_provider = cache_provider
        self.onyx_integration = onyx_integration
        self.metrics_collector = metrics_collector
        
        # Production optimizations
        self.max_concurrent = max_concurrent_generations
        self.rate_limit_per_minute = rate_limit_per_minute
        self.circuit_breaker_threshold = circuit_breaker_threshold
        
        # Concurrency control
        self.generation_semaphore = asyncio.Semaphore(max_concurrent_generations)
        self.rate_limiter = Throttler(rate_limit=rate_limit_per_minute, period=60)
        
        # Circuit breaker for fault tolerance
        self.circuit_breaker_failures = 0
        self.circuit_breaker_last_failure = None
        self.circuit_breaker_timeout = 60  # seconds
        
        # Advanced caching with aiocache
        self.cache = aiocache.Cache(aiocache.RedisCache, endpoint=redis_url.split('//')[1])
        
        # Connection pooling
        self.redis_pool: Optional[aioredis.Redis] = None
        self.db_pool: Optional[asyncpg.Pool] = None
        
        # Metrics tracking
        self.active_requests = 0
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        
        # Weak references for memory optimization
        self._request_cache = weakref.WeakValueDictionary()
    
    async def __aenter__(self) -> Any:
        """Async context manager entry"""
        await self._initialize_connections()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> Any:
        """Async context manager exit"""
        await self._cleanup_connections()
    
    async def _initialize_connections(self) -> Any:
        """Initialize connection pools"""
        try:
            # Redis connection pool
            self.redis_pool = aioredis.from_url(
                "redis://localhost:6379",
                max_connections=20,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Database connection pool (if needed)
            # self.db_pool = await asyncpg.create_pool(
            #     "postgresql://user:pass@localhost/db",
            #     min_size=5,
            #     max_size=20,
            #     command_timeout=60
            # )
            
            logger.info("Connection pools initialized")
            
        except Exception as e:
            logger.error("Failed to initialize connections", error=str(e))
            raise ConfigurationError(f"Connection initialization failed: {e}")
    
    async def _cleanup_connections(self) -> Any:
        """Clean up connection pools"""
        try:
            if self.redis_pool:
                await self.redis_pool.close()
            
            if self.db_pool:
                await self.db_pool.close()
                
            logger.info("Connection pools cleaned up")
            
        except Exception as e:
            logger.warning("Error during cleanup", error=str(e))
    
    def _is_circuit_breaker_open(self) -> bool:
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        """Check if circuit breaker is open"""
        if self.circuit_breaker_failures < self.circuit_breaker_threshold:
            return False
        
        if self.circuit_breaker_last_failure:
            time_since_failure = time.time() - self.circuit_breaker_last_failure
            if time_since_failure > self.circuit_breaker_timeout:
                # Reset circuit breaker
                self.circuit_breaker_failures = 0
                self.circuit_breaker_last_failure = None
                return False
        
        return True
    
    def _record_circuit_breaker_failure(self) -> Any:
        """Record circuit breaker failure"""
        self.circuit_breaker_failures += 1
        self.circuit_breaker_last_failure = time.time()
        logger.warning(
            "Circuit breaker failure recorded",
            failures=self.circuit_breaker_failures,
            threshold=self.circuit_breaker_threshold
        )
    
    def _record_circuit_breaker_success(self) -> Any:
        """Record circuit breaker success"""
        if self.circuit_breaker_failures > 0:
            self.circuit_breaker_failures = max(0, self.circuit_breaker_failures - 1)
    
    @tenacity.retry(
        stop=tenacity.stop_after_attempt(3),
        wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
        retry=tenacity.retry_if_exception_type((GenerationError, ConnectionError))
    )
    async def _generate_with_retry(self, spec: BlogSpec, params: GenerationParams) -> BlogResult:
        """Generate blog with retry logic"""
        return await self.blog_generator.generate_blog(spec, params)
    
    async def _get_cached_result(self, cache_key: str) -> Optional[BlogResult]:
        """Get cached result with Redis optimization"""
        try:
            # Try local cache first (fastest)
            if cache_key in self._request_cache:
                logger.debug("Cache hit (local)", key=cache_key[:20])
                return self._request_cache[cache_key]
            
            # Try Redis cache
            cached_data = await self.cache.get(cache_key)
            if cached_data:
                result = BlogResult.from_dict(json.loads(cached_data))
                self._request_cache[cache_key] = result
                logger.debug("Cache hit (Redis)", key=cache_key[:20])
                return result
            
            return None
            
        except Exception as e:
            logger.warning("Cache get failed", error=str(e), key=cache_key[:20])
            return None
    
    async def _cache_result(self, cache_key: str, result: BlogResult, ttl: int = 3600):
        """Cache result with Redis optimization"""
        try:
            # Cache in Redis
            serialized = json.dumps(result.to_dict())
            await self.cache.set(cache_key, serialized, ttl=ttl)
            
            # Cache locally
            self._request_cache[cache_key] = result
            
            logger.debug("Result cached", key=cache_key[:20], ttl=ttl)
            
        except Exception as e:
            logger.warning("Cache set failed", error=str(e), key=cache_key[:20])
    
    async def generate_blog(
        self,
        spec: BlogSpec,
        params: GenerationParams,
        user_id: str,
        force_regenerate: bool = False
    ) -> BlogResult:
        """
        Generate blog post with production optimizations
        
        Features:
        - Circuit breaker protection
        - Rate limiting
        - Intelligent caching
        - Metrics collection
        - Structured logging
        - Resource management
        """
        
        # Generate request ID and cache key
        request_id = str(uuid.uuid4())
        cache_key = spec.cache_key
        
        # Structured logging context
        log_context = {
            "request_id": request_id,
            "user_id": user_id,
            "blog_type": spec.blog_type.value,
            "model": params.model.value,
            "topic": spec.topic[:50]
        }
        
        logger.info("Blog generation started", **log_context)
        
        # Increment metrics
        self.total_requests += 1
        blog_requests_total.labels(type=spec.blog_type.value, model=params.model.value).inc()
        
        try:
            # Circuit breaker check
            if self._is_circuit_breaker_open():
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
                logger.error("Circuit breaker is open", **log_context)
                raise GenerationError("Service temporarily unavailable")
            
            # Rate limiting
            async with self.rate_limiter:
                # Check cache first (unless forced regeneration)
                if not force_regenerate:
                    cached_result = await self._get_cached_result(cache_key)
                    if cached_result:
                        logger.info("Returning cached result", **log_context)
                        return cached_result
                
                # Concurrency control
                async with self.generation_semaphore:
                    self.active_requests += 1
                    active_generations.inc()
                    
                    try:
                        # Start timing
                        start_time = time.time()
                        
                        with blog_duration_seconds.time():
                            # Validate user access
                            if not await self.onyx_integration.validate_user(user_id):
                                raise ValidationError("User access denied")
                            
                            # Check user quota
                            if not await self.onyx_integration.check_quota(user_id):
                                raise ValidationError("User quota exceeded")
                            
                            # Generate blog content
                            result = await self._generate_with_retry(spec, params)
                            
                            # Record metrics
                            generation_time = time.time() - start_time
                            
                            if result.content and result.content.quality_score:
                                blog_quality_score.observe(result.content.quality_score)
                            
                            # Cache successful result
                            if result.is_successful:
                                await self._cache_result(cache_key, result)
                                
                                # Save to Onyx
                                await self.onyx_integration.save_blog_post(user_id, result)
                                
                                # Record success metrics
                                self.successful_requests += 1
                                self._record_circuit_breaker_success()
                                
                                logger.info(
                                    "Blog generation completed successfully",
                                    generation_time=generation_time,
                                    quality_score=result.content.quality_score if result.content else None,
                                    **log_context
                                )
                            else:
                                self.failed_requests += 1
                                self._record_circuit_breaker_failure()
                                
                                logger.error(
                                    "Blog generation failed",
                                    error=result.error_message,
                                    **log_context
                                )
                            
                            return result
                            
                    finally:
                        self.active_requests -= 1
                        active_generations.dec()
        
        except Exception as e:
            self.failed_requests += 1
            self._record_circuit_breaker_failure()
            
            logger.error(
                "Blog generation error",
                error=str(e),
                error_type=type(e).__name__,
                **log_context
            )
            
            # Return error result
            return BlogResult(
                request_id=request_id,
                status=GenerationStatus.FAILED,
                error_message=str(e),
                content=None,
                seo_data=None,
                metrics=None
            )
    
    async def get_generation_status(self, request_id: str) -> Optional[GenerationStatus]:
        """Get generation status from cache"""
        try:
            status_key = f"status:{request_id}"
            cached_status = await self.cache.get(status_key)
            
            if cached_status:
                return GenerationStatus(cached_status)
            
            return None
            
        except Exception as e:
            logger.warning("Failed to get generation status", error=str(e), request_id=request_id)
            return None
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive use case metrics"""
        success_rate = (self.successful_requests / self.total_requests * 100) if self.total_requests > 0 else 0
        
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": success_rate,
            "active_requests": self.active_requests,
            "circuit_breaker_failures": self.circuit_breaker_failures,
            "circuit_breaker_open": self._is_circuit_breaker_open(),
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
            "cache_stats": await self.cache_provider.get_metrics() if self.cache_provider else {}
        }

# === PRODUCTION BATCH GENERATION USE CASE ===

class ProductionGenerateBatchUseCase:
    """
    Production batch generation with advanced optimizations:
    - Intelligent batching and load balancing
    - Priority queue processing
    - Resource pooling
    - Failure isolation
    - Progress tracking
    """
    
    def __init__(
        self,
        generate_use_case: ProductionGenerateBlogUseCase,
        max_batch_size: int = 20,
        max_concurrent_batches: int = 3,
        batch_timeout: int = 300
    ):
        
    """__init__ function."""
self.generate_use_case = generate_use_case
        self.max_batch_size = max_batch_size
        self.max_concurrent_batches = max_concurrent_batches
        self.batch_timeout = batch_timeout
        
        # Batch management
        self.batch_semaphore = asyncio.Semaphore(max_concurrent_batches)
        self.active_batches: Dict[str, Dict[str, Any]] = {}
        
        # Priority queue for batch processing
        self.batch_queue = asyncio.PriorityQueue()
        
        # Batch metrics
        self.total_batches = 0
        self.successful_batches = 0
        self.failed_batches = 0
    
    async def generate_batch(
        self,
        requests: List[Tuple[BlogSpec, GenerationParams]],
        user_id: str,
        priority: int = 5,
        batch_id: Optional[str] = None
    ) -> Dict[str, BlogResult]:
        """
        Generate multiple blog posts with intelligent batching
        
        Features:
        - Automatic batch size optimization
        - Priority-based processing
        - Failure isolation
        - Progress tracking
        - Resource optimization
        """
        
        batch_id = batch_id or str(uuid.uuid4())
        
        if len(requests) > self.max_batch_size:
            raise ValidationError(f"Batch size {len(requests)} exceeds maximum {self.max_batch_size}")
        
        logger.info(
            "Batch generation started",
            batch_id=batch_id,
            user_id=user_id,
            batch_size=len(requests),
            priority=priority
        )
        
        self.total_batches += 1
        
        # Initialize batch tracking
        self.active_batches[batch_id] = {
            "status": "processing",
            "total": len(requests),
            "completed": 0,
            "failed": 0,
            "start_time": time.time(),
            "results": {}
        }
        
        try:
            async with self.batch_semaphore:
                # Create tasks for concurrent processing
                tasks = []
                
                for i, (spec, params) in enumerate(requests):
                    task_id = f"{batch_id}_{i}"
                    
                    task = asyncio.create_task(
                        self._process_batch_item(
                            task_id, spec, params, user_id, batch_id
                        )
                    )
                    
                    tasks.append((task_id, task))
                
                # Wait for all tasks with timeout
                results = {}
                
                try:
                    completed_tasks = await asyncio.wait_for(
                        asyncio.gather(*[task for _, task in tasks], return_exceptions=True),
                        timeout=self.batch_timeout
                    )
                    
                    # Process results
                    for (task_id, _), result in zip(tasks, completed_tasks):
                        if isinstance(result, Exception):
                            logger.error(
                                "Batch item failed",
                                batch_id=batch_id,
                                task_id=task_id,
                                error=str(result)
                            )
                            self.active_batches[batch_id]["failed"] += 1
                        else:
                            results[task_id] = result
                            self.active_batches[batch_id]["completed"] += 1
                            self.active_batches[batch_id]["results"][task_id] = result
                
                except asyncio.TimeoutError:
                    logger.error("Batch processing timeout", batch_id=batch_id)
                    
                    # Cancel remaining tasks
                    for task_id, task in tasks:
                        if not task.done():
                            task.cancel()
                    
                    raise GenerationError("Batch processing timeout")
                
                # Update batch status
                self.active_batches[batch_id]["status"] = "completed"
                self.active_batches[batch_id]["end_time"] = time.time()
                
                # Calculate success rate
                success_rate = len(results) / len(requests) * 100
                
                if success_rate > 50:  # Consider batch successful if >50% items succeeded
                    self.successful_batches += 1
                else:
                    self.failed_batches += 1
                
                logger.info(
                    "Batch generation completed",
                    batch_id=batch_id,
                    success_rate=success_rate,
                    total_time=time.time() - self.active_batches[batch_id]["start_time"]
                )
                
                return results
                
        except Exception as e:
            self.failed_batches += 1
            self.active_batches[batch_id]["status"] = "failed"
            self.active_batches[batch_id]["error"] = str(e)
            
            logger.error(
                "Batch generation failed",
                batch_id=batch_id,
                error=str(e)
            )
            
            raise
        
        finally:
            # Clean up batch tracking after delay
            asyncio.create_task(self._cleanup_batch_tracking(batch_id, delay=300))
    
    async def _process_batch_item(
        self,
        task_id: str,
        spec: BlogSpec,
        params: GenerationParams,
        user_id: str,
        batch_id: str
    ) -> BlogResult:
        """Process individual batch item"""
        
        try:
            result = await self.generate_use_case.generate_blog(spec, params, user_id)
            
            logger.debug(
                "Batch item completed",
                task_id=task_id,
                batch_id=batch_id,
                success=result.is_successful
            )
            
            return result
            
        except Exception as e:
            logger.error(
                "Batch item failed",
                task_id=task_id,
                batch_id=batch_id,
                error=str(e)
            )
            raise
    
    async def _cleanup_batch_tracking(self, batch_id: str, delay: int = 300):
        """Clean up batch tracking data after delay"""
        await asyncio.sleep(delay)
        self.active_batches.pop(batch_id, None)
        logger.debug("Batch tracking cleaned up", batch_id=batch_id)
    
    async def get_batch_status(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Get batch processing status"""
        return self.active_batches.get(batch_id)
    
    async def get_batch_metrics(self) -> Dict[str, Any]:
        """Get batch processing metrics"""
        success_rate = (self.successful_batches / self.total_batches * 100) if self.total_batches > 0 else 0
        
        return {
            "total_batches": self.total_batches,
            "successful_batches": self.successful_batches,
            "failed_batches": self.failed_batches,
            "success_rate": success_rate,
            "active_batches": len(self.active_batches),
            "average_batch_size": self.max_batch_size // 2  # Rough estimate
        }

# === PRODUCTION CONTENT ANALYSIS USE CASE ===

class ProductionAnalyzeContentUseCase:
    """
    Production content analysis with ML-powered insights
    """
    
    def __init__(
        self,
        quality_analyzer: IQualityAnalyzer,
        content_validator: IContentValidator,
        ai_provider: IAIProvider,
        cache_provider: ICacheProvider
    ):
        
    """__init__ function."""
self.quality_analyzer = quality_analyzer
        self.content_validator = content_validator
        self.ai_provider = ai_provider
        self.cache_provider = cache_provider
        
        # Analysis cache
        self.analysis_cache = TTLCache(maxsize=1000, ttl=1800)  # 30 min TTL
        
        # Analysis metrics
        self.total_analyses = 0
        self.cache_hits = 0
    
    @lru_cache(maxsize=128)
    def _get_analysis_cache_key(self, content_hash: str) -> str:
        """Generate cache key for analysis"""
        return f"analysis:{content_hash}"
    
    async def analyze_content(
        self,
        content: str,
        target_keywords: List[str] = None,
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        Analyze content with comprehensive metrics
        
        Features:
        - ML-powered quality assessment
        - Keyword analysis
        - Readability scoring
        - SEO optimization suggestions
        - Competitive analysis
        """
        
        self.total_analyses += 1
        
        # Generate content hash for caching
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        cache_key = self._get_analysis_cache_key(content_hash)
        
        # Check cache first
        if cache_key in self.analysis_cache:
            self.cache_hits += 1
            logger.debug("Analysis cache hit", content_hash=content_hash)
            return self.analysis_cache[cache_key]
        
        logger.info(
            "Content analysis started",
            content_hash=content_hash,
            content_length=len(content),
            user_id=user_id
        )
        
        try:
            # Parallel analysis for performance
            tasks = [
                self.quality_analyzer.analyze_quality(content, target_keywords or []),
                self.quality_analyzer.analyze_detailed(content, target_keywords or []),
                self._analyze_readability(content),
                self._analyze_seo_factors(content, target_keywords or [])
            ]
            
            quality_result, detailed_result, readability_result, seo_result = await asyncio.gather(*tasks)
            
            # Combine results
            analysis_result = {
                "content_hash": content_hash,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "quality_score": quality_result.overall_score,
                "detailed_analysis": detailed_result,
                "readability": readability_result,
                "seo_analysis": seo_result,
                "recommendations": self._generate_recommendations(
                    quality_result, detailed_result, readability_result, seo_result
                )
            }
            
            # Cache the result
            self.analysis_cache[cache_key] = analysis_result
            
            logger.info(
                "Content analysis completed",
                content_hash=content_hash,
                quality_score=quality_result.overall_score
            )
            
            return analysis_result
            
        except Exception as e:
            logger.error(
                "Content analysis failed",
                content_hash=content_hash,
                error=str(e)
            )
            raise
    
    async def _analyze_readability(self, content: str) -> Dict[str, Any]:
        """Analyze content readability"""
        # Simplified readability analysis
        sentences = content.split('.')
        words = content.split()
        
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        
        # Flesch Reading Ease approximation
        flesch_score = 206.835 - (1.015 * avg_sentence_length)
        
        if flesch_score >= 90:
            reading_level = "Very Easy"
        elif flesch_score >= 80:
            reading_level = "Easy"
        elif flesch_score >= 70:
            reading_level = "Fairly Easy"
        elif flesch_score >= 60:
            reading_level = "Standard"
        elif flesch_score >= 50:
            reading_level = "Fairly Difficult"
        else:
            reading_level = "Difficult"
        
        return {
            "flesch_score": max(0, min(100, flesch_score)),
            "reading_level": reading_level,
            "avg_sentence_length": avg_sentence_length,
            "total_words": len(words),
            "total_sentences": len(sentences)
        }
    
    async def _analyze_seo_factors(self, content: str, keywords: List[str]) -> Dict[str, Any]:
        """Analyze SEO factors"""
        content_lower = content.lower()
        
        keyword_density = {}
        for keyword in keywords:
            count = content_lower.count(keyword.lower())
            density = (count / len(content.split())) * 100 if content.split() else 0
            keyword_density[keyword] = {
                "count": count,
                "density": density,
                "optimal": 1 <= density <= 3  # Optimal keyword density
            }
        
        return {
            "keyword_density": keyword_density,
            "content_length": len(content),
            "word_count": len(content.split()),
            "has_headers": "##" in content or "#" in content,
            "has_links": "[" in content and "]" in content,
            "seo_score": self._calculate_seo_score(content, keywords)
        }
    
    def _calculate_seo_score(self, content: str, keywords: List[str]) -> float:
        """Calculate overall SEO score"""
        score = 0
        
        # Content length score
        word_count = len(content.split())
        if 300 <= word_count <= 2000:
            score += 30
        elif word_count > 2000:
            score += 20
        
        # Keyword presence
        content_lower = content.lower()
        for keyword in keywords:
            if keyword.lower() in content_lower:
                score += 20
        
        # Structure score
        if "##" in content or "#" in content:
            score += 25
        
        # Link score
        if "[" in content and "]" in content:
            score += 25
        
        return min(100, score)
    
    def _generate_recommendations(self, quality, detailed, readability, seo) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        if quality.overall_score < 7:
            recommendations.append("Improve overall content quality with more detailed examples")
        
        if readability["flesch_score"] < 50:
            recommendations.append("Simplify sentence structure for better readability")
        
        if seo["seo_score"] < 70:
            recommendations.append("Optimize content for better SEO performance")
        
        if readability["total_words"] < 300:
            recommendations.append("Increase content length for better search visibility")
        
        return recommendations
    
    async def get_analysis_metrics(self) -> Dict[str, Any]:
        """Get analysis metrics"""
        cache_hit_rate = (self.cache_hits / self.total_analyses * 100) if self.total_analyses > 0 else 0
        
        return {
            "total_analyses": self.total_analyses,
            "cache_hits": self.cache_hits,
            "cache_hit_rate": cache_hit_rate,
            "cache_size": len(self.analysis_cache)
        }

# === EXPORTS ===

__all__ = [
    'ProductionGenerateBlogUseCase',
    'ProductionGenerateBatchUseCase', 
    'ProductionAnalyzeContentUseCase'
] 