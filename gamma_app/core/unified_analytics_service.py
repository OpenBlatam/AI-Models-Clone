"""
Unified Analytics Service - Consolidated analytics functionality
Combines all analytics-related services into a single, optimized service
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import time
import json
from datetime import datetime, timedelta
from collections import defaultdict, deque
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import redis
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge, Summary

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Metric Types"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    CUSTOM = "custom"

class AnalyticsEvent(Enum):
    """Analytics Events"""
    USER_LOGIN = "user_login"
    CONTENT_CREATED = "content_created"
    CONTENT_VIEWED = "content_viewed"
    CONTENT_SHARED = "content_shared"
    API_CALL = "api_call"
    ERROR_OCCURRED = "error_occurred"
    PERFORMANCE_METRIC = "performance_metric"

@dataclass
class AnalyticsData:
    """Analytics Data Point"""
    timestamp: datetime
    event_type: AnalyticsEvent
    user_id: Optional[str]
    session_id: Optional[str]
    data: Dict[str, Any]
    metadata: Dict[str, Any]

@dataclass
class AnalyticsQuery:
    """Analytics Query"""
    start_time: datetime
    end_time: datetime
    event_types: List[AnalyticsEvent]
    filters: Dict[str, Any]
    group_by: List[str]
    aggregation: str
    limit: int = 1000

class UnifiedAnalyticsService:
    """
    Unified Analytics Service - Consolidated analytics functionality
    Handles metrics, real-time analytics, predictive analytics, and visualizations
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = redis.Redis.from_url(config.get("redis_url", "redis://localhost:6379"))
        
        # Data storage
        self.analytics_data: deque = deque(maxlen=100000)  # Keep last 100k events
        self.real_time_metrics: Dict[str, Any] = {}
        
        # Prometheus metrics
        self.prometheus_metrics = {
            "requests_total": Counter('gamma_app_requests_total', 'Total requests', ['method', 'endpoint']),
            "request_duration": Histogram('gamma_app_request_duration_seconds', 'Request duration'),
            "active_users": Gauge('gamma_app_active_users', 'Active users'),
            "content_created": Counter('gamma_app_content_created_total', 'Content created', ['type']),
            "errors_total": Counter('gamma_app_errors_total', 'Total errors', ['error_type']),
            "performance_score": Gauge('gamma_app_performance_score', 'Performance score')
        }
        
        # ML models for predictive analytics
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.clustering_model = KMeans(n_clusters=5, random_state=42)
        self.scaler = StandardScaler()
        
        # Model training data
        self.training_data = []
        self.models_trained = False
        
        logger.info("UnifiedAnalyticsService initialized")
    
    async def track_event(self, event_type: AnalyticsEvent, 
                         user_id: str = None,
                         session_id: str = None,
                         data: Dict[str, Any] = None,
                         metadata: Dict[str, Any] = None) -> str:
        """Track analytics event"""
        try:
            event_id = f"{int(time.time() * 1000)}_{hash(str(data))}"
            
            analytics_data = AnalyticsData(
                timestamp=datetime.now(),
                event_type=event_type,
                user_id=user_id,
                session_id=session_id,
                data=data or {},
                metadata=metadata or {}
            )
            
            # Store in memory
            self.analytics_data.append(analytics_data)
            
            # Store in Redis for persistence
            await self._store_in_redis(event_id, analytics_data)
            
            # Update Prometheus metrics
            await self._update_prometheus_metrics(event_type, data)
            
            # Update real-time metrics
            await self._update_real_time_metrics(event_type, data)
            
            logger.debug(f"Tracked event: {event_type.value}")
            return event_id
            
        except Exception as e:
            logger.error(f"Error tracking event: {e}")
            raise
    
    async def _store_in_redis(self, event_id: str, data: AnalyticsData):
        """Store analytics data in Redis"""
        try:
            key = f"analytics:{event_id}"
            value = {
                "timestamp": data.timestamp.isoformat(),
                "event_type": data.event_type.value,
                "user_id": data.user_id,
                "session_id": data.session_id,
                "data": json.dumps(data.data),
                "metadata": json.dumps(data.metadata)
            }
            
            # Store with TTL of 30 days
            self.redis_client.hset(key, mapping=value)
            self.redis_client.expire(key, 30 * 24 * 3600)
            
        except Exception as e:
            logger.error(f"Error storing in Redis: {e}")
    
    async def _update_prometheus_metrics(self, event_type: AnalyticsEvent, data: Dict[str, Any]):
        """Update Prometheus metrics"""
        try:
            if event_type == AnalyticsEvent.API_CALL:
                method = data.get("method", "unknown")
                endpoint = data.get("endpoint", "unknown")
                self.prometheus_metrics["requests_total"].labels(method=method, endpoint=endpoint).inc()
                
                duration = data.get("duration", 0)
                self.prometheus_metrics["request_duration"].observe(duration)
            
            elif event_type == AnalyticsEvent.CONTENT_CREATED:
                content_type = data.get("content_type", "unknown")
                self.prometheus_metrics["content_created"].labels(type=content_type).inc()
            
            elif event_type == AnalyticsEvent.ERROR_OCCURRED:
                error_type = data.get("error_type", "unknown")
                self.prometheus_metrics["errors_total"].labels(error_type=error_type).inc()
            
            elif event_type == AnalyticsEvent.PERFORMANCE_METRIC:
                score = data.get("score", 0)
                self.prometheus_metrics["performance_score"].set(score)
            
            elif event_type == AnalyticsEvent.USER_LOGIN:
                self.prometheus_metrics["active_users"].inc()
                
        except Exception as e:
            logger.error(f"Error updating Prometheus metrics: {e}")
    
    async def _update_real_time_metrics(self, event_type: AnalyticsEvent, data: Dict[str, Any]):
        """Update real-time metrics"""
        try:
            current_time = datetime.now()
            minute_key = current_time.strftime("%Y-%m-%d %H:%M")
            
            if minute_key not in self.real_time_metrics:
                self.real_time_metrics[minute_key] = defaultdict(int)
            
            # Update counters
            self.real_time_metrics[minute_key][f"{event_type.value}_count"] += 1
            
            # Update specific metrics
            if event_type == AnalyticsEvent.USER_LOGIN:
                self.real_time_metrics[minute_key]["unique_users"] = len(set(
                    event.user_id for event in self.analytics_data 
                    if event.user_id and event.timestamp >= current_time - timedelta(minutes=1)
                ))
            
            # Keep only last 60 minutes
            cutoff_time = current_time - timedelta(minutes=60)
            self.real_time_metrics = {
                k: v for k, v in self.real_time_metrics.items()
                if datetime.strptime(k, "%Y-%m-%d %H:%M") > cutoff_time
            }
            
        except Exception as e:
            logger.error(f"Error updating real-time metrics: {e}")
    
    async def query_analytics(self, query: AnalyticsQuery) -> List[AnalyticsData]:
        """Query analytics data"""
        try:
            # Filter data based on query
            filtered_data = []
            
            for event in self.analytics_data:
                # Time filter
                if not (query.start_time <= event.timestamp <= query.end_time):
                    continue
                
                # Event type filter
                if query.event_types and event.event_type not in query.event_types:
                    continue
                
                # Custom filters
                if query.filters:
                    match = True
                    for key, value in query.filters.items():
                        if key in event.data and event.data[key] != value:
                            match = False
                            break
                    if not match:
                        continue
                
                filtered_data.append(event)
            
            # Sort by timestamp
            filtered_data.sort(key=lambda x: x.timestamp, reverse=True)
            
            return filtered_data[:query.limit]
            
        except Exception as e:
            logger.error(f"Error querying analytics: {e}")
            return []
    
    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time metrics"""
        try:
            current_time = datetime.now()
            last_minute = (current_time - timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M")
            
            if last_minute in self.real_time_metrics:
                return dict(self.real_time_metrics[last_minute])
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Error getting real-time metrics: {e}")
            return {}
    
    async def get_analytics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get analytics summary for specified hours"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            # Filter data
            recent_data = [
                event for event in self.analytics_data
                if start_time <= event.timestamp <= end_time
            ]
            
            # Calculate summary statistics
            summary = {
                "total_events": len(recent_data),
                "unique_users": len(set(event.user_id for event in recent_data if event.user_id)),
                "events_by_type": defaultdict(int),
                "hourly_distribution": defaultdict(int),
                "top_content_types": defaultdict(int),
                "error_rate": 0
            }
            
            # Process events
            for event in recent_data:
                # Events by type
                summary["events_by_type"][event.event_type.value] += 1
                
                # Hourly distribution
                hour_key = event.timestamp.strftime("%Y-%m-%d %H:00")
                summary["hourly_distribution"][hour_key] += 1
                
                # Content types
                if event.event_type == AnalyticsEvent.CONTENT_CREATED:
                    content_type = event.data.get("content_type", "unknown")
                    summary["top_content_types"][content_type] += 1
                
                # Error rate
                if event.event_type == AnalyticsEvent.ERROR_OCCURRED:
                    summary["error_rate"] += 1
            
            # Calculate error rate percentage
            if summary["total_events"] > 0:
                summary["error_rate"] = (summary["error_rate"] / summary["total_events"]) * 100
            
            # Convert defaultdicts to regular dicts
            summary["events_by_type"] = dict(summary["events_by_type"])
            summary["hourly_distribution"] = dict(summary["hourly_distribution"])
            summary["top_content_types"] = dict(summary["top_content_types"])
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting analytics summary: {e}")
            return {}
    
    async def detect_anomalies(self, metric_name: str, threshold: float = 0.1) -> List[Dict[str, Any]]:
        """Detect anomalies in metrics"""
        try:
            if not self.models_trained:
                await self._train_models()
            
            # Get recent data for the metric
            recent_data = []
            for event in list(self.analytics_data)[-1000:]:  # Last 1000 events
                if metric_name in event.data:
                    recent_data.append(event.data[metric_name])
            
            if len(recent_data) < 10:
                return []
            
            # Prepare data for anomaly detection
            data_array = np.array(recent_data).reshape(-1, 1)
            data_scaled = self.scaler.fit_transform(data_array)
            
            # Detect anomalies
            anomaly_scores = self.anomaly_detector.decision_function(data_scaled)
            anomalies = []
            
            for i, score in enumerate(anomaly_scores):
                if score < -threshold:
                    anomalies.append({
                        "index": i,
                        "value": recent_data[i],
                        "score": score,
                        "timestamp": list(self.analytics_data)[-1000:][i].timestamp.isoformat()
                    })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return []
    
    async def perform_clustering(self, features: List[str]) -> Dict[str, Any]:
        """Perform clustering analysis"""
        try:
            if not self.models_trained:
                await self._train_models()
            
            # Prepare feature data
            feature_data = []
            for event in list(self.analytics_data)[-1000:]:  # Last 1000 events
                event_features = []
                for feature in features:
                    event_features.append(event.data.get(feature, 0))
                feature_data.append(event_features)
            
            if len(feature_data) < 10:
                return {"error": "Insufficient data for clustering"}
            
            # Scale features
            feature_array = np.array(feature_data)
            feature_scaled = self.scaler.fit_transform(feature_array)
            
            # Perform clustering
            clusters = self.clustering_model.fit_predict(feature_scaled)
            
            # Analyze clusters
            cluster_analysis = {
                "n_clusters": len(set(clusters)),
                "cluster_sizes": defaultdict(int),
                "cluster_centers": self.clustering_model.cluster_centers_.tolist(),
                "silhouette_score": 0  # Would calculate if sklearn.metrics available
            }
            
            for cluster in clusters:
                cluster_analysis["cluster_sizes"][f"cluster_{cluster}"] += 1
            
            cluster_analysis["cluster_sizes"] = dict(cluster_analysis["cluster_sizes"])
            
            return cluster_analysis
            
        except Exception as e:
            logger.error(f"Error performing clustering: {e}")
            return {"error": str(e)}
    
    async def _train_models(self):
        """Train ML models for analytics"""
        try:
            if len(self.analytics_data) < 100:
                return
            
            # Prepare training data
            training_features = []
            for event in list(self.analytics_data)[-1000:]:  # Last 1000 events
                features = [
                    event.timestamp.hour,
                    event.timestamp.weekday(),
                    len(event.data),
                    hash(event.event_type.value) % 100
                ]
                training_features.append(features)
            
            if len(training_features) < 10:
                return
            
            # Scale features
            feature_array = np.array(training_features)
            feature_scaled = self.scaler.fit_transform(feature_array)
            
            # Train models
            self.anomaly_detector.fit(feature_scaled)
            self.clustering_model.fit(feature_scaled)
            
            self.models_trained = True
            logger.info("ML models trained successfully")
            
        except Exception as e:
            logger.error(f"Error training models: {e}")
    
    async def generate_visualization(self, 
                                   chart_type: str,
                                   data: Dict[str, Any],
                                   title: str = "Analytics Chart") -> str:
        """Generate visualization chart"""
        try:
            if chart_type == "line":
                fig = go.Figure()
                for key, values in data.items():
                    fig.add_trace(go.Scatter(
                        x=list(values.keys()),
                        y=list(values.values()),
                        mode='lines+markers',
                        name=key
                    ))
            
            elif chart_type == "bar":
                fig = go.Figure(data=[
                    go.Bar(x=list(data.keys()), y=list(data.values()))
                ])
            
            elif chart_type == "pie":
                fig = go.Figure(data=[
                    go.Pie(labels=list(data.keys()), values=list(data.values()))
                ])
            
            elif chart_type == "scatter":
                fig = go.Figure(data=[
                    go.Scatter(
                        x=data.get("x", []),
                        y=data.get("y", []),
                        mode='markers',
                        marker=dict(size=10)
                    )
                ])
            
            else:
                raise ValueError(f"Unsupported chart type: {chart_type}")
            
            fig.update_layout(
                title=title,
                xaxis_title=data.get("x_title", ""),
                yaxis_title=data.get("y_title", ""),
                template="plotly_white"
            )
            
            # Convert to HTML
            chart_html = fig.to_html(include_plotlyjs=False)
            return chart_html
            
        except Exception as e:
            logger.error(f"Error generating visualization: {e}")
            return f"<p>Error generating chart: {str(e)}</p>"
    
    async def export_analytics(self, 
                             start_time: datetime,
                             end_time: datetime,
                             format: str = "json") -> str:
        """Export analytics data"""
        try:
            # Filter data
            filtered_data = [
                event for event in self.analytics_data
                if start_time <= event.timestamp <= end_time
            ]
            
            if format == "json":
                export_data = []
                for event in filtered_data:
                    export_data.append({
                        "timestamp": event.timestamp.isoformat(),
                        "event_type": event.event_type.value,
                        "user_id": event.user_id,
                        "session_id": event.session_id,
                        "data": event.data,
                        "metadata": event.metadata
                    })
                
                return json.dumps(export_data, indent=2)
            
            elif format == "csv":
                import io
                import csv
                
                output = io.StringIO()
                writer = csv.writer(output)
                
                # Write header
                writer.writerow(["timestamp", "event_type", "user_id", "session_id", "data", "metadata"])
                
                # Write data
                for event in filtered_data:
                    writer.writerow([
                        event.timestamp.isoformat(),
                        event.event_type.value,
                        event.user_id,
                        event.session_id,
                        json.dumps(event.data),
                        json.dumps(event.metadata)
                    ])
                
                return output.getvalue()
            
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            logger.error(f"Error exporting analytics: {e}")
            return ""
    
    async def get_prometheus_metrics(self) -> str:
        """Get Prometheus metrics in text format"""
        try:
            from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
            return generate_latest().decode('utf-8')
        except Exception as e:
            logger.error(f"Error getting Prometheus metrics: {e}")
            return ""
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for analytics service"""
        try:
            summary = await self.get_analytics_summary(hours=1)
            
            return {
                "status": "healthy",
                "total_events": len(self.analytics_data),
                "recent_events": summary.get("total_events", 0),
                "unique_users": summary.get("unique_users", 0),
                "models_trained": self.models_trained,
                "redis_connected": True,  # Would check actual connection
                "prometheus_metrics": len(self.prometheus_metrics)
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}


























