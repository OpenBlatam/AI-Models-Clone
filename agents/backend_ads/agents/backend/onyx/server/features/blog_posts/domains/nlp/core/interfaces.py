"""
Core Interfaces for Modular NLP System.

This module defines the main interfaces and abstract base classes
for the NLP analysis system, ensuring loose coupling and high modularity.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum

class AnalysisType(Enum):
    """Types of NLP analysis available."""
    READABILITY = "readability"
    SENTIMENT = "sentiment"
    SEO = "seo"
    SEMANTIC = "semantic"
    LANGUAGE = "language"
    ENTITY = "entity"
    KEYWORD = "keyword"
    GRAMMAR = "grammar"

class Priority(Enum):
    """Priority levels for analysis."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class AnalysisResult:
    """Base result class for all NLP analyses."""
    analysis_type: AnalysisType
    score: float  # 0-100
    confidence: float  # 0-1
    metadata: Dict[str, Any]
    processing_time_ms: float
    recommendations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            'analysis_type': self.analysis_type.value,
            'score': self.score,
            'confidence': self.confidence,
            'metadata': self.metadata,
            'processing_time_ms': self.processing_time_ms,
            'recommendations': self.recommendations
        }

@dataclass
class AnalysisConfig:
    """Configuration for NLP analysis."""
    enabled: bool = True
    priority: Priority = Priority.MEDIUM
    timeout_ms: int = 5000
    cache_enabled: bool = True
    parameters: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}

class IAnalyzer(ABC):
    """Interface for all NLP analyzers."""
    
    @property
    @abstractmethod
    def analysis_type(self) -> AnalysisType:
        """Get the type of analysis this analyzer performs."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the name of this analyzer."""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Get the version of this analyzer."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this analyzer is available (dependencies installed, etc.)."""
        pass
    
    @abstractmethod
    def analyze(self, text: str, config: Optional[AnalysisConfig] = None) -> AnalysisResult:
        """
        Analyze the given text.
        
        Args:
            text: Text to analyze
            config: Optional configuration for analysis
            
        Returns:
            AnalysisResult with analysis data
        """
        pass
    
    @abstractmethod
    def validate_input(self, text: str) -> bool:
        """Validate input text for this analyzer."""
        pass

class IAnalyzerManager(ABC):
    """Interface for analyzer managers."""
    
    @abstractmethod
    def register_analyzer(self, analyzer: IAnalyzer) -> None:
        """Register an analyzer with this manager."""
        pass
    
    @abstractmethod
    def get_analyzer(self, name: str) -> Optional[IAnalyzer]:
        """Get an analyzer by name."""
        pass
    
    @abstractmethod
    def get_available_analyzers(self) -> List[IAnalyzer]:
        """Get all available analyzers."""
        pass
    
    @abstractmethod
    def analyze_all(self, text: str, config: Optional[Dict[str, AnalysisConfig]] = None) -> Dict[str, AnalysisResult]:
        """Run all available analyzers on the text."""
        pass

class IEnhancer(ABC):
    """Interface for content enhancers."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the name of this enhancer."""
        pass
    
    @abstractmethod
    def can_enhance(self, analysis_result: AnalysisResult) -> bool:
        """Check if this enhancer can improve the content based on analysis."""
        pass
    
    @abstractmethod
    def enhance(self, text: str, analysis_result: AnalysisResult) -> str:
        """
        Enhance the text based on analysis results.
        
        Args:
            text: Original text
            analysis_result: Analysis result suggesting improvements
            
        Returns:
            Enhanced text
        """
        pass

class IEnhancementManager(ABC):
    """Interface for enhancement managers."""
    
    @abstractmethod
    def register_enhancer(self, enhancer: IEnhancer) -> None:
        """Register an enhancer with this manager."""
        pass
    
    @abstractmethod
    def enhance_content(self, text: str, analysis_results: Dict[str, AnalysisResult]) -> str:
        """Enhance content based on multiple analysis results."""
        pass

class IConfiguration(ABC):
    """Interface for configuration management."""
    
    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        pass
    
    @abstractmethod
    def get_analyzer_config(self, analyzer_name: str) -> AnalysisConfig:
        """Get configuration for specific analyzer."""
        pass

class ICache(ABC):
    """Interface for caching analysis results."""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get cached value."""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> None:
        """Set cached value with TTL."""
        pass
    
    @abstractmethod
    def invalidate(self, key: str) -> None:
        """Invalidate cached value."""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all cached values."""
        pass

class IPlugin(ABC):
    """Interface for NLP plugins."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get plugin name."""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Get plugin version."""
        pass
    
    @abstractmethod
    def initialize(self, config: IConfiguration) -> bool:
        """Initialize the plugin."""
        pass
    
    @abstractmethod
    def get_analyzers(self) -> List[IAnalyzer]:
        """Get analyzers provided by this plugin."""
        pass
    
    @abstractmethod
    def get_enhancers(self) -> List[IEnhancer]:
        """Get enhancers provided by this plugin."""
        pass

class INLPEngine(ABC):
    """Interface for the main NLP engine."""
    
    @abstractmethod
    def add_plugin(self, plugin: IPlugin) -> None:
        """Add a plugin to the engine."""
        pass
    
    @abstractmethod
    def analyze_content(
        self,
        text: str,
        title: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, AnalysisConfig]] = None
    ) -> Dict[str, AnalysisResult]:
        """Perform comprehensive content analysis."""
        pass
    
    @abstractmethod
    def enhance_content(
        self,
        text: str,
        analysis_results: Optional[Dict[str, AnalysisResult]] = None,
        enhancement_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Enhance content based on analysis results."""
        pass
    
    @abstractmethod
    def get_quality_score(self, analysis_results: Dict[str, AnalysisResult]) -> float:
        """Calculate overall quality score from analysis results."""
        pass

# Type aliases for convenience
AnalysisResults = Dict[str, AnalysisResult]
EnhancementConfig = Dict[str, Any]
Metadata = Dict[str, Any] 