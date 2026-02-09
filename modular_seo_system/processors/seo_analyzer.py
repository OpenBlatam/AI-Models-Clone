"""
SEO Analyzer - Modular text processing component
Implements comprehensive SEO analysis with configurable strategies
"""

import asyncio
import time
from typing import Any, Dict, List, Optional

from ..core.interfaces import BaseProcessor
from ..core.component_registry import component_registry


class SEOAnalyzer(BaseProcessor):
    """Modular SEO analyzer with configurable analysis strategies."""

    def __init__(self, name: str = "seo_analyzer", version: str = "2.0.0"):
        super().__init__(name, version)
        self._analysis_strategies: List[str] = []
        self._config: Dict[str, Any] = {
            "min_word_count": 300,
            "max_sentence_length": 20,
            "min_sentences": 5,
            "min_keywords": 5,
            "min_content_length": 1500,
            "keyword_density_range": (1.0, 3.0),
        }
        self._enabled_strategies: List[str] = []

    async def initialize(self) -> bool:
        """Initialize the SEO analyzer."""
        try:
            # Register with component registry
            component_registry.register(self, "processor")

            # Setup default strategies
            self._setup_default_strategies()

            self._health_status = True
            return True

        except Exception as e:
            print(f"Failed to initialize SEO analyzer: {e}")
            self._health_status = False
            return False

    async def shutdown(self) -> bool:
        """Shutdown the SEO analyzer."""
        try:
            # Unregister from component registry
            component_registry.unregister(self.name)

            self._health_status = False
            return True

        except Exception as e:
            print(f"Failed to shutdown SEO analyzer: {e}")
            return False

    async def health_check(self) -> bool:
        """Check analyzer health."""
        return self._health_status and self._enabled

    async def process(self, text: str) -> Dict[str, Any]:
        """Process text with comprehensive SEO analysis."""
        start_time = time.time()

        try:
            # Validate input
            validated_text = self._validate_text(text)

            # Perform analysis
            analysis_results = await self._perform_analysis(validated_text)

            # Calculate overall SEO score
            analysis_results["seo_score"] = self._calculate_seo_score(analysis_results)
            analysis_results["processing_time"] = time.time() - start_time
            analysis_results["timestamp"] = start_time
            analysis_results["analyzer"] = self.name
            analysis_results["version"] = self.version

            # Update statistics
            self._update_stats(True, analysis_results["processing_time"])

            return analysis_results

        except Exception as e:
            # Update statistics
            self._update_stats(False, time.time() - start_time)
            raise

    def get_capabilities(self) -> List[str]:
        """Get list of processing capabilities."""
        return [
            "seo_analysis",
            "text_metrics",
            "readability_analysis",
            "keyword_analysis",
            "structure_analysis",
            "sentiment_analysis",
        ]

    def get_metadata(self) -> Dict[str, Any]:
        """Get component metadata."""
        return {
            "name": self.name,
            "version": self.version,
            "capabilities": self.get_capabilities(),
            "enabled_strategies": self._enabled_strategies,
            "configuration": self._config.copy(),
        }

    def configure(self, config: Dict[str, Any]) -> None:
        """Configure the analyzer."""
        self._config.update(config)

    def enable_strategy(self, strategy_name: str) -> bool:
        """Enable a specific analysis strategy."""
        if strategy_name in self._analysis_strategies:
            if strategy_name not in self._enabled_strategies:
                self._enabled_strategies.append(strategy_name)
            return True
        return False

    def disable_strategy(self, strategy_name: str) -> bool:
        """Disable a specific analysis strategy."""
        if strategy_name in self._enabled_strategies:
            self._enabled_strategies.remove(strategy_name)
            return True
        return False

    def _setup_default_strategies(self) -> None:
        """Setup default analysis strategies."""
        self._analysis_strategies = ["basic_metrics", "readability", "keywords", "structure", "sentiment"]

        # Enable all strategies by default
        self._enabled_strategies = self._analysis_strategies.copy()

    def _validate_text(self, text: str) -> str:
        """Validate and clean input text."""
        if not isinstance(text, str):
            raise ValueError("Text must be a string")

        if not text.strip():
            raise ValueError("Text cannot be empty")

        # Clean and normalize
        cleaned = text.strip()
        cleaned = " ".join(cleaned.split())  # Normalize whitespace

        if len(cleaned) > 10000:
            raise ValueError("Text too long (max 10000 characters)")

        return cleaned

    async def _perform_analysis(self, text: str) -> Dict[str, Any]:
        """Perform analysis using enabled strategies."""
        analysis_results = {}

        # Basic metrics (always enabled)
        if "basic_metrics" in self._enabled_strategies:
            basic_metrics = await self._analyze_basic_metrics(text)
            analysis_results.update(basic_metrics)

        # Readability analysis
        if "readability" in self._enabled_strategies:
            readability = await self._analyze_readability(text)
            analysis_results.update(readability)

        # Keyword analysis
        if "keywords" in self._enabled_strategies:
            keywords = await self._analyze_keywords(text)
            analysis_results.update(keywords)

        # Structure analysis
        if "structure" in self._enabled_strategies:
            structure = await self._analyze_structure(text)
            analysis_results.update(structure)

        # Sentiment analysis
        if "sentiment" in self._enabled_strategies:
            sentiment = await self._analyze_sentiment(text)
            analysis_results.update(sentiment)

        return analysis_results

    async def _analyze_basic_metrics(self, text: str) -> Dict[str, Any]:
        """Analyze basic text metrics."""
        words = text.split()
        sentences = text.split(".")

        return {
            "word_count": len(words),
            "character_count": len(text),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "avg_word_length": sum(len(word) for word in words) / max(len(words), 1),
            "avg_sentence_length": len(words) / max(len([s for s in sentences if s.strip()]), 1),
        }

    async def _analyze_readability(self, text: str) -> Dict[str, Any]:
        """Analyze text readability."""
        words = text.split()
        sentences = [s for s in text.split(".") if s.strip()]

        # Simple Flesch Reading Ease approximation
        avg_sentence_length = len(words) / max(len(sentences), 1)
        avg_word_length = sum(len(word) for word in words) / max(len(words), 1)

        # Calculate readability score (0-1, higher is more readable)
        readability_score = max(0, 1 - (avg_sentence_length / 30) - (avg_word_length / 10))

        return {
            "readability_score": readability_score,
            "complexity_level": self._get_complexity_level(readability_score),
        }

    async def _analyze_keywords(self, text: str) -> Dict[str, Any]:
        """Analyze keywords and their density."""
        words = [word.lower().strip(".,!?;:") for word in text.split()]

        # Filter meaningful words
        meaningful_words = [word for word in words if len(word) >= 3 and word not in self._get_stop_words()]

        # Count word frequency
        word_freq = {}
        for word in meaningful_words:
            word_freq[word] = word_freq.get(word, 0) + 1

        # Get top keywords
        top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]

        # Calculate keyword density
        total_words = len(words)
        keyword_density = {word: count / total_words for word, count in top_keywords}

        return {
            "unique_keywords": len(word_freq),
            "top_keywords": top_keywords,
            "keyword_density": keyword_density,
            "keyword_variety_score": min(len(word_freq) / 10, 1.0),
        }

    async def _analyze_structure(self, text: str) -> Dict[str, Any]:
        """Analyze text structure and organization."""
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        sentences = [s.strip() for s in text.split(".") if s.strip()]

        # Analyze paragraph structure
        paragraph_lengths = [len(p.split()) for p in paragraphs]
        avg_paragraph_length = sum(paragraph_lengths) / max(len(paragraph_lengths), 1)

        # Analyze sentence variety
        sentence_lengths = [len(s.split()) for s in sentences]
        if sentence_lengths:
            sentence_variety = 1 - (sum(sentence_lengths) / len(sentence_lengths) / 30)
        else:
            sentence_variety = 0.0

        return {
            "paragraph_count": len(paragraphs),
            "avg_paragraph_length": avg_paragraph_length,
            "sentence_variety": sentence_variety,
            "structure_score": self._calculate_structure_score(paragraphs, sentences),
        }

    async def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze text sentiment (basic implementation)."""
        # Simple sentiment analysis based on positive/negative words
        positive_words = {"good", "great", "excellent", "amazing", "wonderful", "best", "love", "like"}
        negative_words = {"bad", "terrible", "awful", "worst", "hate", "dislike", "poor", "horrible"}

        words = text.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)

        total_words = len(words)
        if total_words == 0:
            sentiment_score = 0.0
        else:
            sentiment_score = (positive_count - negative_count) / total_words

        return {
            "sentiment_score": sentiment_score,
            "positive_words_count": positive_count,
            "negative_words_count": negative_count,
            "sentiment_label": self._get_sentiment_label(sentiment_score),
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

    def _get_stop_words(self) -> set:
        """Get common stop words."""
        return {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "can",
            "this",
            "that",
            "these",
            "those",
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

    def _get_sentiment_label(self, score: float) -> str:
        """Get sentiment label based on score."""
        if score >= 0.1:
            return "Positive"
        elif score <= -0.1:
            return "Negative"
        else:
            return "Neutral"

    def _calculate_seo_score(self, results: Dict[str, Any]) -> int:
        """Calculate overall SEO score."""
        score = 0

        # Word count score
        word_count = results.get("word_count", 0)
        if word_count >= self._config["min_word_count"]:
            score += 20

        # Sentence structure score
        sentence_count = results.get("sentence_count", 0)
        if sentence_count >= self._config["min_sentences"]:
            score += 20

        # Readability score
        readability_score = results.get("readability_score", 0)
        if readability_score >= 0.7:
            score += 20

        # Keyword score
        keyword_count = results.get("unique_keywords", 0)
        if keyword_count >= self._config["min_keywords"]:
            score += 20

        # Content length score
        content_length = results.get("character_count", 0)
        if content_length >= self._config["min_content_length"]:
            score += 20

        return min(score, 100)
