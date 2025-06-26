"""
Flesch Reading Ease Analyzer for Modular NLP System.

This module provides a specialized analyzer for calculating the Flesch Reading Ease score,
which measures how difficult a text is to understand.
"""

import re
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from ...core import AnalysisType, AnalysisResult, AnalysisConfig
from ..base import BaseAnalyzer

logger = logging.getLogger(__name__)

@dataclass
class FleschMetrics:
    """Metrics used for Flesch Reading Ease calculation."""
    total_sentences: int
    total_words: int
    total_syllables: int
    flesch_score: float
    reading_level: str
    grade_level: float

class FleschReadabilityAnalyzer(BaseAnalyzer):
    """
    Analyzer for Flesch Reading Ease score calculation.
    
    The Flesch Reading Ease formula:
    206.835 - 1.015 × (total words / total sentences) - 84.6 × (total syllables / total words)
    
    Score interpretation:
    - 90-100: Very Easy (5th grade level)
    - 80-89: Easy (6th grade level)
    - 70-79: Fairly Easy (7th grade level)
    - 60-69: Standard (8th-9th grade level)
    - 50-59: Fairly Difficult (10th-12th grade level)
    - 30-49: Difficult (college level)
    - 0-29: Very Difficult (graduate level)
    """
    
    def __init__(self):
        """Initialize Flesch Reading Ease analyzer."""
        super().__init__(
            name="flesch_readability",
            analysis_type=AnalysisType.READABILITY,
            version="1.0.0",
            description="Analyzes text readability using the Flesch Reading Ease formula",
            dependencies=[]  # No external dependencies
        )
        
        # Syllable patterns for English
        self._vowel_pattern = re.compile(r'[aeiouyAEIOUY]')
        self._silent_e_pattern = re.compile(r'[^aeiouyAEIOUY]e\b', re.IGNORECASE)
        self._double_vowel_pattern = re.compile(r'[aeiouyAEIOUY]{2,}', re.IGNORECASE)
        
        # Sentence boundary patterns  
        self._sentence_pattern = re.compile(r'[.!?]+\s+')
        self._word_pattern = re.compile(r'\b\w+\b')
        
        logger.info("FleschReadabilityAnalyzer initialized")
    
    def _perform_analysis(self, text: str, config: AnalysisConfig) -> AnalysisResult:
        """
        Perform Flesch Reading Ease analysis.
        
        Args:
            text: Text to analyze
            config: Analysis configuration
            
        Returns:
            AnalysisResult with Flesch score and metrics
        """
        try:
            # Calculate basic metrics
            metrics = self._calculate_flesch_metrics(text)
            
            # Convert to 0-100 scale for consistency
            normalized_score = self._normalize_flesch_score(metrics.flesch_score)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(metrics, config)
            
            # Create detailed metadata
            metadata = {
                'flesch_score': metrics.flesch_score,
                'reading_level': metrics.reading_level,
                'grade_level': metrics.grade_level,
                'total_sentences': metrics.total_sentences,
                'total_words': metrics.total_words,
                'total_syllables': metrics.total_syllables,
                'average_sentence_length': metrics.total_words / max(metrics.total_sentences, 1),
                'average_syllables_per_word': metrics.total_syllables / max(metrics.total_words, 1),
                'interpretation': self._get_score_interpretation(metrics.flesch_score)
            }
            
            # Calculate confidence based on text length and complexity
            confidence = self._calculate_confidence(metrics, text)
            
            return AnalysisResult(
                analysis_type=self.analysis_type,
                score=normalized_score,
                confidence=confidence,
                metadata=metadata,
                processing_time_ms=0.0,  # Will be set by base class
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error in Flesch analysis: {e}")
            return self._create_error_result(str(e))
    
    def _calculate_flesch_metrics(self, text: str) -> FleschMetrics:
        """Calculate all metrics needed for Flesch Reading Ease score."""
        # Count sentences
        sentences = self._count_sentences(text)
        
        # Count words
        words = self._count_words(text)
        
        # Count syllables
        syllables = self._count_syllables(text)
        
        # Calculate Flesch Reading Ease score
        if sentences == 0 or words == 0:
            flesch_score = 0.0
        else:
            avg_sentence_length = words / sentences
            avg_syllables_per_word = syllables / words
            flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        
        # Determine reading level and grade level
        reading_level = self._get_reading_level(flesch_score)
        grade_level = self._get_grade_level(flesch_score)
        
        return FleschMetrics(
            total_sentences=sentences,
            total_words=words,
            total_syllables=syllables,
            flesch_score=flesch_score,
            reading_level=reading_level,
            grade_level=grade_level
        )
    
    def _count_sentences(self, text: str) -> int:
        """Count the number of sentences in the text."""
        # Split by sentence boundaries
        sentences = self._sentence_pattern.split(text.strip())
        
        # Filter out empty sentences
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Ensure at least 1 sentence
        return max(len(sentences), 1)
    
    def _count_words(self, text: str) -> int:
        """Count the number of words in the text."""
        words = self._word_pattern.findall(text)
        return max(len(words), 1)
    
    def _count_syllables(self, text: str) -> int:
        """Count the total number of syllables in the text."""
        words = self._word_pattern.findall(text.lower())
        total_syllables = 0
        
        for word in words:
            total_syllables += self._count_syllables_in_word(word)
        
        return max(total_syllables, 1)
    
    def _count_syllables_in_word(self, word: str) -> int:
        """Count syllables in a single word."""
        word = word.lower()
        
        # Count vowel groups
        vowel_groups = len(self._vowel_pattern.findall(word))
        
        # Subtract consecutive vowels (they form one syllable)
        consecutive_vowels = len(self._double_vowel_pattern.findall(word))
        vowel_groups -= consecutive_vowels
        
        # Subtract silent 'e' at the end
        if self._silent_e_pattern.search(word):
            vowel_groups -= 1
        
        # Every word has at least one syllable
        return max(vowel_groups, 1)
    
    def _normalize_flesch_score(self, flesch_score: float) -> float:
        """
        Normalize Flesch score to 0-100 scale.
        
        Since Flesch scores can be negative or above 100,
        we clamp them to 0-100 for consistency.
        """
        return max(0.0, min(100.0, flesch_score))
    
    def _get_reading_level(self, flesch_score: float) -> str:
        """Get reading level description from Flesch score."""
        if flesch_score >= 90:
            return "Very Easy"
        elif flesch_score >= 80:
            return "Easy"
        elif flesch_score >= 70:
            return "Fairly Easy"
        elif flesch_score >= 60:
            return "Standard"
        elif flesch_score >= 50:
            return "Fairly Difficult"
        elif flesch_score >= 30:
            return "Difficult"
        else:
            return "Very Difficult"
    
    def _get_grade_level(self, flesch_score: float) -> float:
        """Get approximate grade level from Flesch score."""
        if flesch_score >= 90:
            return 5.0
        elif flesch_score >= 80:
            return 6.0
        elif flesch_score >= 70:
            return 7.0
        elif flesch_score >= 60:
            return 8.5
        elif flesch_score >= 50:
            return 11.0
        elif flesch_score >= 30:
            return 14.0
        else:
            return 16.0
    
    def _get_score_interpretation(self, flesch_score: float) -> str:
        """Get detailed interpretation of the Flesch score."""
        reading_level = self._get_reading_level(flesch_score)
        grade_level = self._get_grade_level(flesch_score)
        
        interpretations = {
            "Very Easy": "Easily understood by an average 11-year-old student.",
            "Easy": "Easily understood by 13- to 15-year-old students.",
            "Fairly Easy": "Easily understood by 16- to 17-year-old students.",
            "Standard": "Easily understood by 18- to 19-year-old students.",
            "Fairly Difficult": "Best understood by college-level readers.",
            "Difficult": "Best understood by university graduates.",
            "Very Difficult": "Best understood by university graduates with advanced degrees."
        }
        
        return interpretations.get(reading_level, "Score interpretation not available.")
    
    def _generate_recommendations(self, metrics: FleschMetrics, config: AnalysisConfig) -> List[str]:
        """Generate recommendations based on Flesch analysis."""
        recommendations = []
        
        # Get target grade level from config
        target_grade = config.parameters.get('target_grade_level', 8)
        
        # Check if text is too difficult
        if metrics.grade_level > target_grade:
            recommendations.extend([
                f"Text is at grade level {metrics.grade_level:.1f}, consider simplifying for grade {target_grade}",
                "Use shorter sentences to improve readability",
                "Replace complex words with simpler alternatives"
            ])
        
        # Specific recommendations based on metrics
        avg_sentence_length = metrics.total_words / max(metrics.total_sentences, 1)
        avg_syllables_per_word = metrics.total_syllables / max(metrics.total_words, 1)
        
        if avg_sentence_length > 20:
            recommendations.append(f"Average sentence length is {avg_sentence_length:.1f} words. Consider breaking long sentences (aim for 15-20 words)")
        
        if avg_syllables_per_word > 1.7:
            recommendations.append(f"Average syllables per word is {avg_syllables_per_word:.2f}. Use simpler words to improve readability")
        
        # Positive feedback for good scores
        if metrics.flesch_score >= 70:
            recommendations.append("Great job! Your text has good readability")
        
        return recommendations
    
    def _calculate_confidence(self, metrics: FleschMetrics, text: str) -> float:
        """Calculate confidence score for the analysis."""
        confidence = 1.0
        
        # Reduce confidence for very short texts
        if metrics.total_words < 50:
            confidence *= 0.7
        elif metrics.total_words < 100:
            confidence *= 0.9
        
        # Reduce confidence for texts with very few sentences
        if metrics.total_sentences < 3:
            confidence *= 0.8
        
        # Reduce confidence for texts with unusual characteristics
        avg_word_length = len(text.replace(' ', '')) / max(metrics.total_words, 1)
        if avg_word_length < 3 or avg_word_length > 8:
            confidence *= 0.9
        
        return confidence 