"""
AI Content Generator Service

Refactored from copywriting_model.py to fit the modular architecture.
Provides enterprise-grade AI-powered content generation.
"""

import asyncio
import time
import re
from typing import Dict, List, Any, Optional, Union
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timezone
import uuid
import logging

# High-performance imports
try:
    import numpy as np
    from textstat import flesch_reading_ease, flesch_kincaid_grade
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False

# AI and NLP libraries
try:
    from transformers import pipeline
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from .config import CopywritingConfig, AIProviderConfig, AIProvider
from .models import (
    ContentType, ContentTone, ContentLanguage, 
    ContentRequest, GeneratedContent, ContentMetrics
)
from .exceptions import ContentGenerationError
from .langchain_service import create_langchain_service, LangChainService
from ..optimization.engines.ultra_optimizer import ultra_optimize

logger = logging.getLogger(__name__)

class ContentAnalyzer:
    """Advanced content analysis with NLP and metrics."""
    
    def __init__(self):
        self._sentiment_analyzer = None
        self._emotion_detector = None
        
        if TRANSFORMERS_AVAILABLE:
            try:
                self._sentiment_analyzer = pipeline(
                    "sentiment-analysis", 
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest"
                )
                self._emotion_detector = pipeline(
                    "text-classification", 
                    model="j-hartmann/emotion-english-distilroberta-base"
                )
            except Exception as e:
                logger.warning(f"Failed to load NLP models: {e}")
    
    @ultra_optimize(enable_caching=True, monitor_performance=True)
    async def analyze_content(self, content: str, keywords: List[str] = None) -> ContentMetrics:
        """Comprehensive content analysis."""
        start_time = time.perf_counter()
        
        # Basic metrics
        word_count = len(content.split())
        character_count = len(content)
        reading_time = word_count / 200  # Average reading speed
        
        # Readability analysis
        try:
            readability_score = flesch_reading_ease(content) if NLP_AVAILABLE else 50.0
        except:
            readability_score = 50.0  # Default neutral score
        
        # Sentiment analysis
        sentiment_score = await self._analyze_sentiment(content)
        
        # Keyword density analysis
        keyword_density = self._calculate_keyword_density(content, keywords or [])
        
        # Emotional triggers detection
        emotional_triggers = await self._detect_emotional_triggers(content)
        
        # Call-to-action strength
        cta_strength = self._analyze_cta_strength(content)
        
        # Engagement prediction
        engagement_prediction = await self._predict_engagement(
            content, readability_score, sentiment_score
        )
        
        analysis_time = (time.perf_counter() - start_time) * 1000
        logger.info(f"Content analysis completed in {analysis_time:.2f}ms")
        
        return ContentMetrics(
            readability_score=readability_score,
            sentiment_score=sentiment_score,
            engagement_prediction=engagement_prediction,
            word_count=word_count,
            character_count=character_count,
            reading_time_minutes=reading_time,
            keyword_density=keyword_density,
            emotional_triggers=emotional_triggers,
            call_to_action_strength=cta_strength
        )
    
    async def _analyze_sentiment(self, content: str) -> float:
        """Analyze sentiment using AI models."""
        if not self._sentiment_analyzer:
            return 0.5  # Neutral default
        
        try:
            result = self._sentiment_analyzer(content[:512])  # Limit for performance
            if result[0]['label'] == 'POSITIVE':
                return result[0]['score']
            elif result[0]['label'] == 'NEGATIVE':
                return -result[0]['score']
            else:
                return 0.0
        except Exception as e:
            logger.warning(f"Sentiment analysis failed: {e}")
            return 0.0
    
    def _calculate_keyword_density(self, content: str, keywords: List[str]) -> Dict[str, float]:
        """Calculate keyword density efficiently."""
        if not keywords:
            return {}
        
        content_lower = content.lower()
        word_count = len(content.split())
        
        density = {}
        for keyword in keywords:
            count = content_lower.count(keyword.lower())
            density[keyword] = (count / word_count) * 100 if word_count > 0 else 0
        
        return density
    
    async def _detect_emotional_triggers(self, content: str) -> List[str]:
        """Detect emotional triggers in content."""
        emotional_words = {
            'urgency': ['now', 'limited', 'hurry', 'fast', 'quick', 'urgent', 'immediate'],
            'scarcity': ['exclusive', 'rare', 'limited', 'only', 'last', 'final'],
            'social_proof': ['popular', 'trending', 'bestseller', 'recommended', 'trusted'],
            'fear': ['risk', 'danger', 'warning', 'mistake', 'lose', 'miss'],
            'joy': ['amazing', 'incredible', 'fantastic', 'wonderful', 'perfect', 'love']
        }
        
        content_lower = content.lower()
        triggers = []
        
        for category, words in emotional_words.items():
            if any(word in content_lower for word in words):
                triggers.append(category)
        
        return triggers
    
    def _analyze_cta_strength(self, content: str) -> float:
        """Analyze call-to-action strength."""
        cta_patterns = [
            r'\b(buy|purchase|order|get|download|subscribe|sign up|register|join|start|try)\b',
            r'\b(click|tap|visit|explore|discover|learn|find out)\b',
            r'\b(save|win|earn|gain|receive|claim)\b'
        ]
        
        strength = 0.0
        for pattern in cta_patterns:
            matches = len(re.findall(pattern, content, re.IGNORECASE))
            strength += matches * 0.2  # Each match adds 20% strength
        
        return min(strength, 1.0)  # Cap at 100%
    
    async def _predict_engagement(self, content: str, readability: float, sentiment: float) -> float:
        """Predict engagement using ML model."""
        if not NLP_AVAILABLE:
            return 0.5
        
        # Simplified engagement prediction
        factors = np.array([
            readability / 100,  # Normalize readability
            (sentiment + 1) / 2,  # Normalize sentiment to 0-1
            len(content.split()) / 100,  # Word count factor
            self._analyze_cta_strength(content),  # CTA strength
        ])
        
        # Simple weighted prediction
        weights = np.array([0.3, 0.25, 0.2, 0.25])
        engagement_score = np.dot(factors, weights)
        
        return float(np.clip(engagement_score, 0.0, 1.0))

class TemplateEngine:
    """High-performance templates for different content types."""
    
    TEMPLATES = {
        ContentType.AD_COPY: {
            ContentTone.URGENT: "🚨 {key_message} - Limited Time! {call_to_action}",
            ContentTone.EMOTIONAL: "Discover how {key_message} can transform your life. {call_to_action}",
            ContentTone.PROFESSIONAL: "{key_message} - The professional solution for {target_audience}. {call_to_action}",
        },
        ContentType.SOCIAL_POST: {
            ContentTone.CASUAL: "Hey {target_audience}! 👋 {key_message} {hashtags}",
            ContentTone.PROFESSIONAL: "{key_message} Perfect for {target_audience}. {hashtags}",
            ContentTone.PLAYFUL: "🎉 {key_message} Who's ready to try this? {hashtags}",
        },
        ContentType.EMAIL_SUBJECT: {
            ContentTone.URGENT: "⏰ Last Chance: {key_message}",
            ContentTone.PROFESSIONAL: "{key_message} - Important Update",
            ContentTone.FRIENDLY: "You'll love this: {key_message}",
        },
        ContentType.BLOG_POST: {
            ContentTone.PROFESSIONAL: """# {title}

{key_message}

## Introduction

In today's fast-paced world, {target_audience} need solutions that work. {key_message} provides exactly that.

## Key Benefits

- Proven results for {target_audience}
- Easy to implement and use
- Backed by expert recommendations

## Conclusion

{call_to_action} Transform your approach today!

{hashtags}""",
            ContentTone.CASUAL: """# {title}

Hey there! Let's talk about {key_message}.

If you're like most {target_audience}, you've probably been looking for something that actually works. Well, I've got some good news for you!

{key_message} is exactly what you need. Here's why:

• It's designed specifically for {target_audience}
• Super easy to get started
• You'll see results quickly

Ready to give it a try? {call_to_action}

{hashtags}"""
        }
    }
    
    @classmethod
    def get_template(cls, content_type: ContentType, tone: ContentTone) -> Optional[str]:
        """Get template for content type and tone."""
        return cls.TEMPLATES.get(content_type, {}).get(tone)
    
    @classmethod
    def generate_hashtags(cls, keywords: List[str], max_hashtags: int = 5) -> str:
        """Generate hashtags from keywords."""
        if not keywords:
            return ""
        
        hashtags = [f"#{kw.replace(' ', '').replace('-', '')}" for kw in keywords[:max_hashtags]]
        return " ".join(hashtags)

class AIContentGenerator:
    """AI-powered content generation with multiple backends including LangChain."""
    
    def __init__(self, config: CopywritingConfig, ai_config: AIProviderConfig = None):
        self.config = config
        self.ai_config = ai_config or AIProviderConfig()
        self.template_engine = TemplateEngine()
        self.analyzer = ContentAnalyzer()
        
        # Initialize AI clients
        self._openai_client = None
        self._local_model = None
        self._langchain_service = None
        
        # Initialize providers based on configuration
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all available AI providers."""
        # OpenAI client
        if OPENAI_AVAILABLE and self.ai_config.openai_api_key:
            self._openai_client = openai.OpenAI(api_key=self.ai_config.openai_api_key)
        
        # LangChain service
        try:
            self._langchain_service = create_langchain_service(self.config, self.ai_config)
            if self._langchain_service:
                logger.info("LangChain service initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize LangChain service: {e}")
            self._langchain_service = None
    
    def _get_provider_priority(self) -> List[AIProvider]:
        """Get ordered list of providers to try."""
        providers = []
        
        # Add primary provider first
        if hasattr(self.config, 'primary_ai_provider'):
            providers.append(self.config.primary_ai_provider)
        
        # Add fallback provider
        if hasattr(self.config, 'fallback_ai_provider'):
            providers.append(self.config.fallback_ai_provider)
        
        # Add remaining providers as additional fallbacks
        all_providers = [AIProvider.LANGCHAIN, AIProvider.OPENAI, AIProvider.LOCAL]
        for provider in all_providers:
            if provider not in providers:
                providers.append(provider)
        
        return providers
    
    @ultra_optimize(enable_caching=True, monitor_performance=True)
    async def generate_content(self, request: ContentRequest) -> GeneratedContent:
        """Generate optimized content using AI with LangChain integration."""
        start_time = time.perf_counter()
        
        try:
            # Determine provider priority
            providers_to_try = self._get_provider_priority()
            
            content = None
            model_used = "unknown"
            provider_used = "unknown"
            
            # Try providers in order of priority
            for provider in providers_to_try:
                try:
                    if provider == AIProvider.LANGCHAIN and self._langchain_service:
                        content_result = await self._langchain_service.generate_content(request)
                        # LangChain returns a complete GeneratedContent object
                        return content_result
                    
                    elif provider == AIProvider.OPENAI and self._openai_client:
                        content = await self._generate_with_openai(request)
                        model_used = "openai-gpt"
                        provider_used = "openai"
                        break
                    
                    elif provider == AIProvider.LOCAL and TRANSFORMERS_AVAILABLE:
                        content = await self._generate_with_transformers(request)
                        model_used = "transformers"
                        provider_used = "local"
                        break
                
                except Exception as e:
                    logger.warning(f"Provider {provider} failed: {e}")
                    continue
            
            # Fallback to templates if all providers fail
            if not content:
                content = await self._generate_with_templates(request)
                model_used = "templates"
                provider_used = "templates-fallback"
        
        except Exception as e:
            logger.warning(f"AI generation failed, using templates: {e}")
            content = await self._generate_with_templates(request)
            model_used = "templates-fallback"
            provider_used = "fallback"
        
        # Generate alternatives
        alternatives = await self._generate_alternatives(request, content)
        
        # Analyze generated content
        metrics = await self.analyzer.analyze_content(content, request.keywords)
        
        generation_time = (time.perf_counter() - start_time) * 1000
        
        return GeneratedContent(
            content=content,
            content_type=request.content_type,
            tone=request.tone,
            language=request.language,
            request_params=request.dict(),
            metrics=metrics,
            alternatives=alternatives,
            generation_time_ms=generation_time,
            model_used=model_used,
            confidence_score=metrics.engagement_prediction if metrics else 0.5
        )
    
    async def _generate_with_openai(self, request: ContentGenerationRequest) -> str:
        """Generate content using OpenAI GPT."""
        if not self._openai_client:
            raise ContentGenerationError("OpenAI client not available")
        
        prompt = self._create_optimized_prompt(request)
        
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=request.max_length or 300,
                    temperature=0.7,
                    top_p=0.9
                )
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise ContentGenerationError(f"OpenAI generation failed: {e}")
    
    async def _generate_with_transformers(self, request: ContentGenerationRequest) -> str:
        """Generate content using local transformer models."""
        # Placeholder for transformer-based generation
        # In real implementation, would use local models like GPT-2
        return await self._generate_with_templates(request)
    
    async def _generate_with_templates(self, request: ContentGenerationRequest) -> str:
        """Generate content using optimized templates."""
        template = self.template_engine.get_template(request.content_type, request.tone)
        
        if not template:
            # Fallback to generic template
            template = "{key_message} - Perfect for {target_audience}. {call_to_action}"
        
        # Generate hashtags if needed
        hashtags = ""
        if request.include_hashtags and request.keywords:
            hashtags = self.template_engine.generate_hashtags(request.keywords)
        
        # Handle blog post title
        title = request.title if hasattr(request, 'title') else f"The Ultimate Guide to {request.topic}"
        
        # Replace template variables
        content = template.format(
            title=title,
            key_message=request.topic,
            target_audience=request.target_audience,
            call_to_action=request.call_to_action or "Learn more today!",
            hashtags=hashtags
        )
        
        # Add emojis if requested
        if request.include_emojis:
            content = self._add_emojis(content, request.tone)
        
        # Apply length constraints
        if request.max_length and len(content) > request.max_length:
            content = content[:request.max_length-3] + "..."
        
        return content
    
    def _create_optimized_prompt(self, request: ContentGenerationRequest) -> str:
        """Create optimized prompt for AI generation."""
        prompt_parts = [
            f"Create {request.content_type.value} content with a {request.tone.value} tone.",
            f"Target audience: {request.target_audience}",
            f"Topic: {request.topic}",
        ]
        
        if request.keywords:
            prompt_parts.append(f"Include these keywords naturally: {', '.join(request.keywords)}")
        
        if request.call_to_action:
            prompt_parts.append(f"Include this call-to-action: {request.call_to_action}")
        
        if request.max_length:
            prompt_parts.append(f"Maximum length: {request.max_length} characters")
        
        if request.brand_voice:
            prompt_parts.append(f"Brand voice: {request.brand_voice}")
        
        return "\n".join(prompt_parts)
    
    async def _generate_alternatives(self, request: ContentGenerationRequest, original: str) -> List[str]:
        """Generate alternative versions of content."""
        alternatives = []
        
        # Generate variations by modifying tone
        tones_to_try = [tone for tone in ContentTone if tone != request.tone][:2]
        
        for tone in tones_to_try:
            try:
                alt_request = ContentGenerationRequest(
                    content_type=request.content_type,
                    topic=request.topic,
                    target_audience=request.target_audience,
                    tone=tone,
                    keywords=request.keywords,
                    call_to_action=request.call_to_action
                )
                alt_content = await self._generate_with_templates(alt_request)
                alternatives.append(alt_content)
            except Exception:
                continue
        
        return alternatives
    
    def _add_emojis(self, content: str, tone: ContentTone) -> str:
        """Add emojis based on tone."""
        emoji_map = {
            ContentTone.PLAYFUL: ["🎉", "😄", "🚀", "✨", "🌟"],
            ContentTone.URGENT: ["⏰", "🚨", "⚡", "🔥", "💥"],
            ContentTone.FRIENDLY: ["😊", "👋", "💕", "🤗", "✌️"],
            ContentTone.PROFESSIONAL: ["📈", "💼", "🎯", "📊", "⭐"],
        }
        
        emojis = emoji_map.get(tone, ["✨"])
        
        # Add a random emoji to the content
        import random
        emoji = random.choice(emojis)
        
        # Add emoji at the beginning or end
        if random.choice([True, False]):
            content = f"{emoji} {content}"
        else:
            content = f"{content} {emoji}"
        
        return content

def create_ai_generator(config: CopywritingConfig) -> AIContentGenerator:
    """Factory function to create AI content generator."""
    return AIContentGenerator(config) 