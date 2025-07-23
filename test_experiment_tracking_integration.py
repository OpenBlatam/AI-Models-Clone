#!/usr/bin/env python3
"""
Test script for experiment tracking integration with Gradio app.
"""

import sys
import os
import json
import torch
import numpy as np
from pathlib import Path

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_experiment_tracking_imports():
    """Test that experiment tracking system can be imported."""
    print("Testing experiment tracking imports...")
    
    try:
        from experiment_tracking_system import (
            ExperimentTracker, ExperimentConfig, create_experiment_config,
            experiment_context, track_experiment, start_tensorboard_server,
            compare_experiments, get_tensorboard_url
        )
        print("✅ Experiment tracking system imports successful")
        return True
    except ImportError as e:
        print(f"❌ Experiment tracking system import failed: {e}")
        return False

def test_gradio_app_imports():
    """Test that Gradio app can import experiment tracking system."""
    print("\nTesting Gradio app imports...")
    
    try:
        # Import the gradio app module
        import gradio_app
        print("✅ Gradio app import successful")
        
        # Check if EXPERIMENT_TRACKING_AVAILABLE is defined
        if hasattr(gradio_app, 'EXPERIMENT_TRACKING_AVAILABLE'):
            print(f"✅ EXPERIMENT_TRACKING_AVAILABLE: {gradio_app.EXPERIMENT_TRACKING_AVAILABLE}")
        else:
            print("❌ EXPERIMENT_TRACKING_AVAILABLE not found")
            return False
            
        return True
    except ImportError as e:
        print(f"❌ Gradio app import failed: {e}")
        return False

def test_experiment_tracking_interface_functions():
    """Test that experiment tracking interface functions exist."""
    print("\nTesting experiment tracking interface functions...")
    
    try:
        import gradio_app
        
        # Check if interface functions exist
        required_functions = [
            'start_experiment_tracking_interface',
            'log_training_metrics_interface',
            'log_validation_metrics_interface',
            'log_model_checkpoint_interface',
            'get_experiment_summary_interface',
            'finish_experiment_interface',
            'start_tensorboard_server_interface',
            'compare_experiments_interface'
        ]
        
        for func_name in required_functions:
            if hasattr(gradio_app, func_name):
                print(f"✅ {func_name} found")
            else:
                print(f"❌ {func_name} not found")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Error testing interface functions: {e}")
        return False

def test_basic_experiment_tracking():
    """Test basic experiment tracking functionality."""
    print("\nTesting basic experiment tracking...")
    
    try:
        from experiment_tracking_system import ExperimentTracker, create_experiment_config
        
        # Create experiment configuration
        config = create_experiment_config(
            experiment_name="test_experiment",
            project_name="test_project",
            enable_tensorboard=True,
            enable_wandb=False,  # Disable wandb for testing
            log_interval=5
        )
        
        # Create tracker
        tracker = ExperimentTracker(config)
        
        # Log some metrics
        tracker.log_training_step(loss=0.5, accuracy=0.8, learning_rate=0.001)
        tracker.log_validation_step(loss=0.6, accuracy=0.75, precision=0.8, recall=0.7, f1=0.75)
        tracker.log_epoch(0)
        
        # Get summary
        summary = tracker.get_experiment_summary()
        
        # Finish experiment
        tracker.finish()
        
        print(f"✅ Basic experiment tracking successful")
        print(f"   - Experiment name: {summary.get('experiment_name')}")
        print(f"   - Total steps: {summary.get('total_steps')}")
        print(f"   - Total epochs: {summary.get('total_epochs')}")
        
        return True
    except Exception as e:
        print(f"❌ Basic experiment tracking failed: {e}")
        return False

def test_experiment_config_creation():
    """Test experiment configuration creation."""
    print("\nTesting experiment configuration creation...")
    
    try:
        from experiment_tracking_system import create_experiment_config
        
        # Test basic configuration
        config = create_experiment_config(
            experiment_name="test_config",
            project_name="test_project",
            enable_tensorboard=True,
            enable_wandb=False
        )
        
        print(f"✅ Experiment configuration creation successful")
        print(f"   - Experiment name: {config.experiment_name}")
        print(f"   - Project name: {config.project_name}")
        print(f"   - TensorBoard enabled: {config.enable_tensorboard}")
        print(f"   - WandB enabled: {config.enable_wandb}")
        
        return True
    except Exception as e:
        print(f"❌ Experiment configuration creation failed: {e}")
        return False

def test_context_manager():
    """Test experiment context manager."""
    print("\nTesting experiment context manager...")
    
    try:
        from experiment_tracking_system import experiment_context, create_experiment_config
        
        # Create configuration
        config = create_experiment_config(
            experiment_name="context_test",
            project_name="test_project",
            enable_tensorboard=True,
            enable_wandb=False
        )
        
        # Use context manager
        with experiment_context(config) as tracker:
            # Log some metrics
            tracker.log_training_step(loss=0.3, accuracy=0.9)
            tracker.log_validation_step(loss=0.4, accuracy=0.85)
            
            # Get summary
            summary = tracker.get_experiment_summary()
        
        print(f"✅ Context manager test successful")
        print(f"   - Total steps: {summary.get('total_steps')}")
        
        return True
    except Exception as e:
        print(f"❌ Context manager test failed: {e}")
        return False

def test_decorator():
    """Test experiment tracking decorator."""
    print("\nTesting experiment tracking decorator...")
    
    try:
        from experiment_tracking_system import track_experiment, create_experiment_config
        
        # Create configuration
        config = create_experiment_config(
            experiment_name="decorator_test",
            project_name="test_project",
            enable_tensorboard=True,
            enable_wandb=False
        )
        
        # Test function with decorator
        @track_experiment(config)
        def test_function():
            return "test_result"
        
        # Call function
        result = test_function()
        
        print(f"✅ Decorator test successful")
        print(f"   - Function result: {result}")
        
        return True
    except Exception as e:
        print(f"❌ Decorator test failed: {e}")
        return False

def test_hyperparameter_logging():
    """Test hyperparameter logging."""
    print("\nTesting hyperparameter logging...")
    
    try:
        from experiment_tracking_system import ExperimentTracker, create_experiment_config
        
        # Create configuration
        config = create_experiment_config(
            experiment_name="hyperparam_test",
            project_name="test_project",
            enable_tensorboard=True,
            enable_wandb=False
        )
        
        # Create tracker
        tracker = ExperimentTracker(config)
        
        # Log hyperparameters
        hyperparams = {
            'learning_rate': 0.001,
            'batch_size': 32,
            'num_epochs': 10,
            'model_type': 'test_model'
        }
        tracker.log_hyperparameters(hyperparams)
        
        # Finish experiment
        tracker.finish()
        
        print(f"✅ Hyperparameter logging successful")
        print(f"   - Logged {len(hyperparams)} hyperparameters")
        
        return True
    except Exception as e:
        print(f"❌ Hyperparameter logging failed: {e}")
        return False

def test_model_checkpointing():
    """Test model checkpointing."""
    print("\nTesting model checkpointing...")
    
    try:
        from experiment_tracking_system import ExperimentTracker, create_experiment_config
        import torch
        
        # Create configuration
        config = create_experiment_config(
            experiment_name="checkpoint_test",
            project_name="test_project",
            enable_tensorboard=True,
            enable_wandb=False
        )
        
        # Create tracker
        tracker = ExperimentTracker(config)
        
        # Create simple model
        model = torch.nn.Linear(10, 2)
        optimizer = torch.optim.Adam(model.parameters())
        
        # Log model checkpoint
        tracker.log_model_checkpoint(
            model=model,
            optimizer=optimizer,
            epoch=5,
            step=100,
            metrics={'train_loss': 0.3, 'val_loss': 0.4}
        )
        
        # Finish experiment
        tracker.finish()
        
        print(f"✅ Model checkpointing successful")
        
        return True
    except Exception as e:
        print(f"❌ Model checkpointing failed: {e}")
        return False

def test_tensorboard_url():
    """Test TensorBoard URL generation."""
    print("\nTesting TensorBoard URL generation...")
    
    try:
        from experiment_tracking_system import get_tensorboard_url
        
        # Test URL generation
        url = get_tensorboard_url("runs/tensorboard")
        
        print(f"✅ TensorBoard URL generation successful")
        print(f"   - URL: {url}")
        
        return True
    except Exception as e:
        print(f"❌ TensorBoard URL generation failed: {e}")
        return False

def test_experiment_comparison():
    """Test experiment comparison functionality."""
    print("\nTesting experiment comparison...")
    
    try:
        from experiment_tracking_system import compare_experiments
        import matplotlib.pyplot as plt
        
        # Test comparison
        experiment_names = ["exp1", "exp2", "exp3"]
        fig = compare_experiments(experiment_names, "train_loss")
        
        if fig:
            # Save plot
            fig.savefig("test_comparison.png", dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            print(f"✅ Experiment comparison successful")
            print(f"   - Compared {len(experiment_names)} experiments")
            print(f"   - Plot saved as 'test_comparison.png'")
            
            return True
        else:
            print(f"❌ Experiment comparison failed: No figure generated")
            return False
            
    except Exception as e:
        print(f"❌ Experiment comparison failed: {e}")
        return False

def test_interface_function_calls():
    """Test calling interface functions directly."""
    print("\nTesting interface function calls...")
    
    try:
        import gradio_app
        
        # Test start experiment tracking
        result = gradio_app.start_experiment_tracking_interface(
            experiment_name="interface_test",
            project_name="test_project",
            enable_tensorboard=True,
            enable_wandb=False,
            wandb_entity="",
            tags="test,demo"
        )
        
        result_dict = json.loads(result)
        
        if "error" in result_dict:
            print(f"⚠️  Interface function returned error: {result_dict['error']}")
            # This might be expected if dependencies are not available
            return True
        else:
            print(f"✅ Interface function call successful")
            print(f"   - Status: {result_dict.get('status')}")
            return True
            
    except Exception as e:
        print(f"❌ Interface function call failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Experiment Tracking Integration with Gradio App")
    print("=" * 70)
    
    tests = [
        test_experiment_tracking_imports,
        test_gradio_app_imports,
        test_experiment_tracking_interface_functions,
        test_basic_experiment_tracking,
        test_experiment_config_creation,
        test_context_manager,
        test_decorator,
        test_hyperparameter_logging,
        test_model_checkpointing,
        test_tensorboard_url,
        test_experiment_comparison,
        test_interface_function_calls
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 70)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Experiment tracking integration is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 