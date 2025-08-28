#!/usr/bin/env python3
"""
QUICK OPTIMIZER v5.0 - Sistema de Optimización Rápida
Versión ligera del LinkedIn Optimizer v5.0 para desarrollo continuo
"""

import asyncio
import time
import uuid
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OptimizationMode(Enum):
    """Modos de optimización disponibles."""
    BASIC = "basic"
    ADVANCED = "advanced"
    ENTERPRISE = "enterprise"
    QUANTUM = "quantum"

class ContentType(Enum):
    """Tipos de contenido soportados."""
    POST = "post"
    ARTICLE = "article"
    COMMENT = "comment"
    MESSAGE = "message"

@dataclass
class OptimizationResult:
    """Resultado de optimización."""
    content_id: str
    original_content: str
    optimized_content: str
    optimization_score: float
    suggestions: List[str]
    hashtags: List[str]
    mentions: List[str]
    mode: OptimizationMode
    timestamp: datetime
    processing_time: float

class QuickContentAnalyzer:
    """Analizador rápido de contenido."""
    
    def __init__(self):
        self.positive_words = [
            "excelente", "increíble", "fantástico", "brillante", "innovador",
            "revolucionario", "exitoso", "creativo", "inspirador", "poderoso"
        ]
        self.negative_words = [
            "terrible", "horrible", "malo", "pésimo", "fracaso", "problema",
            "error", "fallo", "deficiente", "inútil"
        ]
        self.professional_hashtags = [
            "#LinkedIn", "#Networking", "#Profesional", "#Carrera", "#Empleo",
            "#Negocios", "#Liderazgo", "#Innovación", "#Tecnología", "#Marketing"
        ]
        
        logger.info("🔍 Quick Content Analyzer initialized")
    
    def analyze_sentiment(self, content: str) -> float:
        """Análisis básico de sentimiento."""
        content_lower = content.lower()
        positive_count = sum(1 for word in self.positive_words if word in content_lower)
        negative_count = sum(1 for word in self.negative_words if word in content_lower)
        
        total_words = len(content.split())
        if total_words == 0:
            return 0.5
        
        sentiment_score = (positive_count - negative_count) / total_words
        return max(0.0, min(1.0, 0.5 + sentiment_score))
    
    def extract_hashtags(self, content: str) -> List[str]:
        """Extraer hashtags del contenido."""
        words = content.split()
        hashtags = [word for word in words if word.startswith('#')]
        return hashtags[:5]  # Máximo 5 hashtags
    
    def suggest_hashtags(self, content: str) -> List[str]:
        """Sugerir hashtags relevantes."""
        content_lower = content.lower()
        suggestions = []
        
        # Hashtags basados en palabras clave
        if any(word in content_lower for word in ["tecnología", "tech", "software"]):
            suggestions.extend(["#Tecnología", "#Software", "#Innovación"])
        
        if any(word in content_lower for word in ["negocio", "empresa", "startup"]):
            suggestions.extend(["#Negocios", "#Emprendimiento", "#Startup"])
        
        if any(word in content_lower for word in ["liderazgo", "management", "equipo"]):
            suggestions.extend(["#Liderazgo", "#Management", "#Equipo"])
        
        # Agregar hashtags profesionales generales
        suggestions.extend(self.professional_hashtags[:3])
        
        return list(set(suggestions))[:5]  # Máximo 5 hashtags únicos
    
    def extract_mentions(self, content: str) -> List[str]:
        """Extraer menciones del contenido."""
        words = content.split()
        mentions = [word for word in words if word.startswith('@')]
        return mentions

class QuickContentOptimizer:
    """Optimizador rápido de contenido."""
    
    def __init__(self):
        self.analyzer = QuickContentAnalyzer()
        self.optimization_rules = {
            OptimizationMode.BASIC: {
                "min_length": 50,
                "max_length": 300,
                "hashtag_limit": 3,
                "mention_limit": 2
            },
            OptimizationMode.ADVANCED: {
                "min_length": 100,
                "max_length": 500,
                "hashtag_limit": 5,
                "mention_limit": 3
            },
            OptimizationMode.ENTERPRISE: {
                "min_length": 150,
                "max_length": 800,
                "hashtag_limit": 7,
                "mention_limit": 5
            },
            OptimizationMode.QUANTUM: {
                "min_length": 200,
                "max_length": 1200,
                "hashtag_limit": 10,
                "mention_limit": 7
            }
        }
        
        logger.info("🚀 Quick Content Optimizer initialized")
    
    async def optimize_content(self, content: str, mode: OptimizationMode = OptimizationMode.ADVANCED) -> OptimizationResult:
        """Optimizar contenido según el modo especificado."""
        start_time = time.time()
        content_id = str(uuid.uuid4())
        
        logger.info(f"🔧 Optimizing content in {mode.value} mode")
        
        # Análisis inicial
        sentiment_score = self.analyzer.analyze_sentiment(content)
        current_hashtags = self.analyzer.extract_hashtags(content)
        current_mentions = self.analyzer.extract_mentions(content)
        
        # Optimización según modo
        optimized_content = content
        suggestions = []
        
        # Reglas del modo
        rules = self.optimization_rules[mode]
        
        # Verificar longitud
        if len(content) < rules["min_length"]:
            suggestions.append(f"Considera agregar más detalles (mínimo {rules['min_length']} caracteres)")
        
        if len(content) > rules["max_length"]:
            suggestions.append(f"Considera acortar el contenido (máximo {rules['max_length']} caracteres)")
        
        # Optimizar hashtags
        suggested_hashtags = self.analyzer.suggest_hashtags(content)
        if len(current_hashtags) < rules["hashtag_limit"]:
            missing_hashtags = suggested_hashtags[:rules["hashtag_limit"] - len(current_hashtags)]
            if missing_hashtags:
                optimized_content += " " + " ".join(missing_hashtags)
                suggestions.append(f"Hashtags agregados: {', '.join(missing_hashtags)}")
        
        # Optimizar menciones
        if len(current_mentions) < rules["mention_limit"]:
            suggestions.append(f"Considera agregar más menciones (máximo {rules['mention_limit']})")
        
        # Mejorar sentimiento si es necesario
        if sentiment_score < 0.4:
            suggestions.append("Considera usar un tono más positivo y motivador")
        elif sentiment_score > 0.8:
            suggestions.append("El contenido tiene un tono muy positivo, ¡excelente!")
        
        # Calcular score de optimización
        optimization_score = self._calculate_optimization_score(
            content_length=len(optimized_content),
            sentiment_score=sentiment_score,
            hashtag_count=len(self.analyzer.extract_hashtags(optimized_content)),
            mention_count=len(self.analyzer.extract_mentions(optimized_content)),
            mode=mode
        )
        
        processing_time = time.time() - start_time
        
        result = OptimizationResult(
            content_id=content_id,
            original_content=content,
            optimized_content=optimized_content,
            optimization_score=optimization_score,
            suggestions=suggestions,
            hashtags=self.analyzer.extract_hashtags(optimized_content),
            mentions=self.analyzer.extract_mentions(optimized_content),
            mode=mode,
            timestamp=datetime.now(),
            processing_time=processing_time
        )
        
        logger.info(f"✅ Content optimized with score: {optimization_score:.2f}")
        return result
    
    def _calculate_optimization_score(self, content_length: int, sentiment_score: float, 
                                    hashtag_count: int, mention_count: int, mode: OptimizationMode) -> float:
        """Calcular score de optimización."""
        rules = self.optimization_rules[mode]
        
        # Score de longitud (0-25 puntos)
        length_score = 0
        if rules["min_length"] <= content_length <= rules["max_length"]:
            length_score = 25
        elif content_length < rules["min_length"]:
            length_score = (content_length / rules["min_length"]) * 25
        else:
            length_score = max(0, 25 - ((content_length - rules["max_length"]) / 100) * 25)
        
        # Score de sentimiento (0-30 puntos)
        sentiment_points = sentiment_score * 30
        
        # Score de hashtags (0-25 puntos)
        hashtag_points = min(25, (hashtag_count / rules["hashtag_limit"]) * 25)
        
        # Score de menciones (0-20 puntos)
        mention_points = min(20, (mention_count / rules["mention_limit"]) * 20)
        
        total_score = length_score + sentiment_points + hashtag_points + mention_points
        return min(100.0, total_score)

class QuickSystemV5:
    """Sistema rápido v5.0."""
    
    def __init__(self):
        self.optimizer = QuickContentOptimizer()
        self.optimization_history = []
        self.system_status = "running"
        
        logger.info("🚀 Quick System v5.0 initialized")
    
    async def optimize_content(self, content: str, mode: OptimizationMode = OptimizationMode.ADVANCED) -> OptimizationResult:
        """Optimizar contenido usando el sistema rápido."""
        try:
            result = await self.optimizer.optimize_content(content, mode)
            self.optimization_history.append(result)
            return result
        except Exception as e:
            logger.error(f"❌ Optimization failed: {e}")
            raise
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado del sistema."""
        return {
            "status": self.system_status,
            "total_optimizations": len(self.optimization_history),
            "average_score": sum(r.optimization_score for r in self.optimization_history) / len(self.optimization_history) if self.optimization_history else 0,
            "last_optimization": self.optimization_history[-1].timestamp.isoformat() if self.optimization_history else None
        }
    
    def get_optimization_history(self) -> List[Dict[str, Any]]:
        """Obtener historial de optimizaciones."""
        return [
            {
                "content_id": result.content_id,
                "mode": result.mode.value,
                "score": result.optimization_score,
                "timestamp": result.timestamp.isoformat(),
                "processing_time": result.processing_time
            }
            for result in self.optimization_history
        ]

async def demo():
    """Función de demostración."""
    logger.info("🎯 Starting Quick System v5.0 Demo")
    
    try:
        # Crear sistema
        system = QuickSystemV5()
        
        # Contenido de ejemplo
        sample_content = """
        ¡Hola! Soy desarrollador de software y me encanta crear soluciones innovadoras.
        Tengo experiencia en Python, JavaScript y cloud computing.
        """
        
        # Optimizar en diferentes modos
        modes = [OptimizationMode.BASIC, OptimizationMode.ADVANCED, OptimizationMode.ENTERPRISE]
        
        for mode in modes:
            logger.info(f"🔧 Testing {mode.value} mode...")
            result = await system.optimize_content(sample_content, mode)
            
            print(f"\n📊 Resultados - Modo {mode.value.upper()}:")
            print(f"Score: {result.optimization_score:.1f}/100")
            print(f"Tiempo: {result.processing_time:.3f}s")
            print(f"Hashtags: {result.hashtags}")
            print(f"Sugerencias: {result.suggestions}")
            print("-" * 50)
        
        # Estado del sistema
        status = system.get_system_status()
        print(f"\n📈 Estado del Sistema:")
        print(f"Total optimizaciones: {status['total_optimizations']}")
        print(f"Score promedio: {status['average_score']:.1f}")
        
        logger.info("✅ Demo completed successfully")
        return system
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        raise

async def interactive_demo():
    """Demo interactivo."""
    print("🚀 QUICK LINKEDIN OPTIMIZER v5.0")
    print("=" * 40)
    
    try:
        system = QuickSystemV5()
        
        while True:
            print("\n📝 Ingresa tu contenido (o 'salir' para terminar):")
            content = input("> ").strip()
            
            if content.lower() in ['salir', 'exit', 'quit']:
                break
            
            if not content:
                print("❌ Por favor ingresa algún contenido")
                continue
            
            print("\n🎯 Selecciona el modo de optimización:")
            print("1. Básico")
            print("2. Avanzado")
            print("3. Empresarial")
            print("4. Cuántico")
            
            try:
                choice = input("> ").strip()
                mode_map = {
                    '1': OptimizationMode.BASIC,
                    '2': OptimizationMode.ADVANCED,
                    '3': OptimizationMode.ENTERPRISE,
                    '4': OptimizationMode.QUANTUM
                }
                
                mode = mode_map.get(choice, OptimizationMode.ADVANCED)
                
                print(f"\n🔧 Optimizando en modo {mode.value}...")
                result = await system.optimize_content(content, mode)
                
                print(f"\n📊 RESULTADOS:")
                print(f"Score: {result.optimization_score:.1f}/100")
                print(f"Tiempo: {result.processing_time:.3f}s")
                print(f"\n📝 Contenido optimizado:")
                print(result.optimized_content)
                print(f"\n🏷️ Hashtags: {result.hashtags}")
                print(f"👥 Menciones: {result.mentions}")
                print(f"\n💡 Sugerencias:")
                for suggestion in result.suggestions:
                    print(f"• {suggestion}")
                
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print("\n🎉 ¡Gracias por usar Quick LinkedIn Optimizer v5.0!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(interactive_demo())
    except KeyboardInterrupt:
        print("\n\nDemo cancelled by user.")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("Please check the error messages and try again.")
