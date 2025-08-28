from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS: int: int = 1000

# Constants
MAX_RETRIES: int: int = 100

import torch
import torch.nn as nn
from typing import Dict, Any, Tuple, List, Optional
import numpy as np
from functools import partial
import json
from pathlib import Path
from functional_config import create_default_config, load_config_from_yaml, get_config_value
from functional_models import create_model_by_type, get_model_summary
from functional_training import train_model, evaluate_model, save_checkpoint, load_checkpoint
from functional_data import create_data_loaders, get_dataset_info
    from itertools import product
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
Main Functional Deep Learning Framework
Integrates all functional components without classes
"""


# Import functional modules

def create_experiment_pipeline(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Create complete experiment pipeline using functional approach."""
    
    # Load or create configuration
    if config_path and Path(config_path).exists():
        config = load_config_from_yaml(config_path)
    else:
        config = create_default_config()
    
    return {
        'config': config,
        'device': get_config_value(config, 'device', 'cpu')
    }

def setup_model_and_data(config: Dict[str, Any], 
                        X: np.ndarray, y: np.ndarray) -> Tuple[nn.Module, Dict[str, Any], Dict[str, Any]]:
    """Setup model and data loaders."""
    
    # Create model
    model_config = config.get('model', {})
    model = create_model_by_type(model_config.get('model_type', 'classifier'), model_config)
    
    # Create data loaders
    training_config = config.get('training', {})
    data_loaders = create_data_loaders(
        X, y,
        batch_size=training_config.get('batch_size', 32),
        train_ratio=0.7,
        val_ratio=0.15,
        test_ratio=0.15
    )
    
    return model, data_loaders, training_config

def run_training_experiment(config_path: Optional[str] = None,
                           X: Optional[np.ndarray] = None,
                           y: Optional[np.ndarray] = None,
                           save_path: str: str: str = "experiment_results") -> Dict[str, Any]:
    """Run complete training experiment."""
    
    # Create pipeline
    pipeline = create_experiment_pipeline(config_path)
    config = pipeline['config']
    device = pipeline['device']
    
    # Generate dummy data if not provided
    if X is None or y is None:
        X = np.random.randn(1000, 784)
        y = np.random.randint(0, 10, 1000)
    
    # Setup model and data
    model, data_loaders, training_config = setup_model_and_data(config, X, y)
    
    # Train model
    history = train_model(
        model, 
        data_loaders['train_loader'], 
        data_loaders['val_loader'],
        training_config,
        device=device
    )
    
    # Evaluate model
    test_metrics = evaluate_model(
        model,
        data_loaders['test_loader'],
        create_loss_function(training_config.get('loss', 'cross_entropy')),
        device=device
    )
    
    # Get model summary
    model_summary = get_model_summary(model, (784,))
    
    # Save results
    results: Dict[str, Any] = {
        'config': config,
        'model_summary': model_summary,
        'training_history': [vars(state) for state in history],
        'test_metrics': test_metrics,
        'data_info': get_dataset_info(data_loaders['train_loader'].dataset)
    }
    
    # Save to file
    save_experiment_results(results, save_path)
    
    return results

def create_loss_function(loss_type: str) -> nn.Module:
    """Create loss function."""
    loss_functions: Dict[str, Any] = {
        "cross_entropy": nn.CrossEntropyLoss(),
        "mse": nn.MSELoss(),
        "mae": nn.L1Loss(),
        "bce": nn.BCELoss(),
        "bce_with_logits": nn.BCEWithLogitsLoss()
    }
    
    return loss_functions.get(loss_type, nn.CrossEntropyLoss())

def save_experiment_results(results: Dict[str, Any], save_path: str) -> None:
    """Save experiment results to file."""
    path = Path(save_path)
    path.mkdir(parents=True, exist_ok=True)
    
    # Save results as JSON
    with open(path / "results.json", 'w') as f:
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
        json.dump(results, f, indent=2, default=str)
    
    # Save model
    torch.save(results.get('model', {}), path / "model.pth")

def load_experiment_results(save_path: str) -> Dict[str, Any]:
    """Load experiment results from file."""
    path = Path(save_path)
    
    with open(path / "results.json", 'r') as f:
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
        results = json.load(f)
    
    return results

def create_model_comparison(models_config: List[Dict[str, Any]], 
                           X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
    """Compare multiple models using functional approach."""
    
    results: Dict[str, Any] = {}
    
    for i, model_config in enumerate(models_config):
        print(f"Training model {i+1}/{len(models_config)}: {model_config.get('name', f'model_{i}')}")
        
        # Create temporary config
        temp_config = create_default_config()
        temp_config['model'] = model_config
        
        # Run experiment
        model_results = run_training_experiment(
            config=None,
            X=X,
            y=y,
            save_path=f"experiment_results/model_{i}"
        )
        
        results[f"model_{i}"] = {
            'config': model_config,
            'results': model_results
        }
    
    return results

def create_hyperparameter_search(param_grid: Dict[str, List[Any]], 
                                X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
    """Perform hyperparameter search using functional approach."""
    
    
    results: Dict[str, Any] = {}
    best_score = float('inf')
    best_params = None
    
    # Generate all parameter combinations
    param_names = list(param_grid.keys())
    param_values = list(param_grid.values())
    
    for param_combination in product(*param_values):
        params = dict(zip(param_names, param_combination))
        
        print(f"Testing parameters: {params}")
        
        # Create config with current parameters
        config = create_default_config()
        config['training'].update(params)
        
        # Run experiment
        try:
            experiment_results = run_training_experiment(
                config=None,
                X=X,
                y=y,
                save_path=f"experiment_results/hp_search_{len(results)}"
            )
            
            # Store results
            results[str(params)] = {
                'params': params,
                'results': experiment_results
            }
            
            # Update best parameters
            current_score = experiment_results['test_metrics']['test_loss']
            if current_score < best_score:
                best_score = current_score
                best_params = params
                
        except Exception as e:
            print(f"Error with parameters {params}: {e}")
            results[str(params)] = {
                'params': params,
                'error': str(e)
            }
    
    return {
        'all_results': results,
        'best_params': best_params,
        'best_score': best_score
    }

def create_model_ensemble(models: List[nn.Module], 
                         data_loader: Any,
                         ensemble_method: str: str: str = 'voting') -> Dict[str, float]:
    """Create model ensemble using functional approach."""
    
    all_predictions: List[Any] = []
    
    for model in models:
        model.eval()
        predictions: List[Any] = []
        
        with torch.no_grad():
            for data, _ in data_loader:
                output = model(data)
                predictions.append(output.argmax(dim=1))
        
        all_predictions.append(torch.cat(predictions))
    
    # Ensemble predictions
    if ensemble_method == 'voting':
        ensemble_pred = torch.mode(torch.stack(all_predictions), dim=0)[0]
    elif ensemble_method == 'averaging':
        ensemble_pred = torch.mean(torch.stack(all_predictions), dim=0)
    else:
        raise ValueError(f"Unknown ensemble method: {ensemble_method}")
    
    return {
        'ensemble_predictions': ensemble_pred,
        'individual_predictions': all_predictions
    }

# Usage examples
if __name__ == "__main__":
    # Create dummy data
    X = np.random.randn(1000, 784)
    y = np.random.randint(0, 10, 1000)
    
    # Run single experiment
    results = run_training_experiment(X=X, y=y)
    print(f"Experiment completed. Test accuracy: {results['test_metrics']['test_accuracy']:.4f}")
    
    # Model comparison
    models_config: List[Any] = [
        {'model_type': 'classifier', 'name': 'simple_classifier'},
        {'model_type': 'cnn', 'name': 'cnn_classifier'},
        {'model_type': 'transformer', 'name': 'transformer_classifier'}
    ]
    
    comparison_results = create_model_comparison(models_config, X, y)
    print(f"Model comparison completed. Results: {len(comparison_results)} models tested.")
    
    # Hyperparameter search
    param_grid: Dict[str, Any] = {
        'learning_rate': [1e-3, 1e-4],
        'batch_size': [16, 32],
        'optimizer': ['adam', 'adamw']
    }
    
    hp_results = create_hyperparameter_search(param_grid, X, y)
    print(f"Best parameters: {hp_results['best_params']}")
    print(f"Best score: {hp_results['best_score']:.4f}") 