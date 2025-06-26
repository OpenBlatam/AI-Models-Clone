"""
Data models for advanced NLP analysis.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class AnalysisMode(Enum):
    """Analysis modes for different use cases."""
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    ULTRA = "ultra"

class ContentType(Enum):
    """Content type for specialized analysis."""
    BLOG_POST = "blog_post"
    ARTICLE = "article"
    SOCIAL_MEDIA = "social_media"
    TECHNICAL = "technical"
    MARKETING = "marketing"

@dataclass
class ReadabilityMetrics:
    """Comprehensive readability metrics."""
    flesch_reading_ease: float = 0.0
    flesch_kincaid_grade: float = 0.0
    gunning_fog: float = 0.0
    coleman_liau_index: float = 0.0
    automated_readability_index: float = 0.0
    dale_chall_readability: float = 0.0
    difficult_words: int = 0
    avg_sentence_length: float = 0.0
    avg_syllables_per_word: float = 0.0
    complex_words_ratio: float = 0.0

@dataclass
class SentimentMetrics:
    """Sentiment analysis results."""
    polarity: float = 0.0  # -1 (negative) to 1 (positive)
    subjectivity: float = 0.0  # 0 (objective) to 1 (subjective)
    label: str = "neutral"
    confidence: float = 0.0
    emotions: Dict[str, float] = field(default_factory=dict)

@dataclass
class SEOMetrics:
    """SEO-specific analysis metrics."""
    keyword_density: Dict[str, float] = field(default_factory=dict)
    title_keyword_presence: bool = False
    meta_description_quality: float = 0.0
    heading_structure_score: float = 0.0
    internal_links_count: int = 0
    external_links_count: int = 0
    image_alt_text_ratio: float = 0.0

@dataclass
class QualityScores:
    """Quality scores for different aspects."""
    overall: float = 0.0
    readability: float = 0.0
    engagement: float = 0.0
    seo: float = 0.0
    semantic_coherence: float = 0.0
    uniqueness: float = 0.0
    structure: float = 0.0
    tone_consistency: float = 0.0

@dataclass
class SemanticAnalysisResult:
    """Comprehensive semantic analysis results."""
    
    # Basic metrics
    word_count: int = 0
    sentence_count: int = 0
    paragraph_count: int = 0
    character_count: int = 0
    
    # Language detection
    detected_language: str = "unknown"
    language_confidence: float = 0.0
    
    # Detailed metrics
    readability: ReadabilityMetrics = field(default_factory=ReadabilityMetrics)
    sentiment: SentimentMetrics = field(default_factory=SentimentMetrics)
    seo: SEOMetrics = field(default_factory=SEOMetrics)
    quality_scores: QualityScores = field(default_factory=QualityScores)
    
    # Keywords and entities
    top_keywords: List[Tuple[str, float]] = field(default_factory=list)
    named_entities: List[Dict[str, Any]] = field(default_factory=list)
    topics: List[Tuple[str, float]] = field(default_factory=list)
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    improvements: List[str] = field(default_factory=list)
    
    # Processing metadata
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    processing_time_ms: float = 0.0
    libraries_used: List[str] = field(default_factory=list)
    analysis_mode: AnalysisMode = AnalysisMode.STANDARD
    content_type: ContentType = ContentType.BLOG_POST

@dataclass
class NLPConfig:
    """Configuration for NLP analysis."""
    language: str = "auto"
    analysis_mode: AnalysisMode = AnalysisMode.STANDARD
    content_type: ContentType = ContentType.BLOG_POST
    target_keywords: List[str] = field(default_factory=list)
    enable_sentiment: bool = True
    enable_readability: bool = True
    enable_seo: bool = True
    enable_entities: bool = True
    enable_topics: bool = True
    enable_grammar_check: bool = False
    max_keywords: int = 20
    max_entities: int = 50
    cache_results: bool = True 