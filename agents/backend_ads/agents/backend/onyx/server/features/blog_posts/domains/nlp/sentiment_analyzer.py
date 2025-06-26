"""
Advanced Sentiment Analyzer for Blog Content.
"""

import logging
from typing import Dict, Optional
from .models import SentimentMetrics
from . import TEXTBLOB_AVAILABLE, TRANSFORMERS_AVAILABLE, NLTK_AVAILABLE

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """
    Advanced sentiment analyzer using multiple NLP techniques.
    
    Combines TextBlob, NLTK VADER, and Transformer models for
    comprehensive sentiment analysis including polarity, subjectivity,
    and emotion detection.
    """
    
    def __init__(self):
        """Initialize the sentiment analyzer."""
        self.transformer_model = None
        self.vader_analyzer = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize sentiment analysis models."""
        # Initialize transformer model
        if TRANSFORMERS_AVAILABLE:
            try:
                from transformers import pipeline
                self.transformer_model = pipeline(
                    "sentiment-analysis",
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                    return_all_scores=True
                )
                logger.info("Transformer sentiment model initialized")
            except Exception as e:
                logger.warning(f"Could not initialize transformer sentiment model: {e}")
        
        # Initialize VADER sentiment analyzer
        if NLTK_AVAILABLE:
            try:
                import nltk
                from nltk.sentiment import SentimentIntensityAnalyzer
                nltk.download('vader_lexicon', quiet=True)
                self.vader_analyzer = SentimentIntensityAnalyzer()
                logger.info("VADER sentiment analyzer initialized")
            except Exception as e:
                logger.warning(f"Could not initialize VADER analyzer: {e}")
    
    def analyze(self, content: str) -> SentimentMetrics:
        """
        Analyze sentiment of content using multiple techniques.
        
        Args:
            content: Text content to analyze
            
        Returns:
            SentimentMetrics with comprehensive sentiment analysis
        """
        metrics = SentimentMetrics()
        
        if not content or not content.strip():
            logger.warning("Empty content provided for sentiment analysis")
            return metrics
        
        # Use multiple analysis methods and combine results
        textblob_result = self._analyze_with_textblob(content)
        vader_result = self._analyze_with_vader(content)
        transformer_result = self._analyze_with_transformer(content)
        
        # Combine results (weighted average)
        polarity_scores = []
        subjectivity_scores = []
        confidence_scores = []
        labels = []
        
        if textblob_result:
            polarity_scores.append(textblob_result['polarity'])
            subjectivity_scores.append(textblob_result['subjectivity'])
            confidence_scores.append(abs(textblob_result['polarity']))
            labels.append(textblob_result['label'])
        
        if vader_result:
            polarity_scores.append(vader_result['polarity'])
            confidence_scores.append(vader_result['confidence'])
            labels.append(vader_result['label'])
        
        if transformer_result:
            polarity_scores.append(transformer_result['polarity'])
            confidence_scores.append(transformer_result['confidence'])
            labels.append(transformer_result['label'])
            # Store emotion details
            metrics.emotions = transformer_result.get('emotions', {})
        
        # Calculate combined metrics
        if polarity_scores:
            metrics.polarity = sum(polarity_scores) / len(polarity_scores)
        
        if subjectivity_scores:
            metrics.subjectivity = sum(subjectivity_scores) / len(subjectivity_scores)
        
        if confidence_scores:
            metrics.confidence = sum(confidence_scores) / len(confidence_scores)
        
        # Determine final label based on combined polarity
        metrics.label = self._determine_sentiment_label(metrics.polarity)
        
        logger.info(
            f"Sentiment analysis completed. "
            f"Label: {metrics.label}, "
            f"Polarity: {metrics.polarity:.2f}, "
            f"Confidence: {metrics.confidence:.2f}"
        )
        
        return metrics
    
    def _analyze_with_textblob(self, content: str) -> Optional[Dict]:
        """Analyze sentiment using TextBlob."""
        if not TEXTBLOB_AVAILABLE:
            return None
        
        try:
            from textblob import TextBlob
            
            blob = TextBlob(content)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            label = self._determine_sentiment_label(polarity)
            
            return {
                'polarity': polarity,
                'subjectivity': subjectivity,
                'label': label,
                'confidence': abs(polarity)
            }
            
        except Exception as e:
            logger.warning(f"TextBlob sentiment analysis failed: {e}")
            return None
    
    def _analyze_with_vader(self, content: str) -> Optional[Dict]:
        """Analyze sentiment using NLTK VADER."""
        if not self.vader_analyzer:
            return None
        
        try:
            scores = self.vader_analyzer.polarity_scores(content)
            
            # VADER returns compound score from -1 to 1
            polarity = scores['compound']
            label = self._determine_sentiment_label(polarity)
            
            return {
                'polarity': polarity,
                'label': label,
                'confidence': abs(polarity),
                'positive': scores['pos'],
                'negative': scores['neg'],
                'neutral': scores['neu']
            }
            
        except Exception as e:
            logger.warning(f"VADER sentiment analysis failed: {e}")
            return None
    
    def _analyze_with_transformer(self, content: str) -> Optional[Dict]:
        """Analyze sentiment using transformer model."""
        if not self.transformer_model:
            return None
        
        try:
            # Limit content length for transformer (token limit)
            short_content = content[:512]
            results = self.transformer_model(short_content)
            
            if not results or not results[0]:
                return None
            
            # Get the most confident prediction
            best_result = max(results[0], key=lambda x: x['score'])
            label = best_result['label'].lower()
            confidence = best_result['score']
            
            # Convert label to polarity score
            polarity = self._label_to_polarity(label, confidence)
            
            # Store all emotion scores
            emotions = {}
            for result in results[0]:
                emotion_label = result['label'].lower()
                emotions[emotion_label] = result['score']
            
            return {
                'polarity': polarity,
                'label': label,
                'confidence': confidence,
                'emotions': emotions
            }
            
        except Exception as e:
            logger.warning(f"Transformer sentiment analysis failed: {e}")
            return None
    
    def _determine_sentiment_label(self, polarity: float) -> str:
        """Determine sentiment label from polarity score."""
        if polarity > 0.1:
            return "positive"
        elif polarity < -0.1:
            return "negative"
        else:
            return "neutral"
    
    def _label_to_polarity(self, label: str, confidence: float) -> float:
        """Convert sentiment label to polarity score."""
        label = label.lower()
        
        if 'positive' in label:
            return confidence
        elif 'negative' in label:
            return -confidence
        else:
            return 0.0
    
    def get_sentiment_interpretation(self, metrics: SentimentMetrics) -> str:
        """
        Get human-readable interpretation of sentiment.
        
        Args:
            metrics: SentimentMetrics object
            
        Returns:
            Human-readable sentiment interpretation
        """
        if not metrics:
            return "Unknown sentiment"
        
        label = metrics.label.title()
        confidence = metrics.confidence
        
        if confidence >= 0.8:
            strength = "Very Strong"
        elif confidence >= 0.6:
            strength = "Strong"
        elif confidence >= 0.4:
            strength = "Moderate"
        elif confidence >= 0.2:
            strength = "Weak"
        else:
            strength = "Very Weak"
        
        interpretation = f"{strength} {label}"
        
        # Add subjectivity information
        if metrics.subjectivity >= 0.7:
            interpretation += " (Highly Subjective)"
        elif metrics.subjectivity >= 0.4:
            interpretation += " (Moderately Subjective)"
        else:
            interpretation += " (Mostly Objective)"
        
        return interpretation
    
    def calculate_engagement_score(self, metrics: SentimentMetrics) -> float:
        """
        Calculate engagement score based on sentiment.
        
        Args:
            metrics: SentimentMetrics object
            
        Returns:
            Engagement score from 0-100
        """
        if not metrics:
            return 50.0
        
        # Positive sentiment and moderate subjectivity = more engaging
        sentiment_score = (metrics.polarity + 1) * 50  # Convert -1,1 to 0,100
        
        # Optimal subjectivity for engagement is around 0.5-0.7
        if 0.5 <= metrics.subjectivity <= 0.7:
            subjectivity_score = 100
        elif 0.3 <= metrics.subjectivity <= 0.8:
            subjectivity_score = 80
        elif metrics.subjectivity > 0:
            subjectivity_score = 60
        else:
            subjectivity_score = 40
        
        # Combine scores (60% sentiment, 40% subjectivity)
        engagement_score = (sentiment_score * 0.6) + (subjectivity_score * 0.4)
        
        return min(100, max(0, engagement_score)) 