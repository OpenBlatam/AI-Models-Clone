from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS = 1000

# Constants
MAX_RETRIES = 100

# Constants
TIMEOUT_SECONDS = 60

import sys
import os
import time
import random
import numpy as np
import pandas as pd
from pathlib import Path
from modular_ml_structure import (
        import traceback
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
Modular ML Structure Runner Script

This script demonstrates the modular ML/DL project structure with separate files
for models, data loading, training, and evaluation, following key conventions.
"""


# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

    ModelConfig,
    MLPipeline,
    ModelFactory,
    DataLoaderManager,
    Trainer,
    ModelEvaluator,
    create_sample_data,
    save_sample_data
)


def demonstrate_data_loading():
    """Demonstrate data loading and preprocessing."""
    print("=" * 60)
    print("DATA LOADING MODULE DEMONSTRATION")
    print("=" * 60)
    
    # Create configuration
    config = ModelConfig(
        input_size=784,
        output_size=10,
        batch_size=16,
        experiment_name="data_loading_demo"
    )
    
    # Create sample data
    print("\n1. Creating sample data...")
    features, labels = create_sample_data(n_samples=1000, n_features=784, n_classes=10)
    print(f"   Created {len(features)} samples with {features.shape[1]} features")
    print(f"   Labels: {np.unique(labels, return_counts=True)}")
    
    # Save data
    data_path = "./data/sample_data.npy"
    save_sample_data(features, labels, data_path)
    print(f"   Data saved to {data_path}")
    
    # Test data loading
    print("\n2. Testing data loading...")
    data_manager = DataLoaderManager(config)
    train_loader, val_loader = data_manager.create_dataloaders(data_path)
    
    print(f"   Train batches: {len(train_loader)}")
    print(f"   Validation batches: {len(val_loader)}")
    
    # Test batch iteration
    print("\n3. Testing batch iteration...")
    for batch_idx, (data, targets) in enumerate(train_loader):
        print(f"   Batch {batch_idx + 1}: {data.shape}, targets: {targets.shape}")
        if batch_idx >= 2:  # Show first 3 batches
            break


def demonstrate_model_creation():
    """Demonstrate model creation and architecture."""
    print("\n" + "=" * 60)
    print("MODEL CREATION MODULE DEMONSTRATION")
    print("=" * 60)
    
    # Create configuration
    config = ModelConfig(
        input_size=784,
        hidden_sizes=[512, 256, 128],
        output_size=10,
        dropout_rate=0.2,
        experiment_name="model_creation_demo"
    )
    
    # Test MLP model
    print("\n1. Creating MLP model...")
    mlp_model = ModelFactory.create_model("mlp", config)
    print(f"   MLP parameters: {sum(p.numel() for p in mlp_model.parameters()):,}")
    print(f"   MLP trainable parameters: {sum(p.numel() for p in mlp_model.parameters() if p.requires_grad):,}")
    
    # Test CNN model
    print("\n2. Creating CNN model...")
    cnn_model = ModelFactory.create_model("cnn", config)
    print(f"   CNN parameters: {sum(p.numel() for p in cnn_model.parameters()):,}")
    print(f"   CNN trainable parameters: {sum(p.numel() for p in cnn_model.parameters() if p.requires_grad):,}")
    
    # Test forward pass
    print("\n3. Testing forward pass...")
    test_input = torch.randn(4, 784)  # 4 samples, 784 features
    
    mlp_output = mlp_model(test_input)
    print(f"   MLP output shape: {mlp_output.shape}")
    
    cnn_output = cnn_model(test_input)
    print(f"   CNN output shape: {cnn_output.shape}")
    
    # Test model saving/loading
    print("\n4. Testing model saving/loading...")
    model_path = "./models/test_model.pth"
    mlp_model.save_model(model_path)
    print(f"   Model saved to {model_path}")
    
    # Create new model and load
    new_model = ModelFactory.create_model("mlp", config)
    new_model.load_model(model_path)
    print("   Model loaded successfully")


def demonstrate_training():
    """Demonstrate training process."""
    print("\n" + "=" * 60)
    print("TRAINING MODULE DEMONSTRATION")
    print("=" * 60)
    
    # Create configuration for quick training
    config = ModelConfig(
        input_size=784,
        hidden_sizes=[256, 128],
        output_size=10,
        learning_rate=0.001,
        batch_size=32,
        num_epochs=5,  # Short training for demo
        early_stopping_patience=3,
        experiment_name="training_demo"
    )
    
    # Create sample data
    print("\n1. Preparing data...")
    features, labels = create_sample_data(n_samples=500, n_features=784, n_classes=10)
    data_path = "./data/training_data.npy"
    save_sample_data(features, labels, data_path)
    
    # Create data loaders
    data_manager = DataLoaderManager(config)
    train_loader, val_loader = data_manager.create_dataloaders(data_path)
    
    # Create model
    print("\n2. Creating model...")
    model = ModelFactory.create_model("mlp", config)
    
    # Initialize trainer
    trainer = Trainer(config)
    
    # Train model
    print("\n3. Training model...")
    start_time = time.time()
    history = trainer.train_model(model, train_loader, val_loader)
    training_time = time.time() - start_time
    
    print(f"\n   Training completed in {training_time:.2f} seconds")
    print(f"   Final train accuracy: {history['train_acc'][-1]:.4f}")
    print(f"   Final validation accuracy: {history['val_acc'][-1]:.4f}")


def demonstrate_evaluation():
    """Demonstrate model evaluation."""
    print("\n" + "=" * 60)
    print("EVALUATION MODULE DEMONSTRATION")
    print("=" * 60)
    
    # Create configuration
    config = ModelConfig(
        input_size=784,
        hidden_sizes=[256, 128],
        output_size=10,
        batch_size=32,
        experiment_name="evaluation_demo"
    )
    
    # Create sample data
    print("\n1. Preparing test data...")
    features, labels = create_sample_data(n_samples=200, n_features=784, n_classes=10)
    data_path = "./data/evaluation_data.npy"
    save_sample_data(features, labels, data_path)
    
    # Create data loader
    data_manager = DataLoaderManager(config)
    _, test_loader = data_manager.create_dataloaders(data_path)
    
    # Create and train a model quickly
    print("\n2. Training model for evaluation...")
    model = ModelFactory.create_model("mlp", config)
    trainer = Trainer(ModelConfig(num_epochs=3, experiment_name="quick_train"))
    history = trainer.train_model(model, test_loader, test_loader)  # Using same data for demo
    
    # Evaluate model
    print("\n3. Evaluating model...")
    evaluator = ModelEvaluator(config)
    results = evaluator.evaluate_model(model, test_loader)
    
    print(f"   Test accuracy: {results['accuracy']:.4f}")
    print(f"   Test loss: {results['loss']:.4f}")
    
    # Save results
    results_path = "./logs/evaluation_results.json"
    evaluator.save_results(results, results_path)
    print(f"   Results saved to {results_path}")
    
    # Plot results
    plots_path = "./logs/evaluation_plots.png"
    evaluator.plot_results(results, plots_path)
    print(f"   Plots saved to {plots_path}")


def demonstrate_complete_pipeline():
    """Demonstrate the complete ML pipeline."""
    print("\n" + "=" * 60)
    print("COMPLETE ML PIPELINE DEMONSTRATION")
    print("=" * 60)
    
    # Create configuration
    config = ModelConfig(
        input_size=784,
        hidden_sizes=[512, 256, 128],
        output_size=10,
        learning_rate=0.001,
        batch_size=32,
        num_epochs=8,
        early_stopping_patience=5,
        experiment_name="complete_pipeline_demo"
    )
    
    # Create sample data
    print("\n1. Creating sample dataset...")
    features, labels = create_sample_data(n_samples=1000, n_features=784, n_classes=10)
    data_path = "./data/complete_pipeline_data.npy"
    save_sample_data(features, labels, data_path)
    
    # Initialize pipeline
    print("\n2. Initializing ML pipeline...")
    pipeline = MLPipeline(config)
    
    # Run experiment
    print("\n3. Running complete experiment...")
    start_time = time.time()
    results = pipeline.run_experiment(data_path, model_type="mlp")
    experiment_time = time.time() - start_time
    
    print(f"\n   Experiment completed in {experiment_time:.2f} seconds")
    print(f"   Best accuracy: {results['evaluation_results']['accuracy']:.4f}")
    print(f"   Model saved to: {results['model_path']}")
    print(f"   Results saved to: ./logs/{config.experiment_name}_results.json")
    print(f"   Plots saved to: ./logs/{config.experiment_name}_plots.png")


def demonstrate_multiple_models():
    """Demonstrate training multiple model types."""
    print("\n" + "=" * 60)
    print("MULTIPLE MODELS COMPARISON")
    print("=" * 60)
    
    # Create sample data
    print("\n1. Creating sample dataset...")
    features, labels = create_sample_data(n_samples=800, n_features=784, n_classes=10)
    data_path = "./data/multiple_models_data.npy"
    save_sample_data(features, labels, data_path)
    
    # Test different model types
    model_types = ["mlp", "cnn"]
    results_comparison = {}
    
    for model_type in model_types:
        print(f"\n2. Training {model_type.upper()} model...")
        
        config = ModelConfig(
            input_size=784,
            hidden_sizes=[256, 128] if model_type == "mlp" else [256, 128],
            output_size=10,
            learning_rate=0.001,
            batch_size=32,
            num_epochs=5,
            experiment_name=f"{model_type}_comparison"
        )
        
        pipeline = MLPipeline(config)
        results = pipeline.run_experiment(data_path, model_type=model_type)
        
        results_comparison[model_type] = {
            'accuracy': results['evaluation_results']['accuracy'],
            'loss': results['evaluation_results']['loss'],
            'parameters': sum(p.numel() for p in results['model'].parameters())
        }
    
    # Compare results
    print("\n3. Model Comparison Results:")
    print("-" * 50)
    for model_type, metrics in results_comparison.items():
        print(f"   {model_type.upper()}:")
        print(f"     Accuracy: {metrics['accuracy']:.4f}")
        print(f"     Loss: {metrics['loss']:.4f}")
        print(f"     Parameters: {metrics['parameters']:,}")


def demonstrate_error_handling():
    """Demonstrate error handling in the modular structure."""
    print("\n" + "=" * 60)
    print("ERROR HANDLING DEMONSTRATION")
    print("=" * 60)
    
    # Test invalid model type
    print("\n1. Testing invalid model type...")
    try:
        config = ModelConfig()
        model = ModelFactory.create_model("invalid_model", config)
    except ValueError as e:
        print(f"   ✓ Caught expected error: {e}")
    
    # Test invalid data path
    print("\n2. Testing invalid data path...")
    try:
        config = ModelConfig()
        data_manager = DataLoaderManager(config)
        train_loader, val_loader = data_manager.create_dataloaders("nonexistent_file.csv")
    except Exception as e:
        print(f"   ✓ Caught expected error: {e}")
    
    # Test invalid configuration
    print("\n3. Testing invalid configuration...")
    try:
        config = ModelConfig(input_size=-1)  # Invalid input size
        model = ModelFactory.create_model("mlp", config)
    except Exception as e:
        print(f"   ✓ Caught expected error: {e}")


def main():
    """Main function to run all modular ML structure demonstrations."""
    print("MODULAR ML STRUCTURE IMPLEMENTATION DEMONSTRATION")
    print("=" * 80)
    
    try:
        # Create necessary directories
        os.makedirs("./data", exist_ok=True)
        os.makedirs("./models", exist_ok=True)
        os.makedirs("./logs", exist_ok=True)
        
        # Run demonstrations
        demonstrate_data_loading()
        demonstrate_model_creation()
        demonstrate_training()
        demonstrate_evaluation()
        demonstrate_complete_pipeline()
        demonstrate_multiple_models()
        demonstrate_error_handling()
        
        print("\n" + "=" * 80)
        print("MODULAR ML STRUCTURE IMPLEMENTATION COMPLETE")
        print("=" * 80)
        print("\nKey Features Demonstrated:")
        print("✓ Modular code structure with separate files")
        print("✓ Data loading and preprocessing")
        print("✓ Model creation and architecture")
        print("✓ Training with progress tracking")
        print("✓ Model evaluation and analysis")
        print("✓ Complete ML pipeline")
        print("✓ Multiple model comparison")
        print("✓ Error handling and validation")
        print("✓ Configuration management")
        print("✓ Logging and visualization")
        
        print("\nFiles Created:")
        print("- modular_ml_structure.py: Main implementation")
        print("- data/: Sample datasets")
        print("- models/                    # Saved models")
        print("- logs/                      # Results and plots")
        
        print("\nProject Structure:")
        print("├── modular_ml_structure.py    # Main implementation")
        print("├── run_modular_ml_structure.py # Runner script")
        print("├── data/                      # Data files")
        print("├── models/                    # Saved models")
        print("└── logs/                      # Results and plots")
        
    except ImportError as e:
        print(f"Error: Missing required dependency - {e}")
        print("Please install required packages:")
        print("pip install torch numpy pandas scikit-learn matplotlib seaborn omegaconf")
    except Exception as e:
        print(f"Error during execution: {e}")
        traceback.print_exc()


match __name__:
    case "__main__":
    main() 