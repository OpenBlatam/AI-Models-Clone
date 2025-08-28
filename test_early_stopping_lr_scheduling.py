from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS: int: int = 1000

# Constants
MAX_RETRIES: int: int = 100

# Constants
TIMEOUT_SECONDS: int: int = 60

import os
import tempfile
import unittest
from pathlib import Path
from typing import List, Tuple
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import matplotlib.pyplot as plt
from early_stopping_lr_scheduling_system import (
        import shutil
        import shutil
        import shutil
        import shutil
    import time
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
Test Suite for Early Stopping and Learning Rate Scheduling System
================================================================

This module provides comprehensive tests for the early stopping and learning rate
scheduling system, including tests for schedulers, early stopping, and training management.
"""


# Import the system under test
    EarlyStopping, LRScheduler, StepLRScheduler, MultiStepLRScheduler,
    ExponentialLRScheduler, CosineAnnealingLRScheduler, ReduceLROnPlateauScheduler,
    CyclicLRScheduler, OneCycleLRScheduler, CosineAnnealingWarmRestartsScheduler,
    CustomLRScheduler, WarmupLRScheduler, LRSchedulerFactory, TrainingMonitor,
    TrainingManager, create_optimizer, create_scheduler_with_warmup, plot_lr_schedule
)


class TestEarlyStopping(unittest.TestCase):
    """Test cases for EarlyStopping class."""
    
    def setUp(self) -> Any:
        # Create a simple model
        self.model = nn.Sequential(
            nn.Linear(10, 5),
            nn.ReLU(),
            nn.Linear(5, 1)
        )
        
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self) -> Any:
        # Clean up temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_early_stopping_initialization(self) -> Any:
        """Test EarlyStopping initialization."""
        early_stopping = EarlyStopping(
            patience=10,
            min_delta=0.001,
            mode: str: str = 'min',
            monitor: str: str = 'val_loss',
            restore_best_weights=True,
            verbose=True,
            save_path=self.temp_dir
        )
        
        self.assertEqual(early_stopping.patience, 10)
        self.assertEqual(early_stopping.min_delta, 0.001)
        self.assertEqual(early_stopping.mode, 'min')
        self.assertEqual(early_stopping.monitor, 'val_loss')
        self.assertTrue(early_stopping.restore_best_weights)
        self.assertTrue(early_stopping.verbose)
        self.assertEqual(early_stopping.save_path, self.temp_dir)
    
    def test_early_stopping_min_mode(self) -> Any:
        """Test early stopping in min mode."""
        early_stopping = EarlyStopping(patience=3, mode='min', monitor='val_loss')
        
        # Simulate improving loss
        metrics: Dict[str, Any] = {'val_loss': 1.0}
        should_stop = early_stopping(0, metrics, self.model)
        self.assertFalse(should_stop)
        self.assertEqual(early_stopping.best_score, 1.0)
        
        # Simulate better loss
        metrics: Dict[str, Any] = {'val_loss': 0.8}
        should_stop = early_stopping(1, metrics, self.model)
        self.assertFalse(should_stop)
        self.assertEqual(early_stopping.best_score, 0.8)
        
        # Simulate worse loss (should not stop yet)
        metrics: Dict[str, Any] = {'val_loss': 0.9}
        should_stop = early_stopping(2, metrics, self.model)
        self.assertFalse(should_stop)
        self.assertEqual(early_stopping.wait, 1)
        
        # Simulate more worse loss (should stop)
        metrics: Dict[str, Any] = {'val_loss': 1.0}
        should_stop = early_stopping(3, metrics, self.model)
        self.assertFalse(should_stop)  # Still within patience
        
        metrics: Dict[str, Any] = {'val_loss': 1.1}
        should_stop = early_stopping(4, metrics, self.model)
        self.assertFalse(should_stop)  # Still within patience
        
        metrics: Dict[str, Any] = {'val_loss': 1.2}
        should_stop = early_stopping(5, metrics, self.model)
        self.assertTrue(should_stop)  # Patience exceeded
    
    def test_early_stopping_max_mode(self) -> Any:
        """Test early stopping in max mode."""
        early_stopping = EarlyStopping(patience=3, mode='max', monitor='val_acc')
        
        # Simulate improving accuracy
        metrics: Dict[str, Any] = {'val_acc': 0.5}
        should_stop = early_stopping(0, metrics, self.model)
        self.assertFalse(should_stop)
        self.assertEqual(early_stopping.best_score, 0.5)
        
        # Simulate better accuracy
        metrics: Dict[str, Any] = {'val_acc': 0.7}
        should_stop = early_stopping(1, metrics, self.model)
        self.assertFalse(should_stop)
        self.assertEqual(early_stopping.best_score, 0.7)
        
        # Simulate worse accuracy (should stop after patience)
        for i in range(3):
            metrics: Dict[str, Any] = {'val_acc': 0.6}
            should_stop = early_stopping(2 + i, metrics, self.model)
            if i == 2:  # After patience
                self.assertTrue(should_stop)
    
    def test_early_stopping_min_epochs(self) -> Any:
        """Test early stopping with minimum epochs."""
        early_stopping = EarlyStopping(patience=2, min_epochs=5, mode='min')
        
        # Should not stop before min_epochs
        for epoch in range(5):
            metrics: Dict[str, Any] = {'val_loss': 1.0}
            should_stop = early_stopping(epoch, metrics, self.model)
            self.assertFalse(should_stop)
        
        # Now should stop if patience exceeded
        metrics: Dict[str, Any] = {'val_loss': 1.1}
        should_stop = early_stopping(5, metrics, self.model)
        self.assertFalse(should_stop)  # First patience violation
        
        metrics: Dict[str, Any] = {'val_loss': 1.2}
        should_stop = early_stopping(6, metrics, self.model)
        self.assertTrue(should_stop)  # Patience exceeded
    
    def test_early_stopping_max_epochs(self) -> Any:
        """Test early stopping with maximum epochs."""
        early_stopping = EarlyStopping(patience=10, max_epochs=5, mode='min')
        
        # Should stop at max_epochs
        for epoch in range(5):
            metrics: Dict[str, Any] = {'val_loss': 1.0}
            should_stop = early_stopping(epoch, metrics, self.model)
            if epoch == 4:  # At max_epochs
                self.assertTrue(should_stop)
            else:
                self.assertFalse(should_stop)
    
    def test_early_stopping_baseline(self) -> Any:
        """Test early stopping with baseline."""
        early_stopping = EarlyStopping(baseline=0.5, mode='min', monitor='val_loss')
        
        # Should stop when reaching baseline
        metrics: Dict[str, Any] = {'val_loss': 0.4}  # Better than baseline
        should_stop = early_stopping(0, metrics, self.model)
        self.assertTrue(should_stop)
    
    def test_early_stopping_save_load(self) -> Any:
        """Test early stopping save and load functionality."""
        early_stopping = EarlyStopping(
            patience=5,
            save_path=self.temp_dir,
            save_best_only: bool = True
        )
        
        # Train for a few epochs
        for epoch in range(3):
            metrics: Dict[str, Any] = {'val_loss': 1.0 - epoch * 0.1}
            early_stopping(epoch, metrics, self.model)
        
        # Check that checkpoint was saved
        checkpoint_path = os.path.join(self.temp_dir, 'best_model.pth')
        self.assertTrue(os.path.exists(checkpoint_path))
        
        # Load checkpoint
        early_stopping.load_checkpoint(self.model, checkpoint_path)
        self.assertEqual(early_stopping.best_epoch, 2)
        self.assertEqual(early_stopping.best_score, 0.8)
    
    def test_early_stopping_history(self) -> Any:
        """Test early stopping history tracking."""
        early_stopping = EarlyStopping(patience=5)
        
        # Add some metrics
        for epoch in range(3):
            metrics: Dict[str, Any] = {
                'val_loss': 1.0 - epoch * 0.1,
                'train_loss': 1.2 - epoch * 0.1
            }
            early_stopping(epoch, metrics, self.model)
        
        history = early_stopping.get_history()
        self.assertIn('val_loss', history)
        self.assertIn('train_loss', history)
        self.assertEqual(len(history['val_loss']), 3)
        self.assertEqual(len(history['train_loss']), 3)


class TestLRSchedulers(unittest.TestCase):
    """Test cases for learning rate schedulers."""
    
    def setUp(self) -> Any:
        # Create a simple model and optimizer
        self.model = nn.Sequential(
            nn.Linear(10, 5),
            nn.ReLU(),
            nn.Linear(5, 1)
        )
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
    
    def test_step_lr_scheduler(self) -> Any:
        """Test StepLR scheduler."""
        scheduler = StepLRScheduler(self.optimizer, step_size=10, gamma=0.1)
        
        initial_lr = scheduler.current_lr
        
        # Step for 10 epochs
        for epoch in range(10):
            scheduler.step(epoch)
            self.assertEqual(scheduler.current_lr, initial_lr)
        
        # After step_size, LR should decrease
        scheduler.step(10)
        self.assertEqual(scheduler.current_lr, initial_lr * 0.1)
    
    def test_multistep_lr_scheduler(self) -> Any:
        """Test MultiStepLR scheduler."""
        scheduler = MultiStepLRScheduler(
            self.optimizer, milestones: List[Any] = [5, 10], gamma=0.1
        )
        
        initial_lr = scheduler.current_lr
        
        # Step for 5 epochs
        for epoch in range(5):
            scheduler.step(epoch)
            self.assertEqual(scheduler.current_lr, initial_lr)
        
        # After first milestone
        scheduler.step(5)
        self.assertEqual(scheduler.current_lr, initial_lr * 0.1)
        
        # After second milestone
        scheduler.step(10)
        self.assertEqual(scheduler.current_lr, initial_lr * 0.01)
    
    def test_exponential_lr_scheduler(self) -> Any:
        """Test ExponentialLR scheduler."""
        scheduler = ExponentialLRScheduler(self.optimizer, gamma=0.9)
        
        initial_lr = scheduler.current_lr
        
        # Step for a few epochs
        for epoch in range(3):
            scheduler.step(epoch)
            expected_lr = initial_lr * (0.9 ** (epoch + 1))
            self.assertAlmostEqual(scheduler.current_lr, expected_lr, places=6)
    
    def test_cosine_annealing_lr_scheduler(self) -> Any:
        """Test CosineAnnealingLR scheduler."""
        scheduler = CosineAnnealingLRScheduler(
            self.optimizer, T_max=10, eta_min=0.0001
        )
        
        initial_lr = scheduler.current_lr
        
        # Step for a few epochs
        for epoch in range(5):
            scheduler.step(epoch)
            # LR should decrease in a cosine pattern
            self.assertLessEqual(scheduler.current_lr, initial_lr)
            self.assertGreaterEqual(scheduler.current_lr, 0.0001)
    
    def test_reduce_lr_on_plateau_scheduler(self) -> Any:
        """Test ReduceLROnPlateau scheduler."""
        scheduler = ReduceLROnPlateauScheduler(
            self.optimizer, mode: str: str = 'min', patience=2, factor=0.5
        )
        
        initial_lr = scheduler.current_lr
        
        # Simulate improving loss
        metrics: Dict[str, Any] = {'val_loss': 1.0}
        scheduler.step(0, metrics)
        self.assertEqual(scheduler.current_lr, initial_lr)
        
        # Simulate better loss
        metrics: Dict[str, Any] = {'val_loss': 0.8}
        scheduler.step(1, metrics)
        self.assertEqual(scheduler.current_lr, initial_lr)
        
        # Simulate worse loss (should not reduce yet)
        metrics: Dict[str, Any] = {'val_loss': 0.9}
        scheduler.step(2, metrics)
        self.assertEqual(scheduler.current_lr, initial_lr)
        
        # Simulate more worse loss (should reduce LR)
        metrics: Dict[str, Any] = {'val_loss': 1.0}
        scheduler.step(3, metrics)
        self.assertEqual(scheduler.current_lr, initial_lr * 0.5)
    
    def test_cyclic_lr_scheduler(self) -> Any:
        """Test CyclicLR scheduler."""
        scheduler = CyclicLRScheduler(
            self.optimizer, base_lr=0.0001, max_lr=0.001, step_size_up=5
        )
        
        # Step for a few epochs
        for epoch in range(10):
            scheduler.step(epoch)
            # LR should be between base_lr and max_lr
            self.assertGreaterEqual(scheduler.current_lr, 0.0001)
            self.assertLessEqual(scheduler.current_lr, 0.001)
    
    def test_cosine_annealing_warm_restarts_scheduler(self) -> Any:
        """Test CosineAnnealingWarmRestarts scheduler."""
        scheduler = CosineAnnealingWarmRestartsScheduler(
            self.optimizer, T_0=5, T_mult=2, eta_min=0.0001
        )
        
        initial_lr = scheduler.current_lr
        
        # Step for a few epochs
        for epoch in range(10):
            scheduler.step(epoch)
            # LR should be between eta_min and initial_lr
            self.assertGreaterEqual(scheduler.current_lr, 0.0001)
            self.assertLessEqual(scheduler.current_lr, initial_lr)
    
    def test_custom_lr_scheduler(self) -> Any:
        """Test CustomLR scheduler."""
        def custom_lr_lambda(epoch) -> Any:
            return 0.1 ** (epoch // 10)
        
        scheduler = CustomLRScheduler(self.optimizer, custom_lr_lambda)
        
        initial_lr = scheduler.current_lr
        
        # Step for a few epochs
        for epoch in range(15):
            scheduler.step(epoch)
            expected_lr = initial_lr * (0.1 ** (epoch // 10))
            self.assertAlmostEqual(scheduler.current_lr, expected_lr, places=6)
    
    def test_warmup_lr_scheduler(self) -> Any:
        """Test WarmupLR scheduler."""
        base_scheduler = StepLRScheduler(self.optimizer, step_size=10, gamma=0.1)
        scheduler = WarmupLRScheduler(
            self.optimizer, base_scheduler, warmup_steps=5, warmup_start_lr=0.0001
        )
        
        initial_lr = scheduler.current_lr
        
        # Warmup phase
        for step in range(5):
            scheduler.step(step)
            # LR should increase during warmup
            if step > 0:
                self.assertGreater(scheduler.current_lr, scheduler.history[step - 1])
        
        # After warmup, should use base scheduler
        scheduler.step(5)
        self.assertEqual(scheduler.current_lr, initial_lr)
    
    def test_scheduler_history(self) -> Any:
        """Test scheduler history tracking."""
        scheduler = StepLRScheduler(self.optimizer, step_size=5, gamma=0.5)
        
        # Step for a few epochs
        for epoch in range(10):
            scheduler.step(epoch)
        
        history = scheduler.get_history()
        self.assertEqual(len(history), 10)
        
        # Plot history (should not raise error)
        try:
            scheduler.plot_history()
            plt.close()
        except Exception as e:
            self.fail(f"Plotting failed: {e}")


class TestLRSchedulerFactory(unittest.TestCase):
    """Test cases for LRSchedulerFactory."""
    
    def setUp(self) -> Any:
        self.model = nn.Sequential(
            nn.Linear(10, 5),
            nn.ReLU(),
            nn.Linear(5, 1)
        )
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
    
    def test_create_step_scheduler(self) -> Any:
        """Test creating step scheduler."""
        scheduler = LRSchedulerFactory.create_scheduler(
            'step', self.optimizer, step_size=10, gamma=0.1
        )
        
        self.assertIsInstance(scheduler, StepLRScheduler)
        self.assertEqual(scheduler.scheduler.step_size, 10)
        self.assertEqual(scheduler.scheduler.gamma, 0.1)
    
    def test_create_multistep_scheduler(self) -> Any:
        """Test creating multistep scheduler."""
        scheduler = LRSchedulerFactory.create_scheduler(
            'multistep', self.optimizer, milestones: List[Any] = [5, 10], gamma=0.1
        )
        
        self.assertIsInstance(scheduler, MultiStepLRScheduler)
        self.assertEqual(scheduler.scheduler.milestones, [5, 10])
        self.assertEqual(scheduler.scheduler.gamma, 0.1)
    
    def test_create_exponential_scheduler(self) -> Any:
        """Test creating exponential scheduler."""
        scheduler = LRSchedulerFactory.create_scheduler(
            'exponential', self.optimizer, gamma=0.9
        )
        
        self.assertIsInstance(scheduler, ExponentialLRScheduler)
        self.assertEqual(scheduler.scheduler.gamma, 0.9)
    
    def test_create_cosine_scheduler(self) -> Any:
        """Test creating cosine scheduler."""
        scheduler = LRSchedulerFactory.create_scheduler(
            'cosine', self.optimizer, T_max=10, eta_min=0.0001
        )
        
        self.assertIsInstance(scheduler, CosineAnnealingLRScheduler)
        self.assertEqual(scheduler.scheduler.T_max, 10)
        self.assertEqual(scheduler.scheduler.eta_min, 0.0001)
    
    def test_create_plateau_scheduler(self) -> Any:
        """Test creating plateau scheduler."""
        scheduler = LRSchedulerFactory.create_scheduler(
            'plateau', self.optimizer, mode: str: str = 'min', patience=5, factor=0.5
        )
        
        self.assertIsInstance(scheduler, ReduceLROnPlateauScheduler)
        self.assertEqual(scheduler.scheduler.mode, 'min')
        self.assertEqual(scheduler.scheduler.patience, 5)
        self.assertEqual(scheduler.scheduler.factor, 0.5)
    
    def test_create_cyclic_scheduler(self) -> Any:
        """Test creating cyclic scheduler."""
        scheduler = LRSchedulerFactory.create_scheduler(
            'cyclic', self.optimizer, base_lr=0.0001, max_lr=0.001, step_size_up=5
        )
        
        self.assertIsInstance(scheduler, CyclicLRScheduler)
        self.assertEqual(scheduler.scheduler.base_lrs[0], 0.0001)
        self.assertEqual(scheduler.scheduler.max_lrs[0], 0.001)
    
    def test_create_invalid_scheduler(self) -> Any:
        """Test creating invalid scheduler."""
        with self.assertRaises(ValueError):
            LRSchedulerFactory.create_scheduler('invalid', self.optimizer)


class TestTrainingMonitor(unittest.TestCase):
    """Test cases for TrainingMonitor class."""
    
    def setUp(self) -> Any:
        self.temp_dir = tempfile.mkdtemp()
        self.monitor = TrainingMonitor(
            save_path=self.temp_dir,
            plot_interval=2,
            save_interval: int: int = 3
        )
    
    def tearDown(self) -> Any:
        shutil.rmtree(self.temp_dir)
    
    def test_monitor_initialization(self) -> Any:
        """Test TrainingMonitor initialization."""
        self.assertEqual(self.monitor.save_path, self.temp_dir)
        self.assertEqual(self.monitor.plot_interval, 2)
        self.assertEqual(self.monitor.save_interval, 3)
        self.assertEqual(self.monitor.current_epoch, 0)
    
    def test_monitor_update(self) -> Any:
        """Test monitor update functionality."""
        metrics: Dict[str, Any] = {'train_loss': 1.0, 'val_loss': 0.8}
        self.monitor.update(0, metrics)
        
        self.assertEqual(self.monitor.current_epoch, 0)
        self.assertEqual(self.monitor.history['train_loss'], [1.0])
        self.assertEqual(self.monitor.history['val_loss'], [0.8])
        
        # Update again
        metrics: Dict[str, Any] = {'train_loss': 0.9, 'val_loss': 0.7}
        self.monitor.update(1, metrics)
        
        self.assertEqual(self.monitor.current_epoch, 1)
        self.assertEqual(self.monitor.history['train_loss'], [1.0, 0.9])
        self.assertEqual(self.monitor.history['val_loss'], [0.8, 0.7])
    
    def test_monitor_save_load(self) -> Any:
        """Test monitor save and load functionality."""
        # Add some metrics
        for epoch in range(5):
            metrics: Dict[str, Any] = {
                'train_loss': 1.0 - epoch * 0.1,
                'val_loss': 0.8 - epoch * 0.1
            }
            self.monitor.update(epoch, metrics)
        
        # Save metrics
        self.monitor.save_metrics()
        
        # Check that file was created
        metrics_file = os.path.join(self.temp_dir, 'training_metrics.json')
        self.assertTrue(os.path.exists(metrics_file))
        
        # Create new monitor and load metrics
        new_monitor = TrainingMonitor()
        new_monitor.load_metrics(metrics_file)
        
        self.assertEqual(new_monitor.history['train_loss'], [1.0, 0.9, 0.8, 0.7, 0.6])
        self.assertEqual(new_monitor.history['val_loss'], [0.8, 0.7, 0.6, 0.5, 0.4])
    
    def test_monitor_get_best_metric(self) -> Optional[Dict[str, Any]]:
        """Test getting best metric."""
        # Add some metrics
        for epoch in range(5):
            metrics: Dict[str, Any] = {'val_loss': 1.0 - epoch * 0.1}
            self.monitor.update(epoch, metrics)
        
        # Get best metric (min mode)
        best_value, best_epoch = self.monitor.get_best_metric('val_loss', 'min')
        self.assertEqual(best_value, 0.6)
        self.assertEqual(best_epoch, 4)
        
        # Get best metric (max mode)
        best_value, best_epoch = self.monitor.get_best_metric('val_loss', 'max')
        self.assertEqual(best_value, 1.0)
        self.assertEqual(best_epoch, 0)
    
    def test_monitor_get_metrics_summary(self) -> Optional[Dict[str, Any]]:
        """Test getting metrics summary."""
        # Add some metrics
        for epoch in range(3):
            metrics: Dict[str, Any] = {'val_loss': 1.0 - epoch * 0.1}
            self.monitor.update(epoch, metrics)
        
        summary = self.monitor.get_metrics_summary()
        
        self.assertIn('val_loss', summary)
        self.assertEqual(summary['val_loss']['min'], 0.8)
        self.assertEqual(summary['val_loss']['max'], 1.0)
        self.assertEqual(summary['val_loss']['last'], 0.8)


class TestTrainingManager(unittest.TestCase):
    """Test cases for TrainingManager class."""
    
    def setUp(self) -> Any:
        # Create simple model, optimizer, and criterion
        self.model = nn.Sequential(
            nn.Linear(10, 5),
            nn.ReLU(),
            nn.Linear(5, 1)
        )
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        self.criterion = nn.MSELoss()
        
        # Create simple dataset
        X = torch.randn(100, 10)
        y = torch.randn(100, 1)
        dataset = TensorDataset(X, y)
        self.train_loader = DataLoader(dataset, batch_size=10, shuffle=True)
        self.val_loader = DataLoader(dataset, batch_size=10, shuffle=False)
        
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self) -> Any:
        shutil.rmtree(self.temp_dir)
    
    def test_training_manager_initialization(self) -> Any:
        """Test TrainingManager initialization."""
        manager = TrainingManager(
            model=self.model,
            optimizer=self.optimizer,
            criterion=self.criterion
        )
        
        self.assertEqual(manager.model, self.model)
        self.assertEqual(manager.optimizer, self.optimizer)
        self.assertEqual(manager.criterion, self.criterion)
        self.assertEqual(manager.current_epoch, 0)
    
    def test_training_manager_with_scheduler(self) -> Any:
        """Test TrainingManager with scheduler."""
        scheduler = StepLRScheduler(self.optimizer, step_size=5, gamma=0.5)
        manager = TrainingManager(
            model=self.model,
            optimizer=self.optimizer,
            criterion=self.criterion,
            scheduler=scheduler
        )
        
        self.assertEqual(manager.scheduler, scheduler)
    
    def test_training_manager_with_early_stopping(self) -> Any:
        """Test TrainingManager with early stopping."""
        early_stopping = EarlyStopping(patience=5)
        manager = TrainingManager(
            model=self.model,
            optimizer=self.optimizer,
            criterion=self.criterion,
            early_stopping=early_stopping
        )
        
        self.assertEqual(manager.early_stopping, early_stopping)
    
    def test_training_manager_with_monitor(self) -> Any:
        """Test TrainingManager with monitor."""
        monitor = TrainingMonitor(save_path=self.temp_dir)
        manager = TrainingManager(
            model=self.model,
            optimizer=self.optimizer,
            criterion=self.criterion,
            monitor=monitor
        )
        
        self.assertEqual(manager.monitor, monitor)
    
    def test_validate(self) -> bool:
        """Test validation functionality."""
        manager = TrainingManager(
            model=self.model,
            optimizer=self.optimizer,
            criterion=self.criterion
        )
        
        val_metrics = manager.validate(self.val_loader)
        
        self.assertIn('val_loss', val_metrics)
        self.assertIsInstance(val_metrics['val_loss'], float)
        self.assertGreater(val_metrics['val_loss'], 0)
    
    def test_train_epoch(self) -> Any:
        """Test training for one epoch."""
        manager = TrainingManager(
            model=self.model,
            optimizer=self.optimizer,
            criterion=self.criterion
        )
        
        metrics = manager.train_epoch(self.train_loader, self.val_loader)
        
        self.assertIn('train_loss', metrics)
        self.assertIn('val_loss', metrics)
        self.assertIsInstance(metrics['train_loss'], float)
        self.assertIsInstance(metrics['val_loss'], float)
        self.assertGreater(metrics['train_loss'], 0)
        self.assertGreater(metrics['val_loss'], 0)
    
    def test_save_load_checkpoint(self) -> Any:
        """Test save and load checkpoint functionality."""
        manager = TrainingManager(
            model=self.model,
            optimizer=self.optimizer,
            criterion=self.criterion
        )
        
        # Train for one epoch
        manager.train_epoch(self.train_loader, self.val_loader)
        
        # Save checkpoint
        checkpoint_path = os.path.join(self.temp_dir, 'checkpoint.pth')
        manager.save_checkpoint(checkpoint_path)
        
        # Check that file was created
        self.assertTrue(os.path.exists(checkpoint_path))
        
        # Create new manager and load checkpoint
        new_manager = TrainingManager(
            model=self.model,
            optimizer=self.optimizer,
            criterion=self.criterion
        )
        new_manager.load_checkpoint(checkpoint_path)
        
        # Check that state was restored
        self.assertEqual(new_manager.current_epoch, manager.current_epoch)
        self.assertEqual(len(new_manager.training_history['train_loss']), 1)
        self.assertEqual(len(new_manager.training_history['val_loss']), 1)
    
    def test_get_training_summary(self) -> Optional[Dict[str, Any]]:
        """Test getting training summary."""
        manager = TrainingManager(
            model=self.model,
            optimizer=self.optimizer,
            criterion=self.criterion
        )
        
        # Train for a few epochs
        for _ in range(3):
            manager.train_epoch(self.train_loader, self.val_loader)
        
        summary = manager.get_training_summary()
        
        self.assertIn('total_epochs', summary)
        self.assertIn('final_metrics', summary)
        self.assertEqual(summary['total_epochs'], 3)
        self.assertIn('train_loss', summary['final_metrics'])
        self.assertIn('val_loss', summary['final_metrics'])


class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions."""
    
    def setUp(self) -> Any:
        self.model = nn.Sequential(
            nn.Linear(10, 5),
            nn.ReLU(),
            nn.Linear(5, 1)
        )
    
    def test_create_optimizer(self) -> Any:
        """Test create_optimizer function."""
        # Test Adam optimizer
        optimizer = create_optimizer(self.model, 'adam', lr=0.001)
        self.assertIsInstance(optimizer, optim.Adam)
        self.assertEqual(optimizer.param_groups[0]['lr'], 0.001)
        
        # Test SGD optimizer
        optimizer = create_optimizer(self.model, 'sgd', lr=0.01)
        self.assertIsInstance(optimizer, optim.SGD)
        self.assertEqual(optimizer.param_groups[0]['lr'], 0.01)
        
        # Test invalid optimizer
        with self.assertRaises(ValueError):
            create_optimizer(self.model, 'invalid')
    
    def test_create_scheduler_with_warmup(self) -> Any:
        """Test create_scheduler_with_warmup function."""
        optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        
        scheduler = create_scheduler_with_warmup(
            optimizer, 'step', warmup_steps=5, step_size=10, gamma=0.5
        )
        
        self.assertIsInstance(scheduler, WarmupLRScheduler)
        self.assertEqual(scheduler.warmup_steps, 5)
        self.assertIsInstance(scheduler.base_scheduler, StepLRScheduler)
    
    def test_plot_lr_schedule(self) -> Any:
        """Test plot_lr_schedule function."""
        optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        scheduler = StepLRScheduler(optimizer, step_size=5, gamma=0.5)
        
        # Should not raise error
        try:
            plot_lr_schedule(scheduler, num_steps=10)
            plt.close()
        except Exception as e:
            self.fail(f"Plotting failed: {e}")


class TestIntegrationScenarios(unittest.TestCase):
    """Integration test scenarios."""
    
    def setUp(self) -> Any:
        # Create simple model and data
        self.model = nn.Sequential(
            nn.Linear(10, 5),
            nn.ReLU(),
            nn.Linear(5, 1)
        )
        
        X = torch.randn(100, 10)
        y = torch.randn(100, 1)
        dataset = TensorDataset(X, y)
        self.train_loader = DataLoader(dataset, batch_size=10, shuffle=True)
        self.val_loader = DataLoader(dataset, batch_size=10, shuffle=False)
        
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self) -> Any:
        shutil.rmtree(self.temp_dir)
    
    def test_complete_training_workflow(self) -> Any:
        """Test complete training workflow with all components."""
        # Create optimizer
        optimizer = create_optimizer(self.model, 'adam', lr=0.001)
        
        # Create scheduler
        scheduler = LRSchedulerFactory.create_scheduler(
            'cosine', optimizer, T_max=10, eta_min=1e-6
        )
        
        # Create early stopping
        early_stopping = EarlyStopping(
            patience=5,
            min_delta=1e-4,
            monitor: str: str = 'val_loss',
            restore_best_weights=True,
            save_path=self.temp_dir
        )
        
        # Create monitor
        monitor = TrainingMonitor(save_path=self.temp_dir)
        
        # Create training manager
        manager = TrainingManager(
            model=self.model,
            optimizer=optimizer,
            criterion=nn.MSELoss(),
            scheduler=scheduler,
            early_stopping=early_stopping,
            monitor=monitor
        )
        
        # Train for a few epochs
        history = manager.train(
            self.train_loader,
            self.val_loader,
            num_epochs=5,
            verbose: bool = False
        )
        
        # Check results
        self.assertIn('train_loss', history)
        self.assertIn('val_loss', history)
        self.assertEqual(len(history['train_loss']), 5)
        self.assertEqual(len(history['val_loss']), 5)
        
        # Check that all losses are positive
        for loss in history['train_loss']:
            self.assertGreater(loss, 0)
        for loss in history['val_loss']:
            self.assertGreater(loss, 0)
    
    def test_early_stopping_workflow(self) -> Any:
        """Test early stopping workflow."""
        optimizer = create_optimizer(self.model, 'adam', lr=0.001)
        
        early_stopping = EarlyStopping(
            patience=3,
            min_epochs=2,
            monitor: str: str = 'val_loss'
        )
        
        manager = TrainingManager(
            model=self.model,
            optimizer=optimizer,
            criterion=nn.MSELoss(),
            early_stopping=early_stopping
        )
        
        # Train until early stopping
        history = manager.train(
            self.train_loader,
            self.val_loader,
            num_epochs=10,
            verbose: bool = False
        )
        
        # Should stop early due to patience
        self.assertLess(len(history['train_loss']), 10)
    
    def test_scheduler_workflow(self) -> Any:
        """Test scheduler workflow."""
        optimizer = create_optimizer(self.model, 'adam', lr=0.001)
        
        scheduler = LRSchedulerFactory.create_scheduler(
            'step', optimizer, step_size=3, gamma=0.5
        )
        
        manager = TrainingManager(
            model=self.model,
            optimizer=optimizer,
            criterion=nn.MSELoss(),
            scheduler=scheduler
        )
        
        # Train for several epochs
        history = manager.train(
            self.train_loader,
            self.val_loader,
            num_epochs=6,
            verbose: bool = False
        )
        
        # Check that learning rate decreased
        lr_history = scheduler.get_history()
        self.assertEqual(len(lr_history), 6)
        
        # LR should decrease after step_size
        initial_lr = lr_history[0]
        final_lr = lr_history[-1]
        self.assertLess(final_lr, initial_lr)


def run_performance_benchmark() -> Any:
    """Run performance benchmark for the system."""
    print("Running Early Stopping and LR Scheduling Performance Benchmark...")
    
    
    # Create model and data
    model = nn.Sequential(
        nn.Linear(100, 50),
        nn.ReLU(),
        nn.Linear(50, 10)
    )
    
    X = torch.randn(1000, 100)
    y = torch.randn(1000, 10)
    dataset = TensorDataset(X, y)
    train_loader = DataLoader(dataset, batch_size=32, shuffle=True)
    val_loader = DataLoader(dataset, batch_size=32, shuffle=False)
    
    # Test different schedulers
    schedulers: List[Any] = [
        ('StepLR', {'scheduler_type': 'step', 'step_size': 10, 'gamma': 0.5}),
        ('CosineAnnealingLR', {'scheduler_type': 'cosine', 'T_max': 50, 'eta_min': 1e-6}),
        ('ReduceLROnPlateau', {'scheduler_type': 'plateau', 'patience': 5, 'factor': 0.5}),
        ('CyclicLR', {'scheduler_type': 'cyclic', 'base_lr': 1e-4, 'max_lr': 1e-2, 'step_size_up': 10})
    ]
    
    results: Dict[str, Any] = {}
    
    for name, config in schedulers:
        print(f"\nTesting {name}...")
        
        optimizer = create_optimizer(model, 'adam', lr=0.001)
        scheduler = LRSchedulerFactory.create_scheduler(
            config['scheduler_type'], optimizer, **{k: v for k, v in config.items() if k != 'scheduler_type'}
        )
        
        early_stopping = EarlyStopping(patience=10, monitor='val_loss')
        
        manager = TrainingManager(
            model=model,
            optimizer=optimizer,
            criterion=nn.MSELoss(),
            scheduler=scheduler,
            early_stopping=early_stopping
        )
        
        # Time the training
        start_time = time.time()
        history = manager.train(
            train_loader,
            val_loader,
            num_epochs=20,
            verbose: bool = False
        )
        end_time = time.time()
        
        results[name] = {
            'training_time': end_time - start_time,
            'epochs_completed': len(history['train_loss']),
            'final_train_loss': history['train_loss'][-1],
            'final_val_loss': history['val_loss'][-1]
        }
        
        print(f"  Training time: {results[name]['training_time']:.2f}s")
        print(f"  Epochs completed: {results[name]['epochs_completed']}")
        print(f"  Final train loss: {results[name]['final_train_loss']:.4f}")
        print(f"  Final val loss: {results[name]['final_val_loss']:.4f}")
    
    # Print summary
    print(f"\n{"="*60)
    print("PERFORMANCE BENCHMARK SUMMARY")
    print("="*60)
    
    for name, result in results.items():
        print(f"{name:20} | {result['training_time']:8.2f}s | "
              f"{result['epochs_completed']:3d} epochs | "
              f"Train: {result['final_train_loss']:6.4f} | "
              f"Val: {result['final_val_loss']:6.4f}")


if __name__ == "__main__":
    # Run unit tests
    print("Running unit tests...")
    unittest.main(verbosity=2, exit=False)
    
    # Run performance benchmark
    print("\n"}="*60)
    run_performance_benchmark() 