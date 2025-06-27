"""
Application Layer - Use Cases
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from ..models.facebook_models import (
    FacebookPostEntity, FacebookPostRequest, FacebookPostResponse,
    FacebookPostAnalysis, ContentStatus
)
from ..domain.entities import FacebookPostDomainEntity
from ..core.facebook_engine import FacebookPostEngine


class GeneratePostUseCase:
    """Caso de uso: Generar Facebook post."""
    
    def __init__(self, facebook_engine: FacebookPostEngine):
        self.facebook_engine = facebook_engine
        self.logger = logging.getLogger(__name__)
    
    async def execute(self, request: FacebookPostRequest) -> FacebookPostResponse:
        """Ejecutar generación de post."""
        try:
            self.logger.info(f"Executing post generation for topic: {request.topic}")
            
            # Validate request
            self._validate_request(request)
            
            # Generate post using engine
            response = await self.facebook_engine.generate_post(request)
            
            self.logger.info("Post generation completed successfully")
            return response
            
        except Exception as e:
            self.logger.error(f"Error in post generation use case: {e}")
            return FacebookPostResponse(
                success=False,
                post=None,
                variations=[],
                analysis=None,
                recommendations=[],
                processing_time_ms=0.0,
                error_message=str(e)
            )
    
    def _validate_request(self, request: FacebookPostRequest) -> None:
        """Validar solicitud."""
        if not request.topic or len(request.topic.strip()) < 3:
            raise ValueError("Topic must be at least 3 characters long")
        
        if request.max_length < 50 or request.max_length > 2000:
            raise ValueError("Max length must be between 50 and 2000 characters")


class AnalyzePostUseCase:
    """Caso de uso: Analizar post existente."""
    
    def __init__(self, facebook_engine: FacebookPostEngine):
        self.facebook_engine = facebook_engine
        self.logger = logging.getLogger(__name__)
    
    async def execute(self, post: FacebookPostEntity) -> FacebookPostAnalysis:
        """Ejecutar análisis de post."""
        try:
            self.logger.info(f"Executing post analysis for: {post.identifier.content_id}")
            
            # Analyze using engine
            analysis = await self.facebook_engine.analyze_post(post)
            
            # Update post with analysis
            post.set_analysis(analysis)
            
            self.logger.info("Post analysis completed successfully")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error in post analysis use case: {e}")
            raise


class ApprovePostUseCase:
    """Caso de uso: Aprobar post para publicación."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def execute(
        self, 
        post: FacebookPostEntity, 
        approver_id: str,
        notes: Optional[str] = None
    ) -> bool:
        """Ejecutar aprobación de post."""
        try:
            self.logger.info(f"Executing post approval for: {post.identifier.content_id}")
            
            # Validate post is ready for approval
            validation_errors = post.validate_for_publication()
            if validation_errors:
                raise ValueError(f"Post cannot be approved: {'; '.join(validation_errors)}")
            
            # Update status
            post.update_status(ContentStatus.APPROVED, approver_id)
            
            # Add trace
            post.add_langchain_trace("post_approved", {
                "approver_id": approver_id,
                "notes": notes,
                "approval_time": datetime.now().isoformat()
            })
            
            self.logger.info("Post approval completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in post approval use case: {e}")
            raise


class GetAnalyticsUseCase:
    """Caso de uso: Obtener analytics."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def execute(
        self,
        workspace_id: str,
        date_from: datetime,
        date_to: datetime
    ) -> Dict[str, Any]:
        """Ejecutar obtención de analytics."""
        try:
            self.logger.info(f"Executing analytics retrieval for workspace: {workspace_id}")
            
            # Mock analytics for now
            analytics = {
                "workspace_id": workspace_id,
                "period": {
                    "from": date_from.isoformat(),
                    "to": date_to.isoformat()
                },
                "summary": {
                    "total_posts": 25,
                    "average_engagement": 0.72,
                    "top_topics": ["Digital Marketing", "Leadership"],
                    "engagement_trend": "increasing"
                },
                "generated_at": datetime.now().isoformat()
            }
            
            self.logger.info("Analytics retrieval completed successfully")
            return analytics
            
        except Exception as e:
            self.logger.error(f"Error in analytics use case: {e}")
            raise 