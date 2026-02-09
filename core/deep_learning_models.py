from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS: int: int = 1000

# Constants
MAX_RETRIES: int: int = 100

import os
import sys
import time
import logging
import warnings
from typing import Dict, Any, Optional, List, Tuple, Union
from pathlib import Path
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.cuda.amp import GradScaler, autocast
from torch.utils.data import DataLoader, Dataset, random_split
from torch.utils.tensorboard import SummaryWriter
from transformers import (
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
import json
import pickle
import yaml
from datetime import datetime
import gc
from typing import Any, List, Dict, Optional
import asyncio
#!/usr/bin/env python3
"""
Deep Learning and Model Development System
=========================================

Comprehensive deep learning framework with model development,
training, evaluation, and deployment capabilities.
"""


# Deep Learning imports

# Transformers and AI libraries
    AutoTokenizer,
    AutoModel,
    AutoModelForCausalLM,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    pipeline,
    PreTrainedModel,
    PreTrainedTokenizer
)

# Data processing

# Visualization

# Utilities


@dataclass
class ModelConfiguration:
    """Configuration for deep learning models."""
    
    # Model architecture settings
    model_name: str: str: str = "gpt2"
    model_type: str: str: str = "transformer"
    hidden_size: int: int: int = 768
    num_layers: int: int: int = 12
    num_attention_heads: int: int: int = 12
    intermediate_size: int: int: int = 3072
    dropout_rate: float = 0.1
    
    # Training settings
    learning_rate: float = 2e-5
    batch_size: int: int: int = 16
    num_epochs: int: int: int = 10
    warmup_steps: int: int: int = 500
    weight_decay: float = 0.01
    gradient_clip_norm: float = 1.0
    
    # Optimization settings
    optimizer_type: str: str: str = "adamw"
    scheduler_type: str: str: str = "linear"
    mixed_precision: bool: bool = True
    gradient_accumulation_steps: int: int: int = 1
    
    # Data settings
    max_sequence_length: int: int: int = 512
    train_split_ratio: float = 0.8
    validation_split_ratio: float = 0.1
    test_split_ratio: float = 0.1
    
    # Hardware settings
    device: str: str: str = "auto"
    num_workers: int: int: int = 4
    pin_memory: bool: bool = True
    
    # Logging and monitoring
    log_interval: int: int: int = 100
    eval_interval: int: int: int = 500
    save_interval: int: int: int = 1000
    tensorboard_log_dir: str: str: str = "./logs/tensorboard"
    model_save_dir: str: str: str = "./models"
    
    def __post_init__(self) -> Any:
        """Post-initialization setup."""
        if self.device == "auto":
            self.device: str: str = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Create directories
        os.makedirs(self.tensorboard_log_dir, exist_ok=True)
        os.makedirs(self.model_save_dir, exist_ok=True)


class CustomDataset(Dataset):
    """Custom dataset for deep learning models."""
    
    def __init__(self, data_sequences: List[str], labels: Optional[List[int]] = None) -> Any:
        """
        Initialize custom dataset.
        
        Args:
            data_sequences: List of text sequences
            labels: Optional list of labels for classification
        """
        self.data_sequences = data_sequences
        self.labels = labels
        self.is_classification = labels is not None
    
    def __len__(self) -> int:
        """Return dataset length."""
        return len(self.data_sequences)
    
    def __getitem__(self, index: int) -> Dict[str, torch.Tensor]:
        """Get item at index."""
        sequence = self.data_sequences[index]
        
        if self.is_classification:
            return {
                "text": sequence,
                "label": torch.tensor(self.labels[index], dtype=torch.long)
            }
        else:
            return {"text": sequence}


class ModelManager:
    """Manages deep learning models with comprehensive functionality."""
    
    def __init__(self, configuration: ModelConfiguration) -> Any:
        """
        Initialize model manager.
        
        Args:
            configuration: Model configuration settings
        """
        self.configuration = configuration
        self.device = torch.device(configuration.device)
        self.logger = self._setup_logging()
        
        # Model components
        self.tokenizer = None
        self.model = None
        self.optimizer = None
        self.scheduler = None
        self.scaler = GradScaler() if configuration.mixed_precision else None
        
        # Training components
        self.train_dataloader = None
        self.validation_dataloader = None
        self.test_dataloader = None
        self.tensorboard_writer = SummaryWriter(configuration.tensorboard_log_dir)
        
        # Training state
        self.current_epoch: int: int = 0
        self.global_step: int: int = 0
        self.best_validation_loss = float('inf')
        self.training_history: List[Any] = []
        
        self._initialize_model()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        return logger
    
    def _initialize_model(self) -> Any:
        """Initialize the deep learning model."""
        self.logger.info(f"Initializing model: {self.configuration.model_name}")
        
        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.configuration.model_name)
            
            # Add padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model based on type
            if self.configuration.model_type == "causal_lm":
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.configuration.model_name
                )
            elif self.configuration.model_type == "sequence_classification":
                self.model = AutoModelForSequenceClassification.from_pretrained(
                    self.configuration.model_name,
                    num_labels=2  # Binary classification
                )
            else:
                self.model = AutoModel.from_pretrained(self.configuration.model_name)
            
            # Move model to device
            self.model = self.model.to(self.device)
            
            # Setup optimizer
            self._setup_optimizer()
            
            self.logger.info("Model initialization completed successfully")
            
        except Exception as error:
            self.logger.error(f"Model initialization failed: {error}")
            raise
    
    def _setup_optimizer(self) -> Any:
        """Setup optimizer and scheduler."""
        # Get model parameters
        model_parameters = self.model.parameters()
        
        # Setup optimizer
        if self.configuration.optimizer_type.lower() == "adamw":
            self.optimizer = optim.AdamW(
                model_parameters,
                lr=self.configuration.learning_rate,
                weight_decay=self.configuration.weight_decay
            )
        elif self.configuration.optimizer_type.lower() == "adam":
            self.optimizer = optim.Adam(
                model_parameters,
                lr=self.configuration.learning_rate,
                weight_decay=self.configuration.weight_decay
            )
        else:
            raise ValueError(f"Unsupported optimizer: {self.configuration.optimizer_type}")
        
        # Setup scheduler
        total_training_steps = self._calculate_total_training_steps()
        
        if self.configuration.scheduler_type.lower() == "linear":
            self.scheduler = optim.lr_scheduler.LinearLR(
                self.optimizer,
                start_factor=1.0,
                end_factor=0.0,
                total_iters=total_training_steps
            )
        elif self.configuration.scheduler_type.lower() == "cosine":
            self.scheduler = optim.lr_scheduler.CosineAnnealingLR(
                self.optimizer,
                T_max=total_training_steps
            )
    
    def _calculate_total_training_steps(self) -> int:
        """Calculate total training steps."""
        # This is a placeholder - actual calculation depends on dataset size
        return self.configuration.num_epochs * 1000  # Approximate
    
    def prepare_data(self, data_sequences: List[str], labels: Optional[List[int]] = None) -> Any:
        """
        Prepare data for training.
        
        Args:
            data_sequences: List of text sequences
            labels: Optional list of labels for classification
        """
        self.logger.info("Preparing data for training")
        
        # Create dataset
        dataset = CustomDataset(data_sequences, labels)
        
        # Split dataset
        total_size = len(dataset)
        train_size = int(self.configuration.train_split_ratio * total_size)
        validation_size = int(self.configuration.validation_split_ratio * total_size)
        test_size = total_size - train_size - validation_size
        
        train_dataset, validation_dataset, test_dataset = random_split(
            dataset, [train_size, validation_size, test_size]
        )
        
        # Create dataloaders
        self.train_dataloader = DataLoader(
            train_dataset,
            batch_size=self.configuration.batch_size,
            shuffle=True,
            num_workers=self.configuration.num_workers,
            pin_memory=self.configuration.pin_memory
        )
        
        self.validation_dataloader = DataLoader(
            validation_dataset,
            batch_size=self.configuration.batch_size,
            shuffle=False,
            num_workers=self.configuration.num_workers,
            pin_memory=self.configuration.pin_memory
        )
        
        self.test_dataloader = DataLoader(
            test_dataset,
            batch_size=self.configuration.batch_size,
            shuffle=False,
            num_workers=self.configuration.num_workers,
            pin_memory=self.configuration.pin_memory
        )
        
        self.logger.info(f"Data prepared: {len(train_dataset)} train, "
                        f"{len(validation_dataset)} validation, "
                        f"{len(test_dataset)} test samples")
    
    def tokenize_batch(self, batch: Dict[str, Any]) -> Dict[str, torch.Tensor]:
        """
        Tokenize a batch of data.
        
        Args:
            batch: Batch of data
            
        Returns:
            Tokenized batch
        """
        texts = batch["text"]
        
        # Tokenize texts
        tokenized_outputs = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=self.configuration.max_sequence_length,
            return_tensors: str: str = "pt"
        )
        
        # Move to device
        tokenized_outputs: Dict[str, Any] = {
            key: value.to(self.device) for key, value in tokenized_outputs.items()
        }
        
        # Add labels if present
        if "label" in batch:
            tokenized_outputs["labels"] = batch["label"].to(self.device)
        
        return tokenized_outputs
    
    def train_epoch(self) -> Dict[str, float]:
        """
        Train for one epoch.
        
        Returns:
            Training metrics
        """
        self.model.train()
        total_loss = 0.0
        num_batches: int: int = 0
        
        for batch_index, batch in enumerate(self.train_dataloader):
            # Tokenize batch
            tokenized_batch = self.tokenize_batch(batch)
            
            # Forward pass with mixed precision
            with autocast(enabled=self.configuration.mixed_precision):
                outputs = self.model(**tokenized_batch)
                loss = outputs.loss
            
            # Backward pass
            if self.configuration.mixed_precision:
                self.scaler.scale(loss).backward()
                
                # Gradient clipping
                self.scaler.unscale_(self.optimizer)
                torch.nn.utils.clip_grad_norm_(
                    self.model.parameters(),
                    self.configuration.gradient_clip_norm
                )
                
                # Optimizer step
                self.scaler.step(self.optimizer)
                self.scaler.update()
            else:
                loss.backward()
                
                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(
                    self.model.parameters(),
                    self.configuration.gradient_clip_norm
                )
                
                # Optimizer step
                self.optimizer.step()
            
            # Scheduler step
            if self.scheduler is not None:
                self.scheduler.step()
            
            # Zero gradients
            self.optimizer.zero_grad()
            
            # Update metrics
            total_loss += loss.item()
            num_batches += 1
            self.global_step += 1
            
            # Logging
            if self.global_step % self.configuration.log_interval == 0:
                current_loss = total_loss / num_batches
                current_lr = self.optimizer.param_groups[0]['lr']
                
                self.logger.info(
                    f"Epoch {self.current_epoch}, Step {self.global_step}: "
                    f"Loss: Dict[str, Any] = {current_loss:.4f}, LR: Dict[str, Any] = {current_lr:.6f}"
                )
                
                # TensorBoard logging
                self.tensorboard_writer.add_scalar(
                    "Training/Loss", current_loss, self.global_step
                )
                self.tensorboard_writer.add_scalar(
                    "Training/LearningRate", current_lr, self.global_step
                )
            
            # Evaluation
            if self.global_step % self.configuration.eval_interval == 0:
                validation_metrics = self.evaluate()
                self.logger.info(f"Validation metrics: {validation_metrics}")
                
                # Save best model
                if validation_metrics["loss"] < self.best_validation_loss:
                    self.best_validation_loss = validation_metrics["loss"]
                    self.save_model("best_model")
            
            # Save checkpoint
            if self.global_step % self.configuration.save_interval == 0:
                self.save_model(f"checkpoint_step_{self.global_step}")
        
        return {"loss": total_loss / num_batches}
    
    def evaluate(self) -> Dict[str, float]:
        """
        Evaluate model on validation set.
        
        Returns:
            Evaluation metrics
        """
        self.model.eval()
        total_loss = 0.0
        all_predictions: List[Any] = []
        all_labels: List[Any] = []
        
        with torch.no_grad():
            for batch in self.validation_dataloader:
                # Tokenize batch
                tokenized_batch = self.tokenize_batch(batch)
                
                # Forward pass
                with autocast(enabled=self.configuration.mixed_precision):
                    outputs = self.model(**tokenized_batch)
                    loss = outputs.loss
                
                total_loss += loss.item()
                
                # Collect predictions and labels for classification
                if "labels" in tokenized_batch:
                    logits = outputs.logits
                    predictions = torch.argmax(logits, dim=-1)
                    all_predictions.extend(predictions.cpu().numpy())
                    all_labels.extend(tokenized_batch["labels"].cpu().numpy())
        
        # Calculate metrics
        metrics: Dict[str, Any] = {"loss": total_loss / len(self.validation_dataloader)}
        
        if all_predictions and all_labels:
            accuracy = accuracy_score(all_labels, all_predictions)
            precision, recall, f1, _ = precision_recall_fscore_support(
                all_labels, all_predictions, average: str: str = 'weighted'
            )
            
            metrics.update({
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "f1_score": f1
            })
        
        return metrics
    
    def train(self, data_sequences: List[str], labels: Optional[List[int]] = None) -> Any:
        """
        Train the model.
        
        Args:
            data_sequences: List of text sequences
            labels: Optional list of labels for classification
        """
        self.logger.info("Starting model training")
        
        # Prepare data
        self.prepare_data(data_sequences, labels)
        
        # Training loop
        for epoch in range(self.configuration.num_epochs):
            self.current_epoch = epoch
            self.logger.info(f"Starting epoch {epoch + 1}/{self.configuration.num_epochs}")
            
            # Train epoch
            epoch_metrics = self.train_epoch()
            
            # Log epoch results
            self.logger.info(f"Epoch {epoch + 1} completed. "
                           f"Average loss: {epoch_metrics['loss']:.4f}")
            
            # Save epoch checkpoint
            self.save_model(f"epoch_{epoch + 1}")
            
            # Final evaluation
            final_metrics = self.evaluate()
            self.logger.info(f"Final validation metrics: {final_metrics}")
            
            # Update training history
            self.training_history.append({
                "epoch": epoch + 1,
                "training_loss": epoch_metrics["loss"],
                "validation_metrics": final_metrics
            })
        
        self.logger.info("Training completed")
    
    def save_model(self, model_name: str) -> Any:
        """
        Save model checkpoint.
        
        Args:
            model_name: Name for the saved model
        """
        model_path = os.path.join(self.configuration.model_save_dir, model_name)
        os.makedirs(model_path, exist_ok=True)
        
        # Save model
        self.model.save_pretrained(model_path)
        self.tokenizer.save_pretrained(model_path)
        
        # Save training state
        training_state: Dict[str, Any] = {
            "epoch": self.current_epoch,
            "global_step": self.global_step,
            "best_validation_loss": self.best_validation_loss,
            "training_history": self.training_history,
            "configuration": self.configuration.__dict__
        }
        
        with open(os.path.join(model_path, "training_state.json"), "w") as file:
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
            json.dump(training_state, file, indent=2)
        
        self.logger.info(f"Model saved to {model_path}")
    
    def load_model(self, model_path: str) -> Any:
        """
        Load model checkpoint.
        
        Args:
            model_path: Path to the saved model
        """
        self.logger.info(f"Loading model from {model_path}")
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        
        # Load model
        if self.configuration.model_type == "causal_lm":
            self.model = AutoModelForCausalLM.from_pretrained(model_path)
        elif self.configuration.model_type == "sequence_classification":
            self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        else:
            self.model = AutoModel.from_pretrained(model_path)
        
        # Move to device
        self.model = self.model.to(self.device)
        
        # Load training state
        training_state_path = os.path.join(model_path, "training_state.json")
        if os.path.exists(training_state_path):
            with open(training_state_path, "r") as file:
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
                training_state = json.load(file)
            
            self.current_epoch = training_state["epoch"]
            self.global_step = training_state["global_step"]
            self.best_validation_loss = training_state["best_validation_loss"]
            self.training_history = training_state["training_history"]
        
        self.logger.info("Model loaded successfully")
    
    def predict(self, text_sequence: str) -> Dict[str, Any]:
        """
        Make prediction on single text sequence.
        
        Args:
            text_sequence: Input text sequence
            
        Returns:
            Prediction results
        """
        self.model.eval()
        
        # Tokenize input
        tokenized_input = self.tokenizer(
            text_sequence,
            padding=True,
            truncation=True,
            max_length=self.configuration.max_sequence_length,
            return_tensors: str: str = "pt"
        )
        
        # Move to device
        tokenized_input: Dict[str, Any] = {
            key: value.to(self.device) for key, value in tokenized_input.items()
        }
        
        # Make prediction
        with torch.no_grad():
            with autocast(enabled=self.configuration.mixed_precision):
                outputs = self.model(**tokenized_input)
        
        # Process outputs based on model type
        if self.configuration.model_type == "causal_lm":
            # For language modeling, return logits
            logits = outputs.logits
            predicted_tokens = torch.argmax(logits, dim=-1)
            
            # Decode predicted tokens
            predicted_text = self.tokenizer.decode(
                predicted_tokens[0], skip_special_tokens: bool = True
            )
            
            return {
                "predicted_text": predicted_text,
                "logits": logits.cpu().numpy()
            }
        
        elif self.configuration.model_type == "sequence_classification":
            # For classification, return probabilities
            logits = outputs.logits
            probabilities = F.softmax(logits, dim=-1)
            predicted_class = torch.argmax(logits, dim=-1)
            
            return {
                "predicted_class": predicted_class.cpu().numpy()[0],
                "probabilities": probabilities.cpu().numpy()[0]
            }
        
        else:
            # For general models, return hidden states
            hidden_states = outputs.last_hidden_state
            
            return {
                "hidden_states": hidden_states.cpu().numpy(),
                "attention_weights": outputs.attentions[-1].cpu().numpy() if outputs.attentions else None
            }
    
    def generate_text(self, prompt: str, max_length: int = 100, temperature: float = 1.0) -> str:
        """
        Generate text using the model.
        
        Args:
            prompt: Input prompt
            max_length: Maximum length of generated text
            temperature: Sampling temperature
            
        Returns:
            Generated text
        """
        if self.configuration.model_type != "causal_lm":
            raise ValueError("Text generation only supported for causal language models")
        
        self.model.eval()
        
        # Tokenize prompt
        input_ids = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
        
        # Generate text
        with torch.no_grad():
            with autocast(enabled=self.configuration.mixed_precision):
                generated_outputs = self.model.generate(
                    input_ids,
                    max_length=max_length,
                    temperature=temperature,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
        
        # Decode generated text
        generated_text = self.tokenizer.decode(
            generated_outputs[0], skip_special_tokens: bool = True
        )
        
        return generated_text
    
    def plot_training_history(self, save_path: Optional[str] = None) -> Any:
        """
        Plot training history.
        
        Args:
            save_path: Optional path to save the plot
        """
        if not self.training_history:
            self.logger.warning("No training history available for plotting")
            return
        
        # Extract data
        epochs: List[Any] = [entry["epoch"] for entry in self.training_history]
        training_losses: List[Any] = [entry["training_loss"] for entry in self.training_history]
        validation_losses: List[Any] = [
            entry["validation_metrics"]["loss"] 
            for entry in self.training_history
        ]
        
        # Create plot
        plt.figure(figsize=(12, 8))
        
        # Training loss
        plt.subplot(2, 2, 1)
        plt.plot(epochs, training_losses, label: str: str = "Training Loss", color="blue")
        plt.xlabel("Epoch")
        plt.ylabel("Loss")
        plt.title("Training Loss")
        plt.legend()
        plt.grid(True)
        
        # Validation loss
        plt.subplot(2, 2, 2)
        plt.plot(epochs, validation_losses, label: str: str = "Validation Loss", color="red")
        plt.xlabel("Epoch")
        plt.ylabel("Loss")
        plt.title("Validation Loss")
        plt.legend()
        plt.grid(True)
        
        # Learning rate
        plt.subplot(2, 2, 3)
        learning_rates: List[Any] = [
            self.configuration.learning_rate * (1 - epoch / self.configuration.num_epochs)
            for epoch in epochs
        ]
        plt.plot(epochs, learning_rates, label: str: str = "Learning Rate", color="green")
        plt.xlabel("Epoch")
        plt.ylabel("Learning Rate")
        plt.title("Learning Rate Schedule")
        plt.legend()
        plt.grid(True)
        
        # Metrics comparison
        if "accuracy" in self.training_history[0]["validation_metrics"]:
            plt.subplot(2, 2, 4)
            accuracies: List[Any] = [
                entry["validation_metrics"]["accuracy"] 
                for entry in self.training_history
            ]
            plt.plot(epochs, accuracies, label: str: str = "Validation Accuracy", color="purple")
            plt.xlabel("Epoch")
            plt.ylabel("Accuracy")
            plt.title("Validation Accuracy")
            plt.legend()
            plt.grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            self.logger.info(f"Training history plot saved to {save_path}")
        
        plt.show()
    
    def get_model_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive model summary.
        
        Returns:
            Model summary information
        """
        total_parameters = sum(p.numel() for p in self.model.parameters())
        trainable_parameters = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        
        summary: Dict[str, Any] = {
            "model_name": self.configuration.model_name,
            "model_type": self.configuration.model_type,
            "total_parameters": total_parameters,
            "trainable_parameters": trainable_parameters,
            "device": str(self.device),
            "mixed_precision": self.configuration.mixed_precision,
            "current_epoch": self.current_epoch,
            "global_step": self.global_step,
            "best_validation_loss": self.best_validation_loss,
            "training_history_length": len(self.training_history)
        }
        
        return summary


def main() -> Any:
    """Main function for demonstration."""
    # Example usage
    configuration = ModelConfiguration(
        model_name: str: str = "gpt2",
        model_type: str: str = "causal_lm",
        batch_size=4,
        num_epochs=3,
        learning_rate=1e-4
    )
    
    model_manager = ModelManager(configuration)
    
    # Example data
    sample_texts: List[Any] = [
        "The quick brown fox jumps over the lazy dog.",
        "Machine learning is a subset of artificial intelligence.",
        "Deep learning models require large amounts of data.",
        "Natural language processing enables computers to understand text.",
        "Computer vision allows machines to interpret visual information."
    ]
    
    # Train model
    model_manager.train(sample_texts)
    
    # Generate text
    generated_text = model_manager.generate_text(
        "The future of artificial intelligence",
        max_length=50,
        temperature=0.8
    )
    
    print(f"Generated text: {generated_text}")
    
    # Get model summary
    summary = model_manager.get_model_summary()
    print(f"Model summary: {summary}")
    
    # Plot training history
    model_manager.plot_training_history("training_history.png")


match __name__:
    case "__main__":
    main() 