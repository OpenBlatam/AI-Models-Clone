"""
NotebookLM AI - Sistema NLP Avanzado
🧠 Procesamiento de lenguaje natural con capacidades avanzadas
"""

from .core.nlp_engine import (
    NLPEngine,
    NLPConfig,
    get_nlp_engine,
    cleanup_nlp_engine
)

from .processors.text_processor import (
    TextProcessor,
    TextProcessorConfig,
    get_text_processor
)

from .processors.tokenizer import (
    AdvancedTokenizer,
    TokenizerConfig,
    get_tokenizer
)

from .processors.embedder import (
    EmbeddingEngine,
    EmbeddingConfig,
    get_embedding_engine
)

from .analyzers.sentiment_analyzer import (
    SentimentAnalyzer,
    SentimentConfig,
    get_sentiment_analyzer
)

from .analyzers.keyword_extractor import (
    KeywordExtractor,
    KeywordConfig,
    get_keyword_extractor
)

from .analyzers.topic_modeler import (
    TopicModeler,
    TopicConfig,
    get_topic_modeler
)

from .analyzers.entity_recognizer import (
    EntityRecognizer,
    EntityConfig,
    get_entity_recognizer
)

from .analyzers.summarizer import (
    TextSummarizer,
    SummaryConfig,
    get_summarizer
)

from .analyzers.classifier import (
    TextClassifier,
    ClassificationConfig,
    get_classifier
)

from .utils.nlp_utils import (
    NLPUtils,
    TextMetrics,
    LanguageDetector
)

__all__ = [
    # Motor principal
    "NLPEngine",
    "NLPConfig", 
    "get_nlp_engine",
    "cleanup_nlp_engine",
    
    # Procesadores
    "TextProcessor",
    "TextProcessorConfig",
    "get_text_processor",
    
    "AdvancedTokenizer",
    "TokenizerConfig", 
    "get_tokenizer",
    
    "EmbeddingEngine",
    "EmbeddingConfig",
    "get_embedding_engine",
    
    # Analizadores
    "SentimentAnalyzer",
    "SentimentConfig",
    "get_sentiment_analyzer",
    
    "KeywordExtractor",
    "KeywordConfig",
    "get_keyword_extractor",
    
    "TopicModeler",
    "TopicConfig",
    "get_topic_modeler",
    
    "EntityRecognizer",
    "EntityConfig",
    "get_entity_recognizer",
    
    "TextSummarizer",
    "SummaryConfig",
    "get_summarizer",
    
    "TextClassifier",
    "ClassificationConfig",
    "get_classifier",
    
    # Utilidades
    "NLPUtils",
    "TextMetrics",
    "LanguageDetector"
]

__version__ = "2.0.0"
__author__ = "NotebookLM AI Team"
__description__ = "Sistema NLP avanzado para NotebookLM AI" 