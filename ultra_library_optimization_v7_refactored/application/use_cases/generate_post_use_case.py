#!/usr/bin/env python3
"""
Generate Post Use Case - Application Layer
=========================================

Use case for generating LinkedIn posts with optimization.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass

from ...domain.entities.linkedin_post import LinkedInPost
from ...domain.value_objects.post_tone import PostTone
from ...domain.value_objects.post_length import PostLength
from ...domain.value_objects.optimization_strategy import OptimizationStrategy
from ...domain.repositories.post_repository import PostRepository


@dataclass
class GeneratePostRequest:
    """Request data for generating a LinkedIn post."""
    
    topic: str
    tone: str = "professional"
    length: str = "medium"
    include_hashtags: bool = True
    include_call_to_action: bool = True
    optimization_strategy: str = "default"
    custom_hashtags: Optional[list[str]] = None
    custom_call_to_action: Optional[str] = None
    target_audience: Optional[str] = None
    industry_context: Optional[str] = None
    content_style: Optional[str] = None


@dataclass
class GeneratePostResponse:
    """Response data for generated LinkedIn post."""
    
    post: LinkedInPost
    generation_time_ms: float
    optimization_time_ms: float
    cache_hit: bool
    optimization_score: float
    engagement_score: float
    readiness_score: float
    suggestions: list[str]
    warnings: list[str]
    metadata: Dict[str, Any]


class GeneratePostUseCase(ABC):
    """
    Abstract use case for generating LinkedIn posts.
    
    This use case orchestrates the generation of LinkedIn posts by coordinating
    between domain entities, repositories, and external services.
    """
    
    def __init__(self, post_repository: PostRepository):
        self.post_repository = post_repository
    
    @abstractmethod
    async def execute(self, request: GeneratePostRequest) -> GeneratePostResponse:
        """
        Execute the generate post use case.
        
        Args:
            request: The generate post request
            
        Returns:
            The generate post response
            
        Raises:
            UseCaseError: If use case execution fails
        """
        pass


class GeneratePostUseCaseImpl(GeneratePostUseCase):
    """
    Implementation of the generate post use case.
    
    This implementation provides the business logic for generating LinkedIn posts
    with various optimization strategies and quality checks.
    """
    
    def __init__(self, post_repository: PostRepository):
        super().__init__(post_repository)
    
    async def execute(self, request: GeneratePostRequest) -> GeneratePostResponse:
        """
        Execute the generate post use case.
        
        Args:
            request: The generate post request
            
        Returns:
            The generate post response
            
        Raises:
            UseCaseError: If use case execution fails
        """
        try:
            # Validate request
            self._validate_request(request)
            
            # Create initial post
            post = await self._create_initial_post(request)
            
            # Apply optimization strategy
            optimized_post = await self._apply_optimization(post, request.optimization_strategy)
            
            # Generate hashtags if requested
            if request.include_hashtags:
                await self._add_hashtags(optimized_post, request)
            
            # Add call to action if requested
            if request.include_call_to_action:
                await self._add_call_to_action(optimized_post, request)
            
            # Calculate scores and metrics
            scores = await self._calculate_scores(optimized_post)
            
            # Generate suggestions and warnings
            suggestions = await self._generate_suggestions(optimized_post, scores)
            warnings = await self._generate_warnings(optimized_post, scores)
            
            # Save post to repository
            saved_post = await self.post_repository.save(optimized_post)
            
            # Create response
            response = GeneratePostResponse(
                post=saved_post,
                generation_time_ms=saved_post.generation_time_ms,
                optimization_time_ms=saved_post.optimization_time_ms,
                cache_hit=saved_post.cache_hit,
                optimization_score=saved_post.optimization_score,
                engagement_score=scores['engagement_score'],
                readiness_score=scores['readiness_score'],
                suggestions=suggestions,
                warnings=warnings,
                metadata=saved_post.optimization_metadata
            )
            
            return response
            
        except Exception as e:
            raise UseCaseError(f"Failed to generate post: {str(e)}") from e
    
    def _validate_request(self, request: GeneratePostRequest) -> None:
        """Validate the generate post request."""
        if not request.topic or not request.topic.strip():
            raise UseCaseError("Topic cannot be empty")
        
        if len(request.topic) > 200:
            raise UseCaseError("Topic is too long (max 200 characters)")
        
        # Validate tone
        try:
            PostTone(request.tone)
        except ValueError:
            raise UseCaseError(f"Invalid tone: {request.tone}")
        
        # Validate length
        try:
            PostLength(request.length)
        except ValueError:
            raise UseCaseError(f"Invalid length: {request.length}")
        
        # Validate optimization strategy
        try:
            OptimizationStrategy(request.optimization_strategy)
        except ValueError:
            raise UseCaseError(f"Invalid optimization strategy: {request.optimization_strategy}")
    
    async def _create_initial_post(self, request: GeneratePostRequest) -> LinkedInPost:
        """Create initial LinkedIn post."""
        # Generate base content based on topic and parameters
        content = await self._generate_base_content(request)
        
        # Create post entity
        post = LinkedInPost(
            topic=request.topic,
            content=content,
            tone=PostTone(request.tone),
            length=PostLength(request.length),
            optimization_strategy=OptimizationStrategy(request.optimization_strategy)
        )
        
        return post
    
    async def _generate_base_content(self, request: GeneratePostRequest) -> str:
        """Generate base content for the post."""
        # This would typically integrate with an AI service
        # For now, we'll create a template-based content
        
        tone_characteristics = PostTone(request.tone).get_characteristics()
        length_range = PostLength(request.length).get_character_range()
        target_length = (length_range[0] + length_range[1]) // 2
        
        # Create content template
        content_parts = []
        
        # Introduction
        intro_templates = {
            "professional": f"Today, I want to share insights about {request.topic}.",
            "casual": f"Hey everyone! Let's talk about {request.topic}.",
            "friendly": f"I'm excited to share some thoughts on {request.topic} with you.",
            "authoritative": f"As an expert in this field, I'd like to address {request.topic}.",
            "inspirational": f"Let me inspire you with some thoughts on {request.topic}.",
            "educational": f"Let me teach you something valuable about {request.topic}.",
            "conversational": f"What do you think about {request.topic}?",
            "humorous": f"Here's a funny take on {request.topic}.",
            "motivational": f"Let's get motivated about {request.topic}!",
            "analytical": f"Let me analyze {request.topic} for you."
        }
        
        intro = intro_templates.get(request.tone, intro_templates["professional"])
        content_parts.append(intro)
        
        # Main content
        main_content = self._generate_main_content(request, target_length - len(intro))
        content_parts.append(main_content)
        
        # Combine content
        content = " ".join(content_parts)
        
        # Ensure content fits within length constraints
        if len(content) > length_range[1]:
            content = content[:length_range[1] - 3] + "..."
        
        return content
    
    def _generate_main_content(self, request: GeneratePostRequest, available_length: int) -> str:
        """Generate main content for the post."""
        # Create industry-specific content
        industry_context = request.industry_context or "business"
        content_style = request.content_style or "informative"
        
        # Generate content based on style and context
        if content_style == "informative":
            content = f"This topic is crucial for {industry_context} professionals. "
            content += f"Understanding {request.topic} can significantly impact your success. "
            content += f"Here are key insights that matter in today's {industry_context} landscape."
        
        elif content_style == "storytelling":
            content = f"Let me share a story about {request.topic}. "
            content += f"It's amazing how this relates to {industry_context} challenges. "
            content += f"The lessons learned here are invaluable for professionals."
        
        elif content_style == "actionable":
            content = f"Ready to take action on {request.topic}? "
            content += f"Here are practical steps for {industry_context} success. "
            content += f"Implement these strategies and see immediate results."
        
        else:
            content = f"Exploring {request.topic} reveals important insights for {industry_context}. "
            content += f"This knowledge can transform your approach to {industry_context} challenges. "
            content += f"Let's dive deeper into what makes this topic so significant."
        
        # Truncate if necessary
        if len(content) > available_length:
            content = content[:available_length - 3] + "..."
        
        return content
    
    async def _apply_optimization(self, post: LinkedInPost, strategy: str) -> LinkedInPost:
        """Apply optimization strategy to the post."""
        optimization_strategy = OptimizationStrategy(strategy)
        
        # Calculate optimization score based on strategy
        base_score = 0.7  # Base score for all posts
        strategy_multiplier = optimization_strategy.get_performance_multiplier()
        optimization_score = min(1.0, base_score * strategy_multiplier)
        
        # Create optimization metadata
        metadata = {
            "strategy": strategy,
            "strategy_multiplier": strategy_multiplier,
            "complexity_score": optimization_strategy.get_complexity_score(),
            "processing_time_estimate": optimization_strategy.get_processing_time_estimate(),
            "accuracy_estimate": optimization_strategy.get_accuracy_estimate()
        }
        
        # Apply optimization
        post.apply_optimization(optimization_strategy, optimization_score, metadata)
        
        # Set performance metrics
        generation_time = post.generation_time_ms
        optimization_time = optimization_strategy.get_processing_time_estimate()
        post.set_performance_metrics(generation_time, optimization_time, cache_hit=False)
        
        return post
    
    async def _add_hashtags(self, post: LinkedInPost, request: GeneratePostRequest) -> None:
        """Add hashtags to the post."""
        if request.custom_hashtags:
            for hashtag in request.custom_hashtags:
                post.add_hashtag(hashtag)
        else:
            # Generate relevant hashtags based on topic and industry
            suggested_hashtags = self._generate_suggested_hashtags(request)
            for hashtag in suggested_hashtags[:5]:  # Limit to 5 hashtags
                post.add_hashtag(hashtag)
    
    def _generate_suggested_hashtags(self, request: GeneratePostRequest) -> list[str]:
        """Generate suggested hashtags for the post."""
        hashtags = []
        
        # Add topic-based hashtags
        topic_words = request.topic.lower().split()
        for word in topic_words:
            if len(word) > 3:  # Only use words longer than 3 characters
                hashtags.append(word)
        
        # Add industry-based hashtags
        industry = request.industry_context or "business"
        industry_hashtags = {
            "business": ["business", "leadership", "strategy", "growth"],
            "technology": ["tech", "innovation", "digital", "ai"],
            "marketing": ["marketing", "branding", "socialmedia", "content"],
            "finance": ["finance", "investment", "money", "economy"],
            "healthcare": ["healthcare", "medical", "wellness", "health"]
        }
        
        if industry in industry_hashtags:
            hashtags.extend(industry_hashtags[industry])
        
        # Add tone-based hashtags
        tone_hashtags = {
            "professional": ["professional", "expertise", "industry"],
            "casual": ["casual", "authentic", "real"],
            "friendly": ["community", "connection", "support"],
            "authoritative": ["authority", "expert", "leadership"],
            "inspirational": ["inspiration", "motivation", "growth"],
            "educational": ["learning", "education", "knowledge"],
            "conversational": ["conversation", "discussion", "engagement"],
            "humorous": ["humor", "fun", "entertainment"],
            "motivational": ["motivation", "success", "achievement"],
            "analytical": ["analysis", "data", "insights"]
        }
        
        tone = request.tone
        if tone in tone_hashtags:
            hashtags.extend(tone_hashtags[tone])
        
        return list(set(hashtags))  # Remove duplicates
    
    async def _add_call_to_action(self, post: LinkedInPost, request: GeneratePostRequest) -> None:
        """Add call to action to the post."""
        if request.custom_call_to_action:
            post.set_call_to_action(request.custom_call_to_action)
        else:
            # Generate appropriate call to action based on tone
            cta = self._generate_call_to_action(request)
            post.set_call_to_action(cta)
    
    def _generate_call_to_action(self, request: GeneratePostRequest) -> str:
        """Generate call to action based on tone and context."""
        tone = request.tone
        industry = request.industry_context or "business"
        
        cta_templates = {
            "professional": "What are your thoughts on this topic?",
            "casual": "What do you think? Share your experience!",
            "friendly": "I'd love to hear your perspective on this.",
            "authoritative": "How does this resonate with your experience?",
            "inspirational": "What inspires you about this topic?",
            "educational": "What questions do you have about this?",
            "conversational": "Let's discuss this further in the comments.",
            "humorous": "What's your take on this?",
            "motivational": "What action will you take based on this?",
            "analytical": "What data points would you add to this analysis?"
        }
        
        return cta_templates.get(tone, cta_templates["professional"])
    
    async def _calculate_scores(self, post: LinkedInPost) -> Dict[str, float]:
        """Calculate various scores for the post."""
        scores = {
            'engagement_score': post.get_engagement_score(),
            'readiness_score': 1.0 if post.is_ready_for_posting() else 0.5,
            'optimization_score': post.optimization_score,
            'length_score': self._calculate_length_score(post),
            'tone_score': self._calculate_tone_score(post),
            'hashtag_score': self._calculate_hashtag_score(post)
        }
        
        return scores
    
    def _calculate_length_score(self, post: LinkedInPost) -> float:
        """Calculate length appropriateness score."""
        length = post.length
        content_length = len(post.content)
        min_chars, max_chars = length.get_character_range()
        
        if min_chars <= content_length <= max_chars:
            return 1.0
        elif content_length < min_chars:
            return content_length / min_chars
        else:
            return max(0.0, 1.0 - (content_length - max_chars) / max_chars)
    
    def _calculate_tone_score(self, post: LinkedInPost) -> float:
        """Calculate tone appropriateness score."""
        tone = post.tone
        return tone.get_engagement_multiplier()
    
    def _calculate_hashtag_score(self, post: LinkedInPost) -> float:
        """Calculate hashtag appropriateness score."""
        hashtag_count = len(post.hashtags)
        optimal_count = post.length.get_hashtag_recommendations()
        
        if hashtag_count == optimal_count:
            return 1.0
        elif hashtag_count < optimal_count:
            return hashtag_count / optimal_count
        else:
            return max(0.0, 1.0 - (hashtag_count - optimal_count) / optimal_count)
    
    async def _generate_suggestions(self, post: LinkedInPost, scores: Dict[str, float]) -> list[str]:
        """Generate improvement suggestions for the post."""
        suggestions = []
        
        # Length suggestions
        if scores['length_score'] < 0.8:
            suggestions.append("Consider adjusting the post length for better engagement")
        
        # Tone suggestions
        if scores['tone_score'] < 0.8:
            suggestions.append("The tone could be more engaging for your audience")
        
        # Hashtag suggestions
        if scores['hashtag_score'] < 0.8:
            suggestions.append("Consider adding more relevant hashtags")
        
        # Content suggestions
        if len(post.content) < 100:
            suggestions.append("Consider adding more detail to increase engagement")
        
        if not post.call_to_action:
            suggestions.append("Adding a call to action can increase engagement")
        
        return suggestions
    
    async def _generate_warnings(self, post: LinkedInPost, scores: Dict[str, float]) -> list[str]:
        """Generate warnings for the post."""
        warnings = []
        
        # Length warnings
        if len(post.content) > 3000:
            warnings.append("Post exceeds LinkedIn character limit")
        
        # Hashtag warnings
        if len(post.hashtags) > 30:
            warnings.append("Too many hashtags may reduce engagement")
        
        # Readiness warnings
        if not post.is_ready_for_posting():
            warnings.append("Post may not be ready for publishing")
        
        # Score warnings
        if scores['engagement_score'] < 0.5:
            warnings.append("Low engagement score - consider revising")
        
        return warnings


class UseCaseError(Exception):
    """Base exception for use case operations."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
    
    def __str__(self) -> str:
        return f"UseCaseError: {self.message}" 