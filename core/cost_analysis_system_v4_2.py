"""
Sistema de Análisis de Costos en Tiempo Real v4.2
HeyGen AI - Sistema de Monitoreo Inteligente con IA Avanzada

Este sistema implementa:
- Análisis de costos en tiempo real
- Optimización automática de gastos
- Predicción de costos futuros
- Análisis de ROI y eficiencia
- Gestión inteligente de presupuestos
"""

import asyncio
import time
import json
import logging
from typing import Dict, List, Any, Optional, Callable, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics
import numpy as np
import pandas as pd
from pathlib import Path
import threading
import queue
import pickle
import hashlib
import random
import math

# Machine Learning imports
try:
    import sklearn
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.linear_model import LinearRegression, Ridge
    from sklearn.preprocessing import StandardScaler, MinMaxScaler
    from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("Warning: scikit-learn not available, using simplified models")

# Advanced Cost Analysis Components
@dataclass
class CostMetric:
    """Real-time cost metric with detailed breakdown"""
    metric_id: str
    timestamp: datetime
    service_name: str
    resource_type: str
    cost_per_hour: float
    usage_hours: float
    total_cost: float
    currency: str
    region: str
    instance_type: str
    optimization_potential: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CostOptimization:
    """Cost optimization recommendation with ROI analysis"""
    optimization_id: str
    timestamp: datetime
    service_name: str
    optimization_type: str
    current_cost: float
    optimized_cost: float
    cost_savings: float
    savings_percentage: float
    roi_percentage: float
    implementation_cost: float
    payback_period_days: int
    risk_level: str
    priority: int
    recommended_actions: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BudgetAlert:
    """Budget threshold alert with recommendations"""
    alert_id: str
    timestamp: datetime
    budget_name: str
    current_spend: float
    budget_limit: float
    utilization_percentage: float
    alert_type: str  # warning, critical, over_budget
    days_remaining: int
    projected_overspend: float
    recommended_actions: List[str]
    urgency_level: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CostPrediction:
    """Cost prediction with confidence intervals"""
    prediction_id: str
    timestamp: datetime
    service_name: str
    prediction_date: datetime
    predicted_cost: float
    confidence_interval_lower: float
    confidence_interval_upper: float
    confidence_level: float
    trend_direction: str
    seasonal_factors: Dict[str, float]
    model_used: str
    features_importance: Dict[str, float]
    metadata: Dict[str, Any] = field(default_factory=dict)

class RealTimeCostAnalyzer:
    """Real-time cost analysis with ML-powered insights"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.cost_history = deque(maxlen=10000)
        self.optimization_history = deque(maxlen=1000)
        self.budget_alerts = deque(maxlen=500)
        self.cost_predictions = deque(maxlen=1000)
        
        # Cost models
        self.cost_models = {}
        self.cost_scalers = {}
        
        # Budget thresholds
        self.budget_thresholds = config.get('budget_thresholds', {
            'warning': 0.7,  # 70% of budget
            'critical': 0.9,  # 90% of budget
            'over_budget': 1.0  # 100% of budget
        })
        
        # Initialize cost models
        self._initialize_cost_models()
        
    def _initialize_cost_models(self):
        """Initialize cost prediction models"""
        if ML_AVAILABLE:
            # Cost prediction models for different services
            services = ['compute', 'storage', 'network', 'ai_models', 'data_processing']
            
            for service in services:
                self.cost_models[service] = {
                    'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
                    'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
                    'linear': Ridge(alpha=1.0)
                }
                self.cost_scalers[service] = StandardScaler()
        else:
            # Fallback to simplified models
            for service in ['compute', 'storage', 'network', 'ai_models', 'data_processing']:
                self.cost_models[service] = {'simple': self._create_simple_cost_model()}
    
    def _create_simple_cost_model(self):
        """Create simple cost prediction model"""
        class SimpleCostPredictor:
            def __init__(self):
                self.history = deque(maxlen=100)
                self.base_cost = random.uniform(10, 100)
                
            def predict(self, features):
                if len(self.history) < 5:
                    return self.base_cost, 0.5
                
                # Simple moving average with trend
                recent_costs = list(self.history)[-5:]
                base_prediction = statistics.mean(recent_costs)
                
                # Add trend component
                if len(recent_costs) >= 2:
                    trend = (recent_costs[-1] - recent_costs[0]) / len(recent_costs)
                    prediction = base_prediction + trend
                else:
                    prediction = base_prediction
                
                confidence = min(0.9, len(self.history) / 100)
                return prediction, confidence
            
            def update(self, actual_cost):
                self.history.append(actual_cost)
        
        return SimpleCostPredictor()
    
    async def analyze_current_costs(self, metrics: Dict[str, Any]) -> List[CostMetric]:
        """Analyze current costs in real-time"""
        cost_metrics = []
        current_time = datetime.now()
        
        # Analyze different resource types
        resource_types = ['cpu', 'memory', 'gpu', 'storage', 'network']
        
        for resource_type in resource_types:
            try:
                cost_metric = await self._calculate_resource_cost(
                    resource_type, metrics, current_time
                )
                cost_metrics.append(cost_metric)
                
                # Store in history
                self.cost_history.append(cost_metric)
                
            except Exception as e:
                logging.warning(f"Error calculando costos para {resource_type}: {e}")
                continue
        
        return cost_metrics
    
    async def _calculate_resource_cost(
        self, 
        resource_type: str, 
        metrics: Dict[str, Any], 
        timestamp: datetime
    ) -> CostMetric:
        """Calculate cost for a specific resource type"""
        
        # Get usage metrics
        usage_metrics = self._extract_usage_metrics(resource_type, metrics)
        
        # Calculate cost based on resource type and usage
        cost_per_hour = self._get_cost_per_hour(resource_type)
        usage_hours = usage_metrics.get('usage_hours', 1.0)
        total_cost = cost_per_hour * usage_hours
        
        # Calculate optimization potential
        optimization_potential = self._calculate_optimization_potential(
            resource_type, usage_metrics
        )
        
        # Create cost metric
        cost_metric = CostMetric(
            metric_id=f"cost_{resource_type}_{int(timestamp.timestamp())}",
            timestamp=timestamp,
            service_name=f"heygen_ai_{resource_type}",
            resource_type=resource_type,
            cost_per_hour=cost_per_hour,
            usage_hours=usage_hours,
            total_cost=total_cost,
            currency="USD",
            region="us-west-2",
            instance_type=self._get_instance_type(resource_type),
            optimization_potential=optimization_potential,
            metadata={
                'usage_metrics': usage_metrics,
                'cost_model': 'real_time_analysis'
            }
        )
        
        return cost_metric
    
    def _extract_usage_metrics(self, resource_type: str, metrics: Dict[str, Any]) -> Dict[str, float]:
        """Extract usage metrics for cost calculation"""
        usage_metrics = {}
        
        if resource_type == 'cpu':
            cpu_usage = metrics.get('system', {}).get('cpu_usage', 50)
            usage_metrics['usage_percentage'] = cpu_usage
            usage_metrics['usage_hours'] = 1.0  # Current hour
            usage_metrics['cores_utilized'] = max(1, cpu_usage / 100 * 8)  # Assume 8 cores
            
        elif resource_type == 'memory':
            memory_usage = metrics.get('system', {}).get('memory_usage', 60)
            usage_metrics['usage_percentage'] = memory_usage
            usage_metrics['usage_hours'] = 1.0
            usage_metrics['gb_utilized'] = max(1, memory_usage / 100 * 32)  # Assume 32GB
            
        elif resource_type == 'gpu':
            gpu_usage = metrics.get('system', {}).get('gpu_usage', 30)
            usage_metrics['usage_percentage'] = gpu_usage
            usage_metrics['usage_hours'] = 1.0
            usage_metrics['gpu_utilization'] = gpu_usage / 100
            
        elif resource_type == 'storage':
            disk_usage = metrics.get('system', {}).get('disk_usage', 70)
            usage_metrics['usage_percentage'] = disk_usage
            usage_metrics['usage_hours'] = 1.0
            usage_metrics['gb_stored'] = max(100, disk_usage / 100 * 1000)  # Assume 1TB
            
        elif resource_type == 'network':
            # Simulate network usage
            usage_metrics['usage_percentage'] = random.uniform(20, 80)
            usage_metrics['usage_hours'] = 1.0
            usage_metrics['gb_transferred'] = random.uniform(10, 100)
        
        return usage_metrics
    
    def _get_cost_per_hour(self, resource_type: str) -> float:
        """Get cost per hour for resource type"""
        cost_map = {
            'cpu': 0.05,      # $0.05 per hour per core
            'memory': 0.01,   # $0.01 per hour per GB
            'gpu': 0.50,      # $0.50 per hour per GPU
            'storage': 0.001, # $0.001 per hour per GB
            'network': 0.01   # $0.01 per hour per GB
        }
        
        return cost_map.get(resource_type, 0.01)
    
    def _get_instance_type(self, resource_type: str) -> str:
        """Get instance type for resource"""
        instance_map = {
            'cpu': 'c5.2xlarge',
            'memory': 'r5.2xlarge',
            'gpu': 'p3.2xlarge',
            'storage': 'i3.2xlarge',
            'network': 'c5.2xlarge'
        }
        
        return instance_map.get(resource_type, 't3.medium')
    
    def _calculate_optimization_potential(self, resource_type: str, usage_metrics: Dict[str, float]) -> float:
        """Calculate potential cost optimization percentage"""
        usage_percentage = usage_metrics.get('usage_percentage', 50)
        
        if usage_percentage < 30:
            # Under-utilized: potential for downsizing
            return min(40, (30 - usage_percentage) * 2)
        elif usage_percentage > 80:
            # Over-utilized: potential for optimization
            return min(25, (usage_percentage - 80) * 1.5)
        else:
            # Well-utilized: minimal optimization potential
            return max(5, 20 - abs(usage_percentage - 50) * 0.3)
    
    async def generate_cost_optimizations(self, cost_metrics: List[CostMetric]) -> List[CostOptimization]:
        """Generate cost optimization recommendations"""
        optimizations = []
        
        for cost_metric in cost_metrics:
            if cost_metric.optimization_potential > 15:  # Only if significant potential
                optimization = await self._create_optimization_recommendation(cost_metric)
                optimizations.append(optimization)
                
                # Store in history
                self.optimization_history.append(optimization)
        
        return optimizations
    
    async def _create_optimization_recommendation(self, cost_metric: CostMetric) -> CostOptimization:
        """Create detailed optimization recommendation"""
        
        current_cost = cost_metric.total_cost
        optimization_potential = cost_metric.optimization_potential
        
        # Calculate optimized cost
        optimized_cost = current_cost * (1 - optimization_potential / 100)
        cost_savings = current_cost - optimized_cost
        savings_percentage = (cost_savings / current_cost) * 100
        
        # Determine optimization type
        usage_percentage = cost_metric.metadata.get('usage_metrics', {}).get('usage_percentage', 50)
        
        if usage_percentage < 30:
            optimization_type = "downsizing"
            recommended_actions = [
                "Reduce instance size",
                "Switch to spot instances",
                "Implement auto-scaling"
            ]
        elif usage_percentage > 80:
            optimization_type = "performance_optimization"
            recommended_actions = [
                "Optimize resource allocation",
                "Implement caching strategies",
                "Review workload distribution"
            ]
        else:
            optimization_type = "efficiency_improvement"
            recommended_actions = [
                "Fine-tune resource allocation",
                "Monitor usage patterns",
                "Implement cost alerts"
            ]
        
        # Calculate ROI and payback period
        implementation_cost = cost_savings * 0.1  # Assume 10% of savings for implementation
        roi_percentage = ((cost_savings - implementation_cost) / implementation_cost) * 100
        payback_period_days = math.ceil(implementation_cost / (cost_savings / 30))  # Monthly savings
        
        # Determine priority and risk
        priority = self._calculate_priority(optimization_potential, roi_percentage)
        risk_level = self._assess_risk(optimization_type, usage_percentage)
        
        optimization = CostOptimization(
            optimization_id=f"opt_{cost_metric.metric_id}",
            timestamp=datetime.now(),
            service_name=cost_metric.service_name,
            optimization_type=optimization_type,
            current_cost=current_cost,
            optimized_cost=optimized_cost,
            cost_savings=cost_savings,
            savings_percentage=savings_percentage,
            roi_percentage=roi_percentage,
            implementation_cost=implementation_cost,
            payback_period_days=payback_period_days,
            risk_level=risk_level,
            priority=priority,
            recommended_actions=recommended_actions,
            metadata={
                'resource_type': cost_metric.resource_type,
                'usage_percentage': usage_percentage,
                'instance_type': cost_metric.instance_type
            }
        )
        
        return optimization
    
    def _calculate_priority(self, optimization_potential: float, roi_percentage: float) -> int:
        """Calculate optimization priority (1=highest, 5=lowest)"""
        # Higher potential and ROI = higher priority
        potential_score = optimization_potential / 100
        roi_score = min(roi_percentage / 100, 1.0)
        
        combined_score = (potential_score + roi_score) / 2
        
        if combined_score > 0.8:
            return 1
        elif combined_score > 0.6:
            return 2
        elif combined_score > 0.4:
            return 3
        elif combined_score > 0.2:
            return 4
        else:
            return 5
    
    def _assess_risk(self, optimization_type: str, usage_percentage: float) -> str:
        """Assess risk level of optimization"""
        if optimization_type == "downsizing":
            if usage_percentage < 20:
                return "low"
            elif usage_percentage < 30:
                return "medium"
            else:
                return "high"
        elif optimization_type == "performance_optimization":
            if usage_percentage > 95:
                return "low"
            elif usage_percentage > 80:
                return "medium"
            else:
                return "high"
        else:
            return "low"
    
    async def check_budget_alerts(self, cost_metrics: List[CostMetric]) -> List[BudgetAlert]:
        """Check for budget threshold alerts"""
        alerts = []
        
        # Calculate total current spend
        total_spend = sum(metric.total_cost for metric in cost_metrics)
        
        # Get budget limits from config
        budget_limits = self.config.get('budget_limits', {
            'daily': 100.0,
            'weekly': 700.0,
            'monthly': 3000.0
        })
        
        # Check different budget periods
        for period, limit in budget_limits.items():
            alert = await self._check_budget_period(period, limit, total_spend)
            if alert:
                alerts.append(alert)
                self.budget_alerts.append(alert)
        
        return alerts
    
    async def _check_budget_period(
        self, 
        period: str, 
        budget_limit: float, 
        current_spend: float
    ) -> Optional[BudgetAlert]:
        """Check budget for specific period"""
        
        # Calculate utilization percentage
        utilization_percentage = (current_spend / budget_limit) * 100
        
        # Determine alert type
        alert_type = "normal"
        if utilization_percentage >= self.budget_thresholds['over_budget'] * 100:
            alert_type = "over_budget"
        elif utilization_percentage >= self.budget_thresholds['critical'] * 100:
            alert_type = "critical"
        elif utilization_percentage >= self.budget_thresholds['warning'] * 100:
            alert_type = "warning"
        else:
            return None  # No alert needed
        
        # Calculate days remaining and projected overspend
        days_remaining = self._calculate_days_remaining(period)
        projected_overspend = self._calculate_projected_overspend(
            current_spend, budget_limit, period
        )
        
        # Generate recommended actions
        recommended_actions = self._generate_budget_actions(
            alert_type, utilization_percentage, projected_overspend
        )
        
        # Determine urgency level
        urgency_level = self._determine_urgency(alert_type, utilization_percentage)
        
        alert = BudgetAlert(
            alert_id=f"budget_{period}_{int(time.time())}",
            timestamp=datetime.now(),
            budget_name=f"{period.capitalize()} Budget",
            current_spend=current_spend,
            budget_limit=budget_limit,
            utilization_percentage=utilization_percentage,
            alert_type=alert_type,
            days_remaining=days_remaining,
            projected_overspend=projected_overspend,
            recommended_actions=recommended_actions,
            urgency_level=urgency_level,
            metadata={
                'period': period,
                'threshold_exceeded': self.budget_thresholds.get(alert_type, 0)
            }
        )
        
        return alert
    
    def _calculate_days_remaining(self, period: str) -> int:
        """Calculate days remaining in budget period"""
        now = datetime.now()
        
        if period == 'daily':
            # Hours remaining in current day
            return 1
        elif period == 'weekly':
            # Days remaining in current week
            days_since_monday = now.weekday()
            return 7 - days_since_monday
        elif period == 'monthly':
            # Days remaining in current month
            last_day = (now.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            return (last_day - now).days
        else:
            return 30  # Default to monthly
    
    def _calculate_projected_overspend(
        self, 
        current_spend: float, 
        budget_limit: float, 
        period: str
    ) -> float:
        """Calculate projected overspend for the period"""
        days_elapsed = self._get_days_elapsed(period)
        total_days = self._get_total_days(period)
        
        if days_elapsed == 0:
            return 0.0
        
        # Project current spending rate to end of period
        daily_spend_rate = current_spend / days_elapsed
        projected_total = daily_spend_rate * total_days
        
        return max(0, projected_total - budget_limit)
    
    def _get_days_elapsed(self, period: str) -> int:
        """Get days elapsed in current period"""
        now = datetime.now()
        
        if period == 'daily':
            return now.hour / 24
        elif period == 'weekly':
            return now.weekday() + 1
        elif period == 'monthly':
            return now.day
        else:
            return 15  # Default to mid-month
    
    def _get_total_days(self, period: str) -> int:
        """Get total days in period"""
        if period == 'daily':
            return 1
        elif period == 'weekly':
            return 7
        elif period == 'monthly':
            return 30
        else:
            return 30
    
    def _generate_budget_actions(
        self, 
        alert_type: str, 
        utilization_percentage: float, 
        projected_overspend: float
    ) -> List[str]:
        """Generate recommended actions for budget alerts"""
        actions = []
        
        if alert_type == "over_budget":
            actions.extend([
                "Immediate cost reduction required",
                "Scale down non-critical resources",
                "Review and optimize all services",
                "Contact finance team for budget increase"
            ])
        elif alert_type == "critical":
            actions.extend([
                "Implement aggressive cost optimization",
                "Pause non-essential operations",
                "Review resource allocation",
                "Set up cost alerts for all services"
            ])
        elif alert_type == "warning":
            actions.extend([
                "Monitor spending closely",
                "Implement cost optimization measures",
                "Review resource utilization",
                "Set up budget alerts"
            ])
        
        # Add specific actions based on projected overspend
        if projected_overspend > 0:
            actions.append(f"Projected overspend: ${projected_overspend:.2f} - immediate action required")
        
        return actions
    
    def _determine_urgency(self, alert_type: str, utilization_percentage: float) -> str:
        """Determine urgency level of budget alert"""
        if alert_type == "over_budget":
            return "immediate"
        elif alert_type == "critical":
            return "high"
        elif alert_type == "warning":
            return "medium"
        else:
            return "low"
    
    async def predict_future_costs(
        self, 
        cost_metrics: List[CostMetric], 
        horizon_days: int = 30
    ) -> List[CostPrediction]:
        """Predict future costs using ML models"""
        predictions = []
        
        # Group costs by service
        service_costs = defaultdict(list)
        for metric in cost_metrics:
            service_name = metric.service_name
            service_costs[service_name].append({
                'timestamp': metric.timestamp,
                'cost': metric.total_cost,
                'usage': metric.metadata.get('usage_metrics', {}).get('usage_percentage', 50)
            })
        
        # Generate predictions for each service
        for service_name, cost_data in service_costs.items():
            if len(cost_data) >= 5:  # Need minimum data for prediction
                try:
                    prediction = await self._predict_service_cost(
                        service_name, cost_data, horizon_days
                    )
                    predictions.append(prediction)
                    
                    # Store in history
                    self.cost_predictions.append(prediction)
                    
                except Exception as e:
                    logging.warning(f"Error prediciendo costos para {service_name}: {e}")
                    continue
        
        return predictions
    
    async def _predict_service_cost(
        self, 
        service_name: str, 
        cost_data: List[Dict[str, Any]], 
        horizon_days: int
    ) -> CostPrediction:
        """Predict cost for a specific service"""
        
        # Extract features for prediction
        features = self._extract_cost_features(cost_data)
        
        # Make prediction using appropriate model
        service_type = self._categorize_service(service_name)
        
        if service_type in self.cost_models and ML_AVAILABLE:
            prediction, confidence = await self._ml_cost_prediction(
                service_type, features, horizon_days
            )
        else:
            prediction, confidence = await self._simple_cost_prediction(
                cost_data, horizon_days
            )
        
        # Calculate confidence intervals
        confidence_interval = confidence * 0.2  # 20% of confidence as interval
        confidence_interval_lower = max(0, prediction - confidence_interval)
        confidence_interval_upper = prediction + confidence_interval
        
        # Analyze trend
        trend_direction = self._analyze_cost_trend(cost_data)
        
        # Calculate seasonal factors
        seasonal_factors = self._calculate_seasonal_factors(horizon_days)
        
        # Get feature importance
        features_importance = self._get_cost_feature_importance(service_type)
        
        cost_prediction = CostPrediction(
            prediction_id=f"pred_{service_name}_{int(time.time())}",
            timestamp=datetime.now(),
            service_name=service_name,
            prediction_date=datetime.now() + timedelta(days=horizon_days),
            predicted_cost=prediction,
            confidence_interval_lower=confidence_interval_lower,
            confidence_interval_upper=confidence_interval_upper,
            confidence_level=confidence,
            trend_direction=trend_direction,
            seasonal_factors=seasonal_factors,
            model_used=service_type if service_type in self.cost_models else "simple",
            features_importance=features_importance,
            metadata={
                'horizon_days': horizon_days,
                'data_points_used': len(cost_data),
                'prediction_method': 'ml' if service_type in self.cost_models else 'statistical'
            }
        )
        
        return cost_prediction
    
    def _extract_cost_features(self, cost_data: List[Dict[str, Any]]) -> np.ndarray:
        """Extract features for cost prediction"""
        features = []
        
        # Recent costs (last 7 data points)
        recent_costs = [d['cost'] for d in cost_data[-7:]]
        features.extend(recent_costs)
        
        # Recent usage percentages
        recent_usage = [d['usage'] for d in cost_data[-7:]]
        features.extend(recent_usage)
        
        # Time-based features
        if cost_data:
            latest_timestamp = cost_data[-1]['timestamp']
            features.extend([
                latest_timestamp.hour,
                latest_timestamp.weekday(),
                latest_timestamp.month
            ])
        
        # Statistical features
        if len(recent_costs) > 1:
            features.extend([
                statistics.mean(recent_costs),
                statistics.stdev(recent_costs) if len(recent_costs) > 1 else 0,
                max(recent_costs),
                min(recent_costs)
            ])
        else:
            features.extend([recent_costs[0], 0, recent_costs[0], recent_costs[0]])
        
        # Pad features to consistent length
        while len(features) < 20:
            features.append(0.0)
        
        return np.array(features[:20], dtype=np.float32)
    
    def _categorize_service(self, service_name: str) -> str:
        """Categorize service for model selection"""
        if 'cpu' in service_name or 'compute' in service_name:
            return 'compute'
        elif 'storage' in service_name:
            return 'storage'
        elif 'network' in service_name:
            return 'network'
        elif 'ai' in service_name or 'gpu' in service_name:
            return 'ai_models'
        else:
            return 'data_processing'
    
    async def _ml_cost_prediction(
        self, 
        service_type: str, 
        features: np.ndarray, 
        horizon_days: int
    ) -> Tuple[float, float]:
        """Make ML-based cost prediction"""
        if service_type not in self.cost_models:
            return 100.0, 0.5
        
        predictions = []
        confidences = []
        
        for model_name, model in self.cost_models[service_type].items():
            try:
                if model_name == 'simple':
                    pred, conf = model.predict(features)
                else:
                    # For sklearn models, we need to train them first
                    # In a real system, these would be pre-trained
                    pred, conf = self._sklearn_cost_prediction(model, features)
                
                predictions.append(pred)
                confidences.append(conf)
                
            except Exception as e:
                logging.warning(f"Error in {model_name} cost prediction: {e}")
                continue
        
        if not predictions:
            return 100.0, 0.5
        
        # Ensemble prediction
        ensemble_prediction = np.average(predictions, weights=confidences)
        ensemble_confidence = np.mean(confidences)
        
        # Adjust for prediction horizon
        horizon_factor = 1 + (horizon_days / 30) * 0.5  # 50% increase per month
        adjusted_prediction = ensemble_prediction * horizon_factor
        
        return adjusted_prediction, ensemble_confidence
    
    def _sklearn_cost_prediction(self, model, features: np.ndarray) -> Tuple[float, float]:
        """Make scikit-learn cost prediction"""
        try:
            # In a real system, the model would be trained
            # For demo purposes, use a simple heuristic
            base_cost = 50.0
            feature_factor = np.mean(features) / 100
            prediction = base_cost * (1 + feature_factor)
            
            confidence = 0.7  # Default confidence
            
            return prediction, confidence
            
        except Exception as e:
            logging.warning(f"Error in sklearn cost prediction: {e}")
            return 100.0, 0.5
    
    async def _simple_cost_prediction(
        self, 
        cost_data: List[Dict[str, Any]], 
        horizon_days: int
    ) -> Tuple[float, float]:
        """Make simple statistical cost prediction"""
        if not cost_data:
            return 100.0, 0.5
        
        # Get recent costs
        recent_costs = [d['cost'] for d in cost_data[-5:]]
        
        # Calculate base prediction (moving average)
        base_prediction = statistics.mean(recent_costs)
        
        # Add trend component
        if len(recent_costs) >= 2:
            trend = (recent_costs[-1] - recent_costs[0]) / len(recent_costs)
            trend_factor = 1 + (trend / base_prediction) * horizon_days
        else:
            trend_factor = 1.0
        
        # Add seasonal factor
        seasonal_factor = 1 + 0.1 * math.sin(2 * math.pi * horizon_days / 30)
        
        # Final prediction
        prediction = base_prediction * trend_factor * seasonal_factor
        
        # Calculate confidence based on data quality
        confidence = min(0.9, len(cost_data) / 20)
        
        return prediction, confidence
    
    def _analyze_cost_trend(self, cost_data: List[Dict[str, Any]]) -> str:
        """Analyze cost trend direction"""
        if len(cost_data) < 3:
            return "stable"
        
        recent_costs = [d['cost'] for d in cost_data[-3:]]
        
        # Calculate trend
        x = np.arange(len(recent_costs))
        slope = np.polyfit(x, recent_costs, 1)[0]
        
        if slope > 0.1:
            return "increasing"
        elif slope < -0.1:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_seasonal_factors(self, horizon_days: int) -> Dict[str, float]:
        """Calculate seasonal factors for cost prediction"""
        seasonal_factors = {}
        
        # Day of week factor
        target_date = datetime.now() + timedelta(days=horizon_days)
        day_of_week = target_date.weekday()
        
        # Weekdays typically have higher costs
        if day_of_week < 5:  # Monday to Friday
            seasonal_factors['day_of_week'] = 1.1
        else:
            seasonal_factors['day_of_week'] = 0.9
        
        # Month factor (business cycles)
        month = target_date.month
        if month in [1, 7, 12]:  # January, July, December
            seasonal_factors['month'] = 0.9  # Lower costs
        elif month in [3, 9]:  # March, September
            seasonal_factors['month'] = 1.1  # Higher costs
        else:
            seasonal_factors['month'] = 1.0
        
        # Quarter factor
        quarter = (month - 1) // 3 + 1
        if quarter == 4:  # Q4
            seasonal_factors['quarter'] = 1.2  # Higher costs
        else:
            seasonal_factors['quarter'] = 1.0
        
        return seasonal_factors
    
    def _get_cost_feature_importance(self, service_type: str) -> Dict[str, float]:
        """Get feature importance for cost prediction"""
        # In a real system, this would come from trained models
        # For demo purposes, use predefined importance
        base_importance = {
            'recent_costs': 0.3,
            'usage_patterns': 0.25,
            'time_factors': 0.2,
            'statistical_features': 0.15,
            'seasonal_factors': 0.1
        }
        
        # Adjust based on service type
        if service_type == 'compute':
            base_importance['usage_patterns'] += 0.1
        elif service_type == 'storage':
            base_importance['recent_costs'] += 0.1
        elif service_type == 'ai_models':
            base_importance['time_factors'] += 0.1
        
        return base_importance

class CostAnalysisSystem:
    """Main system combining all cost analysis capabilities"""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self._load_config()
        self.cost_analyzer = RealTimeCostAnalyzer(self.config)
        self.is_running = False
        self.analysis_interval = self.config.get('analysis_interval', 300)  # 5 minutes
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration"""
        try:
            import yaml
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'analysis_interval': 300,
            'budget_thresholds': {
                'warning': 0.7,
                'critical': 0.9,
                'over_budget': 1.0
            },
            'budget_limits': {
                'daily': 100.0,
                'weekly': 700.0,
                'monthly': 3000.0
            }
        }
    
    async def start(self):
        """Start the cost analysis system"""
        if self.is_running:
            print("⚠️ El sistema ya está ejecutándose")
            return
        
        self.is_running = True
        print("🚀 Iniciando Sistema de Análisis de Costos v4.2...")
        
        # Start analysis loop
        asyncio.create_task(self._analysis_loop())
        
        print("✅ Sistema de Análisis de Costos v4.2 iniciado")
    
    async def _analysis_loop(self):
        """Main cost analysis loop"""
        while self.is_running:
            try:
                # Get current metrics (simulated for demo)
                current_metrics = self._get_simulated_metrics()
                
                # Analyze current costs
                cost_metrics = await self.cost_analyzer.analyze_current_costs(current_metrics)
                
                # Generate optimizations
                optimizations = await self.cost_analyzer.generate_cost_optimizations(cost_metrics)
                
                # Check budget alerts
                budget_alerts = await self.cost_analyzer.check_budget_alerts(cost_metrics)
                
                # Predict future costs
                cost_predictions = await self.cost_analyzer.predict_future_costs(cost_metrics)
                
                # Display results
                await self._display_analysis_results(
                    cost_metrics, optimizations, budget_alerts, cost_predictions
                )
                
                # Wait for next cycle
                await asyncio.sleep(self.analysis_interval)
                
            except Exception as e:
                print(f"Error en loop de análisis de costos: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    def _get_simulated_metrics(self) -> Dict[str, Any]:
        """Get simulated system metrics"""
        return {
            'system': {
                'cpu_usage': random.uniform(40, 80),
                'memory_usage': random.uniform(50, 85),
                'gpu_usage': random.uniform(20, 70),
                'disk_usage': random.uniform(60, 90)
            },
            'timestamp': datetime.now().isoformat()
        }
    
    async def _display_analysis_results(
        self,
        cost_metrics: List[CostMetric],
        optimizations: List[CostOptimization],
        budget_alerts: List[BudgetAlert],
        cost_predictions: List[CostPrediction]
    ):
        """Display cost analysis results"""
        print(f"\n💰 Análisis de Costos - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60)
        
        # Display current costs
        total_current_cost = sum(metric.total_cost for metric in cost_metrics)
        print(f"\n📊 Costos Actuales: ${total_current_cost:.2f}/hora")
        
        for metric in cost_metrics:
            print(f"  {metric.resource_type}: ${metric.total_cost:.2f}/hora "
                  f"(Optimización: {metric.optimization_potential:.1f}%)")
        
        # Display optimizations
        if optimizations:
            total_savings = sum(opt.cost_savings for opt in optimizations)
            print(f"\n🔧 Optimizaciones Detectadas: ${total_savings:.2f}/hora de ahorro")
            
            for opt in optimizations[:3]:  # Show top 3
                print(f"  {opt.optimization_type}: ${opt.cost_savings:.2f}/hora "
                      f"(ROI: {opt.roi_percentage:.1f}%, Prioridad: {opt.priority})")
        
        # Display budget alerts
        if budget_alerts:
            print(f"\n⚠️ Alertas de Presupuesto ({len(budget_alerts)}):")
            for alert in budget_alerts:
                print(f"  {alert.budget_name}: {alert.alert_type.upper()} "
                      f"({alert.utilization_percentage:.1f}% utilizado)")
        
        # Display cost predictions
        if cost_predictions:
            print(f"\n🔮 Predicciones de Costos:")
            for pred in cost_predictions[:2]:  # Show top 2
                print(f"  {pred.service_name}: ${pred.predicted_cost:.2f} "
                      f"(Confianza: {pred.confidence_level:.1%})")
        
        print(f"\n⏰ Próxima actualización en {self.analysis_interval} segundos")
    
    async def stop(self):
        """Stop the cost analysis system"""
        print("🛑 Deteniendo Sistema de Análisis de Costos v4.2...")
        self.is_running = False
        print("✅ Sistema detenido")

# Factory function
async def create_cost_analysis_system(config_path: str) -> CostAnalysisSystem:
    """Create and initialize the cost analysis system"""
    system = CostAnalysisSystem(config_path)
    return system

if __name__ == "__main__":
    # Demo usage
    async def main():
        config_path = "advanced_integration_config_v4_1.yaml"
        system = await create_cost_analysis_system(config_path)
        
        try:
            await system.start()
            
            # Keep running
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            await system.stop()
    
    asyncio.run(main())
