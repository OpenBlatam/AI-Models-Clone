from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_RETRIES = 100

from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field, validator
from enum import Enum
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
🧠 NLP MODELS - NATURAL LANGUAGE PROCESSING EXTENSIONS
=====================================================

Modelos Pydantic ultra-avanzados para análisis NLP de landing pages:
- Análisis de sentimientos
- Extracción de keywords
- Análisis de legibilidad
- Optimización de contenido
- Scoring de calidad semántica
"""



# =============================================================================
# 🎯 ENUMS NLP
# =============================================================================

class SentimentType(str, Enum):
    """Tipos de sentimiento detectados."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class EmotionType(str, Enum):
    """Tipos de emociones analizadas."""
    JOY = "joy"
    TRUST = "trust"
    FEAR = "fear"
    SURPRISE = "surprise"
    EXCITEMENT = "excitement"
    URGENCY = "urgency"
    CONFIDENCE = "confidence"
    CURIOSITY = "curiosity"


class ReadingLevel(str, Enum):
    """Niveles de lectura."""
    ELEMENTARY = "elementary"
    MIDDLE_SCHOOL = "middle_school"
    HIGH_SCHOOL = "high_school"
    COLLEGE = "college"
    GRADUATE = "graduate"
    PROFESSIONAL = "professional"


class ToneCategory(str, Enum):
    """Categorías de tono detectadas."""
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    URGENT = "urgent"
    LUXURY = "luxury"
    CASUAL = "casual"
    AUTHORITATIVE = "authoritative"
    CONVERSATIONAL = "conversational"
    TECHNICAL = "technical"


# =============================================================================
# 🧠 MODELOS DE ANÁLISIS NLP
# =============================================================================

class EmotionScore(BaseModel):
    """Score de una emoción específica."""
    
    emotion: EmotionType = Field(..., description="Tipo de emoción")
    score: float = Field(..., ge=0.0, le=100.0, description="Score 0-100")
    confidence: float = Field(..., ge=0.0, le=100.0, description="Confianza del análisis")
    detected_words: List[str] = Field(default_factory=list, description="Palabras que dispararon esta emoción")
    impact_on_conversion: float = Field(..., ge=0.0, le=100.0, description="Impacto en conversión")


class SentimentAnalysisModel(BaseModel):
    """Modelo completo de análisis de sentimientos."""
    
    # Sentimiento general
    overall_sentiment: SentimentType = Field(..., description="Sentimiento general")
    confidence_score: float = Field(..., ge=0.0, le=100.0, description="Confianza del análisis")
    polarity_score: float = Field(..., ge=-1.0, le=1.0, description="Polaridad (-1 negativo, +1 positivo)")
    
    # Análisis de emociones detallado
    emotion_scores: List[EmotionScore] = Field(default_factory=list, description="Scores por emoción")
    dominant_emotion: EmotionType = Field(..., description="Emoción dominante")
    
    # Elementos de persuasión
    persuasion_level: float = Field(..., ge=0.0, le=100.0, description="Nivel de persuasión")
    urgency_detected: bool = Field(default=False, description="Urgencia detectada")
    scarcity_detected: bool = Field(default=False, description="Escasez detectada")
    
    # Pain points y beneficios
    pain_points_detected: List[str] = Field(default_factory=list, description="Pain points encontrados")
    benefits_highlighted: List[str] = Field(default_factory=list, description="Beneficios destacados")
    
    # Score de conversión
    conversion_sentiment_score: float = Field(..., ge=0.0, le=100.0, description="Score optimizado para conversión")
    
    @validator('emotion_scores')
    def validate_emotion_scores(cls, v) -> bool:
        """Valida que hay al menos una emoción analizada."""
        if not v:
            return [EmotionScore(
                emotion=EmotionType.TRUST,
                score=50.0,
                confidence=70.0,
                detected_words=[],
                impact_on_conversion=50.0
            )]
        return v


class KeywordItem(BaseModel):
    """Item individual de keyword."""
    
    keyword: str = Field(..., min_length=1, description="Keyword o frase")
    frequency: int = Field(..., ge=1, description="Frecuencia de aparición")
    relevance_score: float = Field(..., ge=0.0, le=100.0, description="Score de relevancia")
    density_percentage: float = Field(..., ge=0.0, le=100.0, description="Densidad porcentual")
    position_weights: Dict[str, float] = Field(default_factory=dict, description="Peso por posición")
    semantic_related: List[str] = Field(default_factory=list, description="Keywords semánticamente relacionadas")
    competition_level: str = Field(default="medium", description="Nivel de competencia SEO")


class KeywordAnalysisModel(BaseModel):
    """Modelo completo de análisis de keywords."""
    
    # Keywords principales
    primary_keywords: List[KeywordItem] = Field(default_factory=list, description="Keywords principales")
    secondary_keywords: List[KeywordItem] = Field(default_factory=list, description="Keywords secundarias")
    long_tail_phrases: List[KeywordItem] = Field(default_factory=list, description="Frases long tail")
    
    # Análisis semántico
    semantic_clusters: Dict[str, List[str]] = Field(default_factory=dict, description="Clusters semánticos")
    topic_coverage: List[str] = Field(default_factory=list, description="Temas cubiertos")
    
    # Métricas generales
    total_unique_keywords: int = Field(default=0, ge=0, description="Total keywords únicas")
    keyword_diversity_score: float = Field(..., ge=0.0, le=100.0, description="Score de diversidad")
    keyword_density_score: float = Field(..., ge=0.0, le=100.0, description="Score de densidad general")
    
    # Distribución por secciones
    keyword_distribution: Dict[str, int] = Field(default_factory=dict, description="Distribución por sección")
    
    # Oportunidades SEO
    seo_keyword_gaps: List[str] = Field(default_factory=list, description="Keywords faltantes importantes")
    competitor_keywords: List[str] = Field(default_factory=list, description="Keywords de competidores")
    opportunity_keywords: List[str] = Field(default_factory=list, description="Oportunidades de keywords")


class ReadabilityMetrics(BaseModel):
    """Métricas detalladas de legibilidad."""
    
    # Scores principales
    flesch_kincaid_score: float = Field(..., ge=0.0, le=100.0, description="Score Flesch-Kincaid")
    gunning_fog_index: float = Field(..., ge=0.0, description="Índice Gunning Fog")
    coleman_liau_index: float = Field(..., ge=0.0, description="Índice Coleman-Liau")
    
    # Nivel de lectura
    reading_level: ReadingLevel = Field(..., description="Nivel de lectura requerido")
    grade_level: float = Field(..., ge=1.0, le=20.0, description="Nivel de grado escolar")
    
    # Métricas de texto
    avg_sentence_length: float = Field(..., ge=0.0, description="Longitud promedio de oraciones")
    avg_word_length: float = Field(..., ge=0.0, description="Longitud promedio de palabras")
    avg_syllables_per_word: float = Field(..., ge=0.0, description="Sílabas promedio por palabra")
    
    # Complejidad
    complex_words_count: int = Field(..., ge=0, description="Número de palabras complejas")
    complex_words_ratio: float = Field(..., ge=0.0, le=1.0, description="Ratio de palabras complejas")
    
    # Estructura
    passive_voice_ratio: float = Field(..., ge=0.0, le=1.0, description="Ratio de voz pasiva")
    sentence_variety_score: float = Field(..., ge=0.0, le=100.0, description="Variedad de oraciones")
    
    # Calificación general
    readability_grade: str = Field(..., description="Calificación (A+, A, B+, etc.)")
    target_audience_match: float = Field(..., ge=0.0, le=100.0, description="Match con audiencia objetivo")


class ReadabilityAnalysisModel(BaseModel):
    """Modelo completo de análisis de legibilidad."""
    
    metrics: ReadabilityMetrics = Field(..., description="Métricas de legibilidad")
    
    # Recomendaciones
    improvement_suggestions: List[str] = Field(default_factory=list, description="Sugerencias de mejora")
    priority_fixes: List[str] = Field(default_factory=list, description="Correcciones prioritarias")
    
    # Análisis específico
    difficult_sentences: List[str] = Field(default_factory=list, description="Oraciones difíciles")
    complex_words: List[str] = Field(default_factory=list, description="Palabras complejas encontradas")
    
    # Optimización para audiencia
    audience_optimization_score: float = Field(..., ge=0.0, le=100.0, description="Optimización para audiencia")
    
    @validator('improvement_suggestions')
    def validate_suggestions(cls, v) -> bool:
        """Asegura que hay al menos una sugerencia."""
        if not v:
            return ["Texto optimizado para la audiencia objetivo"]
        return v


class ToneMetrics(BaseModel):
    """Métricas detalladas de tono."""
    
    # Categoría principal
    primary_tone: ToneCategory = Field(..., description="Tono principal detectado")
    secondary_tones: List[ToneCategory] = Field(default_factory=list, description="Tonos secundarios")
    tone_consistency: float = Field(..., ge=0.0, le=100.0, description="Consistencia del tono")
    
    # Niveles de formalidad y estilo
    formality_level: float = Field(..., ge=0.0, le=100.0, description="Nivel de formalidad")
    professionalism_score: float = Field(..., ge=0.0, le=100.0, description="Score de profesionalismo")
    approachability_score: float = Field(..., ge=0.0, le=100.0, description="Score de accesibilidad")
    
    # Elementos persuasivos
    persuasiveness: float = Field(..., ge=0.0, le=100.0, description="Nivel de persuasión")
    trustworthiness: float = Field(..., ge=0.0, le=100.0, description="Nivel de confiabilidad")
    emotional_appeal: float = Field(..., ge=0.0, le=100.0, description="Apelación emocional")
    
    # Claridad y entendimiento
    clarity_score: float = Field(..., ge=0.0, le=100.0, description="Score de claridad")
    jargon_level: float = Field(..., ge=0.0, le=100.0, description="Nivel de jerga técnica")
    
    # Alineación con marca y audiencia
    brand_voice_alignment: float = Field(..., ge=0.0, le=100.0, description="Alineación con voz de marca")
    target_audience_fit: float = Field(..., ge=0.0, le=100.0, description="Ajuste con audiencia objetivo")


class ToneAnalysisModel(BaseModel):
    """Modelo completo de análisis de tono."""
    
    metrics: ToneMetrics = Field(..., description="Métricas de tono")
    
    # Elementos detectados
    power_words_found: List[str] = Field(default_factory=list, description="Power words encontradas")
    urgency_indicators: List[str] = Field(default_factory=list, description="Indicadores de urgencia")
    trust_signals: List[str] = Field(default_factory=list, description="Señales de confianza")
    
    # Recomendaciones de tono
    tone_adjustments: List[str] = Field(default_factory=list, description="Ajustes de tono sugeridos")
    voice_recommendations: List[str] = Field(default_factory=list, description="Recomendaciones de voz")
    
    # Score general
    overall_tone_score: float = Field(..., ge=0.0, le=100.0, description="Score general de tono")


class ContentOptimizationSuggestion(BaseModel):
    """Sugerencia individual de optimización."""
    
    category: str = Field(..., description="Categoría (SEO, Conversion, Readability, etc.)")
    suggestion: str = Field(..., description="Descripción de la sugerencia")
    impact_level: str = Field(..., description="Nivel de impacto (high, medium, low)")
    implementation_effort: str = Field(..., description="Esfuerzo de implementación")
    expected_improvement: float = Field(..., ge=0.0, le=100.0, description="Mejora esperada %")
    priority_score: int = Field(..., ge=1, le=10, description="Prioridad 1-10")


class ContentOptimizationModel(BaseModel):
    """Modelo completo de optimización de contenido."""
    
    # Optimizaciones por categoría
    seo_optimizations: List[ContentOptimizationSuggestion] = Field(default_factory=list)
    conversion_optimizations: List[ContentOptimizationSuggestion] = Field(default_factory=list)
    readability_optimizations: List[ContentOptimizationSuggestion] = Field(default_factory=list)
    tone_optimizations: List[ContentOptimizationSuggestion] = Field(default_factory=list)
    
    # Análisis de gaps
    content_gaps: List[str] = Field(default_factory=list, description="Gaps de contenido detectados")
    missing_elements: List[str] = Field(default_factory=list, description="Elementos faltantes")
    
    # Priorización
    high_priority_fixes: List[ContentOptimizationSuggestion] = Field(default_factory=list)
    quick_wins: List[ContentOptimizationSuggestion] = Field(default_factory=list)
    
    # Scores de mejora potencial
    potential_seo_improvement: float = Field(..., ge=0.0, le=100.0, description="Mejora SEO potencial")
    potential_conversion_improvement: float = Field(..., ge=0.0, le=100.0, description="Mejora conversión potencial")
    
    # Score general
    optimization_priority_score: float = Field(..., ge=0.0, le=100.0, description="Prioridad general de optimización")


# =============================================================================
# 🎯 MODELO PRINCIPAL NLP INSIGHTS
# =============================================================================

class UltraNLPInsights(BaseModel):
    """Modelo principal que contiene todos los insights NLP."""
    
    # ID y metadatos
    analysis_id: str = Field(..., description="ID único del análisis")
    landing_page_id: Optional[str] = Field(None, description="ID de la landing page analizada")
    
    # Análisis principales
    sentiment_analysis: SentimentAnalysisModel = Field(..., description="Análisis de sentimientos")
    keyword_analysis: KeywordAnalysisModel = Field(..., description="Análisis de keywords")
    readability_analysis: ReadabilityAnalysisModel = Field(..., description="Análisis de legibilidad")
    tone_analysis: ToneAnalysisModel = Field(..., description="Análisis de tono")
    content_optimization: ContentOptimizationModel = Field(..., description="Optimizaciones sugeridas")
    
    # Scores generales NLP
    overall_nlp_score: float = Field(..., ge=0.0, le=100.0, description="Score NLP general")
    content_quality_score: float = Field(..., ge=0.0, le=100.0, description="Score de calidad del contenido")
    semantic_coherence_score: float = Field(..., ge=0.0, le=100.0, description="Score de coherencia semántica")
    
    # Metadatos del análisis
    processing_time_ms: float = Field(..., ge=0.0, description="Tiempo de procesamiento en ms")
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp del análisis")
    nlp_model_version: str = Field(default="1.0.0", description="Versión del modelo NLP")
    
    # Configuración utilizada
    target_audience: Optional[str] = Field(None, description="Audiencia objetivo configurada")
    industry_context: Optional[str] = Field(None, description="Contexto de industria")
    conversion_goal: Optional[str] = Field(None, description="Objetivo de conversión")
    
    def get_top_recommendations(self, limit: int = 5) -> List[ContentOptimizationSuggestion]:
        """Obtiene las top recomendaciones priorizadas."""
        all_suggestions = (
            self.content_optimization.seo_optimizations +
            self.content_optimization.conversion_optimizations +
            self.content_optimization.readability_optimizations +
            self.content_optimization.tone_optimizations
        )
        
        # Ordenar por prioridad y tomar los top
        sorted_suggestions = sorted(all_suggestions, key=lambda x: x.priority_score, reverse=True)
        return sorted_suggestions[:limit]
    
    def get_nlp_summary(self) -> Dict[str, Any]:
        """Obtiene un resumen ejecutivo del análisis NLP."""
        return {
            "overall_score": self.overall_nlp_score,
            "dominant_sentiment": self.sentiment_analysis.overall_sentiment,
            "dominant_emotion": self.sentiment_analysis.dominant_emotion,
            "reading_level": self.readability_analysis.metrics.reading_level,
            "primary_tone": self.tone_analysis.metrics.primary_tone,
            "total_keywords": self.keyword_analysis.total_unique_keywords,
            "optimization_opportunities": len(self.get_top_recommendations()),
            "processing_time": f"{self.processing_time_ms:.1f}ms"
        }


# =============================================================================
# 📊 MODELOS DE REQUEST/RESPONSE PARA API
# =============================================================================

class NLPAnalysisRequest(BaseModel):
    """Request para análisis NLP de contenido."""
    
    # Contenido a analizar
    content: Dict[str, str] = Field(..., description="Contenido por secciones")
    
    # Configuración del análisis
    target_audience: Optional[str] = Field(None, description="Audiencia objetivo")
    industry_context: Optional[str] = Field(None, description="Contexto de industria")
    conversion_goal: Optional[str] = Field(None, description="Objetivo de conversión")
    
    # Opciones de análisis
    include_sentiment: bool = Field(default=True, description="Incluir análisis de sentimientos")
    include_keywords: bool = Field(default=True, description="Incluir análisis de keywords")
    include_readability: bool = Field(default=True, description="Incluir análisis de legibilidad")
    include_tone: bool = Field(default=True, description="Incluir análisis de tono")
    include_optimization: bool = Field(default=True, description="Incluir sugerencias de optimización")
    
    # Configuración avanzada
    keyword_extraction_depth: str = Field(default="standard", description="Profundidad extracción keywords")
    sentiment_sensitivity: str = Field(default="balanced", description="Sensibilidad análisis sentimientos")


class NLPAnalysisResponse(BaseModel):
    """Response del análisis NLP."""
    
    # Resultados principales
    insights: UltraNLPInsights = Field(..., description="Insights completos del análisis")
    
    # Resumen ejecutivo
    summary: Dict[str, Any] = Field(..., description="Resumen ejecutivo")
    
    # Top recomendaciones
    top_recommendations: List[ContentOptimizationSuggestion] = Field(..., description="Top recomendaciones")
    
    # Metadatos de la respuesta
    success: bool = Field(default=True, description="Éxito del análisis")
    message: str = Field(default="Analysis completed successfully", description="Mensaje de estado")


if __name__ == "__main__":
    print("🧠 NLP Models Loaded Successfully")
    print("✅ Sentiment Analysis Models")
    print("✅ Keyword Extraction Models")
    print("✅ Readability Analysis Models")
    print("✅ Tone Analysis Models")
    print("✅ Content Optimization Models")
    print("🚀 Ready for ultra-advanced NLP analysis!") 