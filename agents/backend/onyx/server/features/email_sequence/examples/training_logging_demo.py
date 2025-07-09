"""
Training Logging System Demonstration

This example demonstrates the comprehensive training logging system
for tracking training progress, errors, and performance metrics.
"""

import asyncio
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
import random
import time
from pathlib import Path
import sys

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from core.training_logger import (
    TrainingLogger, TrainingEventType, LogLevel, 
    create_training_logger, load_training_logs, analyze_training_logs
)
from core.enhanced_training_optimizer import (
    EnhancedTrainingOptimizer, create_enhanced_training_optimizer,
    train_model_with_logging
)
from core.error_handling import ErrorHandler, ModelError


class TrainingLoggingDemo:
    """Demonstration of the training logging system"""
    
    def __init__(self):
        """Initialize the demo"""
        
        print("🚀 Initializing Training Logging Demo...")
        
        # Set random seeds for reproducibility
        torch.manual_seed(42)
        np.random.seed(42)
        random.seed(42)
        
        # Create demo data and model
        self.train_loader, self.val_loader = self._create_demo_data()
        self.model = self._create_demo_model()
        
        # Initialize logging components
        self.logger = create_training_logger(
            experiment_name="demo_training",
            log_dir="demo_logs",
            log_level="DEBUG",
            enable_visualization=True,
            enable_metrics_logging=True
        )
        
        self.error_handler = ErrorHandler(debug_mode=True)
        
        print("✅ Training logging demo initialized successfully!")
    
    def _create_demo_data(self):
        """Create demo training and validation data"""
        
        print("📊 Creating demo dataset...")
        
        # Generate synthetic data
        num_samples = 1000
        input_size = 20
        num_classes = 3
        
        # Training data
        X_train = torch.randn(num_samples, input_size)
        y_train = torch.randint(0, num_classes, (num_samples,))
        
        # Validation data
        X_val = torch.randn(num_samples // 4, input_size)
        y_val = torch.randint(0, num_classes, (num_samples // 4,))
        
        # Create data loaders
        train_dataset = TensorDataset(X_train, y_train)
        val_dataset = TensorDataset(X_val, y_val)
        
        train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)
        
        print(f"  ✅ Created dataset: {len(train_dataset)} training, {len(val_dataset)} validation samples")
        
        return train_loader, val_loader
    
    def _create_demo_model(self):
        """Create a demo neural network model"""
        
        print("🧠 Creating demo model...")
        
        class DemoModel(nn.Module):
            def __init__(self, input_size=20, hidden_size=64, num_classes=3):
                super().__init__()
                self.layers = nn.Sequential(
                    nn.Linear(input_size, hidden_size),
                    nn.ReLU(),
                    nn.Dropout(0.2),
                    nn.Linear(hidden_size, hidden_size // 2),
                    nn.ReLU(),
                    nn.Dropout(0.2),
                    nn.Linear(hidden_size // 2, num_classes)
                )
                self.loss_fn = nn.CrossEntropyLoss()
            
            def forward(self, x):
                return self.layers(x)
        
        model = DemoModel()
        print(f"  ✅ Created model with {sum(p.numel() for p in model.parameters())} parameters")
        
        return model
    
    def demo_basic_logging(self):
        """Demonstrate basic logging functionality"""
        
        print("\n" + "="*60)
        print("📝 BASIC LOGGING DEMONSTRATION")
        print("="*60)
        
        # Test different log levels
        self.logger.log_debug("This is a debug message")
        self.logger.log_info("This is an info message")
        self.logger.log_warning("This is a warning message")
        self.logger.log_error("This is an error message")
        
        # Test event logging
        self.logger._log_event(
            TrainingEventType.CONFIG_CHANGE,
            LogLevel.INFO,
            "Configuration updated",
            {"learning_rate": 0.001, "batch_size": 32}
        )
        
        # Test metric logging
        self.logger.log_metric_update("loss", 0.5, step=1)
        self.logger.log_metric_update("accuracy", 0.85, step=1)
        
        print("✅ Basic logging demonstration completed")
    
    def demo_training_session(self):
        """Demonstrate a complete training session with logging"""
        
        print("\n" + "="*60)
        print("🏋️ TRAINING SESSION DEMONSTRATION")
        print("="*60)
        
        # Start training session
        self.logger.start_training(
            total_epochs=5,
            total_batches=len(self.train_loader),
            config={
                "learning_rate": 0.001,
                "batch_size": 32,
                "model_type": "DemoModel",
                "optimizer": "AdamW"
            }
        )
        
        # Simulate training epochs
        for epoch in range(5):
            self.logger.start_epoch(epoch, len(self.train_loader))
            
            epoch_loss = 0.0
            epoch_accuracy = 0.0
            num_batches = 0
            
            # Simulate training batches
            for batch in range(len(self.train_loader)):
                self.logger.start_batch(batch, len(self.train_loader))
                
                # Simulate batch training
                batch_loss = 1.0 / (epoch + 1) + np.random.normal(0, 0.1)
                batch_accuracy = 0.6 + epoch * 0.08 + np.random.normal(0, 0.05)
                
                batch_metrics = {
                    "loss": batch_loss,
                    "accuracy": batch_accuracy,
                    "learning_rate": 0.001 / (epoch + 1),
                    "gradient_norm": np.random.uniform(0.1, 2.0),
                    "memory_usage": np.random.uniform(0.3, 0.8),
                    "gpu_usage": np.random.uniform(0.2, 0.7) if torch.cuda.is_available() else 0.0
                }
                
                self.logger.end_batch(batch_metrics)
                
                epoch_loss += batch_loss
                epoch_accuracy += batch_accuracy
                num_batches += 1
            
            # Simulate validation
            val_loss = epoch_loss / num_batches * 1.1
            val_accuracy = epoch_accuracy / num_batches * 0.95
            
            validation_metrics = {
                "validation_loss": val_loss,
                "validation_accuracy": val_accuracy
            }
            
            self.logger.log_validation(validation_metrics)
            
            # End epoch
            epoch_metrics = {
                "loss": epoch_loss / num_batches,
                "accuracy": epoch_accuracy / num_batches,
                "validation_loss": val_loss,
                "validation_accuracy": val_accuracy,
                "learning_rate": 0.001 / (epoch + 1)
            }
            
            self.logger.end_epoch(epoch_metrics)
            
            # Simulate checkpoint saving
            if epoch % 2 == 0:
                self.logger.log_checkpoint(
                    f"checkpoint_epoch_{epoch}.pth",
                    epoch_metrics
                )
            
            # Simulate learning rate change
            if epoch == 2:
                self.logger.log_learning_rate_change(
                    0.001, 0.0005, "Reducing learning rate"
                )
        
        # End training
        final_metrics = {
            "final_loss": epoch_metrics["loss"],
            "final_accuracy": epoch_metrics["accuracy"],
            "final_validation_loss": epoch_metrics["validation_loss"],
            "final_validation_accuracy": epoch_metrics["validation_accuracy"]
        }
        
        self.logger.end_training(final_metrics)
        
        print("✅ Training session demonstration completed")
    
    def demo_error_handling(self):
        """Demonstrate error handling and logging"""
        
        print("\n" + "="*60)
        print("⚠️ ERROR HANDLING DEMONSTRATION")
        print("="*60)
        
        # Simulate different types of errors
        error_scenarios = [
            ("ValueError", ValueError("Invalid input parameter")),
            ("RuntimeError", RuntimeError("CUDA out of memory")),
            ("FileNotFoundError", FileNotFoundError("Model checkpoint not found")),
            ("TypeError", TypeError("Incompatible tensor types")),
        ]
        
        for error_type, error in error_scenarios:
            print(f"  Simulating {error_type}...")
            self.logger.log_error(error, f"Demo context for {error_type}", "demo_operation")
        
        # Simulate warnings
        warning_messages = [
            "Learning rate might be too high",
            "Gradient norm is getting large",
            "Validation loss is not improving",
            "Memory usage is high"
        ]
        
        for warning in warning_messages:
            self.logger.log_warning(warning, "Training monitoring")
        
        # Simulate critical error
        critical_error = RuntimeError("Critical: Model weights corrupted")
        self.logger.log_error(critical_error, "Model loading", "load_model", level=LogLevel.CRITICAL)
        
        print("✅ Error handling demonstration completed")
    
    def demo_enhanced_training_optimizer(self):
        """Demonstrate the enhanced training optimizer with logging"""
        
        print("\n" + "="*60)
        print("🚀 ENHANCED TRAINING OPTIMIZER DEMONSTRATION")
        print("="*60)
        
        try:
            # Create enhanced training optimizer
            optimizer = create_enhanced_training_optimizer(
                model=self.model,
                train_loader=self.train_loader,
                val_loader=self.val_loader,
                experiment_name="demo_enhanced_training",
                log_dir="demo_enhanced_logs",
                log_level="DEBUG",
                max_epochs=3,
                learning_rate=0.001,
                batch_size=32,
                early_stopping_patience=5,
                gradient_clip=1.0
            )
            
            print("✅ Enhanced training optimizer created")
            
            # Run training
            print("🏋️ Starting enhanced training...")
            results = asyncio.run(optimizer.train())
            
            print(f"✅ Training completed with results: {results}")
            
            # Get training summary
            summary = optimizer.get_training_summary()
            print(f"📊 Training summary: {summary}")
            
            # Create visualizations
            optimizer.create_training_visualizations()
            
            # Cleanup
            optimizer.cleanup()
            
        except Exception as e:
            print(f"❌ Enhanced training failed: {e}")
            self.logger.log_error(e, "Enhanced training", "demo_enhanced_training_optimizer")
    
    def demo_log_analysis(self):
        """Demonstrate log analysis and insights"""
        
        print("\n" + "="*60)
        print("📊 LOG ANALYSIS DEMONSTRATION")
        print("="*60)
        
        try:
            # Get error summary
            error_summary = self.logger.get_error_summary()
            print(f"📈 Error Summary: {error_summary}")
            
            # Get training summary
            training_summary = self.logger.get_training_summary()
            print(f"📊 Training Summary: {training_summary}")
            
            # Analyze log files if they exist
            events_file = Path("demo_logs/demo_training_events.jsonl")
            if events_file.exists():
                print("📖 Loading and analyzing training events...")
                events = load_training_logs(str(events_file))
                analysis = analyze_training_logs(events)
                
                print(f"📊 Log Analysis Results:")
                print(f"  Total events: {analysis['total_events']}")
                print(f"  Event types: {analysis['event_types']}")
                print(f"  Total errors: {analysis['error_analysis']['total_errors']}")
                print(f"  Critical errors: {analysis['error_analysis']['critical_errors']}")
                
                if 'performance_analysis' in analysis:
                    print(f"  Total epochs: {analysis['performance_analysis'].get('total_epochs', 'N/A')}")
                    print(f"  Avg epoch duration: {analysis['performance_analysis'].get('avg_epoch_duration', 'N/A')}")
            
            # Create visualizations
            self.logger.create_visualizations()
            
        except Exception as e:
            print(f"❌ Log analysis failed: {e}")
            self.logger.log_error(e, "Log analysis", "demo_log_analysis")
    
    def demo_context_managers(self):
        """Demonstrate context managers for training"""
        
        print("\n" + "="*60)
        print("🎭 CONTEXT MANAGERS DEMONSTRATION")
        print("="*60)
        
        # Training context
        with self.logger.training_context(3, {"demo": True}):
            print("  📝 Training session started")
            
            # Epoch context
            with self.logger.epoch_context(0, 10):
                print("    📊 Epoch 0 started")
                
                # Batch context
                with self.logger.batch_context(0, 10):
                    print("      🔄 Batch 0 processing")
                    time.sleep(0.1)  # Simulate processing
                    print("      ✅ Batch 0 completed")
                
                print("    ✅ Epoch 0 completed")
            
            print("  ✅ Training session completed")
        
        print("✅ Context managers demonstration completed")
    
    def demo_resource_monitoring(self):
        """Demonstrate resource monitoring"""
        
        print("\n" + "="*60)
        print("💻 RESOURCE MONITORING DEMONSTRATION")
        print("="*60)
        
        # Simulate resource monitoring during training
        for i in range(5):
            # Simulate resource usage
            memory_usage = np.random.uniform(0.3, 0.9)
            gpu_usage = np.random.uniform(0.2, 0.8) if torch.cuda.is_available() else 0.0
            cpu_usage = np.random.uniform(0.1, 0.7)
            
            self.logger.log_resource_usage(memory_usage, gpu_usage, cpu_usage)
            
            print(f"  📊 Step {i}: Memory={memory_usage:.2f}, GPU={gpu_usage:.2f}, CPU={cpu_usage:.2f}")
            time.sleep(0.2)
        
        print("✅ Resource monitoring demonstration completed")
    
    def demo_performance_tracking(self):
        """Demonstrate performance tracking"""
        
        print("\n" + "="*60)
        print("⚡ PERFORMANCE TRACKING DEMONSTRATION")
        print("="*60)
        
        # Simulate performance metrics
        for step in range(10):
            # Simulate gradient updates
            gradient_norm = np.random.uniform(0.1, 3.0)
            self.logger.log_gradient_update(gradient_norm, clip_threshold=1.0)
            
            # Simulate metric updates
            loss = 1.0 / (step + 1) + np.random.normal(0, 0.1)
            accuracy = 0.5 + step * 0.05 + np.random.normal(0, 0.02)
            
            self.logger.log_metric_update("loss", loss, step)
            self.logger.log_metric_update("accuracy", accuracy, step)
            
            print(f"  📈 Step {step}: Loss={loss:.4f}, Accuracy={accuracy:.4f}, GradNorm={gradient_norm:.4f}")
        
        print("✅ Performance tracking demonstration completed")
    
    def run_full_demo(self):
        """Run the complete training logging demonstration"""
        
        print("🚀 TRAINING LOGGING SYSTEM DEMONSTRATION")
        print("="*80)
        
        try:
            # Run all demo sections
            self.demo_basic_logging()
            self.demo_training_session()
            self.demo_error_handling()
            self.demo_context_managers()
            self.demo_resource_monitoring()
            self.demo_performance_tracking()
            self.demo_enhanced_training_optimizer()
            self.demo_log_analysis()
            
            print("\n" + "="*80)
            print("✅ TRAINING LOGGING DEMONSTRATION COMPLETED SUCCESSFULLY!")
            print("="*80)
            
            # Final summary
            print("\n📊 DEMONSTRATION SUMMARY:")
            print("  • Basic logging functionality")
            print("  • Complete training session tracking")
            print("  • Error handling and reporting")
            print("  • Context managers for structured logging")
            print("  • Resource monitoring")
            print("  • Performance tracking")
            print("  • Enhanced training optimizer integration")
            print("  • Log analysis and insights")
            print("  • Visualization generation")
            
            # Show log files created
            log_dir = Path("demo_logs")
            if log_dir.exists():
                print(f"\n📁 Log files created in: {log_dir.absolute()}")
                for log_file in log_dir.glob("*"):
                    print(f"  • {log_file.name}")
            
            enhanced_log_dir = Path("demo_enhanced_logs")
            if enhanced_log_dir.exists():
                print(f"\n📁 Enhanced training logs in: {enhanced_log_dir.absolute()}")
                for log_file in enhanced_log_dir.glob("*"):
                    print(f"  • {log_file.name}")
            
        except Exception as e:
            print(f"\n❌ Demo failed with error: {e}")
            self.logger.log_error(e, "Demo execution", "run_full_demo")
        
        finally:
            # Cleanup
            self.logger.cleanup()
            print("\n🧹 Demo cleanup completed")


def main():
    """Main function to run the training logging demonstration"""
    
    print("Starting Training Logging System Demonstration...")
    
    # Create and run the demo
    demo = TrainingLoggingDemo()
    demo.run_full_demo()
    
    print("\n🎯 Training logging demonstration completed!")
    print("The system demonstrated comprehensive logging for:")
    print("  • Training progress tracking")
    print("  • Error handling and reporting")
    print("  • Performance monitoring")
    print("  • Resource usage tracking")
    print("  • Visualization generation")
    print("  • Log analysis and insights")


if __name__ == "__main__":
    main() 