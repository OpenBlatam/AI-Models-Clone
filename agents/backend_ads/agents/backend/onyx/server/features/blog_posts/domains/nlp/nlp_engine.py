"""
NLP Engine - Main orchestrator for blog content analysis.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime

from .models import (
    SemanticAnalysisResult, NLPConfig, AnalysisMode, 
    QualityScores, ReadabilityMetrics, SentimentMetrics
)
from .readability_analyzer import ReadabilityAnalyzer
from . import get_nlp_status

logger = logging.getLogger(__name__)

class NLPEngine:
    """Main NLP engine for blog content analysis."""
    
    def __init__(self):
        """Initialize the NLP engine."""
        logger.info("NLP Engine initialized")
    
    def analyze_content(self, content: str) -> Dict:
        """Analyze blog content using NLP techniques."""
        return {"status": "analyzed", "content_length": len(content)}

    def _initialize_analyzers(self):
        """Initialize all available analyzers."""
        try:
            # Import and initialize other analyzers as they become available
            if self.config.enable_sentiment:
                try:
                    from .sentiment_analyzer import SentimentAnalyzer
                    self.sentiment_analyzer = SentimentAnalyzer()
                except ImportError:
                    logger.warning("Sentiment analyzer not available")
            
            # Additional analyzers can be initialized here
            
        except Exception as e:
            logger.error(f"Error initializing analyzers: {e}")
    
    def analyze_content(
        self,
        content: str,
        title: str = "",
        meta_description: str = "",
        target_keywords: Optional[List[str]] = None
    ) -> SemanticAnalysisResult:
        """
        Perform comprehensive NLP analysis of blog content.
        
        Args:
            content: The main blog content
            title: Blog title
            meta_description: Meta description
            target_keywords: Target SEO keywords
            
        Returns:
            SemanticAnalysisResult with comprehensive analysis
        """
        start_time = datetime.now()
        
        # Initialize result
        result = SemanticAnalysisResult()
        result.content_type = self.config.content_type
        result.analysis_mode = self.config.analysis_mode
        
        if not content or not content.strip():
            logger.warning("Empty content provided for analysis")
            return result
        
        try:
            # Basic content metrics
            result = self._analyze_basic_metrics(content, result)
            
            # Language detection
            result = self._detect_language(content, result)
            
            # Readability analysis
            if self.config.enable_readability:
                result.readability = self.readability_analyzer.analyze(content)
            
            # Sentiment analysis
            if self.config.enable_sentiment and self.sentiment_analyzer:
                result.sentiment = self.sentiment_analyzer.analyze(content)
            
            # Keyword extraction
            if self.config.enable_entities:
                result = self._extract_keywords(content, result)
            
            # SEO analysis
            if self.config.enable_seo:
                result = self._analyze_seo(content, title, meta_description, target_keywords, result)
            
            # Calculate quality scores
            result.quality_scores = self._calculate_quality_scores(result)
            
            # Generate recommendations
            result = self._generate_recommendations(result)
            
            # Set processing metadata
            result.processing_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            result.libraries_used = self._get_used_libraries()
            
            logger.info(
                f"NLP analysis completed in {result.processing_time_ms:.2f}ms. "
                f"Overall quality: {result.quality_scores.overall:.1f}/100"
            )
            
        except Exception as e:
            logger.error(f"Error during NLP analysis: {e}")
            result.recommendations.append(f"Analysis error: {str(e)}")
        
        return result
    
    def _analyze_basic_metrics(self, content: str, result: SemanticAnalysisResult) -> SemanticAnalysisResult:
        """Analyze basic content metrics."""
        import re
        
        result.character_count = len(content)
        result.word_count = len(content.split())
        result.sentence_count = len(re.findall(r'[.!?]+', content))
        result.paragraph_count = len([p for p in content.split('\n\n') if p.strip()])
        
        return result
    
    def _detect_language(self, content: str, result: SemanticAnalysisResult) -> SemanticAnalysisResult:
        """Detect content language."""
        from . import LANGDETECT_AVAILABLE
        
        if LANGDETECT_AVAILABLE:
            try:
                from langdetect import detect, detect_langs
                result.detected_language = detect(content)
                
                # Get confidence score
                langs = detect_langs(content)
                if langs:
                    result.language_confidence = langs[0].prob
                    
            except Exception as e:
                logger.warning(f"Language detection failed: {e}")
                result.detected_language = "unknown"
        
        return result
    
    def _extract_keywords(self, content: str, result: SemanticAnalysisResult) -> SemanticAnalysisResult:
        """Extract keywords from content."""
        from . import YAKE_AVAILABLE
        
        if YAKE_AVAILABLE:
            try:
                import yake
                
                kw_extractor = yake.KeywordExtractor(
                    lan="en",
                    n=3,
                    dedupLim=0.9,
                    top=self.config.max_keywords,
                    features=None
                )
                
                keywords = kw_extractor.extract_keywords(content)
                # YAKE returns (score, keyword) where lower score = better
                result.top_keywords = [(kw, 1.0 - min(score, 1.0)) for score, kw in keywords]
                
            except Exception as e:
                logger.warning(f"Keyword extraction failed: {e}")
        
        return result
    
    def _analyze_seo(
        self,
        content: str,
        title: str,
        meta_description: str,
        target_keywords: Optional[List[str]],
        result: SemanticAnalysisResult
    ) -> SemanticAnalysisResult:
        """Analyze SEO aspects."""
        if not target_keywords:
            target_keywords = []
        
        # Calculate keyword density
        if target_keywords:
            content_lower = content.lower()
            total_words = len(content.split())
            
            for keyword in target_keywords:
                keyword_lower = keyword.lower()
                keyword_count = content_lower.count(keyword_lower)
                density = (keyword_count / total_words) * 100 if total_words > 0 else 0
                result.seo.keyword_density[keyword] = density
                
                # Check title keyword presence
                if title and keyword_lower in title.lower():
                    result.seo.title_keyword_presence = True
        
        # Analyze meta description
        if meta_description:
            desc_length = len(meta_description)
            if 150 <= desc_length <= 160:
                result.seo.meta_description_quality = 100.0
            elif 120 <= desc_length <= 170:
                result.seo.meta_description_quality = 80.0
            elif desc_length > 0:
                result.seo.meta_description_quality = 60.0
        
        return result
    
    def _calculate_quality_scores(self, result: SemanticAnalysisResult) -> QualityScores:
        """Calculate comprehensive quality scores."""
        scores = QualityScores()
        
        # Readability score
        if result.readability.flesch_reading_ease > 0:
            scores.readability = min(100, max(0, result.readability.flesch_reading_ease))
        
        # Engagement score based on sentiment
        if result.sentiment.polarity != 0:
            sentiment_score = (result.sentiment.polarity + 1) * 50
            subjectivity_score = result.sentiment.subjectivity * 100
            scores.engagement = (sentiment_score + subjectivity_score) / 2
        
        # SEO score
        seo_components = []
        if result.seo.keyword_density:
            avg_density = sum(result.seo.keyword_density.values()) / len(result.seo.keyword_density)
            if 1 <= avg_density <= 3:
                seo_components.append(100)
            elif 0.5 <= avg_density <= 5:
                seo_components.append(80)
            else:
                seo_components.append(60)
        
        if result.seo.title_keyword_presence:
            seo_components.append(100)
        
        if result.seo.meta_description_quality > 0:
            seo_components.append(result.seo.meta_description_quality)
        
        if seo_components:
            scores.seo = sum(seo_components) / len(seo_components)
        
        # Structure score based on content organization
        scores.structure = self._calculate_structure_score(result)
        
        # Calculate overall score
        component_scores = [
            scores.readability,
            scores.engagement,
            scores.seo,
            scores.structure
        ]
        
        valid_scores = [s for s in component_scores if s > 0]
        if valid_scores:
            scores.overall = sum(valid_scores) / len(valid_scores)
        else:
            scores.overall = 75.0  # Default decent score
        
        return scores
    
    def _calculate_structure_score(self, result: SemanticAnalysisResult) -> float:
        """Calculate content structure score."""
        score = 0.0
        
        # Word count (optimal range: 800-2000 words for blog posts)
        if 800 <= result.word_count <= 2000:
            score += 30
        elif 500 <= result.word_count <= 3000:
            score += 20
        elif result.word_count >= 300:
            score += 10
        
        # Paragraph count (good structure has multiple paragraphs)
        if result.paragraph_count >= 5:
            score += 25
        elif result.paragraph_count >= 3:
            score += 20
        elif result.paragraph_count >= 2:
            score += 10
        
        # Sentence structure (average sentence length)
        if hasattr(result.readability, 'avg_sentence_length'):
            if 15 <= result.readability.avg_sentence_length <= 20:
                score += 25
            elif 10 <= result.readability.avg_sentence_length <= 25:
                score += 15
            elif result.readability.avg_sentence_length > 0:
                score += 5
        
        # Reading ease contribution
        if result.readability.flesch_reading_ease >= 60:
            score += 20
        elif result.readability.flesch_reading_ease >= 30:
            score += 10
        
        return min(100, score)
    
    def _generate_recommendations(self, result: SemanticAnalysisResult) -> SemanticAnalysisResult:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Readability recommendations
        if result.readability.flesch_reading_ease < 60:
            recommendations.append("📖 Improve readability: Use shorter sentences and simpler words")
        
        if result.readability.avg_sentence_length > 20:
            recommendations.append("✂️ Break up long sentences for better flow")
        
        # Content length recommendations
        if result.word_count < 500:
            recommendations.append("📝 Consider expanding content for better SEO and depth")
        elif result.word_count > 3000:
            recommendations.append("🔄 Consider breaking into multiple posts or adding subheadings")
        
        # SEO recommendations
        if result.seo.keyword_density:
            low_density = [kw for kw, d in result.seo.keyword_density.items() if d < 0.5]
            if low_density:
                recommendations.append(f"🎯 Increase usage of keywords: {', '.join(low_density[:3])}")
            
            high_density = [kw for kw, d in result.seo.keyword_density.items() if d > 3]
            if high_density:
                recommendations.append(f"⚠️ Reduce keyword stuffing for: {', '.join(high_density[:3])}")
        
        # Sentiment recommendations
        if result.sentiment.label == "negative" and result.sentiment.polarity < -0.3:
            recommendations.append("😊 Consider using more positive language for better engagement")
        
        result.recommendations = recommendations[:10]  # Limit to top 10
        return result
    
    def _get_used_libraries(self) -> List[str]:
        """Get list of NLP libraries used."""
        libraries = []
        for lib, available in self.nlp_status.items():
            if available and lib not in ['total_available', 'ready_for_production']:
                libraries.append(lib)
        return libraries 