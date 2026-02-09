"""
Unified Data Service - Consolidated data processing functionality
Combines ML, data processing, ETL, and data management services
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import accuracy_score, mean_squared_error, silhouette_score
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
import joblib
import pickle
import json
import sqlite3
import aiofiles
from datetime import datetime, timedelta
import hashlib
import uuid
from pathlib import Path
import zipfile
import tarfile

logger = logging.getLogger(__name__)

class DataType(Enum):
    """Data Types"""
    TEXT = "text"
    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    DATETIME = "datetime"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"
    PARQUET = "parquet"

class ModelType(Enum):
    """Model Types"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    DEEP_LEARNING = "deep_learning"
    TIME_SERIES = "time_series"
    NLP = "nlp"
    COMPUTER_VISION = "computer_vision"

class ProcessingStatus(Enum):
    """Processing Status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class Dataset:
    """Dataset Definition"""
    id: str
    name: str
    description: str
    data_type: DataType
    file_path: str
    size: int
    rows: int
    columns: int
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]
    schema: Dict[str, str] = None

@dataclass
class Model:
    """Model Definition"""
    id: str
    name: str
    model_type: ModelType
    algorithm: str
    parameters: Dict[str, Any]
    accuracy: float = 0.0
    created_at: datetime
    updated_at: datetime
    file_path: str = None
    training_data_id: str = None
    status: ProcessingStatus = ProcessingStatus.PENDING

@dataclass
class ProcessingJob:
    """Processing Job Definition"""
    id: str
    name: str
    job_type: str
    dataset_id: str
    parameters: Dict[str, Any]
    status: ProcessingStatus = ProcessingStatus.PENDING
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None

class UnifiedDataService:
    """
    Unified Data Service - Consolidated data processing functionality
    Handles ML, data processing, ETL, feature engineering, and data management
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.data_storage_path = config.get("data_storage_path", "./data_storage")
        self.model_storage_path = config.get("model_storage_path", "./model_storage")
        
        # Data storage
        self.datasets: Dict[str, Dataset] = {}
        self.models: Dict[str, Model] = {}
        self.processing_jobs: Dict[str, ProcessingJob] = {}
        
        # Processing engines
        self.scalers: Dict[str, StandardScaler] = {}
        self.encoders: Dict[str, LabelEncoder] = {}
        
        # ML models
        self.trained_models: Dict[str, Any] = {}
        
        # Database connection
        self.db_path = f"{self.data_storage_path}/data_service.db"
        self._init_database()
        
        logger.info("UnifiedDataService initialized")
    
    def _init_database(self):
        """Initialize SQLite database"""
        try:
            Path(self.data_storage_path).mkdir(parents=True, exist_ok=True)
            Path(self.model_storage_path).mkdir(parents=True, exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS datasets (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    data_type TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    size INTEGER,
                    rows INTEGER,
                    columns INTEGER,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    metadata TEXT,
                    schema TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS models (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    model_type TEXT NOT NULL,
                    algorithm TEXT NOT NULL,
                    parameters TEXT,
                    accuracy REAL,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    file_path TEXT,
                    training_data_id TEXT,
                    status TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS processing_jobs (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    job_type TEXT NOT NULL,
                    dataset_id TEXT NOT NULL,
                    parameters TEXT,
                    status TEXT,
                    created_at TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    result TEXT,
                    error TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
    
    async def load_dataset(self, 
                          file_path: str,
                          name: str,
                          description: str = "",
                          data_type: DataType = None) -> str:
        """Load a dataset"""
        try:
            dataset_id = str(uuid.uuid4())
            
            # Determine data type if not provided
            if data_type is None:
                data_type = self._detect_data_type(file_path)
            
            # Load data to get metadata
            if data_type == DataType.CSV:
                df = pd.read_csv(file_path)
            elif data_type == DataType.EXCEL:
                df = pd.read_excel(file_path)
            elif data_type == DataType.PARQUET:
                df = pd.read_parquet(file_path)
            elif data_type == DataType.JSON:
                df = pd.read_json(file_path)
            else:
                raise ValueError(f"Unsupported data type: {data_type}")
            
            # Get file size
            file_size = Path(file_path).stat().st_size
            
            # Create dataset
            dataset = Dataset(
                id=dataset_id,
                name=name,
                description=description,
                data_type=data_type,
                file_path=file_path,
                size=file_size,
                rows=len(df),
                columns=len(df.columns),
                created_at=datetime.now(),
                updated_at=datetime.now(),
                metadata={
                    "columns": list(df.columns),
                    "dtypes": df.dtypes.to_dict(),
                    "null_counts": df.isnull().sum().to_dict(),
                    "memory_usage": df.memory_usage(deep=True).sum()
                },
                schema=self._infer_schema(df)
            )
            
            # Store in memory and database
            self.datasets[dataset_id] = dataset
            await self._save_dataset_to_db(dataset)
            
            logger.info(f"Dataset {name} loaded with ID {dataset_id}")
            return dataset_id
            
        except Exception as e:
            logger.error(f"Error loading dataset: {e}")
            raise
    
    def _detect_data_type(self, file_path: str) -> DataType:
        """Detect data type from file extension"""
        extension = Path(file_path).suffix.lower()
        
        if extension == '.csv':
            return DataType.CSV
        elif extension in ['.xlsx', '.xls']:
            return DataType.EXCEL
        elif extension == '.parquet':
            return DataType.PARQUET
        elif extension == '.json':
            return DataType.JSON
        else:
            return DataType.TEXT
    
    def _infer_schema(self, df: pd.DataFrame) -> Dict[str, str]:
        """Infer schema from DataFrame"""
        schema = {}
        for column in df.columns:
            dtype = str(df[column].dtype)
            if 'int' in dtype:
                schema[column] = 'integer'
            elif 'float' in dtype:
                schema[column] = 'float'
            elif 'bool' in dtype:
                schema[column] = 'boolean'
            elif 'datetime' in dtype:
                schema[column] = 'datetime'
            else:
                schema[column] = 'string'
        return schema
    
    async def _save_dataset_to_db(self, dataset: Dataset):
        """Save dataset to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO datasets 
                (id, name, description, data_type, file_path, size, rows, columns, 
                 created_at, updated_at, metadata, schema)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                dataset.id, dataset.name, dataset.description, dataset.data_type.value,
                dataset.file_path, dataset.size, dataset.rows, dataset.columns,
                dataset.created_at.isoformat(), dataset.updated_at.isoformat(),
                json.dumps(dataset.metadata), json.dumps(dataset.schema)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error saving dataset to database: {e}")
    
    async def get_dataset(self, dataset_id: str) -> Optional[pd.DataFrame]:
        """Get dataset as DataFrame"""
        try:
            if dataset_id not in self.datasets:
                return None
            
            dataset = self.datasets[dataset_id]
            
            # Load data
            if dataset.data_type == DataType.CSV:
                return pd.read_csv(dataset.file_path)
            elif dataset.data_type == DataType.EXCEL:
                return pd.read_excel(dataset.file_path)
            elif dataset.data_type == DataType.PARQUET:
                return pd.read_parquet(dataset.file_path)
            elif dataset.data_type == DataType.JSON:
                return pd.read_json(dataset.file_path)
            else:
                raise ValueError(f"Unsupported data type: {dataset.data_type}")
                
        except Exception as e:
            logger.error(f"Error getting dataset: {e}")
            return None
    
    async def process_data(self, 
                          dataset_id: str,
                          processing_type: str,
                          parameters: Dict[str, Any]) -> str:
        """Process data with specified operations"""
        try:
            job_id = str(uuid.uuid4())
            
            job = ProcessingJob(
                id=job_id,
                name=f"{processing_type}_{dataset_id}",
                job_type=processing_type,
                dataset_id=dataset_id,
                parameters=parameters,
                created_at=datetime.now()
            )
            
            self.processing_jobs[job_id] = job
            
            # Start processing
            asyncio.create_task(self._process_data_async(job))
            
            logger.info(f"Data processing job {job_id} started")
            return job_id
            
        except Exception as e:
            logger.error(f"Error starting data processing: {e}")
            raise
    
    async def _process_data_async(self, job: ProcessingJob):
        """Process data asynchronously"""
        try:
            job.status = ProcessingStatus.PROCESSING
            job.started_at = datetime.now()
            
            # Get dataset
            df = await self.get_dataset(job.dataset_id)
            if df is None:
                raise ValueError(f"Dataset {job.dataset_id} not found")
            
            # Process based on job type
            if job.job_type == "clean":
                result = await self._clean_data(df, job.parameters)
            elif job.job_type == "transform":
                result = await self._transform_data(df, job.parameters)
            elif job.job_type == "feature_engineering":
                result = await self._feature_engineering(df, job.parameters)
            elif job.job_type == "split":
                result = await self._split_data(df, job.parameters)
            else:
                raise ValueError(f"Unsupported processing type: {job.job_type}")
            
            job.result = result
            job.status = ProcessingStatus.COMPLETED
            job.completed_at = datetime.now()
            
            logger.info(f"Data processing job {job.id} completed")
            
        except Exception as e:
            job.status = ProcessingStatus.FAILED
            job.error = str(e)
            job.completed_at = datetime.now()
            logger.error(f"Data processing job {job.id} failed: {e}")
    
    async def _clean_data(self, df: pd.DataFrame, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Clean data"""
        try:
            original_shape = df.shape
            
            # Remove duplicates
            if parameters.get("remove_duplicates", False):
                df = df.drop_duplicates()
            
            # Handle missing values
            missing_strategy = parameters.get("missing_strategy", "drop")
            if missing_strategy == "drop":
                df = df.dropna()
            elif missing_strategy == "fill_mean":
                numeric_columns = df.select_dtypes(include=[np.number]).columns
                df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].mean())
            elif missing_strategy == "fill_median":
                numeric_columns = df.select_dtypes(include=[np.number]).columns
                df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].median())
            elif missing_strategy == "fill_mode":
                for column in df.columns:
                    df[column] = df[column].fillna(df[column].mode()[0] if not df[column].mode().empty else "")
            
            # Remove outliers
            if parameters.get("remove_outliers", False):
                numeric_columns = df.select_dtypes(include=[np.number]).columns
                for column in numeric_columns:
                    Q1 = df[column].quantile(0.25)
                    Q3 = df[column].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
            
            return {
                "cleaned_data": df,
                "original_shape": original_shape,
                "cleaned_shape": df.shape,
                "rows_removed": original_shape[0] - df.shape[0],
                "columns_removed": original_shape[1] - df.shape[1]
            }
            
        except Exception as e:
            logger.error(f"Error cleaning data: {e}")
            raise
    
    async def _transform_data(self, df: pd.DataFrame, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data"""
        try:
            # Scaling
            if parameters.get("scaling", False):
                scaler = StandardScaler()
                numeric_columns = df.select_dtypes(include=[np.number]).columns
                df[numeric_columns] = scaler.fit_transform(df[numeric_columns])
                self.scalers["default"] = scaler
            
            # Encoding categorical variables
            if parameters.get("encoding", False):
                categorical_columns = df.select_dtypes(include=['object']).columns
                for column in categorical_columns:
                    encoder = LabelEncoder()
                    df[column] = encoder.fit_transform(df[column].astype(str))
                    self.encoders[column] = encoder
            
            # Log transformation
            if parameters.get("log_transform", False):
                numeric_columns = df.select_dtypes(include=[np.number]).columns
                for column in numeric_columns:
                    if df[column].min() > 0:  # Only if all values are positive
                        df[column] = np.log1p(df[column])
            
            return {
                "transformed_data": df,
                "scaling_applied": parameters.get("scaling", False),
                "encoding_applied": parameters.get("encoding", False),
                "log_transform_applied": parameters.get("log_transform", False)
            }
            
        except Exception as e:
            logger.error(f"Error transforming data: {e}")
            raise
    
    async def _feature_engineering(self, df: pd.DataFrame, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Feature engineering"""
        try:
            # Create new features
            new_features = []
            
            # Polynomial features
            if parameters.get("polynomial_features", False):
                from sklearn.preprocessing import PolynomialFeatures
                poly = PolynomialFeatures(degree=2, include_bias=False)
                numeric_columns = df.select_dtypes(include=[np.number]).columns
                if len(numeric_columns) > 0:
                    poly_features = poly.fit_transform(df[numeric_columns])
                    poly_df = pd.DataFrame(
                        poly_features,
                        columns=poly.get_feature_names_out(numeric_columns)
                    )
                    df = pd.concat([df, poly_df], axis=1)
                    new_features.extend(poly_df.columns.tolist())
            
            # Interaction features
            if parameters.get("interaction_features", False):
                numeric_columns = df.select_dtypes(include=[np.number]).columns
                for i, col1 in enumerate(numeric_columns):
                    for col2 in numeric_columns[i+1:]:
                        interaction_name = f"{col1}_x_{col2}"
                        df[interaction_name] = df[col1] * df[col2]
                        new_features.append(interaction_name)
            
            # Date features
            date_columns = df.select_dtypes(include=['datetime64']).columns
            for column in date_columns:
                df[f"{column}_year"] = df[column].dt.year
                df[f"{column}_month"] = df[column].dt.month
                df[f"{column}_day"] = df[column].dt.day
                df[f"{column}_weekday"] = df[column].dt.weekday
                new_features.extend([f"{column}_year", f"{column}_month", f"{column}_day", f"{column}_weekday"])
            
            return {
                "engineered_data": df,
                "new_features": new_features,
                "total_features": len(df.columns)
            }
            
        except Exception as e:
            logger.error(f"Error in feature engineering: {e}")
            raise
    
    async def _split_data(self, df: pd.DataFrame, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Split data for training/testing"""
        try:
            target_column = parameters.get("target_column")
            test_size = parameters.get("test_size", 0.2)
            random_state = parameters.get("random_state", 42)
            
            if target_column and target_column in df.columns:
                X = df.drop(columns=[target_column])
                y = df[target_column]
                
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=test_size, random_state=random_state
                )
                
                return {
                    "X_train": X_train,
                    "X_test": X_test,
                    "y_train": y_train,
                    "y_test": y_test,
                    "train_size": len(X_train),
                    "test_size": len(X_test)
                }
            else:
                # Split without target
                train_size = int(len(df) * (1 - test_size))
                train_data = df[:train_size]
                test_data = df[train_size:]
                
                return {
                    "train_data": train_data,
                    "test_data": test_data,
                    "train_size": len(train_data),
                    "test_size": len(test_data)
                }
                
        except Exception as e:
            logger.error(f"Error splitting data: {e}")
            raise
    
    async def train_model(self, 
                         dataset_id: str,
                         model_type: ModelType,
                         algorithm: str,
                         parameters: Dict[str, Any]) -> str:
        """Train a machine learning model"""
        try:
            model_id = str(uuid.uuid4())
            
            # Get dataset
            df = await self.get_dataset(dataset_id)
            if df is None:
                raise ValueError(f"Dataset {dataset_id} not found")
            
            # Create model
            model = Model(
                id=model_id,
                name=f"{algorithm}_{dataset_id}",
                model_type=model_type,
                algorithm=algorithm,
                parameters=parameters,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                training_data_id=dataset_id
            )
            
            self.models[model_id] = model
            
            # Start training
            asyncio.create_task(self._train_model_async(model, df))
            
            logger.info(f"Model training started for {model_id}")
            return model_id
            
        except Exception as e:
            logger.error(f"Error starting model training: {e}")
            raise
    
    async def _train_model_async(self, model: Model, df: pd.DataFrame):
        """Train model asynchronously"""
        try:
            model.status = ProcessingStatus.PROCESSING
            
            # Prepare data
            target_column = model.parameters.get("target_column")
            if not target_column or target_column not in df.columns:
                raise ValueError("Target column not specified or not found")
            
            X = df.drop(columns=[target_column])
            y = df[target_column]
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Train model based on algorithm
            if model.algorithm == "random_forest_classifier":
                ml_model = RandomForestClassifier(**model.parameters.get("model_params", {}))
            elif model.algorithm == "random_forest_regressor":
                ml_model = RandomForestRegressor(**model.parameters.get("model_params", {}))
            elif model.algorithm == "linear_regression":
                ml_model = LinearRegression(**model.parameters.get("model_params", {}))
            elif model.algorithm == "logistic_regression":
                ml_model = LogisticRegression(**model.parameters.get("model_params", {}))
            elif model.algorithm == "kmeans":
                ml_model = KMeans(**model.parameters.get("model_params", {}))
            else:
                raise ValueError(f"Unsupported algorithm: {model.algorithm}")
            
            # Train model
            ml_model.fit(X_train, y_train)
            
            # Evaluate model
            if model.model_type in [ModelType.CLASSIFICATION, ModelType.REGRESSION]:
                y_pred = ml_model.predict(X_test)
                if model.model_type == ModelType.CLASSIFICATION:
                    accuracy = accuracy_score(y_test, y_pred)
                else:
                    accuracy = 1 / (1 + mean_squared_error(y_test, y_pred))
            else:
                accuracy = 0.0
            
            # Save model
            model_file_path = f"{self.model_storage_path}/model_{model.id}.joblib"
            joblib.dump(ml_model, model_file_path)
            
            # Update model
            model.accuracy = accuracy
            model.file_path = model_file_path
            model.status = ProcessingStatus.COMPLETED
            model.updated_at = datetime.now()
            
            # Store trained model
            self.trained_models[model.id] = ml_model
            
            logger.info(f"Model {model.id} training completed with accuracy {accuracy}")
            
        except Exception as e:
            model.status = ProcessingStatus.FAILED
            model.updated_at = datetime.now()
            logger.error(f"Model {model.id} training failed: {e}")
    
    async def predict(self, model_id: str, data: Union[pd.DataFrame, Dict[str, Any]]) -> Any:
        """Make predictions using trained model"""
        try:
            if model_id not in self.trained_models:
                raise ValueError(f"Model {model_id} not found or not trained")
            
            model = self.trained_models[model_id]
            
            # Convert data to DataFrame if needed
            if isinstance(data, dict):
                data = pd.DataFrame([data])
            
            # Make prediction
            prediction = model.predict(data)
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error making prediction: {e}")
            raise
    
    async def get_data_statistics(self) -> Dict[str, Any]:
        """Get data service statistics"""
        try:
            total_datasets = len(self.datasets)
            total_models = len(self.models)
            trained_models = len(self.trained_models)
            total_jobs = len(self.processing_jobs)
            
            # Job statistics
            completed_jobs = len([j for j in self.processing_jobs.values() if j.status == ProcessingStatus.COMPLETED])
            failed_jobs = len([j for j in self.processing_jobs.values() if j.status == ProcessingStatus.FAILED])
            
            return {
                "total_datasets": total_datasets,
                "total_models": total_models,
                "trained_models": trained_models,
                "total_jobs": total_jobs,
                "completed_jobs": completed_jobs,
                "failed_jobs": failed_jobs,
                "success_rate": (completed_jobs / (completed_jobs + failed_jobs) * 100) if (completed_jobs + failed_jobs) > 0 else 0,
                "storage_used": sum(d.size for d in self.datasets.values())
            }
            
        except Exception as e:
            logger.error(f"Error getting data statistics: {e}")
            return {}
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for data service"""
        try:
            stats = await self.get_data_statistics()
            
            return {
                "status": "healthy",
                "total_datasets": stats.get("total_datasets", 0),
                "total_models": stats.get("total_models", 0),
                "trained_models": stats.get("trained_models", 0),
                "database_connected": Path(self.db_path).exists(),
                "storage_available": True
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}


























