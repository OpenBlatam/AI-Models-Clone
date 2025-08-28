#!/usr/bin/env python3
"""
Version Control Manager for Diffusion Models

This module provides comprehensive version control management for diffusion models
using Git, including configuration tracking, experiment versioning, and best practices.

Features:
- Git operations for code and configuration tracking
- Experiment versioning and tagging
- Configuration file versioning
- Model checkpoint versioning
- Automated commit messages and branching
- Integration with experiment tracking
"""

import os
import subprocess
import json
import yaml
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import hashlib
import shutil

class VersionControlManager:
    """Comprehensive version control manager for diffusion models."""
    
    def __init__(self, repo_path: str = ".", config_dir: str = "config"):
        """
        Initialize version control manager.
        
        Args:
            repo_path: Path to Git repository
            config_dir: Directory for configuration files
        """
        self.repo_path = Path(repo_path).resolve()
        self.config_dir = Path(config_dir)
        self.logger = logging.getLogger(__name__)
        
        # Ensure Git repository exists
        if not self._is_git_repo():
            self._init_git_repo()
    
    def _is_git_repo(self) -> bool:
        """Check if current directory is a Git repository."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False
    
    def _init_git_repo(self):
        """Initialize Git repository if it doesn't exist."""
        try:
            subprocess.run(["git", "init"], cwd=self.repo_path, check=True)
            self.logger.info(f"Initialized Git repository at {self.repo_path}")
            
            # Create initial .gitignore if it doesn't exist
            gitignore_path = self.repo_path / ".gitignore"
            if not gitignore_path.exists():
                self._create_gitignore()
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to initialize Git repository: {e}")
            raise
    
    def _create_gitignore(self):
        """Create comprehensive .gitignore for diffusion models."""
        gitignore_content = """# Diffusion Models .gitignore

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/
.venv/
.env/

# Jupyter Notebook
.ipynb_checkpoints

# PyTorch
*.pth
*.pt
*.ckpt
*.safetensors

# Model checkpoints and weights
models/
checkpoints/
weights/
*.bin
*.safetensors

# Data
data/
datasets/
*.jpg
*.jpeg
*.png
*.gif
*.bmp
*.tiff
*.webp

# Logs and outputs
logs/
outputs/
results/
*.log
tensorboard_logs/
wandb/

# Configuration files with sensitive data
config/local/
config/secrets/
*.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Temporary files
tmp/
temp/
*.tmp
*.temp

# Large files
*.zip
*.tar.gz
*.rar

# Experiment tracking
mlruns/
.mlruns/

# CUDA
*.cubin
*.fatbin

# Profiling
*.prof
*.trace

# Memory dumps
*.hprof
"""
        
        gitignore_path = self.repo_path / ".gitignore"
        with open(gitignore_path, 'w') as f:
            f.write(gitignore_content)
        
        # Add and commit .gitignore
        self._git_add([".gitignore"])
        self._git_commit("Initial commit: Add .gitignore for diffusion models")
    
    def _git_add(self, files: List[str]) -> bool:
        """Add files to Git staging area."""
        try:
            subprocess.run(
                ["git", "add"] + files,
                cwd=self.repo_path,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to add files to Git: {e}")
            return False
    
    def _git_commit(self, message: str) -> bool:
        """Commit staged changes."""
        try:
            subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.repo_path,
                check=True
            )
            self.logger.info(f"Committed: {message}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to commit: {e}")
            return False
    
    def _git_tag(self, tag_name: str, message: str = "") -> bool:
        """Create Git tag."""
        try:
            if message:
                subprocess.run(
                    ["git", "tag", "-a", tag_name, "-m", message],
                    cwd=self.repo_path,
                    check=True
                )
            else:
                subprocess.run(
                    ["git", "tag", tag_name],
                    cwd=self.repo_path,
                    check=True
                )
            self.logger.info(f"Created tag: {tag_name}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to create tag: {e}")
            return False
    
    def _git_branch(self, branch_name: str, checkout: bool = True) -> bool:
        """Create and optionally checkout new branch."""
        try:
            subprocess.run(
                ["git", "checkout", "-b", branch_name],
                cwd=self.repo_path,
                check=True
            )
            self.logger.info(f"Created and checked out branch: {branch_name}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to create branch: {e}")
            return False
    
    def get_current_branch(self) -> str:
        """Get current Git branch name."""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "main"
    
    def get_current_commit(self) -> str:
        """Get current Git commit hash."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return ""
    
    def get_status(self) -> Dict[str, Any]:
        """Get Git repository status."""
        try:
            # Get current branch
            branch = self.get_current_branch()
            
            # Get current commit
            commit = self.get_current_commit()
            
            # Get status
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            status_lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            return {
                "branch": branch,
                "commit": commit,
                "modified_files": [line[3:] for line in status_lines if line.startswith(' M')],
                "untracked_files": [line[3:] for line in status_lines if line.startswith('??')],
                "staged_files": [line[3:] for line in status_lines if line.startswith('M ')]
            }
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to get Git status: {e}")
            return {}
    
    def commit_configuration_changes(self, config_files: List[str], message: str = None) -> bool:
        """Commit configuration file changes."""
        if not message:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"Update configuration files - {timestamp}"
        
        # Add configuration files
        if self._git_add(config_files):
            return self._git_commit(message)
        return False
    
    def commit_model_changes(self, model_files: List[str], experiment_name: str = None) -> bool:
        """Commit model-related changes."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if experiment_name:
            message = f"Update model files for experiment '{experiment_name}' - {timestamp}"
        else:
            message = f"Update model files - {timestamp}"
        
        # Add model files
        if self._git_add(model_files):
            return self._git_commit(message)
        return False
    
    def create_experiment_branch(self, experiment_name: str) -> bool:
        """Create a new branch for an experiment."""
        branch_name = f"experiment/{experiment_name}"
        return self._git_branch(branch_name)
    
    def tag_experiment(self, experiment_name: str, version: str = None) -> bool:
        """Create a tag for an experiment."""
        if not version:
            version = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        tag_name = f"experiment/{experiment_name}/v{version}"
        message = f"Experiment {experiment_name} version {version}"
        
        return self._git_tag(tag_name, message)
    
    def save_configuration_snapshot(self, config_data: Dict[str, Any], filename: str) -> bool:
        """Save configuration snapshot with version control."""
        # Create config directory if it doesn't exist
        config_path = self.repo_path / self.config_dir
        config_path.mkdir(exist_ok=True)
        
        # Save configuration with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_filename = f"{filename}_{timestamp}.yaml"
        snapshot_path = config_path / snapshot_filename
        
        with open(snapshot_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False, indent=2)
        
        # Add and commit configuration snapshot
        if self._git_add([str(snapshot_path.relative_to(self.repo_path))]):
            message = f"Add configuration snapshot: {snapshot_filename}"
            return self._git_commit(message)
        
        return False
    
    def track_model_checkpoint(self, checkpoint_path: str, experiment_name: str = None) -> bool:
        """Track model checkpoint in version control."""
        # Create checkpoints directory if it doesn't exist
        checkpoints_dir = self.repo_path / "checkpoints"
        checkpoints_dir.mkdir(exist_ok=True)
        
        # Copy checkpoint to tracked location
        checkpoint_name = Path(checkpoint_path).name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if experiment_name:
            tracked_name = f"{experiment_name}_{checkpoint_name}_{timestamp}"
        else:
            tracked_name = f"{checkpoint_name}_{timestamp}"
        
        tracked_path = checkpoints_dir / tracked_name
        shutil.copy2(checkpoint_path, tracked_path)
        
        # Add and commit checkpoint
        if self._git_add([str(tracked_path.relative_to(self.repo_path))]):
            message = f"Add model checkpoint: {tracked_name}"
            return self._git_commit(message)
        
        return False
    
    def create_release_tag(self, version: str, message: str = None) -> bool:
        """Create a release tag."""
        if not message:
            message = f"Release version {version}"
        
        tag_name = f"v{version}"
        return self._git_tag(tag_name, message)
    
    def get_experiment_history(self, experiment_name: str = None) -> List[Dict[str, Any]]:
        """Get experiment history from Git."""
        try:
            if experiment_name:
                # Get commits for specific experiment
                result = subprocess.run(
                    ["git", "log", "--oneline", "--grep", experiment_name],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
            else:
                # Get all commits
                result = subprocess.run(
                    ["git", "log", "--oneline"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split(' ', 1)
                    if len(parts) == 2:
                        commits.append({
                            "hash": parts[0],
                            "message": parts[1]
                        })
            
            return commits
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to get experiment history: {e}")
            return []
    
    def revert_to_commit(self, commit_hash: str) -> bool:
        """Revert to a specific commit."""
        try:
            subprocess.run(
                ["git", "reset", "--hard", commit_hash],
                cwd=self.repo_path,
                check=True
            )
            self.logger.info(f"Reverted to commit: {commit_hash}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to revert to commit: {e}")
            return False
    
    def create_backup_branch(self, backup_name: str = None) -> bool:
        """Create a backup branch of current state."""
        if not backup_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}"
        
        return self._git_branch(backup_name)
    
    def get_file_history(self, file_path: str) -> List[Dict[str, Any]]:
        """Get history of changes for a specific file."""
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "--follow", file_path],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            history = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split(' ', 1)
                    if len(parts) == 2:
                        history.append({
                            "hash": parts[0],
                            "message": parts[1]
                        })
            
            return history
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to get file history: {e}")
            return []


class DiffusionExperimentTracker:
    """Specialized experiment tracker for diffusion models with version control."""
    
    def __init__(self, vc_manager: VersionControlManager):
        """
        Initialize diffusion experiment tracker.
        
        Args:
            vc_manager: Version control manager instance
        """
        self.vc_manager = vc_manager
        self.logger = logging.getLogger(__name__)
        self.current_experiment = None
    
    def start_experiment(self, experiment_name: str, config: Dict[str, Any]) -> bool:
        """Start a new experiment with version control."""
        try:
            # Create experiment branch
            if not self.vc_manager.create_experiment_branch(experiment_name):
                return False
            
            # Save configuration snapshot
            if not self.vc_manager.save_configuration_snapshot(config, f"config_{experiment_name}"):
                return False
            
            self.current_experiment = experiment_name
            self.logger.info(f"Started experiment: {experiment_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start experiment: {e}")
            return False
    
    def commit_training_progress(self, epoch: int, metrics: Dict[str, float], checkpoint_path: str = None) -> bool:
        """Commit training progress to version control."""
        if not self.current_experiment:
            self.logger.error("No active experiment")
            return False
        
        try:
            # Save metrics to file
            metrics_file = f"metrics_{self.current_experiment}_epoch_{epoch}.json"
            metrics_path = self.vc_manager.repo_path / metrics_file
            
            with open(metrics_path, 'w') as f:
                json.dump(metrics, f, indent=2)
            
            # Add metrics file
            if not self.vc_manager._git_add([metrics_file]):
                return False
            
            # Add checkpoint if provided
            if checkpoint_path:
                if not self.vc_manager.track_model_checkpoint(checkpoint_path, self.current_experiment):
                    return False
            
            # Commit progress
            message = f"Training progress - Epoch {epoch} - {self.current_experiment}"
            return self.vc_manager._git_commit(message)
        except Exception as e:
            self.logger.error(f"Failed to commit training progress: {e}")
            return False
    
    def finish_experiment(self, final_metrics: Dict[str, float], final_checkpoint_path: str = None) -> bool:
        """Finish experiment and create tag."""
        if not self.current_experiment:
            self.logger.error("No active experiment")
            return False
        
        try:
            # Save final metrics
            final_metrics_file = f"final_metrics_{self.current_experiment}.json"
            final_metrics_path = self.vc_manager.repo_path / final_metrics_file
            
            with open(final_metrics_path, 'w') as f:
                json.dump(final_metrics, f, indent=2)
            
            # Add final metrics
            if not self.vc_manager._git_add([final_metrics_file]):
                return False
            
            # Add final checkpoint if provided
            if final_checkpoint_path:
                if not self.vc_manager.track_model_checkpoint(final_checkpoint_path, self.current_experiment):
                    return False
            
            # Commit final state
            message = f"Finish experiment: {self.current_experiment}"
            if not self.vc_manager._git_commit(message):
                return False
            
            # Create experiment tag
            if not self.vc_manager.tag_experiment(self.current_experiment):
                return False
            
            self.logger.info(f"Finished experiment: {self.current_experiment}")
            self.current_experiment = None
            return True
        except Exception as e:
            self.logger.error(f"Failed to finish experiment: {e}")
            return False
    
    def get_experiment_summary(self, experiment_name: str) -> Dict[str, Any]:
        """Get summary of an experiment."""
        try:
            # Get experiment commits
            commits = self.vc_manager.get_experiment_history(experiment_name)
            
            # Get configuration files
            config_files = list(self.vc_manager.repo_path.glob(f"config/config_{experiment_name}_*.yaml"))
            
            # Get metrics files
            metrics_files = list(self.vc_manager.repo_path.glob(f"metrics_{experiment_name}_*.json"))
            
            # Get checkpoint files
            checkpoint_files = list(self.vc_manager.repo_path.glob(f"checkpoints/{experiment_name}_*"))
            
            return {
                "experiment_name": experiment_name,
                "commits": commits,
                "config_files": [str(f) for f in config_files],
                "metrics_files": [str(f) for f in metrics_files],
                "checkpoint_files": [str(f) for f in checkpoint_files]
            }
        except Exception as e:
            self.logger.error(f"Failed to get experiment summary: {e}")
            return {}


# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize version control manager
    vc_manager = VersionControlManager()
    
    # Initialize experiment tracker
    experiment_tracker = DiffusionExperimentTracker(vc_manager)
    
    # Example: Start an experiment
    config = {
        "model": "stable-diffusion-v1-5",
        "learning_rate": 1e-4,
        "batch_size": 4,
        "epochs": 100,
        "optimizer": "adamw"
    }
    
    if experiment_tracker.start_experiment("test_experiment", config):
        print("✅ Experiment started successfully")
        
        # Example: Commit training progress
        metrics = {"loss": 0.5, "accuracy": 0.85}
        if experiment_tracker.commit_training_progress(1, metrics):
            print("✅ Training progress committed")
        
        # Example: Finish experiment
        final_metrics = {"final_loss": 0.2, "final_accuracy": 0.92}
        if experiment_tracker.finish_experiment(final_metrics):
            print("✅ Experiment finished successfully")
    
    # Get repository status
    status = vc_manager.get_status()
    print(f"Repository status: {status}")
