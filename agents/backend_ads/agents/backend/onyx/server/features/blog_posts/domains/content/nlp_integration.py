"""
NLP Integration for Ultra Blog Engine.

This module integrates advanced NLP analysis with the existing ultra-optimized
blog generation system to achieve the highest possible content quality.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field

from ..nlp.models import (
    SemanticAnalysisResult, NLPConfig, AnalysisMode, ContentType
)
from ..nlp.readability_analyzer import ReadabilityAnalyzer
from ..nlp import get_nlp_status

logger = logging.getLogger(__name__)

@dataclass
class EnhancedContentMetrics:
    """Enhanced content metrics combining ultra optimization with NLP analysis."""
    
    # Ultra optimization metrics (existing)
    generation_time_ms: float = 0.0
    quality_score: float = 0.0
    optimization_level: str = "STANDARD"
    
    # NLP analysis metrics (new)
    nlp_analysis: Optional[SemanticAnalysisResult] = None
    readability_score: float = 0.0
    sentiment_score: float = 0.0
    seo_score: float = 0.0
    semantic_coherence: float = 0.0
    
    # Combined quality metrics
    ultra_nlp_score: float = 0.0  # Combined ultra + NLP score
    content_grade: str = "B"  # A+, A, B+, B, C+, C, D, F
    
    # Recommendations
    improvements: List[str] = field(default_factory=list)
    nlp_recommendations: List[str] = field(default_factory=list)

@dataclass
class NLPAnalysisResult:
    """Results from NLP analysis of blog content."""
    readability_score: float = 0.0
    sentiment_score: float = 0.0
    seo_score: float = 0.0
    overall_quality: float = 0.0
    recommendations: List[str] = None
    
    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []

class NLPIntegration:
    """
    Advanced NLP integration for ultra-high-quality blog generation.
    
    This class combines the ultra-fast blog generation with comprehensive
    NLP analysis to achieve the highest possible content quality.
    """
    
    def __init__(self, enable_advanced_analysis: bool = True):
        """
        Initialize NLP integration.
        
        Args:
            enable_advanced_analysis: Enable advanced NLP analysis
        """
        self.enable_advanced_analysis = enable_advanced_analysis
        self.readability_analyzer = ReadabilityAnalyzer()
        self.nlp_status = get_nlp_status()
        
        # Initialize based on available libraries
        self._initialize_components()
        
        logger.info(
            f"NLP Integration initialized. "
            f"Advanced analysis: {enable_advanced_analysis}. "
            f"NLP libraries available: {self.nlp_status['total_available']}/11"
        )
    
    def _initialize_components(self):
        """Initialize NLP components based on availability."""
        try:
            # Additional NLP components can be initialized here
            pass
        except Exception as e:
            logger.error(f"Error initializing NLP components: {e}")
    
    def analyze_and_enhance_content(
        self,
        content: str,
        title: str = "",
        meta_description: str = "",
        target_keywords: Optional[List[str]] = None,
        content_type: ContentType = ContentType.BLOG_POST
    ) -> EnhancedContentMetrics:
        """
        Analyze content and provide enhancement recommendations.
        
        Args:
            content: Generated blog content
            title: Blog title
            meta_description: Meta description
            target_keywords: Target SEO keywords
            content_type: Type of content being analyzed
            
        Returns:
            EnhancedContentMetrics with comprehensive analysis
        """
        start_time = datetime.now()
        metrics = EnhancedContentMetrics()
        
        if not content or not content.strip():
            logger.warning("Empty content provided for NLP analysis")
            return metrics
        
        try:
            # Basic content analysis
            metrics = self._analyze_basic_metrics(content, metrics)
            
            # Advanced NLP analysis (if enabled and libraries available)
            if self.enable_advanced_analysis:
                metrics = self._perform_advanced_analysis(
                    content, title, meta_description, target_keywords, metrics
                )
            
            # Calculate combined ultra + NLP score
            metrics = self._calculate_combined_scores(metrics)
            
            # Generate enhancement recommendations
            metrics = self._generate_enhancements(metrics)
            
            # Assign content grade
            metrics.content_grade = self._assign_content_grade(metrics.ultra_nlp_score)
            
            analysis_time = (datetime.now() - start_time).total_seconds() * 1000
            logger.info(
                f"NLP analysis completed in {analysis_time:.2f}ms. "
                f"Ultra-NLP Score: {metrics.ultra_nlp_score:.1f}/100, "
                f"Grade: {metrics.content_grade}"
            )
            
        except Exception as e:
            logger.error(f"Error during NLP analysis: {e}")
            metrics.improvements.append(f"Analysis error: {str(e)}")
        
        return metrics
    
    def _analyze_basic_metrics(self, content: str, metrics: EnhancedContentMetrics) -> EnhancedContentMetrics:
        """Analyze basic content metrics."""
        # Basic readability analysis
        readability_metrics = self.readability_analyzer.analyze(content)
        
        if readability_metrics.flesch_reading_ease > 0:
            metrics.readability_score = min(100, max(0, readability_metrics.flesch_reading_ease))
        
        return metrics
    
    def _perform_advanced_analysis(
        self,
        content: str,
        title: str,
        meta_description: str,
        target_keywords: Optional[List[str]],
        metrics: EnhancedContentMetrics
    ) -> EnhancedContentMetrics:
        """Perform advanced NLP analysis if libraries are available."""
        
        # Language detection
        if self.nlp_status.get('langdetect', False):
            try:
                from langdetect import detect
                detected_lang = detect(content)
                logger.info(f"Detected language: {detected_lang}")
            except Exception as e:
                logger.warning(f"Language detection failed: {e}")
        
        # Sentiment analysis
        if self.nlp_status.get('textblob', False):
            try:
                from textblob import TextBlob
                blob = TextBlob(content)
                sentiment_polarity = blob.sentiment.polarity
                # Convert to 0-100 scale (positive sentiment = higher score)
                metrics.sentiment_score = (sentiment_polarity + 1) * 50
            except Exception as e:
                logger.warning(f"Sentiment analysis failed: {e}")
        
        # Keyword density analysis
        if target_keywords:
            metrics.seo_score = self._calculate_seo_score(content, title, target_keywords)
        
        # Semantic coherence (if sentence transformers available)
        if self.nlp_status.get('sentence_transformers', False):
            metrics.semantic_coherence = self._analyze_semantic_coherence(content)
        
        return metrics
    
    def _calculate_seo_score(self, content: str, title: str, keywords: List[str]) -> float:
        """Calculate SEO score based on keyword usage."""
        if not keywords:
            return 50.0
        
        content_lower = content.lower()
        title_lower = title.lower()
        total_words = len(content.split())
        
        seo_components = []
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            # Keyword density in content (1-3% is optimal)
            keyword_count = content_lower.count(keyword_lower)
            density = (keyword_count / total_words) * 100 if total_words > 0 else 0
            
            if 1 <= density <= 3:
                density_score = 100
            elif 0.5 <= density <= 5:
                density_score = 80
            elif density > 0:
                density_score = 60
            else:
                density_score = 20
            
            seo_components.append(density_score)
            
            # Title keyword presence
            if keyword_lower in title_lower:
                seo_components.append(100)
            else:
                seo_components.append(50)
        
        return sum(seo_components) / len(seo_components) if seo_components else 50.0
    
    def _analyze_semantic_coherence(self, content: str) -> float:
        """Analyze semantic coherence using sentence transformers."""
        try:
            from sentence_transformers import SentenceTransformer
            import re
            
            model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Split into sentences
            sentences = re.split(r'[.!?]+', content)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if len(sentences) < 2:
                return 100.0
            
            # Get embeddings
            embeddings = model.encode(sentences)
            
            # Calculate pairwise similarities
            from sklearn.metrics.pairwise import cosine_similarity
            similarities = cosine_similarity(embeddings)
            
            # Calculate average coherence
            total_similarity = 0
            count = 0
            for i in range(len(similarities)):
                for j in range(i + 1, len(similarities)):
                    total_similarity += similarities[i][j]
                    count += 1
            
            if count > 0:
                avg_coherence = total_similarity / count
                return avg_coherence * 100
            
        except Exception as e:
            logger.warning(f"Semantic coherence analysis failed: {e}")
        
        return 75.0  # Default decent score
    
    def _calculate_combined_scores(self, metrics: EnhancedContentMetrics) -> EnhancedContentMetrics:
        """Calculate combined ultra + NLP quality score."""
        
        # Collect available scores
        scores = []
        weights = []
        
        # Readability (weight: 25%)
        if metrics.readability_score > 0:
            scores.append(metrics.readability_score)
            weights.append(0.25)
        
        # Sentiment (weight: 20%)
        if metrics.sentiment_score > 0:
            scores.append(metrics.sentiment_score)
            weights.append(0.20)
        
        # SEO (weight: 25%)
        if metrics.seo_score > 0:
            scores.append(metrics.seo_score)
            weights.append(0.25)
        
        # Semantic coherence (weight: 15%)
        if metrics.semantic_coherence > 0:
            scores.append(metrics.semantic_coherence)
            weights.append(0.15)
        
        # Ultra optimization score (weight: 15%)
        if metrics.quality_score > 0:
            scores.append(metrics.quality_score)
            weights.append(0.15)
        
        # Calculate weighted average
        if scores and weights:
            total_weight = sum(weights)
            weighted_score = sum(s * w for s, w in zip(scores, weights)) / total_weight
            metrics.ultra_nlp_score = min(100, max(0, weighted_score))
        else:
            metrics.ultra_nlp_score = 75.0  # Default decent score
        
        return metrics
    
    def _generate_enhancements(self, metrics: EnhancedContentMetrics) -> EnhancedContentMetrics:
        """Generate enhancement recommendations."""
        improvements = []
        
        # Readability improvements
        if metrics.readability_score < 70:
            improvements.append("🔧 Improve readability: Use shorter sentences and simpler words")
        
        # Sentiment improvements
        if metrics.sentiment_score < 60:
            improvements.append("😊 Add more positive language to improve engagement")
        
        # SEO improvements
        if metrics.seo_score < 70:
            improvements.append("🎯 Optimize keyword usage for better SEO performance")
        
        # Semantic coherence improvements
        if metrics.semantic_coherence < 70:
            improvements.append("🔗 Improve content flow and logical connections between ideas")
        
        # Overall quality improvements
        if metrics.ultra_nlp_score >= 90:
            improvements.append("🌟 Excellent content quality! Minor optimizations possible")
        elif metrics.ultra_nlp_score >= 80:
            improvements.append("✨ High-quality content with room for refinement")
        elif metrics.ultra_nlp_score >= 70:
            improvements.append("📈 Good content that could benefit from optimization")
        else:
            improvements.append("🔄 Significant improvements needed for optimal quality")
        
        metrics.improvements = improvements
        return metrics
    
    def _assign_content_grade(self, score: float) -> str:
        """Assign letter grade based on ultra-NLP score."""
        if score >= 97:
            return "A+"
        elif score >= 93:
            return "A"
        elif score >= 90:
            return "A-"
        elif score >= 87:
            return "B+"
        elif score >= 83:
            return "B"
        elif score >= 80:
            return "B-"
        elif score >= 77:
            return "C+"
        elif score >= 73:
            return "C"
        elif score >= 70:
            return "C-"
        elif score >= 65:
            return "D"
        else:
            return "F"
    
    def get_optimization_recommendations(self, metrics: EnhancedContentMetrics) -> List[str]:
        """Get specific optimization recommendations."""
        recommendations = []
        
        if metrics.readability_score < 80:
            recommendations.append("Simplify complex sentences and use common vocabulary")
        
        if metrics.sentiment_score < 70:
            recommendations.append("Include more positive and engaging language")
        
        if metrics.seo_score < 80:
            recommendations.append("Improve keyword distribution and title optimization")
        
        if metrics.semantic_coherence < 80:
            recommendations.append("Enhance logical flow and transitions between paragraphs")
        
        return recommendations[:5]  # Limit to top 5 recommendations

    def analyze_content(self, content: str, title: str = "", keywords: Optional[List[str]] = None) -> NLPAnalysisResult:
        """Analyze blog content using NLP techniques."""
        result = NLPAnalysisResult()
        
        if not content:
            return result
        
        # Basic analysis
        result.readability_score = self._analyze_readability(content)
        result.sentiment_score = self._analyze_sentiment(content)
        result.seo_score = self._analyze_seo(content, title, keywords or [])
        
        # Calculate overall quality
        scores = [result.readability_score, result.sentiment_score, result.seo_score]
        valid_scores = [s for s in scores if s > 0]
        result.overall_quality = sum(valid_scores) / len(valid_scores) if valid_scores else 0
        
        # Generate recommendations
        result.recommendations = self._generate_recommendations(result)
        
        logger.info(f"NLP analysis completed. Overall quality: {result.overall_quality:.1f}/100")
        return result
    
    def _analyze_readability(self, content: str) -> float:
        """Analyze content readability."""
        try:
            # Simple readability check - can be enhanced with textstat
            words = len(content.split())
            sentences = content.count('.') + content.count('!') + content.count('?')
            
            if sentences > 0:
                avg_words_per_sentence = words / sentences
                # Optimal is around 15-20 words per sentence
                if 15 <= avg_words_per_sentence <= 20:
                    return 90.0
                elif 10 <= avg_words_per_sentence <= 25:
                    return 75.0
                else:
                    return 60.0
            
            return 70.0
        except:
            return 50.0
    
    def _analyze_sentiment(self, content: str) -> float:
        """Analyze content sentiment."""
        try:
            # Simple sentiment analysis - can be enhanced with TextBlob
            positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic']
            negative_words = ['bad', 'terrible', 'awful', 'horrible', 'poor', 'disappointing']
            
            content_lower = content.lower()
            positive_count = sum(content_lower.count(word) for word in positive_words)
            negative_count = sum(content_lower.count(word) for word in negative_words)
            
            total_sentiment_words = positive_count + negative_count
            if total_sentiment_words == 0:
                return 70.0  # Neutral
            
            positive_ratio = positive_count / total_sentiment_words
            return positive_ratio * 100
        except:
            return 70.0
    
    def _analyze_seo(self, content: str, title: str, keywords: List[str]) -> float:
        """Analyze SEO aspects."""
        try:
            if not keywords:
                return 50.0
            
            content_lower = content.lower()
            title_lower = title.lower()
            
            seo_score = 0.0
            for keyword in keywords:
                keyword_lower = keyword.lower()
                
                # Check keyword in title
                if keyword_lower in title_lower:
                    seo_score += 25
                
                # Check keyword density (simple)
                keyword_count = content_lower.count(keyword_lower)
                content_words = len(content.split())
                
                if content_words > 0:
                    density = (keyword_count / content_words) * 100
                    if 1 <= density <= 3:  # Optimal density
                        seo_score += 25
                    elif 0.5 <= density <= 5:
                        seo_score += 15
                    elif density > 0:
                        seo_score += 10
            
            # Average across keywords
            max_possible = len(keywords) * 50
            return (seo_score / max_possible * 100) if max_possible > 0 else 50.0
        except:
            return 50.0
    
    def _generate_recommendations(self, result: NLPAnalysisResult) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []
        
        if result.readability_score < 70:
            recommendations.append("Improve readability by using shorter sentences")
        
        if result.sentiment_score < 60:
            recommendations.append("Add more positive language to improve engagement")
        
        if result.seo_score < 70:
            recommendations.append("Optimize keyword usage and distribution")
        
        if result.overall_quality >= 85:
            recommendations.append("Excellent content quality!")
        elif result.overall_quality >= 70:
            recommendations.append("Good content with room for improvement")
        else:
            recommendations.append("Significant improvements needed")
        
        return recommendations 