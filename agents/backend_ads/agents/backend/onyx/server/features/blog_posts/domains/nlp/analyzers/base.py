"""
Base Analyzer for Modular NLP System.

This module provides the base class for all NLP analyzers, implementing
common functionality and providing a template for specific analyzers.
"""

import time
import logging
import hashlib
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass

from ..core import (
    IAnalyzer, AnalysisType, AnalysisResult, AnalysisConfig, Priority,
    AnalyzerException, InvalidInputException, AnalysisFailedException,
    AnalyzerTimeoutException, get_config
)

logger = logging.getLogger(__name__)

@dataclass
class ValidationRule:
    """Validation rule for input text."""
    name: str
    validator: Callable[[str], bool]
    error_message: str

class BaseAnalyzer(IAnalyzer):
    """
    Base class for all NLP analyzers.
    
    Provides common functionality including:
    - Input validation
    - Performance monitoring
    - Error handling
    - Caching integration
    - Configuration management
    """
    
    def __init__(
        self,
        name: str,
        analysis_type: AnalysisType,
        version: str = "1.0.0",
        description: str = "",
        dependencies: Optional[List[str]] = None
    ):
        """
        Initialize base analyzer.
        
        Args:
            name: Unique name for this analyzer
            analysis_type: Type of analysis this analyzer performs
            version: Version of the analyzer
            description: Description of the analyzer
            dependencies: List of required dependencies
        """
        self._name = name
        self._analysis_type = analysis_type
        self._version = version
        self._description = description
        self._dependencies = dependencies or []
        
        # Performance tracking
        self._analysis_count = 0
        self._total_processing_time = 0.0
        self._error_count = 0
        
        # Validation rules
        self._validation_rules: List[ValidationRule] = []
        self._setup_default_validation_rules()
        
        # Configuration
        self._config_manager = get_config()
        
        logger.debug(f"Initialized {self._name} analyzer v{self._version}")
    
    @property
    def name(self) -> str:
        """Get the name of this analyzer."""
        return self._name
    
    @property
    def analysis_type(self) -> AnalysisType:
        """Get the type of analysis this analyzer performs."""
        return self._analysis_type
    
    @property
    def version(self) -> str:
        """Get the version of this analyzer."""
        return self._version
    
    @property
    def description(self) -> str:
        """Get the description of this analyzer."""
        return self._description
    
    @property
    def dependencies(self) -> List[str]:
        """Get the list of dependencies."""
        return self._dependencies.copy()
    
    def is_available(self) -> bool:
        """
        Check if this analyzer is available.
        
        Default implementation checks if all dependencies are importable.
        Subclasses should override this method for more specific checks.
        """
        try:
            return self._check_dependencies()
        except Exception as e:
            logger.error(f"Error checking availability for {self._name}: {e}")
            return False
    
    def analyze(self, text: str, config: Optional[AnalysisConfig] = None) -> AnalysisResult:
        """
        Analyze the given text.
        
        This method implements the common analysis workflow:
        1. Validate input
        2. Get configuration
        3. Check timeout
        4. Perform analysis
        5. Track performance
        6. Return results
        
        Args:
            text: Text to analyze
            config: Optional configuration for analysis
            
        Returns:
            AnalysisResult with analysis data
            
        Raises:
            InvalidInputException: If input validation fails
            AnalyzerTimeoutException: If analysis times out
            AnalysisFailedException: If analysis fails
        """
        start_time = time.time()
        
        try:
            # Validate input
            if not self.validate_input(text):
                raise InvalidInputException(
                    self._name, 
                    "Input validation failed"
                )
            
            # Get configuration
            analysis_config = config or self._get_default_config()
            
            # Check if analyzer is enabled
            if not analysis_config.enabled:
                return self._create_disabled_result()
            
            # Perform the actual analysis with timeout
            result = self._analyze_with_timeout(text, analysis_config)
            
            # Track performance
            processing_time = (time.time() - start_time) * 1000
            result.processing_time_ms = processing_time
            
            self._analysis_count += 1
            self._total_processing_time += processing_time
            
            logger.debug(
                f"{self._name} analysis completed in {processing_time:.2f}ms "
                f"(score: {result.score:.1f})"
            )
            
            return result
            
        except Exception as e:
            self._error_count += 1
            processing_time = (time.time() - start_time) * 1000
            
            if isinstance(e, (InvalidInputException, AnalyzerTimeoutException)):
                raise
            else:
                logger.error(f"Analysis failed for {self._name}: {e}")
                raise AnalysisFailedException(self._name, str(e))
    
    def validate_input(self, text: str) -> bool:
        """
        Validate input text for this analyzer.
        
        Args:
            text: Text to validate
            
        Returns:
            True if input is valid
        """
        if not isinstance(text, str):
            return False
        
        # Run all validation rules
        for rule in self._validation_rules:
            try:
                if not rule.validator(text):
                    logger.warning(f"Validation failed for {self._name}: {rule.error_message}")
                    return False
            except Exception as e:
                logger.error(f"Error in validation rule '{rule.name}': {e}")
                return False
        
        return True
    
    def add_validation_rule(self, rule: ValidationRule):
        """Add a validation rule for input text."""
        self._validation_rules.append(rule)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for this analyzer."""
        avg_time = (
            self._total_processing_time / self._analysis_count 
            if self._analysis_count > 0 else 0
        )
        
        return {
            'name': self._name,
            'analysis_count': self._analysis_count,
            'error_count': self._error_count,
            'success_rate': (
                (self._analysis_count - self._error_count) / self._analysis_count * 100
                if self._analysis_count > 0 else 0
            ),
            'average_processing_time_ms': avg_time,
            'total_processing_time_ms': self._total_processing_time
        }
    
    def reset_performance_stats(self):
        """Reset performance statistics."""
        self._analysis_count = 0
        self._total_processing_time = 0.0
        self._error_count = 0
    
    @abstractmethod
    def _perform_analysis(self, text: str, config: AnalysisConfig) -> AnalysisResult:
        """
        Perform the actual analysis logic.
        
        This method must be implemented by subclasses to provide
        the specific analysis functionality.
        
        Args:
            text: Text to analyze
            config: Analysis configuration
            
        Returns:
            AnalysisResult with analysis data
        """
        pass
    
    def _analyze_with_timeout(self, text: str, config: AnalysisConfig) -> AnalysisResult:
        """
        Perform analysis with timeout handling.
        
        Args:
            text: Text to analyze
            config: Analysis configuration
            
        Returns:
            AnalysisResult with analysis data
            
        Raises:
            AnalyzerTimeoutException: If analysis times out
        """
        import signal
        
        def timeout_handler(signum, frame):
            raise AnalyzerTimeoutException(self._name, config.timeout_ms)
        
        # Set up timeout (only on Unix systems)
        old_handler = None
        if hasattr(signal, 'SIGALRM'):
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(config.timeout_ms // 1000)
        
        try:
            result = self._perform_analysis(text, config)
            return result
        finally:
            # Clean up timeout
            if hasattr(signal, 'SIGALRM') and old_handler is not None:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
    
    def _get_default_config(self) -> AnalysisConfig:
        """Get default configuration for this analyzer."""
        return self._config_manager.get_analyzer_config(self._name)
    
    def _create_disabled_result(self) -> AnalysisResult:
        """Create a result for when the analyzer is disabled."""
        return AnalysisResult(
            analysis_type=self._analysis_type,
            score=0.0,
            confidence=0.0,
            metadata={'status': 'disabled'},
            processing_time_ms=0.0,
            recommendations=[]
        )
    
    def _setup_default_validation_rules(self):
        """Set up default validation rules."""
        # Basic text validation rules
        self._validation_rules = [
            ValidationRule(
                name="not_empty",
                validator=lambda text: len(text.strip()) > 0,
                error_message="Text cannot be empty"
            ),
            ValidationRule(
                name="max_length",
                validator=lambda text: len(text) <= 50000,  # 50k character limit
                error_message="Text too long (max 50,000 characters)"
            ),
            ValidationRule(
                name="min_length",
                validator=lambda text: len(text.strip()) >= 10,
                error_message="Text too short (min 10 characters)"
            )
        ]
    
    def _check_dependencies(self) -> bool:
        """Check if all dependencies are available."""
        for dependency in self._dependencies:
            try:
                __import__(dependency)
            except ImportError:
                logger.warning(f"Missing dependency for {self._name}: {dependency}")
                return False
        return True
    
    def _generate_cache_key(self, text: str, config: AnalysisConfig) -> str:
        """Generate a cache key for the analysis."""
        content = f"{self._name}:{self._version}:{text}:{str(config)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _create_error_result(self, error_message: str) -> AnalysisResult:
        """Create an error result."""
        return AnalysisResult(
            analysis_type=self._analysis_type,
            score=0.0,
            confidence=0.0,
            metadata={
                'status': 'error',
                'error_message': error_message
            },
            processing_time_ms=0.0,
            recommendations=[f"Error in {self._name}: {error_message}"]
        )
    
    def __repr__(self) -> str:
        """String representation of the analyzer."""
        return f"{self.__class__.__name__}(name='{self._name}', version='{self._version}')" 