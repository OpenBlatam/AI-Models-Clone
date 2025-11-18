"""
Text Quality Detection AI Model
Detects aggressive, low-quality, or subservient text patterns during document creation.
"""

import re
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextQualityIssue(Enum):
    """Types of text quality issues that can be detected."""
    AGGRESSIVE = "aggressive"
    LOW_QUALITY = "low_quality"
    SUBSERVIENT = "subservient"
    REPETITIVE = "repetitive"
    VAGUE = "vague"
    UNPROFESSIONAL = "unprofessional"

@dataclass
class QualityDetectionResult:
    """Result of text quality analysis."""
    text: str
    issues: List[TextQualityIssue]
    confidence_scores: Dict[TextQualityIssue, float]
    overall_quality_score: float
    suggestions: List[str]
    severity: str  # "low", "medium", "high", "critical"

class TextQualityDetector:
    """
    AI model for detecting text quality issues including:
    - Aggressive language patterns
    - Low quality content indicators
    - Subservient or overly deferential language
    """
    
    def __init__(self):
        """Initialize the text quality detector with pattern libraries."""
        self.aggressive_patterns = self._load_aggressive_patterns()
        self.subservient_patterns = self._load_subservient_patterns()
        self.quality_indicators = self._load_quality_indicators()
        self.repetitive_patterns = self._load_repetitive_patterns()
        
    def _load_aggressive_patterns(self) -> Dict[str, List[str]]:
        """Load patterns that indicate aggressive language."""
        return {
            "direct_aggression": [
                r'\b(you\s+are\s+wrong|you\s+don\'t\s+understand|you\s+clearly\s+don\'t)',
                r'\b(that\'s\s+stupid|that\'s\s+ridiculous|that\'s\s+nonsense)',
                r'\b(you\s+must\s+be\s+joking|are\s+you\s+kidding|seriously\?)',
                r'\b(obviously|clearly|without\s+a\s+doubt)',
                r'\b(you\s+should\s+know|everyone\s+knows|it\'s\s+obvious)'
            ],
            "condescending": [
                r'\b(let\s+me\s+explain\s+to\s+you|you\s+need\s+to\s+understand)',
                r'\b(if\s+you\s+had\s+any\s+idea|if\s+you\s+knew\s+anything)',
                r'\b(perhaps\s+you\s+should\s+learn|maybe\s+you\s+should\s+study)',
                r'\b(you\s+clearly\s+haven\'t|you\s+obviously\s+don\'t)'
            ],
            "demanding": [
                r'\b(you\s+must|you\s+have\s+to|you\s+need\s+to)',
                r'\b(do\s+it\s+now|immediately|right\s+away)',
                r'\b(no\s+excuses|no\s+buts|no\s+questions)',
                r'\b(just\s+do\s+it|stop\s+arguing|end\s+of\s+story)'
            ]
        }
    
    def _load_subservient_patterns(self) -> Dict[str, List[str]]:
        """Load patterns that indicate overly subservient language."""
        return {
            "excessive_apology": [
                r'\b(i\'m\s+so\s+sorry|i\s+apologize\s+profusely|my\s+deepest\s+apologies)',
                r'\b(please\s+forgive\s+me|i\s+beg\s+your\s+pardon|excuse\s+my\s+incompetence)',
                r'\b(i\'m\s+terribly\s+sorry|i\s+feel\s+awful|i\'m\s+such\s+a\s+failure)'
            ],
            "overly_deferential": [
                r'\b(if\s+it\s+pleases\s+you|if\s+you\s+would\s+be\s+so\s+kind)',
                r'\b(only\s+if\s+you\s+don\'t\s+mind|whenever\s+you\s+have\s+time)',
                r'\b(i\s+wouldn\'t\s+want\s+to\s+bother\s+you|i\s+hope\s+this\s+isn\'t\s+too\s+much)',
                r'\b(please\s+don\'t\s+feel\s+obligated|only\s+if\s+it\'s\s+convenient)'
            ],
            "self_deprecating": [
                r'\b(i\'m\s+probably\s+wrong|i\s+might\s+be\s+mistaken|i\'m\s+not\s+sure)',
                r'\b(i\'m\s+not\s+qualified|i\'m\s+not\s+expert|i\'m\s+just\s+a\s+beginner)',
                r'\b(my\s+opinion\s+doesn\'t\s+matter|i\'m\s+not\s+important|i\'m\s+nobody)'
            ]
        }
    
    def _load_quality_indicators(self) -> Dict[str, List[str]]:
        """Load patterns that indicate low quality content."""
        return {
            "vague_language": [
                r'\b(somehow|somewhere|sometime|some\s+way)',
                r'\b(things|stuff|whatever|something\s+like\s+that)',
                r'\b(kind\s+of|sort\s+of|maybe|perhaps)',
                r'\b(i\s+guess|i\s+think|probably|possibly)'
            ],
            "filler_words": [
                r'\b(um|uh|er|ah|like|you\s+know|basically)',
                r'\b(actually|literally|honestly|frankly)',
                r'\b(well|so|then|now|here)'
            ],
            "unprofessional": [
                r'\b(awesome|cool|amazing|incredible)',
                r'\b(OMG|WTF|LOL|BTW|FYI)',
                r'\b(yeah|yep|nope|nah|sure)',
                r'\b(whatever|anyway|so\s+what|big\s+deal)'
            ]
        }
    
    def _load_repetitive_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for detecting repetitive content."""
        return {
            "repeated_phrases": [
                r'\b(\w+)\s+\1\s+\1',  # Same word repeated 3 times
                r'\b(\w+\s+\w+)\s+\1',  # Same phrase repeated
            ],
            "redundant_expressions": [
                r'\b(completely\s+finished|totally\s+complete|absolutely\s+certain)',
                r'\b(very\s+unique|extremely\s+essential|highly\s+important)',
                r'\b(completely\s+empty|totally\s+full|absolutely\s+perfect)'
            ]
        }
    
    def analyze_text(self, text: str) -> QualityDetectionResult:
        """
        Analyze text for quality issues and return detailed results.
        
        Args:
            text: The text to analyze
            
        Returns:
            QualityDetectionResult with detected issues and suggestions
        """
        if not text or not text.strip():
            return QualityDetectionResult(
                text=text,
                issues=[],
                confidence_scores={},
                overall_quality_score=0.0,
                suggestions=["Text is empty or contains only whitespace"],
                severity="low"
            )
        
        issues = []
        confidence_scores = {}
        suggestions = []
        
        # Check for aggressive language
        aggressive_score = self._detect_aggressive_language(text)
        if aggressive_score > 0.3:
            issues.append(TextQualityIssue.AGGRESSIVE)
            confidence_scores[TextQualityIssue.AGGRESSIVE] = aggressive_score
            suggestions.append("Consider using more diplomatic and respectful language")
        
        # Check for subservient language
        subservient_score = self._detect_subservient_language(text)
        if subservient_score > 0.3:
            issues.append(TextQualityIssue.SUBSERVIENT)
            confidence_scores[TextQualityIssue.SUBSERVIENT] = subservient_score
            suggestions.append("Try to be more confident and assertive in your communication")
        
        # Check for low quality indicators
        quality_score = self._detect_low_quality(text)
        if quality_score > 0.4:
            issues.append(TextQualityIssue.LOW_QUALITY)
            confidence_scores[TextQualityIssue.LOW_QUALITY] = quality_score
            suggestions.append("Improve clarity and specificity of your language")
        
        # Check for repetitive content
        repetitive_score = self._detect_repetitive_content(text)
        if repetitive_score > 0.3:
            issues.append(TextQualityIssue.REPETITIVE)
            confidence_scores[TextQualityIssue.REPETITIVE] = repetitive_score
            suggestions.append("Avoid repetition and vary your vocabulary")
        
        # Calculate overall quality score
        overall_score = self._calculate_overall_quality_score(
            aggressive_score, subservient_score, quality_score, repetitive_score
        )
        
        # Determine severity
        severity = self._determine_severity(overall_score, issues)
        
        return QualityDetectionResult(
            text=text,
            issues=issues,
            confidence_scores=confidence_scores,
            overall_quality_score=overall_score,
            suggestions=suggestions,
            severity=severity
        )
    
    def _detect_aggressive_language(self, text: str) -> float:
        """Detect aggressive language patterns in text."""
        text_lower = text.lower()
        total_matches = 0
        total_patterns = 0
        
        for category, patterns in self.aggressive_patterns.items():
            for pattern in patterns:
                total_patterns += 1
                matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
                total_matches += matches
        
        return min(total_matches / max(total_patterns, 1), 1.0)
    
    def _detect_subservient_language(self, text: str) -> float:
        """Detect overly subservient language patterns."""
        text_lower = text.lower()
        total_matches = 0
        total_patterns = 0
        
        for category, patterns in self.subservient_patterns.items():
            for pattern in patterns:
                total_patterns += 1
                matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
                total_matches += matches
        
        return min(total_matches / max(total_patterns, 1), 1.0)
    
    def _detect_low_quality(self, text: str) -> float:
        """Detect low quality content indicators."""
        text_lower = text.lower()
        total_matches = 0
        total_patterns = 0
        
        for category, patterns in self.quality_indicators.items():
            for pattern in patterns:
                total_patterns += 1
                matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
                total_matches += matches
        
        # Also check for very short sentences or lack of detail
        sentences = text.split('.')
        short_sentences = sum(1 for s in sentences if len(s.strip()) < 10)
        if len(sentences) > 0:
            short_sentence_ratio = short_sentences / len(sentences)
            total_matches += short_sentence_ratio * 10
        
        return min(total_matches / max(total_patterns, 1), 1.0)
    
    def _detect_repetitive_content(self, text: str) -> float:
        """Detect repetitive content patterns."""
        text_lower = text.lower()
        total_matches = 0
        total_patterns = 0
        
        for category, patterns in self.repetitive_patterns.items():
            for pattern in patterns:
                total_patterns += 1
                matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
                total_matches += matches
        
        # Check for word frequency repetition
        words = re.findall(r'\b\w+\b', text_lower)
        if len(words) > 0:
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # Calculate repetition score based on most frequent words
            max_freq = max(word_freq.values()) if word_freq else 0
            repetition_ratio = max_freq / len(words)
            total_matches += repetition_ratio * 5
        
        return min(total_matches / max(total_patterns, 1), 1.0)
    
    def _calculate_overall_quality_score(self, aggressive: float, subservient: float, 
                                       quality: float, repetitive: float) -> float:
        """Calculate overall quality score (0-1, higher is better)."""
        # Weight the different factors
        weights = {
            'aggressive': 0.3,
            'subservient': 0.2,
            'quality': 0.3,
            'repetitive': 0.2
        }
        
        # Convert to quality scores (invert negative indicators)
        aggressive_quality = 1.0 - aggressive
        subservient_quality = 1.0 - subservient
        quality_score = 1.0 - quality
        repetitive_quality = 1.0 - repetitive
        
        overall = (
            aggressive_quality * weights['aggressive'] +
            subservient_quality * weights['subservient'] +
            quality_score * weights['quality'] +
            repetitive_quality * weights['repetitive']
        )
        
        return max(0.0, min(1.0, overall))
    
    def _determine_severity(self, quality_score: float, issues: List[TextQualityIssue]) -> str:
        """Determine the severity level based on quality score and issues."""
        if quality_score < 0.3 or len(issues) >= 3:
            return "critical"
        elif quality_score < 0.5 or len(issues) >= 2:
            return "high"
        elif quality_score < 0.7 or len(issues) >= 1:
            return "medium"
        else:
            return "low"
    
    def get_real_time_feedback(self, text: str) -> Dict[str, any]:
        """
        Provide real-time feedback during text creation.
        
        Args:
            text: Current text being created
            
        Returns:
            Dictionary with real-time feedback
        """
        result = self.analyze_text(text)
        
        return {
            "quality_score": result.overall_quality_score,
            "issues_detected": [issue.value for issue in result.issues],
            "severity": result.severity,
            "suggestions": result.suggestions,
            "confidence_scores": {k.value: v for k, v in result.confidence_scores.items()},
            "is_acceptable": result.overall_quality_score > 0.6 and result.severity in ["low", "medium"]
        }

# Example usage and testing
if __name__ == "__main__":
    detector = TextQualityDetector()
    
    # Test cases
    test_texts = [
        "You are completely wrong and don't understand anything about this topic.",
        "I'm so sorry, I hope this isn't too much trouble, but could you please help me if it's not too inconvenient?",
        "This is like, you know, really awesome and stuff, but I guess it's kind of okay.",
        "The implementation requires careful consideration of multiple factors to ensure optimal performance.",
        "This is amazing! OMG, you're so cool! This is literally the best thing ever!"
    ]
    
    print("Text Quality Detection Results:")
    print("=" * 50)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\nTest {i}: {text}")
        result = detector.analyze_text(text)
        print(f"Quality Score: {result.overall_quality_score:.2f}")
        print(f"Severity: {result.severity}")
        print(f"Issues: {[issue.value for issue in result.issues]}")
        print(f"Suggestions: {result.suggestions}")
        print("-" * 30)


























