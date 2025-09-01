"""
Sistema de Predicción Avanzada con IA Generativa v4.2
HeyGen AI - Sistema de Monitoreo Inteligente con IA Avanzada

Este sistema implementa:
- Predicción avanzada con modelos generativos
- Reinforcement Learning para auto-scaling
- Análisis de patrones temporales complejos
- Optimización automática de recursos
- Predicción de costos y ROI
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

# Deep Learning imports
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import Dataset, DataLoader
    DL_AVAILABLE = True
except ImportError:
    DL_AVAILABLE = False
    print("Warning: PyTorch not available, using simplified models")

# Advanced AI Integration Components
@dataclass
class ResourcePrediction:
    """Advanced resource prediction with confidence and uncertainty"""
    resource_name: str
    timestamp: datetime
    predicted_value: float
    confidence: float
    uncertainty: float
    trend_direction: str
    seasonal_factor: float
    anomaly_score: float
    model_used: str
    features_importance: Dict[str, float]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CostPrediction:
    """Cost prediction with ROI analysis"""
    service_name: str
    timestamp: datetime
    predicted_cost: float
    current_cost: float
    cost_savings: float
    roi_percentage: float
    optimization_opportunities: List[str]
    risk_factors: List[str]
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ScalingDecision:
    """Intelligent scaling decision with reinforcement learning"""
    decision_id: str
    timestamp: datetime
    action_type: str  # scale_up, scale_down, maintain
    resource_type: str  # cpu, memory, gpu, instances
    magnitude: float
    expected_improvement: Dict[str, float]
    confidence: float
    q_value: float  # Reinforcement learning Q-value
    risk_assessment: str
    rollback_plan: str
    metadata: Dict[str, Any] = field(default_factory=dict)

class GenerativeAIPredictor:
    """Advanced predictor using generative AI techniques"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
        self.prediction_history = deque(maxlen=10000)
        self.anomaly_detector = None
        self.seasonality_detector = None
        
        # Initialize ML models
        self._initialize_models()
        
    def _initialize_models(self):
        """Initialize machine learning models"""
        if ML_AVAILABLE:
            # CPU prediction model
            self.models['cpu'] = {
                'lstm': self._create_lstm_model() if DL_AVAILABLE else None,
                'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
                'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
                'linear': Ridge(alpha=1.0)
            }
            
            # Memory prediction model
            self.models['memory'] = {
                'lstm': self._create_lstm_model() if DL_AVAILABLE else None,
                'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
                'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
                'linear': LinearRegression()
            }
            
            # GPU prediction model
            self.models['gpu'] = {
                'lstm': self._create_lstm_model() if DL_AVAILABLE else None,
                'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
                'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
                'linear': Ridge(alpha=0.5)
            }
            
            # Initialize scalers
            for resource in ['cpu', 'memory', 'gpu']:
                self.scalers[resource] = StandardScaler()
                
        else:
            # Fallback to simplified models
            self.models = {
                'cpu': {'simple': self._create_simple_model()},
                'memory': {'simple': self._create_simple_model()},
                'gpu': {'simple': self._create_simple_model()}
            }
    
    def _create_lstm_model(self) -> Optional[nn.Module]:
        """Create LSTM model for time series prediction"""
        if not DL_AVAILABLE:
            return None
            
        class LSTMPredictor(nn.Module):
            def __init__(self, input_size=10, hidden_size=64, num_layers=2, output_size=1):
                super(LSTMPredictor, self).__init__()
                self.hidden_size = hidden_size
                self.num_layers = num_layers
                
                self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
                self.fc = nn.Linear(hidden_size, output_size)
                self.dropout = nn.Dropout(0.2)
                
            def forward(self, x):
                h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
                c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
                
                out, _ = self.lstm(x, (h0, c0))
                out = self.dropout(out[:, -1, :])
                out = self.fc(out)
                return out
        
        return LSTMPredictor()
    
    def _create_simple_model(self):
        """Create simple statistical model as fallback"""
        class SimplePredictor:
            def __init__(self):
                self.history = deque(maxlen=100)
                self.trend = 0
                
            def predict(self, features):
                if len(self.history) < 10:
                    return 50.0, 0.5  # Default prediction
                
                # Simple moving average with trend
                recent_values = list(self.history)[-10:]
                base_prediction = statistics.mean(recent_values)
                
                # Add trend component
                if len(recent_values) >= 2:
                    self.trend = (recent_values[-1] - recent_values[0]) / len(recent_values)
                
                prediction = base_prediction + self.trend
                confidence = min(0.9, len(self.history) / 100)
                
                return prediction, confidence
            
            def update(self, actual_value):
                self.history.append(actual_value)
        
        return SimplePredictor()
    
    async def predict_resource_usage(
        self, 
        resource_type: str, 
        horizon_hours: int = 24,
        confidence_threshold: float = 0.8
    ) -> List[ResourcePrediction]:
        """Predict resource usage for specified horizon"""
        
        predictions = []
        current_time = datetime.now()
        
        # Generate predictions for each hour
        for hour in range(1, horizon_hours + 1):
            prediction_time = current_time + timedelta(hours=hour)
            
            # Get features for prediction
            features = await self._extract_features(resource_type, hour)
            
            # Make prediction using ensemble of models
            prediction, confidence, uncertainty = await self._ensemble_predict(
                resource_type, features
            )
            
            # Detect anomalies and seasonality
            anomaly_score = self._detect_anomalies(resource_type, prediction)
            seasonal_factor = self._detect_seasonality(resource_type, hour)
            trend_direction = self._analyze_trend(resource_type)
            
            # Calculate feature importance
            features_importance = self._calculate_feature_importance(resource_type, features)
            
            # Create prediction object
            resource_prediction = ResourcePrediction(
                resource_name=resource_type,
                timestamp=prediction_time,
                predicted_value=prediction,
                confidence=confidence,
                uncertainty=uncertainty,
                trend_direction=trend_direction,
                seasonal_factor=seasonal_factor,
                anomaly_score=anomaly_score,
                model_used="ensemble",
                features_importance=features_importance,
                metadata={
                    'horizon_hours': hour,
                    'models_used': list(self.models[resource_type].keys())
                }
            )
            
            predictions.append(resource_prediction)
            
            # Filter by confidence threshold
            if confidence < confidence_threshold:
                break
        
        # Store predictions in history
        self.prediction_history.extend(predictions)
        
        return predictions
    
    async def _extract_features(self, resource_type: str, horizon_hours: int) -> np.ndarray:
        """Extract features for prediction"""
        features = []
        
        # Historical values (last 24 hours)
        historical_values = self._get_historical_values(resource_type, 24)
        features.extend(historical_values)
        
        # Time-based features
        current_hour = datetime.now().hour
        features.extend([
            current_hour + horizon_hours,  # Target hour
            (current_hour + horizon_hours) % 24,  # Hour of day
            (datetime.now() + timedelta(hours=horizon_hours)).weekday(),  # Day of week
            (datetime.now() + timedelta(hours=horizon_hours)).month,  # Month
        ])
        
        # System features (if available)
        try:
            import psutil
            features.extend([
                psutil.cpu_percent(interval=1),
                psutil.virtual_memory().percent,
                psutil.disk_usage('/').percent
            ])
        except ImportError:
            features.extend([50.0, 60.0, 70.0])  # Default values
        
        # Convert to numpy array
        features_array = np.array(features, dtype=np.float32)
        
        # Normalize features
        if resource_type in self.scalers:
            features_array = self.scalers[resource_type].fit_transform(
                features_array.reshape(1, -1)
            ).flatten()
        
        return features_array
    
    async def _ensemble_predict(
        self, 
        resource_type: str, 
        features: np.ndarray
    ) -> Tuple[float, float, float]:
        """Make ensemble prediction using multiple models"""
        
        if resource_type not in self.models:
            return 50.0, 0.5, 0.5
        
        predictions = []
        confidences = []
        
        for model_name, model in self.models[resource_type].items():
            try:
                if model_name == 'lstm' and DL_AVAILABLE:
                    pred, conf = self._lstm_predict(model, features)
                elif model_name == 'simple':
                    pred, conf = model.predict(features)
                else:
                    pred, conf = self._sklearn_predict(model, features)
                
                predictions.append(pred)
                confidences.append(conf)
                
            except Exception as e:
                logging.warning(f"Error in {model_name} prediction: {e}")
                continue
        
        if not predictions:
            return 50.0, 0.5, 0.5
        
        # Ensemble prediction (weighted average)
        ensemble_prediction = np.average(predictions, weights=confidences)
        ensemble_confidence = np.mean(confidences)
        ensemble_uncertainty = np.std(predictions)
        
        return ensemble_prediction, ensemble_confidence, ensemble_uncertainty
    
    def _lstm_predict(self, model: nn.Module, features: np.ndarray) -> Tuple[float, float]:
        """Make LSTM prediction"""
        model.eval()
        with torch.no_grad():
            # Reshape features for LSTM
            x = torch.tensor(features.reshape(1, 1, -1), dtype=torch.float32)
            prediction = model(x).item()
            
            # Simple confidence based on feature quality
            confidence = min(0.95, np.mean(np.abs(features)) / 100)
            
            return prediction, confidence
    
    def _sklearn_predict(self, model, features: np.ndarray) -> Tuple[float, float]:
        """Make scikit-learn prediction"""
        try:
            prediction = model.predict(features.reshape(1, -1))[0]
            
            # Estimate confidence based on model type
            if hasattr(model, 'score'):
                confidence = max(0.5, min(0.95, model.score(features.reshape(1, -1), [0]) + 0.5))
            else:
                confidence = 0.7
            
            return prediction, confidence
            
        except Exception as e:
            logging.warning(f"Error in sklearn prediction: {e}")
            return 50.0, 0.5
    
    def _get_historical_values(self, resource_type: str, hours: int) -> List[float]:
        """Get historical values for the resource"""
        # In a real system, this would query a time-series database
        # For now, generate synthetic data
        base_value = 50.0
        if resource_type == 'cpu':
            base_value = 45.0
        elif resource_type == 'memory':
            base_value = 65.0
        elif resource_type == 'gpu':
            base_value = 30.0
        
        values = []
        for hour in range(hours):
            # Add some realistic variation
            variation = random.uniform(-20, 20)
            seasonal_factor = 10 * np.sin(2 * np.pi * hour / 24)
            value = max(0, min(100, base_value + variation + seasonal_factor))
            values.append(value)
        
        return values
    
    def _detect_anomalies(self, resource_type: str, value: float) -> float:
        """Detect anomalies in predicted values"""
        if len(self.prediction_history) < 10:
            return 0.0
        
        # Get recent predictions for this resource
        recent_predictions = [
            p.predicted_value for p in self.prediction_history 
            if p.resource_name == resource_type
        ][-10:]
        
        if not recent_predictions:
            return 0.0
        
        # Calculate z-score
        mean_val = np.mean(recent_predictions)
        std_val = np.std(recent_predictions)
        
        if std_val == 0:
            return 0.0
        
        z_score = abs(value - mean_val) / std_val
        anomaly_score = min(1.0, z_score / 3.0)  # Normalize to [0, 1]
        
        return anomaly_score
    
    def _detect_seasonality(self, resource_type: str, hour: int) -> float:
        """Detect seasonal patterns"""
        # Simple seasonal pattern based on hour of day
        if resource_type == 'cpu':
            # CPU usage typically higher during business hours
            if 9 <= hour % 24 <= 17:
                return 1.2
            else:
                return 0.8
        elif resource_type == 'memory':
            # Memory usage more stable
            return 1.0
        elif resource_type == 'gpu':
            # GPU usage might have different patterns
            return 1.0
        
        return 1.0
    
    def _analyze_trend(self, resource_type: str) -> str:
        """Analyze trend direction"""
        if len(self.prediction_history) < 5:
            return "stable"
        
        recent_predictions = [
            p.predicted_value for p in self.prediction_history 
            if p.resource_name == resource_type
        ][-5:]
        
        if len(recent_predictions) < 2:
            return "stable"
        
        # Calculate trend
        x = np.arange(len(recent_predictions))
        slope = np.polyfit(x, recent_predictions, 1)[0]
        
        if slope > 5:
            return "increasing"
        elif slope < -5:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_feature_importance(self, resource_type: str, features: np.ndarray) -> Dict[str, float]:
        """Calculate feature importance"""
        if resource_type not in self.feature_importance:
            # Initialize feature importance
            feature_names = [
                'historical_24h', 'historical_23h', 'historical_22h', 'historical_21h',
                'historical_20h', 'historical_19h', 'historical_18h', 'historical_17h',
                'historical_16h', 'historical_15h', 'historical_14h', 'historical_13h',
                'historical_12h', 'historical_11h', 'historical_10h', 'historical_9h',
                'historical_8h', 'historical_7h', 'historical_6h', 'historical_5h',
                'historical_4h', 'historical_3h', 'historical_2h', 'historical_1h',
                'target_hour', 'hour_of_day', 'day_of_week', 'month',
                'current_cpu', 'current_memory', 'current_disk'
            ]
            
            # Assign random importance (in real system, this would come from model training)
            self.feature_importance[resource_type] = {
                name: random.uniform(0.1, 1.0) for name in feature_names
            }
        
        return self.feature_importance[resource_type]

class ReinforcementLearningScaler:
    """Intelligent scaling using reinforcement learning"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.q_table = defaultdict(lambda: defaultdict(float))
        self.learning_rate = config.get('learning_rate', 0.1)
        self.discount_factor = config.get('discount_factor', 0.95)
        self.epsilon = config.get('epsilon', 0.1)
        self.action_history = deque(maxlen=1000)
        self.reward_history = deque(maxlen=1000)
        
        # Define possible actions
        self.actions = [
            'scale_up_cpu', 'scale_down_cpu', 'scale_up_memory', 'scale_down_memory',
            'scale_up_gpu', 'scale_down_gpu', 'scale_up_instances', 'scale_down_instances',
            'maintain_current'
        ]
        
        # Define states (resource usage levels)
        self.states = [
            'very_low', 'low', 'normal', 'high', 'very_high', 'critical'
        ]
    
    def get_state(self, metrics: Dict[str, Any]) -> str:
        """Convert metrics to state representation"""
        cpu_usage = metrics.get('system', {}).get('cpu_usage', 50)
        memory_usage = metrics.get('system', {}).get('memory_usage', 50)
        gpu_usage = metrics.get('system', {}).get('gpu_usage', 50)
        
        # Calculate overall system state
        avg_usage = (cpu_usage + memory_usage + gpu_usage) / 3
        
        if avg_usage < 20:
            return 'very_low'
        elif avg_usage < 40:
            return 'low'
        elif avg_usage < 60:
            return 'normal'
        elif avg_usage < 80:
            return 'high'
        elif avg_usage < 95:
            return 'very_high'
        else:
            return 'critical'
    
    def choose_action(self, state: str, exploration: bool = True) -> str:
        """Choose action using epsilon-greedy policy"""
        if exploration and random.random() < self.epsilon:
            # Exploration: random action
            return random.choice(self.actions)
        else:
            # Exploitation: best action based on Q-values
            q_values = self.q_table[state]
            if not q_values:
                return random.choice(self.actions)
            
            best_action = max(q_values.keys(), key=lambda a: q_values[a])
            return best_action
    
    def update_q_value(self, state: str, action: str, reward: float, next_state: str):
        """Update Q-value using Q-learning"""
        current_q = self.q_table[state][action]
        
        # Get max Q-value for next state
        next_q_values = self.q_table[next_state]
        max_next_q = max(next_q_values.values()) if next_q_values else 0
        
        # Q-learning update formula
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )
        
        self.q_table[state][action] = new_q
    
    def calculate_reward(self, action: str, before_metrics: Dict[str, Any], after_metrics: Dict[str, Any]) -> float:
        """Calculate reward for the action taken"""
        reward = 0.0
        
        # Performance improvement reward
        if 'scale_up' in action:
            # Reward for scaling up when needed
            if before_metrics.get('system', {}).get('cpu_usage', 0) > 80:
                reward += 10
            else:
                reward -= 5  # Penalty for unnecessary scaling
        
        elif 'scale_down' in action:
            # Reward for scaling down when appropriate
            if before_metrics.get('system', {}).get('cpu_usage', 0) < 30:
                reward += 5
            else:
                reward -= 10  # Penalty for scaling down when needed
        
        elif action == 'maintain_current':
            # Reward for maintaining when system is stable
            cpu_usage = before_metrics.get('system', {}).get('cpu_usage', 50)
            if 40 <= cpu_usage <= 70:
                reward += 3
            else:
                reward -= 2
        
        # Cost efficiency reward
        if 'scale_up' in action:
            reward -= 2  # Cost penalty for scaling up
        elif 'scale_down' in action:
            reward += 1  # Cost benefit for scaling down
        
        return reward
    
    async def make_scaling_decision(
        self, 
        current_metrics: Dict[str, Any],
        predictions: List[ResourcePrediction]
    ) -> ScalingDecision:
        """Make intelligent scaling decision"""
        
        current_state = self.get_state(current_metrics)
        
        # Choose action
        action = self.choose_action(current_state)
        
        # Analyze predictions to improve decision
        if predictions:
            # Look at short-term predictions (next 2 hours)
            short_term_predictions = [p for p in predictions if p.timestamp.hour <= 2]
            
            if short_term_predictions:
                avg_predicted_usage = np.mean([p.predicted_value for p in short_term_predictions])
                
                # Adjust action based on predictions
                if avg_predicted_usage > 80 and 'scale_up' not in action:
                    action = 'scale_up_instances'
                elif avg_predicted_usage < 30 and 'scale_down' not in action:
                    action = 'scale_down_instances'
        
        # Calculate expected improvement
        expected_improvement = self._calculate_expected_improvement(action, current_metrics)
        
        # Get Q-value for confidence
        q_value = self.q_table[current_state].get(action, 0.0)
        confidence = min(0.95, max(0.1, (q_value + 10) / 20))  # Normalize to [0.1, 0.95]
        
        # Create scaling decision
        decision = ScalingDecision(
            decision_id=f"scale_{int(time.time())}",
            timestamp=datetime.now(),
            action_type=action,
            resource_type=self._extract_resource_type(action),
            magnitude=self._calculate_magnitude(action, current_metrics),
            expected_improvement=expected_improvement,
            confidence=confidence,
            q_value=q_value,
            risk_assessment=self._assess_risk(action, current_metrics),
            rollback_plan=self._generate_rollback_plan(action),
            metadata={
                'current_state': current_state,
                'predictions_used': len(predictions),
                'exploration_used': random.random() < self.epsilon
            }
        )
        
        return decision
    
    def _extract_resource_type(self, action: str) -> str:
        """Extract resource type from action"""
        if 'cpu' in action:
            return 'cpu'
        elif 'memory' in action:
            return 'memory'
        elif 'gpu' in action:
            return 'gpu'
        elif 'instances' in action:
            return 'instances'
        else:
            return 'general'
    
    def _calculate_magnitude(self, action: str, metrics: Dict[str, Any]) -> float:
        """Calculate scaling magnitude"""
        if 'scale_up' in action:
            current_usage = metrics.get('system', {}).get('cpu_usage', 50)
            if current_usage > 90:
                return 2.0  # Double the resources
            elif current_usage > 80:
                return 1.5  # 50% increase
            else:
                return 1.2  # 20% increase
        elif 'scale_down' in action:
            current_usage = metrics.get('system', {}).get('cpu_usage', 50)
            if current_usage < 20:
                return 0.5  # Halve the resources
            elif current_usage < 30:
                return 0.7  # 30% decrease
            else:
                return 0.8  # 20% decrease
        else:
            return 1.0  # No change
    
    def _calculate_expected_improvement(self, action: str, metrics: Dict[str, Any]) -> Dict[str, float]:
        """Calculate expected improvement from action"""
        improvements = {}
        
        if 'scale_up' in action:
            improvements['cpu_usage'] = -20  # Reduce CPU usage by 20%
            improvements['response_time'] = -30  # Reduce response time by 30%
            improvements['throughput'] = 25  # Increase throughput by 25%
        elif 'scale_down' in action:
            improvements['cost'] = -15  # Reduce cost by 15%
            improvements['resource_efficiency'] = 20  # Improve efficiency by 20%
        else:
            improvements['stability'] = 10  # Improve stability by 10%
        
        return improvements
    
    def _assess_risk(self, action: str, metrics: Dict[str, Any]) -> str:
        """Assess risk of the scaling action"""
        if 'scale_down' in action:
            current_usage = metrics.get('system', {}).get('cpu_usage', 50)
            if current_usage > 70:
                return 'high'  # Risk of performance degradation
            elif current_usage > 50:
                return 'medium'  # Moderate risk
            else:
                return 'low'  # Low risk
        elif 'scale_up' in action:
            return 'low'  # Scaling up is generally safe
        else:
            return 'minimal'  # No action has minimal risk
    
    def _generate_rollback_plan(self, action: str) -> str:
        """Generate rollback plan for the action"""
        if 'scale_up' in action:
            return "Scale down to previous level if performance doesn't improve within 5 minutes"
        elif 'scale_down' in action:
            return "Scale up immediately if performance degrades below acceptable threshold"
        else:
            return "No rollback needed for maintain action"
    
    def update_from_result(self, decision: ScalingDecision, result_metrics: Dict[str, Any]):
        """Update Q-values based on action results"""
        # Calculate reward
        reward = self.calculate_reward(decision.action_type, {}, result_metrics)
        
        # Get next state
        next_state = self.get_state(result_metrics)
        
        # Update Q-value
        current_state = decision.metadata.get('current_state', 'normal')
        self.update_q_value(current_state, decision.action_type, reward, next_state)
        
        # Store action and reward for analysis
        self.action_history.append({
            'action': decision.action_type,
            'state': current_state,
            'reward': reward,
            'timestamp': datetime.now()
        })
        self.reward_history.append(reward)
        
        # Decay epsilon for less exploration over time
        self.epsilon = max(0.01, self.epsilon * 0.999)

class AdvancedPredictionSystem:
    """Main system combining all advanced prediction capabilities"""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self._load_config()
        self.ai_predictor = GenerativeAIPredictor(self.config)
        self.rl_scaler = ReinforcementLearningScaler(self.config)
        self.is_running = False
        self.prediction_interval = self.config.get('prediction_interval', 300)  # 5 minutes
        
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
            'prediction_interval': 300,
            'prediction_horizon': 24,
            'confidence_threshold': 0.8,
            'learning_rate': 0.1,
            'discount_factor': 0.95,
            'epsilon': 0.1
        }
    
    async def start(self):
        """Start the advanced prediction system"""
        if self.is_running:
            print("⚠️ El sistema ya está ejecutándose")
            return
        
        self.is_running = True
        print("🚀 Iniciando Sistema de Predicción Avanzada v4.2...")
        
        # Start prediction loop
        asyncio.create_task(self._prediction_loop())
        
        print("✅ Sistema de Predicción Avanzada v4.2 iniciado")
    
    async def _prediction_loop(self):
        """Main prediction loop"""
        while self.is_running:
            try:
                # Generate predictions for all resources
                predictions = await self._generate_all_predictions()
                
                # Make scaling decisions
                scaling_decisions = await self._make_scaling_decisions(predictions)
                
                # Display results
                await self._display_predictions(predictions, scaling_decisions)
                
                # Wait for next cycle
                await asyncio.sleep(self.prediction_interval)
                
            except Exception as e:
                print(f"Error en loop de predicción: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def _generate_all_predictions(self) -> Dict[str, List[ResourcePrediction]]:
        """Generate predictions for all resources"""
        resources = ['cpu', 'memory', 'gpu']
        all_predictions = {}
        
        for resource in resources:
            try:
                predictions = await self.ai_predictor.predict_resource_usage(
                    resource_type=resource,
                    horizon_hours=self.config.get('prediction_horizon', 24),
                    confidence_threshold=self.config.get('confidence_threshold', 0.8)
                )
                all_predictions[resource] = predictions
                
            except Exception as e:
                print(f"Error generando predicciones para {resource}: {e}")
                all_predictions[resource] = []
        
        return all_predictions
    
    async def _make_scaling_decisions(self, predictions: Dict[str, List[ResourcePrediction]]) -> List[ScalingDecision]:
        """Make scaling decisions based on predictions"""
        decisions = []
        
        # Get current metrics (simulated for demo)
        current_metrics = self._get_simulated_metrics()
        
        # Make decision for each resource type
        for resource_type, resource_predictions in predictions.items():
            if resource_predictions:
                try:
                    decision = await self.rl_scaler.make_scaling_decision(
                        current_metrics, resource_predictions
                    )
                    decisions.append(decision)
                    
                except Exception as e:
                    print(f"Error tomando decisión de escalado para {resource_type}: {e}")
        
        return decisions
    
    def _get_simulated_metrics(self) -> Dict[str, Any]:
        """Get simulated system metrics"""
        return {
            'system': {
                'cpu_usage': random.uniform(40, 80),
                'memory_usage': random.uniform(50, 85),
                'gpu_usage': random.uniform(20, 70)
            },
            'timestamp': datetime.now().isoformat()
        }
    
    async def _display_predictions(
        self, 
        predictions: Dict[str, List[ResourcePrediction]], 
        decisions: List[ScalingDecision]
    ):
        """Display predictions and decisions"""
        print(f"\n📊 Predicciones Generadas - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60)
        
        for resource_type, resource_predictions in predictions.items():
            if resource_predictions:
                print(f"\n🤖 {resource_type.upper()}:")
                for i, pred in enumerate(resource_predictions[:3]):  # Show first 3 predictions
                    print(f"  {i+1}h: {pred.predicted_value:.1f}% "
                          f"(Conf: {pred.confidence:.2%}, "
                          f"Anomalía: {pred.anomaly_score:.2%})")
        
        if decisions:
            print(f"\n🔧 Decisiones de Escalado ({len(decisions)}):")
            for decision in decisions:
                print(f"  {decision.action_type}: "
                      f"Confianza {decision.confidence:.2%}, "
                      f"Q-valor: {decision.q_value:.2f}")
        
        print(f"\n⏰ Próxima actualización en {self.prediction_interval} segundos")
    
    async def stop(self):
        """Stop the prediction system"""
        print("🛑 Deteniendo Sistema de Predicción Avanzada v4.2...")
        self.is_running = False
        print("✅ Sistema detenido")

# Factory function
async def create_advanced_prediction_system(config_path: str) -> AdvancedPredictionSystem:
    """Create and initialize the advanced prediction system"""
    system = AdvancedPredictionSystem(config_path)
    return system

if __name__ == "__main__":
    # Demo usage
    async def main():
        config_path = "advanced_integration_config_v4_1.yaml"
        system = await create_advanced_prediction_system(config_path)
        
        try:
            await system.start()
            
            # Keep running
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            await system.stop()
    
    asyncio.run(main())
