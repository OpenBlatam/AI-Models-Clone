"""
Ultra Blog Engine - The Ultimate Blog Generation System.

Combines super quality optimization with turbo speed generation to deliver
the fastest, highest-quality blog content generation system available.
"""

import asyncio
import time
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import structlog

from .quality_optimizer import SuperQualityContentGenerator, QualityMetrics
from .speed_optimizer import TurboContentGenerator, SpeedMetrics
from .validator import ContentValidatorService
from .processor import ContentProcessorService
from ...models import ContentRequest, ContentGenerationResult
from ...config import BlogPostConfig
from ...exceptions import ContentGenerationError

logger = structlog.get_logger(__name__)


class GenerationMode(Enum):
    """Generation modes for different use cases."""
    LIGHTNING = "lightning"      # Maximum speed, good quality
    TURBO = "turbo"             # High speed, high quality
    PREMIUM = "premium"         # Balanced speed and quality
    ULTRA = "ultra"             # Maximum quality, reasonable speed
    LUDICROUS = "ludicrous"     # Maximum everything


@dataclass
class UltraMetrics:
    """Comprehensive metrics for ultra blog engine."""
    generation_time_ms: int
    quality_score: float
    speed_score: float
    optimization_efficiency: float
    user_satisfaction_estimate: float
    mode_used: str
    enhancements_applied: List[str]


class UltraBlogEngine:
    """
    The ultimate blog generation engine combining speed and quality optimizations.
    
    Features:
    - Multi-mode generation (Lightning to Ludicrous)
    - Intelligent mode selection based on requirements
    - Advanced caching and optimization
    - Real-time quality monitoring
    - Adaptive performance tuning
    """
    
    def __init__(self, config: BlogPostConfig):
        self.config = config
        self.logger = logger.bind(service="ultra_blog_engine")
        
        # Initialize all optimization engines
        self.quality_engine = SuperQualityContentGenerator(config)
        self.speed_engine = TurboContentGenerator(config)
        self.validator = ContentValidatorService(config)
        self.processor = ContentProcessorService(config)
        
        # Performance tracking
        self.generation_history = []
        self.performance_stats = {
            "total_generations": 0,
            "average_quality": 0.0,
            "average_speed": 0.0,
            "mode_usage": {mode.value: 0 for mode in GenerationMode}
        }
        
        # Intelligent mode selection parameters
        self.mode_thresholds = {
            "quality_threshold": 85.0,
            "speed_threshold": 3000,  # ms
            "user_preference_weight": 0.3
        }
    
    async def generate_ultra_blog(
        self, 
        request: ContentRequest,
        mode: Optional[GenerationMode] = None,
        priority: str = "balanced"  # "speed", "quality", "balanced"
    ) -> ContentGenerationResult:
        """
        Generate ultra-high-quality blog content with optimal speed.
        
        Args:
            request: Content generation request
            mode: Specific generation mode (auto-selected if None)
            priority: Priority focus ("speed", "quality", "balanced")
            
        Returns:
            ContentGenerationResult with enhanced metrics and optimization data
        """
        start_time = time.time()
        
        try:
            # Step 1: Intelligent mode selection
            if mode is None:
                mode = await self._select_optimal_mode(request, priority)
            
            self.logger.info(
                "Starting ultra blog generation",
                mode=mode.value,
                priority=priority,
                topic=request.topic
            )
            
            # Step 2: Pre-generation optimization
            optimized_request = await self._optimize_request(request, mode)
            
            # Step 3: Execute generation based on mode
            result = await self._execute_generation(optimized_request, mode, priority)
            
            # Step 4: Post-generation enhancements
            enhanced_result = await self._apply_post_enhancements(result, mode, optimized_request)
            
            # Step 5: Quality validation and final optimization
            validated_result = await self._validate_and_finalize(enhanced_result, optimized_request)
            
            # Step 6: Track performance and update statistics
            total_time = int((time.time() - start_time) * 1000)
            await self._track_performance(validated_result, mode, total_time, priority)
            
            self.logger.info(
                "Ultra blog generation completed",
                mode=mode.value,
                total_time_ms=total_time,
                quality_score=validated_result.metadata.get("quality_score", 0),
                word_count=validated_result.word_count
            )
            
            return validated_result
            
        except Exception as e:
            self.logger.error("Ultra blog generation failed", error=str(e), mode=mode.value if mode else "unknown")
            raise ContentGenerationError(f"Ultra blog generation failed: {str(e)}")
    
    async def batch_generate_ultra(
        self,
        requests: List[ContentRequest],
        mode: Optional[GenerationMode] = None,
        priority: str = "balanced",
        max_concurrent: Optional[int] = None
    ) -> List[ContentGenerationResult]:
        """
        Generate multiple ultra blogs with intelligent batching and optimization.
        
        Args:
            requests: List of content generation requests
            mode: Generation mode for all requests (auto-selected if None)
            priority: Priority focus for all requests
            max_concurrent: Maximum concurrent generations (auto-calculated if None)
            
        Returns:
            List of ContentGenerationResult objects
        """
        start_time = time.time()
        
        if not requests:
            return []
        
        # Optimize batch processing
        if max_concurrent is None:
            max_concurrent = min(len(requests), self.config.max_concurrent_generations or 8)
        
        self.logger.info(
            "Starting batch ultra generation",
            total_requests=len(requests),
            mode=mode.value if mode else "auto",
            max_concurrent=max_concurrent
        )
        
        # Group similar requests for better optimization
        request_groups = self._group_requests_intelligently(requests)
        
        all_results = []
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def generate_with_semaphore(req, selected_mode):
            async with semaphore:
                return await self.generate_ultra_blog(req, selected_mode, priority)
        
        # Process groups with optimized mode selection
        for group in request_groups:
            # Select optimal mode for this group
            group_mode = mode or await self._select_optimal_mode_for_group(group, priority)
            
            # Generate all requests in the group
            group_tasks = [
                generate_with_semaphore(req, group_mode) 
                for req in group
            ]
            
            group_results = await asyncio.gather(*group_tasks, return_exceptions=True)
            
            # Filter successful results
            successful_results = [
                r for r in group_results 
                if isinstance(r, ContentGenerationResult) and r.success
            ]
            
            all_results.extend(successful_results)
        
        total_time = int((time.time() - start_time) * 1000)
        success_rate = len(all_results) / len(requests) if requests else 0
        
        self.logger.info(
            "Batch ultra generation completed",
            total_requests=len(requests),
            successful_results=len(all_results),
            success_rate=success_rate,
            total_time_ms=total_time,
            throughput_per_second=len(all_results) / (total_time / 1000) if total_time > 0 else 0
        )
        
        return all_results
    
    async def _select_optimal_mode(
        self, 
        request: ContentRequest, 
        priority: str
    ) -> GenerationMode:
        """Intelligently select the optimal generation mode."""
        
        # Analyze request complexity
        complexity_score = self._calculate_request_complexity(request)
        
        # Consider user priority
        priority_weights = {
            "speed": {"speed": 0.7, "quality": 0.3},
            "quality": {"speed": 0.2, "quality": 0.8},
            "balanced": {"speed": 0.5, "quality": 0.5}
        }
        
        weights = priority_weights[priority]
        
        # Calculate optimal mode based on complexity and priority
        if complexity_score < 3 and weights["speed"] > 0.6:
            return GenerationMode.LIGHTNING
        elif complexity_score < 5 and weights["speed"] > 0.4:
            return GenerationMode.TURBO
        elif complexity_score < 7:
            return GenerationMode.PREMIUM
        elif weights["quality"] > 0.6:
            return GenerationMode.ULTRA
        else:
            return GenerationMode.LUDICROUS
    
    def _calculate_request_complexity(self, request: ContentRequest) -> int:
        """Calculate complexity score for a content request."""
        
        complexity = 0
        
        # Length complexity
        if request.length_words and request.length_words > 2000:
            complexity += 2
        elif request.length_words and request.length_words > 1000:
            complexity += 1
        
        # Topic complexity (simplified heuristic)
        complex_topics = ["artificial intelligence", "machine learning", "blockchain", "quantum computing"]
        if any(topic in request.topic.lower() for topic in complex_topics):
            complexity += 2
        
        # Keyword complexity
        if len(request.keywords) > 8:
            complexity += 2
        elif len(request.keywords) > 5:
            complexity += 1
        
        # Additional features
        if request.include_seo:
            complexity += 1
        if request.include_outline:
            complexity += 1
        if request.custom_instructions:
            complexity += 1
        
        return complexity
    
    async def _execute_generation(
        self, 
        request: ContentRequest, 
        mode: GenerationMode, 
        priority: str
    ) -> ContentGenerationResult:
        """Execute content generation based on selected mode."""
        
        generation_strategies = {
            GenerationMode.LIGHTNING: self._lightning_generation,
            GenerationMode.TURBO: self._turbo_generation,
            GenerationMode.PREMIUM: self._premium_generation,
            GenerationMode.ULTRA: self._ultra_generation,
            GenerationMode.LUDICROUS: self._ludicrous_generation
        }
        
        strategy = generation_strategies[mode]
        return await strategy(request, priority)
    
    async def _lightning_generation(self, request: ContentRequest, priority: str) -> ContentGenerationResult:
        """Lightning-fast generation with good quality."""
        return await self.speed_engine.turbo_generate(request, "fast")
    
    async def _turbo_generation(self, request: ContentRequest, priority: str) -> ContentGenerationResult:
        """High-speed generation with high quality."""
        return await self.speed_engine.turbo_generate(request, "ultra")
    
    async def _premium_generation(self, request: ContentRequest, priority: str) -> ContentGenerationResult:
        """Balanced speed and quality generation."""
        # Parallel execution of speed and quality engines, take best result
        speed_task = self.speed_engine.turbo_generate(request, "ultra")
        quality_task = self.quality_engine.generate_super_quality_content(request, "premium")
        
        speed_result, quality_result = await asyncio.gather(speed_task, quality_task, return_exceptions=True)
        
        # Select best result based on combined metrics
        if isinstance(quality_result, ContentGenerationResult) and quality_result.success:
            return quality_result
        elif isinstance(speed_result, ContentGenerationResult) and speed_result.success:
            return speed_result
        else:
            raise ContentGenerationError("Both generation engines failed")
    
    async def _ultra_generation(self, request: ContentRequest, priority: str) -> ContentGenerationResult:
        """Maximum quality generation with reasonable speed."""
        return await self.quality_engine.generate_super_quality_content(request, "premium")
    
    async def _ludicrous_generation(self, request: ContentRequest, priority: str) -> ContentGenerationResult:
        """Maximum quality and speed - the ultimate generation mode."""
        
        # Multi-stage generation with all optimizations
        
        # Stage 1: Parallel generation with multiple engines
        speed_task = self.speed_engine.turbo_generate(request, "ludicrous")
        quality_task = self.quality_engine.generate_super_quality_content(request, "premium")
        
        speed_result, quality_result = await asyncio.gather(speed_task, quality_task)
        
        # Stage 2: Combine best aspects of both results
        if quality_result.success and speed_result.success:
            combined_result = await self._combine_results(quality_result, speed_result, request)
            return combined_result
        elif quality_result.success:
            return quality_result
        elif speed_result.success:
            return speed_result
        else:
            raise ContentGenerationError("All generation engines failed in ludicrous mode")
    
    async def _combine_results(
        self, 
        quality_result: ContentGenerationResult, 
        speed_result: ContentGenerationResult,
        request: ContentRequest
    ) -> ContentGenerationResult:
        """Intelligently combine results from multiple engines."""
        
        # Use quality content with speed optimizations
        content = quality_result.content
        title = quality_result.title if len(quality_result.title) < len(speed_result.title) else speed_result.title
        outline = quality_result.outline or speed_result.outline
        seo_data = quality_result.seo_data or speed_result.seo_data
        
        # Combine metadata
        combined_metadata = {
            **quality_result.metadata,
            **speed_result.metadata,
            "generation_method": "ludicrous_combined",
            "engines_used": ["quality", "speed"],
            "combination_time": time.time()
        }
        
        return ContentGenerationResult(
            success=True,
            content=content,
            title=title,
            outline=outline,
            seo_data=seo_data,
            generation_time_ms=max(quality_result.generation_time_ms, speed_result.generation_time_ms),
            word_count=quality_result.word_count,
            metadata=combined_metadata
        )
    
    async def _optimize_request(self, request: ContentRequest, mode: GenerationMode) -> ContentRequest:
        """Optimize the request based on generation mode."""
        
        # Mode-specific optimizations
        if mode in [GenerationMode.LIGHTNING, GenerationMode.TURBO]:
            # Speed optimizations
            if not request.length_words:
                request.length_words = 800  # Shorter for speed
        elif mode in [GenerationMode.ULTRA, GenerationMode.LUDICROUS]:
            # Quality optimizations
            if not request.length_words:
                request.length_words = 1500  # Longer for quality
            
            # Enhance keywords for better SEO
            if len(request.keywords) < 5:
                request.keywords.extend(self._generate_related_keywords(request.topic))
        
        return request
    
    def _generate_related_keywords(self, topic: str) -> List[str]:
        """Generate related keywords for a topic."""
        # Simple keyword generation - in real implementation, this would be more sophisticated
        base_keywords = [
            f"{topic.lower()} guide",
            f"{topic.lower()} tips",
            f"{topic.lower()} strategies",
            f"best {topic.lower()}",
            f"{topic.lower()} examples"
        ]
        return base_keywords[:3]  # Return top 3
    
    def get_performance_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive performance dashboard data."""
        
        recent_generations = self.generation_history[-50:]  # Last 50 generations
        
        if not recent_generations:
            return {"status": "no_data", "message": "No generations recorded yet"}
        
        # Calculate performance metrics
        avg_quality = sum(g.get("quality_score", 0) for g in recent_generations) / len(recent_generations)
        avg_speed = sum(g.get("generation_time_ms", 0) for g in recent_generations) / len(recent_generations)
        
        mode_distribution = {}
        for mode in GenerationMode:
            count = sum(1 for g in recent_generations if g.get("mode") == mode.value)
            mode_distribution[mode.value] = count
        
        return {
            "total_generations": self.performance_stats["total_generations"],
            "recent_generations": len(recent_generations),
            "average_quality_score": avg_quality,
            "average_generation_time_ms": avg_speed,
            "mode_distribution": mode_distribution,
            "optimization_effectiveness": "excellent" if avg_quality > 85 and avg_speed < 3000 else "good",
            "cache_performance": self.speed_engine.get_speed_statistics(),
            "recommendations": self._generate_performance_recommendations(avg_quality, avg_speed)
        }
    
    def _generate_performance_recommendations(self, avg_quality: float, avg_speed: float) -> List[str]:
        """Generate performance improvement recommendations."""
        
        recommendations = []
        
        if avg_quality < 80:
            recommendations.append("Consider using higher quality modes for better results")
        
        if avg_speed > 5000:
            recommendations.append("Enable caching and use faster generation modes")
        
        if len(self.generation_history) > 100:
            recommendations.append("Performance is stable - consider enabling ludicrous mode")
        
        return recommendations
    
    async def optimize_for_user_preferences(self, user_feedback: Dict[str, Any]):
        """Optimize engine settings based on user feedback."""
        
        # Adjust mode selection thresholds based on feedback
        if user_feedback.get("prefer_speed", False):
            self.mode_thresholds["speed_threshold"] += 500
        
        if user_feedback.get("prefer_quality", False):
            self.mode_thresholds["quality_threshold"] -= 5
        
        # Update user preference weight
        satisfaction = user_feedback.get("satisfaction_score", 5)
        if satisfaction < 7:
            self.mode_thresholds["user_preference_weight"] += 0.1
        
        self.logger.info("Engine optimized based on user feedback", feedback=user_feedback) 