"""
Specialized NLP analyzers for different content aspects.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

from .models import (
    SemanticAnalysisResult, ReadabilityMetrics, SentimentMetrics,
    SEOMetrics, QualityScores, NLPConfig, AnalysisMode
)
from . import (
    SPACY_AVAILABLE, NLTK_AVAILABLE, TRANSFORMERS_AVAILABLE,
    TEXTSTAT_AVAILABLE, YAKE_AVAILABLE, TEXTBLOB_AVAILABLE,
    LANGDETECT_AVAILABLE, SENTENCE_TRANSFORMERS_AVAILABLE
)

logger = logging.getLogger(__name__)

class ReadabilityAnalyzer:
    """Analyzes content readability using multiple metrics."""
    
    def analyze(self, content: str) -> ReadabilityMetrics:
        """Analyze readability of content."""
        metrics = ReadabilityMetrics()
        
        if not TEXTSTAT_AVAILABLE:
            logger.warning("Textstat not available for readability analysis")
            return metrics
        
        try:
            import textstat
            
            # Core readability metrics
            metrics.flesch_reading_ease = textstat.flesch_reading_ease(content)
            metrics.flesch_kincaid_grade = textstat.flesch_kincaid_grade(content)
            metrics.gunning_fog = textstat.gunning_fog(content)
            metrics.coleman_liau_index = textstat.coleman_liau_index(content)
            metrics.automated_readability_index = textstat.automated_readability_index(content)
            metrics.dale_chall_readability = textstat.dale_chall_readability_score(content)
            metrics.difficult_words = textstat.difficult_words(content)
            
            # Additional metrics
            word_count = len(content.split())
            sentence_count = len(re.findall(r'[.!?]+', content))
            
            if sentence_count > 0:
                metrics.avg_sentence_length = word_count / sentence_count
            
            # Calculate syllables and complex words
            syllable_count = textstat.syllable_count(content)
            if word_count > 0:
                metrics.avg_syllables_per_word = syllable_count / word_count
                metrics.complex_words_ratio = metrics.difficult_words / word_count
                
            logger.info(f"Readability analysis completed. Flesch score: {metrics.flesch_reading_ease:.1f}")
            
        except Exception as e:
            logger.error(f"Readability analysis failed: {e}")
        
        return metrics

class SentimentAnalyzer:
    """Analyzes content sentiment and emotions."""
    
    def __init__(self):
        self.transformer_model = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize sentiment analysis models."""
        if TRANSFORMERS_AVAILABLE:
            try:
                from transformers import pipeline
                self.transformer_model = pipeline(
                    "sentiment-analysis",
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                    return_all_scores=True
                )
            except Exception as e:
                logger.warning(f"Could not initialize transformer sentiment model: {e}")
    
    def analyze(self, content: str) -> SentimentMetrics:
        """Analyze sentiment of content."""
        metrics = SentimentMetrics()
        
        # Try TextBlob first (faster and simpler)
        if TEXTBLOB_AVAILABLE:
            try:
                from textblob import TextBlob
                blob = TextBlob(content)
                metrics.polarity = blob.sentiment.polarity
                metrics.subjectivity = blob.sentiment.subjectivity
                
                # Determine sentiment label
                if metrics.polarity > 0.1:
                    metrics.label = "positive"
                elif metrics.polarity < -0.1:
                    metrics.label = "negative"
                else:
                    metrics.label = "neutral"
                
                metrics.confidence = abs(metrics.polarity)
                
            except Exception as e:
                logger.warning(f"TextBlob sentiment analysis failed: {e}")
        
        # Try transformers for more detailed analysis
        if self.transformer_model and len(content) < 512:
            try:
                results = self.transformer_model(content)
                if results and len(results[0]) > 0:
                    # Get the most confident prediction
                    best_result = max(results[0], key=lambda x: x['score'])
                    metrics.label = best_result['label'].lower()
                    metrics.confidence = best_result['score']
                    
                    # Store all emotion scores
                    for result in results[0]:
                        metrics.emotions[result['label'].lower()] = result['score']
                        
            except Exception as e:
                logger.warning(f"Transformer sentiment analysis failed: {e}")
        
        logger.info(f"Sentiment analysis completed. Label: {metrics.label}, Confidence: {metrics.confidence:.2f}")
        return metrics

class KeywordAnalyzer:
    """Extracts and analyzes keywords from content."""
    
    def extract_keywords(self, content: str, max_keywords: int = 20) -> List[Tuple[str, float]]:
        """Extract important keywords from content."""
        keywords = []
        
        # Try YAKE for advanced keyword extraction
        if YAKE_AVAILABLE:
            try:
                import yake
                
                kw_extractor = yake.KeywordExtractor(
                    lan="en",  # Default to English
                    n=3,  # Extract up to 3-word phrases
                    dedupLim=0.9,
                    top=max_keywords,
                    features=None
                )
                
                yake_keywords = kw_extractor.extract_keywords(content)
                # YAKE returns (score, keyword) where lower score = better
                keywords = [(kw, 1.0 - min(score, 1.0)) for score, kw in yake_keywords]
                
            except Exception as e:
                logger.warning(f"YAKE keyword extraction failed: {e}")
        
        # Fallback: simple frequency-based extraction
        if not keywords:
            try:
                words = re.findall(r'\b[a-zA-Z]{4,}\b', content.lower())
                if NLTK_AVAILABLE:
                    import nltk
                    from nltk.corpus import stopwords
                    stop_words = set(stopwords.words('english'))
                    words = [w for w in words if w not in stop_words]
                
                word_freq = {}
                for word in words:
                    word_freq[word] = word_freq.get(word, 0) + 1
                
                # Get top words
                sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
                total_words = len(words)
                keywords = [(word, freq/total_words) for word, freq in sorted_words[:max_keywords]]
                
            except Exception as e:
                logger.warning(f"Fallback keyword extraction failed: {e}")
        
        logger.info(f"Extracted {len(keywords)} keywords")
        return keywords

class EntityAnalyzer:
    """Extracts named entities from content."""
    
    def __init__(self, language: str = "en"):
        self.language = language
        self.nlp_model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize spaCy model for entity extraction."""
        if SPACY_AVAILABLE:
            try:
                import spacy
                
                if self.language == "es":
                    try:
                        self.nlp_model = spacy.load("es_core_news_md")
                    except OSError:
                        try:
                            self.nlp_model = spacy.load("es_core_news_sm")
                        except OSError:
                            logger.warning("Spanish spaCy model not found")
                
                elif self.language == "en":
                    try:
                        self.nlp_model = spacy.load("en_core_web_md")
                    except OSError:
                        try:
                            self.nlp_model = spacy.load("en_core_web_sm")
                        except OSError:
                            logger.warning("English spaCy model not found")
                            
            except Exception as e:
                logger.error(f"Error initializing spaCy model: {e}")
    
    def extract_entities(self, content: str, max_entities: int = 50) -> List[Dict[str, Any]]:
        """Extract named entities from content."""
        entities = []
        
        if not self.nlp_model:
            logger.warning("No spaCy model available for entity extraction")
            return entities
        
        try:
            # Limit content length for performance
            doc = self.nlp_model(content[:2000])
            
            for ent in doc.ents:
                entity = {
                    "text": ent.text.strip(),
                    "label": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "confidence": getattr(ent, "confidence", 1.0)
                }
                entities.append(entity)
                
                if len(entities) >= max_entities:
                    break
            
            logger.info(f"Extracted {len(entities)} named entities")
            
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
        
        return entities

class SEOAnalyzer:
    """Analyzes SEO aspects of content."""
    
    def analyze(
        self,
        content: str,
        title: str = "",
        meta_description: str = "",
        target_keywords: Optional[List[str]] = None
    ) -> SEOMetrics:
        """Analyze SEO metrics of content."""
        metrics = SEOMetrics()
        
        if not target_keywords:
            target_keywords = []
        
        # Calculate keyword density
        if target_keywords:
            content_lower = content.lower()
            total_words = len(content.split())
            
            for keyword in target_keywords:
                keyword_lower = keyword.lower()
                keyword_count = content_lower.count(keyword_lower)
                density = (keyword_count / total_words) * 100 if total_words > 0 else 0
                metrics.keyword_density[keyword] = density
                
                # Check title keyword presence
                if title and keyword_lower in title.lower():
                    metrics.title_keyword_presence = True
        
        # Analyze meta description quality
        if meta_description:
            desc_length = len(meta_description)
            if 150 <= desc_length <= 160:
                metrics.meta_description_quality = 100.0
            elif 120 <= desc_length <= 170:
                metrics.meta_description_quality = 80.0
            elif desc_length > 0:
                metrics.meta_description_quality = 60.0
        
        # Analyze heading structure (simplified)
        headings = re.findall(r'#+\s+.+', content)  # Markdown headings
        if headings:
            h1_count = len([h for h in headings if h.startswith('# ')])
            h2_count = len([h for h in headings if h.startswith('## ')])
            
            if h1_count == 1 and h2_count >= 2:
                metrics.heading_structure_score = 100.0
            elif h1_count <= 2 and h2_count >= 1:
                metrics.heading_structure_score = 80.0
            else:
                metrics.heading_structure_score = 60.0
        
        # Count links (simplified)
        metrics.internal_links_count = len(re.findall(r'\[.+\]\(.+\)', content))
        metrics.external_links_count = len(re.findall(r'https?://', content))
        
        logger.info(f"SEO analysis completed. Keyword densities: {metrics.keyword_density}")
        return metrics

class CoherenceAnalyzer:
    """Analyzes semantic coherence of content."""
    
    def __init__(self):
        self.sentence_model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize sentence transformer model."""
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                from sentence_transformers import SentenceTransformer
                self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                logger.error(f"Error initializing sentence transformer: {e}")
    
    def analyze_coherence(self, content: str) -> float:
        """Analyze semantic coherence of content."""
        if not self.sentence_model:
            logger.warning("Sentence transformer not available for coherence analysis")
            return 0.0
        
        try:
            # Split content into sentences
            sentences = re.split(r'[.!?]+', content)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if len(sentences) < 2:
                return 100.0  # Single sentence is perfectly coherent
            
            # Get embeddings for all sentences
            embeddings = self.sentence_model.encode(sentences)
            
            # Calculate pairwise similarities
            from sklearn.metrics.pairwise import cosine_similarity
            similarities = cosine_similarity(embeddings)
            
            # Calculate average coherence (excluding diagonal)
            total_similarity = 0
            count = 0
            for i in range(len(similarities)):
                for j in range(i + 1, len(similarities)):
                    total_similarity += similarities[i][j]
                    count += 1
            
            if count > 0:
                avg_coherence = total_similarity / count
                coherence_score = avg_coherence * 100
                logger.info(f"Semantic coherence score: {coherence_score:.1f}")
                return coherence_score
            
        except Exception as e:
            logger.error(f"Coherence analysis failed: {e}")
        
        return 0.0 