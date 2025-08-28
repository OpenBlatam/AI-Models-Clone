#!/usr/bin/env python3
"""
Deep Learning Architectures System
=================================

Object-oriented model architectures with functional data processing pipelines.
Implements best practices for clarity, efficiency, and maintainability.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torch.cuda.amp import GradScaler, autocast
import torch.optim as optim
from torch.optim.lr_scheduler import CosineAnnealingLR, ReduceLROnPlateau
from transformers import (
    AutoTokenizer, AutoModel, AutoModelForSequenceClassification,
    TrainingArguments, Trainer, pipeline
)
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import logging
import warnings
from functools import partial, reduce
from pathlib import Path
import json
import yaml
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore")

# =============================================================================
# OBJECT-ORIENTED MODEL ARCHITECTURES
# =============================================================================

class ModelType(Enum):
    """Supported model types"""
    TRANSFORMER = "transformer"
    CNN = "cnn"
    RNN = "rnn"
    LSTM = "lstm"
    GRU = "gru"
    HYBRID = "hybrid"
    CUSTOM = "custom"

class TaskType(Enum):
    """Supported task types"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    SEQUENCE_CLASSIFICATION = "sequence_classification"
    TOKEN_CLASSIFICATION = "token_classification"
    QUESTION_ANSWERING = "question_answering"
    TEXT_GENERATION = "text_generation"
    MULTI_TASK = "multi_task"

@dataclass
class ModelConfig:
    """Configuration for model architectures"""
    model_type: ModelType
    task_type: TaskType
    model_name: str = "distilbert-base-uncased"
    num_classes: int = 2
    hidden_size: int = 768
    num_layers: int = 6
    num_heads: int = 8
    dropout_rate: float = 0.1
    learning_rate: float = 2e-5
    batch_size: int = 16
    max_length: int = 512
    num_epochs: int = 10
    warmup_steps: int = 100
    weight_decay: float = 0.01
    gradient_clip_val: float = 1.0
    
    # Advanced settings
    use_mixed_precision: bool = True
    use_gradient_accumulation: bool = True
    gradient_accumulation_steps: int = 4
    use_early_stopping: bool = True
    early_stopping_patience: int = 5
    use_lr_scheduling: bool = True
    scheduler_type: str = "cosine"
    
    # Multi-GPU settings
    use_distributed_training: bool = False
    num_gpus: int = 1
    distributed_backend: str = "nccl"

class BaseModel(ABC, nn.Module):
    """Abstract base class for all model architectures"""
    
    def __init__(self, config: ModelConfig):
        super().__init__()
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.scaler = GradScaler() if config.use_mixed_precision else None
        
        # Training state
        self.optimizer = None
        self.scheduler = None
        self.best_val_loss = float('inf')
        self.patience_counter = 0
        
        logger.info(f"Initialized {self.__class__.__name__} on {self.device}")
    
    @abstractmethod
    def forward(self, **kwargs) -> torch.Tensor:
        """Forward pass through the model"""
        pass
    
    def create_optimizer(self) -> optim.Optimizer:
        """Create optimizer with weight decay"""
        no_decay = ['bias', 'LayerNorm.weight']
        optimizer_grouped_parameters = [
            {
                'params': [p for n, p in self.named_parameters() 
                          if not any(nd in n for nd in no_decay)],
                'weight_decay': self.config.weight_decay,
            },
            {
                'params': [p for n, p in self.named_parameters() 
                          if any(nd in n for nd in no_decay)],
                'weight_decay': 0.0,
            }
        ]
        return optim.AdamW(optimizer_grouped_parameters, lr=self.config.learning_rate)
    
    def create_scheduler(self, optimizer: optim.Optimizer) -> optim.lr_scheduler._LRScheduler:
        """Create learning rate scheduler"""
        if self.config.scheduler_type == "cosine":
            return CosineAnnealingLR(optimizer, T_max=self.config.num_epochs)
        elif self.config.scheduler_type == "plateau":
            return ReduceLROnPlateau(optimizer, mode='min', patience=3, factor=0.5)
        else:
            return optim.lr_scheduler.LinearLR(optimizer, start_factor=1.0, end_factor=0.1)
    
    def save_model(self, path: str):
        """Save model checkpoint"""
        checkpoint = {
            'model_state_dict': self.state_dict(),
            'config': self.config,
            'optimizer_state_dict': self.optimizer.state_dict() if self.optimizer else None,
            'scheduler_state_dict': self.scheduler.state_dict() if self.scheduler else None,
            'best_val_loss': self.best_val_loss,
            'timestamp': datetime.now().isoformat()
        }
        torch.save(checkpoint, path)
        logger.info(f"Model saved to {path}")
    
    def load_model(self, path: str):
        """Load model checkpoint"""
        checkpoint = torch.load(path, map_location=self.device)
        self.load_state_dict(checkpoint['model_state_dict'])
        if checkpoint['optimizer_state_dict'] and self.optimizer:
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        if checkpoint['scheduler_state_dict'] and self.scheduler:
            self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        self.best_val_loss = checkpoint.get('best_val_loss', float('inf'))
        logger.info(f"Model loaded from {path}")

class TransformerModel(BaseModel):
    """Transformer-based model architecture"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        
        # Load pre-trained transformer
        self.transformer = AutoModel.from_pretrained(config.model_name)
        
        # Task-specific head
        if config.task_type == TaskType.SEQUENCE_CLASSIFICATION:
            self.classifier = nn.Linear(config.hidden_size, config.num_classes)
        elif config.task_type == TaskType.REGRESSION:
            self.regressor = nn.Linear(config.hidden_size, 1)
        elif config.task_type == TaskType.MULTI_TASK:
            self.classifier = nn.Linear(config.hidden_size, config.num_classes)
            self.regressor = nn.Linear(config.hidden_size, 1)
        
        # Dropout for regularization
        self.dropout = nn.Dropout(config.dropout_rate)
        
        # Initialize weights
        self._init_weights()
    
    def _init_weights(self):
        """Initialize model weights"""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
    
    def forward(self, input_ids, attention_mask=None, labels=None):
        """Forward pass"""
        # Get transformer outputs
        outputs = self.transformer(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        
        # Get pooled output
        pooled_output = outputs.pooler_output
        pooled_output = self.dropout(pooled_output)
        
        # Task-specific forward pass
        if self.config.task_type == TaskType.SEQUENCE_CLASSIFICATION:
            logits = self.classifier(pooled_output)
            if labels is not None:
                loss = F.cross_entropy(logits, labels)
                return {'loss': loss, 'logits': logits}
            return {'logits': logits}
        
        elif self.config.task_type == TaskType.REGRESSION:
            predictions = self.regressor(pooled_output).squeeze(-1)
            if labels is not None:
                loss = F.mse_loss(predictions, labels)
                return {'loss': loss, 'predictions': predictions}
            return {'predictions': predictions}
        
        elif self.config.task_type == TaskType.MULTI_TASK:
            classification_logits = self.classifier(pooled_output)
            regression_predictions = self.regressor(pooled_output).squeeze(-1)
            
            if labels is not None:
                # Assuming labels is a dict with 'classification' and 'regression' keys
                classification_loss = F.cross_entropy(classification_logits, labels['classification'])
                regression_loss = F.mse_loss(regression_predictions, labels['regression'])
                total_loss = classification_loss + regression_loss
                
                return {
                    'loss': total_loss,
                    'classification_logits': classification_logits,
                    'regression_predictions': regression_predictions
                }
            
            return {
                'classification_logits': classification_logits,
                'regression_predictions': regression_predictions
            }

class CNNLSTMModel(BaseModel):
    """CNN-LSTM hybrid model for sequence processing"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        
        # CNN layers for feature extraction
        self.conv_layers = nn.ModuleList([
            nn.Conv1d(config.hidden_size, 128, kernel_size=3, padding=1),
            nn.Conv1d(128, 256, kernel_size=3, padding=1),
            nn.Conv1d(256, 512, kernel_size=3, padding=1)
        ])
        
        # LSTM layer
        self.lstm = nn.LSTM(
            input_size=512,
            hidden_size=config.hidden_size,
            num_layers=config.num_layers,
            dropout=config.dropout_rate if config.num_layers > 1 else 0,
            bidirectional=True,
            batch_first=True
        )
        
        # Attention mechanism
        self.attention = nn.MultiheadAttention(
            embed_dim=config.hidden_size * 2,  # Bidirectional
            num_heads=config.num_heads,
            dropout=config.dropout_rate,
            batch_first=True
        )
        
        # Output layers
        if config.task_type == TaskType.SEQUENCE_CLASSIFICATION:
            self.classifier = nn.Linear(config.hidden_size * 2, config.num_classes)
        elif config.task_type == TaskType.REGRESSION:
            self.regressor = nn.Linear(config.hidden_size * 2, 1)
        
        self.dropout = nn.Dropout(config.dropout_rate)
        self._init_weights()
    
    def _init_weights(self):
        """Initialize model weights"""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
    
    def forward(self, input_ids, attention_mask=None, labels=None):
        """Forward pass"""
        batch_size, seq_len = input_ids.shape
        
        # Embedding layer (assuming input_ids are already embedded)
        embedded = input_ids.float()  # Convert to float for CNN
        
        # CNN feature extraction
        x = embedded.transpose(1, 2)  # (batch, hidden_size, seq_len)
        for conv in self.conv_layers:
            x = F.relu(conv(x))
            x = F.max_pool1d(x, kernel_size=2, stride=1, padding=1)
        
        # Prepare for LSTM
        x = x.transpose(1, 2)  # (batch, seq_len, features)
        
        # LSTM processing
        lstm_out, (hidden, cell) = self.lstm(x)
        
        # Attention mechanism
        attn_out, attn_weights = self.attention(lstm_out, lstm_out, lstm_out)
        
        # Global average pooling
        pooled = torch.mean(attn_out, dim=1)
        pooled = self.dropout(pooled)
        
        # Task-specific output
        if self.config.task_type == TaskType.SEQUENCE_CLASSIFICATION:
            logits = self.classifier(pooled)
            if labels is not None:
                loss = F.cross_entropy(logits, labels)
                return {'loss': loss, 'logits': logits}
            return {'logits': logits}
        
        elif self.config.task_type == TaskType.REGRESSION:
            predictions = self.regressor(pooled).squeeze(-1)
            if labels is not None:
                loss = F.mse_loss(predictions, labels)
                return {'loss': loss, 'predictions': predictions}
            return {'predictions': predictions}

class ModelFactory:
    """Factory for creating model architectures"""
    
    @staticmethod
    def create_model(config: ModelConfig) -> BaseModel:
        """Create model based on configuration"""
        if config.model_type == ModelType.TRANSFORMER:
            return TransformerModel(config)
        elif config.model_type == ModelType.HYBRID:
            return CNNLSTMModel(config)
        else:
            raise ValueError(f"Unsupported model type: {config.model_type}")

# =============================================================================
# FUNCTIONAL DATA PROCESSING PIPELINES
# =============================================================================

@dataclass
class DataPoint:
    """Single data point with text and optional labels"""
    text: str
    labels: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ProcessedData:
    """Processed data point ready for model input"""
    input_ids: torch.Tensor
    attention_mask: torch.Tensor
    labels: Optional[torch.Tensor] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ProcessingConfig:
    """Configuration for data processing"""
    tokenizer_name: str = "distilbert-base-uncased"
    max_length: int = 512
    truncation: bool = True
    padding: str = "max_length"
    return_tensors: str = "pt"
    text_column: str = "text"
    label_columns: List[str] = field(default_factory=list)
    task_type: TaskType = TaskType.SEQUENCE_CLASSIFICATION

# Functional data transformations
def load_tokenizer(config: ProcessingConfig):
    """Load tokenizer - pure function"""
    return AutoTokenizer.from_pretrained(config.tokenizer_name)

def tokenize_text(text: str, tokenizer, config: ProcessingConfig) -> Dict[str, torch.Tensor]:
    """Tokenize single text - pure function"""
    return tokenizer(
        text,
        max_length=config.max_length,
        truncation=config.truncation,
        padding=config.padding,
        return_tensors=config.return_tensors
    )

def process_labels(labels: Dict[str, Any], config: ProcessingConfig) -> torch.Tensor:
    """Process labels - pure function"""
    if config.task_type == TaskType.SEQUENCE_CLASSIFICATION:
        return torch.tensor(labels.get('classification', 0), dtype=torch.long)
    elif config.task_type == TaskType.REGRESSION:
        return torch.tensor(labels.get('regression', 0.0), dtype=torch.float)
    elif config.task_type == TaskType.MULTI_TASK:
        return {
            'classification': torch.tensor(labels.get('classification', 0), dtype=torch.long),
            'regression': torch.tensor(labels.get('regression', 0.0), dtype=torch.float)
        }
    return None

def process_data_point(data_point: DataPoint, tokenizer, config: ProcessingConfig) -> ProcessedData:
    """Process single data point - pure function"""
    # Tokenize text
    tokenized = tokenize_text(data_point.text, tokenizer, config)
    
    # Process labels
    labels = None
    if data_point.labels:
        labels = process_labels(data_point.labels, config)
    
    return ProcessedData(
        input_ids=tokenized['input_ids'].squeeze(0),
        attention_mask=tokenized['attention_mask'].squeeze(0),
        labels=labels,
        metadata=data_point.metadata
    )

def load_data_from_file(file_path: str, config: ProcessingConfig) -> List[DataPoint]:
    """Load data from file - pure function"""
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
        return [
            DataPoint(
                text=row[config.text_column],
                labels={col: row[col] for col in config.label_columns if col in row},
                metadata=row.to_dict()
            )
            for _, row in df.iterrows()
        ]
    elif file_path.endswith('.json'):
        with open(file_path, 'r') as f:
            data = json.load(f)
        return [DataPoint(**item) for item in data]
    else:
        raise ValueError(f"Unsupported file format: {file_path}")

def split_data(data: List[ProcessedData], train_ratio: float = 0.8, val_ratio: float = 0.1) -> Tuple[List[ProcessedData], List[ProcessedData], List[ProcessedData]]:
    """Split data into train/val/test sets - pure function"""
    total_size = len(data)
    train_size = int(total_size * train_ratio)
    val_size = int(total_size * val_ratio)
    
    train_data = data[:train_size]
    val_data = data[train_size:train_size + val_size]
    test_data = data[train_size + val_size:]
    
    return train_data, val_data, test_data

def create_data_loader(data: List[ProcessedData], batch_size: int, shuffle: bool = True) -> DataLoader:
    """Create DataLoader - pure function"""
    return DataLoader(data, batch_size=batch_size, shuffle=shuffle)

# Functional composition utilities
def compose(*functions):
    """Compose multiple functions - functional utility"""
    def inner(arg):
        return reduce(lambda acc, f: f(acc), reversed(functions), arg)
    return inner

def pipe(data, *functions):
    """Pipe data through functions - functional utility"""
    return compose(*functions)(data)

# =============================================================================
# INTEGRATED TRAINING SYSTEM
# =============================================================================

class FunctionalDataset(Dataset):
    """Functional dataset implementation"""
    
    def __init__(self, data: List[ProcessedData]):
        self.data = data
    
    def __len__(self) -> int:
        return len(self.data)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        item = self.data[idx]
        result = {
            'input_ids': item.input_ids,
            'attention_mask': item.attention_mask
        }
        if item.labels is not None:
            result['labels'] = item.labels
        return result

class ModelTrainer:
    """Integrated trainer combining OOP models with functional data processing"""
    
    def __init__(self, model: BaseModel, config: ModelConfig):
        self.model = model
        self.config = config
        self.device = model.device
        
        # Initialize training components
        self.optimizer = model.create_optimizer()
        self.scheduler = model.create_scheduler(self.optimizer)
        
        # Move model to device
        self.model.to(self.device)
        
        # Training metrics
        self.train_losses = []
        self.val_losses = []
        self.train_accuracies = []
        self.val_accuracies = []
        
        logger.info(f"Trainer initialized for {model.__class__.__name__}")
    
    def train_epoch(self, train_loader: DataLoader) -> Dict[str, float]:
        """Train for one epoch"""
        self.model.train()
        total_loss = 0
        correct_predictions = 0
        total_predictions = 0
        
        for batch_idx, batch in enumerate(train_loader):
            # Move batch to device
            batch = {k: v.to(self.device) for k, v in batch.items()}
            
            # Forward pass with mixed precision
            if self.config.use_mixed_precision:
                with autocast():
                    outputs = self.model(**batch)
                    loss = outputs['loss']
                
                # Backward pass with gradient scaling
                self.optimizer.zero_grad()
                self.model.scaler.scale(loss).backward()
                
                if self.config.gradient_clip_val > 0:
                    self.model.scaler.unscale_(self.optimizer)
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.config.gradient_clip_val)
                
                self.model.scaler.step(self.optimizer)
                self.model.scaler.update()
            else:
                outputs = self.model(**batch)
                loss = outputs['loss']
                
                self.optimizer.zero_grad()
                loss.backward()
                
                if self.config.gradient_clip_val > 0:
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.config.gradient_clip_val)
                
                self.optimizer.step()
            
            # Update metrics
            total_loss += loss.item()
            
            # Calculate accuracy for classification tasks
            if self.config.task_type == TaskType.SEQUENCE_CLASSIFICATION:
                logits = outputs['logits']
                predictions = torch.argmax(logits, dim=-1)
                correct_predictions += (predictions == batch['labels']).sum().item()
                total_predictions += batch['labels'].size(0)
            
            # Gradient accumulation
            if self.config.use_gradient_accumulation and (batch_idx + 1) % self.config.gradient_accumulation_steps == 0:
                self.optimizer.step()
                self.optimizer.zero_grad()
        
        # Calculate epoch metrics
        avg_loss = total_loss / len(train_loader)
        accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
        
        return {'loss': avg_loss, 'accuracy': accuracy}
    
    def validate_epoch(self, val_loader: DataLoader) -> Dict[str, float]:
        """Validate for one epoch"""
        self.model.eval()
        total_loss = 0
        correct_predictions = 0
        total_predictions = 0
        
        with torch.no_grad():
            for batch in val_loader:
                batch = {k: v.to(self.device) for k, v in batch.items()}
                
                if self.config.use_mixed_precision:
                    with autocast():
                        outputs = self.model(**batch)
                        loss = outputs['loss']
                else:
                    outputs = self.model(**batch)
                    loss = outputs['loss']
                
                total_loss += loss.item()
                
                if self.config.task_type == TaskType.SEQUENCE_CLASSIFICATION:
                    logits = outputs['logits']
                    predictions = torch.argmax(logits, dim=-1)
                    correct_predictions += (predictions == batch['labels']).sum().item()
                    total_predictions += batch['labels'].size(0)
        
        avg_loss = total_loss / len(val_loader)
        accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
        
        return {'loss': avg_loss, 'accuracy': accuracy}
    
    def train(self, train_loader: DataLoader, val_loader: DataLoader):
        """Complete training loop"""
        logger.info("Starting training...")
        
        for epoch in range(self.config.num_epochs):
            # Training
            train_metrics = self.train_epoch(train_loader)
            self.train_losses.append(train_metrics['loss'])
            self.train_accuracies.append(train_metrics['accuracy'])
            
            # Validation
            val_metrics = self.validate_epoch(val_loader)
            self.val_losses.append(val_metrics['loss'])
            self.val_accuracies.append(val_metrics['accuracy'])
            
            # Learning rate scheduling
            if self.config.use_lr_scheduling:
                if isinstance(self.scheduler, ReduceLROnPlateau):
                    self.scheduler.step(val_metrics['loss'])
                else:
                    self.scheduler.step()
            
            # Early stopping
            if self.config.use_early_stopping:
                if val_metrics['loss'] < self.model.best_val_loss:
                    self.model.best_val_loss = val_metrics['loss']
                    self.model.patience_counter = 0
                    # Save best model
                    self.model.save_model(f"best_model_epoch_{epoch}.pt")
                else:
                    self.model.patience_counter += 1
                    if self.model.patience_counter >= self.config.early_stopping_patience:
                        logger.info(f"Early stopping triggered at epoch {epoch}")
                        break
            
            # Log progress
            logger.info(
                f"Epoch {epoch+1}/{self.config.num_epochs} - "
                f"Train Loss: {train_metrics['loss']:.4f}, "
                f"Train Acc: {train_metrics['accuracy']:.4f}, "
                f"Val Loss: {val_metrics['loss']:.4f}, "
                f"Val Acc: {val_metrics['accuracy']:.4f}"
            )
        
        logger.info("Training completed!")

# =============================================================================
# USAGE EXAMPLE
# =============================================================================

def create_training_pipeline(config: ModelConfig, data_config: ProcessingConfig):
    """Create complete training pipeline - functional approach"""
    
    # Load and process data
    raw_data = load_data_from_file("data.csv", data_config)
    tokenizer = load_tokenizer(data_config)
    
    # Process data points
    processed_data = [
        process_data_point(dp, tokenizer, data_config) 
        for dp in raw_data
    ]
    
    # Split data
    train_data, val_data, test_data = split_data(processed_data)
    
    # Create datasets and loaders
    train_dataset = FunctionalDataset(train_data)
    val_dataset = FunctionalDataset(val_data)
    
    train_loader = create_data_loader(train_dataset, config.batch_size, shuffle=True)
    val_loader = create_data_loader(val_dataset, config.batch_size, shuffle=False)
    
    # Create model
    model = ModelFactory.create_model(config)
    
    # Create trainer
    trainer = ModelTrainer(model, config)
    
    return trainer, train_loader, val_loader

if __name__ == "__main__":
    # Example usage
    model_config = ModelConfig(
        model_type=ModelType.TRANSFORMER,
        task_type=TaskType.SEQUENCE_CLASSIFICATION,
        num_classes=3,
        learning_rate=2e-5,
        batch_size=16,
        num_epochs=5
    )
    
    data_config = ProcessingConfig(
        tokenizer_name="distilbert-base-uncased",
        max_length=512,
        task_type=TaskType.SEQUENCE_CLASSIFICATION,
        label_columns=["label"]
    )
    
    # Create and run training pipeline
    trainer, train_loader, val_loader = create_training_pipeline(model_config, data_config)
    trainer.train(train_loader, val_loader)
