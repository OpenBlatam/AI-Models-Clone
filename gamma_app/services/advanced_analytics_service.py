"""
Advanced Analytics Service with ML and Predictive Analytics
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score, silhouette_score
from sklearn.model_selection import train_test_split
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from ..utils.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class AnalyticsType(Enum):
    """Types of analytics"""
    PREDICTIVE = "predictive"
    DESCRIPTIVE = "descriptive"
    DIAGNOSTIC = "diagnostic"
    PRESCRIPTIVE = "prescriptive"
    REAL_TIME = "real_time"
    BATCH = "batch"

class MetricType(Enum):
    """Types of metrics"""
    PERFORMANCE = "performance"
    USER_BEHAVIOR = "user_behavior"
    CONTENT_QUALITY = "content_quality"
    BUSINESS = "business"
    TECHNICAL = "technical"

@dataclass
class AnalyticsConfig:
    """Configuration for analytics"""
    window_size: int = 30
    prediction_horizon: int = 7
    confidence_level: float = 0.95
    min_data_points: int = 100
    auto_retrain: bool = True
    retrain_frequency: int = 24  # hours
    feature_engineering: bool = True
    anomaly_detection: bool = True
    clustering: bool = True
    forecasting: bool = True

@dataclass
class PredictionResult:
    """Result of a prediction"""
    value: float
    confidence: float
    lower_bound: float
    upper_bound: float
    model_accuracy: float
    feature_importance: Dict[str, float]
    timestamp: datetime

@dataclass
class AnomalyResult:
    """Result of anomaly detection"""
    is_anomaly: bool
    anomaly_score: float
    anomaly_type: str
    confidence: float
    explanation: str
    timestamp: datetime

@dataclass
class ClusterResult:
    """Result of clustering analysis"""
    cluster_id: int
    cluster_size: int
    cluster_centroid: List[float]
    silhouette_score: float
    features: Dict[str, float]
    members: List[str]

class AdvancedAnalyticsService:
    """Advanced Analytics Service with ML and Predictive Analytics"""
    
    def __init__(self):
        self.config = AnalyticsConfig()
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.feature_importance = {}
        self.anomaly_threshold = 0.95
        self.cluster_models = {}
        self.prediction_cache = {}
        self.analytics_cache = {}
        
        # Initialize models
        self._initialize_models()
        
        logger.info("Advanced Analytics Service initialized")
    
    def _initialize_models(self):
        """Initialize ML models"""
        try:
            # Predictive models
            self.models['performance'] = {
                'regressor': RandomForestRegressor(n_estimators=100, random_state=42),
                'scaler': StandardScaler(),
                'features': ['cpu_usage', 'memory_usage', 'response_time', 'throughput']
            }
            
            self.models['user_behavior'] = {
                'regressor': GradientBoostingRegressor(n_estimators=100, random_state=42),
                'scaler': StandardScaler(),
                'features': ['session_duration', 'page_views', 'bounce_rate', 'conversion_rate']
            }
            
            self.models['content_quality'] = {
                'regressor': RandomForestRegressor(n_estimators=100, random_state=42),
                'scaler': StandardScaler(),
                'features': ['content_length', 'readability_score', 'engagement_rate', 'share_rate']
            }
            
            # Anomaly detection models
            self.models['anomaly'] = {
                'isolation_forest': None,  # Will be initialized when needed
                'scaler': StandardScaler(),
                'features': ['cpu_usage', 'memory_usage', 'response_time', 'error_rate']
            }
            
            # Clustering models
            self.cluster_models['user_segments'] = KMeans(n_clusters=5, random_state=42)
            self.cluster_models['content_categories'] = DBSCAN(eps=0.5, min_samples=5)
            
            logger.info("ML models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing models: {e}")
            raise
    
    async def collect_metrics(self, metric_type: MetricType, data: Dict[str, Any]) -> Dict[str, Any]:
        """Collect and process metrics"""
        try:
            timestamp = datetime.utcnow()
            
            # Process raw data
            processed_data = await self._process_metrics_data(metric_type, data)
            
            # Store in cache
            cache_key = f"{metric_type.value}_{timestamp.strftime('%Y%m%d_%H')}"
            if cache_key not in self.analytics_cache:
                self.analytics_cache[cache_key] = []
            
            self.analytics_cache[cache_key].append({
                'timestamp': timestamp,
                'data': processed_data,
                'metric_type': metric_type.value
            })
            
            # Trigger real-time analysis
            if self.config.auto_retrain:
                await self._trigger_real_time_analysis(metric_type, processed_data)
            
            return {
                'status': 'success',
                'timestamp': timestamp,
                'processed_data': processed_data,
                'cache_key': cache_key
            }
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _process_metrics_data(self, metric_type: MetricType, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw metrics data"""
        try:
            processed = {}
            
            if metric_type == MetricType.PERFORMANCE:
                processed = {
                    'cpu_usage': float(data.get('cpu_usage', 0)),
                    'memory_usage': float(data.get('memory_usage', 0)),
                    'response_time': float(data.get('response_time', 0)),
                    'throughput': float(data.get('throughput', 0)),
                    'error_rate': float(data.get('error_rate', 0))
                }
            
            elif metric_type == MetricType.USER_BEHAVIOR:
                processed = {
                    'session_duration': float(data.get('session_duration', 0)),
                    'page_views': int(data.get('page_views', 0)),
                    'bounce_rate': float(data.get('bounce_rate', 0)),
                    'conversion_rate': float(data.get('conversion_rate', 0)),
                    'user_id': data.get('user_id', '')
                }
            
            elif metric_type == MetricType.CONTENT_QUALITY:
                processed = {
                    'content_length': int(data.get('content_length', 0)),
                    'readability_score': float(data.get('readability_score', 0)),
                    'engagement_rate': float(data.get('engagement_rate', 0)),
                    'share_rate': float(data.get('share_rate', 0)),
                    'content_id': data.get('content_id', '')
                }
            
            # Add derived features
            processed = await self._add_derived_features(processed)
            
            return processed
            
        except Exception as e:
            logger.error(f"Error processing metrics data: {e}")
            return data
    
    async def _add_derived_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add derived features for better ML performance"""
        try:
            # Time-based features
            now = datetime.utcnow()
            data['hour'] = now.hour
            data['day_of_week'] = now.weekday()
            data['is_weekend'] = 1 if now.weekday() >= 5 else 0
            
            # Performance ratios
            if 'cpu_usage' in data and 'memory_usage' in data:
                data['cpu_memory_ratio'] = data['cpu_usage'] / (data['memory_usage'] + 1)
            
            if 'response_time' in data and 'throughput' in data:
                data['efficiency_score'] = data['throughput'] / (data['response_time'] + 1)
            
            # User behavior ratios
            if 'page_views' in data and 'session_duration' in data:
                data['pages_per_minute'] = data['page_views'] / (data['session_duration'] / 60 + 1)
            
            if 'bounce_rate' in data and 'conversion_rate' in data:
                data['engagement_score'] = (1 - data['bounce_rate']) * data['conversion_rate']
            
            return data
            
        except Exception as e:
            logger.error(f"Error adding derived features: {e}")
            return data
    
    async def predict_metrics(self, metric_type: MetricType, horizon: int = None) -> PredictionResult:
        """Predict future metrics using ML models"""
        try:
            if horizon is None:
                horizon = self.config.prediction_horizon
            
            # Get historical data
            historical_data = await self._get_historical_data(metric_type)
            
            if len(historical_data) < self.config.min_data_points:
                raise ValueError(f"Insufficient data for prediction. Need at least {self.config.min_data_points} data points")
            
            # Prepare features
            features = await self._prepare_features(historical_data, metric_type)
            
            # Train model if needed
            if metric_type.value not in self.models:
                await self._train_model(metric_type, features)
            
            # Make prediction
            model_info = self.models[metric_type.value]
            prediction = model_info['regressor'].predict([features[-1]])[0]
            
            # Calculate confidence intervals
            confidence = await self._calculate_confidence_interval(model_info, features)
            
            # Get feature importance
            feature_importance = await self._get_feature_importance(model_info)
            
            result = PredictionResult(
                value=prediction,
                confidence=confidence,
                lower_bound=prediction - (confidence * 2),
                upper_bound=prediction + (confidence * 2),
                model_accuracy=await self._calculate_model_accuracy(model_info, features),
                feature_importance=feature_importance,
                timestamp=datetime.utcnow()
            )
            
            # Cache prediction
            cache_key = f"prediction_{metric_type.value}_{horizon}"
            self.prediction_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Error predicting metrics: {e}")
            raise
    
    async def detect_anomalies(self, metric_type: MetricType, data: Dict[str, Any]) -> AnomalyResult:
        """Detect anomalies in metrics using ML"""
        try:
            # Prepare features
            features = await self._prepare_features([data], metric_type)
            
            # Get anomaly model
            if 'anomaly' not in self.models:
                await self._initialize_anomaly_model()
            
            anomaly_model = self.models['anomaly']
            
            # Calculate anomaly score
            anomaly_score = await self._calculate_anomaly_score(anomaly_model, features[0])
            
            # Determine if anomaly
            is_anomaly = anomaly_score > self.anomaly_threshold
            
            # Classify anomaly type
            anomaly_type = await self._classify_anomaly_type(anomaly_score, features[0])
            
            # Generate explanation
            explanation = await self._generate_anomaly_explanation(anomaly_type, features[0])
            
            result = AnomalyResult(
                is_anomaly=is_anomaly,
                anomaly_score=anomaly_score,
                anomaly_type=anomaly_type,
                confidence=anomaly_score,
                explanation=explanation,
                timestamp=datetime.utcnow()
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            raise
    
    async def perform_clustering(self, metric_type: MetricType, data: List[Dict[str, Any]]) -> List[ClusterResult]:
        """Perform clustering analysis on metrics data"""
        try:
            # Prepare features
            features_matrix = []
            for item in data:
                features = await self._prepare_features([item], metric_type)
                features_matrix.append(features[0])
            
            features_matrix = np.array(features_matrix)
            
            # Get cluster model
            cluster_model = self.cluster_models.get(f"{metric_type.value}_clusters")
            if cluster_model is None:
                cluster_model = KMeans(n_clusters=5, random_state=42)
                self.cluster_models[f"{metric_type.value}_clusters"] = cluster_model
            
            # Perform clustering
            cluster_labels = cluster_model.fit_predict(features_matrix)
            
            # Calculate silhouette score
            silhouette_avg = silhouette_score(features_matrix, cluster_labels)
            
            # Create cluster results
            results = []
            for cluster_id in range(cluster_model.n_clusters):
                cluster_mask = cluster_labels == cluster_id
                cluster_data = features_matrix[cluster_mask]
                
                if len(cluster_data) > 0:
                    cluster_centroid = cluster_model.cluster_centers_[cluster_id].tolist()
                    
                    result = ClusterResult(
                        cluster_id=cluster_id,
                        cluster_size=int(np.sum(cluster_mask)),
                        cluster_centroid=cluster_centroid,
                        silhouette_score=silhouette_avg,
                        features=await self._extract_cluster_features(cluster_data),
                        members=[str(i) for i in np.where(cluster_mask)[0]]
                    )
                    results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error performing clustering: {e}")
            raise
    
    async def generate_analytics_report(self, metric_type: MetricType, period: str = "7d") -> Dict[str, Any]:
        """Generate comprehensive analytics report"""
        try:
            # Get data for period
            data = await self._get_historical_data(metric_type, period)
            
            if not data:
                return {'error': 'No data available for the specified period'}
            
            # Basic statistics
            stats = await self._calculate_basic_statistics(data)
            
            # Trends
            trends = await self._analyze_trends(data)
            
            # Predictions
            predictions = await self._generate_predictions(metric_type, data)
            
            # Anomalies
            anomalies = await self._detect_anomalies_in_data(data, metric_type)
            
            # Clustering
            clusters = await self.perform_clustering(metric_type, data)
            
            # Visualizations
            visualizations = await self._generate_visualizations(data, metric_type)
            
            report = {
                'metric_type': metric_type.value,
                'period': period,
                'generated_at': datetime.utcnow().isoformat(),
                'data_points': len(data),
                'statistics': stats,
                'trends': trends,
                'predictions': predictions,
                'anomalies': anomalies,
                'clusters': [cluster.__dict__ for cluster in clusters],
                'visualizations': visualizations,
                'insights': await self._generate_insights(stats, trends, predictions, anomalies)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating analytics report: {e}")
            return {'error': str(e)}
    
    async def _get_historical_data(self, metric_type: MetricType, period: str = None) -> List[Dict[str, Any]]:
        """Get historical data for analysis"""
        try:
            # This would typically query a database
            # For now, return cached data
            data = []
            
            for cache_key, cache_data in self.analytics_cache.items():
                if metric_type.value in cache_key:
                    data.extend(cache_data)
            
            # Sort by timestamp
            data.sort(key=lambda x: x['timestamp'])
            
            # Filter by period if specified
            if period:
                end_time = datetime.utcnow()
                if period.endswith('d'):
                    days = int(period[:-1])
                    start_time = end_time - timedelta(days=days)
                elif period.endswith('h'):
                    hours = int(period[:-1])
                    start_time = end_time - timedelta(hours=hours)
                else:
                    start_time = end_time - timedelta(days=7)
                
                data = [item for item in data if item['timestamp'] >= start_time]
            
            return data
            
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return []
    
    async def _prepare_features(self, data: List[Dict[str, Any]], metric_type: MetricType) -> List[List[float]]:
        """Prepare features for ML models"""
        try:
            features = []
            
            for item in data:
                feature_vector = []
                
                if metric_type == MetricType.PERFORMANCE:
                    feature_vector = [
                        item.get('cpu_usage', 0),
                        item.get('memory_usage', 0),
                        item.get('response_time', 0),
                        item.get('throughput', 0),
                        item.get('error_rate', 0),
                        item.get('hour', 0),
                        item.get('day_of_week', 0),
                        item.get('is_weekend', 0)
                    ]
                
                elif metric_type == MetricType.USER_BEHAVIOR:
                    feature_vector = [
                        item.get('session_duration', 0),
                        item.get('page_views', 0),
                        item.get('bounce_rate', 0),
                        item.get('conversion_rate', 0),
                        item.get('hour', 0),
                        item.get('day_of_week', 0),
                        item.get('is_weekend', 0)
                    ]
                
                elif metric_type == MetricType.CONTENT_QUALITY:
                    feature_vector = [
                        item.get('content_length', 0),
                        item.get('readability_score', 0),
                        item.get('engagement_rate', 0),
                        item.get('share_rate', 0),
                        item.get('hour', 0),
                        item.get('day_of_week', 0),
                        item.get('is_weekend', 0)
                    ]
                
                features.append(feature_vector)
            
            return features
            
        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            return []
    
    async def _train_model(self, metric_type: MetricType, features: List[List[float]]):
        """Train ML model for specific metric type"""
        try:
            if len(features) < self.config.min_data_points:
                logger.warning(f"Insufficient data to train model for {metric_type.value}")
                return
            
            # Prepare training data
            X = np.array(features[:-1])  # All but last
            y = np.array([f[0] for f in features[1:]])  # Target is first feature of next time step
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train model
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = model.predict(X_test_scaled)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # Store model
            self.models[metric_type.value] = {
                'regressor': model,
                'scaler': scaler,
                'mse': mse,
                'r2': r2,
                'features': features[0] if features else []
            }
            
            logger.info(f"Model trained for {metric_type.value}: MSE={mse:.4f}, R2={r2:.4f}")
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
            raise
    
    async def _calculate_confidence_interval(self, model_info: Dict, features: List[float]) -> float:
        """Calculate confidence interval for prediction"""
        try:
            # Use model's R2 score as confidence measure
            r2 = model_info.get('r2', 0.5)
            confidence = min(0.95, max(0.1, r2))
            return confidence
            
        except Exception as e:
            logger.error(f"Error calculating confidence interval: {e}")
            return 0.5
    
    async def _get_feature_importance(self, model_info: Dict) -> Dict[str, float]:
        """Get feature importance from trained model"""
        try:
            model = model_info.get('regressor')
            if model and hasattr(model, 'feature_importances_'):
                importance = model.feature_importances_
                feature_names = model_info.get('features', [f'feature_{i}' for i in range(len(importance))])
                return dict(zip(feature_names, importance.tolist()))
            return {}
            
        except Exception as e:
            logger.error(f"Error getting feature importance: {e}")
            return {}
    
    async def _calculate_model_accuracy(self, model_info: Dict, features: List[List[float]]) -> float:
        """Calculate model accuracy"""
        try:
            r2 = model_info.get('r2', 0.5)
            return r2
            
        except Exception as e:
            logger.error(f"Error calculating model accuracy: {e}")
            return 0.5
    
    async def _initialize_anomaly_model(self):
        """Initialize anomaly detection model"""
        try:
            from sklearn.ensemble import IsolationForest
            
            self.models['anomaly'] = {
                'isolation_forest': IsolationForest(contamination=0.1, random_state=42),
                'scaler': StandardScaler(),
                'features': []
            }
            
        except Exception as e:
            logger.error(f"Error initializing anomaly model: {e}")
            raise
    
    async def _calculate_anomaly_score(self, anomaly_model: Dict, features: List[float]) -> float:
        """Calculate anomaly score for given features"""
        try:
            isolation_forest = anomaly_model.get('isolation_forest')
            if isolation_forest is None:
                return 0.0
            
            # Scale features
            scaler = anomaly_model.get('scaler')
            features_scaled = scaler.fit_transform([features])
            
            # Calculate anomaly score
            score = isolation_forest.decision_function(features_scaled)[0]
            
            # Normalize to 0-1 range
            normalized_score = (score - score.min()) / (score.max() - score.min() + 1e-8)
            
            return float(normalized_score)
            
        except Exception as e:
            logger.error(f"Error calculating anomaly score: {e}")
            return 0.0
    
    async def _classify_anomaly_type(self, anomaly_score: float, features: List[float]) -> str:
        """Classify the type of anomaly"""
        try:
            if anomaly_score > 0.9:
                return "critical"
            elif anomaly_score > 0.7:
                return "major"
            elif anomaly_score > 0.5:
                return "minor"
            else:
                return "normal"
                
        except Exception as e:
            logger.error(f"Error classifying anomaly type: {e}")
            return "unknown"
    
    async def _generate_anomaly_explanation(self, anomaly_type: str, features: List[float]) -> str:
        """Generate explanation for anomaly"""
        try:
            explanations = {
                "critical": "Critical anomaly detected. Immediate attention required.",
                "major": "Major anomaly detected. Investigation recommended.",
                "minor": "Minor anomaly detected. Monitor closely.",
                "normal": "No anomaly detected. System operating normally."
            }
            
            return explanations.get(anomaly_type, "Anomaly type unknown.")
            
        except Exception as e:
            logger.error(f"Error generating anomaly explanation: {e}")
            return "Error generating explanation."
    
    async def _extract_cluster_features(self, cluster_data: np.ndarray) -> Dict[str, float]:
        """Extract features from cluster data"""
        try:
            features = {}
            
            for i in range(cluster_data.shape[1]):
                feature_name = f'feature_{i}'
                features[feature_name] = {
                    'mean': float(np.mean(cluster_data[:, i])),
                    'std': float(np.std(cluster_data[:, i])),
                    'min': float(np.min(cluster_data[:, i])),
                    'max': float(np.max(cluster_data[:, i]))
                }
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting cluster features: {e}")
            return {}
    
    async def _calculate_basic_statistics(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate basic statistics for data"""
        try:
            if not data:
                return {}
            
            # Extract numeric values
            numeric_data = {}
            for item in data:
                for key, value in item.items():
                    if isinstance(value, (int, float)):
                        if key not in numeric_data:
                            numeric_data[key] = []
                        numeric_data[key].append(value)
            
            # Calculate statistics
            stats = {}
            for key, values in numeric_data.items():
                if values:
                    stats[key] = {
                        'count': len(values),
                        'mean': float(np.mean(values)),
                        'median': float(np.median(values)),
                        'std': float(np.std(values)),
                        'min': float(np.min(values)),
                        'max': float(np.max(values)),
                        'q25': float(np.percentile(values, 25)),
                        'q75': float(np.percentile(values, 75))
                    }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating basic statistics: {e}")
            return {}
    
    async def _analyze_trends(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trends in data"""
        try:
            if len(data) < 2:
                return {}
            
            # Extract numeric values
            numeric_data = {}
            for item in data:
                for key, value in item.items():
                    if isinstance(value, (int, float)):
                        if key not in numeric_data:
                            numeric_data[key] = []
                        numeric_data[key].append(value)
            
            # Calculate trends
            trends = {}
            for key, values in numeric_data.items():
                if len(values) >= 2:
                    # Simple linear trend
                    x = np.arange(len(values))
                    slope, intercept = np.polyfit(x, values, 1)
                    
                    trends[key] = {
                        'slope': float(slope),
                        'intercept': float(intercept),
                        'trend_direction': 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable',
                        'trend_strength': abs(float(slope))
                    }
            
            return trends
            
        except Exception as e:
            logger.error(f"Error analyzing trends: {e}")
            return {}
    
    async def _generate_predictions(self, metric_type: MetricType, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate predictions for future values"""
        try:
            if len(data) < self.config.min_data_points:
                return {}
            
            # Get prediction
            prediction = await self.predict_metrics(metric_type)
            
            return {
                'predicted_value': prediction.value,
                'confidence': prediction.confidence,
                'lower_bound': prediction.lower_bound,
                'upper_bound': prediction.upper_bound,
                'model_accuracy': prediction.model_accuracy,
                'feature_importance': prediction.feature_importance
            }
            
        except Exception as e:
            logger.error(f"Error generating predictions: {e}")
            return {}
    
    async def _detect_anomalies_in_data(self, data: List[Dict[str, Any]], metric_type: MetricType) -> List[Dict[str, Any]]:
        """Detect anomalies in historical data"""
        try:
            anomalies = []
            
            for item in data:
                anomaly_result = await self.detect_anomalies(metric_type, item)
                
                if anomaly_result.is_anomaly:
                    anomalies.append({
                        'timestamp': item.get('timestamp', datetime.utcnow()).isoformat(),
                        'anomaly_score': anomaly_result.anomaly_score,
                        'anomaly_type': anomaly_result.anomaly_type,
                        'confidence': anomaly_result.confidence,
                        'explanation': anomaly_result.explanation
                    })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting anomalies in data: {e}")
            return []
    
    async def _generate_visualizations(self, data: List[Dict[str, Any]], metric_type: MetricType) -> Dict[str, str]:
        """Generate visualizations for data"""
        try:
            visualizations = {}
            
            # Time series plot
            if data:
                timestamps = [item.get('timestamp', datetime.utcnow()) for item in data]
                numeric_data = {}
                
                for item in data:
                    for key, value in item.items():
                        if isinstance(value, (int, float)):
                            if key not in numeric_data:
                                numeric_data[key] = []
                            numeric_data[key].append(value)
                
                # Create time series plot
                fig = make_subplots(rows=len(numeric_data), cols=1, subplot_titles=list(numeric_data.keys()))
                
                for i, (key, values) in enumerate(numeric_data.items()):
                    fig.add_trace(
                        go.Scatter(x=timestamps, y=values, mode='lines', name=key),
                        row=i+1, col=1
                    )
                
                fig.update_layout(height=200 * len(numeric_data), title=f"{metric_type.value} Metrics Over Time")
                visualizations['time_series'] = fig.to_html()
            
            return visualizations
            
        except Exception as e:
            logger.error(f"Error generating visualizations: {e}")
            return {}
    
    async def _generate_insights(self, stats: Dict, trends: Dict, predictions: Dict, anomalies: List) -> List[str]:
        """Generate insights from analysis"""
        try:
            insights = []
            
            # Performance insights
            if 'cpu_usage' in stats:
                cpu_mean = stats['cpu_usage']['mean']
                if cpu_mean > 80:
                    insights.append("High CPU usage detected. Consider scaling or optimization.")
                elif cpu_mean < 20:
                    insights.append("Low CPU usage. System may be underutilized.")
            
            # Trend insights
            for key, trend in trends.items():
                if trend['trend_direction'] == 'increasing' and trend['trend_strength'] > 0.1:
                    insights.append(f"{key} is showing a strong increasing trend.")
                elif trend['trend_direction'] == 'decreasing' and trend['trend_strength'] > 0.1:
                    insights.append(f"{key} is showing a strong decreasing trend.")
            
            # Anomaly insights
            if anomalies:
                critical_anomalies = [a for a in anomalies if a['anomaly_type'] == 'critical']
                if critical_anomalies:
                    insights.append(f"{len(critical_anomalies)} critical anomalies detected.")
            
            # Prediction insights
            if predictions:
                confidence = predictions.get('confidence', 0)
                if confidence > 0.8:
                    insights.append("High confidence predictions available.")
                elif confidence < 0.5:
                    insights.append("Low confidence predictions. More data needed.")
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return []
    
    async def _trigger_real_time_analysis(self, metric_type: MetricType, data: Dict[str, Any]):
        """Trigger real-time analysis"""
        try:
            # Detect anomalies
            anomaly_result = await self.detect_anomalies(metric_type, data)
            
            if anomaly_result.is_anomaly:
                logger.warning(f"Anomaly detected: {anomaly_result.explanation}")
                
                # Send alert
                await self._send_anomaly_alert(anomaly_result)
            
            # Update models if needed
            if self.config.auto_retrain:
                await self._check_retrain_models(metric_type)
            
        except Exception as e:
            logger.error(f"Error in real-time analysis: {e}")
    
    async def _send_anomaly_alert(self, anomaly_result: AnomalyResult):
        """Send anomaly alert"""
        try:
            # This would typically send to notification service
            logger.warning(f"Anomaly Alert: {anomaly_result.explanation}")
            
        except Exception as e:
            logger.error(f"Error sending anomaly alert: {e}")
    
    async def _check_retrain_models(self, metric_type: MetricType):
        """Check if models need retraining"""
        try:
            # Check if enough time has passed since last training
            last_training = getattr(self, f'_last_training_{metric_type.value}', datetime.min)
            now = datetime.utcnow()
            
            if (now - last_training).total_seconds() > (self.config.retrain_frequency * 3600):
                # Retrain model
                historical_data = await self._get_historical_data(metric_type)
                if len(historical_data) >= self.config.min_data_points:
                    features = await self._prepare_features(historical_data, metric_type)
                    await self._train_model(metric_type, features)
                    setattr(self, f'_last_training_{metric_type.value}', now)
            
        except Exception as e:
            logger.error(f"Error checking retrain models: {e}")
    
    async def get_analytics_dashboard_data(self) -> Dict[str, Any]:
        """Get data for analytics dashboard"""
        try:
            dashboard_data = {
                'real_time_metrics': await self._get_real_time_metrics(),
                'predictions': await self._get_recent_predictions(),
                'anomalies': await self._get_recent_anomalies(),
                'trends': await self._get_current_trends(),
                'clusters': await self._get_current_clusters(),
                'insights': await self._get_current_insights()
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return {}
    
    async def _get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time metrics"""
        try:
            # Get latest data from cache
            latest_data = {}
            
            for cache_key, cache_data in self.analytics_cache.items():
                if cache_data:
                    latest_item = max(cache_data, key=lambda x: x['timestamp'])
                    latest_data[cache_key] = latest_item['data']
            
            return latest_data
            
        except Exception as e:
            logger.error(f"Error getting real-time metrics: {e}")
            return {}
    
    async def _get_recent_predictions(self) -> List[Dict[str, Any]]:
        """Get recent predictions"""
        try:
            predictions = []
            
            for cache_key, prediction in self.prediction_cache.items():
                predictions.append({
                    'metric_type': cache_key.split('_')[1],
                    'predicted_value': prediction.value,
                    'confidence': prediction.confidence,
                    'timestamp': prediction.timestamp.isoformat()
                })
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error getting recent predictions: {e}")
            return []
    
    async def _get_recent_anomalies(self) -> List[Dict[str, Any]]:
        """Get recent anomalies"""
        try:
            # This would typically query a database
            # For now, return empty list
            return []
            
        except Exception as e:
            logger.error(f"Error getting recent anomalies: {e}")
            return []
    
    async def _get_current_trends(self) -> Dict[str, Any]:
        """Get current trends"""
        try:
            trends = {}
            
            for metric_type in MetricType:
                data = await self._get_historical_data(metric_type, "24h")
                if data:
                    trends[metric_type.value] = await self._analyze_trends(data)
            
            return trends
            
        except Exception as e:
            logger.error(f"Error getting current trends: {e}")
            return {}
    
    async def _get_current_clusters(self) -> Dict[str, Any]:
        """Get current clusters"""
        try:
            clusters = {}
            
            for metric_type in MetricType:
                data = await self._get_historical_data(metric_type, "7d")
                if len(data) >= 10:  # Minimum data for clustering
                    cluster_results = await self.perform_clustering(metric_type, data)
                    clusters[metric_type.value] = [cluster.__dict__ for cluster in cluster_results]
            
            return clusters
            
        except Exception as e:
            logger.error(f"Error getting current clusters: {e}")
            return {}
    
    async def _get_current_insights(self) -> List[str]:
        """Get current insights"""
        try:
            insights = []
            
            # Get insights from all metric types
            for metric_type in MetricType:
                data = await self._get_historical_data(metric_type, "7d")
                if data:
                    stats = await self._calculate_basic_statistics(data)
                    trends = await self._analyze_trends(data)
                    anomalies = await self._detect_anomalies_in_data(data, metric_type)
                    
                    metric_insights = await self._generate_insights(stats, trends, {}, anomalies)
                    insights.extend(metric_insights)
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting current insights: {e}")
            return []
    
    async def export_analytics_data(self, format: str = "json", period: str = "30d") -> str:
        """Export analytics data in specified format"""
        try:
            # Get data for period
            all_data = {}
            
            for metric_type in MetricType:
                data = await self._get_historical_data(metric_type, period)
                if data:
                    all_data[metric_type.value] = data
            
            if format.lower() == "json":
                return json.dumps(all_data, default=str, indent=2)
            elif format.lower() == "csv":
                # Convert to CSV format
                csv_data = []
                for metric_type, data in all_data.items():
                    for item in data:
                        row = {'metric_type': metric_type, 'timestamp': item['timestamp']}
                        row.update(item['data'])
                        csv_data.append(row)
                
                if csv_data:
                    df = pd.DataFrame(csv_data)
                    return df.to_csv(index=False)
                else:
                    return ""
            else:
                raise ValueError(f"Unsupported format: {format}")
            
        except Exception as e:
            logger.error(f"Error exporting analytics data: {e}")
            return ""
    
    async def cleanup_old_data(self, retention_days: int = 30):
        """Clean up old analytics data"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            # Clean cache
            keys_to_remove = []
            for cache_key, cache_data in self.analytics_cache.items():
                filtered_data = [item for item in cache_data if item['timestamp'] >= cutoff_date]
                if filtered_data:
                    self.analytics_cache[cache_key] = filtered_data
                else:
                    keys_to_remove.append(cache_key)
            
            for key in keys_to_remove:
                del self.analytics_cache[key]
            
            # Clean prediction cache
            pred_keys_to_remove = []
            for cache_key, prediction in self.prediction_cache.items():
                if prediction.timestamp < cutoff_date:
                    pred_keys_to_remove.append(cache_key)
            
            for key in pred_keys_to_remove:
                del self.prediction_cache[key]
            
            logger.info(f"Cleaned up analytics data older than {retention_days} days")
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get service status"""
        try:
            status = {
                'service': 'Advanced Analytics Service',
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'models_loaded': len(self.models),
                'cluster_models_loaded': len(self.cluster_models),
                'cache_size': len(self.analytics_cache),
                'prediction_cache_size': len(self.prediction_cache),
                'config': {
                    'window_size': self.config.window_size,
                    'prediction_horizon': self.config.prediction_horizon,
                    'confidence_level': self.config.confidence_level,
                    'min_data_points': self.config.min_data_points,
                    'auto_retrain': self.config.auto_retrain,
                    'retrain_frequency': self.config.retrain_frequency
                }
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting service status: {e}")
            return {
                'service': 'Advanced Analytics Service',
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }


























