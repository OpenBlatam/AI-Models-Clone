"""
🧪 Unit Tests for ADS Training System

Tests for the training system including trainers, models, and training workflows
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
import asyncio

# Import training components
from training.base_trainer import BaseTrainer, TrainingConfig, TrainingResult
from training.model_trainer import ModelTrainer
from training.data_trainer import DataTrainer
from training.performance_trainer import PerformanceTrainer


class TestTrainingConfig:
    """Test cases for TrainingConfig."""
    
    def test_training_config_creation(self):
        """Test training config creation."""
        config = TrainingConfig(
            model_name="test_model",
            batch_size=32,
            learning_rate=0.001,
            epochs=100,
            validation_split=0.2
        )
        
        assert config.model_name == "test_model"
        assert config.batch_size == 32
        assert config.learning_rate == 0.001
        assert config.epochs == 100
        assert config.validation_split == 0.2
    
    def test_training_config_defaults(self):
        """Test training config with default values."""
        config = TrainingConfig()
        
        assert config.model_name == "default_model"
        assert config.batch_size == 16
        assert config.learning_rate == 0.01
        assert config.epochs == 50
        assert config.validation_split == 0.1


class TestTrainingResult:
    """Test cases for TrainingResult."""
    
    def test_training_result_creation(self):
        """Test training result creation."""
        result = TrainingResult(
            model_name="test_model",
            accuracy=0.95,
            loss=0.05,
            training_time=120.5,
            epochs_completed=100,
            status="completed"
        )
        
        assert result.model_name == "test_model"
        assert result.accuracy == 0.95
        assert result.loss == 0.05
        assert result.training_time == 120.5
        assert result.epochs_completed == 100
        assert result.status == "completed"
    
    def test_training_result_to_dict(self):
        """Test training result serialization."""
        result = TrainingResult(
            model_name="test_model",
            accuracy=0.95,
            loss=0.05,
            training_time=120.5
        )
        
        result_dict = result.to_dict()
        
        assert "model_name" in result_dict
        assert "accuracy" in result_dict
        assert "loss" in result_dict
        assert "training_time" in result_dict
        assert result_dict["model_name"] == "test_model"


class TestBaseTrainer:
    """Test cases for BaseTrainer."""
    
    def test_base_trainer_creation(self):
        """Test base trainer creation."""
        trainer = BaseTrainer("Test Trainer")
        
        assert trainer.name == "Test Trainer"
        assert trainer.training_history == []
        assert trainer.current_config is None
    
    def test_base_trainer_set_config(self):
        """Test setting training configuration."""
        trainer = BaseTrainer("Test Trainer")
        config = TrainingConfig(model_name="test_model")
        
        trainer.set_config(config)
        
        assert trainer.current_config == config
    
    def test_base_trainer_add_to_history(self):
        """Test adding results to training history."""
        trainer = BaseTrainer("Test Trainer")
        result = TrainingResult(model_name="test_model")
        
        trainer.add_to_history(result)
        
        assert len(trainer.training_history) == 1
        assert trainer.training_history[0] == result
    
    def test_base_trainer_get_training_stats(self):
        """Test getting training statistics."""
        trainer = BaseTrainer("Test Trainer")
        
        # Add some results to history
        result1 = TrainingResult(model_name="model1", accuracy=0.9, training_time=100)
        result2 = TrainingResult(model_name="model2", accuracy=0.95, training_time=150)
        
        trainer.add_to_history(result1)
        trainer.add_to_history(result2)
        
        stats = trainer.get_training_stats()
        
        assert stats["total_trainings"] == 2
        assert stats["average_accuracy"] == 0.925
        assert stats["total_training_time"] == 250
        assert stats["best_accuracy"] == 0.95


class TestModelTrainer:
    """Test cases for ModelTrainer."""
    
    def test_model_trainer_creation(self):
        """Test model trainer creation."""
        trainer = ModelTrainer("Test Model Trainer")
        
        assert trainer.name == "Test Model Trainer"
        assert trainer.model_type == "generic"
    
    def test_model_trainer_set_model_type(self):
        """Test setting model type."""
        trainer = ModelTrainer("Test Model Trainer")
        
        trainer.set_model_type("transformer")
        assert trainer.model_type == "transformer"
    
    @pytest.mark.asyncio
    async def test_model_trainer_train(self):
        """Test model training execution."""
        trainer = ModelTrainer("Test Model Trainer")
        config = TrainingConfig(model_name="test_model")
        
        # Mock the training process
        with patch.object(trainer, '_execute_training') as mock_execute:
            mock_execute.return_value = TrainingResult(
                model_name="test_model",
                accuracy=0.95,
                loss=0.05,
                training_time=120.0
            )
            
            result = await trainer.train(config)
            
            assert result is not None
            assert result.model_name == "test_model"
            assert result.accuracy == 0.95
            assert result.status == "completed"
    
    def test_model_trainer_validate_config(self):
        """Test configuration validation."""
        trainer = ModelTrainer("Test Model Trainer")
        
        # Valid config
        valid_config = TrainingConfig(
            model_name="test_model",
            batch_size=32,
            learning_rate=0.001,
            epochs=100
        )
        assert trainer.validate_config(valid_config) is True
        
        # Invalid config (negative learning rate)
        invalid_config = TrainingConfig(
            model_name="test_model",
            learning_rate=-0.001
        )
        assert trainer.validate_config(invalid_config) is False


class TestDataTrainer:
    """Test cases for DataTrainer."""
    
    def test_data_trainer_creation(self):
        """Test data trainer creation."""
        trainer = DataTrainer("Test Data Trainer")
        
        assert trainer.name == "Test Data Trainer"
        assert trainer.data_type == "generic"
    
    def test_data_trainer_set_data_type(self):
        """Test setting data type."""
        trainer = DataTrainer("Test Data Trainer")
        
        trainer.set_data_type("text")
        assert trainer.data_type == "text"
    
    def test_data_trainer_preprocess_data(self):
        """Test data preprocessing."""
        trainer = DataTrainer("Test Data Trainer")
        
        # Mock data
        raw_data = ["sample1", "sample2", "sample3"]
        
        processed_data = trainer.preprocess_data(raw_data)
        
        assert processed_data is not None
        assert len(processed_data) == len(raw_data)
    
    @pytest.mark.asyncio
    async def test_data_trainer_train(self):
        """Test data training execution."""
        trainer = DataTrainer("Test Data Trainer")
        config = TrainingConfig(model_name="data_model")
        
        # Mock the training process
        with patch.object(trainer, '_execute_training') as mock_execute:
            mock_execute.return_value = TrainingResult(
                model_name="data_model",
                accuracy=0.92,
                loss=0.08,
                training_time=90.0
            )
            
            result = await trainer.train(config)
            
            assert result is not None
            assert result.model_name == "data_model"
            assert result.accuracy == 0.92


class TestPerformanceTrainer:
    """Test cases for PerformanceTrainer."""
    
    def test_performance_trainer_creation(self):
        """Test performance trainer creation."""
        trainer = PerformanceTrainer("Test Performance Trainer")
        
        assert trainer.name == "Test Performance Trainer"
        assert trainer.performance_metrics == []
    
    def test_performance_trainer_add_metric(self):
        """Test adding performance metrics."""
        trainer = PerformanceTrainer("Test Performance Trainer")
        
        metric = {"name": "accuracy", "value": 0.95, "timestamp": datetime.now(timezone.utc)}
        trainer.add_metric(metric)
        
        assert len(trainer.performance_metrics) == 1
        assert trainer.performance_metrics[0] == metric
    
    def test_performance_trainer_get_performance_summary(self):
        """Test getting performance summary."""
        trainer = PerformanceTrainer("Test Performance Trainer")
        
        # Add some metrics
        trainer.add_metric({"name": "accuracy", "value": 0.9, "timestamp": datetime.now(timezone.utc)})
        trainer.add_metric({"name": "accuracy", "value": 0.95, "timestamp": datetime.now(timezone.utc)})
        trainer.add_metric({"name": "loss", "value": 0.1, "timestamp": datetime.now(timezone.utc)})
        
        summary = trainer.get_performance_summary()
        
        assert "accuracy" in summary
        assert "loss" in summary
        assert summary["accuracy"]["average"] == 0.925
        assert summary["accuracy"]["best"] == 0.95
        assert summary["accuracy"]["worst"] == 0.9
    
    @pytest.mark.asyncio
    async def test_performance_trainer_train(self):
        """Test performance training execution."""
        trainer = PerformanceTrainer("Test Performance Trainer")
        config = TrainingConfig(model_name="perf_model")
        
        # Mock the training process
        with patch.object(trainer, '_execute_training') as mock_execute:
            mock_execute.return_value = TrainingResult(
                model_name="perf_model",
                accuracy=0.98,
                loss=0.02,
                training_time=200.0
            )
            
            result = await trainer.train(config)
            
            assert result is not None
            assert result.model_name == "perf_model"
            assert result.accuracy == 0.98


class TestTrainingSystemIntegration:
    """Integration tests for training system."""
    
    @pytest.mark.asyncio
    async def test_complete_training_workflow(self):
        """Test complete training workflow."""
        # Create trainers
        model_trainer = ModelTrainer("Integration Model Trainer")
        data_trainer = DataTrainer("Integration Data Trainer")
        perf_trainer = PerformanceTrainer("Integration Performance Trainer")
        
        # Create config
        config = TrainingConfig(
            model_name="integration_model",
            batch_size=64,
            learning_rate=0.001,
            epochs=200
        )
        
        # Execute training with each trainer
        model_result = await model_trainer.train(config)
        data_result = await data_trainer.train(config)
        perf_result = await perf_trainer.train(config)
        
        # Verify results
        assert model_result is not None
        assert data_result is not None
        assert perf_result is not None
        
        assert model_result.model_name == "integration_model"
        assert data_result.model_name == "integration_model"
        assert perf_result.model_name == "integration_model"
    
    def test_training_history_tracking(self):
        """Test that training history is properly tracked."""
        trainer = ModelTrainer("History Test Trainer")
        config = TrainingConfig(model_name="history_model")
        
        # Simulate multiple training runs
        for i in range(3):
            result = TrainingResult(
                model_name=f"history_model_v{i}",
                accuracy=0.9 + (i * 0.02),
                loss=0.1 - (i * 0.02),
                training_time=100.0 + (i * 10)
            )
            trainer.add_to_history(result)
        
        # Check history
        assert len(trainer.training_history) == 3
        
        # Check stats
        stats = trainer.get_training_stats()
        assert stats["total_trainings"] == 3
        assert stats["best_accuracy"] == 0.94
        assert stats["total_training_time"] == 330.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

