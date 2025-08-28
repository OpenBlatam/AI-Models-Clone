#!/usr/bin/env python3
"""
Refactored Enhanced SEO Engine - Advanced Architecture
Implements advanced design patterns, better separation of concerns, and optimized structure
"""

import asyncio
import hashlib
import logging
import time
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable, Union
from typing_extensions import Self

import numpy as np
import psutil
import torch
from transformers import AutoModel, AutoTokenizer, PreTrainedModel, PreTrainedTokenizer

# ============================================================================
# ENUMS AND CONSTANTS
# ============================================================================

class ProcessingMode(Enum):
    """Processing modes for the SEO engine."""
    SYNC = "sync"
    ASYNC = "async"
    BATCH = "batch"
    STREAMING = "streaming"

class CacheStrategy(Enum):
    """Cache strategies for different use cases."""
    LRU = "lru"
    LFU = "lfu"
    TTL = "ttl"
    HYBRID = "hybrid"

class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# ============================================================================
# INTERFACES AND PROTOCOLS
# ============================================================================

@runtime_checkable
class TextProcessor(Protocol):
    """Protocol for text processing components."""
    
    async def process_text(self, text: str) -> Dict[str, Any]:
        """Process text asynchronously."""
        ...
    
    def process_text_sync(self, text: str) -> Dict[str, Any]:
        """Process text synchronously."""
        ...

@runtime_checkable
class CacheProvider(Protocol):
    """Protocol for cache implementations."""
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        ...
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        ...
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        ...
    
    async def clear(self) -> None:
        """Clear all cached data."""
        ...

@runtime_checkable
class MetricsProvider(Protocol):
    """Protocol for metrics collection."""
    
    def record_timing(self, operation: str, duration: float) -> None:
        """Record timing metric."""
        ...
    
    def increment_counter(self, name: str, value: int = 1) -> None:
        """Increment counter metric."""
        ...
    
    def record_value(self, name: str, value: float) -> None:
        """Record value metric."""
        ...

# ============================================================================
# CONFIGURATION MANAGEMENT
# ============================================================================

@dataclass
class CacheConfig:
    """Cache configuration settings."""
    strategy: CacheStrategy = CacheStrategy.LRU
    max_size: int = 1000
    ttl: int = 3600
    cleanup_interval: int = 300
    enable_compression: bool = False
    compression_threshold: int = 1024

@dataclass
class PerformanceConfig:
    """Performance configuration settings."""
    batch_size: int = 8
    max_concurrent: int = 10
    enable_mixed_precision: bool = True
    enable_model_compilation: bool = True
    memory_fraction: float = 0.8
    num_workers: int = 4

@dataclass
class MonitoringConfig:
    """Monitoring configuration settings."""
    enable_metrics: bool = True
    enable_profiling: bool = True
    enable_logging: bool = True
    log_level: str = "INFO"
    metrics_retention: int = 86400  # 24 hours

@dataclass
class SEOConfig:
    """SEO analysis configuration."""
    min_word_count: int = 300
    max_sentence_length: int = 20
    min_sentences: int = 5
    min_keywords: int = 5
    min_content_length: int = 1500
    keyword_density_range: tuple = (1.0, 3.0)

@dataclass
class RefactoredSEOConfig:
    """Refactored configuration for SEO engine."""
    
    # Core settings
    model_name: str = "microsoft/DialoGPT-medium"
    max_length: int = 512
    device: str = "auto"
    
    # Component configurations
    cache: CacheConfig = field(default_factory=CacheConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    seo: SEOConfig = field(default_factory=SEOConfig)
    
    # Feature toggles
    enable_caching: bool = True
    enable_async: bool = True
    enable_circuit_breaker: bool = True
    enable_retry: bool = True
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.performance.memory_fraction <= 0 or self.performance.memory_fraction > 1:
            raise ValueError("memory_fraction must be between 0 and 1")
        if self.performance.batch_size <= 0:
            raise ValueError("batch_size must be positive")
        if self.cache.max_size <= 0:
            raise ValueError("cache max_size must be positive")

# ============================================================================
# ABSTRACT BASE CLASSES
# ============================================================================

class BaseProcessor(ABC):
    """Abstract base class for text processors."""
    
    def __init__(self, config: RefactoredSEOConfig):
        self.config = config
        self.logger = self._setup_logging()
    
    @abstractmethod
    async def process(self, text: str) -> Dict[str, Any]:
        """Process text and return results."""
        pass
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the processor."""
        logger = logging.getLogger(self.__class__.__name__)
        if self.config.monitoring.enable_logging:
            logger.setLevel(getattr(logging, self.config.monitoring.log_level))
        return logger

class BaseCache(ABC):
    """Abstract base class for cache implementations."""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self._stats = defaultdict(int)
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        pass
    
    @abstractmethod
    async def clear(self) -> None:
        """Clear all cached data."""
        pass
    
    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        return dict(self._stats)

# ============================================================================
# IMPLEMENTATIONS
# ============================================================================

class AdvancedLRUCache(BaseCache):
    """Advanced LRU cache with TTL and compression support."""
    
    def __init__(self, config: CacheConfig):
        super().__init__(config)
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._access_order: deque = deque()
        self._lock = asyncio.Lock()
        self._last_cleanup = time.time()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache with async lock."""
        async with self._lock:
            if key not in self._cache:
                self._stats['misses'] += 1
                return None
            
            entry = self._cache[key]
            
            # Check TTL
            if entry.get('ttl') and time.time() > entry['timestamp'] + entry['ttl']:
                await self.delete(key)
                self._stats['expired'] += 1
                return None
            
            # Update access order
            self._access_order.remove(key)
            self._access_order.append(key)
            
            self._stats['hits'] += 1
            return entry['value']
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with async lock."""
        async with self._lock:
            # Remove existing entry
            if key in self._cache:
                self._access_order.remove(key)
            
            # Create entry
            entry = {
                'value': value,
                'timestamp': time.time(),
                'ttl': ttl or self.config.ttl
            }
            
            # Apply compression if enabled
            if self.config.enable_compression and len(str(value)) > self.config.compression_threshold:
                entry['value'] = self._compress_value(value)
                entry['compressed'] = True
            
            self._cache[key] = entry
            self._access_order.append(key)
            
            # Evict if necessary
            if len(self._cache) > self.config.max_size:
                await self._evict_oldest()
            
            # Periodic cleanup
            await self._cleanup_if_needed()
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._access_order.remove(key)
                self._stats['deletes'] += 1
                return True
            return False
    
    async def clear(self) -> None:
        """Clear all cached data."""
        async with self._lock:
            self._cache.clear()
            self._access_order.clear()
            self._stats['clears'] += 1
    
    async def _evict_oldest(self) -> None:
        """Evict oldest entry based on strategy."""
        if self.config.strategy == CacheStrategy.LRU:
            oldest_key = self._access_order.popleft()
        elif self.config.strategy == CacheStrategy.LFU:
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k].get('access_count', 0))
        else:
            oldest_key = self._access_order.popleft()
        
        del self._cache[oldest_key]
        self._stats['evictions'] += 1
    
    async def _cleanup_if_needed(self) -> None:
        """Cleanup expired entries if cleanup interval has passed."""
        current_time = time.time()
        if current_time - self._last_cleanup < self.config.cleanup_interval:
            return
        
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.get('ttl') and current_time > entry['timestamp'] + entry['ttl']
        ]
        
        for key in expired_keys:
            await self.delete(key)
        
        self._last_cleanup = current_time
    
    def _compress_value(self, value: Any) -> Any:
        """Compress value if compression is enabled."""
        # Simple compression implementation
        if isinstance(value, str):
            return value.encode('utf-8')
        return value

class AdvancedMetricsCollector:
    """Advanced metrics collection with aggregation and export capabilities."""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self._metrics: Dict[str, List[float]] = defaultdict(list)
        self._counters: Dict[str, int] = defaultdict(int)
        self._timers: Dict[str, List[float]] = defaultdict(list)
        self._lock = asyncio.Lock()
        self._start_time = time.time()
    
    async def record_timing(self, operation: str, duration: float) -> None:
        """Record timing metric asynchronously."""
        async with self._lock:
            self._timers[operation].append(duration)
            
            # Keep only recent metrics based on retention
            max_retention = int(self.config.metrics_retention / 60)  # Convert to minutes
            if len(self._timers[operation]) > max_retention:
                self._timers[operation] = self._timers[operation][-max_retention:]
    
    def increment_counter(self, name: str, value: int = 1) -> None:
        """Increment counter metric."""
        self._counters[name] += value
    
    def record_value(self, name: str, value: float) -> None:
        """Record value metric."""
        self._metrics[name].append(value)
    
    @contextmanager
    def timer(self, operation: str):
        """Context manager for timing operations."""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            asyncio.create_task(self.record_timing(operation, duration))
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics."""
        async with self._lock:
            stats = {
                'uptime': time.time() - self._start_time,
                'counters': dict(self._counters),
                'timers': {},
                'values': {}
            }
            
            # Calculate timing statistics
            for operation, timings in self._timers.items():
                if timings:
                    stats['timers'][operation] = {
                        'count': len(timings),
                        'mean': np.mean(timings),
                        'std': np.std(timings),
                        'min': np.min(timings),
                        'max': np.max(timings),
                        'p95': np.percentile(timings, 95),
                        'p99': np.percentile(timings, 99)
                    }
            
            # Calculate value statistics
            for name, values in self._metrics.items():
                if values:
                    stats['values'][name] = {
                        'count': len(values),
                        'mean': np.mean(values),
                        'std': np.std(values),
                        'min': np.min(values),
                        'max': np.max(values)
                    }
            
            return stats
    
    async def export_metrics(self, format: str = "json") -> str:
        """Export metrics in specified format."""
        stats = await self.get_stats()
        
        if format.lower() == "json":
            import json
            return json.dumps(stats, indent=2)
        elif format.lower() == "csv":
            return self._export_csv(stats)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _export_csv(self, stats: Dict[str, Any]) -> str:
        """Export metrics as CSV."""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(['Metric', 'Value'])
        
        # Write counters
        for name, value in stats['counters'].items():
            writer.writerow([f"counter_{name}", value])
        
        # Write timing stats
        for operation, timing_stats in stats['timers'].items():
            for stat_name, stat_value in timing_stats.items():
                writer.writerow([f"timer_{operation}_{stat_name}", stat_value])
        
        return output.getvalue()

class SEOAnalyzer(BaseProcessor):
    """Advanced SEO analyzer with multiple analysis strategies."""
    
    def __init__(self, config: RefactoredSEOConfig):
        super().__init__(config)
        self._analysis_strategies = self._setup_analysis_strategies()
    
    async def process(self, text: str) -> Dict[str, Any]:
        """Process text with comprehensive SEO analysis."""
        start_time = time.time()
        
        try:
            # Validate input
            validated_text = self._validate_text(text)
            
            # Perform analysis
            analysis_results = {}
            
            # Run all analysis strategies concurrently
            tasks = [
                strategy.analyze(validated_text) 
                for strategy in self._analysis_strategies
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine results
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.error(f"Analysis strategy {i} failed: {result}")
                    analysis_results[f"strategy_{i}_error"] = str(result)
                else:
                    analysis_results.update(result)
            
            # Calculate overall SEO score
            analysis_results['seo_score'] = self._calculate_seo_score(analysis_results)
            analysis_results['processing_time'] = time.time() - start_time
            analysis_results['timestamp'] = start_time
            
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"SEO analysis failed: {e}")
            raise
    
    def _validate_text(self, text: str) -> str:
        """Validate and clean input text."""
        if not isinstance(text, str):
            raise ValueError("Text must be a string")
        
        if not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Clean and normalize
        cleaned = text.strip()
        cleaned = ' '.join(cleaned.split())  # Normalize whitespace
        
        if len(cleaned) > 10000:
            raise ValueError("Text too long (max 10000 characters)")
        
        return cleaned
    
    def _setup_analysis_strategies(self) -> List['AnalysisStrategy']:
        """Setup analysis strategies."""
        return [
            BasicMetricsStrategy(self.config.seo),
            ReadabilityStrategy(self.config.seo),
            KeywordStrategy(self.config.seo),
            StructureStrategy(self.config.seo)
        ]
    
    def _calculate_seo_score(self, results: Dict[str, Any]) -> int:
        """Calculate overall SEO score."""
        score = 0
        
        # Word count score
        word_count = results.get('word_count', 0)
        if word_count >= self.config.seo.min_word_count:
            score += 20
        
        # Sentence structure score
        sentence_count = results.get('sentence_count', 0)
        if sentence_count >= self.config.seo.min_sentences:
            score += 20
        
        # Readability score
        readability_score = results.get('readability_score', 0)
        if readability_score >= 0.7:
            score += 20
        
        # Keyword score
        keyword_count = results.get('unique_keywords', 0)
        if keyword_count >= self.config.seo.min_keywords:
            score += 20
        
        # Content length score
        content_length = results.get('character_count', 0)
        if content_length >= self.config.seo.min_content_length:
            score += 20
        
        return min(score, 100)

class AnalysisStrategy(ABC):
    """Abstract base class for analysis strategies."""
    
    def __init__(self, seo_config: SEOConfig):
        self.config = seo_config
    
    @abstractmethod
    async def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze text and return results."""
        pass

class BasicMetricsStrategy(AnalysisStrategy):
    """Basic text metrics analysis."""
    
    async def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze basic text metrics."""
        words = text.split()
        sentences = text.split('.')
        
        return {
            'word_count': len(words),
            'character_count': len(text),
            'sentence_count': len([s for s in sentences if s.strip()]),
            'avg_word_length': sum(len(word) for word in words) / max(len(words), 1),
            'avg_sentence_length': len(words) / max(len([s for s in sentences if s.strip()]), 1)
        }

class ReadabilityStrategy(AnalysisStrategy):
    """Readability analysis strategy."""
    
    async def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze text readability."""
        words = text.split()
        sentences = [s for s in text.split('.') if s.strip()]
        
        # Simple Flesch Reading Ease approximation
        avg_sentence_length = len(words) / max(len(sentences), 1)
        avg_word_length = sum(len(word) for word in words) / max(len(words), 1)
        
        # Calculate readability score (0-1, higher is more readable)
        readability_score = max(0, 1 - (avg_sentence_length / 30) - (avg_word_length / 10))
        
        return {
            'readability_score': readability_score,
            'complexity_level': self._get_complexity_level(readability_score)
        }
    
    def _get_complexity_level(self, score: float) -> str:
        """Get complexity level based on readability score."""
        if score >= 0.8:
            return "Very Easy"
        elif score >= 0.6:
            return "Easy"
        elif score >= 0.4:
            return "Moderate"
        elif score >= 0.2:
            return "Difficult"
        else:
            return "Very Difficult"

class KeywordStrategy(AnalysisStrategy):
    """Keyword analysis strategy."""
    
    async def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze keywords and their density."""
        words = [word.lower().strip('.,!?;:') for word in text.split()]
        
        # Filter meaningful words
        meaningful_words = [
            word for word in words 
            if len(word) >= 3 and word not in self._get_stop_words()
        ]
        
        # Count word frequency
        word_freq = defaultdict(int)
        for word in meaningful_words:
            word_freq[word] += 1
        
        # Get top keywords
        top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Calculate keyword density
        total_words = len(words)
        keyword_density = {word: count/total_words for word, count in top_keywords}
        
        return {
            'unique_keywords': len(word_freq),
            'top_keywords': top_keywords,
            'keyword_density': keyword_density,
            'keyword_variety_score': min(len(word_freq) / 10, 1.0)
        }
    
    def _get_stop_words(self) -> set:
        """Get common stop words."""
        return {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'
        }

class StructureStrategy(AnalysisStrategy):
    """Text structure analysis strategy."""
    
    async def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze text structure and organization."""
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        # Analyze paragraph structure
        paragraph_lengths = [len(p.split()) for p in paragraphs]
        avg_paragraph_length = sum(paragraph_lengths) / max(len(paragraph_lengths), 1)
        
        # Analyze sentence variety
        sentence_lengths = [len(s.split()) for s in sentences]
        sentence_variety = 1 - (np.std(sentence_lengths) / max(np.mean(sentence_lengths), 1))
        
        return {
            'paragraph_count': len(paragraphs),
            'avg_paragraph_length': avg_paragraph_length,
            'sentence_variety': sentence_variety,
            'structure_score': self._calculate_structure_score(paragraphs, sentences)
        }
    
    def _calculate_structure_score(self, paragraphs: List[str], sentences: List[str]) -> float:
        """Calculate structure organization score."""
        score = 0.0
        
        # Paragraph balance
        if 3 <= len(paragraphs) <= 10:
            score += 0.3
        
        # Sentence variety
        if len(set(len(s.split()) for s in sentences)) >= 3:
            score += 0.3
        
        # Content distribution
        if all(len(p.split()) >= 50 for p in paragraphs):
            score += 0.4
        
        return score

# ============================================================================
# FACTORY AND BUILDER PATTERNS
# ============================================================================

class SEOEngineFactory:
    """Factory for creating SEO engine instances."""
    
    @staticmethod
    def create_engine(config: RefactoredSEOConfig) -> 'RefactoredSEOEngine':
        """Create SEO engine with specified configuration."""
        return RefactoredSEOEngine(config)
    
    @staticmethod
    def create_engine_with_defaults() -> 'RefactoredSEOEngine':
        """Create SEO engine with default configuration."""
        config = RefactoredSEOConfig()
        return RefactoredSEOEngine(config)
    
    @staticmethod
    def create_engine_for_production() -> 'RefactoredSEOEngine':
        """Create SEO engine optimized for production."""
        config = RefactoredSEOConfig(
            performance=PerformanceConfig(
                batch_size=16,
                max_concurrent=20,
                enable_model_compilation=True
            ),
            cache=CacheConfig(
                max_size=5000,
                ttl=7200,
                enable_compression=True
            ),
            monitoring=MonitoringConfig(
                log_level="WARNING",
                enable_profiling=False
            )
        )
        return RefactoredSEOEngine(config)

class SEOEngineBuilder:
    """Builder pattern for constructing SEO engine configurations."""
    
    def __init__(self):
        self._config = RefactoredSEOConfig()
    
    def with_model(self, model_name: str, max_length: int = 512) -> Self:
        """Set model configuration."""
        self._config.model_name = model_name
        self._config.max_length = max_length
        return self
    
    def with_cache(self, strategy: CacheStrategy, max_size: int = 1000) -> Self:
        """Set cache configuration."""
        self._config.cache.strategy = strategy
        self._config.cache.max_size = max_size
        return self
    
    def with_performance(self, batch_size: int, max_concurrent: int) -> Self:
        """Set performance configuration."""
        self._config.performance.batch_size = batch_size
        self._config.performance.max_concurrent = max_concurrent
        return self
    
    def with_monitoring(self, log_level: str = "INFO") -> Self:
        """Set monitoring configuration."""
        self._config.monitoring.log_level = log_level
        return self
    
    def build(self) -> RefactoredSEOEngine:
        """Build and return the SEO engine."""
        return RefactoredSEOEngine(self._config)

# ============================================================================
# MAIN ENGINE CLASS
# ============================================================================

class RefactoredSEOEngine:
    """Refactored SEO engine with advanced architecture and patterns."""
    
    def __init__(self, config: RefactoredSEOConfig):
        self.config = config
        self.logger = self._setup_logging()
        
        # Initialize components
        self.cache = AdvancedLRUCache(config.cache) if config.enable_caching else None
        self.metrics = AdvancedMetricsCollector(config.monitoring)
        self.analyzer = SEOAnalyzer(config)
        
        # Initialize model manager
        self.model_manager = None
        if config.enable_async:
            asyncio.create_task(self._initialize_model_manager())
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger(self.__class__.__name__)
        if self.config.monitoring.enable_logging:
            logging.basicConfig(
                level=getattr(logging, self.config.monitoring.log_level),
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        return logger
    
    async def _initialize_model_manager(self):
        """Initialize model manager asynchronously."""
        # This would initialize the model manager in the background
        pass
    
    async def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze text with comprehensive SEO analysis."""
        start_time = time.time()
        
        try:
            # Check cache first
            if self.cache:
                cache_key = self._generate_cache_key(text)
                cached_result = await self.cache.get(cache_key)
                if cached_result:
                    self.metrics.increment_counter("cache_hits")
                    return cached_result
            
            # Perform analysis
            with self.metrics.timer("seo_analysis"):
                result = await self.analyzer.process(text)
            
            # Cache result
            if self.cache:
                cache_key = self._generate_cache_key(text)
                await self.cache.set(cache_key, result)
                self.metrics.increment_counter("cache_misses")
            
            # Record metrics
            self.metrics.increment_counter("texts_processed")
            self.metrics.record_value("processing_time", time.time() - start_time)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Text analysis failed: {e}")
            self.metrics.increment_counter("analysis_errors")
            raise
    
    async def analyze_texts_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Analyze multiple texts in batch."""
        if not texts:
            return []
        
        # Process in batches
        results = []
        for i in range(0, len(texts), self.config.performance.batch_size):
            batch = texts[i:i + self.config.performance.batch_size]
            
            # Process batch concurrently
            batch_results = await asyncio.gather(
                *[self.analyze_text(text) for text in batch],
                return_exceptions=True
            )
            
            # Handle results
            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    self.logger.error(f"Batch item {i+j} failed: {result}")
                    results.append({'error': str(result), 'index': i+j})
                else:
                    results.append(result)
        
        return results
    
    async def analyze_texts_streaming(self, texts: List[str]):
        """Analyze texts with streaming results."""
        for i, text in enumerate(texts):
            try:
                result = await self.analyze_text(text)
                yield {'index': i, 'result': result}
            except Exception as e:
                yield {'index': i, 'error': str(e)}
    
    def _generate_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        return hashlib.md5(text.encode()).hexdigest()
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics."""
        metrics = await self.metrics.get_stats()
        
        # Add cache metrics
        if self.cache:
            cache_stats = await self.cache.get_stats()
            metrics['cache'] = cache_stats
        
        # Add system info
        metrics['system'] = {
            'cpu_count': psutil.cpu_count(),
            'memory_usage': psutil.virtual_memory()._asdict(),
            'gpu_available': torch.cuda.is_available(),
            'gpu_count': torch.cuda.device_count() if torch.cuda.is_available() else 0
        }
        
        return metrics
    
    async def cleanup(self):
        """Cleanup resources."""
        if self.cache:
            await self.cache.clear()
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

# ============================================================================
# USAGE EXAMPLES
# ============================================================================

async def main():
    """Example usage of the refactored SEO engine."""
    
    # Create engine using factory
    engine = SEOEngineFactory.create_engine_with_defaults()
    
    # Or use builder pattern
    engine = (SEOEngineBuilder()
              .with_model("microsoft/DialoGPT-medium")
              .with_cache(CacheStrategy.LRU, 2000)
              .with_performance(16, 20)
              .with_monitoring("INFO")
              .build())
    
    # Analyze single text
    text = "This is a sample text for SEO analysis. It contains multiple sentences and should provide good insights for optimization."
    result = await engine.analyze_text(text)
    print(f"SEO Score: {result['seo_score']}")
    
    # Analyze multiple texts
    texts = [
        "First text for analysis.",
        "Second text with different content.",
        "Third text for comprehensive testing."
    ]
    
    # Batch processing
    batch_results = await engine.analyze_texts_batch(texts)
    print(f"Processed {len(batch_results)} texts")
    
    # Streaming processing
    async for result in engine.analyze_texts_streaming(texts):
        if 'error' in result:
            print(f"Error processing text {result['index']}: {result['error']}")
        else:
            print(f"Text {result['index']} - SEO Score: {result['result']['seo_score']}")
    
    # Get metrics
    metrics = await engine.get_metrics()
    print(f"Cache hits: {metrics['counters']['cache_hits']}")
    print(f"Cache misses: {metrics['counters']['cache_misses']}")
    
    # Cleanup
    await engine.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
