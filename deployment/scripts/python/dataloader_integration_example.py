#!/usr/bin/env python3
"""
DataLoader Integration Example for Blaze AI
Demonstrates integration of enhanced DataLoader utilities with the deep learning framework
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any
import logging
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

# Import our utilities
try:
    from .data_splitting_and_validation import DataSplitter, DataSplitConfig, CrossValidator
    from .enhanced_dataloader import EnhancedDataset, EnhancedDataLoaderFactory, DataLoaderConfig, DataLoaderOptimizer
except ImportError:
    from data_splitting_and_validation import DataSplitter, DataSplitConfig, CrossValidator
    from enhanced_dataloader import EnhancedDataset, EnhancedDataLoaderFactory, DataLoaderConfig, DataLoaderOptimizer

# Import existing framework components
try:
    from .gpu_optimization_and_mixed_precision import GPUOptimizedTrainer
    from .pytorch_utilities import PyTorchMemoryUtils
except ImportError:
    # Fallback imports for demonstration
    GPUOptimizedTrainer = None
    PyTorchMemoryUtils = None

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SimpleNeuralNetwork(nn.Module):
    """Simple neural network for demonstration"""
    
    def __init__(self, input_size: int, hidden_size: int, num_classes: int):
        super().__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.3)
        self.fc2 = nn.Linear(hidden_size, hidden_size // 2)
        self.fc3 = nn.Linear(hidden_size // 2, num_classes)
        
        # Initialize weights
        self.apply(self._init_weights)
    
    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            nn.init.xavier_uniform_(module.weight)
            if module.bias is not None:
                nn.init.constant_(module.bias, 0)
    
    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.fc2(x)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.fc3(x)
        return x


class IntegratedTrainer:
    """Trainer that integrates enhanced DataLoader with training loop"""
    
    def __init__(
        self,
        model: nn.Module,
        dataloader_config: DataLoaderConfig,
        learning_rate: float = 0.001,
        device: str = "auto"
    ):
        self.model = model
        self.dataloader_config = dataloader_config
        self.learning_rate = learning_rate
        
        # Auto-detect device
        if device == "auto":
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        
        # Move model to device
        self.model.to(self.device)
        
        # Setup optimizer and loss
        self.optimizer = optim.AdamW(model.parameters(), lr=learning_rate)
        self.criterion = nn.CrossEntropyLoss()
        
        # Training state
        self.train_losses = []
        self.val_losses = []
        self.train_accuracies = []
        self.val_accuracies = []
        
        # DataLoader factory
        self.dataloader_factory = EnhancedDataLoaderFactory(dataloader_config)
        
        logger.info(f"IntegratedTrainer initialized on device: {self.device}")
    
    def train_with_splits(
        self,
        enhanced_dataset: EnhancedDataset,
        num_epochs: int = 10,
        early_stopping_patience: int = 5
    ) -> Dict[str, List[float]]:
        """Train model using proper train/validation/test splits"""
        logger.info("Starting training with proper data splits...")
        
        # Create data splits if not already created
        if not enhanced_dataset.split_datasets:
            enhanced_dataset.create_splits()
        
        # Create DataLoaders for all splits
        split_dataloaders = self.dataloader_factory.create_split_dataloaders(enhanced_dataset)
        
        # Training loop
        best_val_loss = float('inf')
        patience_counter = 0
        
        for epoch in range(num_epochs):
            logger.info(f"\nEpoch {epoch + 1}/{num_epochs}")
            
            # Training phase
            train_loss, train_acc = self._train_epoch(split_dataloaders['train'])
            
            # Validation phase
            val_loss, val_acc = self._validate_epoch(split_dataloaders['val'])
            
            # Store metrics
            self.train_losses.append(train_loss)
            self.val_losses.append(val_loss)
            self.train_accuracies.append(train_acc)
            self.val_accuracies.append(val_acc)
            
            # Log progress
            logger.info(f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}")
            logger.info(f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}")
            
            # Early stopping
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                # Save best model
                torch.save(self.model.state_dict(), 'best_model.pth')
                logger.info("New best model saved!")
            else:
                patience_counter += 1
                if patience_counter >= early_stopping_patience:
                    logger.info(f"Early stopping triggered after {epoch + 1} epochs")
                    break
        
        # Final evaluation on test set
        test_loss, test_acc = self._validate_epoch(split_dataloaders['test'])
        logger.info(f"\nFinal Test Results - Loss: {test_loss:.4f}, Accuracy: {test_acc:.4f}")
        
        return {
            'train_losses': self.train_losses,
            'val_losses': self.val_losses,
            'train_accuracies': self.train_accuracies,
            'val_accuracies': self.val_accuracies,
            'test_loss': test_loss,
            'test_accuracy': test_acc
        }
    
    def train_with_cross_validation(
        self,
        enhanced_dataset: EnhancedDataset,
        n_folds: int = 5,
        cv_type: str = "stratified",
        num_epochs: int = 10
    ) -> Dict[str, Any]:
        """Train model using cross-validation"""
        logger.info(f"Starting {n_folds}-fold {cv_type} cross-validation training...")
        
        # Create cross-validation DataLoaders
        cv_dataloaders = self.dataloader_factory.create_cv_dataloaders(
            enhanced_dataset, n_folds, cv_type
        )
        
        cv_results = []
        
        for fold_idx, fold_dataloaders in enumerate(cv_dataloaders):
            logger.info(f"\n{'='*50}")
            logger.info(f"Training Fold {fold_idx + 1}/{n_folds}")
            logger.info(f"{'='*50}")
            
            # Reset model weights for each fold
            self.model.apply(self._init_weights)
            
            # Training loop for this fold
            fold_metrics = self._train_fold(
                fold_dataloaders, num_epochs
            )
            
            cv_results.append(fold_metrics)
            
            logger.info(f"Fold {fold_idx + 1} completed - "
                       f"Best Val Loss: {fold_metrics['best_val_loss']:.4f}, "
                       f"Best Val Acc: {fold_metrics['best_val_acc']:.4f}")
        
        # Calculate cross-validation summary
        cv_summary = self._calculate_cv_summary(cv_results)
        
        logger.info(f"\nCross-validation completed!")
        logger.info(f"Mean CV Accuracy: {cv_summary['mean_cv_accuracy']:.4f} ± {cv_summary['std_cv_accuracy']:.4f}")
        
        return {
            'fold_results': cv_results,
            'cv_summary': cv_summary
        }
    
    def _train_epoch(self, train_dataloader: DataLoader) -> Tuple[float, float]:
        """Train for one epoch"""
        self.model.train()
        total_loss = 0.0
        correct = 0
        total = 0
        
        for batch_idx, (data, targets) in enumerate(train_dataloader):
            data, targets = data.to(self.device), targets.to(self.device)
            
            # Forward pass
            self.optimizer.zero_grad()
            outputs = self.model(data)
            loss = self.criterion(outputs, targets)
            
            # Backward pass
            loss.backward()
            self.optimizer.step()
            
            # Metrics
            total_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += targets.size(0)
            correct += (predicted == targets).sum().item()
        
        avg_loss = total_loss / len(train_dataloader)
        accuracy = correct / total
        
        return avg_loss, accuracy
    
    def _validate_epoch(self, val_dataloader: DataLoader) -> Tuple[float, float]:
        """Validate for one epoch"""
        self.model.eval()
        total_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for data, targets in val_dataloader:
                data, targets = data.to(self.device), targets.to(self.device)
                
                outputs = self.model(data)
                loss = self.criterion(outputs, targets)
                
                total_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                total += targets.size(0)
                correct += (predicted == targets).sum().item()
        
        avg_loss = total_loss / len(val_dataloader)
        accuracy = correct / total
        
        return avg_loss, accuracy
    
    def _train_fold(
        self, 
        fold_dataloaders: Dict[str, DataLoader], 
        num_epochs: int
    ) -> Dict[str, float]:
        """Train model on a single fold"""
        best_val_loss = float('inf')
        best_val_acc = 0.0
        
        for epoch in range(num_epochs):
            # Training
            train_loss, train_acc = self._train_epoch(fold_dataloaders['train'])
            
            # Validation
            val_loss, val_acc = self._validate_epoch(fold_dataloaders['val'])
            
            # Update best metrics
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                best_val_acc = val_acc
        
        return {
            'best_val_loss': best_val_loss,
            'best_val_acc': best_val_acc
        }
    
    def _calculate_cv_summary(self, cv_results: List[Dict[str, float]]) -> Dict[str, float]:
        """Calculate summary statistics for cross-validation results"""
        val_accuracies = [result['best_val_acc'] for result in cv_results]
        val_losses = [result['best_val_loss'] for result in cv_results]
        
        return {
            'mean_cv_accuracy': np.mean(val_accuracies),
            'std_cv_accuracy': np.std(val_accuracies),
            'mean_cv_loss': np.mean(val_losses),
            'std_cv_loss': np.std(val_losses),
            'min_cv_accuracy': np.min(val_accuracies),
            'max_cv_accuracy': np.max(val_accuracies)
        }
    
    def _init_weights(self, module):
        """Initialize model weights"""
        if isinstance(module, nn.Linear):
            nn.init.xavier_uniform_(module.weight)
            if module.bias is not None:
                nn.init.constant_(module.bias, 0)
    
    def plot_training_curves(self, save_path: Optional[str] = None):
        """Plot training and validation curves"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        epochs = range(1, len(self.train_losses) + 1)
        
        # Loss curves
        ax1.plot(epochs, self.train_losses, 'b-', label='Training Loss')
        ax1.plot(epochs, self.val_losses, 'r-', label='Validation Loss')
        ax1.set_title('Training and Validation Loss')
        ax1.set_xlabel('Epoch')
        ax1.set_ylabel('Loss')
        ax1.legend()
        ax1.grid(True)
        
        # Accuracy curves
        ax2.plot(epochs, self.train_accuracies, 'b-', label='Training Accuracy')
        ax2.plot(epochs, self.val_accuracies, 'r-', label='Validation Accuracy')
        ax2.set_title('Training and Validation Accuracy')
        ax2.set_xlabel('Epoch')
        ax2.set_ylabel('Accuracy')
        ax2.legend()
        ax2.grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Training curves saved to {save_path}")
        
        plt.show()


def demonstrate_integration():
    """Demonstrate integration of enhanced DataLoader with training framework"""
    logger.info("Demonstrating DataLoader integration with training framework...")
    
    # 1. Generate synthetic data
    logger.info("\n1. Generating Synthetic Data")
    np.random.seed(42)
    n_samples = 2000
    n_features = 20
    n_classes = 4
    
    # Create imbalanced dataset for demonstration
    X = np.random.randn(n_samples, n_features)
    
    # Create imbalanced labels
    y = np.concatenate([
        np.zeros(n_samples // 2),  # Class 0: 50%
        np.ones(n_samples // 4),   # Class 1: 25%
        np.full(n_samples // 6, 2), # Class 2: 17%
        np.full(n_samples // 12, 3) # Class 3: 8%
    ])
    
    # Add some noise to make it more realistic
    y += np.random.normal(0, 0.1, len(y))
    y = np.clip(y, 0, n_classes - 1).astype(int)
    
    logger.info(f"Generated {n_samples} samples with {n_features} features and {n_classes} classes")
    unique_labels, counts = np.unique(y, return_counts=True)
    logger.info(f"Label distribution: {dict(zip(unique_labels, counts))}")
    
    # 2. Create enhanced dataset
    logger.info("\n2. Creating Enhanced Dataset")
    split_config = DataSplitConfig(
        train_ratio=0.7,
        val_ratio=0.15,
        test_ratio=0.15,
        stratify=True,
        random_state=42
    )
    
    dataset = EnhancedDataset(X, y, split_config=split_config)
    
    # 3. Configure DataLoader
    logger.info("\n3. Configuring Enhanced DataLoader")
    dataloader_config = DataLoaderConfig(
        batch_size=64,
        num_workers=2,
        pin_memory=True,
        persistent_workers=True,
        shuffle=True
    )
    
    # Optimize for GPU if available
    if torch.cuda.is_available():
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)  # GB
        dataloader_config = DataLoaderOptimizer.optimize_for_gpu(
            dataloader_config, gpu_memory_gb=gpu_memory
        )
    
    # 4. Create model
    logger.info("\n4. Creating Neural Network Model")
    model = SimpleNeuralNetwork(
        input_size=n_features,
        hidden_size=128,
        num_classes=n_classes
    )
    
    # 5. Create integrated trainer
    logger.info("\n5. Creating Integrated Trainer")
    trainer = IntegratedTrainer(
        model=model,
        dataloader_config=dataloader_config,
        learning_rate=0.001
    )
    
    # 6. Train with proper splits
    logger.info("\n6. Training with Proper Data Splits")
    split_results = trainer.train_with_splits(
        enhanced_dataset=dataset,
        num_epochs=15,
        early_stopping_patience=5
    )
    
    # 7. Train with cross-validation
    logger.info("\n7. Training with Cross-Validation")
    cv_results = trainer.train_with_cross_validation(
        enhanced_dataset=dataset,
        n_folds=3,
        cv_type="stratified",
        num_epochs=10
    )
    
    # 8. Plot training curves
    logger.info("\n8. Plotting Training Curves")
    trainer.plot_training_curves(save_path="./training_curves.png")
    
    # 9. Performance analysis
    logger.info("\n9. Performance Analysis")
    
    # Profile DataLoader performance
    split_datasets = dataset.split_datasets
    train_dataloader = trainer.dataloader_factory.create_dataloader(
        split_datasets['train'], 'train'
    )
    
    profile_results = DataLoaderOptimizer.profile_dataloader(train_dataloader, num_batches=10)
    
    logger.info("Integration demonstration completed!")
    
    return {
        'dataset': dataset,
        'trainer': trainer,
        'split_results': split_results,
        'cv_results': cv_results,
        'profile_results': profile_results
    }


def demonstrate_advanced_features():
    """Demonstrate advanced features of the enhanced DataLoader"""
    logger.info("Demonstrating advanced DataLoader features...")
    
    # 1. Group-based splitting
    logger.info("\n1. Group-based Data Splitting")
    np.random.seed(42)
    n_samples = 1000
    n_features = 10
    
    # Create data with groups
    X = np.random.randn(n_samples, n_features)
    y = np.random.randint(0, 3, n_samples)
    groups = np.random.randint(0, 50, n_samples)  # 50 groups
    
    # Create dataset with group-based splitting
    group_config = DataSplitConfig(
        train_ratio=0.7,
        val_ratio=0.15,
        test_ratio=0.15,
        group_by='groups',
        stratify=False
    )
    
    group_dataset = EnhancedDataset(X, y, split_config=group_config)
    group_splits = group_dataset.create_splits(groups=groups)
    
    logger.info(f"Group-based splits created:")
    for split_name, split_dataset in group_splits.items():
        logger.info(f"  {split_name}: {len(split_dataset)} samples")
    
    # 2. Time series splitting
    logger.info("\n2. Time Series Data Splitting")
    time_config = DataSplitConfig(
        train_ratio=0.6,
        val_ratio=0.2,
        test_ratio=0.2,
        is_time_series=True,
        stratify=False
    )
    
    time_dataset = EnhancedDataset(X, y, split_config=time_config)
    time_splits = time_dataset.create_splits()
    
    logger.info(f"Time series splits created:")
    for split_name, split_dataset in time_splits.items():
        logger.info(f"  {split_name}: {len(split_dataset)} samples")
    
    # 3. Weighted sampling for imbalanced data
    logger.info("\n3. Weighted Sampling for Imbalanced Data")
    
    # Calculate class weights
    unique_labels, counts = np.unique(y, return_counts=True)
    total_samples = len(y)
    class_weights = {label: total_samples / (len(unique_labels) * count) for label, count in zip(unique_labels, counts)}
    
    logger.info(f"Class weights calculated: {class_weights}")
    
    # Configure DataLoader with weighted sampling
    weighted_config = DataLoaderConfig(
        batch_size=32,
        num_workers=2,
        use_weighted_sampling=True,
        class_weights=class_weights
    )
    
    weighted_factory = EnhancedDataLoaderFactory(weighted_config)
    
    # Create DataLoaders with weighted sampling
    weighted_dataloaders = weighted_factory.create_split_dataloaders(group_dataset)
    
    logger.info("Weighted sampling DataLoaders created successfully")
    
    return {
        'group_dataset': group_dataset,
        'time_dataset': time_dataset,
        'weighted_dataloaders': weighted_dataloaders,
        'class_weights': class_weights
    }


if __name__ == "__main__":
    # Run main integration demonstration
    logger.info("="*60)
    logger.info("DATALOADER INTEGRATION DEMONSTRATION")
    logger.info("="*60)
    
    main_results = demonstrate_integration()
    
    # Run advanced features demonstration
    logger.info("\n" + "="*60)
    logger.info("ADVANCED FEATURES DEMONSTRATION")
    logger.info("="*60)
    
    advanced_results = demonstrate_advanced_features()
    
    # Print comprehensive summary
    print("\n" + "="*80)
    print("COMPREHENSIVE INTEGRATION SUMMARY")
    print("="*80)
    
    print(f"\nDataset Information:")
    print(f"  Total samples: {len(main_results['dataset'])}")
    print(f"  Features: {main_results['dataset'].data.shape[1]}")
    print(f"  Classes: {len(torch.unique(main_results['dataset'].labels))}")
    
    print(f"\nTraining Results (with splits):")
    split_results = main_results['split_results']
    print(f"  Final train accuracy: {split_results['train_accuracies'][-1]:.4f}")
    print(f"  Final val accuracy: {split_results['val_accuracies'][-1]:.4f}")
    print(f"  Test accuracy: {split_results['test_accuracy']:.4f}")
    
    print(f"\nCross-Validation Results:")
    cv_results = main_results['cv_results']
    cv_summary = cv_results['cv_summary']
    print(f"  Mean CV accuracy: {cv_summary['mean_cv_accuracy']:.4f} ± {cv_summary['std_cv_accuracy']:.4f}")
    print(f"  CV accuracy range: {cv_summary['min_cv_accuracy']:.4f} - {cv_summary['max_cv_accuracy']:.4f}")
    
    print(f"\nDataLoader Performance:")
    profile = main_results['profile_results']
    print(f"  Throughput: {profile['samples_per_second']:.1f} samples/sec")
    print(f"  Avg batch time: {profile['avg_batch_time']:.3f}s")
    
    print(f"\nAdvanced Features:")
    print(f"  Group-based splitting: ✓")
    print(f"  Time series splitting: ✓")
    print(f"  Weighted sampling: ✓")
    print(f"  Cross-validation: ✓")
    print(f"  Early stopping: ✓")
    
    print("\n" + "="*80)
    print("Integration demonstration completed successfully!")
    print("="*80)
