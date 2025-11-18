"""
Advanced ML Service with Model Training, Evaluation, and Deployment
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
import pickle
from pathlib import Path

from ..utils.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class ModelType(Enum):
    """Types of ML models"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    DIMENSIONALITY_REDUCTION = "dimensionality_reduction"
    TIME_SERIES = "time_series"
    NLP = "nlp"
    COMPUTER_VISION = "computer_vision"
    RECOMMENDATION = "recommendation"
    ANOMALY_DETECTION = "anomaly_detection"
    REINFORCEMENT_LEARNING = "reinforcement_learning"

class ModelStatus(Enum):
    """Model status"""
    TRAINING = "training"
    TRAINED = "trained"
    EVALUATING = "evaluating"
    DEPLOYED = "deployed"
    FAILED = "failed"
    ARCHIVED = "archived"

class TrainingStatus(Enum):
    """Training status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ModelConfig:
    """Model configuration"""
    id: str
    name: str
    model_type: ModelType
    algorithm: str
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    feature_columns: List[str] = field(default_factory=list)
    target_column: str = ""
    preprocessing_steps: List[Dict[str, Any]] = field(default_factory=list)
    validation_strategy: str = "holdout"
    test_size: float = 0.2
    random_state: int = 42
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TrainingJob:
    """Training job"""
    id: str
    model_config_id: str
    dataset_id: str
    status: TrainingStatus
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: float = 0.0
    current_epoch: int = 0
    total_epochs: int = 0
    loss: float = 0.0
    metrics: Dict[str, float] = field(default_factory=dict)
    error_message: Optional[str] = None
    model_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ModelEvaluation:
    """Model evaluation results"""
    model_id: str
    dataset_id: str
    metrics: Dict[str, float] = field(default_factory=dict)
    confusion_matrix: Optional[np.ndarray] = None
    feature_importance: Optional[Dict[str, float]] = None
    predictions: Optional[np.ndarray] = None
    actual_values: Optional[np.ndarray] = None
    evaluation_time: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Dataset:
    """Dataset information"""
    id: str
    name: str
    description: str
    file_path: str
    size: int
    features: int
    target_column: str
    feature_columns: List[str]
    data_types: Dict[str, str] = field(default_factory=dict)
    missing_values: Dict[str, int] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

class AdvancedMLService:
    """Advanced ML Service with Model Training, Evaluation, and Deployment"""
    
    def __init__(self):
        self.model_configs = {}
        self.training_jobs = {}
        self.model_evaluations = {}
        self.datasets = {}
        self.trained_models = {}
        self.training_queue = asyncio.Queue()
        self.evaluation_queue = asyncio.Queue()
        self.model_registry = {}
        
        # Initialize model algorithms
        self._initialize_algorithms()
        
        # Start background tasks
        self._start_background_tasks()
        
        logger.info("Advanced ML Service initialized")
    
    def _initialize_algorithms(self):
        """Initialize ML algorithms"""
        try:
            self.algorithms = {
                'classification': {
                    'logistic_regression': 'sklearn.linear_model.LogisticRegression',
                    'random_forest': 'sklearn.ensemble.RandomForestClassifier',
                    'svm': 'sklearn.svm.SVC',
                    'naive_bayes': 'sklearn.naive_bayes.GaussianNB',
                    'knn': 'sklearn.neighbors.KNeighborsClassifier',
                    'gradient_boosting': 'sklearn.ensemble.GradientBoostingClassifier',
                    'neural_network': 'sklearn.neural_network.MLPClassifier'
                },
                'regression': {
                    'linear_regression': 'sklearn.linear_model.LinearRegression',
                    'ridge_regression': 'sklearn.linear_model.Ridge',
                    'lasso_regression': 'sklearn.linear_model.Lasso',
                    'random_forest': 'sklearn.ensemble.RandomForestRegressor',
                    'gradient_boosting': 'sklearn.ensemble.GradientBoostingRegressor',
                    'svr': 'sklearn.svm.SVR',
                    'neural_network': 'sklearn.neural_network.MLPRegressor'
                },
                'clustering': {
                    'kmeans': 'sklearn.cluster.KMeans',
                    'dbscan': 'sklearn.cluster.DBSCAN',
                    'hierarchical': 'sklearn.cluster.AgglomerativeClustering',
                    'gaussian_mixture': 'sklearn.mixture.GaussianMixture'
                },
                'dimensionality_reduction': {
                    'pca': 'sklearn.decomposition.PCA',
                    'lda': 'sklearn.discriminant_analysis.LinearDiscriminantAnalysis',
                    'tsne': 'sklearn.manifold.TSNE',
                    'umap': 'umap.UMAP'
                }
            }
            
            logger.info("ML algorithms initialized")
            
        except Exception as e:
            logger.error(f"Error initializing algorithms: {e}")
    
    def _start_background_tasks(self):
        """Start background tasks"""
        try:
            # Start training processor
            asyncio.create_task(self._process_training_jobs())
            
            # Start evaluation processor
            asyncio.create_task(self._process_evaluations())
            
            logger.info("Background tasks started")
            
        except Exception as e:
            logger.error(f"Error starting background tasks: {e}")
    
    async def _process_training_jobs(self):
        """Process training jobs"""
        try:
            while True:
                try:
                    training_job = await asyncio.wait_for(self.training_queue.get(), timeout=1.0)
                    await self._execute_training_job(training_job)
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error processing training job: {e}")
                    
        except Exception as e:
            logger.error(f"Error in training processor: {e}")
    
    async def _process_evaluations(self):
        """Process model evaluations"""
        try:
            while True:
                try:
                    evaluation_request = await asyncio.wait_for(self.evaluation_queue.get(), timeout=1.0)
                    await self._execute_evaluation(evaluation_request)
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error processing evaluation: {e}")
                    
        except Exception as e:
            logger.error(f"Error in evaluation processor: {e}")
    
    async def create_model_config(self, config: ModelConfig) -> str:
        """Create model configuration"""
        try:
            config_id = str(uuid.uuid4())
            config.id = config_id
            config.created_at = datetime.utcnow()
            config.updated_at = datetime.utcnow()
            
            self.model_configs[config_id] = config
            
            logger.info(f"Model config created: {config_id}")
            
            return config_id
            
        except Exception as e:
            logger.error(f"Error creating model config: {e}")
            raise
    
    async def create_dataset(self, dataset: Dataset) -> str:
        """Create dataset"""
        try:
            dataset_id = str(uuid.uuid4())
            dataset.id = dataset_id
            dataset.created_at = datetime.utcnow()
            
            # Analyze dataset
            await self._analyze_dataset(dataset)
            
            self.datasets[dataset_id] = dataset
            
            logger.info(f"Dataset created: {dataset_id}")
            
            return dataset_id
            
        except Exception as e:
            logger.error(f"Error creating dataset: {e}")
            raise
    
    async def _analyze_dataset(self, dataset: Dataset):
        """Analyze dataset characteristics"""
        try:
            # Load dataset
            df = pd.read_csv(dataset.file_path)
            
            # Update dataset info
            dataset.size = len(df)
            dataset.features = len(df.columns) - 1  # Exclude target column
            dataset.feature_columns = [col for col in df.columns if col != dataset.target_column]
            
            # Analyze data types
            dataset.data_types = df.dtypes.astype(str).to_dict()
            
            # Analyze missing values
            dataset.missing_values = df.isnull().sum().to_dict()
            
            logger.info(f"Dataset analyzed: {dataset.id}")
            
        except Exception as e:
            logger.error(f"Error analyzing dataset: {e}")
    
    async def start_training(self, model_config_id: str, dataset_id: str) -> str:
        """Start model training"""
        try:
            if model_config_id not in self.model_configs:
                raise ValueError(f"Model config not found: {model_config_id}")
            
            if dataset_id not in self.datasets:
                raise ValueError(f"Dataset not found: {dataset_id}")
            
            # Create training job
            job_id = str(uuid.uuid4())
            training_job = TrainingJob(
                id=job_id,
                model_config_id=model_config_id,
                dataset_id=dataset_id,
                status=TrainingStatus.PENDING
            )
            
            self.training_jobs[job_id] = training_job
            
            # Add to training queue
            await self.training_queue.put(training_job)
            
            logger.info(f"Training job started: {job_id}")
            
            return job_id
            
        except Exception as e:
            logger.error(f"Error starting training: {e}")
            raise
    
    async def _execute_training_job(self, training_job: TrainingJob):
        """Execute training job"""
        try:
            training_job.status = TrainingStatus.RUNNING
            training_job.started_at = datetime.utcnow()
            
            # Get model config and dataset
            model_config = self.model_configs[training_job.model_config_id]
            dataset = self.datasets[training_job.dataset_id]
            
            # Load and preprocess data
            X, y = await self._load_and_preprocess_data(dataset, model_config)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=model_config.test_size, random_state=model_config.random_state
            )
            
            # Train model
            model = await self._train_model(model_config, X_train, y_train, training_job)
            
            # Save model
            model_path = await self._save_model(model, training_job.id)
            training_job.model_path = model_path
            
            # Evaluate model
            metrics = await self._evaluate_model(model, X_test, y_test, model_config)
            training_job.metrics = metrics
            
            # Update job status
            training_job.status = TrainingStatus.COMPLETED
            training_job.completed_at = datetime.utcnow()
            training_job.progress = 100.0
            
            # Store trained model
            self.trained_models[training_job.id] = {
                'model': model,
                'config': model_config,
                'metrics': metrics,
                'training_job': training_job
            }
            
            logger.info(f"Training job completed: {training_job.id}")
            
        except Exception as e:
            logger.error(f"Error executing training job: {e}")
            training_job.status = TrainingStatus.FAILED
            training_job.error_message = str(e)
            training_job.completed_at = datetime.utcnow()
    
    async def _load_and_preprocess_data(self, dataset: Dataset, model_config: ModelConfig) -> Tuple[np.ndarray, np.ndarray]:
        """Load and preprocess data"""
        try:
            # Load dataset
            df = pd.read_csv(dataset.file_path)
            
            # Select features and target
            X = df[model_config.feature_columns].values
            y = df[model_config.target_column].values
            
            # Apply preprocessing steps
            for step in model_config.preprocessing_steps:
                step_type = step.get('type')
                
                if step_type == 'imputation':
                    # Handle missing values
                    from sklearn.impute import SimpleImputer
                    imputer = SimpleImputer(strategy=step.get('strategy', 'mean'))
                    X = imputer.fit_transform(X)
                
                elif step_type == 'scaling':
                    # Scale features
                    from sklearn.preprocessing import StandardScaler
                    scaler = StandardScaler()
                    X = scaler.fit_transform(X)
                
                elif step_type == 'encoding':
                    # Encode categorical variables
                    from sklearn.preprocessing import LabelEncoder
                    encoder = LabelEncoder()
                    y = encoder.fit_transform(y)
            
            return X, y
            
        except Exception as e:
            logger.error(f"Error loading and preprocessing data: {e}")
            raise
    
    async def _train_model(self, model_config: ModelConfig, X_train: np.ndarray, y_train: np.ndarray, training_job: TrainingJob):
        """Train model"""
        try:
            algorithm = model_config.algorithm
            model_type = model_config.model_type.value
            
            # Get algorithm class
            if model_type in self.algorithms and algorithm in self.algorithms[model_type]:
                algorithm_path = self.algorithms[model_type][algorithm]
                module_path, class_name = algorithm_path.rsplit('.', 1)
                
                # Import and instantiate
                module = __import__(module_path, fromlist=[class_name])
                model_class = getattr(module, class_name)
                
                # Create model with hyperparameters
                model = model_class(**model_config.hyperparameters)
                
                # Train model
                if hasattr(model, 'fit'):
                    model.fit(X_train, y_train)
                else:
                    raise ValueError(f"Model {algorithm} does not support fit method")
                
                return model
            else:
                raise ValueError(f"Unknown algorithm: {algorithm} for type: {model_type}")
                
        except Exception as e:
            logger.error(f"Error training model: {e}")
            raise
    
    async def _evaluate_model(self, model, X_test: np.ndarray, y_test: np.ndarray, model_config: ModelConfig) -> Dict[str, float]:
        """Evaluate model"""
        try:
            # Make predictions
            y_pred = model.predict(X_test)
            
            # Calculate metrics based on model type
            metrics = {}
            
            if model_config.model_type == ModelType.CLASSIFICATION:
                metrics['accuracy'] = accuracy_score(y_test, y_pred)
                metrics['precision'] = precision_score(y_test, y_pred, average='weighted')
                metrics['recall'] = recall_score(y_test, y_pred, average='weighted')
                metrics['f1_score'] = f1_score(y_test, y_pred, average='weighted')
            
            elif model_config.model_type == ModelType.REGRESSION:
                from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
                metrics['mse'] = mean_squared_error(y_test, y_pred)
                metrics['mae'] = mean_absolute_error(y_test, y_pred)
                metrics['r2_score'] = r2_score(y_test, y_pred)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error evaluating model: {e}")
            raise
    
    async def _save_model(self, model, job_id: str) -> str:
        """Save trained model"""
        try:
            # Create models directory
            models_dir = Path("gamma_app/models")
            models_dir.mkdir(parents=True, exist_ok=True)
            
            # Save model
            model_path = models_dir / f"model_{job_id}.joblib"
            joblib.dump(model, model_path)
            
            return str(model_path)
            
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            raise
    
    async def evaluate_model(self, model_id: str, dataset_id: str) -> str:
        """Evaluate model on dataset"""
        try:
            if model_id not in self.trained_models:
                raise ValueError(f"Trained model not found: {model_id}")
            
            if dataset_id not in self.datasets:
                raise ValueError(f"Dataset not found: {dataset_id}")
            
            # Create evaluation request
            evaluation_id = str(uuid.uuid4())
            evaluation_request = {
                'id': evaluation_id,
                'model_id': model_id,
                'dataset_id': dataset_id
            }
            
            # Add to evaluation queue
            await self.evaluation_queue.put(evaluation_request)
            
            logger.info(f"Model evaluation started: {evaluation_id}")
            
            return evaluation_id
            
        except Exception as e:
            logger.error(f"Error starting model evaluation: {e}")
            raise
    
    async def _execute_evaluation(self, evaluation_request: Dict[str, Any]):
        """Execute model evaluation"""
        try:
            model_id = evaluation_request['model_id']
            dataset_id = evaluation_request['dataset_id']
            
            # Get trained model and dataset
            trained_model_info = self.trained_models[model_id]
            model = trained_model_info['model']
            model_config = trained_model_info['config']
            dataset = self.datasets[dataset_id]
            
            # Load and preprocess data
            X, y = await self._load_and_preprocess_data(dataset, model_config)
            
            # Make predictions
            start_time = time.time()
            y_pred = model.predict(X)
            evaluation_time = time.time() - start_time
            
            # Calculate metrics
            metrics = await self._evaluate_model(model, X, y, model_config)
            
            # Create evaluation result
            evaluation = ModelEvaluation(
                model_id=model_id,
                dataset_id=dataset_id,
                metrics=metrics,
                predictions=y_pred,
                actual_values=y,
                evaluation_time=evaluation_time
            )
            
            self.model_evaluations[evaluation_request['id']] = evaluation
            
            logger.info(f"Model evaluation completed: {evaluation_request['id']}")
            
        except Exception as e:
            logger.error(f"Error executing evaluation: {e}")
    
    async def predict(self, model_id: str, data: List[Dict[str, Any]]) -> List[Any]:
        """Make predictions using trained model"""
        try:
            if model_id not in self.trained_models:
                raise ValueError(f"Trained model not found: {model_id}")
            
            trained_model_info = self.trained_models[model_id]
            model = trained_model_info['model']
            model_config = trained_model_info['config']
            
            # Convert data to DataFrame
            df = pd.DataFrame(data)
            
            # Select features
            X = df[model_config.feature_columns].values
            
            # Apply preprocessing
            for step in model_config.preprocessing_steps:
                step_type = step.get('type')
                
                if step_type == 'imputation':
                    from sklearn.impute import SimpleImputer
                    imputer = SimpleImputer(strategy=step.get('strategy', 'mean'))
                    X = imputer.transform(X)
                
                elif step_type == 'scaling':
                    from sklearn.preprocessing import StandardScaler
                    scaler = StandardScaler()
                    X = scaler.transform(X)
            
            # Make predictions
            predictions = model.predict(X)
            
            return predictions.tolist()
            
        except Exception as e:
            logger.error(f"Error making predictions: {e}")
            raise
    
    async def get_training_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get training job status"""
        try:
            if job_id not in self.training_jobs:
                return None
            
            training_job = self.training_jobs[job_id]
            
            return {
                'id': training_job.id,
                'model_config_id': training_job.model_config_id,
                'dataset_id': training_job.dataset_id,
                'status': training_job.status.value,
                'progress': training_job.progress,
                'current_epoch': training_job.current_epoch,
                'total_epochs': training_job.total_epochs,
                'loss': training_job.loss,
                'metrics': training_job.metrics,
                'created_at': training_job.created_at.isoformat(),
                'started_at': training_job.started_at.isoformat() if training_job.started_at else None,
                'completed_at': training_job.completed_at.isoformat() if training_job.completed_at else None,
                'error_message': training_job.error_message
            }
            
        except Exception as e:
            logger.error(f"Error getting training status: {e}")
            return None
    
    async def get_model_evaluation(self, evaluation_id: str) -> Optional[Dict[str, Any]]:
        """Get model evaluation results"""
        try:
            if evaluation_id not in self.model_evaluations:
                return None
            
            evaluation = self.model_evaluations[evaluation_id]
            
            return {
                'id': evaluation_id,
                'model_id': evaluation.model_id,
                'dataset_id': evaluation.dataset_id,
                'metrics': evaluation.metrics,
                'evaluation_time': evaluation.evaluation_time,
                'created_at': evaluation.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting model evaluation: {e}")
            return None
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List all trained models"""
        try:
            models = []
            
            for model_id, model_info in self.trained_models.items():
                model_data = {
                    'id': model_id,
                    'name': model_info['config'].name,
                    'type': model_info['config'].model_type.value,
                    'algorithm': model_info['config'].algorithm,
                    'metrics': model_info['metrics'],
                    'created_at': model_info['training_job'].created_at.isoformat(),
                    'status': model_info['training_job'].status.value
                }
                models.append(model_data)
            
            return models
            
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []
    
    async def delete_model(self, model_id: str) -> bool:
        """Delete trained model"""
        try:
            if model_id not in self.trained_models:
                return False
            
            # Remove model file
            model_info = self.trained_models[model_id]
            if model_info['training_job'].model_path:
                import os
                try:
                    os.remove(model_info['training_job'].model_path)
                except:
                    pass
            
            # Remove from registry
            del self.trained_models[model_id]
            
            logger.info(f"Model deleted: {model_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting model: {e}")
            return False
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get service status"""
        try:
            status = {
                'service': 'Advanced ML Service',
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'models': {
                    'configs': len(self.model_configs),
                    'trained_models': len(self.trained_models),
                    'training_jobs': len(self.training_jobs),
                    'evaluations': len(self.model_evaluations)
                },
                'datasets': {
                    'total': len(self.datasets),
                    'total_size': sum(dataset.size for dataset in self.datasets.values())
                },
                'algorithms': {
                    'classification': len(self.algorithms.get('classification', {})),
                    'regression': len(self.algorithms.get('regression', {})),
                    'clustering': len(self.algorithms.get('clustering', {})),
                    'dimensionality_reduction': len(self.algorithms.get('dimensionality_reduction', {}))
                },
                'queues': {
                    'training_queue_size': self.training_queue.qsize(),
                    'evaluation_queue_size': self.evaluation_queue.qsize()
                }
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting service status: {e}")
            return {
                'service': 'Advanced ML Service',
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }


























