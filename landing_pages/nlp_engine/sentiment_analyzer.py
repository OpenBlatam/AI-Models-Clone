"""
😊 SENTIMENT ANALYZER - ADVANCED EMOTION & PERSUASION DETECTION
==============================================================

Analizador de sentimientos ultra-avanzado para landing pages:
- Detección de emociones múltiples
- Análisis de persuasión y confianza
- Scoring de conversión emocional
- Detección de pain points y beneficios
"""

import re
import asyncio
from typing import Dict, List, Any, Tuple
from collections import Counter
from dataclasses import dataclass


@dataclass
class EmotionSignals:
    """Señales emocionales detectadas en el texto."""
    
    joy_words: List[str]
    trust_words: List[str]
    fear_words: List[str]
    excitement_words: List[str]
    urgency_words: List[str]
    confidence_words: List[str]


class UltraSentimentAnalyzer:
    """Analizador de sentimientos ultra-avanzado."""
    
    def __init__(self):
        # Diccionarios emocionales expandidos
        self.emotion_lexicon = {
            "joy": {
                "words": ["amazing", "incredible", "fantastic", "excellent", "outstanding", "superb", 
                         "wonderful", "brilliant", "awesome", "perfect", "exceptional", "remarkable"],
                "weight": 1.2,
                "conversion_impact": 0.9
            },
            "trust": {
                "words": ["proven", "reliable", "trusted", "guaranteed", "certified", "verified",
                         "secure", "safe", "established", "reputable", "credible", "authentic"],
                "weight": 1.5,
                "conversion_impact": 1.0
            },
            "excitement": {
                "words": ["revolutionary", "breakthrough", "game-changing", "cutting-edge", "innovative",
                         "groundbreaking", "transformational", "disruptive", "next-generation"],
                "weight": 1.3,
                "conversion_impact": 0.8
            },
            "urgency": {
                "words": ["now", "today", "immediately", "limited", "expires", "hurry", "fast",
                         "instant", "quick", "deadline", "last-chance", "final"],
                "weight": 1.1,
                "conversion_impact": 0.7
            },
            "fear": {
                "words": ["problem", "struggle", "difficult", "challenging", "pain", "frustrating",
                         "stuck", "failing", "losing", "missing", "waste", "risk"],
                "weight": 0.8,
                "conversion_impact": 0.6
            },
            "confidence": {
                "words": ["expert", "professional", "mastery", "skilled", "experienced", "qualified",
                         "certified", "trained", "knowledgeable", "specialist"],
                "weight": 1.4,
                "conversion_impact": 0.9
            }
        }
        
        # Patrones de persuasión
        self.persuasion_patterns = {
            "social_proof": [
                r"\d+[\+\,]?\s*(customers?|clients?|users?|companies?)",
                r"\d+%\s*of\s*(people|users|customers)",
                r"join\s+\d+[\+\,]?\s*(others?|customers?)",
                r"trusted\s+by\s+\d+"
            ],
            "scarcity": [
                r"only\s+\d+\s+(left|remaining|available)",
                r"limited\s+(time|supply|offer|availability)",
                r"exclusive\s+(access|offer|deal)",
                r"while\s+supplies\s+last"
            ],
            "authority": [
                r"expert\s+(recommended|approved|designed)",
                r"industry\s+(leader|standard|expert)",
                r"award[\-\s]winning",
                r"featured\s+in\s+(forbes|techcrunch|wsj)"
            ],
            "reciprocity": [
                r"free\s+(trial|download|access|guide)",
                r"no\s+(cost|charge|obligation)",
                r"complimentary\s+(consultation|analysis)",
                r"bonus\s+(included|material|content)"
            ]
        }
        
        # Pain points comunes por industria
        self.industry_pain_points = {
            "saas": ["manual processes", "inefficiency", "time wasting", "human error", "scaling issues"],
            "ecommerce": ["slow shipping", "high prices", "poor quality", "difficult returns"],
            "education": ["outdated skills", "lack of certification", "expensive courses", "time constraints"],
            "consulting": ["stagnant growth", "unclear strategy", "poor ROI", "market confusion"]
        }
        
        # Beneficios específicos
        self.benefit_patterns = [
            r"save\s+(\d+[\+\%]?)\s*(hours?|minutes?|time|money)",
            r"increase\s+(\d+[\+\%]?)",
            r"boost\s+(\d+[\+\%]?)",
            r"improve\s+(\d+[\+\%]?)",
            r"(\d+[\+\%]?)\s*(more|faster|better|higher)",
            r"(\d+x)\s*(growth|increase|improvement)"
        ]
    
    async def analyze_sentiment_ultra(
        self,
        text: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Análisis de sentimientos ultra-completo."""
        
        print(f"😊 Analyzing sentiment for {len(text)} characters of content...")
        
        # Preparar texto
        clean_text = self._clean_text(text)
        words = clean_text.split()
        
        # Análisis en paralelo
        tasks = [
            self._analyze_emotions(clean_text, words),
            self._analyze_persuasion_elements(clean_text),
            self._detect_pain_points(clean_text, context),
            self._detect_benefits(clean_text),
            self._calculate_conversion_sentiment(clean_text)
        ]
        
        results = await asyncio.gather(*tasks)
        
        emotion_analysis = results[0]
        persuasion_analysis = results[1]
        pain_points = results[2]
        benefits = results[3]
        conversion_score = results[4]
        
        # Determinar sentimiento general
        overall_sentiment = self._determine_overall_sentiment(emotion_analysis)
        
        # Calcular confianza
        confidence = self._calculate_confidence(emotion_analysis, len(words))
        
        # Preparar resultado completo
        sentiment_result = {
            "overall_sentiment": overall_sentiment["sentiment"],
            "confidence_score": confidence,
            "polarity_score": overall_sentiment["polarity"],
            
            # Análisis emocional detallado
            "emotion_scores": emotion_analysis,
            "dominant_emotion": max(emotion_analysis.keys(), key=lambda k: emotion_analysis[k]["score"]),
            
            # Elementos de persuasión
            "persuasion_level": persuasion_analysis["overall_score"],
            "persuasion_elements": persuasion_analysis["elements"],
            "urgency_detected": persuasion_analysis["urgency_detected"],
            "scarcity_detected": persuasion_analysis["scarcity_detected"],
            
            # Pain points y beneficios
            "pain_points_detected": pain_points,
            "benefits_highlighted": benefits,
            
            # Score de conversión
            "conversion_sentiment_score": conversion_score,
            
            # Insights adicionales
            "emotional_balance": self._calculate_emotional_balance(emotion_analysis),
            "trust_indicators": self._extract_trust_indicators(clean_text),
            "urgency_level": self._calculate_urgency_level(clean_text)
        }
        
        print(f"✅ Sentiment analysis completed")
        print(f"📊 Overall: {overall_sentiment['sentiment']} ({confidence:.1f}% confidence)")
        print(f"🎯 Conversion Score: {conversion_score:.1f}/100")
        print(f"💪 Persuasion Level: {persuasion_analysis['overall_score']:.1f}/100")
        
        return sentiment_result
    
    async def _analyze_emotions(self, text: str, words: List[str]) -> Dict[str, Dict[str, Any]]:
        """Análisis detallado de emociones."""
        
        emotion_results = {}
        
        for emotion, config in self.emotion_lexicon.items():
            # Contar palabras de la emoción
            emotion_words_found = []
            score = 0
            
            for word in config["words"]:
                count = text.lower().count(word.lower())
                if count > 0:
                    emotion_words_found.append(word)
                    score += count * config["weight"]
            
            # Normalizar score
            normalized_score = min((score / max(len(words) * 0.1, 1)) * 100, 100)
            
            # Calcular confianza basada en diversidad de palabras
            confidence = min(len(emotion_words_found) * 20, 100) if emotion_words_found else 0
            
            emotion_results[emotion] = {
                "score": normalized_score,
                "confidence": confidence,
                "detected_words": emotion_words_found,
                "impact_on_conversion": normalized_score * config["conversion_impact"]
            }
        
        return emotion_results
    
    async def _analyze_persuasion_elements(self, text: str) -> Dict[str, Any]:
        """Análisis de elementos de persuasión."""
        
        persuasion_scores = {}
        detected_elements = []
        
        for principle, patterns in self.persuasion_patterns.items():
            score = 0
            found_patterns = []
            
            for pattern in patterns:
                matches = re.findall(pattern, text.lower())
                if matches:
                    found_patterns.extend(matches)
                    score += len(matches) * 25  # 25 puntos por match
            
            if found_patterns:
                detected_elements.append({
                    "principle": principle,
                    "score": min(score, 100),
                    "evidence": found_patterns[:3]  # Top 3 ejemplos
                })
                persuasion_scores[principle] = min(score, 100)
            else:
                persuasion_scores[principle] = 0
        
        # Score general de persuasión
        overall_score = sum(persuasion_scores.values()) / len(persuasion_scores) if persuasion_scores else 0
        
        # Detección específica de urgencia y escasez
        urgency_detected = persuasion_scores.get("scarcity", 0) > 20 or any(
            word in text.lower() for word in ["now", "today", "limited", "expires"]
        )
        
        scarcity_detected = persuasion_scores.get("scarcity", 0) > 30
        
        return {
            "overall_score": overall_score,
            "elements": detected_elements,
            "urgency_detected": urgency_detected,
            "scarcity_detected": scarcity_detected,
            "individual_scores": persuasion_scores
        }
    
    async def _detect_pain_points(self, text: str, context: Dict[str, Any] = None) -> List[str]:
        """Detecta pain points mencionados."""
        
        pain_points_found = []
        
        # Patrones generales de pain points
        general_patterns = [
            r"struggling with ([^.]+)",
            r"tired of ([^.]+)",
            r"frustrated (by|with) ([^.]+)",
            r"problem with ([^.]+)",
            r"difficult to ([^.]+)",
            r"hard to ([^.]+)",
            r"wasting (time|money) on ([^.]+)",
            r"inefficient ([^.]+)",
            r"manual ([^.]+)",
            r"outdated ([^.]+)"
        ]
        
        for pattern in general_patterns:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                if isinstance(match, tuple):
                    pain_point = " ".join(match).strip()
                else:
                    pain_point = match.strip()
                
                if len(pain_point) > 3 and pain_point not in pain_points_found:
                    pain_points_found.append(pain_point)
        
        # Pain points específicos por industria
        if context and "industry" in context:
            industry = context["industry"].lower()
            if industry in self.industry_pain_points:
                for pain_point in self.industry_pain_points[industry]:
                    if pain_point.lower() in text.lower():
                        pain_points_found.append(pain_point)
        
        return pain_points_found[:5]  # Top 5 pain points
    
    async def _detect_benefits(self, text: str) -> List[str]:
        """Detecta beneficios destacados."""
        
        benefits_found = []
        
        for pattern in self.benefit_patterns:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                if isinstance(match, tuple):
                    benefit = " ".join(str(m) for m in match if m).strip()
                else:
                    benefit = str(match).strip()
                
                if benefit and benefit not in benefits_found:
                    benefits_found.append(benefit)
        
        # Beneficios cualitativos
        qualitative_benefits = [
            r"(save|reduce|cut) (time|costs?|money|effort)",
            r"(increase|boost|improve|enhance) (productivity|efficiency|performance|results)",
            r"(eliminate|remove|avoid) (hassle|stress|worry|problems?)",
            r"(get|achieve|reach) (success|goals?|growth|results)"
        ]
        
        for pattern in qualitative_benefits:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                benefit = " ".join(match)
                if benefit not in benefits_found:
                    benefits_found.append(benefit)
        
        return benefits_found[:5]  # Top 5 beneficios
    
    async def _calculate_conversion_sentiment(self, text: str) -> float:
        """Calcula score de sentimiento optimizado para conversión."""
        
        conversion_factors = {
            "positive_emotions": 0.3,    # 30% del score
            "trust_signals": 0.25,      # 25% del score
            "urgency_elements": 0.2,    # 20% del score
            "benefit_mentions": 0.15,   # 15% del score
            "social_proof": 0.1         # 10% del score
        }
        
        scores = {}
        
        # Emociones positivas
        positive_words = (
            self.emotion_lexicon["joy"]["words"] + 
            self.emotion_lexicon["excitement"]["words"] +
            self.emotion_lexicon["confidence"]["words"]
        )
        positive_count = sum(1 for word in positive_words if word.lower() in text.lower())
        scores["positive_emotions"] = min(positive_count * 10, 100)
        
        # Señales de confianza
        trust_count = sum(1 for word in self.emotion_lexicon["trust"]["words"] if word.lower() in text.lower())
        scores["trust_signals"] = min(trust_count * 15, 100)
        
        # Elementos de urgencia
        urgency_count = sum(1 for word in self.emotion_lexicon["urgency"]["words"] if word.lower() in text.lower())
        scores["urgency_elements"] = min(urgency_count * 20, 100)
        
        # Menciones de beneficios
        benefit_count = len(re.findall(r"save|increase|boost|improve|\d+%|\d+x", text.lower()))
        scores["benefit_mentions"] = min(benefit_count * 15, 100)
        
        # Prueba social
        social_proof_count = len(re.findall(r"\d+[\+\,]?\s*(customers?|users?|companies?)", text.lower()))
        scores["social_proof"] = min(social_proof_count * 30, 100)
        
        # Calcular score ponderado
        conversion_score = sum(
            scores[factor] * weight for factor, weight in conversion_factors.items()
        )
        
        return min(conversion_score, 100)
    
    def _clean_text(self, text: str) -> str:
        """Limpia el texto para análisis."""
        # Remover HTML si existe
        text = re.sub(r'<[^>]+>', '', text)
        
        # Normalizar espacios
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _determine_overall_sentiment(self, emotion_analysis: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Determina el sentimiento general."""
        
        positive_score = (
            emotion_analysis["joy"]["score"] + 
            emotion_analysis["trust"]["score"] + 
            emotion_analysis["excitement"]["score"] +
            emotion_analysis["confidence"]["score"]
        ) / 4
        
        negative_score = emotion_analysis["fear"]["score"]
        neutral_elements = emotion_analysis["urgency"]["score"]
        
        if positive_score > negative_score * 1.5:
            sentiment = "positive"
            polarity = 0.3 + (positive_score / 100) * 0.7  # 0.3 to 1.0
        elif negative_score > positive_score:
            sentiment = "negative"
            polarity = -0.3 - (negative_score / 100) * 0.7  # -0.3 to -1.0
        else:
            sentiment = "neutral"
            polarity = 0.0
        
        return {"sentiment": sentiment, "polarity": polarity}
    
    def _calculate_confidence(self, emotion_analysis: Dict[str, Dict[str, Any]], word_count: int) -> float:
        """Calcula la confianza del análisis."""
        
        # Factores de confianza
        total_detections = sum(len(analysis["detected_words"]) for analysis in emotion_analysis.values())
        detection_ratio = total_detections / max(word_count * 0.1, 1)
        
        # Score de diversidad emocional
        emotions_detected = sum(1 for analysis in emotion_analysis.values() if analysis["score"] > 10)
        diversity_score = min(emotions_detected * 15, 90)
        
        # Score de intensidad
        max_emotion_score = max(analysis["score"] for analysis in emotion_analysis.values())
        intensity_score = min(max_emotion_score, 90)
        
        # Calcular confianza final
        confidence = (
            detection_ratio * 30 +    # 30% por ratio de detección
            diversity_score * 0.4 +   # 40% por diversidad
            intensity_score * 0.3     # 30% por intensidad
        )
        
        return min(confidence, 95)  # Max 95% de confianza
    
    def _calculate_emotional_balance(self, emotion_analysis: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        """Calcula el balance emocional del contenido."""
        
        positive_emotions = ["joy", "trust", "excitement", "confidence"]
        negative_emotions = ["fear"]
        neutral_emotions = ["urgency"]
        
        positive_avg = sum(emotion_analysis[emotion]["score"] for emotion in positive_emotions) / len(positive_emotions)
        negative_avg = sum(emotion_analysis[emotion]["score"] for emotion in negative_emotions) / len(negative_emotions)
        neutral_avg = sum(emotion_analysis[emotion]["score"] for emotion in neutral_emotions) / len(neutral_emotions)
        
        return {
            "positive": positive_avg,
            "negative": negative_avg,
            "neutral": neutral_avg,
            "balance_ratio": positive_avg / max(negative_avg, 1)
        }
    
    def _extract_trust_indicators(self, text: str) -> List[str]:
        """Extrae indicadores específicos de confianza."""
        
        trust_patterns = [
            r"(guarantee[d]?|guaranteed)",
            r"(money[\-\s]back)",
            r"(risk[\-\s]free)",
            r"(secure|safety|protected)",
            r"(certified|verified|approved)",
            r"(\d+[\-\+]?\s*years?\s*(of\s+)?experience)",
            r"(award[\-\s]winning)",
            r"(industry[\-\s]leader)"
        ]
        
        trust_indicators = []
        for pattern in trust_patterns:
            matches = re.findall(pattern, text.lower())
            trust_indicators.extend([match[0] if isinstance(match, tuple) else match for match in matches])
        
        return list(set(trust_indicators))[:5]  # Top 5 únicos
    
    def _calculate_urgency_level(self, text: str) -> Dict[str, Any]:
        """Calcula el nivel de urgencia del contenido."""
        
        urgency_indicators = {
            "time_sensitive": ["now", "today", "immediately", "instant"],
            "scarcity": ["limited", "only", "exclusive", "few"],
            "deadlines": ["expires", "deadline", "ends", "final"],
            "action_oriented": ["hurry", "quick", "fast", "don't wait"]
        }
        
        urgency_scores = {}
        detected_indicators = []
        
        for category, indicators in urgency_indicators.items():
            count = sum(1 for indicator in indicators if indicator in text.lower())
            urgency_scores[category] = min(count * 25, 100)
            
            if count > 0:
                detected_indicators.extend([ind for ind in indicators if ind in text.lower()])
        
        overall_urgency = sum(urgency_scores.values()) / len(urgency_scores)
        
        return {
            "overall_level": overall_urgency,
            "category_scores": urgency_scores,
            "detected_indicators": list(set(detected_indicators)),
            "urgency_grade": "high" if overall_urgency > 60 else "medium" if overall_urgency > 30 else "low"
        }


# Demo del analizador
if __name__ == "__main__":
    async def demo_sentiment_analyzer():
        print("😊 ULTRA SENTIMENT ANALYZER DEMO")
        print("=" * 50)
        
        analyzer = UltraSentimentAnalyzer()
        
        # Texto de prueba
        test_text = """
        Revolutionary business automation software that saves 20+ hours weekly! 
        Stop struggling with manual processes and join 10,000+ successful companies 
        already transforming their productivity. Our proven, trusted platform is 
        guaranteed to boost your efficiency by 300%. Limited time offer - 
        start your free trial today!
        """
        
        # Análisis completo
        result = await analyzer.analyze_sentiment_ultra(
            test_text, 
            context={"industry": "saas", "audience": "business owners"}
        )
        
        print(f"\n📊 SENTIMENT ANALYSIS RESULTS:")
        print(f"Overall Sentiment: {result['overall_sentiment']}")
        print(f"Confidence: {result['confidence_score']:.1f}%")
        print(f"Conversion Score: {result['conversion_sentiment_score']:.1f}/100")
        print(f"Dominant Emotion: {result['dominant_emotion']}")
        print(f"Persuasion Level: {result['persuasion_level']:.1f}%")
        
        print(f"\n🎭 EMOTION SCORES:")
        for emotion, data in result['emotion_scores'].items():
            print(f"  {emotion.capitalize()}: {data['score']:.1f}/100")
        
        print(f"\n💡 INSIGHTS:")
        print(f"  Pain Points: {result['pain_points_detected']}")
        print(f"  Benefits: {result['benefits_highlighted']}")
        print(f"  Trust Indicators: {result['trust_indicators']}")
        
        print(f"\n🚀 SENTIMENT ANALYZER READY!")
    
    asyncio.run(demo_sentiment_analyzer()) 