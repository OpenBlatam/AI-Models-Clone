"""
Advanced Readability Analyzer for Blog Content.
"""

import logging
from typing import Optional
from .models import ReadabilityMetrics
from . import TEXTSTAT_AVAILABLE

logger = logging.getLogger(__name__)

class ReadabilityAnalyzer:
    """
    Advanced readability analyzer using multiple metrics.
    
    Uses textstat library to calculate comprehensive readability scores
    including Flesch Reading Ease, Gunning Fog, Coleman-Liau Index, etc.
    """
    
    def __init__(self):
        """Initialize the readability analyzer."""
        if not TEXTSTAT_AVAILABLE:
            logger.warning("Textstat library not available. Install it for readability analysis.")
    
    def analyze(self, content: str) -> ReadabilityMetrics:
        """
        Analyze readability of content using multiple metrics.
        
        Args:
            content: Text content to analyze
            
        Returns:
            ReadabilityMetrics with comprehensive readability scores
        """
        metrics = ReadabilityMetrics()
        
        if not content or not content.strip():
            logger.warning("Empty content provided for readability analysis")
            return metrics
        
        if not TEXTSTAT_AVAILABLE:
            logger.warning("Textstat not available for readability analysis")
            return metrics
        
        try:
            import textstat
            import re
            
            # Core readability metrics
            metrics.flesch_reading_ease = textstat.flesch_reading_ease(content)
            metrics.flesch_kincaid_grade = textstat.flesch_kincaid_grade(content)
            metrics.gunning_fog = textstat.gunning_fog(content)
            metrics.coleman_liau_index = textstat.coleman_liau_index(content)
            metrics.automated_readability_index = textstat.automated_readability_index(content)
            metrics.dale_chall_readability = textstat.dale_chall_readability_score(content)
            metrics.difficult_words = textstat.difficult_words(content)
            
            # Calculate additional metrics
            word_count = len(content.split())
            sentence_count = len(re.findall(r'[.!?]+', content))
            
            if sentence_count > 0:
                metrics.avg_sentence_length = word_count / sentence_count
            
            # Calculate syllables and complex words ratio
            syllable_count = textstat.syllable_count(content)
            if word_count > 0:
                metrics.avg_syllables_per_word = syllable_count / word_count
                metrics.complex_words_ratio = metrics.difficult_words / word_count
            
            logger.info(
                f"Readability analysis completed. "
                f"Flesch Reading Ease: {metrics.flesch_reading_ease:.1f}, "
                f"Grade Level: {metrics.flesch_kincaid_grade:.1f}"
            )
            
        except Exception as e:
            logger.error(f"Readability analysis failed: {e}")
        
        return metrics
    
    def get_readability_interpretation(self, flesch_score: float) -> str:
        """
        Interpret Flesch Reading Ease score.
        
        Args:
            flesch_score: Flesch Reading Ease score
            
        Returns:
            Human-readable interpretation of the score
        """
        if flesch_score >= 90:
            return "Very Easy (5th grade level)"
        elif flesch_score >= 80:
            return "Easy (6th grade level)"
        elif flesch_score >= 70:
            return "Fairly Easy (7th grade level)"
        elif flesch_score >= 60:
            return "Standard (8th-9th grade level)"
        elif flesch_score >= 50:
            return "Fairly Difficult (10th-12th grade level)"
        elif flesch_score >= 30:
            return "Difficult (College level)"
        else:
            return "Very Difficult (Graduate level)"
    
    def calculate_readability_score(self, metrics: ReadabilityMetrics) -> float:
        """
        Calculate overall readability score (0-100).
        
        Args:
            metrics: ReadabilityMetrics object
            
        Returns:
            Overall readability score from 0-100
        """
        if not metrics:
            return 0.0
        
        # Weight different metrics
        scores = []
        weights = []
        
        # Flesch Reading Ease (higher is better)
        if metrics.flesch_reading_ease > 0:
            scores.append(min(100, max(0, metrics.flesch_reading_ease)))
            weights.append(0.4)
        
        # Flesch-Kincaid Grade (lower is better, normalize to 0-100)
        if metrics.flesch_kincaid_grade > 0:
            # Convert grade level to readability score (grade 12 = 0, grade 1 = 100)
            grade_score = max(0, 100 - (metrics.flesch_kincaid_grade - 1) * 9)
            scores.append(grade_score)
            weights.append(0.3)
        
        # Gunning Fog (lower is better)
        if metrics.gunning_fog > 0:
            fog_score = max(0, 100 - (metrics.gunning_fog - 1) * 8)
            scores.append(fog_score)
            weights.append(0.2)
        
        # Sentence length (shorter is better for readability)
        if metrics.avg_sentence_length > 0:
            # Optimal sentence length is around 15-20 words
            if 15 <= metrics.avg_sentence_length <= 20:
                length_score = 100
            elif 10 <= metrics.avg_sentence_length <= 25:
                length_score = 80
            elif metrics.avg_sentence_length <= 30:
                length_score = 60
            else:
                length_score = 40
            scores.append(length_score)
            weights.append(0.1)
        
        # Calculate weighted average
        if scores and weights:
            total_weight = sum(weights)
            weighted_score = sum(s * w for s, w in zip(scores, weights)) / total_weight
            return min(100, max(0, weighted_score))
        
        return 50.0  # Default middle score 