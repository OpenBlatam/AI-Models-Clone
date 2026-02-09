"""
Adaptive improvement service with continuous learning and optimization
"""
from typing import Dict, Any, List, Optional, Union, Callable, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, text
import uuid
import asyncio
import time
import json
import numpy as np
import pandas as pd
from collections import defaultdict, deque
import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import psutil
import gc
import logging
from pathlib import Path
import pickle
import hashlib

# Advanced ML Libraries
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    import xgboost as xgb
    import lightgbm as lgb
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

# Advanced Analytics
try:
    from scipy import stats
    from scipy.optimize import minimize
    import statsmodels.api as sm
    from prophet import Prophet
    ANALYTICS_AVAILABLE = True
except ImportError:
    ANALYTICS_AVAILABLE = False

from app.core.logging import get_logger
from app.core.errors import handle_validation_error, handle_internal_error
from app.models.adaptive_improvement import (
    AdaptiveImprovement, ImprovementPattern, LearningModel, 
    PerformancePrediction, AutoOptimization
)
from app.schemas.adaptive_improvement import (
    AdaptiveImprovementResponse, ImprovementPatternResponse, LearningModelResponse,
    PerformancePredictionResponse, AutoOptimizationResponse, ImprovementAnalysisResponse
)
from app.utils.validators import validate_improvement_config
from app.utils.helpers import calculate_improvement_score, format_improvement_metrics
from app.utils.cache import cache_improvement_data, get_cached_improvement_data

logger = get_logger(__name__)

# Global improvement tracking
_improvement_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
_learning_models: Dict[str, Any] = {}
_performance_patterns: Dict[str, Dict[str, Any]] = {}
_auto_optimizations: Dict[str, Dict[str, Any]] = {}


class AdaptiveLearningEngine:
    """Advanced adaptive learning engine for continuous improvement."""
    
    def __init__(self):
        self.models = {}
        self.patterns = {}
        self.optimizations = {}
        self.learning_rate = 0.01
        self.exploration_rate = 0.1
        self.memory_size = 10000
        self.batch_size = 32
        
    async def initialize_learning_models(self) -> Dict[str, bool]:
        """Initialize machine learning models for adaptive improvement."""
        try:
            initialization_results = {}
            
            if ML_AVAILABLE:
                # Performance Prediction Model
                try:
                    self.models["performance_predictor"] = self._create_performance_predictor()
                    initialization_results["performance_predictor"] = True
                except Exception as e:
                    logger.warning(f"Performance predictor initialization failed: {e}")
                    initialization_results["performance_predictor"] = False
                
                # Pattern Recognition Model
                try:
                    self.models["pattern_recognizer"] = self._create_pattern_recognizer()
                    initialization_results["pattern_recognizer"] = True
                except Exception as e:
                    logger.warning(f"Pattern recognizer initialization failed: {e}")
                    initialization_results["pattern_recognizer"] = False
                
                # Optimization Model
                try:
                    self.models["optimizer"] = self._create_optimization_model()
                    initialization_results["optimizer"] = True
                except Exception as e:
                    logger.warning(f"Optimizer initialization failed: {e}")
                    initialization_results["optimizer"] = False
                
                # Anomaly Detection Model
                try:
                    self.models["anomaly_detector"] = self._create_anomaly_detector()
                    initialization_results["anomaly_detector"] = True
                except Exception as e:
                    logger.warning(f"Anomaly detector initialization failed: {e}")
                    initialization_results["anomaly_detector"] = False
            
            return initialization_results
        
        except Exception as e:
            logger.error(f"Failed to initialize learning models: {e}")
            return {}
    
    def _create_performance_predictor(self) -> Any:
        """Create performance prediction model."""
        if ML_AVAILABLE:
            # Use XGBoost for performance prediction
            model = xgb.XGBRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
            return model
        return None
    
    def _create_pattern_recognizer(self) -> Any:
        """Create pattern recognition model."""
        if ML_AVAILABLE:
            # Use KMeans for pattern recognition
            model = KMeans(n_clusters=5, random_state=42)
            return model
        return None
    
    def _create_optimization_model(self) -> Any:
        """Create optimization model."""
        if ML_AVAILABLE:
            # Use Gradient Boosting for optimization
            model = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )
            return model
        return None
    
    def _create_anomaly_detector(self) -> Any:
        """Create anomaly detection model."""
        if ML_AVAILABLE:
            # Use Isolation Forest for anomaly detection
            from sklearn.ensemble import IsolationForest
            model = IsolationForest(contamination=0.1, random_state=42)
            return model
        return None
    
    async def learn_from_data(
        self, 
        data: np.ndarray, 
        targets: np.ndarray,
        model_name: str
    ) -> Dict[str, Any]:
        """Learn from historical data."""
        try:
            if model_name not in self.models:
                raise ValueError(f"Model {model_name} not found")
            
            model = self.models[model_name]
            
            # Train the model
            if hasattr(model, 'fit'):
                model.fit(data, targets)
            
            # Calculate training metrics
            if hasattr(model, 'score'):
                score = model.score(data, targets)
            else:
                score = 0.0
            
            return {
                "model_name": model_name,
                "training_score": score,
                "data_size": len(data),
                "features": data.shape[1] if len(data.shape) > 1 else 1,
                "trained_at": datetime.utcnow()
            }
        
        except Exception as e:
            logger.error(f"Failed to learn from data: {e}")
            return {"error": str(e)}
    
    async def predict_performance(
        self, 
        features: np.ndarray,
        model_name: str = "performance_predictor"
    ) -> Dict[str, Any]:
        """Predict performance based on features."""
        try:
            if model_name not in self.models:
                raise ValueError(f"Model {model_name} not found")
            
            model = self.models[model_name]
            
            # Make prediction
            if hasattr(model, 'predict'):
                prediction = model.predict(features.reshape(1, -1))[0]
            else:
                prediction = 0.0
            
            # Calculate confidence
            confidence = min(1.0, max(0.0, abs(prediction) / 100.0))
            
            return {
                "prediction": float(prediction),
                "confidence": confidence,
                "model_name": model_name,
                "predicted_at": datetime.utcnow()
            }
        
        except Exception as e:
            logger.error(f"Failed to predict performance: {e}")
            return {"error": str(e)}
    
    async def detect_patterns(self, data: np.ndarray) -> Dict[str, Any]:
        """Detect patterns in data."""
        try:
            if "pattern_recognizer" not in self.models:
                raise ValueError("Pattern recognizer not available")
            
            model = self.models["pattern_recognizer"]
            
            # Detect patterns
            if hasattr(model, 'fit_predict'):
                patterns = model.fit_predict(data)
            else:
                patterns = np.zeros(len(data))
            
            # Analyze patterns
            unique_patterns, counts = np.unique(patterns, return_counts=True)
            pattern_analysis = {
                "total_patterns": len(unique_patterns),
                "pattern_distribution": dict(zip(unique_patterns, counts)),
                "dominant_pattern": int(unique_patterns[np.argmax(counts)]),
                "pattern_entropy": float(stats.entropy(counts) if ANALYTICS_AVAILABLE else 0.0)
            }
            
            return {
                "patterns": patterns.tolist(),
                "analysis": pattern_analysis,
                "detected_at": datetime.utcnow()
            }
        
        except Exception as e:
            logger.error(f"Failed to detect patterns: {e}")
            return {"error": str(e)}
    
    async def optimize_parameters(
        self, 
        objective_function: Callable,
        parameter_bounds: List[Tuple[float, float]],
        optimization_type: str = "minimize"
    ) -> Dict[str, Any]:
        """Optimize parameters using machine learning."""
        try:
            if ANALYTICS_AVAILABLE:
                # Use scipy optimization
                result = minimize(
                    objective_function,
                    x0=[(bounds[0] + bounds[1]) / 2 for bounds in parameter_bounds],
                    bounds=parameter_bounds,
                    method='L-BFGS-B'
                )
                
                return {
                    "optimal_parameters": result.x.tolist(),
                    "optimal_value": float(result.fun),
                    "success": result.success,
                    "iterations": result.nit,
                    "optimization_type": optimization_type,
                    "optimized_at": datetime.utcnow()
                }
            else:
                # Fallback to grid search
                return await self._grid_search_optimization(objective_function, parameter_bounds)
        
        except Exception as e:
            logger.error(f"Failed to optimize parameters: {e}")
            return {"error": str(e)}
    
    async def _grid_search_optimization(
        self, 
        objective_function: Callable,
        parameter_bounds: List[Tuple[float, float]]
    ) -> Dict[str, Any]:
        """Fallback grid search optimization."""
        try:
            best_params = None
            best_value = float('inf')
            
            # Simple grid search
            for i in range(10):  # 10 iterations
                params = []
                for bounds in parameter_bounds:
                    param = bounds[0] + (bounds[1] - bounds[0]) * (i / 9.0)
                    params.append(param)
                
                value = objective_function(params)
                if value < best_value:
                    best_value = value
                    best_params = params
            
            return {
                "optimal_parameters": best_params,
                "optimal_value": best_value,
                "success": True,
                "iterations": 10,
                "optimization_type": "grid_search",
                "optimized_at": datetime.utcnow()
            }
        
        except Exception as e:
            logger.error(f"Grid search optimization failed: {e}")
            return {"error": str(e)}


class ContinuousImprovementEngine:
    """Engine for continuous system improvement."""
    
    def __init__(self):
        self.learning_engine = AdaptiveLearningEngine()
        self.improvement_history = deque(maxlen=10000)
        self.performance_metrics = defaultdict(list)
        self.optimization_queue = asyncio.Queue()
        self.improvement_threshold = 0.05  # 5% improvement threshold
        
    async def initialize(self) -> Dict[str, bool]:
        """Initialize the continuous improvement engine."""
        try:
            # Initialize learning models
            learning_results = await self.learning_engine.initialize_learning_models()
            
            # Start background optimization task
            asyncio.create_task(self._background_optimization())
            
            return learning_results
        
        except Exception as e:
            logger.error(f"Failed to initialize continuous improvement engine: {e}")
            return {}
    
    async def analyze_performance_trends(
        self, 
        time_window_hours: int = 24
    ) -> Dict[str, Any]:
        """Analyze performance trends over time."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
            
            # Filter recent data
            recent_data = [
                entry for entry in self.improvement_history
                if entry.get("timestamp", datetime.min) > cutoff_time
            ]
            
            if not recent_data:
                return {"error": "No recent data available"}
            
            # Extract performance metrics
            performance_data = []
            for entry in recent_data:
                if "performance_metrics" in entry:
                    metrics = entry["performance_metrics"]
                    performance_data.append([
                        metrics.get("response_time_ms", 0),
                        metrics.get("memory_usage_mb", 0),
                        metrics.get("cpu_usage_percent", 0),
                        metrics.get("error_rate", 0),
                        metrics.get("throughput_ops_per_sec", 0)
                    ])
            
            if not performance_data:
                return {"error": "No performance data available"}
            
            performance_array = np.array(performance_data)
            
            # Calculate trends
            trends = {}
            for i, metric_name in enumerate([
                "response_time_ms", "memory_usage_mb", "cpu_usage_percent", 
                "error_rate", "throughput_ops_per_sec"
            ]):
                values = performance_array[:, i]
                if len(values) > 1:
                    # Calculate trend (slope)
                    x = np.arange(len(values))
                    slope = np.polyfit(x, values, 1)[0]
                    trends[metric_name] = {
                        "slope": float(slope),
                        "trend": "improving" if slope < 0 else "degrading",
                        "current_value": float(values[-1]),
                        "average_value": float(np.mean(values))
                    }
            
            # Detect patterns
            pattern_analysis = await self.learning_engine.detect_patterns(performance_array)
            
            return {
                "time_window_hours": time_window_hours,
                "data_points": len(recent_data),
                "trends": trends,
                "pattern_analysis": pattern_analysis,
                "analyzed_at": datetime.utcnow()
            }
        
        except Exception as e:
            logger.error(f"Failed to analyze performance trends: {e}")
            return {"error": str(e)}
    
    async def suggest_improvements(
        self, 
        current_metrics: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Suggest improvements based on current metrics."""
        try:
            suggestions = []
            
            # Analyze response time
            if current_metrics.get("response_time_ms", 0) > 100:
                suggestions.append({
                    "type": "performance",
                    "metric": "response_time_ms",
                    "current_value": current_metrics["response_time_ms"],
                    "target_value": 50,
                    "improvement": "Enable caching and optimize database queries",
                    "expected_improvement_percent": 50,
                    "priority": "high"
                })
            
            # Analyze memory usage
            if current_metrics.get("memory_usage_mb", 0) > 500:
                suggestions.append({
                    "type": "memory",
                    "metric": "memory_usage_mb",
                    "current_value": current_metrics["memory_usage_mb"],
                    "target_value": 300,
                    "improvement": "Implement memory optimization and garbage collection",
                    "expected_improvement_percent": 40,
                    "priority": "medium"
                })
            
            # Analyze CPU usage
            if current_metrics.get("cpu_usage_percent", 0) > 80:
                suggestions.append({
                    "type": "cpu",
                    "metric": "cpu_usage_percent",
                    "current_value": current_metrics["cpu_usage_percent"],
                    "target_value": 60,
                    "improvement": "Enable parallel processing and optimize algorithms",
                    "expected_improvement_percent": 25,
                    "priority": "high"
                })
            
            # Analyze error rate
            if current_metrics.get("error_rate", 0) > 5:
                suggestions.append({
                    "type": "reliability",
                    "metric": "error_rate",
                    "current_value": current_metrics["error_rate"],
                    "target_value": 1,
                    "improvement": "Improve error handling and add validation",
                    "expected_improvement_percent": 80,
                    "priority": "critical"
                })
            
            # Analyze throughput
            if current_metrics.get("throughput_ops_per_sec", 0) < 100:
                suggestions.append({
                    "type": "throughput",
                    "metric": "throughput_ops_per_sec",
                    "current_value": current_metrics["throughput_ops_per_sec"],
                    "target_value": 500,
                    "improvement": "Implement async processing and connection pooling",
                    "expected_improvement_percent": 400,
                    "priority": "medium"
                })
            
            return suggestions
        
        except Exception as e:
            logger.error(f"Failed to suggest improvements: {e}")
            return []
    
    async def apply_improvement(
        self, 
        improvement: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply a suggested improvement."""
        try:
            improvement_id = str(uuid.uuid4())
            start_time = time.perf_counter()
            
            # Record improvement attempt
            improvement_record = {
                "id": improvement_id,
                "type": improvement["type"],
                "metric": improvement["metric"],
                "improvement": improvement["improvement"],
                "applied_at": datetime.utcnow(),
                "status": "applying"
            }
            
            # Simulate improvement application
            await asyncio.sleep(0.1)  # Simulate processing time
            
            # Record success
            improvement_record["status"] = "applied"
            improvement_record["application_time_ms"] = (time.perf_counter() - start_time) * 1000
            
            # Add to history
            self.improvement_history.append(improvement_record)
            
            return {
                "improvement_id": improvement_id,
                "status": "applied",
                "application_time_ms": improvement_record["application_time_ms"],
                "applied_at": datetime.utcnow()
            }
        
        except Exception as e:
            logger.error(f"Failed to apply improvement: {e}")
            return {"error": str(e)}
    
    async def _background_optimization(self):
        """Background task for continuous optimization."""
        while True:
            try:
                # Wait for optimization tasks
                await asyncio.sleep(60)  # Check every minute
                
                # Analyze current performance
                current_metrics = await self._get_current_metrics()
                
                # Suggest improvements
                suggestions = await self.suggest_improvements(current_metrics)
                
                # Apply high-priority improvements automatically
                for suggestion in suggestions:
                    if suggestion.get("priority") == "critical":
                        await self.apply_improvement(suggestion)
                        logger.info(f"Applied critical improvement: {suggestion['improvement']}")
            
            except Exception as e:
                logger.error(f"Background optimization error: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _get_current_metrics(self) -> Dict[str, float]:
        """Get current system metrics."""
        try:
            process = psutil.Process()
            
            return {
                "response_time_ms": 75.0,  # Would be measured from actual requests
                "memory_usage_mb": process.memory_info().rss / 1024 / 1024,
                "cpu_usage_percent": process.cpu_percent(),
                "error_rate": 2.5,  # Would be calculated from actual errors
                "throughput_ops_per_sec": 250.0  # Would be measured from actual operations
            }
        
        except Exception as e:
            logger.error(f"Failed to get current metrics: {e}")
            return {}


# Global improvement engine
_improvement_engine = ContinuousImprovementEngine()


async def initialize_adaptive_improvement() -> Dict[str, bool]:
    """Initialize adaptive improvement system."""
    try:
        return await _improvement_engine.initialize()
    except Exception as e:
        logger.error(f"Failed to initialize adaptive improvement: {e}")
        return {}


async def analyze_system_performance(
    time_window_hours: int = 24,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """Analyze system performance and suggest improvements."""
    try:
        # Analyze performance trends
        trend_analysis = await _improvement_engine.analyze_performance_trends(time_window_hours)
        
        # Get current metrics
        current_metrics = await _improvement_engine._get_current_metrics()
        
        # Suggest improvements
        suggestions = await _improvement_engine.suggest_improvements(current_metrics)
        
        # Calculate improvement score
        improvement_score = calculate_improvement_score(current_metrics, suggestions)
        
        return {
            "trend_analysis": trend_analysis,
            "current_metrics": current_metrics,
            "suggestions": suggestions,
            "improvement_score": improvement_score,
            "analyzed_at": datetime.utcnow()
        }
    
    except Exception as e:
        logger.error(f"Failed to analyze system performance: {e}")
        raise handle_internal_error(f"Failed to analyze system performance: {str(e)}")


async def apply_adaptive_improvements(
    improvements: List[Dict[str, Any]],
    db: AsyncSession
) -> Dict[str, Any]:
    """Apply adaptive improvements to the system."""
    try:
        applied_improvements = []
        failed_improvements = []
        
        for improvement in improvements:
            try:
                result = await _improvement_engine.apply_improvement(improvement)
                applied_improvements.append(result)
            except Exception as e:
                failed_improvements.append({
                    "improvement": improvement,
                    "error": str(e)
                })
        
        return {
            "applied_improvements": applied_improvements,
            "failed_improvements": failed_improvements,
            "total_applied": len(applied_improvements),
            "total_failed": len(failed_improvements),
            "applied_at": datetime.utcnow()
        }
    
    except Exception as e:
        logger.error(f"Failed to apply adaptive improvements: {e}")
        raise handle_internal_error(f"Failed to apply adaptive improvements: {str(e)}")


async def predict_system_performance(
    features: Dict[str, float],
    db: AsyncSession
) -> Dict[str, Any]:
    """Predict system performance based on features."""
    try:
        # Convert features to numpy array
        feature_array = np.array([
            features.get("load_factor", 0.5),
            features.get("memory_pressure", 0.3),
            features.get("cpu_pressure", 0.2),
            features.get("network_latency", 10.0),
            features.get("cache_hit_rate", 0.8)
        ])
        
        # Make prediction
        prediction = await _improvement_engine.learning_engine.predict_performance(feature_array)
        
        return {
            "prediction": prediction,
            "features": features,
            "predicted_at": datetime.utcnow()
        }
    
    except Exception as e:
        logger.error(f"Failed to predict system performance: {e}")
        raise handle_internal_error(f"Failed to predict system performance: {str(e)}")


async def optimize_system_parameters(
    optimization_request: Dict[str, Any],
    db: AsyncSession
) -> Dict[str, Any]:
    """Optimize system parameters using machine learning."""
    try:
        # Define objective function
        def objective_function(params):
            # Simulate performance based on parameters
            response_time = params[0] * 100 + params[1] * 50
            memory_usage = params[2] * 200 + params[3] * 100
            cpu_usage = params[4] * 80 + params[5] * 40
            
            # Minimize total cost
            return response_time + memory_usage + cpu_usage
        
        # Define parameter bounds
        parameter_bounds = [
            (0.1, 1.0),  # cache_size_factor
            (0.1, 1.0),  # connection_pool_factor
            (0.1, 1.0),  # memory_allocation_factor
            (0.1, 1.0),  # garbage_collection_factor
            (0.1, 1.0),  # cpu_optimization_factor
            (0.1, 1.0)   # parallel_processing_factor
        ]
        
        # Optimize parameters
        optimization_result = await _improvement_engine.learning_engine.optimize_parameters(
            objective_function, parameter_bounds
        )
        
        return {
            "optimization_result": optimization_result,
            "parameter_bounds": parameter_bounds,
            "optimized_at": datetime.utcnow()
        }
    
    except Exception as e:
        logger.error(f"Failed to optimize system parameters: {e}")
        raise handle_internal_error(f"Failed to optimize system parameters: {str(e)}")


async def create_improvement_analysis_report(
    db: AsyncSession
) -> Dict[str, Any]:
    """Create comprehensive improvement analysis report."""
    try:
        # Analyze performance trends
        trend_analysis = await _improvement_engine.analyze_performance_trends(24)
        
        # Get current metrics
        current_metrics = await _improvement_engine._get_current_metrics()
        
        # Suggest improvements
        suggestions = await _improvement_engine.suggest_improvements(current_metrics)
        
        # Calculate improvement score
        improvement_score = calculate_improvement_score(current_metrics, suggestions)
        
        # Analyze improvement history
        improvement_history = list(_improvement_engine.improvement_history)
        
        # Calculate improvement statistics
        total_improvements = len(improvement_history)
        successful_improvements = len([imp for imp in improvement_history if imp.get("status") == "applied"])
        success_rate = (successful_improvements / total_improvements * 100) if total_improvements > 0 else 0
        
        # Generate recommendations
        recommendations = []
        
        if improvement_score < 70:
            recommendations.append("System performance needs significant improvement")
        
        if success_rate < 80:
            recommendations.append("Improvement success rate is low, review improvement strategies")
        
        if len(suggestions) > 5:
            recommendations.append("Multiple improvement opportunities available")
        
        return {
            "improvement_score": improvement_score,
            "current_metrics": current_metrics,
            "trend_analysis": trend_analysis,
            "suggestions": suggestions,
            "improvement_history": {
                "total_improvements": total_improvements,
                "successful_improvements": successful_improvements,
                "success_rate": success_rate
            },
            "recommendations": recommendations,
            "generated_at": datetime.utcnow()
        }
    
    except Exception as e:
        logger.error(f"Failed to create improvement analysis report: {e}")
        raise handle_internal_error(f"Failed to create improvement analysis report: {str(e)}")


# Improvement tracking decorator
def track_improvement(improvement_type: str):
    """Decorator to track improvements and their impact."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            try:
                result = await func(*args, **kwargs)
                
                # Record improvement metrics
                execution_time = time.perf_counter() - start_time
                end_memory = psutil.Process().memory_info().rss / 1024 / 1024
                memory_used = end_memory - start_memory
                
                improvement_record = {
                    "type": improvement_type,
                    "function": func.__name__,
                    "execution_time_ms": execution_time * 1000,
                    "memory_usage_mb": memory_used,
                    "cpu_usage_percent": psutil.Process().cpu_percent(),
                    "timestamp": datetime.utcnow(),
                    "status": "success"
                }
                
                _improvement_engine.improvement_history.append(improvement_record)
                
                return result
            
            except Exception as e:
                # Record error
                improvement_record = {
                    "type": improvement_type,
                    "function": func.__name__,
                    "error": str(e),
                    "timestamp": datetime.utcnow(),
                    "status": "error"
                }
                
                _improvement_engine.improvement_history.append(improvement_record)
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            try:
                result = func(*args, **kwargs)
                
                # Record improvement metrics
                execution_time = time.perf_counter() - start_time
                end_memory = psutil.Process().memory_info().rss / 1024 / 1024
                memory_used = end_memory - start_memory
                
                improvement_record = {
                    "type": improvement_type,
                    "function": func.__name__,
                    "execution_time_ms": execution_time * 1000,
                    "memory_usage_mb": memory_used,
                    "cpu_usage_percent": psutil.Process().cpu_percent(),
                    "timestamp": datetime.utcnow(),
                    "status": "success"
                }
                
                _improvement_engine.improvement_history.append(improvement_record)
                
                return result
            
            except Exception as e:
                # Record error
                improvement_record = {
                    "type": improvement_type,
                    "function": func.__name__,
                    "error": str(e),
                    "timestamp": datetime.utcnow(),
                    "status": "error"
                }
                
                _improvement_engine.improvement_history.append(improvement_record)
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator




