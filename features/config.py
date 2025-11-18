"""
Configuration settings for the Features module.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
import os

@dataclass
class TextQualityConfig:
    """Configuration for text quality detection."""
    
    # Thresholds for different quality levels
    excellent_threshold: float = 0.8
    good_threshold: float = 0.6
    warning_threshold: float = 0.4
    critical_threshold: float = 0.2
    
    # Pattern matching settings
    case_sensitive: bool = False
    use_regex: bool = True
    
    # Feedback settings
    max_suggestions_per_issue: int = 3
    enable_positive_feedback: bool = True
    
    # Language-specific settings
    language: str = "en"  # English by default
    custom_patterns: Optional[Dict[str, List[str]]] = None

@dataclass
class DocumentMonitorConfig:
    """Configuration for document monitoring."""
    
    # Timing settings
    check_interval: float = 2.0  # seconds
    session_timeout: float = 300.0  # 5 minutes
    min_text_length: int = 10
    
    # Quality thresholds
    warning_threshold: float = 0.4
    critical_threshold: float = 0.2
    
    # Session limits
    max_suggestions_per_session: int = 5
    max_active_sessions: int = 100
    
    # Logging and storage
    enable_quality_logs: bool = True
    log_directory: str = "quality_logs"
    auto_cleanup_logs: bool = True
    log_retention_days: int = 30
    
    # Real-time features
    enable_real_time_feedback: bool = True
    enable_auto_save: bool = False
    auto_save_interval: float = 60.0  # seconds

@dataclass
class FeaturesConfig:
    """Main configuration for the Features module."""
    
    # Component configurations
    text_quality: TextQualityConfig = None
    document_monitor: DocumentMonitorConfig = None
    
    # General settings
    debug_mode: bool = False
    log_level: str = "INFO"
    
    # Integration settings
    enable_api_endpoints: bool = True
    api_port: int = 8000
    api_host: str = "localhost"
    
    def __post_init__(self):
        """Initialize default configurations if not provided."""
        if self.text_quality is None:
            self.text_quality = TextQualityConfig()
        if self.document_monitor is None:
            self.document_monitor = DocumentMonitorConfig()

# Environment-based configuration
def load_config_from_env() -> FeaturesConfig:
    """Load configuration from environment variables."""
    
    # Text Quality Config
    text_quality_config = TextQualityConfig(
        excellent_threshold=float(os.getenv('TEXT_QUALITY_EXCELLENT_THRESHOLD', '0.8')),
        good_threshold=float(os.getenv('TEXT_QUALITY_GOOD_THRESHOLD', '0.6')),
        warning_threshold=float(os.getenv('TEXT_QUALITY_WARNING_THRESHOLD', '0.4')),
        critical_threshold=float(os.getenv('TEXT_QUALITY_CRITICAL_THRESHOLD', '0.2')),
        case_sensitive=os.getenv('TEXT_QUALITY_CASE_SENSITIVE', 'false').lower() == 'true',
        language=os.getenv('TEXT_QUALITY_LANGUAGE', 'en')
    )
    
    # Document Monitor Config
    document_monitor_config = DocumentMonitorConfig(
        check_interval=float(os.getenv('DOC_MONITOR_CHECK_INTERVAL', '2.0')),
        session_timeout=float(os.getenv('DOC_MONITOR_SESSION_TIMEOUT', '300.0')),
        min_text_length=int(os.getenv('DOC_MONITOR_MIN_TEXT_LENGTH', '10')),
        warning_threshold=float(os.getenv('DOC_MONITOR_WARNING_THRESHOLD', '0.4')),
        critical_threshold=float(os.getenv('DOC_MONITOR_CRITICAL_THRESHOLD', '0.2')),
        max_suggestions_per_session=int(os.getenv('DOC_MONITOR_MAX_SUGGESTIONS', '5')),
        max_active_sessions=int(os.getenv('DOC_MONITOR_MAX_SESSIONS', '100')),
        enable_quality_logs=os.getenv('DOC_MONITOR_ENABLE_LOGS', 'true').lower() == 'true',
        log_directory=os.getenv('DOC_MONITOR_LOG_DIR', 'quality_logs'),
        enable_real_time_feedback=os.getenv('DOC_MONITOR_REAL_TIME', 'true').lower() == 'true'
    )
    
    # Main Config
    return FeaturesConfig(
        text_quality=text_quality_config,
        document_monitor=document_monitor_config,
        debug_mode=os.getenv('FEATURES_DEBUG', 'false').lower() == 'true',
        log_level=os.getenv('FEATURES_LOG_LEVEL', 'INFO'),
        enable_api_endpoints=os.getenv('FEATURES_ENABLE_API', 'true').lower() == 'true',
        api_port=int(os.getenv('FEATURES_API_PORT', '8000')),
        api_host=os.getenv('FEATURES_API_HOST', 'localhost')
    )

# Default configuration
DEFAULT_CONFIG = FeaturesConfig()

# Language-specific patterns
LANGUAGE_PATTERNS = {
    "en": {
        "aggressive": [
            r'\b(you\s+are\s+wrong|you\s+don\'t\s+understand)',
            r'\b(that\'s\s+stupid|that\'s\s+ridiculous)',
            r'\b(obviously|clearly|without\s+a\s+doubt)'
        ],
        "subservient": [
            r'\b(i\'m\s+so\s+sorry|i\s+apologize\s+profusely)',
            r'\b(if\s+it\s+pleases\s+you|if\s+you\s+would\s+be\s+so\s+kind)',
            r'\b(i\'m\s+probably\s+wrong|i\s+might\s+be\s+mistaken)'
        ]
    },
    "es": {
        "aggressive": [
            r'\b(estás\s+equivocado|no\s+entiendes)',
            r'\b(eso\s+es\s+estúpido|eso\s+es\s+ridículo)',
            r'\b(obviamente|claramente|sin\s+duda)'
        ],
        "subservient": [
            r'\b(lo\s+siento\s+mucho|me\s+disculpo\s+profusamente)',
            r'\b(si\s+te\s+place|si\s+fuera\s+tan\s+amable)',
            r'\b(probablemente\s+estoy\s+equivocado|podría\s+estar\s+equivocado)'
        ]
    }
}

def get_language_patterns(language: str = "en") -> Dict[str, List[str]]:
    """Get language-specific patterns for text quality detection."""
    return LANGUAGE_PATTERNS.get(language, LANGUAGE_PATTERNS["en"])

# Quality score interpretation
QUALITY_SCORE_INTERPRETATION = {
    "excellent": (0.8, 1.0, "Text quality is excellent with no significant issues."),
    "good": (0.6, 0.8, "Text quality is good with minor areas for improvement."),
    "fair": (0.4, 0.6, "Text quality is fair but could be improved."),
    "poor": (0.2, 0.4, "Text quality is poor and needs significant improvement."),
    "critical": (0.0, 0.2, "Text quality is critically low and requires immediate attention.")
}

def interpret_quality_score(score: float) -> Dict[str, any]:
    """Interpret a quality score and return description and recommendations."""
    for level, (min_score, max_score, description) in QUALITY_SCORE_INTERPRETATION.items():
        if min_score <= score < max_score:
            return {
                "level": level,
                "score_range": (min_score, max_score),
                "description": description,
                "recommendations": _get_recommendations_for_level(level)
            }
    
    return {
        "level": "unknown",
        "score_range": (0.0, 1.0),
        "description": "Unable to interpret quality score.",
        "recommendations": []
    }

def _get_recommendations_for_level(level: str) -> List[str]:
    """Get specific recommendations based on quality level."""
    recommendations = {
        "excellent": [
            "Continue maintaining this high quality standard.",
            "Consider sharing your writing techniques with others."
        ],
        "good": [
            "Review any minor issues identified.",
            "Consider adding more specific details where appropriate."
        ],
        "fair": [
            "Focus on improving clarity and specificity.",
            "Avoid vague language and filler words.",
            "Consider the tone and professionalism of your writing."
        ],
        "poor": [
            "Significantly revise the content for clarity.",
            "Remove aggressive or subservient language patterns.",
            "Add more specific and professional language.",
            "Consider getting feedback from others."
        ],
        "critical": [
            "Complete rewrite may be necessary.",
            "Focus on fundamental writing principles.",
            "Consider using writing assistance tools.",
            "Seek professional writing guidance."
        ]
    }
    
    return recommendations.get(level, [])


























