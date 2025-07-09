"""
Example Usage of Configuration Management System
===============================================

This script demonstrates various ways to use the configuration management system
for different scenarios in AI video generation.

Scenarios covered:
1. Loading default configurations
2. Creating custom configurations
3. Environment-specific configurations
4. Command-line configuration management
5. Configuration validation and error handling
6. Configuration inheritance and merging
7. Experiment tracking integration
"""

import os
import sys
import logging
from pathlib import Path

# Add the parent directory to the path to import modules
sys.path.append(str(Path(__file__).parent.parent))

from config import (
    ConfigManager,
    quick_load_config,
    create_custom_config,
    load_config_with_env,
    create_experiment_config,
    validate_and_save_config,
    get_example_configs
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_1_load_default_configs():
    """Example 1: Loading default configurations."""
    print("\n" + "="*50)
    print("EXAMPLE 1: Loading Default Configurations")
    print("="*50)
    
    # Get available example configurations
    example_configs = get_example_configs()
    
    for config_type, config_name in example_configs.items():
        print(f"\n📋 Loading {config_type} configuration:")
        try:
            config = quick_load_config(config_name)
            print(f"   ✅ Loaded: {config.name}")
            print(f"   📝 Description: {config.description}")
            print(f"   🎯 Model type: {config.model.model_type}")
            print(f"   📐 Frame size: {config.model.frame_size}")
            print(f"   🎬 Number of frames: {config.model.num_frames}")
            print(f"   🏋️ Training epochs: {config.training.num_epochs}")
            print(f"   📦 Batch size: {config.training.batch_size}")
            print(f"   🎓 Learning rate: {config.training.learning_rate}")
            
        except Exception as e:
            print(f"   ❌ Error loading {config_name}: {e}")


def example_2_create_custom_configs():
    """Example 2: Creating custom configurations."""
    print("\n" + "="*50)
    print("EXAMPLE 2: Creating Custom Configurations")
    print("="*50)
    
    # Example 2.1: High-resolution video generation
    print("\n🎬 Creating high-resolution video configuration:")
    high_res_config = create_custom_config(
        "diffusion_default",
        {
            "model.frame_size": [512, 512],
            "model.num_frames": 24,
            "model.latent_dim": 1024,
            "training.num_epochs": 200,
            "training.learning_rate": 5e-5,
            "training.batch_size": 2,
            "training.use_gradient_accumulation": True,
            "training.gradient_accumulation_steps": 4,
            "system.environment": "production",
            "system.gpu_memory_fraction": 0.95
        },
        "high_res_video_generation"
    )
    
    print(f"   ✅ Created: {high_res_config.name}")
    print(f"   📐 Frame size: {high_res_config.model.frame_size}")
    print(f"   🎬 Frames: {high_res_config.model.num_frames}")
    print(f"   🏋️ Epochs: {high_res_config.training.num_epochs}")
    print(f"   📦 Batch size: {high_res_config.training.batch_size}")
    print(f"   🔄 Gradient accumulation: {high_res_config.training.use_gradient_accumulation}")
    
    # Example 2.2: Fast experimentation configuration
    print("\n⚡ Creating fast experimentation configuration:")
    fast_config = create_custom_config(
        "diffusion_default",
        {
            "model.frame_size": [128, 128],
            "model.num_frames": 8,
            "model.latent_dim": 256,
            "training.num_epochs": 10,
            "training.learning_rate": 1e-3,
            "training.batch_size": 16,
            "training.save_frequency": 2,
            "training.eval_frequency": 1,
            "system.debug": True,
            "system.log_level": "DEBUG",
            "data.augment": False
        },
        "fast_experimentation"
    )
    
    print(f"   ✅ Created: {fast_config.name}")
    print(f"   📐 Frame size: {fast_config.model.frame_size}")
    print(f"   🎬 Frames: {fast_config.model.num_frames}")
    print(f"   🏋️ Epochs: {fast_config.training.num_epochs}")
    print(f"   📦 Batch size: {fast_config.training.batch_size}")
    print(f"   🐛 Debug mode: {fast_config.system.debug}")
    
    # Save configurations
    validate_and_save_config(high_res_config, "configs/high_res_config.yaml")
    validate_and_save_config(fast_config, "configs/fast_config.yaml")


def example_3_environment_specific_configs():
    """Example 3: Environment-specific configurations."""
    print("\n" + "="*50)
    print("EXAMPLE 3: Environment-Specific Configurations")
    print("="*50)
    
    # Simulate environment variables
    env_vars = {
        "AI_VIDEO_MODEL_FRAME_SIZE": "512,512",
        "AI_VIDEO_TRAINING_BATCH_SIZE": "4",
        "AI_VIDEO_TRAINING_NUM_EPOCHS": "50",
        "AI_VIDEO_SYSTEM_ENVIRONMENT": "production",
        "AI_VIDEO_SYSTEM_DEBUG": "false"
    }
    
    # Set environment variables
    for key, value in env_vars.items():
        os.environ[key] = value
    
    print("🔧 Environment variables set:")
    for key, value in env_vars.items():
        print(f"   {key}={value}")
    
    # Load configuration with environment overrides
    print("\n📋 Loading configuration with environment overrides:")
    try:
        config = load_config_with_env("default_configs.yaml", "diffusion_default")
        print(f"   ✅ Loaded: {config.name}")
        print(f"   📐 Frame size: {config.model.frame_size}")
        print(f"   📦 Batch size: {config.training.batch_size}")
        print(f"   🏋️ Epochs: {config.training.num_epochs}")
        print(f"   🌍 Environment: {config.system.environment}")
        print(f"   🐛 Debug mode: {config.system.debug}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Clean up environment variables
    for key in env_vars:
        if key in os.environ:
            del os.environ[key]


def example_4_configuration_manager():
    """Example 4: Using Configuration Manager."""
    print("\n" + "="*50)
    print("EXAMPLE 4: Using Configuration Manager")
    print("="*50)
    
    # Create configuration manager
    manager = ConfigManager("configs")
    
    # List available configurations
    print("\n📁 Available configuration files:")
    configs = manager.list_configs()
    for config_file in configs:
        print(f"   - {config_file}")
    
    # Create new configuration from template
    print("\n🆕 Creating new configuration from template:")
    new_config = manager.create_config("my_experiment", "transformer")
    
    # Customize the configuration
    new_config.model.frame_size = [384, 384]
    new_config.model.num_layers = 8
    new_config.training.num_epochs = 75
    new_config.training.learning_rate = 3e-5
    new_config.training.use_wandb = True
    new_config.training.experiment_name = "transformer_experiment"
    
    print(f"   ✅ Created: {new_config.name}")
    print(f"   🎯 Model type: {new_config.model.model_type}")
    print(f"   📐 Frame size: {new_config.model.frame_size}")
    print(f"   🏗️ Layers: {new_config.model.num_layers}")
    print(f"   🏋️ Epochs: {new_config.training.num_epochs}")
    print(f"   📊 WandB enabled: {new_config.training.use_wandb}")
    
    # Save configuration
    filepath = manager.save_config(new_config, "my_transformer_experiment.yaml")
    print(f"   💾 Saved to: {filepath}")
    
    # Load and validate configuration
    print("\n🔍 Loading and validating configuration:")
    loaded_config = manager.load_config("my_transformer_experiment.yaml")
    validation_results = manager.validate_config(loaded_config)
    
    if validation_results:
        print("   ⚠️ Validation warnings:")
        for component, errors in validation_results.items():
            for error in errors:
                print(f"      {component}: {error}")
    else:
        print("   ✅ Configuration is valid")


def example_5_experiment_tracking_integration():
    """Example 5: Integration with experiment tracking."""
    print("\n" + "="*50)
    print("EXAMPLE 5: Experiment Tracking Integration")
    print("="*50)
    
    # Create experiment configuration
    experiment_config = create_experiment_config(
        "wandb_integration_experiment",
        "diffusion",
        {
            "training.use_wandb": True,
            "training.use_tensorboard": True,
            "training.experiment_name": "wandb_integration_test",
            "training.project_name": "ai_video_research",
            "model.frame_size": [256, 256],
            "training.num_epochs": 25,
            "training.batch_size": 8,
            "system.environment": "development"
        }
    )
    
    print(f"🎯 Experiment: {experiment_config.name}")
    print(f"📊 WandB enabled: {experiment_config.training.use_wandb}")
    print(f"📈 TensorBoard enabled: {experiment_config.training.use_tensorboard}")
    print(f"🔬 Project: {experiment_config.training.project_name}")
    print(f"🧪 Experiment: {experiment_config.training.experiment_name}")
    
    # Simulate experiment tracking setup
    print("\n🔧 Setting up experiment tracking:")
    print("   import wandb")
    print("   import torch.utils.tensorboard as tensorboard")
    print("")
    print("   # Initialize WandB")
    print("   if config.training.use_wandb:")
    print("       wandb.init(")
    print("           project=config.training.project_name,")
    print("           name=config.training.experiment_name,")
    print("           config=config.to_dict()")
    print("       )")
    print("")
    print("   # Initialize TensorBoard")
    print("   if config.training.use_tensorboard:")
    print("       writer = tensorboard.SummaryWriter(")
    print("           log_dir=f'runs/{config.training.experiment_name}'")
    print("       )")
    
    # Save experiment configuration
    validate_and_save_config(experiment_config, "configs/wandb_experiment.yaml")


def example_6_error_handling():
    """Example 6: Error handling and validation."""
    print("\n" + "="*50)
    print("EXAMPLE 6: Error Handling and Validation")
    print("="*50)
    
    # Create invalid configuration
    print("\n❌ Creating invalid configuration:")
    invalid_config = create_custom_config(
        "diffusion_default",
        {
            "model.frame_size": [-256, 256],  # Invalid negative size
            "training.batch_size": -8,        # Invalid negative batch size
            "training.learning_rate": 0,      # Invalid zero learning rate
            "model.model_type": "invalid_type"  # Invalid model type
        },
        "invalid_config"
    )
    
    print(f"   📋 Created: {invalid_config.name}")
    
    # Validate configuration
    print("\n🔍 Validating configuration:")
    validation_results = invalid_config.get_validation_errors()
    
    if validation_results:
        print("   ❌ Validation errors found:")
        for error in validation_results:
            print(f"      - {error}")
    else:
        print("   ✅ Configuration is valid")
    
    # Try to save invalid configuration
    print("\n💾 Attempting to save invalid configuration:")
    success = validate_and_save_config(invalid_config, "configs/invalid_config.yaml")
    if not success:
        print("   ❌ Failed to save invalid configuration")
    
    # Create valid configuration
    print("\n✅ Creating valid configuration:")
    valid_config = create_custom_config(
        "diffusion_default",
        {
            "model.frame_size": [256, 256],
            "training.batch_size": 8,
            "training.learning_rate": 1e-4
        },
        "valid_config"
    )
    
    print(f"   📋 Created: {valid_config.name}")
    
    # Validate and save valid configuration
    success = validate_and_save_config(valid_config, "configs/valid_config.yaml")
    if success:
        print("   ✅ Successfully saved valid configuration")


def main():
    """Run all examples."""
    print("🚀 AI Video Configuration Management Examples")
    print("=" * 60)
    
    try:
        # Create configs directory
        Path("configs").mkdir(exist_ok=True)
        
        # Run examples
        example_1_load_default_configs()
        example_2_create_custom_configs()
        example_3_environment_specific_configs()
        example_4_configuration_manager()
        example_5_experiment_tracking_integration()
        example_6_error_handling()
        
        print("\n" + "="*60)
        print("✅ All examples completed successfully!")
        print("\n📁 Generated configuration files:")
        config_files = list(Path("configs").glob("*.yaml"))
        for config_file in config_files:
            print(f"   - {config_file}")
        
        print("\n🎯 Next steps:")
        print("   1. Review generated configuration files")
        print("   2. Customize configurations for your experiments")
        print("   3. Use configurations in your training scripts")
        print("   4. Set up environment variables for production")
        print("   5. Integrate with experiment tracking tools")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        logger.exception("Exception occurred")


if __name__ == "__main__":
    main() 