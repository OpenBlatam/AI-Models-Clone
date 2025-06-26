"""
Speed Optimizer for Ultra-Fast Blog Generation.

Implements advanced caching, parallel processing, and optimization techniques
for maximum content generation speed without compromising quality.
"""

import asyncio
import time
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import structlog

from ...models import ContentRequest, ContentGenerationResult
from ...config import BlogPostConfig
from .generator import ContentGeneratorService

logger = structlog.get_logger(__name__)


@dataclass
class SpeedMetrics:
    """Metrics for speed optimization tracking."""
    generation_time_ms: int
    cache_hit_rate: float
    parallel_efficiency: float
    throughput_per_second: float
    optimization_level: str


class TurboContentGenerator(ContentGeneratorService):
    """Ultra-fast content generator with advanced speed optimizations."""
    
    def __init__(self, config: BlogPostConfig):
        super().__init__(config)
        self.logger = logger.bind(service="turbo_generator")
        
        # Speed optimization components
        self.content_cache = {}
        self.template_cache = {}
        self.pattern_cache = {}
        self.semantic_cache = {}
        
        # Parallel processing setup
        self.max_workers = min(32, (config.max_concurrent_generations or 4) * 4)
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        
        # Pre-compiled templates and patterns
        self.precompiled_templates = self._precompile_templates()
        self.content_patterns = self._load_content_patterns()
        
        # Performance tracking
        self.speed_metrics = []
        self.cache_stats = {"hits": 0, "misses": 0}
        
    async def turbo_generate(
        self, 
        request: ContentRequest,
        speed_mode: str = "ultra"  # "fast", "ultra", "ludicrous"
    ) -> ContentGenerationResult:
        """Generate content with maximum speed optimizations."""
        start_time = time.time()
        
        try:
            # Step 1: Smart caching check
            cache_key = self._generate_cache_key(request)
            cached_result = await self._check_smart_cache(cache_key, request)
            
            if cached_result:
                self.cache_stats["hits"] += 1
                self.logger.info("Cache hit for turbo generation", cache_key=cache_key[:16])
                return self._finalize_cached_result(cached_result, start_time)
            
            self.cache_stats["misses"] += 1
            
            # Step 2: Parallel component generation
            generation_tasks = self._create_parallel_tasks(request, speed_mode)
            
            # Step 3: Execute all tasks concurrently
            results = await asyncio.gather(*generation_tasks, return_exceptions=True)
            
            # Step 4: Rapid assembly and optimization
            final_content = await self._rapid_assembly(results, request, speed_mode)
            
            # Step 5: Cache the result for future use
            await self._cache_result(cache_key, final_content, request)
            
            generation_time = int((time.time() - start_time) * 1000)
            
            # Track speed metrics
            self._track_speed_metrics(generation_time, speed_mode)
            
            self.logger.info(
                "Turbo generation completed",
                speed_mode=speed_mode,
                generation_time_ms=generation_time,
                cache_hit_rate=self._calculate_cache_hit_rate(),
                word_count=len(final_content["content"].split()) if final_content.get("content") else 0
            )
            
            return ContentGenerationResult(
                success=True,
                content=final_content["content"],
                title=final_content["title"],
                outline=final_content["outline"],
                seo_data=final_content["seo_data"],
                generation_time_ms=generation_time,
                word_count=len(final_content["content"].split()) if final_content.get("content") else 0,
                metadata={
                    "speed_mode": speed_mode,
                    "cache_hit": False,
                    "parallel_tasks": len(generation_tasks),
                    "optimization_level": "turbo"
                }
            )
            
        except Exception as e:
            self.logger.error("Turbo generation failed", error=str(e), speed_mode=speed_mode)
            # Fallback to standard generation
            return await super().generate_content(request)
    
    async def batch_turbo_generate(
        self, 
        requests: List[ContentRequest],
        speed_mode: str = "ultra"
    ) -> List[ContentGenerationResult]:
        """Generate multiple content pieces with maximum parallelization."""
        start_time = time.time()
        
        # Organize requests by similarity for better caching
        request_groups = self._group_similar_requests(requests)
        
        all_tasks = []
        for group in request_groups:
            # Generate one high-quality version, then create variations
            if len(group) > 1:
                # Generate base content
                base_task = self.turbo_generate(group[0], speed_mode)
                all_tasks.append(base_task)
                
                # Generate variations in parallel
                for variant_request in group[1:]:
                    variant_task = self._generate_variation(group[0], variant_request, speed_mode)
                    all_tasks.append(variant_task)
            else:
                task = self.turbo_generate(group[0], speed_mode)
                all_tasks.append(task)
        
        # Execute all tasks with controlled concurrency
        results = []
        semaphore = asyncio.Semaphore(self.max_workers)
        
        async def controlled_task(task):
            async with semaphore:
                return await task
        
        controlled_tasks = [controlled_task(task) for task in all_tasks]
        results = await asyncio.gather(*controlled_tasks, return_exceptions=True)
        
        # Filter successful results
        successful_results = [r for r in results if isinstance(r, ContentGenerationResult) and r.success]
        
        total_time = int((time.time() - start_time) * 1000)
        throughput = len(successful_results) / (total_time / 1000) if total_time > 0 else 0
        
        self.logger.info(
            "Batch turbo generation completed",
            total_requests=len(requests),
            successful_results=len(successful_results),
            total_time_ms=total_time,
            throughput_per_second=throughput,
            speed_mode=speed_mode
        )
        
        return successful_results
    
    def _create_parallel_tasks(self, request: ContentRequest, speed_mode: str) -> List[asyncio.Task]:
        """Create optimized parallel tasks for content generation."""
        
        tasks = []
        
        # Task 1: Main content generation (highest priority)
        main_content_task = asyncio.create_task(
            self._generate_main_content_fast(request, speed_mode)
        )
        tasks.append(main_content_task)
        
        # Task 2: Title generation (parallel)
        title_task = asyncio.create_task(
            self._generate_title_fast(request)
        )
        tasks.append(title_task)
        
        # Task 3: Outline generation (parallel)
        outline_task = asyncio.create_task(
            self._generate_outline_fast(request)
        )
        tasks.append(outline_task)
        
        # Task 4: SEO data generation (parallel)
        seo_task = asyncio.create_task(
            self._generate_seo_fast(request)
        )
        tasks.append(seo_task)
        
        # Task 5: Content enhancement (lower priority)
        if speed_mode in ["ultra", "ludicrous"]:
            enhancement_task = asyncio.create_task(
                self._prepare_enhancements_fast(request)
            )
            tasks.append(enhancement_task)
        
        return tasks
    
    async def _generate_main_content_fast(self, request: ContentRequest, speed_mode: str) -> str:
        """Generate main content with speed optimizations."""
        
        # Check pattern cache for similar topics
        pattern_key = self._get_pattern_key(request.topic, request.target_audience)
        if pattern_key in self.pattern_cache:
            base_pattern = self.pattern_cache[pattern_key]
            return self._customize_pattern(base_pattern, request, speed_mode)
        
        # Use pre-compiled templates for faster generation
        template_name = self._select_fast_template(request, speed_mode)
        template = self.precompiled_templates.get(template_name)
        
        if template:
            content = await self._fill_template_fast(template, request, speed_mode)
        else:
            # Fallback to dynamic generation with speed optimizations
            content = await self._dynamic_generation_fast(request, speed_mode)
        
        # Cache the pattern for future use
        self.pattern_cache[pattern_key] = content
        
        return content
    
    async def _fill_template_fast(self, template: Dict[str, Any], request: ContentRequest, speed_mode: str) -> str:
        """Fill template with content using fast algorithms."""
        
        # Speed-optimized template filling
        content_parts = []
        
        for section in template["sections"]:
            if speed_mode == "ludicrous":
                # Use cached content blocks
                section_content = self._get_cached_section(section, request)
            else:
                # Generate section content optimized for speed
                section_content = await self._generate_section_fast(section, request)
            
            content_parts.append(section_content)
        
        # Rapid assembly with minimal processing
        final_content = self._fast_assembly(content_parts, template, request)
        
        return final_content
    
    async def _generate_section_fast(self, section: str, request: ContentRequest) -> str:
        """Generate individual section content optimized for speed."""
        
        # Use section-specific fast generators
        fast_generators = {
            "introduction": lambda: self._fast_intro(request),
            "main_content": lambda: self._fast_main(request),
            "benefits": lambda: self._fast_benefits(request),
            "implementation": lambda: self._fast_implementation(request),
            "conclusion": lambda: self._fast_conclusion(request)
        }
        
        generator = fast_generators.get(section, lambda: self._fast_generic(request, section))
        
        return await asyncio.get_event_loop().run_in_executor(
            self.executor, generator
        )
    
    def _fast_intro(self, request: ContentRequest) -> str:
        """Generate introduction optimized for speed."""
        
        intro_templates = [
            f"In today's fast-paced world, {request.topic.lower()} has become essential for {request.target_audience.lower()}. This comprehensive guide will show you exactly how to master {request.topic.lower()} quickly and effectively.",
            
            f"Want to excel in {request.topic.lower()}? You're in the right place. This article provides everything {request.target_audience.lower()} need to know about {request.topic.lower()}, from basics to advanced strategies.",
            
            f"{request.topic} is transforming how {request.target_audience.lower()} approach their goals. Let's dive into the most effective strategies and techniques you can implement today."
        ]
        
        # Simple hash-based selection for consistency
        template_index = abs(hash(request.topic + request.target_audience)) % len(intro_templates)
        return intro_templates[template_index]
    
    def _fast_main(self, request: ContentRequest) -> str:
        """Generate main content optimized for speed."""
        
        return f"""
## Understanding {request.topic}

{request.topic} is a crucial skill for {request.target_audience.lower()}. Here's what you need to know:

### Key Components

1. **Foundation Building**: Start with solid fundamentals
2. **Strategic Planning**: Develop a clear roadmap
3. **Implementation**: Execute with precision
4. **Optimization**: Continuously improve results

### Best Practices

- Focus on high-impact activities
- Measure and track progress
- Stay updated with latest trends
- Learn from industry experts

### Common Mistakes to Avoid

- Lack of clear goals
- Insufficient planning
- Poor execution
- Ignoring feedback

### Advanced Strategies

For {request.target_audience.lower()} ready to take their {request.topic.lower()} skills to the next level:

- Leverage automation tools
- Implement data-driven approaches
- Build strategic partnerships
- Focus on continuous learning
        """
    
    def _fast_benefits(self, request: ContentRequest) -> str:
        """Generate benefits section optimized for speed."""
        
        return f"""
## Key Benefits of {request.topic}

Implementing {request.topic.lower()} effectively provides numerous advantages:

### Immediate Benefits
- Increased efficiency and productivity
- Better decision-making capabilities
- Reduced costs and waste
- Improved quality of results

### Long-term Advantages
- Sustainable competitive advantage
- Enhanced reputation and credibility
- Greater customer satisfaction
- Increased profitability

### Specific Benefits for {request.target_audience}
- Streamlined workflows
- Better resource utilization
- Enhanced collaboration
- Faster problem resolution
        """
    
    def _precompile_templates(self) -> Dict[str, Any]:
        """Precompile content templates for faster generation."""
        
        return {
            "speed_article": {
                "sections": ["introduction", "main_content", "benefits", "implementation", "conclusion"],
                "structure": "linear",
                "optimization": "speed"
            },
            "turbo_guide": {
                "sections": ["introduction", "overview", "detailed_steps", "tips", "conclusion"],
                "structure": "step_by_step",
                "optimization": "comprehensiveness"
            },
            "rapid_overview": {
                "sections": ["introduction", "key_points", "summary"],
                "structure": "concise",
                "optimization": "brevity"
            }
        }
    
    def _load_content_patterns(self) -> Dict[str, str]:
        """Load common content patterns for reuse."""
        
        return {
            "business_technology": "Business + Technology topics pattern",
            "marketing_strategy": "Marketing + Strategy topics pattern",
            "development_guide": "Development + Guide topics pattern"
        }
    
    async def _check_smart_cache(self, cache_key: str, request: ContentRequest) -> Optional[Dict[str, Any]]:
        """Check cache with smart similarity matching."""
        
        # Exact match first
        if cache_key in self.content_cache:
            cached_data = self.content_cache[cache_key]
            if self._is_cache_valid(cached_data):
                return cached_data
        
        # Semantic similarity check for partial matches
        similar_keys = self._find_similar_cache_keys(cache_key, request)
        for similar_key in similar_keys:
            if similar_key in self.content_cache:
                cached_data = self.content_cache[similar_key]
                if self._is_cache_valid(cached_data):
                    # Adapt cached content to current request
                    return self._adapt_cached_content(cached_data, request)
        
        return None
    
    def _generate_cache_key(self, request: ContentRequest) -> str:
        """Generate optimized cache key for request."""
        
        key_components = [
            request.topic.lower(),
            request.target_audience.lower(),
            request.tone,
            str(request.length_words or 1000),
            ','.join(sorted(request.keywords))
        ]
        
        key_string = '|'.join(key_components)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def _rapid_assembly(self, results: List[Any], request: ContentRequest, speed_mode: str) -> Dict[str, Any]:
        """Rapidly assemble all generated components."""
        
        # Extract results from completed tasks
        main_content = ""
        title = ""
        outline = []
        seo_data = None
        enhancements = {}
        
        for result in results:
            if isinstance(result, str) and len(result) > 100:  # Likely main content
                main_content = result
            elif isinstance(result, str) and len(result) < 100:  # Likely title
                title = result
            elif isinstance(result, list):  # Likely outline
                outline = result
            elif isinstance(result, dict):  # Could be SEO data or enhancements
                if "meta_description" in result:
                    seo_data = result
                else:
                    enhancements = result
        
        # Apply rapid enhancements if available
        if enhancements and speed_mode in ["ultra", "ludicrous"]:
            main_content = self._apply_rapid_enhancements(main_content, enhancements)
        
        return {
            "content": main_content,
            "title": title,
            "outline": outline,
            "seo_data": seo_data
        }
    
    def _track_speed_metrics(self, generation_time: int, speed_mode: str):
        """Track speed optimization metrics."""
        
        cache_hit_rate = self._calculate_cache_hit_rate()
        
        metrics = SpeedMetrics(
            generation_time_ms=generation_time,
            cache_hit_rate=cache_hit_rate,
            parallel_efficiency=0.85,  # Placeholder
            throughput_per_second=1000 / generation_time if generation_time > 0 else 0,
            optimization_level=speed_mode
        )
        
        self.speed_metrics.append(metrics)
        
        # Keep only last 100 metrics for performance
        if len(self.speed_metrics) > 100:
            self.speed_metrics = self.speed_metrics[-100:]
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate current cache hit rate."""
        
        total = self.cache_stats["hits"] + self.cache_stats["misses"]
        if total == 0:
            return 0.0
        
        return self.cache_stats["hits"] / total
    
    def get_speed_statistics(self) -> Dict[str, Any]:
        """Get comprehensive speed optimization statistics."""
        
        if not self.speed_metrics:
            return {"status": "no_data"}
        
        recent_metrics = self.speed_metrics[-10:]  # Last 10 generations
        
        avg_time = sum(m.generation_time_ms for m in recent_metrics) / len(recent_metrics)
        avg_throughput = sum(m.throughput_per_second for m in recent_metrics) / len(recent_metrics)
        
        return {
            "average_generation_time_ms": avg_time,
            "average_throughput_per_second": avg_throughput,
            "cache_hit_rate": self._calculate_cache_hit_rate(),
            "total_generations": len(self.speed_metrics),
            "cache_size": len(self.content_cache),
            "pattern_cache_size": len(self.pattern_cache),
            "optimization_effectiveness": "high" if avg_time < 2000 else "medium" if avg_time < 5000 else "low"
        }
    
    async def preload_cache(self, common_topics: List[str], target_audiences: List[str]):
        """Preload cache with common topic/audience combinations."""
        
        self.logger.info("Starting cache preload", topics=len(common_topics), audiences=len(target_audiences))
        
        preload_tasks = []
        for topic in common_topics:
            for audience in target_audiences:
                request = ContentRequest(
                    topic=topic,
                    target_audience=audience,
                    length_words=1000
                )
                task = self.turbo_generate(request, "fast")
                preload_tasks.append(task)
        
        # Execute preload in batches to avoid overwhelming the system
        batch_size = 5
        for i in range(0, len(preload_tasks), batch_size):
            batch = preload_tasks[i:i + batch_size]
            await asyncio.gather(*batch, return_exceptions=True)
            await asyncio.sleep(0.1)  # Small delay between batches
        
        self.logger.info("Cache preload completed", cache_size=len(self.content_cache)) 