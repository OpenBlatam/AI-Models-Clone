#!/usr/bin/env python3
"""
Production Version Control Launcher for Diffusion Models

This script launches the production-ready version control manager
with comprehensive monitoring, error handling, and optimization.
"""

import asyncio
import sys
import logging
import signal
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import production version control manager
from core.version_control_manager_production import OptimizedVersionControlManager

# Configure production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('production_version_control.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProductionVersionControlLauncher:
    """Production launcher for version control manager."""
    
    def __init__(self):
        self.vc_manager = None
        self.running = False
        self.start_time = None
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    async def initialize_manager(self):
        """Initialize the version control manager."""
        try:
            logger.info("🚀 Initializing Production Version Control Manager...")
            self.vc_manager = OptimizedVersionControlManager()
            logger.info("✅ Version Control Manager initialized successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize Version Control Manager: {e}")
            return False
    
    async def run_production_demo(self):
        """Run comprehensive production demo."""
        try:
            logger.info("🧪 Starting Production Demo...")
            
            # Demo 1: Multiple experiments
            experiments = []
            
            # Experiment 1: Stable Diffusion v1.5
            config_sd_v1_5 = {
                "model": "stable-diffusion-v1-5",
                "learning_rate": 1e-4,
                "batch_size": 4,
                "epochs": 50,
                "optimizer": "adamw",
                "scheduler": "cosine",
                "mixed_precision": True,
                "gradient_clipping": 1.0
            }
            
            exp1_id = await self.vc_manager.start_experiment("stable_diffusion_v1_5", config_sd_v1_5)
            experiments.append(exp1_id)
            logger.info(f"✅ Started experiment: {exp1_id}")
            
            # Experiment 2: Stable Diffusion XL
            config_sd_xl = {
                "model": "stable-diffusion-xl",
                "learning_rate": 5e-5,
                "batch_size": 2,
                "epochs": 30,
                "optimizer": "adamw",
                "scheduler": "linear",
                "mixed_precision": True,
                "gradient_clipping": 1.0
            }
            
            exp2_id = await self.vc_manager.start_experiment("stable_diffusion_xl", config_sd_xl)
            experiments.append(exp2_id)
            logger.info(f"✅ Started experiment: {exp2_id}")
            
            # Demo 2: Simulate training progress
            logger.info("📈 Simulating training progress...")
            
            for epoch in range(1, 11):
                # Simulate metrics for both experiments
                for exp_id in experiments:
                    metrics = {
                        "loss": 0.5 - (epoch * 0.03),
                        "accuracy": 0.7 + (epoch * 0.02),
                        "learning_rate": 1e-4 * (0.95 ** epoch),
                        "memory_usage": 0.8 + (epoch * 0.01),
                        "gpu_utilization": 0.85 + (epoch * 0.005)
                    }
                    
                    await self.vc_manager.commit_training_progress(exp_id, epoch, metrics)
                    logger.info(f"  Epoch {epoch} - Experiment {exp_id}: Loss={metrics['loss']:.3f}")
                
                # Simulate checkpoint every 5 epochs
                if epoch % 5 == 0:
                    checkpoint_path = f"checkpoints/model_epoch_{epoch}.pt"
                    for exp_id in experiments:
                        await self.vc_manager.commit_training_progress(
                            exp_id, epoch, metrics, checkpoint_path
                        )
                    logger.info(f"  ✅ Checkpoint saved at epoch {epoch}")
            
            # Demo 3: Finish experiments
            logger.info("🏁 Finishing experiments...")
            
            final_metrics_sd_v1_5 = {
                "final_loss": 0.25,
                "final_accuracy": 0.85,
                "total_epochs": 10,
                "training_time": "00:45:30",
                "best_epoch": 8,
                "convergence_achieved": True
            }
            
            final_metrics_sd_xl = {
                "final_loss": 0.18,
                "final_accuracy": 0.88,
                "total_epochs": 10,
                "training_time": "01:15:45",
                "best_epoch": 9,
                "convergence_achieved": True
            }
            
            await self.vc_manager.finish_experiment(exp1_id, final_metrics_sd_v1_5)
            await self.vc_manager.finish_experiment(exp2_id, final_metrics_sd_xl)
            
            logger.info("✅ All experiments finished successfully")
            
            # Demo 4: Get comprehensive summaries
            logger.info("📊 Generating experiment summaries...")
            
            for exp_id in experiments:
                summary = await self.vc_manager.get_experiment_summary(exp_id)
                logger.info(f"📋 Summary for {exp_id}:")
                logger.info(f"  Name: {summary.get('name')}")
                logger.info(f"  Status: {summary.get('status')}")
                logger.info(f"  Total epochs: {summary.get('total_epochs')}")
                logger.info(f"  Checkpoints: {summary.get('checkpoints')}")
                logger.info(f"  Git commits: {len(summary.get('git_commits', []))}")
            
            # Demo 5: Performance monitoring
            logger.info("📈 Performance monitoring...")
            
            status = await self.vc_manager.git_manager.get_status()
            logger.info(f"📊 Repository Status:")
            logger.info(f"  Branch: {status.get('branch')}")
            logger.info(f"  Commit: {status.get('commit', '')[:8]}...")
            logger.info(f"  Modified files: {len(status.get('modified_files', []))}")
            logger.info(f"  Staged files: {len(status.get('staged_files', []))}")
            
            # Demo 6: Cleanup old experiments
            logger.info("🧹 Cleaning up old experiments...")
            cleaned_count = await self.vc_manager.cleanup_old_experiments(days_old=1)
            logger.info(f"✅ Cleaned up {cleaned_count} old experiments")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Production demo failed: {e}")
            return False
    
    async def run_performance_test(self):
        """Run performance and stress tests."""
        try:
            logger.info("⚡ Running Performance Tests...")
            
            # Test 1: Concurrent experiment creation
            logger.info("🔄 Testing concurrent experiment creation...")
            start_time = time.time()
            
            tasks = []
            for i in range(5):
                config = {
                    "model": f"test_model_{i}",
                    "learning_rate": 1e-4,
                    "batch_size": 4
                }
                task = self.vc_manager.start_experiment(f"perf_test_{i}", config)
                tasks.append(task)
            
            experiment_ids = await asyncio.gather(*tasks)
            end_time = time.time()
            
            logger.info(f"✅ Created {len(experiment_ids)} experiments in {end_time - start_time:.2f}s")
            
            # Test 2: Concurrent commits
            logger.info("🔄 Testing concurrent commits...")
            start_time = time.time()
            
            commit_tasks = []
            for exp_id in experiment_ids:
                for epoch in range(1, 6):
                    metrics = {"loss": 0.5 - epoch * 0.05, "accuracy": 0.7 + epoch * 0.03}
                    task = self.vc_manager.commit_training_progress(exp_id, epoch, metrics)
                    commit_tasks.append(task)
            
            await asyncio.gather(*commit_tasks)
            end_time = time.time()
            
            logger.info(f"✅ Completed {len(commit_tasks)} commits in {end_time - start_time:.2f}s")
            
            # Test 3: Memory usage
            logger.info("💾 Testing memory efficiency...")
            import psutil
            process = psutil.Process()
            memory_usage = process.memory_info().rss / 1024 / 1024  # MB
            logger.info(f"✅ Memory usage: {memory_usage:.2f} MB")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Performance test failed: {e}")
            return False
    
    async def run(self):
        """Main production run method."""
        try:
            self.start_time = datetime.now()
            self.running = True
            
            logger.info("🚀 Starting Production Version Control System...")
            logger.info(f"⏰ Start time: {self.start_time}")
            
            # Initialize manager
            if not await self.initialize_manager():
                return False
            
            # Run production demo
            if not await self.run_production_demo():
                return False
            
            # Run performance tests
            if not await self.run_performance_test():
                return False
            
            # Final status
            end_time = datetime.now()
            duration = end_time - self.start_time
            
            logger.info("🎉 Production Version Control System completed successfully!")
            logger.info(f"⏱️  Total duration: {duration}")
            logger.info(f"📊 Final status: All operations completed successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Production run failed: {e}")
            return False
        finally:
            self.running = False

async def main():
    """Main entry point."""
    launcher = ProductionVersionControlLauncher()
    
    try:
        success = await launcher.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("🛑 Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
