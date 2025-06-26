"""
ONYX BLOG POSTS - Core Business Logic Layer
==========================================

Pure business logic implementation for blog post generation.
This layer contains domain services and business rules without external dependencies.

Architecture: Application Core (Inner circle)
Dependencies: Only interfaces layer
"""

import asyncio
import hashlib
import time
import logging
import re
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass, replace
from datetime import datetime

from ..interfaces import (
    IBlogGenerator, ISEOGenerator, IContentValidator, IQualityAnalyzer,
    IAIProvider, IPromptBuilder, IContentParser, ICacheProvider,
    BlogSpec, GenerationParams, BlogContent, SEOData, BlogResult,
    GenerationMetrics, GenerationStatus, BlogType, BlogTone, BlogLength,
    BlogSection, QualityGrade, ValidationError, ContentParsingError, 
    BlogGenerationError
)

logger = logging.getLogger(__name__)

# === DOMAIN SERVICES ===

class BlogContentValidator:
    """Core content validation service - Pure business logic"""
    
    async def validate_spec(self, spec: BlogSpec) -> List[str]:
        """Validate blog specification according to business rules"""
        errors = []
        
        # Topic validation
        if not spec.topic or len(spec.topic.strip()) < 5:
            errors.append("Topic must be at least 5 characters long")
        
        if len(spec.topic) > 200:
            errors.append("Topic cannot exceed 200 characters")
        
        # Content appropriateness check
        if self._contains_inappropriate_content(spec.topic):
            errors.append("Topic contains inappropriate content")
        
        # Keywords validation
        if len(spec.keywords) > 20:
            errors.append("Maximum 20 keywords allowed")
        
        for i, keyword in enumerate(spec.keywords):
            if not keyword.strip():
                errors.append(f"Keyword {i+1} cannot be empty")
            elif len(keyword) > 50:
                errors.append(f"Keyword {i+1} cannot exceed 50 characters")
            elif self._contains_inappropriate_content(keyword):
                errors.append(f"Keyword {i+1} contains inappropriate content")
        
        # Target audience validation
        if not spec.target_audience.strip():
            errors.append("Target audience is required")
        elif len(spec.target_audience) > 100:
            errors.append("Target audience description too long")
        
        # Context validation
        if len(spec.context) > 1000:
            errors.append("Context cannot exceed 1000 characters")
        
        # Language validation
        if spec.language not in ["es", "en", "fr", "de", "it", "pt"]:
            errors.append("Unsupported language")
        
        # Business rule: Technical blogs should have technical keywords
        if spec.blog_type == BlogType.TECHNICAL and spec.keywords:
            has_technical_keywords = any(
                keyword.lower() in ["api", "software", "código", "programación", "desarrollo", "tecnología"]
                for keyword in spec.keywords
            )
            if not has_technical_keywords:
                errors.append("Technical blogs should include technical keywords")
        
        return errors
    
    async def validate_content(self, content: BlogContent) -> List[str]:
        """Validate generated content according to quality standards"""
        errors = []
        
        # Title validation
        if not content.title.strip():
            errors.append("Title is required")
        elif len(content.title) < 10:
            errors.append("Title too short (minimum 10 characters)")
        elif len(content.title) > 100:
            errors.append("Title too long (maximum 100 characters)")
        
        # Introduction validation
        if not content.introduction.strip():
            errors.append("Introduction is required")
        elif len(content.introduction.split()) < 20:
            errors.append("Introduction too short (minimum 20 words)")
        elif len(content.introduction.split()) > 150:
            errors.append("Introduction too long (maximum 150 words)")
        
        # Sections validation
        if not content.sections:
            errors.append("At least one main section is required")
        elif len(content.sections) > 10:
            errors.append("Too many sections (maximum 10)")
        
        # Validate individual sections
        for i, section in enumerate(content.sections):
            section_errors = self._validate_section(section, i + 1)
            errors.extend(section_errors)
        
        # Conclusion validation
        if not content.conclusion.strip():
            errors.append("Conclusion is required")
        elif len(content.conclusion.split()) < 15:
            errors.append("Conclusion too short (minimum 15 words)")
        
        # Call to action validation
        if len(content.call_to_action) > 200:
            errors.append("Call to action too long (maximum 200 characters)")
        
        # Content coherence check
        if not self._check_content_coherence(content):
            errors.append("Content lacks coherence between sections")
        
        return errors
    
    def _validate_section(self, section: Any, section_num: int) -> List[str]:
        """Validate individual section"""
        errors = []
        
        if isinstance(section, dict):
            title = section.get('title', '')
            section_content = section.get('content', '')
        elif hasattr(section, 'title') and hasattr(section, 'content'):
            title = section.title
            section_content = section.content
        else:
            errors.append(f"Section {section_num} has invalid format")
            return errors
        
        if not title.strip():
            errors.append(f"Section {section_num} must have a title")
        elif len(title) > 80:
            errors.append(f"Section {section_num} title too long")
        
        if not section_content.strip():
            errors.append(f"Section {section_num} must have content")
        elif len(section_content.split()) < 30:
            errors.append(f"Section {section_num} content too short (minimum 30 words)")
        
        return errors
    
    def _contains_inappropriate_content(self, text: str) -> bool:
        """Check for inappropriate content (basic implementation)"""
        inappropriate_patterns = [
            r'\b(spam|fake|scam|illegal)\b',
            r'\b(hate|violence|discrimination)\b'
        ]
        
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in inappropriate_patterns)
    
    def _check_content_coherence(self, content: BlogContent) -> bool:
        """Basic coherence check between sections"""
        if len(content.sections) < 2:
            return True
        
        # Check if sections have overlapping themes (simplified)
        section_words = []
        for section in content.sections:
            if isinstance(section, dict):
                words = (section.get('title', '') + ' ' + section.get('content', '')).lower().split()
            else:
                words = (section.title + ' ' + section.content).lower().split()
            section_words.append(set(words))
        
        # At least some overlap between consecutive sections
        for i in range(len(section_words) - 1):
            overlap = len(section_words[i] & section_words[i + 1])
            if overlap < 3:  # Very basic threshold
                return False
        
        return True

class BlogQualityAnalyzer:
    """Advanced content quality analysis service"""
    
    async def analyze_quality(self, content: BlogContent, spec: BlogSpec) -> float:
        """Comprehensive quality analysis returning score 0-10"""
        
        # Weight different quality aspects
        weights = {
            'structure': 0.25,      # 25% - Overall structure
            'length': 0.20,         # 20% - Length appropriateness  
            'organization': 0.20,   # 20% - Content organization
            'keywords': 0.15,       # 15% - Keyword integration
            'depth': 0.10,          # 10% - Content depth
            'readability': 0.10     # 10% - Readability
        }
        
        scores = {}
        
        # 1. Structural completeness
        scores['structure'] = self._analyze_structure(content)
        
        # 2. Length appropriateness
        scores['length'] = self._analyze_length(content, spec)
        
        # 3. Content organization
        scores['organization'] = self._analyze_organization(content)
        
        # 4. Keyword integration
        scores['keywords'] = self._analyze_keywords(content, spec)
        
        # 5. Content depth
        scores['depth'] = self._analyze_depth(content)
        
        # 6. Readability
        scores['readability'] = self._analyze_readability(content)
        
        # Calculate weighted final score
        final_score = sum(scores[aspect] * weights[aspect] for aspect in weights)
        
        return min(10.0, max(0.0, final_score))
    
    async def analyze_detailed(self, content: BlogContent, spec: BlogSpec) -> Dict[str, Any]:
        """Detailed quality analysis with breakdown"""
        
        # Individual aspect scores
        structure_score = self._analyze_structure(content)
        length_score = self._analyze_length(content, spec)
        organization_score = self._analyze_organization(content)
        keywords_score = self._analyze_keywords(content, spec)
        depth_score = self._analyze_depth(content)
        readability_score = self._analyze_readability(content)
        
        # Overall score
        overall_score = await self.analyze_quality(content, spec)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            content, spec, {
                'structure': structure_score,
                'length': length_score,
                'organization': organization_score,
                'keywords': keywords_score,
                'depth': depth_score,
                'readability': readability_score
            }
        )
        
        return {
            'overall_score': overall_score,
            'grade': QualityGrade.from_score(overall_score).grade,
            'aspect_scores': {
                'structure': structure_score,
                'length_appropriateness': length_score,
                'organization': organization_score,
                'keyword_integration': keywords_score,
                'content_depth': depth_score,
                'readability': readability_score
            },
            'content_metrics': {
                'word_count': content.word_count,
                'section_count': content.section_count,
                'reading_time_minutes': content.reading_time_minutes,
                'avg_section_length': self._calculate_avg_section_length(content)
            },
            'recommendations': recommendations,
            'strengths': self._identify_strengths(content, spec),
            'improvement_areas': self._identify_improvement_areas(content, spec)
        }
    
    def _analyze_structure(self, content: BlogContent) -> float:
        """Analyze structural completeness (0-10)"""
        score = 0.0
        
        # Title (2 points)
        if content.title.strip():
            score += 2.0 if 10 <= len(content.title) <= 80 else 1.0
        
        # Introduction (2 points)
        if content.introduction.strip():
            intro_words = len(content.introduction.split())
            score += 2.0 if 20 <= intro_words <= 100 else 1.0
        
        # Sections (3 points)
        if content.sections:
            if 3 <= len(content.sections) <= 7:
                score += 3.0
            elif len(content.sections) >= 2:
                score += 2.0
            else:
                score += 1.0
        
        # Conclusion (2 points)
        if content.conclusion.strip():
            conclusion_words = len(content.conclusion.split())
            score += 2.0 if conclusion_words >= 15 else 1.0
        
        # Call to action (1 point)
        if content.call_to_action.strip():
            score += 1.0
        
        return score
    
    def _analyze_length(self, content: BlogContent, spec: BlogSpec) -> float:
        """Analyze length appropriateness (0-10)"""
        word_count = content.word_count
        target_min = spec.length.min_words
        target_max = spec.length.max_words
        
        if target_min <= word_count <= target_max:
            return 10.0
        elif word_count < target_min:
            ratio = word_count / target_min
            return 10.0 * ratio
        else:  # word_count > target_max
            # Penalize excess more gradually
            excess_ratio = (word_count - target_max) / target_max
            penalty = min(5.0, excess_ratio * 5.0)
            return max(5.0, 10.0 - penalty)
    
    def _analyze_organization(self, content: BlogContent) -> float:
        """Analyze content organization (0-10)"""
        score = 0.0
        
        # Logical flow between sections (5 points)
        if self._has_logical_flow(content):
            score += 5.0
        else:
            score += 2.0
        
        # Balanced section lengths (3 points)
        section_lengths = [self._get_section_word_count(s) for s in content.sections]
        if section_lengths:
            avg_length = sum(section_lengths) / len(section_lengths)
            variance = sum((length - avg_length) ** 2 for length in section_lengths) / len(section_lengths)
            coefficient_of_variation = (variance ** 0.5) / avg_length if avg_length > 0 else 1
            
            if coefficient_of_variation < 0.3:  # Well balanced
                score += 3.0
            elif coefficient_of_variation < 0.6:
                score += 2.0
            else:
                score += 1.0
        
        # Clear section titles (2 points)
        clear_titles = sum(1 for s in content.sections if self._has_clear_title(s))
        score += min(2.0, (clear_titles / len(content.sections)) * 2.0) if content.sections else 0
        
        return score
    
    def _analyze_keywords(self, content: BlogContent, spec: BlogSpec) -> float:
        """Analyze keyword integration (0-10)"""
        if not spec.keywords:
            return 8.0  # No keywords specified, assume good
        
        # Extract all content text
        all_text = f"{content.title} {content.introduction} {content.conclusion}".lower()
        for section in content.sections:
            if isinstance(section, dict):
                all_text += f" {section.get('title', '')} {section.get('content', '')}".lower()
            else:
                all_text += f" {section.title} {section.content}".lower()
        
        # Check keyword presence and density
        total_words = len(all_text.split())
        keyword_score = 0.0
        
        for keyword in spec.keywords:
            keyword_lower = keyword.lower()
            occurrences = all_text.count(keyword_lower)
            
            if occurrences == 0:
                continue  # Keyword not found
            
            density = (occurrences / total_words) * 100
            
            # Optimal density is 1-3%
            if 1.0 <= density <= 3.0:
                keyword_score += 1.0
            elif 0.5 <= density < 1.0 or 3.0 < density <= 5.0:
                keyword_score += 0.7
            elif density > 0:
                keyword_score += 0.3
        
        # Normalize by number of keywords
        max_possible = len(spec.keywords)
        return min(10.0, (keyword_score / max_possible) * 10.0) if max_possible > 0 else 8.0
    
    def _analyze_depth(self, content: BlogContent) -> float:
        """Analyze content depth and substance (0-10)"""
        if not content.sections:
            return 2.0
        
        section_depths = []
        for section in content.sections:
            section_words = self._get_section_word_count(section)
            
            # Base depth on word count and content indicators
            depth = 0.0
            
            if section_words >= 100:
                depth += 3.0
            elif section_words >= 50:
                depth += 2.0
            else:
                depth += 1.0
            
            # Check for depth indicators (examples, details, explanations)
            section_text = self._get_section_text(section).lower()
            depth_indicators = [
                'ejemplo', 'example', 'específicamente', 'specifically',
                'detalle', 'detail', 'explicación', 'explanation',
                'implementación', 'implementation', 'proceso', 'process'
            ]
            
            found_indicators = sum(1 for indicator in depth_indicators if indicator in section_text)
            depth += min(2.0, found_indicators * 0.5)
            
            section_depths.append(depth)
        
        avg_depth = sum(section_depths) / len(section_depths)
        return min(10.0, avg_depth)
    
    def _analyze_readability(self, content: BlogContent) -> float:
        """Analyze readability (0-10)"""
        # Calculate average sentence length across all content
        all_text = f"{content.title}. {content.introduction}. {content.conclusion}."
        for section in content.sections:
            section_text = self._get_section_text(section)
            all_text += f" {section_text}."
        
        sentences = [s.strip() for s in all_text.split('.') if s.strip()]
        if not sentences:
            return 5.0
        
        words = all_text.split()
        avg_sentence_length = len(words) / len(sentences)
        
        # Readability scoring based on sentence length
        if 10 <= avg_sentence_length <= 20:  # Optimal range
            readability_score = 10.0
        elif 8 <= avg_sentence_length < 10 or 20 < avg_sentence_length <= 25:
            readability_score = 8.0
        elif 6 <= avg_sentence_length < 8 or 25 < avg_sentence_length <= 30:
            readability_score = 6.0
        else:
            readability_score = 4.0
        
        return readability_score
    
    def _get_section_word_count(self, section: Any) -> int:
        """Get word count for a section"""
        if isinstance(section, dict):
            text = f"{section.get('title', '')} {section.get('content', '')}"
        else:
            text = f"{section.title} {section.content}"
        return len(text.split())
    
    def _get_section_text(self, section: Any) -> str:
        """Get text content from a section"""
        if isinstance(section, dict):
            return f"{section.get('title', '')} {section.get('content', '')}"
        else:
            return f"{section.title} {section.content}"
    
    def _has_clear_title(self, section: Any) -> bool:
        """Check if section has a clear, descriptive title"""
        if isinstance(section, dict):
            title = section.get('title', '')
        else:
            title = section.title
        
        return len(title.strip()) >= 3 and not title.lower().startswith(('sección', 'section'))
    
    def _has_logical_flow(self, content: BlogContent) -> bool:
        """Check for logical flow between sections (simplified)"""
        if len(content.sections) < 2:
            return True
        
        # Basic check for transitional elements or thematic consistency
        # This is a simplified implementation
        return True  # For now, assume good flow
    
    def _calculate_avg_section_length(self, content: BlogContent) -> float:
        """Calculate average section length in words"""
        if not content.sections:
            return 0.0
        
        total_words = sum(self._get_section_word_count(s) for s in content.sections)
        return total_words / len(content.sections)
    
    def _generate_recommendations(self, content: BlogContent, spec: BlogSpec, scores: Dict[str, float]) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        if scores['structure'] < 7.0:
            recommendations.append("Improve overall structure with clearer title, introduction, and conclusion")
        
        if scores['length'] < 7.0:
            target_words = spec.length.target_words
            current_words = content.word_count
            if current_words < target_words:
                recommendations.append(f"Expand content to reach target of {target_words} words (currently {current_words})")
            else:
                recommendations.append(f"Consider condensing content to target of {target_words} words (currently {current_words})")
        
        if scores['organization'] < 7.0:
            recommendations.append("Improve content organization with better section flow and balance")
        
        if scores['keywords'] < 7.0:
            recommendations.append("Better integrate target keywords naturally throughout the content")
        
        if scores['depth'] < 7.0:
            recommendations.append("Add more depth with examples, details, and specific explanations")
        
        if scores['readability'] < 7.0:
            recommendations.append("Improve readability with varied sentence lengths and clearer language")
        
        return recommendations
    
    def _identify_strengths(self, content: BlogContent, spec: BlogSpec) -> List[str]:
        """Identify content strengths"""
        strengths = []
        
        if content.word_count >= spec.length.min_words:
            strengths.append("Meets target word count requirements")
        
        if len(content.sections) >= 3:
            strengths.append("Well-structured with multiple sections")
        
        if len(content.introduction.split()) >= 30:
            strengths.append("Comprehensive introduction")
        
        if content.call_to_action.strip():
            strengths.append("Includes clear call-to-action")
        
        return strengths
    
    def _identify_improvement_areas(self, content: BlogContent, spec: BlogSpec) -> List[str]:
        """Identify areas for improvement"""
        areas = []
        
        if content.word_count < spec.length.min_words * 0.8:
            areas.append("Content length below optimal range")
        
        if len(content.sections) < 3:
            areas.append("Could benefit from more detailed sections")
        
        if not content.call_to_action.strip():
            areas.append("Missing call-to-action")
        
        return areas

class CoreBlogGenerator:
    """Core blog generation orchestrator - Domain service"""
    
    def __init__(
        self,
        ai_provider: IAIProvider,
        prompt_builder: IPromptBuilder,
        content_parser: IContentParser,
        validator: IContentValidator,
        quality_analyzer: IQualityAnalyzer,
        cache_provider: Optional[ICacheProvider] = None
    ):
        self.ai_provider = ai_provider
        self.prompt_builder = prompt_builder
        self.content_parser = content_parser
        self.validator = validator
        self.quality_analyzer = quality_analyzer
        self.cache_provider = cache_provider
    
    async def generate_blog(self, spec: BlogSpec, params: GenerationParams) -> BlogResult:
        """Generate a single blog post with full workflow"""
        request_id = self._generate_request_id(spec)
        start_time = time.time()
        
        try:
            # 1. Validate specification
            result = BlogResult(request_id=request_id, status=GenerationStatus.VALIDATING)
            
            validation_errors = await self.validator.validate_spec(spec)
            if validation_errors:
                return result.with_status(GenerationStatus.FAILED).with_error(
                    f"Validation errors: {', '.join(validation_errors)}"
                )
            
            # 2. Check cache
            cache_key = self._generate_cache_key(spec, params)
            if self.cache_provider:
                cached_result = await self.cache_provider.get(cache_key)
                if cached_result:
                    logger.info(f"Cache hit for request {request_id}")
                    cached_result.metrics.cache_hit = True
                    return cached_result
            
            # 3. Generate content
            result = result.with_status(GenerationStatus.GENERATING)
            
            prompt = await self.prompt_builder.build_blog_prompt(spec, params)
            
            ai_response = await self.ai_provider.generate_text(
                prompt=prompt,
                model=params.model,
                max_tokens=params.max_tokens,
                temperature=params.temperature,
                top_p=params.top_p,
                frequency_penalty=params.frequency_penalty,
                presence_penalty=params.presence_penalty
            )
            
            # 4. Parse content
            result = result.with_status(GenerationStatus.PARSING)
            
            try:
                content = await self.content_parser.parse_blog_content(ai_response["content"])
            except Exception as e:
                raise ContentParsingError(f"Failed to parse AI response: {e}")
            
            # 5. Validate generated content
            content_errors = await self.validator.validate_content(content)
            if content_errors:
                logger.warning(f"Content validation warnings for {request_id}: {content_errors}")
            
            # 6. Analyze quality
            result = result.with_status(GenerationStatus.ANALYZING)
            
            quality_score = await self.quality_analyzer.analyze_quality(content, spec)
            
            # 7. Create metrics
            generation_time = (time.time() - start_time) * 1000
            metrics = GenerationMetrics(
                generation_time_ms=generation_time,
                tokens_used=ai_response.get("tokens_used", 0),
                cost_usd=ai_response.get("cost", 0.0),
                quality_score=quality_score,
                model_used=params.model.value,
                prompt_tokens=ai_response.get("prompt_tokens", 0),
                completion_tokens=ai_response.get("completion_tokens", 0),
                cache_hit=False
            )
            
            # 8. Create final result
            final_result = BlogResult(
                request_id=request_id,
                status=GenerationStatus.COMPLETED,
                content=content,
                seo_data=None,  # Will be generated separately if needed
                metrics=metrics,
                error=None
            )
            
            # 9. Cache result
            if self.cache_provider:
                await self.cache_provider.set(cache_key, final_result, ttl=3600)
            
            logger.info(f"Blog generated successfully: {request_id} ({content.word_count} words, quality: {quality_score:.1f})")
            return final_result
            
        except Exception as e:
            generation_time = (time.time() - start_time) * 1000
            
            logger.error(f"Blog generation failed for {request_id}: {e}")
            
            error_metrics = GenerationMetrics(
                generation_time_ms=generation_time,
                tokens_used=0,
                cost_usd=0.0,
                quality_score=0.0,
                model_used=params.model.value,
                cache_hit=False
            )
            
            return BlogResult(
                request_id=request_id,
                status=GenerationStatus.FAILED,
                content=None,
                seo_data=None,
                metrics=error_metrics,
                error=str(e)
            )
    
    async def generate_batch(
        self, 
        specs: List[BlogSpec], 
        params: GenerationParams,
        max_concurrency: int = 5
    ) -> List[BlogResult]:
        """Generate multiple blog posts with controlled concurrency"""
        semaphore = asyncio.Semaphore(max_concurrency)
        
        async def generate_one(spec: BlogSpec) -> BlogResult:
            async with semaphore:
                return await self.generate_blog(spec, params)
        
        tasks = [generate_one(spec) for spec in specs]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error_result = BlogResult(
                    request_id=f"batch_error_{i}",
                    status=GenerationStatus.FAILED,
                    content=None,
                    seo_data=None,
                    metrics=None,
                    error=str(result)
                )
                final_results.append(error_result)
            else:
                final_results.append(result)
        
        return final_results
    
    def _generate_request_id(self, spec: BlogSpec) -> str:
        """Generate unique request ID"""
        timestamp = str(time.time())
        topic_hash = hashlib.md5(spec.topic.encode()).hexdigest()[:8]
        return f"blog_{topic_hash}_{timestamp[-6:]}"
    
    def _generate_cache_key(self, spec: BlogSpec, params: GenerationParams) -> str:
        """Generate cache key for request"""
        key_data = f"{spec.cache_key}|{params.model.value}|{params.temperature}|{params.include_seo}"
        return hashlib.md5(key_data.encode()).hexdigest()

class CoreSEOGenerator:
    """Core SEO generation service"""
    
    def __init__(
        self,
        ai_provider: IAIProvider,
        prompt_builder: IPromptBuilder,
        content_parser: IContentParser
    ):
        self.ai_provider = ai_provider
        self.prompt_builder = prompt_builder
        self.content_parser = content_parser
    
    async def generate_seo(self, content: BlogContent, spec: BlogSpec) -> SEOData:
        """Generate comprehensive SEO metadata for blog content"""
        try:
            # Build SEO-specific prompt
            prompt = await self.prompt_builder.build_seo_prompt(content, spec)
            
            # Use more deterministic settings for SEO
            ai_response = await self.ai_provider.generate_text(
                prompt=prompt,
                model=spec.blog_type,  # Could be configurable
                temperature=0.3,  # More deterministic for SEO
                max_tokens=800  # Sufficient for SEO metadata
            )
            
            # Parse SEO data
            seo_data = await self.content_parser.parse_seo_content(ai_response["content"])
            
            # Validate and enhance SEO data
            enhanced_seo = self._enhance_seo_data(seo_data, content, spec)
            
            return enhanced_seo
            
        except Exception as e:
            logger.error(f"SEO generation failed: {e}")
            # Return fallback SEO data
            return self._create_fallback_seo(content, spec)
    
    def _enhance_seo_data(self, seo_data: SEOData, content: BlogContent, spec: BlogSpec) -> SEOData:
        """Enhance and validate SEO data"""
        
        # Ensure meta title is within limits
        meta_title = seo_data.meta_title
        if len(meta_title) > 60:
            meta_title = meta_title[:57] + "..."
        elif not meta_title:
            meta_title = content.title[:60]
        
        # Ensure meta description is within limits
        meta_description = seo_data.meta_description
        if len(meta_description) > 160:
            meta_description = meta_description[:157] + "..."
        elif not meta_description:
            meta_description = content.introduction[:160]
        
        # Enhance keywords with spec keywords
        combined_keywords = list(seo_data.keywords) + list(spec.keywords)
        unique_keywords = tuple(dict.fromkeys(combined_keywords))  # Remove duplicates, preserve order
        
        # Create enhanced schema markup
        schema_markup = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": meta_title,
            "description": meta_description,
            "author": {
                "@type": "Organization",
                "name": "Onyx Platform"
            },
            "publisher": {
                "@type": "Organization", 
                "name": "Onyx Platform"
            },
            "datePublished": datetime.utcnow().isoformat(),
            "articleSection": spec.blog_type.display_name,
            "keywords": unique_keywords
        }
        
        return SEOData(
            meta_title=meta_title,
            meta_description=meta_description,
            keywords=unique_keywords,
            og_title=seo_data.og_title or meta_title,
            og_description=seo_data.og_description or meta_description,
            og_image=seo_data.og_image,
            canonical_url=seo_data.canonical_url,
            schema_markup=schema_markup
        )
    
    def _create_fallback_seo(self, content: BlogContent, spec: BlogSpec) -> SEOData:
        """Create basic SEO data as fallback"""
        return SEOData(
            meta_title=content.title[:60],
            meta_description=content.introduction[:160],
            keywords=spec.keywords,
            og_title=content.title,
            og_description=content.introduction[:200],
            schema_markup={
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": content.title,
                "description": content.introduction[:160]
            }
        )

class BlogDomainService:
    """High-level domain service orchestrating all blog operations"""
    
    def __init__(
        self,
        blog_generator: CoreBlogGenerator,
        seo_generator: CoreSEOGenerator,
        validator: IContentValidator,
        quality_analyzer: IQualityAnalyzer
    ):
        self.blog_generator = blog_generator
        self.seo_generator = seo_generator
        self.validator = validator
        self.quality_analyzer = quality_analyzer
    
    async def generate_complete_blog(
        self, 
        spec: BlogSpec, 
        params: GenerationParams
    ) -> BlogResult:
        """Generate complete blog with SEO if requested"""
        
        # Generate main content
        result = await self.blog_generator.generate_blog(spec, params)
        
        # If successful and SEO requested, generate SEO
        if (result.status == GenerationStatus.COMPLETED and 
            params.include_seo and 
            result.content):
            
            try:
                seo_data = await self.seo_generator.generate_seo(result.content, spec)
                
                # Update result with SEO data
                result = replace(result, seo_data=seo_data)
                
            except Exception as e:
                logger.warning(f"SEO generation failed, continuing without SEO: {e}")
        
        return result
    
    async def analyze_existing_content(
        self, 
        content_text: str, 
        keywords: List[str] = None,
        blog_type: BlogType = BlogType.TECHNICAL
    ) -> Dict[str, Any]:
        """Analyze existing content for quality metrics"""
        
        # Parse text into basic content structure
        lines = [line.strip() for line in content_text.strip().split('\n') if line.strip()]
        title = lines[0] if lines else "Untitled"
        
        # Simple content parsing
        paragraphs = content_text.split('\n\n')
        introduction = paragraphs[0] if paragraphs else ""
        
        # Create basic sections from remaining paragraphs
        sections = []
        for i, paragraph in enumerate(paragraphs[1:], 1):
            if len(paragraph.strip()) > 50:
                sections.append({
                    "title": f"Section {i}",
                    "content": paragraph.strip()
                })
        
        content = BlogContent(
            title=title,
            introduction=introduction,
            sections=tuple(sections),
            conclusion=paragraphs[-1] if len(paragraphs) > 1 else "",
            call_to_action=""
        )
        
        # Create dummy spec for analysis
        spec = BlogSpec(
            topic=title,
            blog_type=blog_type,
            tone=BlogTone.PROFESSIONAL,
            length=BlogLength.MEDIUM,
            keywords=tuple(keywords) if keywords else ()
        )
        
        # Perform detailed analysis
        detailed_analysis = await self.quality_analyzer.analyze_detailed(content, spec)
        
        # Add additional metrics
        detailed_analysis.update({
            "content_type": "existing_content",
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "content_structure": {
                "has_title": bool(title.strip()),
                "has_introduction": len(introduction.strip()) > 20,
                "section_count": len(sections),
                "has_conclusion": len(content.conclusion.strip()) > 10
            }
        })
        
        return detailed_analysis

# === EXPORTS ===

__all__ = [
    'BlogContentValidator',
    'BlogQualityAnalyzer', 
    'CoreBlogGenerator',
    'CoreSEOGenerator',
    'BlogDomainService'
] 