"""
Analizadores NLP modulares y extensibles.
"""

from .base import BaseAnalyzer, AnalyzerInterface
from .sentiment_analyzer import SentimentAnalyzer
from .readability_analyzer import ReadabilityAnalyzer
from .keyword_analyzer import KeywordAnalyzer
from .language_analyzer import LanguageAnalyzer

__all__ = [
    'BaseAnalyzer',
    'AnalyzerInterface', 
    'SentimentAnalyzer',
    'ReadabilityAnalyzer',
    'KeywordAnalyzer',
    'LanguageAnalyzer'
] 