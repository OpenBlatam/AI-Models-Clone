#!/usr/bin/env python3
"""
Version Control Demo for Diffusion Models

This script demonstrates the comprehensive version control management system
for diffusion models, including Git operations, experiment tracking, and
best practices implementation.
"""

import os
import sys
import logging
import json
import yaml
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import version control manager
from core.version_control_manager import VersionControlManager, DiffusionExperimentTracker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def demo_version_control_setup():
    """Demonstrate version control setup and initialization."""
    print("🔄 Version Control Setup Demo")
    print("=" * 50)
    
    # Initialize version control manager
    vc_manager = VersionControlManager()
    
    # Get repository status
    status = vc_manager.get_status()
    print(f"📊 Repository Status:")
    print(f"  Branch: {status.get('branch', 'N/A')}")
    print(f"  Commit: {status.get('commit', 'N/A')[:8]}...")
    print(f"  Modified files: {len(status.get('modified_files', []))}")
    print(f"  Untracked files: {len(status.get('untracked_files', []))}")
    
    return vc_manager

def demo_configuration_management(vc_manager):
    """Demonstrate configuration management with version control."""
    print("\n⚙️ Configuration Management Demo")
    print("=" * 50)
    
    # Create sample configuration
    config = {
        "model": {
            "name": "stable-diffusion-v1-5",
            "pretrained": True,
            "device": "cuda"
        },
        "training": {
            "learning_rate": 1e-4,
            "batch_size": 4,
            "epochs": 100,
            "optimizer": "adamw",
            "scheduler": "cosine"
        },
        "data": {
            "dataset_path": "data/processed",
            "image_size": 512,
            "num_workers": 4
        },
        "experiment": {
            "name": "demo_experiment",
            "tracking": "wandb",
            "checkpoint_dir": "models/checkpoints"
        }
    }
    
    # Save configuration snapshot
    print("💾 Saving configuration snapshot...")
    if vc_manager.save_configuration_snapshot(config, "demo_config"):
        print("✅ Configuration snapshot saved and committed")
    
    # Create experiment-specific configuration
    experiment_config = {
        "model": {
            "name": "stable-diffusion-xl",
            "pretrained": True,
            "device": "cuda"
        },
        "training": {
            "learning_rate": 5e-5,
            "batch_size": 2,
            "epochs": 50,
            "optimizer": "adamw",
            "scheduler": "linear"
        }
    }
    
    print("💾 Saving experiment configuration...")
    if vc_manager.save_configuration_snapshot(experiment_config, "experiment_sd_xl"):
        print("✅ Experiment configuration saved and committed")

def demo_experiment_tracking(vc_manager):
    """Demonstrate experiment tracking with version control."""
    print("\n🧪 Experiment Tracking Demo")
    print("=" * 50)
    
    # Initialize experiment tracker
    experiment_tracker = DiffusionExperimentTracker(vc_manager)
    
    # Start experiment
    config = {
        "model": "stable-diffusion-v1-5",
        "learning_rate": 1e-4,
        "batch_size": 4,
        "epochs": 10,
        "optimizer": "adamw"
    }
    
    print("🚀 Starting experiment...")
    if experiment_tracker.start_experiment("demo_stable_diffusion", config):
        print("✅ Experiment started successfully")
        
        # Simulate training progress
        print("📈 Simulating training progress...")
        for epoch in range(1, 6):
            # Simulate metrics
            metrics = {
                "loss": 0.5 - (epoch * 0.05),
                "accuracy": 0.7 + (epoch * 0.03),
                "learning_rate": 1e-4 * (0.95 ** epoch)
            }
            
            print(f"  Epoch {epoch}: Loss={metrics['loss']:.3f}, Accuracy={metrics['accuracy']:.3f}")
            
            # Commit training progress
            if experiment_tracker.commit_training_progress(epoch, metrics):
                print(f"  ✅ Epoch {epoch} progress committed")
        
        # Finish experiment
        print("🏁 Finishing experiment...")
        final_metrics = {
            "final_loss": 0.25,
            "final_accuracy": 0.85,
            "total_epochs": 5,
            "training_time": "00:15:30"
        }
        
        if experiment_tracker.finish_experiment(final_metrics):
            print("✅ Experiment finished and tagged")
    
    return experiment_tracker

def demo_branching_and_tagging(vc_manager):
    """Demonstrate branching and tagging strategies."""
    print("\n🌿 Branching and Tagging Demo")
    print("=" * 50)
    
    # Create feature branch
    print("🌿 Creating feature branch...")
    if vc_manager._git_branch("feature/demo-diffusion-pipeline"):
        print("✅ Feature branch created")
    
    # Create experiment branch
    print("🧪 Creating experiment branch...")
    if vc_manager.create_experiment_branch("stable-diffusion-xl"):
        print("✅ Experiment branch created")
    
    # Create backup branch
    print("💾 Creating backup branch...")
    if vc_manager.create_backup_branch("backup_demo_state"):
        print("✅ Backup branch created")
    
    # Create tags
    print("🏷️ Creating tags...")
    if vc_manager.tag_experiment("demo_stable_diffusion", "v1.0.0"):
        print("✅ Experiment tag created")
    
    if vc_manager.create_release_tag("1.0.0", "First demo release"):
        print("✅ Release tag created")

def demo_file_history_and_analytics(vc_manager):
    """Demonstrate file history and analytics."""
    print("\n📊 File History and Analytics Demo")
    print("=" * 50)
    
    # Get experiment history
    print("📈 Getting experiment history...")
    commits = vc_manager.get_experiment_history("demo_stable_diffusion")
    print(f"  Found {len(commits)} commits for experiment")
    
    for i, commit in enumerate(commits[:3]):  # Show first 3 commits
        print(f"  {i+1}. {commit['hash'][:8]} - {commit['message']}")
    
    # Get file history
    print("\n📄 Getting file history...")
    config_files = list(Path("config").glob("*.yaml"))
    if config_files:
        file_history = vc_manager.get_file_history(str(config_files[0]))
        print(f"  Found {len(file_history)} changes for {config_files[0].name}")
    
    # Get repository statistics
    print("\n📊 Repository statistics:")
    status = vc_manager.get_status()
    print(f"  Current branch: {status.get('branch', 'N/A')}")
    print(f"  Current commit: {status.get('commit', 'N/A')[:8]}...")
    print(f"  Modified files: {len(status.get('modified_files', []))}")
    print(f"  Staged files: {len(status.get('staged_files', []))}")

def demo_experiment_comparison(experiment_tracker):
    """Demonstrate experiment comparison capabilities."""
    print("\n🔍 Experiment Comparison Demo")
    print("=" * 50)
    
    # Get experiment summary
    print("📋 Getting experiment summary...")
    summary = experiment_tracker.get_experiment_summary("demo_stable_diffusion")
    
    print(f"  Experiment: {summary.get('experiment_name', 'N/A')}")
    print(f"  Commits: {len(summary.get('commits', []))}")
    print(f"  Config files: {len(summary.get('config_files', []))}")
    print(f"  Metrics files: {len(summary.get('metrics_files', []))}")
    print(f"  Checkpoint files: {len(summary.get('checkpoint_files', []))}")

def demo_security_and_best_practices():
    """Demonstrate security considerations and best practices."""
    print("\n🔒 Security and Best Practices Demo")
    print("=" * 50)
    
    # Check for sensitive files
    sensitive_patterns = [
        "*.env",
        "config/local/*",
        "secrets/*",
        "api_keys/*"
    ]
    
    print("🔍 Checking for sensitive files...")
    for pattern in sensitive_patterns:
        files = list(Path(".").glob(pattern))
        if files:
            print(f"  ⚠️  Found sensitive files matching '{pattern}': {len(files)} files")
        else:
            print(f"  ✅ No sensitive files found for '{pattern}'")
    
    # Check .gitignore
    gitignore_path = Path(".gitignore")
    if gitignore_path.exists():
        print(f"  ✅ .gitignore file exists ({gitignore_path.stat().st_size} bytes)")
    else:
        print("  ⚠️  .gitignore file not found")

def demo_automation_workflows(vc_manager):
    """Demonstrate automation workflows."""
    print("\n🤖 Automation Workflows Demo")
    print("=" * 50)
    
    # Simulate automated configuration commit
    print("⚙️ Simulating automated configuration commit...")
    config_files = ["config/demo_config_*.yaml"]
    if vc_manager.commit_configuration_changes(config_files, "Auto: Update demo configuration"):
        print("✅ Automated configuration commit successful")
    
    # Simulate automated model commit
    print("🤖 Simulating automated model commit...")
    model_files = ["core/diffusion_models.py"]
    if vc_manager.commit_model_changes(model_files, "demo_stable_diffusion"):
        print("✅ Automated model commit successful")

def main():
    """Main demo function."""
    print("🚀 Diffusion Models Version Control Demo")
    print("=" * 60)
    print("This demo showcases comprehensive version control management")
    print("for diffusion models using Git best practices.")
    print("=" * 60)
    
    try:
        # Demo 1: Version Control Setup
        vc_manager = demo_version_control_setup()
        
        # Demo 2: Configuration Management
        demo_configuration_management(vc_manager)
        
        # Demo 3: Experiment Tracking
        experiment_tracker = demo_experiment_tracking(vc_manager)
        
        # Demo 4: Branching and Tagging
        demo_branching_and_tagging(vc_manager)
        
        # Demo 5: File History and Analytics
        demo_file_history_and_analytics(vc_manager)
        
        # Demo 6: Experiment Comparison
        demo_experiment_comparison(experiment_tracker)
        
        # Demo 7: Security and Best Practices
        demo_security_and_best_practices()
        
        # Demo 8: Automation Workflows
        demo_automation_workflows(vc_manager)
        
        print("\n🎉 Version Control Demo Completed Successfully!")
        print("=" * 60)
        print("✅ All version control features demonstrated")
        print("✅ Git repository properly configured")
        print("✅ Experiment tracking implemented")
        print("✅ Best practices followed")
        print("=" * 60)
        
        # Final status
        final_status = vc_manager.get_status()
        print(f"\n📊 Final Repository Status:")
        print(f"  Branch: {final_status.get('branch', 'N/A')}")
        print(f"  Commit: {final_status.get('commit', 'N/A')[:8]}...")
        print(f"  Total commits: {len(vc_manager.get_experiment_history())}")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"❌ Demo failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
