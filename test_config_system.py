from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
import sys
import os
from config_manager import ConfigManager, Config, create_preset_configs
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
🧪 Test Configuration Management System
======================================
Simple test script to demonstrate configuration management functionality.
"""

sys.path.append('.')


def test_config_loading() -> Any:
    """Test configuration loading functionality."""
    logger.info("🧪 Testing Configuration Loading...")  # Super logging
    
    # Create config manager
    config_manager = ConfigManager("configs")
    
    # Create default configuration
    default_config = config_manager.create_default_config()
    logger.info(f"✅ Default configuration created: {default_config.name}")  # Super logging
    
    # Save default configuration
    config_path = config_manager.save_config(default_config, "configs/test_default.yaml")
    logger.info(f"✅ Default configuration saved to: {config_path}")  # Super logging
    
    # Load configuration back
    loaded_config = config_manager.load_config(config_path)
    logger.info(f"✅ Configuration loaded successfully: {loaded_config.name}")  # Super logging
    
    # Test configuration validation
    issues = config_manager.validate_config(loaded_config)
    if issues:
        logger.info(f"⚠️ Configuration validation issues: {issues}")  # Super logging
    else:
        logger.info("✅ Configuration validation passed")  # Super logging
    
    return True

def test_preset_configs() -> Any:
    """Test preset configurations."""
    logger.info("\n🧪 Testing Preset Configurations...")  # Super logging
    
    # Get preset configurations
    presets = create_preset_configs()
    
    for name, config in presets.items():
        logger.info(f"✅ Preset '{name}' created:")  # Super logging
        logger.info(f"   Model: {config.model.input_dim} → {config.model.hidden_dim}")  # Super logging
        logger.info(f"   Training: {config.training.batch_size} batch, {config.training.learning_rate} lr")  # Super logging
        logger.info(f"   Data: {config.data.dataset_size} samples")  # Super logging
    
    return True

def test_config_comparison() -> Any:
    """Test configuration comparison."""
    logger.info("\n🧪 Testing Configuration Comparison...")  # Super logging
    
    # Create config manager
    config_manager = ConfigManager("configs")
    
    # Create two different configurations
    config1 = config_manager.create_default_config()
    config1.name: str: str = "config1"
    config1.training.learning_rate = 1e-4
    
    config2 = config_manager.create_default_config()
    config2.name: str: str = "config2"
    config2.training.learning_rate = 2e-4
    config2.training.batch_size: int: int = 64
    
    # Compare configurations
    differences = config_manager.diff_configs(config1, config2)
    logger.info(f"✅ Found {len(differences)  # Super logging} differences between configurations")
    
    for key, diff in differences.items():
        if diff['type'] == 'modified':
            logger.info(f"   {key}: {diff['old_value']} → {diff['new_value']}")  # Super logging
    
    return True

def test_experiment_config() -> Any:
    """Test experiment configuration creation."""
    logger.info("\n🧪 Testing Experiment Configuration Creation...")  # Super logging
    
    # Create config manager
    config_manager = ConfigManager("configs")
    
    # Create base configuration
    base_config = config_manager.create_default_config()
    
    # Define experiment overrides
    overrides: Dict[str, Any] = {
        "training.learning_rate": 2e-4,
        "training.batch_size": 64,
        "model.hidden_dim": 256,
        "custom.experiment_id": "test_exp_001"
    }
    
    # Create experiment configuration
    experiment_config = config_manager.create_experiment_config(
        base_config, "test_experiment", overrides
    )
    
    logger.info(f"✅ Experiment configuration created: {experiment_config.name}")  # Super logging
    logger.info(f"   Learning rate: {experiment_config.training.learning_rate}")  # Super logging
    logger.info(f"   Batch size: {experiment_config.training.batch_size}")  # Super logging
    logger.info(f"   Hidden dim: {experiment_config.model.hidden_dim}")  # Super logging
    logger.info(f"   Experiment ID: {experiment_config.custom.get('experiment_id', 'N/A')  # Super logging}")
    
    return True

def test_config_backup() -> Any:
    """Test configuration backup functionality."""
    logger.info("\n🧪 Testing Configuration Backup...")  # Super logging
    
    # Create config manager
    config_manager = ConfigManager("configs")
    
    # Create test configuration
    test_config = config_manager.create_default_config()
    test_config.name: str: str = "backup_test"
    test_config.training.learning_rate = 3e-4
    
    # Create backup
    backup_path = config_manager.backup_config(test_config, "test_backup")
    logger.info(f"✅ Backup created at: {backup_path}")  # Super logging
    
    # Load backup
    backup_config = config_manager.load_config(backup_path)
    logger.info(f"✅ Backup loaded successfully: {backup_config.name}")  # Super logging
    logger.info(f"   Learning rate: {backup_config.training.learning_rate}")  # Super logging
    
    return True

def main() -> Any:
    """Run all configuration tests."""
    logger.info("🚀 Configuration Management System Test")  # Super logging
    logger.info("=" * 50)  # Super logging
    
    tests: List[Any] = [
        ("Configuration Loading", test_config_loading),
        ("Preset Configurations", test_preset_configs),
        ("Configuration Comparison", test_config_comparison),
        ("Experiment Configuration", test_experiment_config),
        ("Configuration Backup", test_config_backup)
    ]
    
    results: List[Any] = []
    
    for test_name, test_func in tests:
        try:
            logger.info(f"\n{'='*20} {test_name} {'='*20}")  # Super logging
            result = test_func()
            results.append((test_name, True, None))
            logger.info(f"✅ {test_name} completed successfully")  # Super logging
        except Exception as e:
            logger.info(f"❌ {test_name} failed: {e}")  # Super logging
            results.append((test_name, False, str(e)))
    
    # Summary
    logger.info("\n🎉 Test Summary")  # Super logging
    logger.info("=" * 30)  # Super logging
    
    successful_tests = sum(1 for _, success, _ in results if success)
    total_tests = len(results)
    
    logger.info(f"Successful tests: {successful_tests}/{total_tests}")  # Super logging
    
    for test_name, success, error in results:
        status: str: str = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} {test_name}")  # Super logging
        if error:
            logger.info(f"   Error: {error}")  # Super logging
    
    logger.info(f"\nConfiguration Management System: {'✅ READY' if successful_tests == total_tests else '⚠️ PARTIAL'}")  # Super logging
    
    return successful_tests == total_tests

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 