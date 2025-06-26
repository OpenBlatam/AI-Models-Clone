"""
Advanced Semantic Analyzer for Ultra High-Quality Blog Content

This module provides comprehensive semantic analysis using state-of-the-art NLP
techniques to evaluate and enhance blog content quality beyond human-level.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
import math

from . import (
    SPACY_AVAILABLE, NLTK_AVAILABLE, TRANSFORMERS_AVAILABLE,
    TEXTSTAT_AVAILABLE, YAKE_AVAILABLE, TEXTBLOB_AVAILABLE,
    LANGDETECT_AVAILABLE, SENTENCE_TRANSFORMERS_AVAILABLE
)

logger = logging.getLogger(__name__)

@dataclass
class SemanticAnalysisResult:
    """Comprehensive semantic analysis results."""
    
    # Basic metrics
    word_count: int = 0
    sentence_count: int = 0
    paragraph_count: int = 0
    character_count: int = 0
    
    # Readability metrics
    flesch_reading_ease: float = 0.0
    flesch_kincaid_grade: float = 0.0
    gunning_fog: float = 0.0
    coleman_liau_index: float = 0.0
    automated_readability_index: float = 0.0
    dale_chall_readability: float = 0.0
    difficult_words: int = 0
    
    # Language analysis
    detected_language: str = "unknown"
    language_confidence: float = 0.0
    
    # Sentiment analysis
    sentiment_polarity: float = 0.0  # -1 (negative) to 1 (positive)
    sentiment_subjectivity: float = 0.0  # 0 (objective) to 1 (subjective)
    sentiment_label: str = "neutral"
    
    # Keywords and topics
    top_keywords: List[Tuple[str, float]] = field(default_factory=list)
    named_entities: List[Dict[str, Any]] = field(default_factory=list)
    
    # Content structure
    avg_sentence_length: float = 0.0
    avg_syllables_per_word: float = 0.0
    complex_words_ratio: float = 0.0
    
    # SEO metrics
    keyword_density: Dict[str, float] = field(default_factory=dict)
    title_keyword_presence: bool = False
    meta_description_quality: float = 0.0
    
    # Quality scores (0-100)
    overall_quality_score: float = 0.0
    readability_score: float = 0.0
    engagement_score: float = 0.0
    seo_score: float = 0.0
    semantic_coherence_score: float = 0.0
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    
    # Processing info
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    processing_time_ms: float = 0.0
    libraries_used: List[str] = field(default_factory=list)

class AdvancedSemanticAnalyzer:
    """
    Advanced semantic analyzer using state-of-the-art NLP techniques.
    
    This analyzer provides comprehensive content analysis including:
    - Deep readability analysis
    - Sentiment analysis
    - Keyword extraction
    - Named entity recognition
    - SEO optimization analysis
    - Content structure analysis
    - Semantic coherence evaluation
    """
    
    def __init__(self, language: str = "auto"):
        """
        Initialize the semantic analyzer.
        
        Args:
            language: Target language for analysis ("auto", "en", "es", etc.)
        """
        self.language = language
        self.nlp_models = {}
        self.transformers_models = {}
        self.sentence_model = None
        
        # Initialize available models
        self._initialize_models()
        
    def _initialize_models(self):
        """Initialize all available NLP models."""
        start_time = datetime.now()
        logger.info("Initializing NLP models...")
        
        # Initialize spaCy models
        if SPACY_AVAILABLE:
            try:
                import spacy
                # Try to load language-specific models
                if self.language == "es" or self.language == "auto":
                    try:
                        self.nlp_models["es"] = spacy.load("es_core_news_md")
                    except OSError:
                        try:
                            self.nlp_models["es"] = spacy.load("es_core_news_sm")
                        except OSError:
                            logger.warning("Spanish spaCy model not found")
                
                if self.language == "en" or self.language == "auto":
                    try:
                        self.nlp_models["en"] = spacy.load("en_core_web_md")
                    except OSError:
                        try:
                            self.nlp_models["en"] = spacy.load("en_core_web_sm")
                        except OSError:
                            logger.warning("English spaCy model not found")
                            
            except Exception as e:
                logger.error(f"Error initializing spaCy: {e}")
        
        # Initialize transformers models
        if TRANSFORMERS_AVAILABLE:
            try:
                from transformers import pipeline
                # Sentiment analysis
                self.transformers_models["sentiment"] = pipeline(
                    "sentiment-analysis",
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                    return_all_scores=True
                )
                
                # Text classification for topic detection
                self.transformers_models["zero_shot"] = pipeline(
                    "zero-shot-classification",
                    model="facebook/bart-large-mnli"
                )
                
            except Exception as e:
                logger.error(f"Error initializing transformers: {e}")
        
        # Initialize sentence transformers
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                from sentence_transformers import SentenceTransformer
                self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                logger.error(f"Error initializing sentence transformers: {e}")
        
        # Initialize NLTK data
        if NLTK_AVAILABLE:
            try:
                import nltk
                # Download required data
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True)
                nltk.download('vader_lexicon', quiet=True)
                nltk.download('wordnet', quiet=True)
            except Exception as e:
                logger.error(f"Error initializing NLTK: {e}")
        
        init_time = (datetime.now() - start_time).total_seconds() * 1000
        logger.info(f"NLP models initialized in {init_time:.2f}ms")
    
    def analyze_content(
        self,
        content: str,
        title: str = "",
        meta_description: str = "",
        target_keywords: Optional[List[str]] = None
    ) -> SemanticAnalysisResult:
        """
        Perform comprehensive semantic analysis of content.
        
        Args:
            content: The main content text to analyze
            title: Optional title for SEO analysis
            meta_description: Optional meta description for SEO analysis
            target_keywords: Optional list of target keywords for SEO analysis
            
        Returns:
            SemanticAnalysisResult with comprehensive analysis
        """
        start_time = datetime.now()
        result = SemanticAnalysisResult()
        
        if not content or not content.strip():
            logger.warning("Empty content provided for analysis")
            return result
        
        try:
            # Basic content metrics
            result = self._analyze_basic_metrics(content, result)
            
            # Language detection
            result = self._detect_language(content, result)
            
            # Readability analysis
            result = self._analyze_readability(content, result)
            
            # Sentiment analysis
            result = self._analyze_sentiment(content, result)
            
            # Keyword extraction
            result = self._extract_keywords(content, result)
            
            # Named entity recognition
            result = self._extract_named_entities(content, result)
            
            # Content structure analysis
            result = self._analyze_content_structure(content, result)
            
            # SEO analysis
            if title or meta_description or target_keywords:
                result = self._analyze_seo(
                    content, title, meta_description, target_keywords, result
                )
            
            # Semantic coherence analysis
            result = self._analyze_semantic_coherence(content, result)
            
            # Calculate overall quality scores
            result = self._calculate_quality_scores(result)
            
            # Generate recommendations
            result = self._generate_recommendations(result)
            
            # Set processing info
            result.processing_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            result.libraries_used = self._get_used_libraries()
            
            logger.info(
                f"Semantic analysis completed in {result.processing_time_ms:.2f}ms. "
                f"Overall quality: {result.overall_quality_score:.1f}/100"
            )
            
        except Exception as e:
            logger.error(f"Error during semantic analysis: {e}")
            result.recommendations.append(f"Analysis error: {str(e)}")
        
        return result
    
    def _analyze_basic_metrics(self, content: str, result: SemanticAnalysisResult) -> SemanticAnalysisResult:
        """Analyze basic content metrics."""
        result.character_count = len(content)
        result.word_count = len(content.split())
        result.sentence_count = len(re.findall(r'[.!?]+', content))
        result.paragraph_count = len([p for p in content.split('\n\n') if p.strip()])
        
        if result.sentence_count > 0:
            result.avg_sentence_length = result.word_count / result.sentence_count
        
        return result
    
    def _detect_language(self, content: str, result: SemanticAnalysisResult) -> SemanticAnalysisResult:
        """Detect content language."""
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
    
    def _analyze_readability(self, content: str, result: SemanticAnalysisResult) -> SemanticAnalysisResult:
        """Analyze content readability using multiple metrics."""
        if TEXTSTAT_AVAILABLE:
            try:
                import textstat
                
                result.flesch_reading_ease = textstat.flesch_reading_ease(content)
                result.flesch_kincaid_grade = textstat.flesch_kincaid_grade(content)
                result.gunning_fog = textstat.gunning_fog(content)
                result.coleman_liau_index = textstat.coleman_liau_index(content)
                result.automated_readability_index = textstat.automated_readability_index(content)
                result.dale_chall_readability = textstat.dale_chall_readability_score(content)
                result.difficult_words = textstat.difficult_words(content)
                
                # Calculate average syllables per word
                syllable_count = textstat.syllable_count(content)
                if result.word_count > 0:
                    result.avg_syllables_per_word = syllable_count / result.word_count
                
                # Calculate complex words ratio
                if result.word_count > 0:
                    result.complex_words_ratio = result.difficult_words / result.word_count
                    
            except Exception as e:
                logger.warning(f"Readability analysis failed: {e}")
        
        return result
    
    def _analyze_sentiment(self, content: str, result: SemanticAnalysisResult) -> SemanticAnalysisResult:
        """Analyze content sentiment."""
        # Try TextBlob first (simpler and faster)
        if TEXTBLOB_AVAILABLE:
            try:
                from textblob import TextBlob
                blob = TextBlob(content)
                result.sentiment_polarity = blob.sentiment.polarity
                result.sentiment_subjectivity = blob.sentiment.subjectivity
                
                # Determine sentiment label
                if result.sentiment_polarity > 0.1:
                    result.sentiment_label = "positive"
                elif result.sentiment_polarity < -0.1:
                    result.sentiment_label = "negative"
                else:
                    result.sentiment_label = "neutral"
                    
            except Exception as e:
                logger.warning(f"TextBlob sentiment analysis failed: {e}")
        
        # Try transformers for more advanced analysis
        if TRANSFORMERS_AVAILABLE and "sentiment" in self.transformers_models:
            try:
                # Use first 512 characters for transformer analysis (token limit)
                short_content = content[:512]
                sentiment_results = self.transformers_models["sentiment"](short_content)
                
                # Process results
                if sentiment_results and len(sentiment_results[0]) > 0:
                    best_sentiment = max(sentiment_results[0], key=lambda x: x['score'])
                    result.sentiment_label = best_sentiment['label'].lower()
                    
            except Exception as e:
                logger.warning(f"Transformers sentiment analysis failed: {e}")
        
        return result
    
    def _extract_keywords(self, content: str, result: SemanticAnalysisResult) -> SemanticAnalysisResult:
        """Extract important keywords from content."""
        if YAKE_AVAILABLE:
            try:
                import yake
                
                # Configure YAKE
                language = result.detected_language if result.detected_language != "unknown" else "en"
                kw_extractor = yake.KeywordExtractor(
                    lan=language,
                    n=3,  # Extract up to 3-word phrases
                    dedupLim=0.9,
                    top=20,
                    features=None
                )
                
                keywords = kw_extractor.extract_keywords(content)
                # YAKE returns (score, keyword) where lower score = better
                result.top_keywords = [(kw, 1.0 - score) for score, kw in keywords[:10]]
                
            except Exception as e:
                logger.warning(f"YAKE keyword extraction failed: {e}")
        
        # Fallback: simple frequency-based extraction
        if not result.top_keywords:
            words = re.findall(r'\b[a-zA-Z]{4,}\b', content.lower())
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # Get top words
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            result.top_keywords = [(word, freq/len(words)) for word, freq in sorted_words[:10]]
        
        return result
    
    def _extract_named_entities(self, content: str, result: SemanticAnalysisResult) -> SemanticAnalysisResult:
        """Extract named entities from content."""
        if SPACY_AVAILABLE and self.nlp_models:
            try:
                # Use appropriate language model
                lang = result.detected_language if result.detected_language in self.nlp_models else "en"
                if lang not in self.nlp_models:
                    lang = list(self.nlp_models.keys())[0]  # Use any available model
                
                nlp = self.nlp_models[lang]
                doc = nlp(content[:1000])  # Limit content for performance
                
                entities = []
                for ent in doc.ents:
                    entities.append({
                        "text": ent.text,
                        "label": ent.label_,
                        "start": ent.start_char,
                        "end": ent.end_char,
                        "confidence": getattr(ent, "confidence", 1.0)
                    })
                
                result.named_entities = entities
                
            except Exception as e:
                logger.warning(f"Named entity extraction failed: {e}")
        
        return result
    
    def _analyze_content_structure(self, content: str, result: SemanticAnalysisResult) -> SemanticAnalysisResult:
        """Analyze content structure and organization."""
        # Already calculated in basic metrics
        # Could add more sophisticated structure analysis here
        return result
    
    def _analyze_seo(
        self,
        content: str,
        title: str,
        meta_description: str,
        target_keywords: Optional[List[str]],
        result: SemanticAnalysisResult
    ) -> SemanticAnalysisResult:
        """Analyze SEO aspects of the content."""
        if target_keywords:
            # Calculate keyword density
            content_lower = content.lower()
            total_words = len(content.split())
            
            for keyword in target_keywords:
                keyword_lower = keyword.lower()
                keyword_count = content_lower.count(keyword_lower)
                density = (keyword_count / total_words) * 100 if total_words > 0 else 0
                result.keyword_density[keyword] = density
                
                # Check title keyword presence
                if title and keyword_lower in title.lower():
                    result.title_keyword_presence = True
        
        # Analyze meta description quality
        if meta_description:
            desc_length = len(meta_description)
            if 150 <= desc_length <= 160:
                result.meta_description_quality = 100.0
            elif 120 <= desc_length <= 170:
                result.meta_description_quality = 80.0
            elif desc_length > 0:
                result.meta_description_quality = 60.0
        
        return result
    
    def _analyze_semantic_coherence(self, content: str, result: SemanticAnalysisResult) -> SemanticAnalysisResult:
        """Analyze semantic coherence and consistency."""
        if SENTENCE_TRANSFORMERS_AVAILABLE and self.sentence_model:
            try:
                # Split content into sentences
                sentences = re.split(r'[.!?]+', content)
                sentences = [s.strip() for s in sentences if s.strip()]
                
                if len(sentences) >= 2:
                    # Get embeddings for all sentences
                    embeddings = self.sentence_model.encode(sentences)
                    
                    # Calculate pairwise similarities
                    from sklearn.metrics.pairwise import cosine_similarity
                    similarities = cosine_similarity(embeddings)
                    
                    # Calculate average coherence (excluding diagonal)
                    total_similarity = 0
                    count = 0
                    for i in range(len(similarities)):
                        for j in range(i + 1, len(similarities)):
                            total_similarity += similarities[i][j]
                            count += 1
                    
                    if count > 0:
                        avg_coherence = total_similarity / count
                        result.semantic_coherence_score = avg_coherence * 100
                        
            except Exception as e:
                logger.warning(f"Semantic coherence analysis failed: {e}")
        
        return result
    
    def _calculate_quality_scores(self, result: SemanticAnalysisResult) -> SemanticAnalysisResult:
        """Calculate overall quality scores."""
        scores = []
        
        # Readability score (0-100)
        if result.flesch_reading_ease > 0:
            # Normalize Flesch Reading Ease (0-100) to 0-100 quality score
            result.readability_score = min(100, max(0, result.flesch_reading_ease))
            scores.append(result.readability_score)
        
        # Engagement score based on sentiment and subjectivity
        if result.sentiment_polarity != 0 or result.sentiment_subjectivity != 0:
            # Positive sentiment and moderate subjectivity = more engaging
            sentiment_score = (result.sentiment_polarity + 1) * 50  # Convert -1,1 to 0,100
            subjectivity_score = result.sentiment_subjectivity * 100  # 0,1 to 0,100
            result.engagement_score = (sentiment_score + subjectivity_score) / 2
            scores.append(result.engagement_score)
        
        # SEO score
        seo_components = []
        if result.keyword_density:
            # Good keyword density is 1-3%
            avg_density = sum(result.keyword_density.values()) / len(result.keyword_density)
            if 1 <= avg_density <= 3:
                seo_components.append(100)
            elif 0.5 <= avg_density <= 5:
                seo_components.append(80)
            else:
                seo_components.append(60)
        
        if result.title_keyword_presence:
            seo_components.append(100)
        
        if result.meta_description_quality > 0:
            seo_components.append(result.meta_description_quality)
        
        if seo_components:
            result.seo_score = sum(seo_components) / len(seo_components)
            scores.append(result.seo_score)
        
        # Use semantic coherence score if available
        if result.semantic_coherence_score > 0:
            scores.append(result.semantic_coherence_score)
        
        # Calculate overall quality score
        if scores:
            result.overall_quality_score = sum(scores) / len(scores)
        else:
            result.overall_quality_score = 75.0  # Default decent score
        
        return result
    
    def _generate_recommendations(self, result: SemanticAnalysisResult) -> SemanticAnalysisResult:
        """Generate actionable recommendations based on analysis."""
        recommendations = []
        
        # Readability recommendations
        if result.flesch_reading_ease < 60:
            recommendations.append("Consider simplifying sentences to improve readability")
        
        if result.avg_sentence_length > 20:
            recommendations.append("Break down long sentences for better readability")
        
        if result.complex_words_ratio > 0.15:
            recommendations.append("Replace complex words with simpler alternatives")
        
        # Content length recommendations
        if result.word_count < 300:
            recommendations.append("Consider expanding content for better SEO and depth")
        elif result.word_count > 3000:
            recommendations.append("Consider breaking into multiple articles or adding subheadings")
        
        # SEO recommendations
        if result.keyword_density:
            low_density_keywords = [kw for kw, density in result.keyword_density.items() if density < 0.5]
            if low_density_keywords:
                recommendations.append(f"Increase usage of keywords: {', '.join(low_density_keywords)}")
            
            high_density_keywords = [kw for kw, density in result.keyword_density.items() if density > 3]
            if high_density_keywords:
                recommendations.append(f"Reduce keyword stuffing for: {', '.join(high_density_keywords)}")
        
        # Sentiment recommendations
        if result.sentiment_label == "negative" and result.sentiment_polarity < -0.5:
            recommendations.append("Consider using more positive language to improve engagement")
        
        # Structure recommendations
        if result.paragraph_count < 3 and result.word_count > 500:
            recommendations.append("Break content into more paragraphs for better readability")
        
        result.recommendations = recommendations
        return result
    
    def _get_used_libraries(self) -> List[str]:
        """Get list of libraries used in analysis."""
        libraries = []
        if SPACY_AVAILABLE and self.nlp_models:
            libraries.append("spaCy")
        if NLTK_AVAILABLE:
            libraries.append("NLTK")
        if TRANSFORMERS_AVAILABLE and self.transformers_models:
            libraries.append("Transformers")
        if TEXTSTAT_AVAILABLE:
            libraries.append("Textstat")
        if YAKE_AVAILABLE:
            libraries.append("YAKE")
        if TEXTBLOB_AVAILABLE:
            libraries.append("TextBlob")
        if LANGDETECT_AVAILABLE:
            libraries.append("LangDetect")
        if SENTENCE_TRANSFORMERS_AVAILABLE and self.sentence_model:
            libraries.append("SentenceTransformers")
        
        return libraries 