from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS = 1000

# Constants
MAX_RETRIES = 100

# Constants
TIMEOUT_SECONDS = 60

import asyncio
import re
import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
from collections import Counter
from typing import Any, List, Dict, Optional
import logging
"""
🧠 ULTRA NLP SERVICE - ADVANCED NATURAL LANGUAGE PROCESSING
==========================================================

Motor NLP ultra-avanzado para landing pages con:
- Análisis de sentimientos avanzado
- Extracción automática de keywords
- Análisis de legibilidad y tono
- Optimización de contenido con IA
- Scoring de calidad semántica
- Recomendaciones automáticas
"""



# =============================================================================
# 🎯 MODELOS NLP
# =============================================================================

@dataclass
class SentimentAnalysis:
    """Análisis de sentimientos ultra-detallado."""
    
    overall_sentiment: str  # positive, negative, neutral
    confidence_score: float  # 0-100
    emotion_scores: Dict[str, float]  # joy, trust, fear, surprise, etc.
    persuasion_level: float  # 0-100
    urgency_detected: bool
    pain_points_detected: List[str]
    benefits_highlighted: List[str]
    conversion_sentiment: float  # 0-100 (optimized for conversion)


@dataclass 
class ReadabilityAnalysis:
    """Análisis de legibilidad avanzado."""
    
    flesch_kincaid_score: float  # 0-100
    reading_level: str  # elementary, middle_school, high_school, college
    avg_sentence_length: float
    avg_word_length: float
    complex_words_ratio: float
    passive_voice_ratio: float
    readability_grade: str  # A+, A, B+, B, C+, C, D, F
    recommendations: List[str]


@dataclass
class KeywordAnalysis:
    """Análisis y extracción de keywords."""
    
    primary_keywords: List[Dict[str, Any]]  # keyword, relevance, density
    secondary_keywords: List[Dict[str, Any]]
    long_tail_phrases: List[Dict[str, Any]]
    semantic_keywords: List[str]  # semantically related
    keyword_density_score: float  # 0-100
    keyword_distribution: Dict[str, int]  # section distribution
    seo_keyword_gaps: List[str]  # missing important keywords
    competitor_keywords: List[str]  # potential competitor keywords


@dataclass
class ToneAnalysis:
    """Análisis de tono y estilo."""
    
    tone_category: str  # professional, friendly, urgent, luxury, etc.
    formality_level: float  # 0-100 (informal to very formal)
    persuasiveness: float  # 0-100
    trustworthiness: float  # 0-100
    emotional_appeal: float  # 0-100
    clarity_score: float  # 0-100
    brand_voice_alignment: float  # 0-100
    target_audience_fit: float  # 0-100


@dataclass
class ContentOptimization:
    """Optimizaciones sugeridas por NLP."""
    
    headline_improvements: List[str]
    content_enhancements: List[str]
    cta_optimizations: List[str]
    seo_improvements: List[str]
    conversion_boosters: List[str]
    readability_fixes: List[str]
    tone_adjustments: List[str]
    priority_score: float  # 0-100 (how important these optimizations are)


@dataclass
class NLPInsights:
    """Insights completos del análisis NLP."""
    
    sentiment: SentimentAnalysis
    readability: ReadabilityAnalysis
    keywords: KeywordAnalysis
    tone: ToneAnalysis
    optimization: ContentOptimization
    overall_nlp_score: float  # 0-100
    processing_time_ms: float
    analysis_timestamp: datetime


# =============================================================================
# 🧠 MOTOR NLP ULTRA-AVANZADO
# =============================================================================

class UltraNLPEngine:
    """Motor NLP ultra-avanzado para landing pages."""
    
    def __init__(self) -> Any:
        self.analysis_count = 0
        self.total_processing_time = 0.0
        
        # Diccionarios de emociones y sentimientos
        self.emotion_words = {
            "joy": ["amazing", "incredible", "fantastic", "excellent", "outstanding", "superb"],
            "trust": ["proven", "reliable", "trusted", "guaranteed", "certified", "verified"], 
            "excitement": ["revolutionary", "breakthrough", "game-changing", "cutting-edge"],
            "urgency": ["now", "today", "immediately", "limited", "expires", "hurry"],
            "fear": ["problem", "struggle", "difficult", "challenging", "pain", "frustrating"],
            "surprise": ["unexpected", "shocking", "reveal", "secret", "hidden", "discover"]
        }
        
        # Palabras de poder para conversión
        self.power_words = {
            "action": ["get", "start", "try", "claim", "download", "access", "unlock"],
            "benefit": ["save", "earn", "gain", "achieve", "boost", "increase", "improve"],
            "urgency": ["now", "today", "instantly", "immediately", "fast", "quick"],
            "exclusivity": ["exclusive", "limited", "premium", "select", "vip", "elite"],
            "safety": ["guaranteed", "risk-free", "secure", "protected", "safe", "certified"]
        }
        
        # Patrones de pain points
        self.pain_point_patterns = [
            r"struggling with", r"tired of", r"frustrated by", r"problem with",
            r"difficult to", r"hard to", r"waste time", r"waste money",
            r"inefficient", r"slow", r"manual", r"outdated"
        ]
        
        # Patrones de beneficios
        self.benefit_patterns = [
            r"save \d+", r"increase \d+", r"boost \d+", r"improve \d+",
            r"\d+% more", r"\d+% faster", r"\d+% better", r"\d+x growth"
        ]
    
    async def analyze_complete_content(
        self,
        content: Dict[str, str],
        target_audience: str = "",
        industry: str = "",
        conversion_goal: str = ""
    ) -> NLPInsights:
        """Análisis NLP completo del contenido de landing page."""
        
        start_time = datetime.utcnow()
        self.analysis_count += 1
        
        print(f"🧠 Starting Ultra NLP Analysis #{self.analysis_count}")
        print(f"🎯 Target: {target_audience}")
        print(f"🏢 Industry: {industry}")
        print(f"💰 Goal: {conversion_goal}")
        
        # Combinar todo el contenido para análisis
        full_text = self._combine_content(content)
        
        # Ejecutar análisis en paralelo para velocidad máxima
        tasks = [
            self._analyze_sentiment(full_text, content),
            self._analyze_readability(full_text),
            self._analyze_keywords(full_text, industry),
            self._analyze_tone(full_text, target_audience),
            self._generate_optimizations(content, target_audience, conversion_goal)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Ensamblar resultados
        sentiment_analysis = results[0]
        readability_analysis = results[1] 
        keyword_analysis = results[2]
        tone_analysis = results[3]
        optimization_analysis = results[4]
        
        # Calcular score NLP general
        overall_score = self._calculate_overall_nlp_score(
            sentiment_analysis, readability_analysis, keyword_analysis, tone_analysis
        )
        
        # Calcular tiempo de procesamiento
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        self.total_processing_time += processing_time
        
        # Crear insights completos
        insights = NLPInsights(
            sentiment=sentiment_analysis,
            readability=readability_analysis,
            keywords=keyword_analysis,
            tone=tone_analysis,
            optimization=optimization_analysis,
            overall_nlp_score=overall_score,
            processing_time_ms=processing_time,
            analysis_timestamp=start_time
        )
        
        # Mostrar resultados
        print(f"✅ NLP Analysis completed in {processing_time:.1f}ms")
        print(f"📊 Overall NLP Score: {overall_score:.1f}/100")
        print(f"😊 Sentiment: {sentiment_analysis.overall_sentiment} ({sentiment_analysis.confidence_score:.1f}%)")
        print(f"📖 Readability: {readability_analysis.reading_level} ({readability_analysis.flesch_kincaid_score:.1f})")
        print(f"🔑 Keywords: {len(keyword_analysis.primary_keywords)} primary found")
        print(f"🎭 Tone: {tone_analysis.tone_category} (Trust: {tone_analysis.trustworthiness:.1f}%)")
        
        return insights
    
    async def _analyze_sentiment(self, text: str, content: Dict[str, str]) -> SentimentAnalysis:
        """Análisis de sentimientos ultra-avanzado."""
        
        # Simular análisis avanzado
        await asyncio.sleep(0.1)
        
        # Calcular scores de emociones
        emotion_scores = {}
        for emotion, words in self.emotion_words.items():
            score = sum(1 for word in words if word.lower() in text.lower())
            emotion_scores[emotion] = min(score * 20, 100)  # Normalizar a 0-100
        
        # Detectar sentimiento general
        positive_emotions = emotion_scores.get("joy", 0) + emotion_scores.get("trust", 0) + emotion_scores.get("excitement", 0)
        negative_emotions = emotion_scores.get("fear", 0)
        
        if positive_emotions > negative_emotions * 1.5:
            overall_sentiment = "positive"
            confidence = min(85 + positive_emotions / 10, 95)
        elif negative_emotions > positive_emotions:
            overall_sentiment = "negative" 
            confidence = min(75 + negative_emotions / 10, 90)
        else:
            overall_sentiment = "neutral"
            confidence = 70
        
        # Detectar urgencia
        urgency_detected = any(word in text.lower() for word in self.emotion_words["urgency"])
        
        # Detectar pain points
        pain_points = []
        for pattern in self.pain_point_patterns:
            matches = re.findall(pattern, text.lower())
            pain_points.extend(matches)
        
        # Detectar beneficios
        benefits = []
        for pattern in self.benefit_patterns:
            matches = re.findall(pattern, text.lower())
            benefits.extend(matches)
        
        # Calcular score de conversión
        conversion_sentiment = self._calculate_conversion_sentiment(
            emotion_scores, urgency_detected, len(pain_points), len(benefits)
        )
        
        return SentimentAnalysis(
            overall_sentiment=overall_sentiment,
            confidence_score=confidence,
            emotion_scores=emotion_scores,
            persuasion_level=min(conversion_sentiment + 10, 95),
            urgency_detected=urgency_detected,
            pain_points_detected=pain_points[:5],  # Top 5
            benefits_highlighted=benefits[:5],     # Top 5
            conversion_sentiment=conversion_sentiment
        )
    
    async def _analyze_readability(self, text: str) -> ReadabilityAnalysis:
        """Análisis de legibilidad ultra-detallado."""
        
        await asyncio.sleep(0.05)
        
        # Calcular métricas básicas
        sentences = len(re.findall(r'[.!?]+', text))
        words = len(text.split())
        syllables = self._count_syllables(text)
        
        # Evitar división por cero
        if sentences == 0 or words == 0:
            sentences = 1
            words = 1
        
        # Flesch-Kincaid Score
        avg_sentence_length = words / sentences
        avg_syllables_per_word = syllables / words
        
        flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        flesch_score = max(0, min(100, flesch_score))  # Clamp entre 0-100
        
        # Determinar nivel de lectura
        if flesch_score >= 90:
            reading_level = "elementary"
            grade = "A+"
        elif flesch_score >= 80:
            reading_level = "middle_school"
            grade = "A"
        elif flesch_score >= 70:
            reading_level = "high_school"
            grade = "B+"
        elif flesch_score >= 60:
            reading_level = "college"
            grade = "B"
        elif flesch_score >= 50:
            reading_level = "difficult"
            grade = "C+"
        else:
            reading_level = "very_difficult"
            grade = "C"
        
        # Detectar palabras complejas (3+ sílabas)
        complex_words = [word for word in text.split() if self._count_word_syllables(word) >= 3]
        complex_ratio = len(complex_words) / words if words > 0 else 0
        
        # Detectar voz pasiva (aproximación)
        passive_indicators = ["is", "was", "been", "being", "be"]
        passive_count = sum(1 for word in text.split() if word.lower() in passive_indicators)
        passive_ratio = passive_count / words if words > 0 else 0
        
        # Calcular longitud promedio de palabras
        avg_word_length = sum(len(word) for word in text.split()) / words if words > 0 else 0
        
        # Generar recomendaciones
        recommendations = []
        if avg_sentence_length > 20:
            recommendations.append("Acortar oraciones - promedio ideal: 15-20 palabras")
        if complex_ratio > 0.15:
            recommendations.append("Reducir palabras complejas - usar términos más simples")
        if passive_ratio > 0.10:
            recommendations.append("Reducir voz pasiva - usar voz activa para más impacto")
        if avg_word_length > 5:
            recommendations.append("Usar palabras más cortas y directas")
        
        return ReadabilityAnalysis(
            flesch_kincaid_score=flesch_score,
            reading_level=reading_level,
            avg_sentence_length=avg_sentence_length,
            avg_word_length=avg_word_length,
            complex_words_ratio=complex_ratio,
            passive_voice_ratio=passive_ratio,
            readability_grade=grade,
            recommendations=recommendations
        )
    
    async def _analyze_keywords(self, text: str, industry: str) -> KeywordAnalysis:
        """Análisis y extracción automática de keywords."""
        
        await asyncio.sleep(0.1)
        
        # Limpiar y tokenizar texto
        clean_text = re.sub(r'[^\w\s]', '', text.lower())
        words = clean_text.split()
        
        # Palabras comunes a filtrar
        stop_words = set([
            "the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with",
            "by", "from", "up", "about", "into", "through", "during", "before",
            "after", "above", "below", "between", "among", "this", "that", "these",
            "those", "i", "me", "my", "myself", "we", "our", "ours", "ourselves",
            "you", "your", "yours", "yourself", "he", "him", "his", "himself",
            "she", "her", "hers", "herself", "it", "its", "itself", "they", "them",
            "their", "theirs", "themselves", "what", "which", "who", "whom", "whose",
            "this", "that", "these", "those", "am", "is", "are", "was", "were",
            "be", "been", "being", "have", "has", "had", "having", "do", "does",
            "did", "doing", "will", "would", "could", "should", "may", "might",
            "must", "can", "shall", "a", "an"
        ])
        
        # Filtrar palabras significativas
        meaningful_words = [word for word in words if len(word) > 2 and word not in stop_words]
        
        # Contar frecuencias
        word_freq = Counter(meaningful_words)
        
        # Extraer keywords primarias (más frecuentes)
        primary_keywords = []
        for word, freq in word_freq.most_common(10):
            relevance = min(freq * 10, 100)  # Normalizar
            density = (freq / len(meaningful_words)) * 100 if meaningful_words else 0
            primary_keywords.append({
                "keyword": word,
                "frequency": freq,
                "relevance": relevance,
                "density": round(density, 2)
            })
        
        # Extraer frases de 2-3 palabras (long tail)
        bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
        trigrams = [f"{words[i]} {words[i+1]} {words[i+2]}" for i in range(len(words)-2)]
        
        phrase_freq = Counter(bigrams + trigrams)
        long_tail_phrases = []
        for phrase, freq in phrase_freq.most_common(5):
            if freq > 1:  # Solo frases que aparecen más de una vez
                long_tail_phrases.append({
                    "phrase": phrase,
                    "frequency": freq,
                    "relevance": min(freq * 15, 100)
                })
        
        # Keywords semánticas basadas en industria
        semantic_keywords = self._get_semantic_keywords(industry, meaningful_words)
        
        # Calcular score de densidad general
        if primary_keywords:
            avg_density = sum(kw["density"] for kw in primary_keywords) / len(primary_keywords)
            if 2.0 <= avg_density <= 3.0:
                density_score = 100
            elif 1.5 <= avg_density <= 4.0:
                density_score = 85
            else:
                density_score = 60
        else:
            density_score = 0
        
        # Distribución por secciones (simulada)
        keyword_distribution = {
            "headline": len([kw for kw in primary_keywords[:3]]),
            "body": len([kw for kw in primary_keywords[3:7]]),
            "cta": len([kw for kw in primary_keywords[7:]])
        }
        
        # SEO gaps (keywords que deberían estar presentes)
        seo_gaps = self._identify_seo_gaps(industry, meaningful_words)
        
        return KeywordAnalysis(
            primary_keywords=primary_keywords,
            secondary_keywords=primary_keywords[5:],  # Keywords secundarias
            long_tail_phrases=long_tail_phrases,
            semantic_keywords=semantic_keywords,
            keyword_density_score=density_score,
            keyword_distribution=keyword_distribution,
            seo_keyword_gaps=seo_gaps,
            competitor_keywords=self._suggest_competitor_keywords(industry)
        )
    
    async def _analyze_tone(self, text: str, target_audience: str) -> ToneAnalysis:
        """Análisis de tono y estilo ultra-detallado."""
        
        await asyncio.sleep(0.05)
        
        # Detectar categoría de tono
        tone_indicators = {
            "professional": ["expertise", "solution", "proven", "reliable", "professional"],
            "friendly": ["you", "we", "together", "help", "support", "welcome"],
            "urgent": ["now", "today", "limited", "hurry", "immediately", "expires"],
            "luxury": ["premium", "exclusive", "elite", "luxury", "sophisticated"],
            "casual": ["hey", "cool", "awesome", "easy", "simple", "fun"]
        }
        
        tone_scores = {}
        for tone, indicators in tone_indicators.items():
            score = sum(1 for indicator in indicators if indicator.lower() in text.lower())
            tone_scores[tone] = score
        
        # Determinar tono principal
        primary_tone = max(tone_scores.keys(), key=lambda k: tone_scores[k]) if tone_scores else "professional"
        
        # Calcular nivel de formalidad
        formal_indicators = ["therefore", "however", "furthermore", "consequently", "moreover"]
        informal_indicators = ["you", "we", "get", "make", "do", "go"]
        
        formal_count = sum(1 for word in formal_indicators if word.lower() in text.lower())
        informal_count = sum(1 for word in informal_indicators if word.lower() in text.lower())
        
        total_indicators = formal_count + informal_count
        if total_indicators > 0:
            formality_level = (formal_count / total_indicators) * 100
        else:
            formality_level = 50  # Neutral
        
        # Calcular persuasión
        persuasive_words = sum(1 for word_list in self.power_words.values() for word in word_list if word.lower() in text.lower())
        persuasiveness = min(persuasive_words * 10, 100)
        
        # Calcular confiabilidad
        trust_words = ["guarantee", "proven", "certified", "verified", "trusted", "secure"]
        trust_count = sum(1 for word in trust_words if word.lower() in text.lower())
        trustworthiness = min(trust_count * 20, 100)
        
        # Calcular apelación emocional
        emotional_words = sum(len(words) for words in self.emotion_words.values())
        emotional_count = sum(1 for word_list in self.emotion_words.values() for word in word_list if word.lower() in text.lower())
        emotional_appeal = min((emotional_count / max(emotional_words * 0.1, 1)) * 100, 100)
        
        # Calcular claridad
        avg_word_length = sum(len(word) for word in text.split()) / len(text.split()) if text.split() else 0
        clarity_score = max(100 - (avg_word_length - 4) * 10, 0)  # Penalizar palabras muy largas
        
        # Alineación con audiencia objetivo
        audience_fit = self._calculate_audience_fit(target_audience, primary_tone, formality_level)
        
        return ToneAnalysis(
            tone_category=primary_tone,
            formality_level=formality_level,
            persuasiveness=persuasiveness,
            trustworthiness=trustworthiness,
            emotional_appeal=emotional_appeal,
            clarity_score=clarity_score,
            brand_voice_alignment=85.0,  # Placeholder
            target_audience_fit=audience_fit
        )
    
    async def _generate_optimizations(
        self, 
        content: Dict[str, str], 
        target_audience: str, 
        conversion_goal: str
    ) -> ContentOptimization:
        """Genera optimizaciones automáticas basadas en NLP."""
        
        await asyncio.sleep(0.1)
        
        # Analizar cada sección del contenido
        headline = content.get("headline", "")
        body = content.get("body", "")
        cta = content.get("cta", "")
        
        # Optimizaciones de headline
        headline_improvements = []
        if len(headline.split()) > 15:
            headline_improvements.append("Acortar headline a 10-15 palabras máximo")
        if not any(word in headline.lower() for word in self.power_words["action"]):
            headline_improvements.append("Agregar word de acción al headline")
        if not any(word in headline.lower() for word in self.emotion_words["excitement"]):
            headline_improvements.append("Incluir palabras de emoción/excitement")
        
        # Optimizaciones de contenido
        content_enhancements = []
        if len(body.split()) < 50:
            content_enhancements.append("Expandir contenido - mínimo 50 palabras")
        if body.count(".") < 3:
            content_enhancements.append("Dividir en más párrafos para mejor legibilidad")
        if not any(pattern in body.lower() for pattern in ["save", "increase", "boost"]):
            content_enhancements.append("Agregar beneficios cuantificables")
        
        # Optimizaciones de CTA
        cta_optimizations = []
        if len(cta.split()) > 3:
            cta_optimizations.append("Acortar CTA a máximo 3 palabras")
        if not any(word in cta.lower() for word in self.power_words["action"]):
            cta_optimizations.append("Usar verbo de acción fuerte")
        if not any(word in cta.lower() for word in self.power_words["urgency"]):
            cta_optimizations.append("Agregar elemento de urgencia")
        
        # Optimizaciones SEO
        seo_improvements = [
            "Incluir keyword principal en primera oración",
            "Agregar variaciones de keyword en subtítulos",
            "Optimizar densidad de keywords a 2-3%"
        ]
        
        # Boosters de conversión
        conversion_boosters = [
            "Agregar elemento de scarcity (limitado/exclusivo)",
            "Incluir prueba social específica (números/testimonios)",
            "Añadir garantía o risk-reversal",
            "Crear sentido de urgencia temporal"
        ]
        
        # Mejoras de legibilidad
        readability_fixes = [
            "Usar frases más cortas (15-20 palabras max)",
            "Reemplazar palabras complejas por términos simples",
            "Agregar bullet points para información clave",
            "Usar voz activa en lugar de pasiva"
        ]
        
        # Ajustes de tono
        tone_adjustments = []
        if target_audience == "business owners":
            tone_adjustments.append("Usar tono más profesional y autoritativo")
        elif target_audience == "consumers":
            tone_adjustments.append("Adoptar tono más amigable y accesible")
        
        # Calcular prioridad
        total_improvements = (
            len(headline_improvements) + len(content_enhancements) + 
            len(cta_optimizations) + len(seo_improvements)
        )
        priority_score = min(total_improvements * 10, 100)
        
        return ContentOptimization(
            headline_improvements=headline_improvements,
            content_enhancements=content_enhancements,
            cta_optimizations=cta_optimizations,
            seo_improvements=seo_improvements,
            conversion_boosters=conversion_boosters,
            readability_fixes=readability_fixes,
            tone_adjustments=tone_adjustments,
            priority_score=priority_score
        )
    
    def _combine_content(self, content: Dict[str, str]) -> str:
        """Combina todo el contenido para análisis."""
        return " ".join(content.values())
    
    def _count_syllables(self, text: str) -> int:
        """Cuenta sílabas aproximadas en el texto."""
        words = text.split()
        return sum(self._count_word_syllables(word) for word in words)
    
    def _count_word_syllables(self, word: str) -> int:
        """Cuenta sílabas en una palabra (aproximación)."""
        word = word.lower().strip()
        if len(word) <= 3:
            return 1
        
        vowels = "aeiouy"
        syllables = 0
        prev_char_was_vowel = False
        
        for char in word:
            if char in vowels:
                if not prev_char_was_vowel:
                    syllables += 1
                prev_char_was_vowel = True
            else:
                prev_char_was_vowel = False
        
        # Ajustes
        if word.endswith("e"):
            syllables -= 1
        if syllables == 0:
            syllables = 1
            
        return syllables
    
    def _calculate_conversion_sentiment(
        self, 
        emotions: Dict[str, float], 
        urgency: bool, 
        pain_points: int, 
        benefits: int
    ) -> float:
        """Calcula score de sentimiento optimizado para conversión."""
        
        base_score = emotions.get("trust", 0) + emotions.get("excitement", 0)
        
        if urgency:
            base_score += 15
        
        base_score += min(pain_points * 10, 20)  # Max 20 puntos por pain points
        base_score += min(benefits * 15, 30)     # Max 30 puntos por benefits
        
        return min(base_score, 100)
    
    def _get_semantic_keywords(self, industry: str, words: List[str]) -> List[str]:
        """Obtiene keywords semánticamente relacionadas."""
        
        semantic_mapping = {
            "saas": ["software", "platform", "cloud", "automation", "productivity", "efficiency"],
            "ecommerce": ["shop", "buy", "product", "discount", "shipping", "checkout"],
            "education": ["learn", "course", "training", "skill", "knowledge", "certification"],
            "consulting": ["expert", "strategy", "growth", "optimization", "results", "success"]
        }
        
        base_keywords = semantic_mapping.get(industry.lower(), ["solution", "service", "help"])
        
        # Filtrar las que ya están en el contenido
        present_keywords = [kw for kw in base_keywords if kw in words]
        missing_keywords = [kw for kw in base_keywords if kw not in words]
        
        return present_keywords + missing_keywords[:3]  # Máximo 3 missing
    
    def _identify_seo_gaps(self, industry: str, words: List[str]) -> List[str]:
        """Identifica gaps de SEO importantes."""
        
        industry_keywords = {
            "saas": ["software", "platform", "solution", "business", "automation"],
            "ecommerce": ["online", "store", "shopping", "products", "buy"],
            "education": ["online", "course", "learning", "training", "certification"],
            "consulting": ["consulting", "strategy", "expert", "business", "growth"]
        }
        
        required_keywords = industry_keywords.get(industry.lower(), ["solution", "service"])
        missing = [kw for kw in required_keywords if kw not in words]
        
        return missing[:5]  # Top 5 gaps
    
    def _suggest_competitor_keywords(self, industry: str) -> List[str]:
        """Sugiere keywords que usan los competidores."""
        
        competitor_keywords = {
            "saas": ["alternative", "vs", "comparison", "better", "advanced"],
            "ecommerce": ["best", "top", "premium", "quality", "fast"],
            "education": ["certified", "accredited", "proven", "expert", "master"],
            "consulting": ["proven", "results", "experienced", "specialized", "strategic"]
        }
        
        return competitor_keywords.get(industry.lower(), ["professional", "quality", "reliable"])
    
    def _calculate_audience_fit(self, target_audience: str, tone: str, formality: float) -> float:
        """Calcula qué tan bien el tono se ajusta a la audiencia."""
        
        audience_preferences = {
            "business owners": {"tone": "professional", "formality": 70},
            "entrepreneurs": {"tone": "professional", "formality": 60},
            "consumers": {"tone": "friendly", "formality": 30},
            "students": {"tone": "casual", "formality": 20},
            "executives": {"tone": "professional", "formality": 80}
        }
        
        if target_audience.lower() in audience_preferences:
            prefs = audience_preferences[target_audience.lower()]
            
            # Score de tono
            tone_match = 100 if tone == prefs["tone"] else 70
            
            # Score de formalidad
            formality_diff = abs(formality - prefs["formality"])
            formality_match = max(100 - formality_diff, 0)
            
            return (tone_match + formality_match) / 2
        
        return 75  # Default score
    
    def _calculate_overall_nlp_score(
        self,
        sentiment: SentimentAnalysis,
        readability: ReadabilityAnalysis, 
        keywords: KeywordAnalysis,
        tone: ToneAnalysis
    ) -> float:
        """Calcula el score NLP general."""
        
        scores = [
            sentiment.conversion_sentiment * 0.3,      # 30% peso
            readability.flesch_kincaid_score * 0.25,   # 25% peso  
            keywords.keyword_density_score * 0.25,     # 25% peso
            tone.target_audience_fit * 0.2             # 20% peso
        ]
        
        return round(sum(scores), 1)
    
    def get_nlp_analytics(self) -> Dict[str, Any]:
        """Obtiene analíticas del motor NLP."""
        
        avg_processing_time = self.total_processing_time / self.analysis_count if self.analysis_count > 0 else 0
        
        return {
            "total_analyses": self.analysis_count,
            "avg_processing_time_ms": round(avg_processing_time, 1),
            "features_available": [
                "✅ Sentiment Analysis (6 emotions)",
                "✅ Readability Analysis (Flesch-Kincaid)",
                "✅ Automatic Keyword Extraction", 
                "✅ Tone & Style Analysis",
                "✅ Content Optimization Suggestions",
                "✅ SEO Gap Identification",
                "✅ Conversion Sentiment Scoring",
                "✅ Audience Fit Calculation"
            ],
            "processing_capabilities": {
                "sentiment_emotions": list(self.emotion_words.keys()),
                "power_word_categories": list(self.power_words.keys()),
                "supported_industries": ["saas", "ecommerce", "education", "consulting"],
                "readability_levels": ["elementary", "middle_school", "high_school", "college"],
                "tone_categories": ["professional", "friendly", "urgent", "luxury", "casual"]
            }
        }


# =============================================================================
# 🎮 DEMO NLP AVANZADO
# =============================================================================

async def demo_ultra_nlp_analysis():
    """Demostración del motor NLP ultra-avanzado."""
    
    print("🧠 ULTRA NLP ENGINE - LIVE DEMONSTRATION")
    print("=" * 60)
    
    # Crear motor NLP
    nlp_engine = UltraNLPEngine()
    
    # Casos de prueba
    test_cases = [
        {
            "name": "SaaS Landing Page",
            "content": {
                "headline": "Revolutionary Business Automation Software That Saves 20+ Hours Weekly",
                "body": "Stop wasting time on manual tasks. Our proven automation platform helps small business owners eliminate repetitive work and focus on growth. Join 10,000+ successful companies already transforming their productivity.",
                "cta": "Start Free Trial Today"
            },
            "target_audience": "business owners",
            "industry": "saas",
            "conversion_goal": "signup"
        },
        {
            "name": "E-learning Course",
            "content": {
                "headline": "Master Digital Marketing in 30 Days with Expert Guidance",
                "body": "Struggling with ineffective marketing? Our comprehensive course teaches you proven strategies used by industry leaders. Get certified and boost your career with practical skills that deliver real results.",
                "cta": "Enroll Now"
            },
            "target_audience": "marketing professionals", 
            "industry": "education",
            "conversion_goal": "purchase"
        }
    ]
    
    results = []
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n🎯 NLP ANALYSIS CASE {i}/{len(test_cases)}")
        print(f"📄 {case['name']}")
        print("-" * 40)
        
        # Ejecutar análisis NLP completo
        insights = await nlp_engine.analyze_complete_content(
            content=case["content"],
            target_audience=case["target_audience"],
            industry=case["industry"],
            conversion_goal=case["conversion_goal"]
        )
        
        results.append({"case": case["name"], "insights": insights})
        
        # Mostrar insights principales
        print(f"\n📊 KEY NLP INSIGHTS:")
        print(f"   😊 Sentiment: {insights.sentiment.overall_sentiment} ({insights.sentiment.confidence_score:.1f}% confidence)")
        print(f"   📖 Readability: {insights.readability.reading_level} (Score: {insights.readability.flesch_kincaid_score:.1f})")
        print(f"   🔑 Primary Keywords: {len(insights.keywords.primary_keywords)} found")
        print(f"   🎭 Tone: {insights.tone.tone_category} (Persuasiveness: {insights.tone.persuasiveness:.1f}%)")
        print(f"   🎯 Conversion Fit: {insights.tone.target_audience_fit:.1f}%")
        print(f"   🏆 Overall NLP Score: {insights.overall_nlp_score:.1f}/100")
        
        # Mostrar top optimizations
        if insights.optimization.headline_improvements:
            print(f"\n🔧 TOP OPTIMIZATIONS:")
            for opt in insights.optimization.headline_improvements[:2]:
                print(f"   • {opt}")
        
        if i < len(test_cases):
            print(f"\n⏳ Processing next case...")
            await asyncio.sleep(0.5)
    
    # Resumen final
    print(f"\n🎉 NLP ANALYSIS COMPLETED!")
    print("=" * 60)
    
    analytics = nlp_engine.get_nlp_analytics()
    
    print(f"📈 NLP ENGINE PERFORMANCE:")
    print(f"   🧠 Total Analyses: {analytics['total_analyses']}")
    print(f"   ⚡ Avg Processing Time: {analytics['avg_processing_time_ms']:.1f}ms")
    print(f"   🎯 Overall Scores: {[r['insights'].overall_nlp_score for r in results]}")
    
    print(f"\n🚀 NLP FEATURES DEMONSTRATED:")
    for feature in analytics['features_available']:
        print(f"   {feature}")
    
    print(f"\n💡 INSIGHTS GENERATED:")
    for result in results:
        insights = result["insights"]
        print(f"   📄 {result['case']}:")
        print(f"      • Emotions detected: {list(insights.sentiment.emotion_scores.keys())}")
        print(f"      • Keywords found: {len(insights.keywords.primary_keywords)}")
        print(f"      • Optimizations: {len(insights.optimization.headline_improvements)}")
    
    return results, analytics


if __name__ == "__main__":
    print("🧠 Ultra NLP Engine Loaded")
    print("🚀 Ready for advanced natural language processing!")
    
    # Ejecutar demo
    asyncio.run(demo_ultra_nlp_analysis()) 