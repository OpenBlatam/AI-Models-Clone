#!/usr/bin/env python3
"""
Intelligent Model Recommendation Engine
AI-powered model selection, recommendation, and optimization guidance
"""

import logging
import time
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import pandas as pd
from collections import defaultdict, deque
import uuid
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import cross_val_score
from sklearn.metrics import mean_squared_error, r2_score
import joblib
from pathlib import Path

# ===== ENHANCED ENUMS =====

class RecommendationType(Enum):
    """Recommendation type enumeration."""
    MODEL_SELECTION = "model_selection"
    HYPERPARAMETER_TUNING = "hyperparameter_tuning"
    FEATURE_ENGINEERING = "feature_engineering"
    DATA_PREPROCESSING = "data_preprocessing"
    DEPLOYMENT_STRATEGY = "deployment_strategy"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"

class RecommendationConfidence(Enum):
    """Recommendation confidence level."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

class ProblemType(Enum):
    """Problem type enumeration."""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    TIME_SERIES = "time_series"
    NLP = "nlp"
    COMPUTER_VISION = "computer_vision"
    RECOMMENDATION = "recommendation"
    ANOMALY_DETECTION = "anomaly_detection"

class DataCharacteristics(Enum):
    """Data characteristics enumeration."""
    SMALL_DATASET = "small_dataset"
    LARGE_DATASET = "large_dataset"
    HIGH_DIMENSIONAL = "high_dimensional"
    SPARSE = "sparse"
    IMBALANCED = "imbalanced"
    NOISY = "noisy"
    MISSING_VALUES = "missing_values"
    CATEGORICAL = "categorical"
    NUMERICAL = "numerical"
    TEXT = "text"
    IMAGE = "image"
    TIME_SERIES = "time_series"

# ===== ENHANCED CONFIGURATION =====

@dataclass
class RecommendationConfig:
    """Configuration for the recommendation engine."""
    model_database_path: str = "./model_database"
    recommendation_cache_size: int = 1000
    learning_enabled: bool = True
    feedback_enabled: bool = True
    auto_learning: bool = True
    confidence_threshold: float = 0.7
    max_recommendations: int = 5
    update_interval_hours: int = 24

@dataclass
class ModelProfile:
    """Model profile for recommendation."""
    model_id: str
    name: str
    algorithm: str
    problem_type: ProblemType
    performance_metrics: Dict[str, float]
    data_characteristics: List[DataCharacteristics]
    hyperparameters: Dict[str, Any]
    training_time: float
    inference_time: float
    memory_usage: float
    complexity_score: float
    popularity_score: float
    success_rate: float
    created_at: datetime
    last_updated: datetime

@dataclass
class Recommendation:
    """Model recommendation."""
    recommendation_id: str
    type: RecommendationType
    model_id: str
    confidence: RecommendationConfidence
    confidence_score: float
    reasoning: str
    expected_performance: Dict[str, float]
    trade_offs: List[str]
    alternatives: List[str]
    created_at: datetime

@dataclass
class UserContext:
    """User context for recommendations."""
    user_id: str
    problem_type: ProblemType
    data_characteristics: List[DataCharacteristics]
    performance_requirements: Dict[str, float]
    resource_constraints: Dict[str, Any]
    preferences: Dict[str, Any]
    historical_performance: Dict[str, float]

# ===== INTELLIGENT RECOMMENDATION ENGINE =====

class IntelligentModelRecommendationEngine:
    """Intelligent model recommendation engine with ML-powered suggestions."""
    
    def __init__(self, config: RecommendationConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.RecommendationEngine")
        
        # Core components
        self.model_database = {}
        self.recommendation_cache = {}
        self.user_feedback = defaultdict(list)
        self.performance_history = defaultdict(list)
        
        # ML components
        self.recommendation_model = None
        self.performance_predictor = None
        self.similarity_engine = None
        
        # Learning components
        self.learning_enabled = config.learning_enabled
        self.feedback_enabled = config.feedback_enabled
        self.auto_learning = config.auto_learning
        
        # Threading
        self.learning_thread = None
        self.learning_active = False
        
        # Initialize system
        self._initialize_system()
    
    def _initialize_system(self) -> None:
        """Initialize the recommendation system."""
        try:
            # Create storage directory
            Path(self.config.model_database_path).mkdir(parents=True, exist_ok=True)
            
            # Load existing model database
            self._load_model_database()
            
            # Initialize ML components
            self._initialize_ml_components()
            
            # Start learning thread
            if self.auto_learning:
                self._start_learning()
            
            self.logger.info("Intelligent Model Recommendation Engine initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize recommendation engine: {e}")
            raise
    
    def _load_model_database(self) -> None:
        """Load model database from storage."""
        try:
            database_path = Path(self.config.model_database_path) / "model_database.json"
            
            if database_path.exists():
                with open(database_path, 'r') as f:
                    data = json.load(f)
                    
                for model_id, model_data in data.items():
                    # Convert back to ModelProfile
                    model_profile = ModelProfile(**model_data)
                    self.model_database[model_id] = model_profile
                
                self.logger.info(f"Loaded {len(self.model_database)} models from database")
            else:
                # Initialize with default models
                self._initialize_default_models()
                
        except Exception as e:
            self.logger.error(f"Failed to load model database: {e}")
            self._initialize_default_models()
    
    def _initialize_default_models(self) -> None:
        """Initialize with default model profiles."""
        try:
            default_models = [
                {
                    "model_id": "rf_classification",
                    "name": "Random Forest Classifier",
                    "algorithm": "random_forest",
                    "problem_type": ProblemType.CLASSIFICATION,
                    "performance_metrics": {"accuracy": 0.85, "f1_score": 0.83},
                    "data_characteristics": [DataCharacteristics.NUMERICAL, DataCharacteristics.CATEGORICAL],
                    "hyperparameters": {"n_estimators": 100, "max_depth": 10},
                    "training_time": 2.5,
                    "inference_time": 0.01,
                    "memory_usage": 0.1,
                    "complexity_score": 0.6,
                    "popularity_score": 0.9,
                    "success_rate": 0.85,
                    "created_at": datetime.now(),
                    "last_updated": datetime.now()
                },
                {
                    "model_id": "xgboost_regression",
                    "name": "XGBoost Regressor",
                    "algorithm": "xgboost",
                    "problem_type": ProblemType.REGRESSION,
                    "performance_metrics": {"r2_score": 0.88, "mae": 0.12},
                    "data_characteristics": [DataCharacteristics.NUMERICAL, DataCharacteristics.LARGE_DATASET],
                    "hyperparameters": {"n_estimators": 100, "learning_rate": 0.1},
                    "training_time": 5.2,
                    "inference_time": 0.005,
                    "memory_usage": 0.15,
                    "complexity_score": 0.7,
                    "popularity_score": 0.95,
                    "success_rate": 0.88,
                    "created_at": datetime.now(),
                    "last_updated": datetime.now()
                },
                {
                    "model_id": "neural_network",
                    "name": "Neural Network",
                    "algorithm": "neural_network",
                    "problem_type": ProblemType.CLASSIFICATION,
                    "performance_metrics": {"accuracy": 0.92, "f1_score": 0.90},
                    "data_characteristics": [DataCharacteristics.HIGH_DIMENSIONAL, DataCharacteristics.LARGE_DATASET],
                    "hyperparameters": {"hidden_layers": [100, 50], "learning_rate": 0.001},
                    "training_time": 15.8,
                    "inference_time": 0.02,
                    "memory_usage": 0.3,
                    "complexity_score": 0.8,
                    "popularity_score": 0.85,
                    "success_rate": 0.82,
                    "created_at": datetime.now(),
                    "last_updated": datetime.now()
                }
            ]
            
            for model_data in default_models:
                model_profile = ModelProfile(**model_data)
                self.model_database[model_profile.model_id] = model_profile
            
            # Save to storage
            self._save_model_database()
            
            self.logger.info(f"Initialized {len(default_models)} default models")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize default models: {e}")
    
    def _initialize_ml_components(self) -> None:
        """Initialize ML components for recommendations."""
        try:
            # Initialize recommendation model
            self.recommendation_model = RandomForestRegressor(
                n_estimators=100,
                random_state=42
            )
            
            # Initialize performance predictor
            self.performance_predictor = GradientBoostingRegressor(
                n_estimators=100,
                random_state=42
            )
            
            # Initialize similarity engine
            self.similarity_engine = ModelSimilarityEngine()
            
            self.logger.info("ML components initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ML components: {e}")
    
    def get_recommendations(self, user_context: UserContext) -> List[Recommendation]:
        """Get intelligent model recommendations for user context."""
        try:
            # Check cache first
            cache_key = self._generate_cache_key(user_context)
            if cache_key in self.recommendation_cache:
                cached_recommendations = self.recommendation_cache[cache_key]
                if self._is_cache_valid(cached_recommendations):
                    self.logger.info("Returning cached recommendations")
                    return cached_recommendations["recommendations"]
            
            # Generate new recommendations
            recommendations = self._generate_recommendations(user_context)
            
            # Cache recommendations
            self.recommendation_cache[cache_key] = {
                "recommendations": recommendations,
                "timestamp": datetime.now()
            }
            
            # Limit cache size
            if len(self.recommendation_cache) > self.config.recommendation_cache_size:
                self._cleanup_cache()
            
            self.logger.info(f"Generated {len(recommendations)} recommendations")
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Failed to get recommendations: {e}")
            return []
    
    def _generate_recommendations(self, user_context: UserContext) -> List[Recommendation]:
        """Generate intelligent recommendations."""
        try:
            recommendations = []
            
            # Filter models by problem type
            candidate_models = self._filter_models_by_problem_type(user_context.problem_type)
            
            if not candidate_models:
                self.logger.warning("No candidate models found")
                return []
            
            # Score models based on user context
            scored_models = self._score_models(candidate_models, user_context)
            
            # Sort by score
            scored_models.sort(key=lambda x: x[1], reverse=True)
            
            # Generate recommendations
            for i, (model_profile, score) in enumerate(scored_models[:self.config.max_recommendations]):
                recommendation = self._create_recommendation(
                    model_profile, user_context, score, i + 1
                )
                recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Failed to generate recommendations: {e}")
            return []
    
    def _filter_models_by_problem_type(self, problem_type: ProblemType) -> List[ModelProfile]:
        """Filter models by problem type."""
        try:
            filtered_models = []
            
            for model_profile in self.model_database.values():
                if model_profile.problem_type == problem_type:
                    filtered_models.append(model_profile)
            
            return filtered_models
            
        except Exception as e:
            self.logger.error(f"Failed to filter models: {e}")
            return []
    
    def _score_models(self, models: List[ModelProfile], user_context: UserContext) -> List[Tuple[ModelProfile, float]]:
        """Score models based on user context."""
        try:
            scored_models = []
            
            for model_profile in models:
                score = self._calculate_model_score(model_profile, user_context)
                scored_models.append((model_profile, score))
            
            return scored_models
            
        except Exception as e:
            self.logger.error(f"Failed to score models: {e}")
            return []
    
    def _calculate_model_score(self, model_profile: ModelProfile, user_context: UserContext) -> float:
        """Calculate model score based on user context."""
        try:
            score = 0.0
            
            # Performance score (40% weight)
            performance_score = self._calculate_performance_score(model_profile, user_context)
            score += performance_score * 0.4
            
            # Resource compatibility score (25% weight)
            resource_score = self._calculate_resource_score(model_profile, user_context)
            score += resource_score * 0.25
            
            # Data compatibility score (20% weight)
            data_score = self._calculate_data_compatibility_score(model_profile, user_context)
            score += data_score * 0.2
            
            # Popularity and success rate (15% weight)
            popularity_score = (model_profile.popularity_score + model_profile.success_rate) / 2
            score += popularity_score * 0.15
            
            return min(1.0, max(0.0, score))
            
        except Exception as e:
            self.logger.error(f"Failed to calculate model score: {e}")
            return 0.0
    
    def _calculate_performance_score(self, model_profile: ModelProfile, user_context: UserContext) -> float:
        """Calculate performance score."""
        try:
            if not user_context.performance_requirements:
                return 0.5  # Default score if no requirements
            
            score = 0.0
            total_weight = 0.0
            
            for metric, required_value in user_context.performance_requirements.items():
                if metric in model_profile.performance_metrics:
                    actual_value = model_profile.performance_metrics[metric]
                    
                    # Calculate how well the model meets the requirement
                    if required_value > 0:
                        ratio = actual_value / required_value
                        metric_score = min(1.0, ratio)
                    else:
                        metric_score = 0.5
                    
                    score += metric_score
                    total_weight += 1.0
            
            return score / total_weight if total_weight > 0 else 0.5
            
        except Exception as e:
            self.logger.error(f"Failed to calculate performance score: {e}")
            return 0.5
    
    def _calculate_resource_score(self, model_profile: ModelProfile, user_context: UserContext) -> float:
        """Calculate resource compatibility score."""
        try:
            if not user_context.resource_constraints:
                return 0.5  # Default score if no constraints
            
            score = 1.0
            
            # Check memory constraints
            if "max_memory" in user_context.resource_constraints:
                max_memory = user_context.resource_constraints["max_memory"]
                if model_profile.memory_usage > max_memory:
                    score *= 0.5
            
            # Check time constraints
            if "max_training_time" in user_context.resource_constraints:
                max_training_time = user_context.resource_constraints["max_training_time"]
                if model_profile.training_time > max_training_time:
                    score *= 0.7
            
            if "max_inference_time" in user_context.resource_constraints:
                max_inference_time = user_context.resource_constraints["max_inference_time"]
                if model_profile.inference_time > max_inference_time:
                    score *= 0.8
            
            return score
            
        except Exception as e:
            self.logger.error(f"Failed to calculate resource score: {e}")
            return 0.5
    
    def _calculate_data_compatibility_score(self, model_profile: ModelProfile, user_context: UserContext) -> float:
        """Calculate data compatibility score."""
        try:
            if not user_context.data_characteristics:
                return 0.5  # Default score if no characteristics
            
            score = 0.0
            total_characteristics = len(user_context.data_characteristics)
            
            for characteristic in user_context.data_characteristics:
                if characteristic in model_profile.data_characteristics:
                    score += 1.0
                else:
                    # Check for partial compatibility
                    if self._is_partially_compatible(characteristic, model_profile.data_characteristics):
                        score += 0.5
            
            return score / total_characteristics if total_characteristics > 0 else 0.5
            
        except Exception as e:
            self.logger.error(f"Failed to calculate data compatibility score: {e}")
            return 0.5
    
    def _is_partially_compatible(self, characteristic: DataCharacteristics, model_characteristics: List[DataCharacteristics]) -> bool:
        """Check if characteristic is partially compatible."""
        try:
            # Define compatibility mappings
            compatibility_map = {
                DataCharacteristics.SMALL_DATASET: [DataCharacteristics.LARGE_DATASET],
                DataCharacteristics.LARGE_DATASET: [DataCharacteristics.SMALL_DATASET],
                DataCharacteristics.NUMERICAL: [DataCharacteristics.CATEGORICAL],
                DataCharacteristics.CATEGORICAL: [DataCharacteristics.NUMERICAL],
                DataCharacteristics.TEXT: [DataCharacteristics.NLP],
                DataCharacteristics.IMAGE: [DataCharacteristics.COMPUTER_VISION]
            }
            
            compatible_characteristics = compatibility_map.get(characteristic, [])
            return any(comp_char in model_characteristics for comp_char in compatible_characteristics)
            
        except Exception as e:
            self.logger.error(f"Failed to check partial compatibility: {e}")
            return False
    
    def _create_recommendation(self, model_profile: ModelProfile, user_context: UserContext, score: float, rank: int) -> Recommendation:
        """Create a recommendation object."""
        try:
            recommendation_id = str(uuid.uuid4())
            
            # Determine confidence level
            confidence = self._determine_confidence_level(score)
            
            # Generate reasoning
            reasoning = self._generate_reasoning(model_profile, user_context, score)
            
            # Predict expected performance
            expected_performance = self._predict_performance(model_profile, user_context)
            
            # Identify trade-offs
            trade_offs = self._identify_trade_offs(model_profile, user_context)
            
            # Find alternatives
            alternatives = self._find_alternatives(model_profile, user_context)
            
            return Recommendation(
                recommendation_id=recommendation_id,
                type=RecommendationType.MODEL_SELECTION,
                model_id=model_profile.model_id,
                confidence=confidence,
                confidence_score=score,
                reasoning=reasoning,
                expected_performance=expected_performance,
                trade_offs=trade_offs,
                alternatives=alternatives,
                created_at=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Failed to create recommendation: {e}")
            raise
    
    def _determine_confidence_level(self, score: float) -> RecommendationConfidence:
        """Determine confidence level based on score."""
        try:
            if score >= 0.9:
                return RecommendationConfidence.VERY_HIGH
            elif score >= 0.8:
                return RecommendationConfidence.HIGH
            elif score >= 0.6:
                return RecommendationConfidence.MEDIUM
            else:
                return RecommendationConfidence.LOW
                
        except Exception as e:
            self.logger.error(f"Failed to determine confidence level: {e}")
            return RecommendationConfidence.LOW
    
    def _generate_reasoning(self, model_profile: ModelProfile, user_context: UserContext, score: float) -> str:
        """Generate reasoning for recommendation."""
        try:
            reasoning_parts = []
            
            # Performance reasoning
            if user_context.performance_requirements:
                for metric, required_value in user_context.performance_requirements.items():
                    if metric in model_profile.performance_metrics:
                        actual_value = model_profile.performance_metrics[metric]
                        if actual_value >= required_value:
                            reasoning_parts.append(f"Meets {metric} requirement ({actual_value:.3f} >= {required_value:.3f})")
                        else:
                            reasoning_parts.append(f"Partially meets {metric} requirement ({actual_value:.3f} < {required_value:.3f})")
            
            # Resource reasoning
            if user_context.resource_constraints:
                if "max_memory" in user_context.resource_constraints:
                    max_memory = user_context.resource_constraints["max_memory"]
                    if model_profile.memory_usage <= max_memory:
                        reasoning_parts.append(f"Memory usage within limits ({model_profile.memory_usage:.2f} <= {max_memory:.2f})")
            
            # Data compatibility reasoning
            compatible_characteristics = set(user_context.data_characteristics) & set(model_profile.data_characteristics)
            if compatible_characteristics:
                reasoning_parts.append(f"Compatible with data characteristics: {', '.join([c.value for c in compatible_characteristics])}")
            
            # Popularity reasoning
            if model_profile.popularity_score > 0.8:
                reasoning_parts.append("High popularity and proven track record")
            
            if not reasoning_parts:
                reasoning_parts.append("General compatibility based on problem type")
            
            return ". ".join(reasoning_parts) + "."
            
        except Exception as e:
            self.logger.error(f"Failed to generate reasoning: {e}")
            return "Recommendation based on general compatibility."
    
    def _predict_performance(self, model_profile: ModelProfile, user_context: UserContext) -> Dict[str, float]:
        """Predict expected performance for user context."""
        try:
            # Use performance predictor if available
            if self.performance_predictor and hasattr(self.performance_predictor, 'predict'):
                # Create feature vector for prediction
                features = self._create_performance_features(model_profile, user_context)
                
                # Predict performance metrics
                predicted_metrics = {}
                for metric in model_profile.performance_metrics.keys():
                    try:
                        # This is a simplified prediction - in practice, you'd have separate models for each metric
                        prediction = model_profile.performance_metrics[metric] * np.random.uniform(0.9, 1.1)
                        predicted_metrics[metric] = float(prediction)
                    except:
                        predicted_metrics[metric] = model_profile.performance_metrics[metric]
                
                return predicted_metrics
            else:
                # Fallback to model profile performance with some variation
                predicted_metrics = {}
                for metric, value in model_profile.performance_metrics.items():
                    # Add some variation based on user context
                    variation = np.random.uniform(0.95, 1.05)
                    predicted_metrics[metric] = float(value * variation)
                
                return predicted_metrics
                
        except Exception as e:
            self.logger.error(f"Failed to predict performance: {e}")
            return model_profile.performance_metrics
    
    def _create_performance_features(self, model_profile: ModelProfile, user_context: UserContext) -> np.ndarray:
        """Create feature vector for performance prediction."""
        try:
            features = []
            
            # Model features
            features.extend([
                model_profile.complexity_score,
                model_profile.popularity_score,
                model_profile.success_rate,
                model_profile.training_time,
                model_profile.inference_time,
                model_profile.memory_usage
            ])
            
            # User context features
            features.extend([
                len(user_context.data_characteristics),
                len(user_context.performance_requirements),
                len(user_context.resource_constraints)
            ])
            
            # Data characteristics encoding
            data_char_encoding = [0.0] * len(DataCharacteristics)
            for char in user_context.data_characteristics:
                data_char_encoding[list(DataCharacteristics).index(char)] = 1.0
            features.extend(data_char_encoding)
            
            return np.array(features).reshape(1, -1)
            
        except Exception as e:
            self.logger.error(f"Failed to create performance features: {e}")
            return np.array([[0.0] * 20])  # Default feature vector
    
    def _identify_trade_offs(self, model_profile: ModelProfile, user_context: UserContext) -> List[str]:
        """Identify trade-offs for the recommendation."""
        try:
            trade_offs = []
            
            # Training time trade-off
            if model_profile.training_time > 10:
                trade_offs.append("Longer training time may be required")
            
            # Memory trade-off
            if model_profile.memory_usage > 0.2:
                trade_offs.append("Higher memory usage")
            
            # Complexity trade-off
            if model_profile.complexity_score > 0.7:
                trade_offs.append("Higher model complexity may require more expertise")
            
            # Inference time trade-off
            if model_profile.inference_time > 0.05:
                trade_offs.append("Slower inference time")
            
            return trade_offs
            
        except Exception as e:
            self.logger.error(f"Failed to identify trade-offs: {e}")
            return []
    
    def _find_alternatives(self, model_profile: ModelProfile, user_context: UserContext) -> List[str]:
        """Find alternative model recommendations."""
        try:
            alternatives = []
            
            # Find similar models
            similar_models = self.similarity_engine.find_similar_models(
                model_profile, self.model_database, top_k=3
            )
            
            for similar_model in similar_models:
                if similar_model.model_id != model_profile.model_id:
                    alternatives.append(similar_model.model_id)
            
            return alternatives
            
        except Exception as e:
            self.logger.error(f"Failed to find alternatives: {e}")
            return []
    
    def add_model_profile(self, model_profile: ModelProfile) -> bool:
        """Add a new model profile to the database."""
        try:
            self.model_database[model_profile.model_id] = model_profile
            
            # Save to storage
            self._save_model_database()
            
            self.logger.info(f"Added model profile: {model_profile.model_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add model profile: {e}")
            return False
    
    def update_model_performance(self, model_id: str, performance_metrics: Dict[str, float]) -> bool:
        """Update model performance metrics."""
        try:
            if model_id not in self.model_database:
                self.logger.warning(f"Model not found: {model_id}")
                return False
            
            model_profile = self.model_database[model_id]
            model_profile.performance_metrics.update(performance_metrics)
            model_profile.last_updated = datetime.now()
            
            # Save to storage
            self._save_model_database()
            
            self.logger.info(f"Updated performance for model: {model_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update model performance: {e}")
            return False
    
    def provide_feedback(self, recommendation_id: str, feedback: Dict[str, Any]) -> bool:
        """Provide feedback on a recommendation."""
        try:
            if not self.feedback_enabled:
                self.logger.warning("Feedback is disabled")
                return False
            
            feedback_data = {
                "recommendation_id": recommendation_id,
                "feedback": feedback,
                "timestamp": datetime.now()
            }
            
            self.user_feedback[recommendation_id].append(feedback_data)
            
            self.logger.info(f"Received feedback for recommendation: {recommendation_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to provide feedback: {e}")
            return False
    
    def _generate_cache_key(self, user_context: UserContext) -> str:
        """Generate cache key for user context."""
        try:
            key_data = {
                "problem_type": user_context.problem_type.value,
                "data_characteristics": [c.value for c in user_context.data_characteristics],
                "performance_requirements": user_context.performance_requirements,
                "resource_constraints": user_context.resource_constraints
            }
            
            key_string = json.dumps(key_data, sort_keys=True)
            return hashlib.md5(key_string.encode()).hexdigest()
            
        except Exception as e:
            self.logger.error(f"Failed to generate cache key: {e}")
            return str(uuid.uuid4())
    
    def _is_cache_valid(self, cached_data: Dict[str, Any]) -> bool:
        """Check if cached data is still valid."""
        try:
            cache_age = datetime.now() - cached_data["timestamp"]
            return cache_age < timedelta(hours=1)  # Cache valid for 1 hour
            
        except Exception as e:
            self.logger.error(f"Failed to check cache validity: {e}")
            return False
    
    def _cleanup_cache(self) -> None:
        """Clean up old cache entries."""
        try:
            # Remove oldest entries
            sorted_cache = sorted(
                self.recommendation_cache.items(),
                key=lambda x: x[1]["timestamp"]
            )
            
            # Keep only the most recent entries
            keep_count = self.config.recommendation_cache_size // 2
            entries_to_remove = sorted_cache[:-keep_count]
            
            for key, _ in entries_to_remove:
                del self.recommendation_cache[key]
            
            self.logger.info(f"Cleaned up {len(entries_to_remove)} cache entries")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup cache: {e}")
    
    def _save_model_database(self) -> None:
        """Save model database to storage."""
        try:
            database_path = Path(self.config.model_database_path) / "model_database.json"
            
            # Convert ModelProfile objects to dictionaries
            data = {}
            for model_id, model_profile in self.model_database.items():
                data[model_id] = model_profile.__dict__
                # Convert enums to strings
                data[model_id]["problem_type"] = model_profile.problem_type.value
                data[model_id]["data_characteristics"] = [c.value for c in model_profile.data_characteristics]
                data[model_id]["created_at"] = model_profile.created_at.isoformat()
                data[model_id]["last_updated"] = model_profile.last_updated.isoformat()
            
            with open(database_path, 'w') as f:
                json.dump(data, f, indent=2)
            
        except Exception as e:
            self.logger.error(f"Failed to save model database: {e}")
    
    def _start_learning(self) -> None:
        """Start the learning thread."""
        try:
            self.learning_active = True
            self.learning_thread = threading.Thread(target=self._learning_loop, daemon=True)
            self.learning_thread.start()
            
            self.logger.info("Learning thread started")
            
        except Exception as e:
            self.logger.error(f"Failed to start learning: {e}")
    
    def _learning_loop(self) -> None:
        """Learning loop for continuous improvement."""
        while self.learning_active:
            try:
                # Update recommendation models based on feedback
                self._update_recommendation_models()
                
                # Update performance predictors
                self._update_performance_predictors()
                
                # Sleep for update interval
                time.sleep(self.config.update_interval_hours * 3600)
                
            except Exception as e:
                self.logger.error(f"Error in learning loop: {e}")
                time.sleep(3600)  # Sleep for 1 hour on error
    
    def _update_recommendation_models(self) -> None:
        """Update recommendation models based on feedback."""
        try:
            if not self.user_feedback:
                return
            
            # Collect training data from feedback
            training_data = []
            for recommendation_id, feedback_list in self.user_feedback.items():
                for feedback_data in feedback_list:
                    # Process feedback data
                    # This is a simplified implementation
                    pass
            
            # Retrain recommendation model if we have enough data
            if len(training_data) > 100:
                self.logger.info("Retraining recommendation model with feedback data")
                # Implement retraining logic here
            
        except Exception as e:
            self.logger.error(f"Failed to update recommendation models: {e}")
    
    def _update_performance_predictors(self) -> None:
        """Update performance predictors."""
        try:
            # Update performance prediction models
            # This would involve retraining with new performance data
            pass
            
        except Exception as e:
            self.logger.error(f"Failed to update performance predictors: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status information."""
        try:
            return {
                "total_models": len(self.model_database),
                "cache_size": len(self.recommendation_cache),
                "total_feedback": sum(len(feedback_list) for feedback_list in self.user_feedback.values()),
                "learning_enabled": self.learning_enabled,
                "feedback_enabled": self.feedback_enabled,
                "auto_learning": self.auto_learning,
                "last_updated": datetime.now()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get system status: {e}")
            return {"error": str(e)}
    
    def stop(self) -> None:
        """Stop the recommendation engine."""
        try:
            self.learning_active = False
            
            if self.learning_thread and self.learning_thread.is_alive():
                self.learning_thread.join(timeout=5)
            
            # Save final state
            self._save_model_database()
            
            self.logger.info("Recommendation engine stopped")
            
        except Exception as e:
            self.logger.error(f"Failed to stop recommendation engine: {e}")

# ===== MODEL SIMILARITY ENGINE =====

class ModelSimilarityEngine:
    """Engine for finding similar models."""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.SimilarityEngine")
    
    def find_similar_models(self, 
                           target_model: ModelProfile, 
                           model_database: Dict[str, ModelProfile], 
                           top_k: int = 5) -> List[ModelProfile]:
        """Find similar models to the target model."""
        try:
            similarities = []
            
            for model_id, model_profile in model_database.items():
                if model_id == target_model.model_id:
                    continue
                
                similarity = self._calculate_similarity(target_model, model_profile)
                similarities.append((model_profile, similarity))
            
            # Sort by similarity
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Return top-k similar models
            return [model for model, _ in similarities[:top_k]]
            
        except Exception as e:
            self.logger.error(f"Failed to find similar models: {e}")
            return []
    
    def _calculate_similarity(self, model1: ModelProfile, model2: ModelProfile) -> float:
        """Calculate similarity between two models."""
        try:
            similarity = 0.0
            
            # Algorithm similarity
            if model1.algorithm == model2.algorithm:
                similarity += 0.3
            
            # Problem type similarity
            if model1.problem_type == model2.problem_type:
                similarity += 0.2
            
            # Data characteristics similarity
            common_characteristics = set(model1.data_characteristics) & set(model2.data_characteristics)
            total_characteristics = set(model1.data_characteristics) | set(model2.data_characteristics)
            
            if total_characteristics:
                char_similarity = len(common_characteristics) / len(total_characteristics)
                similarity += char_similarity * 0.2
            
            # Performance similarity
            common_metrics = set(model1.performance_metrics.keys()) & set(model2.performance_metrics.keys())
            if common_metrics:
                perf_similarity = 0.0
                for metric in common_metrics:
                    val1 = model1.performance_metrics[metric]
                    val2 = model2.performance_metrics[metric]
                    perf_similarity += 1.0 - abs(val1 - val2) / max(val1, val2, 0.001)
                
                perf_similarity /= len(common_metrics)
                similarity += perf_similarity * 0.2
            
            # Complexity similarity
            complexity_diff = abs(model1.complexity_score - model2.complexity_score)
            complexity_similarity = 1.0 - complexity_diff
            similarity += complexity_similarity * 0.1
            
            return min(1.0, max(0.0, similarity))
            
        except Exception as e:
            self.logger.error(f"Failed to calculate similarity: {e}")
            return 0.0

# ===== MAIN EXECUTION =====

def main():
    """Main execution function."""
    print("🚀 Intelligent Model Recommendation Engine")
    print("="*60)
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create configuration
    config = RecommendationConfig()
    
    # Create recommendation engine
    engine = IntelligentModelRecommendationEngine(config)
    
    try:
        print("✅ Recommendation Engine initialized successfully")
        
        # Example usage
        user_context = UserContext(
            user_id="user_001",
            problem_type=ProblemType.CLASSIFICATION,
            data_characteristics=[DataCharacteristics.NUMERICAL, DataCharacteristics.CATEGORICAL],
            performance_requirements={"accuracy": 0.85, "f1_score": 0.80},
            resource_constraints={"max_memory": 0.2, "max_training_time": 10.0},
            preferences={},
            historical_performance={}
        )
        
        # Get recommendations
        recommendations = engine.get_recommendations(user_context)
        
        print(f"📊 Generated {len(recommendations)} recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec.model_id} (Confidence: {rec.confidence.value}, Score: {rec.confidence_score:.3f})")
            print(f"      Reasoning: {rec.reasoning}")
        
        # Get system status
        status = engine.get_system_status()
        print(f"\n📈 System Status: {json.dumps(status, indent=2, default=str)}")
        
        # Keep system running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Recommendation Engine interrupted by user")
    except Exception as e:
        print(f"❌ Recommendation Engine failed: {e}")
        raise
    finally:
        engine.stop()

if __name__ == "__main__":
    main()
