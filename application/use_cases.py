"""
🎯 Facebook Posts - Application Use Cases (Onyx Compatible)
==========================================================

Casos de uso de aplicación siguiendo Clean Architecture y patterns Onyx.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import asyncio
import logging

from ..domain.entities import (
    FacebookPostEntity, PostSpecification, PostContent, 
    PostAnalysis, ContentStatus, EngagementTier
)


# ===== USE CASE INTERFACES =====

class GeneratePostUseCase(ABC):
    """Caso de uso: Generar post de Facebook."""
    
    @abstractmethod
    async def execute(
        self, 
        specification: PostSpecification,
        user_id: Optional[str] = None,
        workspace_id: Optional[str] = None
    ) -> FacebookPostEntity:
        """Generar post completo con análisis."""
        pass


class AnalyzePostUseCase(ABC):
    """Caso de uso: Analizar post existente."""
    
    @abstractmethod
    async def execute(
        self, 
        post: FacebookPostEntity,
        analysis_types: Optional[List[str]] = None
    ) -> PostAnalysis:
        """Analizar post y actualizar entidad."""
        pass


class OptimizePostUseCase(ABC):
    """Caso de uso: Optimizar post para mejor engagement."""
    
    @abstractmethod
    async def execute(
        self, 
        post: FacebookPostEntity,
        target_engagement: Optional[EngagementTier] = None
    ) -> FacebookPostEntity:
        """Optimizar contenido del post."""
        pass


class BatchGenerateUseCase(ABC):
    """Caso de uso: Generar múltiples posts."""
    
    @abstractmethod
    async def execute(
        self,
        specifications: List[PostSpecification],
        max_concurrency: int = 5,
        user_id: Optional[str] = None
    ) -> List[FacebookPostEntity]:
        """Generar posts en paralelo."""
        pass


class PublishPostUseCase(ABC):
    """Caso de uso: Publicar post."""
    
    @abstractmethod
    async def execute(
        self,
        post_id: str,
        user_id: str,
        scheduled_time: Optional[datetime] = None
    ) -> bool:
        """Publicar post en Facebook."""
        pass


# ===== CONCRETE IMPLEMENTATIONS =====

class GeneratePostUseCaseImpl(GeneratePostUseCase):
    """Implementación del caso de uso de generación."""
    
    def __init__(
        self,
        content_generator,
        content_analyzer,
        post_repository,
        langchain_service,
        logger: Optional[logging.Logger] = None
    ):
        self.content_generator = content_generator
        self.content_analyzer = content_analyzer
        self.post_repository = post_repository
        self.langchain_service = langchain_service
        self.logger = logger or logging.getLogger(__name__)
    
    async def execute(
        self, 
        specification: PostSpecification,
        user_id: Optional[str] = None,
        workspace_id: Optional[str] = None
    ) -> FacebookPostEntity:
        """Generar post completo con análisis automático."""
        
        start_time = datetime.now()
        self.logger.info(f"Starting post generation for topic: {specification.topic}")
        
        try:
            # Step 1: Generate initial content
            self.logger.debug("Generating initial content...")
            content = await self.content_generator.generate_content(specification)
            
            # Step 2: Create post entity
            from ..domain.entities import PostIdentifier, FacebookPostFactory
            identifier = PostIdentifier.generate(content.text)
            
            post = FacebookPostEntity(
                identifier=identifier,
                specification=specification,
                content=content,
                onyx_user_id=user_id,
                onyx_workspace_id=workspace_id
            )
            
            # Step 3: Add generation trace
            post.add_langchain_trace("content_generated", {
                "content_length": len(content.text),
                "hashtags_count": len(content.hashtags),
                "generator_config": specification.dict()
            })
            
            # Step 4: Analyze generated content
            self.logger.debug("Analyzing generated content...")
            analysis = await self.content_analyzer.analyze_content(post)
            post.set_analysis(analysis)
            
            # Step 5: Save to repository
            saved = await self.post_repository.save(post)
            if not saved:
                raise Exception("Failed to save generated post")
            
            # Step 6: Log completion
            duration = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.info(
                f"Post generation completed in {duration:.2f}ms. "
                f"Quality score: {analysis.get_overall_score():.2f}"
            )
            
            post.add_langchain_trace("generation_completed", {
                "duration_ms": duration,
                "overall_score": analysis.get_overall_score(),
                "status": "success"
            })
            
            return post
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.error(f"Post generation failed after {duration:.2f}ms: {str(e)}")
            raise


class AnalyzePostUseCaseImpl(AnalyzePostUseCase):
    """Implementación del análisis de posts."""
    
    def __init__(
        self,
        content_analyzer,
        post_repository,
        logger: Optional[logging.Logger] = None
    ):
        self.content_analyzer = content_analyzer
        self.post_repository = post_repository
        self.logger = logger or logging.getLogger(__name__)
    
    async def execute(
        self, 
        post: FacebookPostEntity,
        analysis_types: Optional[List[str]] = None
    ) -> PostAnalysis:
        """Analizar post existente con tipos específicos."""
        
        start_time = datetime.now()
        self.logger.info(f"Starting analysis for post: {post.identifier.post_id}")
        
        try:
            # Perform analysis
            analysis = await self.content_analyzer.analyze_content(
                post, 
                analysis_types or ["comprehensive"]
            )
            
            # Update post with analysis
            post.set_analysis(analysis)
            
            # Save updated post
            await self.post_repository.save(post)
            
            duration = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.info(
                f"Analysis completed in {duration:.2f}ms. "
                f"Score: {analysis.get_overall_score():.2f}"
            )
            
            return analysis
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.error(f"Analysis failed after {duration:.2f}ms: {str(e)}")
            raise


class OptimizePostUseCaseImpl(OptimizePostUseCase):
    """Implementación de optimización de posts."""
    
    def __init__(
        self,
        content_optimizer,
        content_analyzer,
        post_repository,
        logger: Optional[logging.Logger] = None
    ):
        self.content_optimizer = content_optimizer
        self.content_analyzer = content_analyzer
        self.post_repository = post_repository
        self.logger = logger or logging.getLogger(__name__)
    
    async def execute(
        self, 
        post: FacebookPostEntity,
        target_engagement: Optional[EngagementTier] = None
    ) -> FacebookPostEntity:
        """Optimizar post para mejor engagement."""
        
        start_time = datetime.now()
        self.logger.info(f"Starting optimization for post: {post.identifier.post_id}")
        
        try:
            # Store original content for comparison
            original_content = post.content
            original_score = post.analysis.get_overall_score() if post.analysis else 0.0
            
            # Optimize content
            target = target_engagement or post.specification.target_engagement
            optimized_content = await self.content_optimizer.optimize_for_engagement(
                post.content, 
                target
            )
            
            # Update post content
            post.update_content(optimized_content)
            
            # Re-analyze optimized content
            new_analysis = await self.content_analyzer.analyze_content(post)
            post.set_analysis(new_analysis)
            
            # Save optimized post
            await self.post_repository.save(post)
            
            # Log optimization results
            new_score = new_analysis.get_overall_score()
            improvement = new_score - original_score
            
            duration = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.info(
                f"Optimization completed in {duration:.2f}ms. "
                f"Score improved from {original_score:.2f} to {new_score:.2f} "
                f"(+{improvement:.2f})"
            )
            
            post.add_langchain_trace("content_optimized", {
                "original_score": original_score,
                "new_score": new_score,
                "improvement": improvement,
                "target_engagement": target.value,
                "duration_ms": duration
            })
            
            return post
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.error(f"Optimization failed after {duration:.2f}ms: {str(e)}")
            raise


class BatchGenerateUseCaseImpl(BatchGenerateUseCase):
    """Implementación de generación en lote."""
    
    def __init__(
        self,
        generate_use_case: GeneratePostUseCase,
        logger: Optional[logging.Logger] = None
    ):
        self.generate_use_case = generate_use_case
        self.logger = logger or logging.getLogger(__name__)
    
    async def execute(
        self,
        specifications: List[PostSpecification],
        max_concurrency: int = 5,
        user_id: Optional[str] = None
    ) -> List[FacebookPostEntity]:
        """Generar múltiples posts en paralelo."""
        
        start_time = datetime.now()
        total_specs = len(specifications)
        self.logger.info(f"Starting batch generation of {total_specs} posts")
        
        # Create semaphore to limit concurrency
        semaphore = asyncio.Semaphore(max_concurrency)
        
        async def generate_single(spec: PostSpecification) -> FacebookPostEntity:
            async with semaphore:
                return await self.generate_use_case.execute(spec, user_id)
        
        try:
            # Execute all generations concurrently
            tasks = [generate_single(spec) for spec in specifications]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Separate successful and failed results
            successful_posts = []
            failed_count = 0
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.error(
                        f"Failed to generate post {i+1}/{total_specs}: {str(result)}"
                    )
                    failed_count += 1
                else:
                    successful_posts.append(result)
            
            duration = (datetime.now() - start_time).total_seconds() * 1000
            success_rate = len(successful_posts) / total_specs * 100
            
            self.logger.info(
                f"Batch generation completed in {duration:.2f}ms. "
                f"Success rate: {success_rate:.1f}% "
                f"({len(successful_posts)}/{total_specs} successful)"
            )
            
            return successful_posts
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.error(f"Batch generation failed after {duration:.2f}ms: {str(e)}")
            raise


class PublishPostUseCaseImpl(PublishPostUseCase):
    """Implementación de publicación de posts."""
    
    def __init__(
        self,
        post_repository,
        facebook_api_client,
        logger: Optional[logging.Logger] = None
    ):
        self.post_repository = post_repository
        self.facebook_api_client = facebook_api_client
        self.logger = logger or logging.getLogger(__name__)
    
    async def execute(
        self,
        post_id: str,
        user_id: str,
        scheduled_time: Optional[datetime] = None
    ) -> bool:
        """Publicar post en Facebook."""
        
        start_time = datetime.now()
        self.logger.info(f"Starting publication of post: {post_id}")
        
        try:
            # Retrieve post
            post = await self.post_repository.find_by_id(post_id)
            if not post:
                raise ValueError(f"Post not found: {post_id}")
            
            # Validate post is ready for publication
            validation_errors = post.validate_for_publication()
            if validation_errors:
                raise ValueError(f"Post validation failed: {', '.join(validation_errors)}")
            
            # Check if scheduled or immediate publication
            if scheduled_time:
                # Schedule post
                success = await self.facebook_api_client.schedule_post(
                    post.content.get_display_text(),
                    scheduled_time,
                    media_urls=post.content.media_urls
                )
                new_status = ContentStatus.SCHEDULED
            else:
                # Publish immediately
                success = await self.facebook_api_client.publish_post(
                    post.content.get_display_text(),
                    media_urls=post.content.media_urls
                )
                new_status = ContentStatus.PUBLISHED
            
            if success:
                # Update post status
                post.update_status(new_status, user_id)
                await self.post_repository.save(post)
                
                duration = (datetime.now() - start_time).total_seconds() * 1000
                self.logger.info(
                    f"Post publication successful in {duration:.2f}ms. "
                    f"Status: {new_status.value}"
                )
                
                return True
            else:
                raise Exception("Facebook API publication failed")
                
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.error(f"Publication failed after {duration:.2f}ms: {str(e)}")
            return False


# ===== ADVANCED USE CASES =====

class GenerateVariationsUseCase:
    """Caso de uso: Generar variaciones A/B."""
    
    def __init__(
        self,
        content_generator,
        content_analyzer,
        post_repository,
        logger: Optional[logging.Logger] = None
    ):
        self.content_generator = content_generator
        self.content_analyzer = content_analyzer
        self.post_repository = post_repository
        self.logger = logger or logging.getLogger(__name__)
    
    async def execute(
        self,
        base_post: FacebookPostEntity,
        variation_count: int = 3,
        variation_types: Optional[List[str]] = None
    ) -> List[FacebookPostEntity]:
        """Generar variaciones A/B del post base."""
        
        start_time = datetime.now()
        self.logger.info(f"Generating {variation_count} variations for post: {base_post.identifier.post_id}")
        
        try:
            # Generate content variations
            variations = await self.content_generator.generate_variations(
                base_post.content,
                variation_count,
                variation_types or ["tone", "length", "hashtags"]
            )
            
            # Create post entities for each variation
            variation_posts = []
            
            for i, variation_content in enumerate(variations):
                # Create variation identifier
                from ..domain.entities import PostIdentifier
                identifier = PostIdentifier.generate(variation_content.text)
                
                # Create variation post
                variation_post = FacebookPostEntity(
                    identifier=identifier,
                    specification=base_post.specification,
                    content=variation_content,
                    parent_id=base_post.identifier.post_id,  # Link to parent
                    onyx_user_id=base_post.onyx_user_id,
                    onyx_workspace_id=base_post.onyx_workspace_id
                )
                
                # Analyze variation
                analysis = await self.content_analyzer.analyze_content(variation_post)
                variation_post.set_analysis(analysis)
                
                # Save variation
                await self.post_repository.save(variation_post)
                
                variation_post.add_langchain_trace("variation_created", {
                    "parent_id": base_post.identifier.post_id,
                    "variation_index": i,
                    "variation_score": analysis.get_overall_score()
                })
                
                variation_posts.append(variation_post)
            
            duration = (datetime.now() - start_time).total_seconds() * 1000
            avg_score = sum(p.analysis.get_overall_score() for p in variation_posts) / len(variation_posts)
            
            self.logger.info(
                f"Generated {len(variation_posts)} variations in {duration:.2f}ms. "
                f"Average quality score: {avg_score:.2f}"
            )
            
            return variation_posts
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.error(f"Variation generation failed after {duration:.2f}ms: {str(e)}")
            raise


class PerformanceTrackingUseCase:
    """Caso de uso: Tracking de performance de posts."""
    
    def __init__(
        self,
        post_repository,
        facebook_api_client,
        logger: Optional[logging.Logger] = None
    ):
        self.post_repository = post_repository
        self.facebook_api_client = facebook_api_client
        self.logger = logger or logging.getLogger(__name__)
    
    async def execute(
        self,
        post_ids: List[str],
        update_predictions: bool = True
    ) -> Dict[str, Dict[str, Any]]:
        """Actualizar métricas reales de performance."""
        
        self.logger.info(f"Tracking performance for {len(post_ids)} posts")
        results = {}
        
        for post_id in post_ids:
            try:
                # Get post
                post = await self.post_repository.find_by_id(post_id)
                if not post or post.status != ContentStatus.PUBLISHED:
                    continue
                
                # Get real metrics from Facebook API
                metrics = await self.facebook_api_client.get_post_metrics(post_id)
                
                if metrics:
                    # Update post with real metrics
                    post.set_actual_metrics(
                        likes=metrics.get("likes", 0),
                        shares=metrics.get("shares", 0),
                        comments=metrics.get("comments", 0),
                        reach=metrics.get("reach", 0)
                    )
                    
                    # Calculate prediction accuracy
                    accuracy = post.get_performance_comparison()
                    
                    await self.post_repository.save(post)
                    
                    results[post_id] = {
                        "metrics": metrics,
                        "prediction_accuracy": accuracy,
                        "status": "updated"
                    }
                    
                    self.logger.debug(f"Updated metrics for post {post_id}")
                
            except Exception as e:
                self.logger.error(f"Failed to update metrics for post {post_id}: {str(e)}")
                results[post_id] = {
                    "status": "failed",
                    "error": str(e)
                }
        
        return results 