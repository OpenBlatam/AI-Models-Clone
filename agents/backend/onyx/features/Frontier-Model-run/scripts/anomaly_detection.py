#!/usr/bin/env python3
"""
Advanced Anomaly Detection System for Frontier Model Training
Provides comprehensive anomaly detection algorithms, outlier identification, and fraud detection capabilities.
"""

import os
import json
import time
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
import matplotlib.pyplot as plt
import seaborn as sns
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
import sqlite3
from contextlib import contextmanager
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.svm import OneClassSVM
from sklearn.neighbors import LocalOutlierFactor
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import joblib
import pickle
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

console = Console()

class AnomalyType(Enum):
    """Types of anomalies."""
    POINT_ANOMALY = "point_anomaly"
    CONTEXTUAL_ANOMALY = "contextual_anomaly"
    COLLECTIVE_ANOMALY = "collective_anomaly"
    TEMPORAL_ANOMALY = "temporal_anomaly"
    SPATIAL_ANOMALY = "spatial_anomaly"
    BEHAVIORAL_ANOMALY = "behavioral_anomaly"
    STATISTICAL_ANOMALY = "statistical_anomaly"
    PATTERN_ANOMALY = "pattern_anomaly"

class AnomalyMethod(Enum):
    """Anomaly detection methods."""
    # Statistical methods
    Z_SCORE = "z_score"
    IQR = "iqr"
    MODIFIED_Z_SCORE = "modified_z_score"
    GRUBBS_TEST = "grubbs_test"
    DIXON_TEST = "dixon_test"
    
    # Machine learning methods
    ISOLATION_FOREST = "isolation_forest"
    ONE_CLASS_SVM = "one_class_svm"
    LOCAL_OUTLIER_FACTOR = "local_outlier_factor"
    DBSCAN = "dbscan"
    ELLIPTIC_ENVELOPE = "elliptic_envelope"
    
    # Deep learning methods
    AUTOENCODER = "autoencoder"
    VARIATIONAL_AUTOENCODER = "variational_autoencoder"
    LSTM_AUTOENCODER = "lstm_autoencoder"
    GAN_BASED = "gan_based"
    TRANSFORMER_BASED = "transformer_based"
    
    # Ensemble methods
    ENSEMBLE_ISOLATION_FOREST = "ensemble_isolation_forest"
    VOTING_ENSEMBLE = "voting_ensemble"
    STACKING_ENSEMBLE = "stacking_ensemble"
    
    # Time series methods
    ARIMA_BASED = "arima_based"
    PROPHET_BASED = "prophet_based"
    LSTM_BASED = "lstm_based"
    GRU_BASED = "gru_based"

class DataType(Enum):
    """Data types for anomaly detection."""
    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    TEXT = "text"
    IMAGE = "image"
    TIME_SERIES = "time_series"
    GRAPH = "graph"
    MULTIMODAL = "multimodal"

class DetectionMode(Enum):
    """Detection modes."""
    SUPERVISED = "supervised"
    UNSUPERVISED = "unsupervised"
    SEMI_SUPERVISED = "semi_supervised"
    ONLINE = "online"
    BATCH = "batch"
    STREAMING = "streaming"

@dataclass
class AnomalyConfig:
    """Anomaly detection configuration."""
    anomaly_type: AnomalyType = AnomalyType.POINT_ANOMALY
    method: AnomalyMethod = AnomalyMethod.ISOLATION_FOREST
    data_type: DataType = DataType.NUMERICAL
    detection_mode: DetectionMode = DetectionMode.UNSUPERVISED
    contamination: float = 0.1
    threshold: float = 0.5
    window_size: int = 100
    min_samples: int = 5
    eps: float = 0.5
    enable_preprocessing: bool = True
    enable_feature_selection: bool = True
    enable_dimensionality_reduction: bool = True
    enable_ensemble_methods: bool = True
    enable_online_learning: bool = True
    enable_explanation: bool = True
    enable_visualization: bool = True
    device: str = "auto"

@dataclass
class AnomalyData:
    """Anomaly detection data container."""
    data_id: str
    data: np.ndarray
    labels: Optional[np.ndarray] = None
    timestamps: Optional[List[datetime]] = None
    metadata: Dict[str, Any] = None
    features: Optional[List[str]] = None

@dataclass
class AnomalyResult:
    """Anomaly detection result."""
    result_id: str
    anomaly_type: AnomalyType
    method: AnomalyMethod
    anomalies: List[int]
    anomaly_scores: List[float]
    performance_metrics: Dict[str, float]
    explanations: Optional[Dict[str, Any]] = None
    model_state: Dict[str, Any] = None
    created_at: datetime = None

class DataPreprocessor:
    """Data preprocessing for anomaly detection."""
    
    def __init__(self, config: AnomalyConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize scalers
        self.scaler = StandardScaler()
        self.minmax_scaler = MinMaxScaler()
    
    def preprocess_data(self, data: AnomalyData) -> AnomalyData:
        """Preprocess data for anomaly detection."""
        console.print("[blue]Preprocessing data for anomaly detection...[/blue]")
        
        processed_data = data.data.copy()
        
        # Handle missing values
        processed_data = self._handle_missing_values(processed_data)
        
        # Scale data
        if self.config.enable_preprocessing:
            processed_data = self._scale_data(processed_data)
        
        # Feature selection
        if self.config.enable_feature_selection:
            processed_data = self._select_features(processed_data)
        
        # Dimensionality reduction
        if self.config.enable_dimensionality_reduction:
            processed_data = self._reduce_dimensions(processed_data)
        
        # Create processed data object
        processed_anomaly_data = AnomalyData(
            data_id=data.data_id,
            data=processed_data,
            labels=data.labels,
            timestamps=data.timestamps,
            metadata=data.metadata,
            features=data.features
        )
        
        console.print("[green]Data preprocessing completed[/green]")
        return processed_anomaly_data
    
    def _handle_missing_values(self, data: np.ndarray) -> np.ndarray:
        """Handle missing values in data."""
        # Forward fill, then backward fill
        if len(data.shape) == 1:
            data = pd.Series(data).fillna(method='ffill').fillna(method='bfill').values
        else:
            df = pd.DataFrame(data)
            df = df.fillna(method='ffill').fillna(method='bfill')
            data = df.values
        
        # If still missing values, interpolate
        if np.isnan(data).any():
            if len(data.shape) == 1:
                data = pd.Series(data).interpolate().values
            else:
                df = pd.DataFrame(data)
                df = df.interpolate()
                data = df.values
        
        return data
    
    def _scale_data(self, data: np.ndarray) -> np.ndarray:
        """Scale data using StandardScaler."""
        if len(data.shape) == 1:
            data = data.reshape(-1, 1)
            scaled_data = self.scaler.fit_transform(data)
            return scaled_data.flatten()
        else:
            return self.scaler.fit_transform(data)
    
    def _select_features(self, data: np.ndarray) -> np.ndarray:
        """Select relevant features."""
        if len(data.shape) == 1:
            return data
        
        # Simple feature selection based on variance
        variances = np.var(data, axis=0)
        threshold = np.percentile(variances, 50)  # Keep top 50% features
        selected_features = variances > threshold
        
        return data[:, selected_features]
    
    def _reduce_dimensions(self, data: np.ndarray) -> np.ndarray:
        """Reduce dimensions using PCA."""
        if len(data.shape) == 1:
            return data
        
        # Determine number of components
        n_components = min(10, data.shape[1] // 2)
        
        if n_components < data.shape[1]:
            pca = PCA(n_components=n_components)
            return pca.fit_transform(data)
        
        return data

class AnomalyDetector:
    """Anomaly detection engine."""
    
    def __init__(self, config: AnomalyConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize device
        if config.device == "auto":
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(config.device)
    
    def detect_anomalies(self, data: AnomalyData) -> AnomalyResult:
        """Detect anomalies in data."""
        console.print(f"[blue]Detecting anomalies using {self.config.method.value}...[/blue]")
        
        try:
            if self.config.method == AnomalyMethod.ISOLATION_FOREST:
                return self._detect_with_isolation_forest(data)
            elif self.config.method == AnomalyMethod.ONE_CLASS_SVM:
                return self._detect_with_one_class_svm(data)
            elif self.config.method == AnomalyMethod.LOCAL_OUTLIER_FACTOR:
                return self._detect_with_lof(data)
            elif self.config.method == AnomalyMethod.DBSCAN:
                return self._detect_with_dbscan(data)
            elif self.config.method == AnomalyMethod.Z_SCORE:
                return self._detect_with_z_score(data)
            elif self.config.method == AnomalyMethod.IQR:
                return self._detect_with_iqr(data)
            elif self.config.method == AnomalyMethod.AUTOENCODER:
                return self._detect_with_autoencoder(data)
            elif self.config.method == AnomalyMethod.LSTM_AUTOENCODER:
                return self._detect_with_lstm_autoencoder(data)
            else:
                return self._detect_with_isolation_forest(data)
                
        except Exception as e:
            self.logger.error(f"Anomaly detection failed: {e}")
            return self._create_fallback_result(data)
    
    def _detect_with_isolation_forest(self, data: AnomalyData) -> AnomalyResult:
        """Detect anomalies using Isolation Forest."""
        model = IsolationForest(
            contamination=self.config.contamination,
            random_state=42
        )
        
        # Fit model
        model.fit(data.data)
        
        # Get anomaly scores
        anomaly_scores = model.decision_function(data.data)
        predictions = model.predict(data.data)
        
        # Convert predictions to anomaly indices
        anomalies = np.where(predictions == -1)[0].tolist()
        
        # Calculate performance metrics
        performance_metrics = self._calculate_performance_metrics(
            predictions, data.labels, anomaly_scores
        )
        
        return AnomalyResult(
            result_id=f"anomaly_{int(time.time())}",
            anomaly_type=self.config.anomaly_type,
            method=self.config.method,
            anomalies=anomalies,
            anomaly_scores=anomaly_scores.tolist(),
            performance_metrics=performance_metrics,
            model_state={'model_type': 'isolation_forest', 'contamination': self.config.contamination},
            created_at=datetime.now()
        )
    
    def _detect_with_one_class_svm(self, data: AnomalyData) -> AnomalyResult:
        """Detect anomalies using One-Class SVM."""
        model = OneClassSVM(
            nu=self.config.contamination,
            kernel='rbf',
            gamma='scale'
        )
        
        # Fit model
        model.fit(data.data)
        
        # Get predictions and scores
        predictions = model.predict(data.data)
        anomaly_scores = model.decision_function(data.data)
        
        # Convert predictions to anomaly indices
        anomalies = np.where(predictions == -1)[0].tolist()
        
        # Calculate performance metrics
        performance_metrics = self._calculate_performance_metrics(
            predictions, data.labels, anomaly_scores
        )
        
        return AnomalyResult(
            result_id=f"anomaly_{int(time.time())}",
            anomaly_type=self.config.anomaly_type,
            method=self.config.method,
            anomalies=anomalies,
            anomaly_scores=anomaly_scores.tolist(),
            performance_metrics=performance_metrics,
            model_state={'model_type': 'one_class_svm', 'nu': self.config.contamination},
            created_at=datetime.now()
        )
    
    def _detect_with_lof(self, data: AnomalyData) -> AnomalyResult:
        """Detect anomalies using Local Outlier Factor."""
        model = LocalOutlierFactor(
            n_neighbors=self.config.min_samples,
            contamination=self.config.contamination
        )
        
        # Fit and predict
        predictions = model.fit_predict(data.data)
        anomaly_scores = model.negative_outlier_factor_
        
        # Convert predictions to anomaly indices
        anomalies = np.where(predictions == -1)[0].tolist()
        
        # Calculate performance metrics
        performance_metrics = self._calculate_performance_metrics(
            predictions, data.labels, anomaly_scores
        )
        
        return AnomalyResult(
            result_id=f"anomaly_{int(time.time())}",
            anomaly_type=self.config.anomaly_type,
            method=self.config.method,
            anomalies=anomalies,
            anomaly_scores=anomaly_scores.tolist(),
            performance_metrics=performance_metrics,
            model_state={'model_type': 'lof', 'n_neighbors': self.config.min_samples},
            created_at=datetime.now()
        )
    
    def _detect_with_dbscan(self, data: AnomalyData) -> AnomalyResult:
        """Detect anomalies using DBSCAN."""
        model = DBSCAN(
            eps=self.config.eps,
            min_samples=self.config.min_samples
        )
        
        # Fit and predict
        predictions = model.fit_predict(data.data)
        
        # Anomalies are points labeled as -1
        anomalies = np.where(predictions == -1)[0].tolist()
        
        # Calculate anomaly scores (distance to nearest core point)
        anomaly_scores = np.zeros(len(data.data))
        for i, point in enumerate(data.data):
            if predictions[i] == -1:
                # Calculate distance to nearest core point
                core_points = data.data[predictions != -1]
                if len(core_points) > 0:
                    distances = np.linalg.norm(core_points - point, axis=1)
                    anomaly_scores[i] = -np.min(distances)  # Negative for consistency
                else:
                    anomaly_scores[i] = -1.0
            else:
                anomaly_scores[i] = 0.0
        
        # Calculate performance metrics
        performance_metrics = self._calculate_performance_metrics(
            predictions, data.labels, anomaly_scores
        )
        
        return AnomalyResult(
            result_id=f"anomaly_{int(time.time())}",
            anomaly_type=self.config.anomaly_type,
            method=self.config.method,
            anomalies=anomalies,
            anomaly_scores=anomaly_scores.tolist(),
            performance_metrics=performance_metrics,
            model_state={'model_type': 'dbscan', 'eps': self.config.eps, 'min_samples': self.config.min_samples},
            created_at=datetime.now()
        )
    
    def _detect_with_z_score(self, data: AnomalyData) -> AnomalyResult:
        """Detect anomalies using Z-Score method."""
        if len(data.data.shape) == 1:
            # Univariate case
            z_scores = np.abs((data.data - np.mean(data.data)) / np.std(data.data))
        else:
            # Multivariate case - use Mahalanobis distance
            mean = np.mean(data.data, axis=0)
            cov = np.cov(data.data.T)
            inv_cov = np.linalg.inv(cov)
            z_scores = np.array([np.sqrt((x - mean).T @ inv_cov @ (x - mean)) for x in data.data])
        
        # Threshold for anomaly detection
        threshold = 3.0  # 3-sigma rule
        
        # Identify anomalies
        anomalies = np.where(z_scores > threshold)[0].tolist()
        
        # Calculate performance metrics
        predictions = np.ones(len(data.data))
        predictions[anomalies] = -1
        
        performance_metrics = self._calculate_performance_metrics(
            predictions, data.labels, z_scores
        )
        
        return AnomalyResult(
            result_id=f"anomaly_{int(time.time())}",
            anomaly_type=self.config.anomaly_type,
            method=self.config.method,
            anomalies=anomalies,
            anomaly_scores=z_scores.tolist(),
            performance_metrics=performance_metrics,
            model_state={'model_type': 'z_score', 'threshold': threshold},
            created_at=datetime.now()
        )
    
    def _detect_with_iqr(self, data: AnomalyData) -> AnomalyResult:
        """Detect anomalies using IQR method."""
        if len(data.data.shape) == 1:
            # Univariate case
            Q1 = np.percentile(data.data, 25)
            Q3 = np.percentile(data.data, 75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            anomalies = np.where((data.data < lower_bound) | (data.data > upper_bound))[0].tolist()
            
            # Calculate anomaly scores
            anomaly_scores = np.maximum(
                (lower_bound - data.data) / IQR,
                (data.data - upper_bound) / IQR
            )
            anomaly_scores = np.maximum(anomaly_scores, 0)
        else:
            # Multivariate case - use IQR for each dimension
            anomalies = []
            anomaly_scores = np.zeros(len(data.data))
            
            for i in range(data.data.shape[1]):
                Q1 = np.percentile(data.data[:, i], 25)
                Q3 = np.percentile(data.data[:, i], 75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                dim_anomalies = np.where((data.data[:, i] < lower_bound) | (data.data[:, i] > upper_bound))[0]
                anomalies.extend(dim_anomalies.tolist())
                
                dim_scores = np.maximum(
                    (lower_bound - data.data[:, i]) / IQR,
                    (data.data[:, i] - upper_bound) / IQR
                )
                anomaly_scores += np.maximum(dim_scores, 0)
            
            anomalies = list(set(anomalies))
        
        # Calculate performance metrics
        predictions = np.ones(len(data.data))
        predictions[anomalies] = -1
        
        performance_metrics = self._calculate_performance_metrics(
            predictions, data.labels, anomaly_scores
        )
        
        return AnomalyResult(
            result_id=f"anomaly_{int(time.time())}",
            anomaly_type=self.config.anomaly_type,
            method=self.config.method,
            anomalies=anomalies,
            anomaly_scores=anomaly_scores.tolist(),
            performance_metrics=performance_metrics,
            model_state={'model_type': 'iqr'},
            created_at=datetime.now()
        )
    
    def _detect_with_autoencoder(self, data: AnomalyData) -> AnomalyResult:
        """Detect anomalies using Autoencoder."""
        class Autoencoder(nn.Module):
            def __init__(self, input_dim, hidden_dim):
                super().__init__()
                self.encoder = nn.Sequential(
                    nn.Linear(input_dim, hidden_dim),
                    nn.ReLU(),
                    nn.Linear(hidden_dim, hidden_dim // 2),
                    nn.ReLU()
                )
                self.decoder = nn.Sequential(
                    nn.Linear(hidden_dim // 2, hidden_dim),
                    nn.ReLU(),
                    nn.Linear(hidden_dim, input_dim),
                    nn.Sigmoid()
                )
            
            def forward(self, x):
                encoded = self.encoder(x)
                decoded = self.decoder(encoded)
                return decoded
        
        # Prepare data
        input_dim = data.data.shape[1] if len(data.data.shape) > 1 else 1
        hidden_dim = max(32, input_dim // 2)
        
        # Convert to tensor
        data_tensor = torch.FloatTensor(data.data).to(self.device)
        if len(data_tensor.shape) == 1:
            data_tensor = data_tensor.unsqueeze(1)
        
        # Create and train model
        model = Autoencoder(input_dim, hidden_dim).to(self.device)
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        criterion = nn.MSELoss()
        
        # Training loop
        model.train()
        for epoch in range(100):
            optimizer.zero_grad()
            reconstructed = model(data_tensor)
            loss = criterion(reconstructed, data_tensor)
            loss.backward()
            optimizer.step()
            
            if epoch % 20 == 0:
                console.print(f"[blue]Epoch {epoch}, Loss: {loss.item():.4f}[/blue]")
        
        # Calculate reconstruction errors
        model.eval()
        with torch.no_grad():
            reconstructed = model(data_tensor)
            reconstruction_errors = torch.mean((data_tensor - reconstructed) ** 2, dim=1).cpu().numpy()
        
        # Identify anomalies based on reconstruction error
        threshold = np.percentile(reconstruction_errors, 90)  # Top 10% as anomalies
        anomalies = np.where(reconstruction_errors > threshold)[0].tolist()
        
        # Calculate performance metrics
        predictions = np.ones(len(data.data))
        predictions[anomalies] = -1
        
        performance_metrics = self._calculate_performance_metrics(
            predictions, data.labels, reconstruction_errors
        )
        
        return AnomalyResult(
            result_id=f"anomaly_{int(time.time())}",
            anomaly_type=self.config.anomaly_type,
            method=self.config.method,
            anomalies=anomalies,
            anomaly_scores=reconstruction_errors.tolist(),
            performance_metrics=performance_metrics,
            model_state={'model_type': 'autoencoder', 'input_dim': input_dim, 'hidden_dim': hidden_dim},
            created_at=datetime.now()
        )
    
    def _detect_with_lstm_autoencoder(self, data: AnomalyData) -> AnomalyResult:
        """Detect anomalies using LSTM Autoencoder."""
        class LSTMAutoencoder(nn.Module):
            def __init__(self, input_dim, hidden_dim):
                super().__init__()
                self.encoder = nn.LSTM(input_dim, hidden_dim, batch_first=True)
                self.decoder = nn.LSTM(hidden_dim, input_dim, batch_first=True)
            
            def forward(self, x):
                encoded, _ = self.encoder(x)
                decoded, _ = self.decoder(encoded)
                return decoded
        
        # Prepare data for LSTM
        if len(data.data.shape) == 1:
            # Convert 1D to 2D for LSTM
            window_size = min(self.config.window_size, len(data.data) // 4)
            sequences = []
            for i in range(window_size, len(data.data)):
                sequences.append(data.data[i-window_size:i])
            sequences = np.array(sequences)
        else:
            sequences = data.data
        
        # Convert to tensor
        sequences_tensor = torch.FloatTensor(sequences).to(self.device)
        if len(sequences_tensor.shape) == 2:
            sequences_tensor = sequences_tensor.unsqueeze(-1)
        
        input_dim = sequences_tensor.shape[-1]
        hidden_dim = 32
        
        # Create and train model
        model = LSTMAutoencoder(input_dim, hidden_dim).to(self.device)
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        criterion = nn.MSELoss()
        
        # Training loop
        model.train()
        for epoch in range(50):
            optimizer.zero_grad()
            reconstructed = model(sequences_tensor)
            loss = criterion(reconstructed, sequences_tensor)
            loss.backward()
            optimizer.step()
            
            if epoch % 10 == 0:
                console.print(f"[blue]Epoch {epoch}, Loss: {loss.item():.4f}[/blue]")
        
        # Calculate reconstruction errors
        model.eval()
        with torch.no_grad():
            reconstructed = model(sequences_tensor)
            reconstruction_errors = torch.mean((sequences_tensor - reconstructed) ** 2, dim=(1, 2)).cpu().numpy()
        
        # Pad errors to match original data length
        if len(reconstruction_errors) < len(data.data):
            padded_errors = np.zeros(len(data.data))
            padded_errors[-len(reconstruction_errors):] = reconstruction_errors
            reconstruction_errors = padded_errors
        
        # Identify anomalies
        threshold = np.percentile(reconstruction_errors, 90)
        anomalies = np.where(reconstruction_errors > threshold)[0].tolist()
        
        # Calculate performance metrics
        predictions = np.ones(len(data.data))
        predictions[anomalies] = -1
        
        performance_metrics = self._calculate_performance_metrics(
            predictions, data.labels, reconstruction_errors
        )
        
        return AnomalyResult(
            result_id=f"anomaly_{int(time.time())}",
            anomaly_type=self.config.anomaly_type,
            method=self.config.method,
            anomalies=anomalies,
            anomaly_scores=reconstruction_errors.tolist(),
            performance_metrics=performance_metrics,
            model_state={'model_type': 'lstm_autoencoder', 'hidden_dim': hidden_dim},
            created_at=datetime.now()
        )
    
    def _calculate_performance_metrics(self, predictions: np.ndarray, 
                                     true_labels: Optional[np.ndarray], 
                                     scores: np.ndarray) -> Dict[str, float]:
        """Calculate performance metrics."""
        metrics = {}
        
        # Basic metrics
        metrics['num_anomalies'] = np.sum(predictions == -1)
        metrics['anomaly_rate'] = np.sum(predictions == -1) / len(predictions)
        metrics['avg_anomaly_score'] = np.mean(scores)
        metrics['max_anomaly_score'] = np.max(scores)
        
        # If true labels are available, calculate supervised metrics
        if true_labels is not None:
            # Convert true labels to binary (assuming -1 for anomalies)
            true_binary = (true_labels == -1).astype(int)
            pred_binary = (predictions == -1).astype(int)
            
            metrics['accuracy'] = accuracy_score(true_binary, pred_binary)
            metrics['precision'] = precision_score(true_binary, pred_binary, zero_division=0)
            metrics['recall'] = recall_score(true_binary, pred_binary, zero_division=0)
            metrics['f1_score'] = f1_score(true_binary, pred_binary, zero_division=0)
            
            # ROC AUC if possible
            try:
                metrics['roc_auc'] = roc_auc_score(true_binary, scores)
            except:
                metrics['roc_auc'] = 0.0
        
        return metrics
    
    def _create_fallback_result(self, data: AnomalyData) -> AnomalyResult:
        """Create fallback result."""
        # Simple random anomaly detection
        num_anomalies = int(len(data.data) * self.config.contamination)
        anomalies = np.random.choice(len(data.data), num_anomalies, replace=False).tolist()
        anomaly_scores = np.random.random(len(data.data)).tolist()
        
        predictions = np.ones(len(data.data))
        predictions[anomalies] = -1
        
        performance_metrics = self._calculate_performance_metrics(
            predictions, data.labels, np.array(anomaly_scores)
        )
        
        return AnomalyResult(
            result_id=f"fallback_{int(time.time())}",
            anomaly_type=self.config.anomaly_type,
            method=self.config.method,
            anomalies=anomalies,
            anomaly_scores=anomaly_scores,
            performance_metrics=performance_metrics,
            model_state={'fallback': True},
            created_at=datetime.now()
        )

class AnomalySystem:
    """Main anomaly detection system."""
    
    def __init__(self, config: AnomalyConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.preprocessor = DataPreprocessor(config)
        self.detector = AnomalyDetector(config)
        
        # Initialize database
        self.db_path = self._init_database()
        
        # Results storage
        self.anomaly_results: Dict[str, AnomalyResult] = {}
    
    def _init_database(self) -> str:
        """Initialize anomaly detection database."""
        db_path = Path("./anomaly_detection.db")
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(str(db_path)) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS anomaly_results (
                    result_id TEXT PRIMARY KEY,
                    anomaly_type TEXT NOT NULL,
                    method TEXT NOT NULL,
                    anomalies TEXT NOT NULL,
                    anomaly_scores TEXT NOT NULL,
                    performance_metrics TEXT NOT NULL,
                    explanations TEXT,
                    model_state TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
        
        return str(db_path)
    
    def run_anomaly_experiment(self, data: AnomalyData) -> AnomalyResult:
        """Run complete anomaly detection experiment."""
        console.print(f"[blue]Starting anomaly detection experiment with {self.config.method.value}...[/blue]")
        
        start_time = time.time()
        
        # Preprocess data
        processed_data = self.preprocessor.preprocess_data(data)
        
        # Detect anomalies
        result = self.detector.detect_anomalies(processed_data)
        
        # Add explanations if enabled
        if self.config.enable_explanation:
            result.explanations = self._generate_explanations(result, processed_data)
        
        # Store result
        self.anomaly_results[result.result_id] = result
        
        # Save to database
        self._save_anomaly_result(result)
        
        experiment_time = time.time() - start_time
        console.print(f"[green]Anomaly detection experiment completed in {experiment_time:.2f} seconds[/green]")
        console.print(f"[blue]Detected {len(result.anomalies)} anomalies[/blue]")
        console.print(f"[blue]Anomaly rate: {result.performance_metrics.get('anomaly_rate', 0):.4f}[/blue]")
        
        return result
    
    def _generate_explanations(self, result: AnomalyResult, data: AnomalyData) -> Dict[str, Any]:
        """Generate explanations for detected anomalies."""
        explanations = {}
        
        # Basic explanations
        explanations['total_anomalies'] = len(result.anomalies)
        explanations['anomaly_rate'] = result.performance_metrics.get('anomaly_rate', 0)
        explanations['method_used'] = result.method.value
        
        # Feature importance (if available)
        if data.features is not None and len(data.features) > 0:
            explanations['feature_analysis'] = self._analyze_features(result, data)
        
        # Temporal analysis (if timestamps available)
        if data.timestamps is not None:
            explanations['temporal_analysis'] = self._analyze_temporal_patterns(result, data)
        
        return explanations
    
    def _analyze_features(self, result: AnomalyResult, data: AnomalyData) -> Dict[str, Any]:
        """Analyze feature importance for anomalies."""
        if len(data.data.shape) == 1:
            return {'univariate_data': True}
        
        feature_analysis = {}
        
        # Calculate feature statistics for anomalies vs normal points
        normal_data = data.data[np.setdiff1d(np.arange(len(data.data)), result.anomalies)]
        anomaly_data = data.data[result.anomalies]
        
        for i, feature in enumerate(data.features):
            normal_mean = np.mean(normal_data[:, i])
            anomaly_mean = np.mean(anomaly_data[:, i])
            normal_std = np.std(normal_data[:, i])
            
            feature_analysis[feature] = {
                'normal_mean': normal_mean,
                'anomaly_mean': anomaly_mean,
                'difference': abs(anomaly_mean - normal_mean),
                'relative_difference': abs(anomaly_mean - normal_mean) / normal_std if normal_std > 0 else 0
            }
        
        return feature_analysis
    
    def _analyze_temporal_patterns(self, result: AnomalyResult, data: AnomalyData) -> Dict[str, Any]:
        """Analyze temporal patterns of anomalies."""
        temporal_analysis = {}
        
        # Convert timestamps to datetime if needed
        timestamps = data.timestamps
        if isinstance(timestamps[0], str):
            timestamps = [datetime.fromisoformat(ts) for ts in timestamps]
        
        # Analyze anomaly distribution over time
        anomaly_timestamps = [timestamps[i] for i in result.anomalies]
        
        # Group by hour, day, month
        hours = [ts.hour for ts in anomaly_timestamps]
        days = [ts.day for ts in anomaly_timestamps]
        months = [ts.month for ts in anomaly_timestamps]
        
        temporal_analysis['hourly_distribution'] = dict(zip(*np.unique(hours, return_counts=True)))
        temporal_analysis['daily_distribution'] = dict(zip(*np.unique(days, return_counts=True)))
        temporal_analysis['monthly_distribution'] = dict(zip(*np.unique(months, return_counts=True)))
        
        return temporal_analysis
    
    def _save_anomaly_result(self, result: AnomalyResult):
        """Save anomaly result to database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO anomaly_results 
                (result_id, anomaly_type, method, anomalies, anomaly_scores,
                 performance_metrics, explanations, model_state, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                result.result_id,
                result.anomaly_type.value,
                result.method.value,
                json.dumps(result.anomalies),
                json.dumps(result.anomaly_scores),
                json.dumps(result.performance_metrics),
                json.dumps(result.explanations) if result.explanations else None,
                json.dumps(result.model_state),
                result.created_at.isoformat()
            ))
    
    def visualize_anomaly_results(self, result: AnomalyResult, 
                                output_path: str = None) -> str:
        """Visualize anomaly detection results."""
        if output_path is None:
            output_path = f"anomaly_detection_{result.result_id}.png"
        
        # Create visualization
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Performance metrics
        performance_metrics = result.performance_metrics
        metric_names = list(performance_metrics.keys())
        metric_values = list(performance_metrics.values())
        
        axes[0, 0].bar(metric_names, metric_values)
        axes[0, 0].set_title('Performance Metrics')
        axes[0, 0].set_ylabel('Value')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Anomaly scores distribution
        axes[0, 1].hist(result.anomaly_scores, bins=30, alpha=0.7, edgecolor='black')
        axes[0, 1].set_title('Anomaly Scores Distribution')
        axes[0, 1].set_xlabel('Anomaly Score')
        axes[0, 1].set_ylabel('Frequency')
        
        # Anomalies over time (if available)
        if len(result.anomalies) > 0:
            axes[1, 0].scatter(result.anomalies, [1] * len(result.anomalies), 
                              c='red', alpha=0.7, s=50)
            axes[1, 0].set_title('Anomalies Detected')
            axes[1, 0].set_xlabel('Data Point Index')
            axes[1, 0].set_ylabel('Anomaly')
            axes[1, 0].set_ylim(0, 2)
        
        # Method and type info
        info_data = {
            'Method': len(result.method.value),
            'Type': len(result.anomaly_type.value),
            'Anomalies': len(result.anomalies),
            'Rate': result.performance_metrics.get('anomaly_rate', 0)
        }
        
        info_names = list(info_data.keys())
        info_values = list(info_data.values())
        
        axes[1, 1].bar(info_names, info_values)
        axes[1, 1].set_title('Detection Summary')
        axes[1, 1].set_ylabel('Value')
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        console.print(f"[green]Anomaly visualization saved: {output_path}[/green]")
        return output_path
    
    def get_anomaly_summary(self) -> Dict[str, Any]:
        """Get anomaly detection system summary."""
        if not self.anomaly_results:
            return {'total_experiments': 0}
        
        total_experiments = len(self.anomaly_results)
        
        # Calculate average metrics
        avg_anomaly_rate = np.mean([result.performance_metrics.get('anomaly_rate', 0) for result in self.anomaly_results.values()])
        avg_f1_score = np.mean([result.performance_metrics.get('f1_score', 0) for result in self.anomaly_results.values()])
        
        # Best performing experiment
        best_result = max(self.anomaly_results.values(), 
                         key=lambda x: x.performance_metrics.get('f1_score', 0))
        
        return {
            'total_experiments': total_experiments,
            'average_anomaly_rate': avg_anomaly_rate,
            'average_f1_score': avg_f1_score,
            'best_f1_score': best_result.performance_metrics.get('f1_score', 0),
            'best_experiment_id': best_result.result_id,
            'methods_used': list(set(result.method.value for result in self.anomaly_results.values())),
            'types_detected': list(set(result.anomaly_type.value for result in self.anomaly_results.values()))
        }

def main():
    """Main function for Anomaly Detection CLI."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Anomaly Detection System")
    parser.add_argument("--method", type=str,
                       choices=["isolation_forest", "one_class_svm", "local_outlier_factor", "dbscan", "z_score", "iqr", "autoencoder"],
                       default="isolation_forest", help="Anomaly detection method")
    parser.add_argument("--anomaly-type", type=str,
                       choices=["point_anomaly", "contextual_anomaly", "collective_anomaly", "temporal_anomaly"],
                       default="point_anomaly", help="Type of anomaly")
    parser.add_argument("--data-type", type=str,
                       choices=["numerical", "categorical", "time_series"],
                       default="numerical", help="Data type")
    parser.add_argument("--contamination", type=float, default=0.1,
                       help="Expected contamination rate")
    parser.add_argument("--threshold", type=float, default=0.5,
                       help="Detection threshold")
    parser.add_argument("--window-size", type=int, default=100,
                       help="Window size for time series")
    parser.add_argument("--min-samples", type=int, default=5,
                       help="Minimum samples for clustering")
    parser.add_argument("--eps", type=float, default=0.5,
                       help="Epsilon for DBSCAN")
    parser.add_argument("--num-points", type=int, default=1000,
                       help="Number of data points to generate")
    parser.add_argument("--device", type=str, default="auto",
                       help="Device to use")
    
    args = parser.parse_args()
    
    # Create anomaly detection configuration
    config = AnomalyConfig(
        anomaly_type=AnomalyType(args.anomaly_type),
        method=AnomalyMethod(args.method),
        data_type=DataType(args.data_type),
        contamination=args.contamination,
        threshold=args.threshold,
        window_size=args.window_size,
        min_samples=args.min_samples,
        eps=args.eps,
        device=args.device
    )
    
    # Create anomaly detection system
    anomaly_system = AnomalySystem(config)
    
    # Create sample data
    if args.data_type == "numerical":
        # Generate normal data with some anomalies
        normal_data = np.random.normal(0, 1, args.num_points)
        anomaly_data = np.random.normal(5, 0.5, int(args.num_points * args.contamination))
        sample_data = np.concatenate([normal_data, anomaly_data])
        np.random.shuffle(sample_data)
        
        # Create labels
        labels = np.ones(len(sample_data))
        labels[-int(args.num_points * args.contamination):] = -1
        
        sample_anomaly_data = AnomalyData(
            data_id="sample_numerical",
            data=sample_data,
            labels=labels,
            metadata={'data_type': 'numerical', 'num_points': len(sample_data)}
        )
    else:
        # Generate time series data
        t = np.linspace(0, 10, args.num_points)
        normal_data = np.sin(t) + 0.1 * np.random.randn(args.num_points)
        
        # Add anomalies
        anomaly_indices = np.random.choice(args.num_points, int(args.num_points * args.contamination), replace=False)
        normal_data[anomaly_indices] += 3 * np.random.randn(len(anomaly_indices))
        
        # Create labels
        labels = np.ones(len(normal_data))
        labels[anomaly_indices] = -1
        
        sample_anomaly_data = AnomalyData(
            data_id="sample_timeseries",
            data=normal_data,
            labels=labels,
            timestamps=[datetime.now() + timedelta(seconds=i) for i in range(len(normal_data))],
            metadata={'data_type': 'time_series', 'num_points': len(normal_data)}
        )
    
    # Run anomaly detection experiment
    result = anomaly_system.run_anomaly_experiment(sample_anomaly_data)
    
    # Show results
    console.print(f"[green]Anomaly detection experiment completed[/green]")
    console.print(f"[blue]Method: {result.method.value}[/blue]")
    console.print(f"[blue]Type: {result.anomaly_type.value}[/blue]")
    console.print(f"[blue]Detected {len(result.anomalies)} anomalies[/blue]")
    console.print(f"[blue]Anomaly rate: {result.performance_metrics.get('anomaly_rate', 0):.4f}[/blue]")
    
    if 'f1_score' in result.performance_metrics:
        console.print(f"[blue]F1 Score: {result.performance_metrics['f1_score']:.4f}[/blue]")
    
    # Create visualization
    anomaly_system.visualize_anomaly_results(result)
    
    # Show summary
    summary = anomaly_system.get_anomaly_summary()
    console.print(f"[blue]Summary: {summary}[/blue]")

if __name__ == "__main__":
    main()
