"""
Sistema de Análisis de Sentimientos y Emociones en Tiempo Real v4.6
HeyGen AI - Sistema de Monitoreo Inteligente con IA Avanzada

Este sistema proporciona capacidades avanzadas de análisis emocional incluyendo:
- Análisis de sentimientos en tiempo real
- Detección de emociones múltiples
- Procesamiento de texto, audio y video
- Generación de insights inteligentes
- Análisis de tendencias emocionales
- Predicción de comportamientos
"""

import asyncio
import time
import json
import logging
import random
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmotionType(Enum):
    """Tipos de emociones detectables"""
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    NEUTRAL = "neutral"
    EXCITEMENT = "excitement"
    CONTEMPT = "contempt"
    LOVE = "love"

class SentimentPolarity(Enum):
    """Polaridad del sentimiento"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"

class ContentType(Enum):
    """Tipos de contenido analizable"""
    TEXT = "text"
    AUDIO = "audio"
    VIDEO = "video"
    MULTIMODAL = "multimodal"

@dataclass
class EmotionScore:
    """Puntuación de emoción"""
    emotion: EmotionType
    confidence: float
    intensity: float
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        self.confidence = max(0.0, min(1.0, self.confidence))
        self.intensity = max(0.0, min(1.0, self.intensity))

@dataclass
class SentimentAnalysis:
    """Análisis de sentimiento"""
    polarity: SentimentPolarity
    confidence: float
    score: float  # -1.0 to 1.0
    emotions: List[EmotionScore]
    timestamp: datetime = field(default_factory=datetime.now)
    context: Optional[str] = None

@dataclass
class ContentSample:
    """Muestra de contenido para análisis"""
    id: str
    content: str
    content_type: ContentType
    metadata: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    user_id: Optional[str] = None
    
    def __post_init__(self):
        if not self.id:
            self.id = hashlib.md5(f"{self.content}{time.time()}".encode()).hexdigest()[:8]

@dataclass
class AnalysisResult:
    """Resultado del análisis"""
    sample_id: str
    sentiment: SentimentAnalysis
    processing_time: float
    confidence_score: float
    insights: List[str]
    recommendations: List[str]
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool = True
    error_message: Optional[str] = None

@dataclass
class EmotionalTrend:
    """Tendencia emocional"""
    emotion: EmotionType
    trend_direction: str  # "increasing", "decreasing", "stable"
    change_rate: float
    confidence: float
    time_period: str
    timestamp: datetime = field(default_factory=datetime.now)

class TextEmotionAnalyzer:
    """Analizador de emociones en texto"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.emotion_keywords = {
            EmotionType.JOY: ['feliz', 'alegre', 'contento', 'emocionado', 'dichoso', 'radiante'],
            EmotionType.SADNESS: ['triste', 'deprimido', 'melancólico', 'desanimado', 'abatido'],
            EmotionType.ANGER: ['enojado', 'furioso', 'irritado', 'molesto', 'indignado'],
            EmotionType.FEAR: ['asustado', 'aterrado', 'nervioso', 'ansioso', 'preocupado'],
            EmotionType.SURPRISE: ['sorprendido', 'asombrado', 'impresionado', 'increíble'],
            EmotionType.DISGUST: ['asqueado', 'repugnado', 'disgustado', 'nauseabundo'],
            EmotionType.EXCITEMENT: ['emocionado', 'entusiasmado', 'eufórico', 'estimulado'],
            EmotionType.LOVE: ['amoroso', 'cariñoso', 'tierno', 'afectuoso', 'romántico']
        }
        self.sentiment_patterns = {
            'positive': ['excelente', 'maravilloso', 'fantástico', 'genial', 'perfecto'],
            'negative': ['terrible', 'horrible', 'pésimo', 'deplorable', 'inaceptable']
        }
        
    async def analyze_text_emotions(self, text: str) -> List[EmotionScore]:
        """Analizar emociones en texto"""
        try:
            emotions = []
            text_lower = text.lower()
            
            # Analyze each emotion type
            for emotion_type, keywords in self.emotion_keywords.items():
                matches = sum(1 for keyword in keywords if keyword in text_lower)
                if matches > 0:
                    confidence = min(0.9, 0.3 + (matches * 0.2))
                    intensity = min(1.0, 0.4 + (matches * 0.3))
                    
                    emotions.append(EmotionScore(
                        emotion=emotion_type,
                        confidence=confidence,
                        intensity=intensity
                    ))
            
            # If no specific emotions detected, assign neutral
            if not emotions:
                emotions.append(EmotionScore(
                    emotion=EmotionType.NEUTRAL,
                    confidence=0.8,
                    intensity=0.5
                ))
            
            # Sort by confidence and intensity
            emotions.sort(key=lambda x: (x.confidence, x.intensity), reverse=True)
            return emotions[:3]  # Return top 3 emotions
            
        except Exception as e:
            logger.error(f"Error analyzing text emotions: {e}")
            return [EmotionScore(EmotionType.NEUTRAL, 0.5, 0.5)]

class AudioEmotionAnalyzer:
    """Analizador de emociones en audio"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.audio_features = {
            'pitch': 'Análisis de tono vocal',
            'tempo': 'Velocidad del habla',
            'volume': 'Intensidad del volumen',
            'clarity': 'Claridad de pronunciación'
        }
        
    async def analyze_audio_emotions(self, audio_data: str) -> List[EmotionScore]:
        """Analizar emociones en audio"""
        try:
            # Simulate audio analysis
            await asyncio.sleep(0.5)  # Simulate processing time
            
            # Simulate emotion detection based on audio characteristics
            emotions = []
            
            # Random emotion detection (in real implementation, this would use audio ML models)
            emotion_types = list(EmotionType)[:8]  # Exclude NEUTRAL
            num_emotions = random.randint(1, 3)
            
            for _ in range(num_emotions):
                emotion_type = random.choice(emotion_types)
                confidence = random.uniform(0.6, 0.95)
                intensity = random.uniform(0.4, 0.9)
                
                emotions.append(EmotionScore(
                    emotion=emotion_type,
                    confidence=confidence,
                    intensity=intensity
                ))
            
            # Sort by confidence
            emotions.sort(key=lambda x: x.confidence, reverse=True)
            return emotions
            
        except Exception as e:
            logger.error(f"Error analyzing audio emotions: {e}")
            return [EmotionScore(EmotionType.NEUTRAL, 0.5, 0.5)]

class VideoEmotionAnalyzer:
    """Analizador de emociones en video"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.video_features = {
            'facial_expressions': 'Expresiones faciales',
            'body_language': 'Lenguaje corporal',
            'movement_patterns': 'Patrones de movimiento',
            'visual_context': 'Contexto visual'
        }
        
    async def analyze_video_emotions(self, video_data: str) -> List[EmotionScore]:
        """Analizar emociones en video"""
        try:
            # Simulate video analysis
            await asyncio.sleep(0.8)  # Simulate processing time
            
            # Simulate emotion detection from video
            emotions = []
            
            # Random emotion detection (in real implementation, this would use computer vision ML models)
            emotion_types = list(EmotionType)[:8]  # Exclude NEUTRAL
            num_emotions = random.randint(1, 4)
            
            for _ in range(num_emotions):
                emotion_type = random.choice(emotion_types)
                confidence = random.uniform(0.7, 0.98)
                intensity = random.uniform(0.5, 0.95)
                
                emotions.append(EmotionScore(
                    emotion=emotion_type,
                    confidence=confidence,
                    intensity=intensity
                ))
            
            # Sort by confidence
            emotions.sort(key=lambda x: x.confidence, reverse=True)
            return emotions
            
        except Exception as e:
            logger.error(f"Error analyzing video emotions: {e}")
            return [EmotionScore(EmotionType.NEUTRAL, 0.5, 0.5)]

class SentimentAnalyzer:
    """Analizador de sentimientos"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.sentiment_models = {
            'rule_based': 'Análisis basado en reglas',
            'ml_based': 'Modelo de machine learning',
            'hybrid': 'Enfoque híbrido'
        }
        
    async def analyze_sentiment(self, text: str, emotions: List[EmotionScore]) -> SentimentAnalysis:
        """Analizar sentimiento basado en texto y emociones"""
        try:
            # Calculate sentiment score based on emotions
            positive_emotions = [e for e in emotions if e.emotion in [EmotionType.JOY, EmotionType.LOVE, EmotionType.EXCITEMENT]]
            negative_emotions = [e for e in emotions if e.emotion in [EmotionType.SADNESS, EmotionType.ANGER, EmotionType.FEAR, EmotionType.DISGUST]]
            
            positive_score = sum(e.intensity * e.confidence for e in positive_emotions)
            negative_score = sum(e.intensity * e.confidence for e in negative_emotions)
            
            # Calculate overall sentiment score
            if positive_score > negative_score:
                polarity = SentimentPolarity.POSITIVE
                score = min(1.0, positive_score / max(positive_score + negative_score, 1))
            elif negative_score > positive_score:
                polarity = SentimentPolarity.NEGATIVE
                score = max(-1.0, -negative_score / max(positive_score + negative_score, 1))
            else:
                polarity = SentimentPolarity.NEUTRAL
                score = 0.0
            
            # Calculate confidence
            total_confidence = sum(e.confidence for e in emotions)
            avg_confidence = total_confidence / len(emotions) if emotions else 0.5
            
            return SentimentAnalysis(
                polarity=polarity,
                confidence=avg_confidence,
                score=score,
                emotions=emotions,
                context=f"Análisis basado en {len(emotions)} emociones detectadas"
            )
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return SentimentAnalysis(
                polarity=SentimentPolarity.NEUTRAL,
                confidence=0.5,
                score=0.0,
                emotions=emotions,
                context="Error en análisis de sentimiento"
            )

class InsightGenerator:
    """Generador de insights inteligentes"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.insight_patterns = {
            'emotional_state': 'Estado emocional del usuario',
            'sentiment_trend': 'Tendencia del sentimiento',
            'communication_style': 'Estilo de comunicación',
            'emotional_triggers': 'Disparadores emocionales'
        }
        
    async def generate_insights(self, sentiment: SentimentAnalysis, 
                              content_type: ContentType) -> List[str]:
        """Generar insights basados en el análisis"""
        try:
            insights = []
            
            # Analyze emotional state
            if sentiment.emotions:
                top_emotion = sentiment.emotions[0]
                insights.append(f"Emoción dominante: {top_emotion.emotion.value} con {top_emotion.confidence:.1%} de confianza")
                
                if top_emotion.intensity > 0.8:
                    insights.append("Intensidad emocional alta detectada")
                elif top_emotion.intensity < 0.3:
                    insights.append("Intensidad emocional baja detectada")
            
            # Analyze sentiment polarity
            if sentiment.polarity == SentimentPolarity.POSITIVE:
                insights.append("Sentimiento general positivo detectado")
            elif sentiment.polarity == SentimentPolarity.NEGATIVE:
                insights.append("Sentimiento general negativo detectado")
            else:
                insights.append("Sentimiento neutral o mixto detectado")
            
            # Content type specific insights
            if content_type == ContentType.TEXT:
                insights.append("Análisis basado en contenido textual")
            elif content_type == ContentType.AUDIO:
                insights.append("Análisis incluye características vocales")
            elif content_type == ContentType.VIDEO:
                insights.append("Análisis incluye expresiones faciales y lenguaje corporal")
            
            # Confidence insights
            if sentiment.confidence > 0.8:
                insights.append("Alta confianza en el análisis realizado")
            elif sentiment.confidence < 0.6:
                insights.append("Confianza moderada, considerar análisis adicional")
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return ["Error generando insights"]

class RecommendationEngine:
    """Motor de recomendaciones"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.recommendation_templates = {
            'positive_sentiment': [
                "Mantener el enfoque positivo actual",
                "Compartir experiencias positivas",
                "Fomentar el estado emocional actual"
            ],
            'negative_sentiment': [
                "Considerar apoyo emocional",
                "Identificar causas del sentimiento negativo",
                "Implementar estrategias de bienestar"
            ],
            'mixed_emotions': [
                "Analizar conflicto emocional",
                "Identificar factores contradictorios",
                "Buscar balance emocional"
            ]
        }
        
    async def generate_recommendations(self, sentiment: SentimentAnalysis) -> List[str]:
        """Generar recomendaciones basadas en el análisis"""
        try:
            recommendations = []
            
            # Base recommendations on sentiment polarity
            if sentiment.polarity == SentimentPolarity.POSITIVE:
                recommendations.extend(self.recommendation_templates['positive_sentiment'])
            elif sentiment.polarity == SentimentPolarity.NEGATIVE:
                recommendations.extend(self.recommendation_templates['negative_sentiment'])
            else:
                recommendations.extend(self.recommendation_templates['mixed_emotions'])
            
            # Emotion-specific recommendations
            if sentiment.emotions:
                top_emotion = sentiment.emotions[0]
                
                if top_emotion.emotion == EmotionType.ANGER:
                    recommendations.append("Implementar técnicas de manejo de ira")
                elif top_emotion.emotion == EmotionType.FEAR:
                    recommendations.append("Identificar y abordar fuentes de ansiedad")
                elif top_emotion.emotion == EmotionType.SADNESS:
                    recommendations.append("Buscar apoyo social y actividades positivas")
                elif top_emotion.emotion == EmotionType.JOY:
                    recommendations.append("Aprovechar el momento positivo para productividad")
            
            # Confidence-based recommendations
            if sentiment.confidence < 0.7:
                recommendations.append("Recopilar más datos para análisis más preciso")
            
            return recommendations[:5]  # Limit to top 5 recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return ["Error generando recomendaciones"]

class TrendAnalyzer:
    """Analizador de tendencias emocionales"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.emotion_history = []
        self.trend_periods = ['hourly', 'daily', 'weekly', 'monthly']
        
    async def analyze_emotional_trends(self, time_period: str = 'daily') -> List[EmotionalTrend]:
        """Analizar tendencias emocionales en el tiempo"""
        try:
            trends = []
            
            # Simulate trend analysis
            await asyncio.sleep(0.3)
            
            # Generate trends for each emotion type
            for emotion_type in list(EmotionType)[:8]:  # Exclude NEUTRAL
                trend_direction = random.choice(['increasing', 'decreasing', 'stable'])
                change_rate = random.uniform(0.05, 0.25)
                confidence = random.uniform(0.6, 0.9)
                
                trends.append(EmotionalTrend(
                    emotion=emotion_type,
                    trend_direction=trend_direction,
                    change_rate=change_rate,
                    confidence=confidence,
                    time_period=time_period
                ))
            
            # Sort by confidence
            trends.sort(key=lambda x: x.confidence, reverse=True)
            return trends[:5]  # Return top 5 trends
            
        except Exception as e:
            logger.error(f"Error analyzing emotional trends: {e}")
            return []

class RealTimeSentimentEmotionAnalysisSystem:
    """Sistema principal de análisis de sentimientos y emociones en tiempo real v4.6"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.is_running = False
        
        # Initialize analyzers
        self.text_analyzer = TextEmotionAnalyzer(config)
        self.audio_analyzer = AudioEmotionAnalyzer(config)
        self.video_analyzer = VideoEmotionAnalyzer(config)
        self.sentiment_analyzer = SentimentAnalyzer(config)
        self.insight_generator = InsightGenerator(config)
        self.recommendation_engine = RecommendationEngine(config)
        self.trend_analyzer = TrendAnalyzer(config)
        
        # System state
        self.analysis_queue = []
        self.completed_analyses = []
        self.performance_metrics = {
            'total_analyses': 0,
            'successful_analyses': 0,
            'average_processing_time': 0.0,
            'average_confidence': 0.0
        }
        
        logger.info("🚀 Sistema de Análisis de Sentimientos y Emociones v4.6 inicializado")
    
    async def start(self):
        """Iniciar el sistema"""
        if self.is_running:
            logger.warning("⚠️ Sistema ya está ejecutándose")
            return
        
        self.is_running = True
        logger.info("🚀 Sistema de Análisis de Sentimientos y Emociones v4.6 iniciado")
        
        # Start background tasks
        asyncio.create_task(self._process_analysis_queue())
        asyncio.create_task(self._update_performance_metrics())
    
    async def stop(self):
        """Detener el sistema"""
        self.is_running = False
        logger.info("🛑 Sistema de Análisis de Sentimientos y Emociones v4.6 detenido")
    
    async def analyze_content(self, sample: ContentSample) -> AnalysisResult:
        """Analizar contenido para sentimientos y emociones"""
        start_time = time.time()
        
        try:
            # Analyze emotions based on content type
            if sample.content_type == ContentType.TEXT:
                emotions = await self.text_analyzer.analyze_text_emotions(sample.content)
            elif sample.content_type == ContentType.AUDIO:
                emotions = await self.audio_analyzer.analyze_audio_emotions(sample.content)
            elif sample.content_type == ContentType.VIDEO:
                emotions = await self.video_analyzer.analyze_video_emotions(sample.content)
            else:
                # Multimodal analysis
                emotions = await self._analyze_multimodal_content(sample.content)
            
            # Analyze sentiment
            sentiment = await self.sentiment_analyzer.analyze_sentiment(sample.content, emotions)
            
            # Generate insights and recommendations
            insights = await self.insight_generator.generate_insights(sentiment, sample.content_type)
            recommendations = await self.recommendation_engine.generate_recommendations(sentiment)
            
            processing_time = time.time() - start_time
            confidence_score = sentiment.confidence
            
            result = AnalysisResult(
                sample_id=sample.id,
                sentiment=sentiment,
                processing_time=processing_time,
                confidence_score=confidence_score,
                insights=insights,
                recommendations=recommendations
            )
            
            self.completed_analyses.append(result)
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing content: {e}")
            return AnalysisResult(
                sample_id=sample.id,
                sentiment=SentimentAnalysis(
                    polarity=SentimentPolarity.NEUTRAL,
                    confidence=0.0,
                    score=0.0,
                    emotions=[],
                    context="Error en análisis"
                ),
                processing_time=time.time() - start_time,
                confidence_score=0.0,
                insights=["Error en análisis"],
                recommendations=["Reintentar análisis"],
                success=False,
                error_message=str(e)
            )
    
    async def _analyze_multimodal_content(self, content: str) -> List[EmotionScore]:
        """Analizar contenido multimodal"""
        try:
            # Simulate multimodal analysis
            await asyncio.sleep(0.6)
            
            # Combine analysis from different modalities
            emotions = []
            emotion_types = list(EmotionType)[:8]
            
            for _ in range(random.randint(2, 4)):
                emotion_type = random.choice(emotion_types)
                confidence = random.uniform(0.7, 0.95)
                intensity = random.uniform(0.5, 0.9)
                
                emotions.append(EmotionScore(
                    emotion=emotion_type,
                    confidence=confidence,
                    intensity=intensity
                ))
            
            # Remove duplicates and sort
            unique_emotions = {}
            for emotion in emotions:
                if emotion.emotion not in unique_emotions:
                    unique_emotions[emotion.emotion] = emotion
                else:
                    # Keep the one with higher confidence
                    if emotion.confidence > unique_emotions[emotion.emotion].confidence:
                        unique_emotions[emotion.emotion] = emotion
            
            emotions = list(unique_emotions.values())
            emotions.sort(key=lambda x: x.confidence, reverse=True)
            return emotions[:3]
            
        except Exception as e:
            logger.error(f"Error in multimodal analysis: {e}")
            return [EmotionScore(EmotionType.NEUTRAL, 0.5, 0.5)]
    
    async def analyze_emotional_trends(self, time_period: str = 'daily') -> List[EmotionalTrend]:
        """Analizar tendencias emocionales"""
        return await self.trend_analyzer.analyze_emotional_trends(time_period)
    
    async def _process_analysis_queue(self):
        """Procesar cola de análisis en background"""
        while self.is_running:
            if self.analysis_queue:
                # Process analysis requests
                await asyncio.sleep(1)
            
            await asyncio.sleep(1)
    
    async def _update_performance_metrics(self):
        """Actualizar métricas de rendimiento"""
        while self.is_running:
            if self.completed_analyses:
                total_time = sum(a.processing_time for a in self.completed_analyses)
                total_confidence = sum(a.confidence_score for a in self.completed_analyses)
                
                self.performance_metrics.update({
                    'total_analyses': len(self.completed_analyses),
                    'successful_analyses': len([a for a in self.completed_analyses if a.success]),
                    'average_processing_time': total_time / len(self.completed_analyses),
                    'average_confidence': total_confidence / len(self.completed_analyses)
                })
            
            await asyncio.sleep(30)  # Update every 30 seconds
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado del sistema"""
        return {
            'system_name': 'Sistema de Análisis de Sentimientos y Emociones v4.6',
            'status': 'running' if self.is_running else 'stopped',
            'performance_metrics': self.performance_metrics,
            'queue_size': len(self.analysis_queue),
            'completed_analyses': len(self.completed_analyses),
            'timestamp': datetime.now().isoformat()
        }
    
    async def get_analysis_history(self, limit: int = 100) -> List[AnalysisResult]:
        """Obtener historial de análisis"""
        return self.completed_analyses[-limit:] if self.completed_analyses else []

# Example usage and testing
async def main():
    """Función principal de ejemplo"""
    config = {
        'max_concurrent_analyses': 10,
        'analysis_timeout': 60,
        'confidence_threshold': 0.6
    }
    
    system = RealTimeSentimentEmotionAnalysisSystem(config)
    await system.start()
    
    # Example content samples
    samples = [
        ContentSample(
            id="",
            content="¡Estoy muy feliz hoy! Ha sido un día maravilloso lleno de alegría y emoción.",
            content_type=ContentType.TEXT,
            metadata={'language': 'spanish', 'length': 85}
        ),
        ContentSample(
            id="",
            content="audio_sample_001.wav",
            content_type=ContentType.AUDIO,
            metadata={'duration': 30, 'format': 'wav', 'sample_rate': 44100}
        ),
        ContentSample(
            id="",
            content="video_sample_001.mp4",
            content_type=ContentType.VIDEO,
            metadata={'duration': 45, 'resolution': '1920x1080', 'fps': 30}
        )
    ]
    
    # Analyze each sample
    results = []
    for sample in samples:
        result = await system.analyze_content(sample)
        results.append(result)
    
    # Display results
    for i, result in enumerate(results):
        print(f"\n🎯 Análisis {i+1} - {samples[i].content_type.value.upper()}:")
        print(f"ID: {result.sample_id}")
        print(f"Sentimiento: {result.sentiment.polarity.value}")
        print(f"Confianza: {result.confidence_score:.2f}")
        print(f"Tiempo: {result.processing_time:.2f}s")
        print(f"Emociones: {[e.emotion.value for e in result.sentiment.emotions[:3]]}")
        print(f"Insights: {result.insights[:2]}")
        print(f"Recomendaciones: {result.recommendations[:2]}")
    
    # Analyze emotional trends
    trends = await system.analyze_emotional_trends('daily')
    print(f"\n📈 Tendencias Emocionales Diarias:")
    for trend in trends[:3]:
        print(f"- {trend.emotion.value}: {trend.trend_direction} ({trend.change_rate:.1%})")
    
    # Get system status
    status = await system.get_system_status()
    print(f"\n📊 Estado del Sistema: {json.dumps(status, indent=2, default=str)}")
    
    await system.stop()

if __name__ == "__main__":
    asyncio.run(main())
