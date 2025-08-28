from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS = 1000

# Constants
MAX_RETRIES = 100

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
import random
import threading
from typing import Any, List, Dict, Optional
import logging
"""
⏰ TIMEZONE OPTIMIZER - OPTIMIZACIÓN TEMPORAL ULTRA-AVANZADA
============================================================

Optimizador ultra-inteligente que ajusta el procesamiento basado en
zonas horarias, patrones temporales y distribución geográfica global.

Características:
- 🌍 Global Timezone Intelligence
- ⚡ Time-based Performance Optimization
- 📊 Temporal Pattern Analysis
- 🔄 Dynamic Load Balancing by Time
- 🎯 Regional Processing Optimization
- 📈 Time-series Performance Analytics
- 🌐 Business Hours Optimization
- ⏰ Predictive Temporal Scheduling
"""



@dataclass
class TimezoneProfile:
    """Perfil completo de zona horaria."""
    
    id: str
    name: str
    utc_offset_hours: float
    region: str
    business_hours_start: int = 9    # 9 AM
    business_hours_end: int = 18     # 6 PM
    peak_hours: List[int] = field(default_factory=lambda: [9, 14, 20])
    low_activity_hours: List[int] = field(default_factory=lambda: [2, 5, 23])
    weekend_behavior: str = "reduced"  # "reduced", "normal", "inactive"
    
    def get_current_time(self) -> datetime:
        """Obtiene tiempo actual en esta zona horaria."""
        utc_now = datetime.utcnow()
        offset = timedelta(hours=self.utc_offset_hours)
        return utc_now + offset
    
    def is_business_hours(self, dt: datetime = None) -> bool:
        """Determina si es horario de negocios."""
        if dt is None:
            dt = self.get_current_time()
        
        # Verificar día de semana (0=Monday, 6=Sunday)
        if dt.weekday() >= 5:  # Weekend
            return False
        
        return self.business_hours_start <= dt.hour < self.business_hours_end
    
    def is_peak_hour(self, dt: datetime = None) -> bool:
        """Determina si es hora pico."""
        if dt is None:
            dt = self.get_current_time()
        
        return dt.hour in self.peak_hours
    
    def get_activity_level(self, dt: datetime = None) -> str:
        """Obtiene nivel de actividad."""
        if dt is None:
            dt = self.get_current_time()
        
        if dt.hour in self.low_activity_hours:
            return "low"
        elif dt.hour in self.peak_hours:
            return "peak"
        elif self.is_business_hours(dt):
            return "business"
        else:
            return "normal"


@dataclass
class TemporalOptimization:
    """Optimización temporal específica."""
    
    operation_type: str
    optimal_timezone: str
    optimal_region: str
    processing_window: Dict[str, Any]
    performance_boost: Dict[str, float]
    confidence_score: float
    reasoning: List[str]
    alternative_options: List[Dict[str, Any]] = field(default_factory=list)


class TemporalPatternAnalyzer:
    """Analizador de patrones temporales."""
    
    def __init__(self) -> Any:
        self.usage_history = defaultdict(lambda: deque(maxlen=1000))
        self.performance_history = defaultdict(lambda: deque(maxlen=1000))
        self.pattern_cache = {}
        self.learning_enabled = True
    
    def record_usage(self, timezone: str, timestamp: datetime, metrics: Dict[str, Any]) -> None:
        """Registra uso para análisis de patrones."""
        
        usage_record = {
            "timestamp": timestamp,
            "hour": timestamp.hour,
            "day_of_week": timestamp.weekday(),
            "response_time_ms": metrics.get("response_time_ms", 0),
            "throughput": metrics.get("throughput", 0),
            "cpu_usage": metrics.get("cpu_usage", 0),
            "memory_usage": metrics.get("memory_usage", 0)
        }
        
        self.usage_history[timezone].append(usage_record)
        
        # Actualizar cache de patrones si hay suficientes datos
        if len(self.usage_history[timezone]) >= 50:
            self.pattern_cache[timezone] = self._analyze_timezone_patterns(timezone)
    
    def _analyze_timezone_patterns(self, timezone: str) -> Dict[str, Any]:
        """Analiza patrones específicos de una zona horaria."""
        
        history = list(self.usage_history[timezone])
        
        if not history:
            return {"status": "insufficient_data"}
        
        # Análisis por horas
        hourly_performance = defaultdict(list)
        for record in history:
            hourly_performance[record["hour"]].append(record["response_time_ms"])
        
        # Calcular promedios por hora
        hourly_averages = {}
        for hour, times in hourly_performance.items():
            hourly_averages[hour] = sum(times) / len(times) if times else 0
        
        # Identificar patrones
        best_hours = sorted(hourly_averages.items(), key=lambda x: x[1])[:3]
        worst_hours = sorted(hourly_averages.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Análisis de días de semana
        weekday_performance = defaultdict(list)
        for record in history:
            weekday_performance[record["day_of_week"]].append(record["response_time_ms"])
        
        weekday_averages = {}
        for day, times in weekday_performance.items():
            weekday_averages[day] = sum(times) / len(times) if times else 0
        
        return {
            "timezone": timezone,
            "total_samples": len(history),
            "best_performance_hours": [hour for hour, _ in best_hours],
            "worst_performance_hours": [hour for hour, _ in worst_hours],
            "hourly_averages": hourly_averages,
            "weekday_averages": weekday_averages,
            "overall_avg_response_ms": sum(r["response_time_ms"] for r in history) / len(history),
            "pattern_confidence": min(len(history) / 100, 1.0),
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def get_timezone_insights(self, timezone: str) -> Dict[str, Any]:
        """Obtiene insights de una zona horaria."""
        
        if timezone in self.pattern_cache:
            return self.pattern_cache[timezone]
        elif timezone in self.usage_history and len(self.usage_history[timezone]) >= 10:
            return self._analyze_timezone_patterns(timezone)
        else:
            return {"status": "insufficient_data", "timezone": timezone}
    
    def predict_optimal_window(self, timezone: str, duration_hours: int = 4) -> Dict[str, Any]:
        """Predice ventana óptima de procesamiento."""
        
        insights = self.get_timezone_insights(timezone)
        
        if insights.get("status") == "insufficient_data":
            # Valores por defecto basados en patrones comunes
            return {
                "optimal_start_hour": 9,
                "duration_hours": duration_hours,
                "confidence": 0.5,
                "reasoning": "Default business hours pattern"
            }
        
        # Encontrar ventana con mejor performance
        best_hours = insights.get("best_performance_hours", [9, 14, 20])
        
        # Seleccionar hora de inicio que permita la duración requerida
        optimal_start = best_hours[0] if best_hours else 9
        
        return {
            "optimal_start_hour": optimal_start,
            "duration_hours": duration_hours,
            "expected_performance": insights.get("hourly_averages", {}).get(optimal_start, 50),
            "confidence": insights.get("pattern_confidence", 0.7),
            "reasoning": f"Based on {insights.get('total_samples', 0)} historical samples"
        }


class TimezoneOptimizer:
    """Optimizador principal de zonas horarias."""
    
    def __init__(self) -> Any:
        self.version = "1.0.0-TIMEZONE-ULTRA"
        
        # Configurar zonas horarias principales
        self.timezones = self._initialize_timezones()
        
        # Analizador de patrones
        self.pattern_analyzer = TemporalPatternAnalyzer()
        
        # Mapeo de regiones a zonas horarias
        self.region_timezone_map = self._create_region_mapping()
        
        # Cache de optimizaciones
        self.optimization_cache = {}
        self.cache_ttl_seconds = 300  # 5 minutos
        
        # Métricas de optimización
        self.optimization_metrics = {
            "total_optimizations": 0,
            "cache_hits": 0,
            "avg_improvement_percent": 0.0,
            "successful_predictions": 0
        }
    
    def _initialize_timezones(self) -> Dict[str, TimezoneProfile]:
        """Inicializa perfiles de zonas horarias."""
        
        timezones = {}
        
        # Definir zonas horarias principales con sus características
        timezone_configs = [
            # Americas
            ("America/New_York", "Eastern Time", -5.0, "us-east", [9, 14, 20], [2, 5, 23]),
            ("America/Chicago", "Central Time", -6.0, "us-central", [9, 13, 19], [1, 4, 23]),
            ("America/Los_Angeles", "Pacific Time", -8.0, "us-west", [9, 14, 21], [2, 6, 24]),
            ("America/Sao_Paulo", "Brazil Time", -3.0, "south-america", [8, 13, 18], [1, 4, 22]),
            
            # Europe
            ("Europe/London", "GMT", 0.0, "europe-west", [9, 14, 19], [2, 5, 23]),
            ("Europe/Paris", "CET", 1.0, "europe-central", [8, 13, 18], [1, 4, 22]),
            ("Europe/Moscow", "MSK", 3.0, "europe-east", [10, 15, 20], [3, 6, 24]),
            
            # Asia-Pacific
            ("Asia/Tokyo", "JST", 9.0, "asia-northeast", [9, 13, 18], [2, 5, 23]),
            ("Asia/Shanghai", "CST", 8.0, "asia-east", [9, 14, 19], [1, 4, 22]),
            ("Asia/Singapore", "SGT", 8.0, "asia-southeast", [9, 14, 20], [2, 5, 23]),
            ("Asia/Mumbai", "IST", 5.5, "asia-south", [10, 15, 21], [3, 6, 24]),
            ("Australia/Sydney", "AEST", 10.0, "oceania", [9, 13, 18], [1, 4, 22]),
            
            # Africa & Middle East
            ("Africa/Cairo", "EET", 2.0, "africa-north", [9, 14, 19], [2, 5, 23]),
            ("Asia/Dubai", "GST", 4.0, "middle-east", [8, 13, 18], [1, 4, 22])
        ]
        
        for tz_id, name, offset, region, peak_hours, low_hours in timezone_configs:
            timezones[tz_id] = TimezoneProfile(
                id=tz_id,
                name=name,
                utc_offset_hours=offset,
                region=region,
                peak_hours=peak_hours,
                low_activity_hours=low_hours
            )
        
        return timezones
    
    def _create_region_mapping(self) -> Dict[str, List[str]]:
        """Crea mapeo de regiones a zonas horarias."""
        
        mapping = defaultdict(list)
        
        for tz_id, tz_profile in self.timezones.items():
            mapping[tz_profile.region].append(tz_id)
        
        return dict(mapping)
    
    async def optimize_by_timezone(
        self,
        operation_type: str,
        user_timezone: str = None,
        target_regions: List[str] = None,
        performance_requirements: Dict[str, Any] = None
    ) -> TemporalOptimization:
        """Optimiza operación basada en zona horaria."""
        
        # Generar clave de cache
        cache_key = f"{operation_type}_{user_timezone}_{hash(str(target_regions))}"
        
        # Verificar cache
        if cache_key in self.optimization_cache:
            cache_entry = self.optimization_cache[cache_key]
            if time.time() - cache_entry["timestamp"] < self.cache_ttl_seconds:
                self.optimization_metrics["cache_hits"] += 1
                return cache_entry["optimization"]
        
        # Realizar optimización
        optimization = await self._perform_timezone_optimization(
            operation_type,
            user_timezone,
            target_regions,
            performance_requirements or {}
        )
        
        # Cachear resultado
        self.optimization_cache[cache_key] = {
            "optimization": optimization,
            "timestamp": time.time()
        }
        
        # Actualizar métricas
        self.optimization_metrics["total_optimizations"] += 1
        
        return optimization
    
    async def _perform_timezone_optimization(
        self,
        operation_type: str,
        user_timezone: str,
        target_regions: List[str],
        performance_requirements: Dict[str, Any]
    ) -> TemporalOptimization:
        """Realiza optimización de zona horaria."""
        
        current_utc = datetime.utcnow()
        
        # Evaluar todas las opciones disponibles
        optimization_options = []
        
        # Si se especifica zona horaria de usuario, evaluarla primero
        if user_timezone and user_timezone in self.timezones:
            option = await self._evaluate_timezone_option(
                user_timezone,
                operation_type,
                current_utc,
                performance_requirements
            )
            optimization_options.append(option)
        
        # Evaluar regiones objetivo
        if target_regions:
            for region in target_regions:
                if region in self.region_timezone_map:
                    for tz_id in self.region_timezone_map[region]:
                        option = await self._evaluate_timezone_option(
                            tz_id,
                            operation_type,
                            current_utc,
                            performance_requirements
                        )
                        optimization_options.append(option)
        
        # Si no hay opciones específicas, evaluar todas las zonas principales
        if not optimization_options:
            main_timezones = [
                "America/New_York", "America/Los_Angeles", "Europe/London",
                "Asia/Tokyo", "Asia/Singapore"
            ]
            
            for tz_id in main_timezones:
                option = await self._evaluate_timezone_option(
                    tz_id,
                    operation_type,
                    current_utc,
                    performance_requirements
                )
                optimization_options.append(option)
        
        # Seleccionar mejor opción
        best_option = max(optimization_options, key=lambda x: x["score"])
        
        # Crear objeto de optimización
        optimization = TemporalOptimization(
            operation_type=operation_type,
            optimal_timezone=best_option["timezone"],
            optimal_region=best_option["region"],
            processing_window=best_option["processing_window"],
            performance_boost=best_option["performance_boost"],
            confidence_score=best_option["score"],
            reasoning=best_option["reasoning"],
            alternative_options=[opt for opt in optimization_options if opt != best_option][:3]
        )
        
        return optimization
    
    async def _evaluate_timezone_option(
        self,
        timezone_id: str,
        operation_type: str,
        current_utc: datetime,
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evalúa una opción de zona horaria."""
        
        tz_profile = self.timezones[timezone_id]
        local_time = tz_profile.get_current_time()
        
        # Factores de evaluación
        score_factors = {}
        reasoning = []
        
        # Factor 1: Horario de negocios (0-30 puntos)
        if tz_profile.is_business_hours(local_time):
            business_hours_score = 30
            reasoning.append("Currently in business hours")
        else:
            business_hours_score = 10
            reasoning.append("Outside business hours")
        
        score_factors["business_hours"] = business_hours_score
        
        # Factor 2: Nivel de actividad (0-25 puntos)
        activity_level = tz_profile.get_activity_level(local_time)
        activity_scores = {"peak": 25, "business": 20, "normal": 15, "low": 10}
        activity_score = activity_scores.get(activity_level, 15)
        
        score_factors["activity_level"] = activity_score
        reasoning.append(f"Activity level: {activity_level}")
        
        # Factor 3: Análisis histórico (0-25 puntos)
        insights = self.pattern_analyzer.get_timezone_insights(timezone_id)
        if insights.get("status") != "insufficient_data":
            historical_performance = insights.get("hourly_averages", {}).get(local_time.hour, 50)
            # Convertir tiempo de respuesta a score (menor tiempo = mayor score)
            historical_score = max(0, 25 - (historical_performance - 20) / 2)
            reasoning.append(f"Historical avg: {historical_performance:.1f}ms")
        else:
            historical_score = 15  # Score neutral
            reasoning.append("No historical data available")
        
        score_factors["historical"] = historical_score
        
        # Factor 4: Carga proyectada (0-20 puntos)
        projected_load = await self._calculate_projected_load(timezone_id, local_time)
        load_score = max(0, 20 - projected_load * 0.2)
        
        score_factors["load"] = load_score
        reasoning.append(f"Projected load: {projected_load:.1f}%")
        
        # Calcular score total
        total_score = sum(score_factors.values())
        
        # Calcular boosts de performance esperados
        performance_boost = {
            "latency_reduction_ms": max(5, (total_score / 100) * 20),
            "throughput_increase_percent": max(10, (total_score / 100) * 30),
            "cpu_efficiency_percent": max(5, (total_score / 100) * 15),
            "overall_improvement_percent": (total_score / 100) * 25
        }
        
        # Calcular ventana de procesamiento
        processing_window = {
            "start_time": local_time.isoformat(),
            "optimal_duration_hours": 2 if activity_level in ["peak", "business"] else 4,
            "expected_performance": "high" if total_score > 70 else "standard",
            "load_level": "low" if projected_load < 50 else "normal"
        }
        
        return {
            "timezone": timezone_id,
            "region": tz_profile.region,
            "score": total_score,
            "score_factors": score_factors,
            "reasoning": reasoning,
            "local_time": local_time.isoformat(),
            "activity_level": activity_level,
            "performance_boost": performance_boost,
            "processing_window": processing_window
        }
    
    async def _calculate_projected_load(self, timezone_id: str, local_time: datetime) -> float:
        """Calcula carga proyectada para una zona horaria."""
        
        tz_profile = self.timezones[timezone_id]
        
        # Factores de carga base
        base_load = 40.0
        
        # Ajustar por hora del día
        if tz_profile.is_peak_hour(local_time):
            base_load += 30
        elif tz_profile.is_business_hours(local_time):
            base_load += 20
        elif local_time.hour in tz_profile.low_activity_hours:
            base_load -= 20
        
        # Ajustar por día de semana
        if local_time.weekday() >= 5:  # Weekend
            base_load -= 15
        elif local_time.weekday() == 0:  # Monday
            base_load += 10
        
        # Variación aleatoria pequeña
        variation = random.uniform(-5, 5)
        
        return max(0, min(100, base_load + variation))
    
    async def analyze_global_optimization_opportunities(self) -> Dict[str, Any]:
        """Analiza oportunidades de optimización global."""
        
        current_utc = datetime.utcnow()
        opportunities = []
        
        # Analizar cada zona horaria
        for tz_id, tz_profile in self.timezones.items():
            local_time = tz_profile.get_current_time()
            
            # Evaluar oportunidad
            opportunity_score = 0
            factors = []
            
            # Horario de negocios
            if tz_profile.is_business_hours(local_time):
                opportunity_score += 30
                factors.append("business_hours_active")
            
            # Baja actividad = oportunidad de pre-procesamiento
            if tz_profile.get_activity_level(local_time) == "low":
                opportunity_score += 25
                factors.append("low_activity_preprocessing")
            
            # Análisis histórico
            insights = self.pattern_analyzer.get_timezone_insights(tz_id)
            if insights.get("status") != "insufficient_data":
                avg_performance = insights.get("overall_avg_response_ms", 50)
                if avg_performance < 30:  # Buen performance histórico
                    opportunity_score += 20
                    factors.append("good_historical_performance")
            
            if opportunity_score > 50:
                opportunities.append({
                    "timezone": tz_id,
                    "region": tz_profile.region,
                    "local_time": local_time.isoformat(),
                    "opportunity_score": opportunity_score,
                    "factors": factors,
                    "recommended_actions": self._generate_recommendations(tz_profile, local_time)
                })
        
        # Ordenar por score
        opportunities.sort(key=lambda x: x["opportunity_score"], reverse=True)
        
        return {
            "analysis_timestamp": current_utc.isoformat(),
            "total_opportunities": len(opportunities),
            "top_opportunities": opportunities[:5],
            "global_insights": {
                "best_regions_now": [opp["region"] for opp in opportunities[:3]],
                "avg_opportunity_score": sum(opp["opportunity_score"] for opp in opportunities) / max(len(opportunities), 1),
                "optimization_potential": "high" if opportunities and opportunities[0]["opportunity_score"] > 70 else "medium"
            }
        }
    
    def _generate_recommendations(self, tz_profile: TimezoneProfile, local_time: datetime) -> List[str]:
        """Genera recomendaciones específicas."""
        
        recommendations = []
        
        if tz_profile.is_business_hours(local_time):
            recommendations.append("Prioritize real-time processing")
            recommendations.extend(["Enable high-performance mode", "Increase cache hit rate"])
        
        if tz_profile.get_activity_level(local_time) == "low":
            recommendations.extend([
                "Schedule batch processing",
                "Perform maintenance tasks",
                "Pre-load content for peak hours"
            ])
        
        if tz_profile.is_peak_hour(local_time):
            recommendations.extend([
                "Scale up resources",
                "Enable aggressive caching",
                "Monitor performance closely"
            ])
        
        return recommendations[:3]  # Limitar a 3 recomendaciones
    
    async def get_optimization_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas de optimización."""
        
        # Calcular eficiencia de cache
        total_requests = self.optimization_metrics["total_optimizations"]
        cache_hit_rate = (self.optimization_metrics["cache_hits"] / max(total_requests, 1)) * 100
        
        # Analizar patrones de uso
        timezone_usage = defaultdict(int)
        for tz_id in self.pattern_analyzer.usage_history.keys():
            timezone_usage[tz_id] = len(self.pattern_analyzer.usage_history[tz_id])
        
        most_used_timezones = sorted(timezone_usage.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_optimizations_performed": total_requests,
            "cache_hit_rate_percent": round(cache_hit_rate, 1),
            "avg_improvement_percent": round(self.optimization_metrics["avg_improvement_percent"], 1),
            "successful_predictions": self.optimization_metrics["successful_predictions"],
            "most_used_timezones": [{"timezone": tz, "usage_count": count} for tz, count in most_used_timezones],
            "pattern_analyzer_stats": {
                "timezones_with_data": len(self.pattern_analyzer.usage_history),
                "total_data_points": sum(len(history) for history in self.pattern_analyzer.usage_history.values()),
                "pattern_cache_size": len(self.pattern_analyzer.pattern_cache)
            },
            "optimization_cache_stats": {
                "cached_optimizations": len(self.optimization_cache),
                "cache_ttl_seconds": self.cache_ttl_seconds
            }
        }
    
    async def simulate_temporal_load_test(self, duration_hours: int = 24) -> Dict[str, Any]:
        """Simula prueba de carga temporal."""
        
        print(f"🧪 Running temporal load test for {duration_hours} hours...")
        
        results = {
            "test_duration_hours": duration_hours,
            "simulated_operations": 0,
            "optimization_results": [],
            "performance_by_hour": {},
            "best_performing_timezones": [],
            "optimization_effectiveness": 0.0
        }
        
        current_utc = datetime.utcnow()
        
        # Simular operaciones cada hora
        for hour_offset in range(duration_hours):
            test_time = current_utc + timedelta(hours=hour_offset)
            
            # Simular múltiples operaciones en esta hora
            hour_results = []
            
            for operation_count in range(5):  # 5 operaciones por hora
                # Seleccionar zona horaria aleatoria para simular usuario
                test_timezone = random.choice(list(self.timezones.keys()))
                
                # Optimizar para esta operación
                optimization = await self.optimize_by_timezone(
                    "landing_page_generation",
                    test_timezone,
                    ["us-east", "us-west", "europe", "asia"]
                )
                
                # Simular métricas de performance
                simulated_metrics = {
                    "response_time_ms": random.uniform(15, 45),
                    "throughput": random.uniform(1000, 3000),
                    "cpu_usage": random.uniform(30, 80),
                    "memory_usage": random.uniform(40, 85)
                }
                
                # Registrar para análisis de patrones
                self.pattern_analyzer.record_usage(
                    optimization.optimal_timezone,
                    test_time,
                    simulated_metrics
                )
                
                hour_results.append({
                    "user_timezone": test_timezone,
                    "optimal_timezone": optimization.optimal_timezone,
                    "confidence_score": optimization.confidence_score,
                    "performance_boost": optimization.performance_boost,
                    "simulated_metrics": simulated_metrics
                })
                
                results["simulated_operations"] += 1
            
            # Calcular promedios para esta hora
            avg_confidence = sum(r["confidence_score"] for r in hour_results) / len(hour_results)
            avg_response_time = sum(r["simulated_metrics"]["response_time_ms"] for r in hour_results) / len(hour_results)
            
            results["performance_by_hour"][hour_offset] = {
                "test_time": test_time.isoformat(),
                "operations": len(hour_results),
                "avg_confidence_score": round(avg_confidence, 1),
                "avg_response_time_ms": round(avg_response_time, 2),
                "optimizations": hour_results
            }
        
        # Analizar resultados
        all_optimizations = []
        for hour_data in results["performance_by_hour"].values():
            all_optimizations.extend(hour_data["optimizations"])
        
        # Encontrar mejores zonas horarias
        timezone_performance = defaultdict(list)
        for opt in all_optimizations:
            timezone_performance[opt["optimal_timezone"]].append(opt["confidence_score"])
        
        timezone_averages = {
            tz: sum(scores) / len(scores)
            for tz, scores in timezone_performance.items()
        }
        
        results["best_performing_timezones"] = sorted(
            timezone_averages.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        # Calcular efectividad general
        total_confidence = sum(opt["confidence_score"] for opt in all_optimizations)
        results["optimization_effectiveness"] = round(total_confidence / len(all_optimizations), 1)
        
        print(f"✅ Temporal load test completed!")
        print(f"📊 Operations simulated: {results['simulated_operations']}")
        print(f"🎯 Avg optimization effectiveness: {results['optimization_effectiveness']}%")
        
        return results


# Demo del optimizador de zonas horarias
if __name__ == "__main__":
    async def demo_timezone_optimizer():
        
    """demo_timezone_optimizer function."""
print("⏰ TIMEZONE OPTIMIZER DEMO")
        print("=" * 40)
        
        optimizer = TimezoneOptimizer()
        
        # Demo 1: Optimización básica
        print("\n🎯 1. BASIC TIMEZONE OPTIMIZATION:")
        
        optimization = await optimizer.optimize_by_timezone(
            "landing_page_generation",
            "America/New_York",
            ["us-east", "us-west", "europe"]
        )
        
        print(f"✅ Operation: {optimization.operation_type}")
        print(f"🌍 Optimal timezone: {optimization.optimal_timezone}")
        print(f"🏆 Confidence score: {optimization.confidence_score:.1f}")
        print(f"⚡ Performance boost: {optimization.performance_boost}")
        print(f"🔍 Reasoning: {', '.join(optimization.reasoning[:2])}")
        
        # Demo 2: Análisis global
        print("\n🌍 2. GLOBAL OPTIMIZATION OPPORTUNITIES:")
        
        opportunities = await optimizer.analyze_global_optimization_opportunities()
        
        print(f"📊 Total opportunities: {opportunities['total_opportunities']}")
        print(f"🏆 Best regions now: {', '.join(opportunities['global_insights']['best_regions_now'])}")
        print(f"📈 Optimization potential: {opportunities['global_insights']['optimization_potential']}")
        
        print("\n🔝 TOP 3 OPPORTUNITIES:")
        for i, opp in enumerate(opportunities['top_opportunities'][:3], 1):
            print(f"  {i}. {opp['timezone']} (Score: {opp['opportunity_score']:.1f})")
            print(f"     Actions: {', '.join(opp['recommended_actions'][:2])}")
        
        # Demo 3: Métricas
        print("\n📊 3. OPTIMIZATION METRICS:")
        
        metrics = await optimizer.get_optimization_metrics()
        
        print(f"🔢 Total optimizations: {metrics['total_optimizations_performed']}")
        print(f"💾 Cache hit rate: {metrics['cache_hit_rate_percent']}%")
        print(f"📈 Avg improvement: {metrics['avg_improvement_percent']}%")
        print(f"🧠 Timezones with data: {metrics['pattern_analyzer_stats']['timezones_with_data']}")
        
        # Demo 4: Simulación corta
        print("\n🧪 4. TEMPORAL LOAD SIMULATION (2 hours):")
        
        simulation = await optimizer.simulate_temporal_load_test(duration_hours=2)
        
        print(f"⚡ Operations simulated: {simulation['simulated_operations']}")
        print(f"🎯 Optimization effectiveness: {simulation['optimization_effectiveness']}%")
        
        if simulation['best_performing_timezones']:
            best_tz, best_score = simulation['best_performing_timezones'][0]
            print(f"🏆 Best timezone: {best_tz} (Score: {best_score:.1f})")
        
        print(f"\n🎉 TIMEZONE OPTIMIZER DEMO COMPLETED!")
        print(f"⏰ System optimized for global temporal performance!")
        
    asyncio.run(demo_timezone_optimizer()) 