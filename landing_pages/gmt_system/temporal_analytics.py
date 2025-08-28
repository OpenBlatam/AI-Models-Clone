from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS = 1000

# Constants
MAX_RETRIES = 100

# Constants
TIMEOUT_SECONDS = 60

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json
import random
import statistics
from typing import Any, List, Dict, Optional
import logging
"""
📊 TEMPORAL ANALYTICS - ANALYTICS BASADOS EN TIEMPO
==================================================

Sistema ultra-avanzado de analytics que analiza patrones temporales,
performance por zonas horarias y optimización basada en tiempo.

Características:
- 📈 Time-series Performance Analytics  
- 🌍 Global Timezone Usage Patterns
- ⏰ Business Hours Impact Analysis
- 📊 Temporal Performance Trends
- 🔄 Real-time Time-based Insights
- 🎯 Peak Hours Optimization
- 📅 Seasonal Pattern Detection
- 🌐 Regional Performance Comparison
"""



@dataclass
class TemporalDataPoint:
    """Punto de datos temporal."""
    
    timestamp: datetime
    timezone: str
    region: str
    operation_type: str
    response_time_ms: float
    throughput_rps: float
    cpu_usage_percent: float
    memory_usage_percent: float
    cache_hit_rate: float
    user_count: int
    conversion_rate: float = 0.0
    error_rate: float = 0.0
    
    @property
    def hour_of_day(self) -> int:
        return self.timestamp.hour
    
    @property
    def day_of_week(self) -> int:
        return self.timestamp.weekday()  # 0=Monday, 6=Sunday
    
    @property
    def is_weekend(self) -> bool:
        return self.day_of_week >= 5
    
    @property
    def is_business_hours(self) -> bool:
        return 9 <= self.hour_of_day < 18 and not self.is_weekend


@dataclass
class TemporalTrend:
    """Tendencia temporal."""
    
    metric_name: str
    timezone: str
    trend_direction: str  # "increasing", "decreasing", "stable"
    trend_strength: float  # 0-1
    period_analyzed: str
    data_points: int
    confidence_level: float
    statistical_significance: float
    projected_values: List[float] = field(default_factory=list)


@dataclass
class PerformancePattern:
    """Patrón de performance temporal."""
    
    pattern_type: str  # "hourly", "daily", "weekly"
    timezone: str
    best_performance_windows: List[Dict[str, Any]]
    worst_performance_windows: List[Dict[str, Any]]
    average_performance: float
    peak_improvement_opportunity: float
    pattern_reliability: float
    recommendations: List[str]


class TemporalAnalytics:
    """Sistema principal de analytics temporales."""
    
    def __init__(self) -> Any:
        self.version = "1.0.0-TEMPORAL-ANALYTICS"
        
        # Almacenamiento de datos temporales
        self.data_storage = defaultdict(lambda: deque(maxlen=10000))
        
        # Cache de análisis
        self.analysis_cache = {}
        self.cache_ttl_seconds = 300
        
        # Configuración de análisis
        self.analysis_config = {
            "min_data_points_for_trend": 20,
            "confidence_threshold": 0.7,
            "pattern_detection_window_hours": 168,  # 1 semana
            "real_time_window_minutes": 30
        }
        
        # Métricas de sistema
        self.system_metrics = {
            "total_data_points": 0,
            "analytics_operations": 0,
            "patterns_detected": 0,
            "trends_identified": 0,
            "cache_hit_rate": 0.0
        }
        
        # Inicializar con datos de ejemplo
        self._initialize_sample_data()
    
    def _initialize_sample_data(self) -> None:
        """Inicializa con datos de ejemplo para demostración."""
        
        timezones = [
            "America/New_York", "America/Los_Angeles", "Europe/London",
            "Asia/Tokyo", "Asia/Singapore", "Europe/Paris"
        ]
        
        regions = {
            "America/New_York": "us-east",
            "America/Los_Angeles": "us-west", 
            "Europe/London": "europe-west",
            "Asia/Tokyo": "asia-northeast",
            "Asia/Singapore": "asia-southeast",
            "Europe/Paris": "europe-central"
        }
        
        # Generar datos de las últimas 48 horas
        base_time = datetime.utcnow() - timedelta(hours=48)
        
        for hour_offset in range(48):
            timestamp = base_time + timedelta(hours=hour_offset)
            
            for tz in timezones:
                # Simular datos realistas basados en hora local
                local_hour = (timestamp.hour + self._get_timezone_offset(tz)) % 24
                
                # Patrones realistas por hora
                base_response_time = self._calculate_base_response_time(local_hour)
                base_throughput = self._calculate_base_throughput(local_hour)
                
                data_point = TemporalDataPoint(
                    timestamp=timestamp,
                    timezone=tz,
                    region=regions[tz],
                    operation_type="landing_page_generation",
                    response_time_ms=base_response_time + random.uniform(-5, 5),
                    throughput_rps=base_throughput + random.uniform(-100, 100),
                    cpu_usage_percent=random.uniform(30, 80),
                    memory_usage_percent=random.uniform(40, 85),
                    cache_hit_rate=random.uniform(85, 98),
                    user_count=random.randint(50, 500),
                    conversion_rate=random.uniform(5, 15),
                    error_rate=random.uniform(0, 2)
                )
                
                self.add_data_point(data_point)
    
    def _get_timezone_offset(self, timezone: str) -> int:
        """Obtiene offset aproximado de zona horaria."""
        offsets = {
            "America/New_York": -5,
            "America/Los_Angeles": -8,
            "Europe/London": 0,
            "Asia/Tokyo": 9,
            "Asia/Singapore": 8,
            "Europe/Paris": 1
        }
        return offsets.get(timezone, 0)
    
    def _calculate_base_response_time(self, local_hour: int) -> float:
        """Calcula tiempo de respuesta base según hora local."""
        # Mejor performance en horas de baja actividad
        if 2 <= local_hour <= 6:  # Madrugada
            return random.uniform(18, 25)
        elif 9 <= local_hour <= 11:  # Mañana temprano
            return random.uniform(22, 30)
        elif 12 <= local_hour <= 14:  # Mediodía
            return random.uniform(28, 35)
        elif 15 <= local_hour <= 17:  # Tarde
            return random.uniform(25, 32)
        elif 18 <= local_hour <= 20:  # Noche temprana
            return random.uniform(30, 40)
        else:  # Resto del día
            return random.uniform(20, 28)
    
    def _calculate_base_throughput(self, local_hour: int) -> float:
        """Calcula throughput base según hora local."""
        # Mayor throughput en horas de alta actividad
        if 9 <= local_hour <= 17:  # Horario de negocios
            return random.uniform(1500, 2500)
        elif 18 <= local_hour <= 22:  # Noche
            return random.uniform(1000, 1800)
        else:  # Madrugada y noche tardía
            return random.uniform(500, 1200)
    
    def add_data_point(self, data_point: TemporalDataPoint) -> None:
        """Agrega punto de datos temporal."""
        
        storage_key = f"{data_point.timezone}_{data_point.operation_type}"
        self.data_storage[storage_key].append(data_point)
        self.system_metrics["total_data_points"] += 1
        
        # Invalidar cache relacionado
        self._invalidate_related_cache(data_point.timezone)
    
    def _invalidate_related_cache(self, timezone: str) -> None:
        """Invalida cache relacionado con una zona horaria."""
        keys_to_remove = [
            key for key in self.analysis_cache.keys()
            if timezone in key
        ]
        
        for key in keys_to_remove:
            del self.analysis_cache[key]
    
    async def analyze_timezone_performance(self, timezone: str, hours_back: int = 24) -> Dict[str, Any]:
        """Analiza performance de una zona horaria específica."""
        
        cache_key = f"tz_performance_{timezone}_{hours_back}"
        
        # Verificar cache
        if cache_key in self.analysis_cache:
            cache_entry = self.analysis_cache[cache_key]
            if time.time() - cache_entry["timestamp"] < self.cache_ttl_seconds:
                self.system_metrics["cache_hit_rate"] += 1
                return cache_entry["data"]
        
        # Realizar análisis
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        
        # Obtener datos relevantes
        storage_keys = [key for key in self.data_storage.keys() if timezone in key]
        all_data_points = []
        
        for key in storage_keys:
            data_points = [
                dp for dp in self.data_storage[key]
                if dp.timestamp >= cutoff_time
            ]
            all_data_points.extend(data_points)
        
        if not all_data_points:
            return {"error": "No data available for analysis"}
        
        # Análisis por horas
        hourly_analysis = self._analyze_hourly_patterns(all_data_points)
        
        # Análisis por días de semana
        weekly_analysis = self._analyze_weekly_patterns(all_data_points)
        
        # Métricas generales
        general_metrics = self._calculate_general_metrics(all_data_points)
        
        # Identificar tendencias
        trends = await self._identify_trends(all_data_points, timezone)
        
        # Generar recomendaciones
        recommendations = self._generate_performance_recommendations(
            hourly_analysis, weekly_analysis, trends
        )
        
        analysis_result = {
            "timezone": timezone,
            "analysis_period_hours": hours_back,
            "data_points_analyzed": len(all_data_points),
            "hourly_patterns": hourly_analysis,
            "weekly_patterns": weekly_analysis,
            "general_metrics": general_metrics,
            "trends": trends,
            "recommendations": recommendations,
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
        
        # Cachear resultado
        self.analysis_cache[cache_key] = {
            "data": analysis_result,
            "timestamp": time.time()
        }
        
        self.system_metrics["analytics_operations"] += 1
        
        return analysis_result
    
    def _analyze_hourly_patterns(self, data_points: List[TemporalDataPoint]) -> Dict[str, Any]:
        """Analiza patrones por horas del día."""
        
        hourly_data = defaultdict(lambda: {
            "response_times": [],
            "throughputs": [],
            "cpu_usage": [],
            "cache_hit_rates": [],
            "user_counts": []
        })
        
        # Agrupar por hora
        for dp in data_points:
            hour = dp.hour_of_day
            hourly_data[hour]["response_times"].append(dp.response_time_ms)
            hourly_data[hour]["throughputs"].append(dp.throughput_rps)
            hourly_data[hour]["cpu_usage"].append(dp.cpu_usage_percent)
            hourly_data[hour]["cache_hit_rates"].append(dp.cache_hit_rate)
            hourly_data[hour]["user_counts"].append(dp.user_count)
        
        # Calcular estadísticas por hora
        hourly_stats = {}
        for hour in range(24):
            if hour in hourly_data and hourly_data[hour]["response_times"]:
                hourly_stats[hour] = {
                    "avg_response_time_ms": statistics.mean(hourly_data[hour]["response_times"]),
                    "avg_throughput_rps": statistics.mean(hourly_data[hour]["throughputs"]),
                    "avg_cpu_usage": statistics.mean(hourly_data[hour]["cpu_usage"]),
                    "avg_cache_hit_rate": statistics.mean(hourly_data[hour]["cache_hit_rates"]),
                    "avg_users": statistics.mean(hourly_data[hour]["user_counts"]),
                    "data_points": len(hourly_data[hour]["response_times"])
                }
        
        # Identificar mejores y peores horas
        if hourly_stats:
            best_hours = sorted(
                hourly_stats.items(),
                key=lambda x: x[1]["avg_response_time_ms"]
            )[:3]
            
            worst_hours = sorted(
                hourly_stats.items(), 
                key=lambda x: x[1]["avg_response_time_ms"],
                reverse=True
            )[:3]
        else:
            best_hours = worst_hours = []
        
        return {
            "hourly_statistics": hourly_stats,
            "best_performance_hours": [{"hour": h, "avg_response_ms": s["avg_response_time_ms"]} for h, s in best_hours],
            "worst_performance_hours": [{"hour": h, "avg_response_ms": s["avg_response_time_ms"]} for h, s in worst_hours],
            "peak_usage_hours": self._identify_peak_hours(hourly_stats),
            "optimization_opportunities": self._identify_hourly_optimization_opportunities(hourly_stats)
        }
    
    def _analyze_weekly_patterns(self, data_points: List[TemporalDataPoint]) -> Dict[str, Any]:
        """Analiza patrones por días de la semana."""
        
        weekly_data = defaultdict(lambda: {
            "response_times": [],
            "throughputs": [],
            "user_counts": []
        })
        
        # Agrupar por día de semana
        for dp in data_points:
            day = dp.day_of_week
            weekly_data[day]["response_times"].append(dp.response_time_ms)
            weekly_data[day]["throughputs"].append(dp.throughput_rps)
            weekly_data[day]["user_counts"].append(dp.user_count)
        
        # Calcular estadísticas por día
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        weekly_stats = {}
        
        for day in range(7):
            if day in weekly_data and weekly_data[day]["response_times"]:
                weekly_stats[day_names[day]] = {
                    "avg_response_time_ms": statistics.mean(weekly_data[day]["response_times"]),
                    "avg_throughput_rps": statistics.mean(weekly_data[day]["throughputs"]),
                    "avg_users": statistics.mean(weekly_data[day]["user_counts"]),
                    "data_points": len(weekly_data[day]["response_times"]),
                    "is_weekend": day >= 5
                }
        
        # Comparar weekdays vs weekend
        weekday_performance = []
        weekend_performance = []
        
        for day_name, stats in weekly_stats.items():
            if stats["is_weekend"]:
                weekend_performance.append(stats["avg_response_time_ms"])
            else:
                weekday_performance.append(stats["avg_response_time_ms"])
        
        weekday_vs_weekend = {
            "weekday_avg_response_ms": statistics.mean(weekday_performance) if weekday_performance else 0,
            "weekend_avg_response_ms": statistics.mean(weekend_performance) if weekend_performance else 0,
            "weekend_performance_diff_percent": 0
        }
        
        if weekday_performance and weekend_performance:
            weekday_avg = statistics.mean(weekday_performance)
            weekend_avg = statistics.mean(weekend_performance)
            diff_percent = ((weekend_avg - weekday_avg) / weekday_avg) * 100
            weekday_vs_weekend["weekend_performance_diff_percent"] = round(diff_percent, 1)
        
        return {
            "daily_statistics": weekly_stats,
            "weekday_vs_weekend": weekday_vs_weekend,
            "best_performing_days": self._identify_best_days(weekly_stats),
            "business_hours_impact": self._analyze_business_hours_impact(data_points)
        }
    
    def _calculate_general_metrics(self, data_points: List[TemporalDataPoint]) -> Dict[str, Any]:
        """Calcula métricas generales."""
        
        if not data_points:
            return {}
        
        response_times = [dp.response_time_ms for dp in data_points]
        throughputs = [dp.throughput_rps for dp in data_points]
        cache_rates = [dp.cache_hit_rate for dp in data_points]
        
        return {
            "total_data_points": len(data_points),
            "time_range": {
                "start": min(dp.timestamp for dp in data_points).isoformat(),
                "end": max(dp.timestamp for dp in data_points).isoformat()
            },
            "response_time_stats": {
                "average_ms": round(statistics.mean(response_times), 2),
                "median_ms": round(statistics.median(response_times), 2),
                "min_ms": round(min(response_times), 2),
                "max_ms": round(max(response_times), 2),
                "std_dev": round(statistics.stdev(response_times) if len(response_times) > 1 else 0, 2)
            },
            "throughput_stats": {
                "average_rps": round(statistics.mean(throughputs), 2),
                "median_rps": round(statistics.median(throughputs), 2),
                "min_rps": round(min(throughputs), 2),
                "max_rps": round(max(throughputs), 2)
            },
            "cache_performance": {
                "average_hit_rate": round(statistics.mean(cache_rates), 2),
                "min_hit_rate": round(min(cache_rates), 2),
                "max_hit_rate": round(max(cache_rates), 2)
            }
        }
    
    async def _identify_trends(self, data_points: List[TemporalDataPoint], timezone: str) -> List[TemporalTrend]:
        """Identifica tendencias temporales."""
        
        if len(data_points) < self.analysis_config["min_data_points_for_trend"]:
            return []
        
        trends = []
        
        # Ordenar por timestamp
        sorted_data = sorted(data_points, key=lambda x: x.timestamp)
        
        # Analizar tendencia de tiempo de respuesta
        response_times = [dp.response_time_ms for dp in sorted_data]
        response_trend = self._calculate_trend(response_times)
        
        if response_trend["confidence"] >= self.analysis_config["confidence_threshold"]:
            trends.append(TemporalTrend(
                metric_name="response_time_ms",
                timezone=timezone,
                trend_direction=response_trend["direction"],
                trend_strength=response_trend["strength"],
                period_analyzed=f"{len(data_points)} data points",
                data_points=len(data_points),
                confidence_level=response_trend["confidence"],
                statistical_significance=response_trend["significance"]
            ))
        
        # Analizar tendencia de throughput
        throughputs = [dp.throughput_rps for dp in sorted_data]
        throughput_trend = self._calculate_trend(throughputs)
        
        if throughput_trend["confidence"] >= self.analysis_config["confidence_threshold"]:
            trends.append(TemporalTrend(
                metric_name="throughput_rps",
                timezone=timezone,
                trend_direction=throughput_trend["direction"],
                trend_strength=throughput_trend["strength"],
                period_analyzed=f"{len(data_points)} data points",
                data_points=len(data_points),
                confidence_level=throughput_trend["confidence"],
                statistical_significance=throughput_trend["significance"]
            ))
        
        self.system_metrics["trends_identified"] += len(trends)
        
        return trends
    
    def _calculate_trend(self, values: List[float]) -> Dict[str, Any]:
        """Calcula tendencia de una serie de valores."""
        
        if len(values) < 3:
            return {"direction": "stable", "strength": 0, "confidence": 0, "significance": 0}
        
        # Calcular diferencias consecutivas
        differences = [values[i+1] - values[i] for i in range(len(values)-1)]
        
        # Determinar dirección
        positive_changes = sum(1 for diff in differences if diff > 0)
        negative_changes = sum(1 for diff in differences if diff < 0)
        
        if positive_changes > negative_changes * 1.5:
            direction = "increasing"
        elif negative_changes > positive_changes * 1.5:
            direction = "decreasing"
        else:
            direction = "stable"
        
        # Calcular fuerza de tendencia
        avg_change = statistics.mean([abs(diff) for diff in differences])
        max_value = max(values)
        min_value = min(values)
        value_range = max_value - min_value
        
        strength = min(avg_change / (value_range + 1), 1.0) if value_range > 0 else 0
        
        # Calcular confianza
        consistency = (max(positive_changes, negative_changes) / len(differences)) if differences else 0
        confidence = min(consistency * strength, 1.0)
        
        # Significancia estadística simplificada
        significance = confidence * (len(values) / 50)  # Más datos = mayor significancia
        
        return {
            "direction": direction,
            "strength": round(strength, 3),
            "confidence": round(confidence, 3),
            "significance": round(min(significance, 1.0), 3)
        }
    
    def _identify_peak_hours(self, hourly_stats: Dict[int, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identifica horas pico basadas en uso y throughput."""
        
        peak_hours = []
        
        for hour, stats in hourly_stats.items():
            if stats["avg_users"] > 200 and stats["avg_throughput_rps"] > 1500:
                peak_hours.append({
                    "hour": hour,
                    "avg_users": round(stats["avg_users"], 1),
                    "avg_throughput_rps": round(stats["avg_throughput_rps"], 1),
                    "avg_response_time_ms": round(stats["avg_response_time_ms"], 2)
                })
        
        return sorted(peak_hours, key=lambda x: x["avg_users"], reverse=True)[:5]
    
    def _identify_hourly_optimization_opportunities(self, hourly_stats: Dict[int, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identifica oportunidades de optimización por hora."""
        
        opportunities = []
        
        for hour, stats in hourly_stats.items():
            # Oportunidad si response time alto pero CPU bajo
            if stats["avg_response_time_ms"] > 30 and stats["avg_cpu_usage"] < 60:
                opportunities.append({
                    "hour": hour,
                    "type": "cpu_underutilization",
                    "description": f"High response time ({stats['avg_response_time_ms']:.1f}ms) with low CPU usage ({stats['avg_cpu_usage']:.1f}%)",
                    "potential_improvement": "Increase parallel processing or check I/O bottlenecks"
                })
            
            # Oportunidad si cache hit rate bajo
            if stats["avg_cache_hit_rate"] < 90:
                opportunities.append({
                    "hour": hour,
                    "type": "cache_optimization",
                    "description": f"Low cache hit rate ({stats['avg_cache_hit_rate']:.1f}%)",
                    "potential_improvement": "Increase cache size or improve caching strategy"
                })
        
        return opportunities[:5]  # Top 5 opportunities
    
    def _identify_best_days(self, weekly_stats: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identifica mejores días de performance."""
        
        best_days = []
        
        for day_name, stats in weekly_stats.items():
            best_days.append({
                "day": day_name,
                "avg_response_time_ms": round(stats["avg_response_time_ms"], 2),
                "avg_throughput_rps": round(stats["avg_throughput_rps"], 1),
                "data_points": stats["data_points"]
            })
        
        return sorted(best_days, key=lambda x: x["avg_response_time_ms"])[:3]
    
    def _analyze_business_hours_impact(self, data_points: List[TemporalDataPoint]) -> Dict[str, Any]:
        """Analiza impacto de horarios de negocios."""
        
        business_hours_data = [dp for dp in data_points if dp.is_business_hours]
        off_hours_data = [dp for dp in data_points if not dp.is_business_hours]
        
        if not business_hours_data or not off_hours_data:
            return {"status": "insufficient_data"}
        
        business_avg_response = statistics.mean([dp.response_time_ms for dp in business_hours_data])
        off_hours_avg_response = statistics.mean([dp.response_time_ms for dp in off_hours_data])
        
        performance_difference = ((business_avg_response - off_hours_avg_response) / off_hours_avg_response) * 100
        
        return {
            "business_hours_avg_response_ms": round(business_avg_response, 2),
            "off_hours_avg_response_ms": round(off_hours_avg_response, 2),
            "performance_difference_percent": round(performance_difference, 1),
            "business_hours_data_points": len(business_hours_data),
            "off_hours_data_points": len(off_hours_data),
            "impact_level": "high" if abs(performance_difference) > 20 else "moderate" if abs(performance_difference) > 10 else "low"
        }
    
    def _generate_performance_recommendations(
        self,
        hourly_analysis: Dict[str, Any],
        weekly_analysis: Dict[str, Any],
        trends: List[TemporalTrend]
    ) -> List[Dict[str, Any]]:
        """Genera recomendaciones de performance."""
        
        recommendations = []
        
        # Recomendaciones basadas en análisis horario
        if hourly_analysis.get("optimization_opportunities"):
            for opp in hourly_analysis["optimization_opportunities"][:2]:
                recommendations.append({
                    "type": "hourly_optimization",
                    "priority": "high",
                    "description": opp["description"],
                    "action": opp["potential_improvement"],
                    "target_hour": opp["hour"]
                })
        
        # Recomendaciones basadas en análisis semanal
        business_impact = weekly_analysis.get("business_hours_impact", {})
        if business_impact.get("impact_level") == "high":
            recommendations.append({
                "type": "business_hours_optimization",
                "priority": "high",
                "description": f"Business hours show {business_impact['performance_difference_percent']:.1f}% performance difference",
                "action": "Implement business hours scaling and optimization"
            })
        
        # Recomendaciones basadas en tendencias
        for trend in trends:
            if trend.trend_direction == "decreasing" and trend.metric_name == "response_time_ms":
                recommendations.append({
                    "type": "performance_improvement",
                    "priority": "medium",
                    "description": f"Response time showing improving trend (confidence: {trend.confidence_level:.1%})",
                    "action": "Continue current optimization strategies"
                })
            elif trend.trend_direction == "increasing" and trend.metric_name == "response_time_ms":
                recommendations.append({
                    "type": "performance_degradation",
                    "priority": "high",
                    "description": f"Response time showing degrading trend (confidence: {trend.confidence_level:.1%})",
                    "action": "Investigate and address performance degradation causes"
                })
        
        return recommendations[:5]  # Top 5 recommendations
    
    async def get_global_temporal_insights(self) -> Dict[str, Any]:
        """Obtiene insights temporales globales."""
        
        all_timezones = set()
        for key in self.data_storage.keys():
            tz = key.split("_")[0]
            all_timezones.add(tz)
        
        global_insights = {
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "total_timezones_analyzed": len(all_timezones),
            "system_metrics": self.system_metrics,
            "timezone_performance_comparison": {},
            "global_patterns": {},
            "optimization_summary": {}
        }
        
        # Comparar performance entre zonas horarias
        timezone_performance = {}
        
        for tz in list(all_timezones)[:5]:  # Analizar top 5 para demo
            analysis = await self.analyze_timezone_performance(tz, hours_back=24)
            if "general_metrics" in analysis:
                timezone_performance[tz] = {
                    "avg_response_time_ms": analysis["general_metrics"]["response_time_stats"]["average_ms"],
                    "avg_throughput_rps": analysis["general_metrics"]["throughput_stats"]["average_rps"],
                    "data_points": analysis["data_points_analyzed"],
                    "trends_count": len(analysis.get("trends", []))
                }
        
        global_insights["timezone_performance_comparison"] = timezone_performance
        
        # Patrones globales
        if timezone_performance:
            best_tz = min(timezone_performance.items(), key=lambda x: x[1]["avg_response_time_ms"])
            worst_tz = max(timezone_performance.items(), key=lambda x: x[1]["avg_response_time_ms"])
            
            global_insights["global_patterns"] = {
                "best_performing_timezone": {
                    "timezone": best_tz[0],
                    "avg_response_time_ms": best_tz[1]["avg_response_time_ms"]
                },
                "worst_performing_timezone": {
                    "timezone": worst_tz[0],
                    "avg_response_time_ms": worst_tz[1]["avg_response_time_ms"]
                },
                "performance_variance": round(worst_tz[1]["avg_response_time_ms"] - best_tz[1]["avg_response_time_ms"], 2)
            }
        
        # Resumen de optimización
        total_recommendations = 0
        for tz in list(all_timezones)[:3]:  # Sample 3 timezones
            analysis = await self.analyze_timezone_performance(tz, hours_back=12)
            total_recommendations += len(analysis.get("recommendations", []))
        
        global_insights["optimization_summary"] = {
            "total_optimization_opportunities": total_recommendations,
            "avg_opportunities_per_timezone": round(total_recommendations / max(len(all_timezones), 1), 1),
            "optimization_potential": "high" if total_recommendations > 10 else "medium"
        }
        
        return global_insights
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtiene estado del sistema de analytics."""
        
        cache_hit_rate = 0
        if self.system_metrics["analytics_operations"] > 0:
            cache_hit_rate = (self.system_metrics["cache_hit_rate"] / self.system_metrics["analytics_operations"]) * 100
        
        return {
            "version": self.version,
            "system_metrics": {
                **self.system_metrics,
                "cache_hit_rate_percent": round(cache_hit_rate, 1)
            },
            "data_storage_status": {
                "total_storage_keys": len(self.data_storage),
                "avg_data_points_per_key": round(
                    sum(len(deque_data) for deque_data in self.data_storage.values()) / max(len(self.data_storage), 1),
                    1
                ),
                "oldest_data_timestamp": self._get_oldest_timestamp(),
                "newest_data_timestamp": self._get_newest_timestamp()
            },
            "analysis_cache_status": {
                "cached_analyses": len(self.analysis_cache),
                "cache_ttl_seconds": self.cache_ttl_seconds
            },
            "configuration": self.analysis_config
        }
    
    def _get_oldest_timestamp(self) -> str:
        """Obtiene timestamp más antiguo."""
        oldest = None
        
        for deque_data in self.data_storage.values():
            if deque_data:
                first_timestamp = deque_data[0].timestamp
                if oldest is None or first_timestamp < oldest:
                    oldest = first_timestamp
        
        return oldest.isoformat() if oldest else "N/A"
    
    def _get_newest_timestamp(self) -> str:
        """Obtiene timestamp más reciente."""
        newest = None
        
        for deque_data in self.data_storage.values():
            if deque_data:
                last_timestamp = deque_data[-1].timestamp
                if newest is None or last_timestamp > newest:
                    newest = last_timestamp
        
        return newest.isoformat() if newest else "N/A"


# Demo del sistema de analytics temporales
if __name__ == "__main__":
    async def demo_temporal_analytics():
        
    """demo_temporal_analytics function."""
print("📊 TEMPORAL ANALYTICS DEMO")
        print("=" * 40)
        
        analytics = TemporalAnalytics()
        
        # Demo 1: Análisis de zona horaria específica
        print("\n🌍 1. TIMEZONE PERFORMANCE ANALYSIS:")
        
        tz_analysis = await analytics.analyze_timezone_performance("America/New_York", hours_back=24)
        
        print(f"🕐 Timezone: {tz_analysis['timezone']}")
        print(f"📊 Data points: {tz_analysis['data_points_analyzed']}")
        print(f"⏱️ Avg response time: {tz_analysis['general_metrics']['response_time_stats']['average_ms']:.1f}ms")
        print(f"🚀 Avg throughput: {tz_analysis['general_metrics']['throughput_stats']['average_rps']:.1f} rps")
        
        # Mejores horas
        if tz_analysis['hourly_patterns']['best_performance_hours']:
            best_hours = tz_analysis['hourly_patterns']['best_performance_hours'][:3]
            print(f"🏆 Best hours: {', '.join([str(h['hour']) + ':00' for h in best_hours])}")
        
        # Tendencias
        if tz_analysis['trends']:
            for trend in tz_analysis['trends']:
                print(f"📈 {trend.metric_name}: {trend.trend_direction} (confidence: {trend.confidence_level:.1%})")
        
        # Demo 2: Insights globales
        print("\n🌐 2. GLOBAL TEMPORAL INSIGHTS:")
        
        global_insights = await analytics.get_global_temporal_insights()
        
        print(f"🌍 Timezones analyzed: {global_insights['total_timezones_analyzed']}")
        print(f"📊 Total data points: {global_insights['system_metrics']['total_data_points']:,}")
        print(f"🔍 Analytics operations: {global_insights['system_metrics']['analytics_operations']}")
        
        # Comparación de performance
        if global_insights['timezone_performance_comparison']:
            print(f"\n📈 TIMEZONE PERFORMANCE COMPARISON:")
            for tz, metrics in list(global_insights['timezone_performance_comparison'].items())[:3]:
                print(f"  🌍 {tz}: {metrics['avg_response_time_ms']:.1f}ms avg response")
        
        # Patrones globales
        if global_insights['global_patterns']:
            patterns = global_insights['global_patterns']
            print(f"\n🏆 GLOBAL PATTERNS:")
            print(f"  ✅ Best: {patterns['best_performing_timezone']['timezone']} ({patterns['best_performing_timezone']['avg_response_time_ms']:.1f}ms)")
            print(f"  ⚠️ Needs improvement: {patterns['worst_performing_timezone']['timezone']} ({patterns['worst_performing_timezone']['avg_response_time_ms']:.1f}ms)")
            print(f"  📊 Variance: {patterns['performance_variance']:.1f}ms")
        
        # Demo 3: Estado del sistema
        print("\n⚙️ 3. SYSTEM STATUS:")
        
        status = analytics.get_system_status()
        
        print(f"📦 Version: {status['version']}")
        print(f"💾 Storage keys: {status['data_storage_status']['total_storage_keys']}")
        print(f"📈 Cache hit rate: {status['system_metrics']['cache_hit_rate_percent']:.1f}%")
        print(f"⏰ Data range: {status['data_storage_status']['oldest_data_timestamp'][:10]} to {status['data_storage_status']['newest_data_timestamp'][:10]}")
        
        print(f"\n🎉 TEMPORAL ANALYTICS DEMO COMPLETED!")
        print(f"📊 Advanced time-based insights generated!")
        
    asyncio.run(demo_temporal_analytics()) 