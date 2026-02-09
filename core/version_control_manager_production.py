#!/usr/bin/env python3
"""
Production Version Control Manager for Diffusion Models

Optimized version control system with advanced features for diffusion models:
- Async operations for better performance
- Comprehensive error handling and recovery
- Memory-efficient operations
- Production-ready logging and monitoring
- Advanced caching and optimization
"""

import asyncio
import os
import subprocess
import json
import yaml
import logging
import hashlib
import shutil
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from functools import lru_cache, wraps
import queue
import weakref

# Production logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('version_control.log'),
        logging.StreamHandler()
    ]
)

@dataclass
class GitConfig:
    """Configuration for Git operations."""
    repo_path: Path
    config_dir: Path
    max_workers: int = 4
    timeout: int = 30
    retry_attempts: int = 3
    cache_size: int = 128

@dataclass
class ExperimentMetadata:
    """Metadata for experiment tracking."""
    experiment_id: str
    name: str
    config_hash: str
    start_time: datetime
    git_commit: str
    branch: str
    status: str = "running"
    metrics: Dict[str, Any] = field(default_factory=dict)
    checkpoints: List[str] = field(default_factory=list)

class GitOperationError(Exception):
    """Custom exception for Git operations."""
    pass

class ExperimentError(Exception):
    """Custom exception for experiment operations."""
    pass

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator for retrying failed operations."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        time.sleep(delay * (2 ** attempt))  # Exponential backoff
            raise last_exception
        return wrapper
    return decorator

class AsyncGitManager:
    """Async Git operations manager."""
    
    def __init__(self, config: GitConfig):
        self.config = config
        self.executor = ThreadPoolExecutor(max_workers=config.max_workers)
        self._cache = {}
        self._lock = threading.Lock()
    
    async def run_git_command(self, command: List[str], timeout: int = None) -> str:
        """Run Git command asynchronously."""
        timeout = timeout or self.config.timeout
        
        def _run_command():
            try:
                result = subprocess.run(
                    command,
                    cwd=self.config.repo_path,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    check=True
                )
                return result.stdout.strip()
            except subprocess.TimeoutExpired:
                raise GitOperationError(f"Git command timed out: {' '.join(command)}")
            except subprocess.CalledProcessError as e:
                raise GitOperationError(f"Git command failed: {e.stderr}")
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _run_command)
    
    @retry_on_failure(max_retries=3)
    async def add_files(self, files: List[str]) -> bool:
        """Add files to Git staging area."""
        if not files:
            return True
        
        command = ["git", "add"] + files
        await self.run_git_command(command)
        return True
    
    @retry_on_failure(max_retries=3)
    async def commit_changes(self, message: str) -> bool:
        """Commit staged changes."""
        command = ["git", "commit", "-m", message]
        await self.run_git_command(command)
        return True
    
    @retry_on_failure(max_retries=3)
    async def create_branch(self, branch_name: str) -> bool:
        """Create and checkout new branch."""
        command = ["git", "checkout", "-b", branch_name]
        await self.run_git_command(command)
        return True
    
    @retry_on_failure(max_retries=3)
    async def create_tag(self, tag_name: str, message: str = "") -> bool:
        """Create Git tag."""
        if message:
            command = ["git", "tag", "-a", tag_name, "-m", message]
        else:
            command = ["git", "tag", tag_name]
        await self.run_git_command(command)
        return True
    
    async def get_status(self) -> Dict[str, Any]:
        """Get Git repository status."""
        try:
            branch = await self.run_git_command(["git", "branch", "--show-current"])
            commit = await self.run_git_command(["git", "rev-parse", "HEAD"])
            status_output = await self.run_git_command(["git", "status", "--porcelain"])
            
            status_lines = status_output.split('\n') if status_output else []
            
            return {
                "branch": branch,
                "commit": commit,
                "modified_files": [line[3:] for line in status_lines if line.startswith(' M')],
                "untracked_files": [line[3:] for line in status_lines if line.startswith('??')],
                "staged_files": [line[3:] for line in status_lines if line.startswith('M ')]
            }
        except Exception as e:
            logging.error(f"Failed to get Git status: {e}")
            return {}

class OptimizedVersionControlManager:
    """Production-ready version control manager for diffusion models."""
    
    def __init__(self, repo_path: str = ".", config_dir: str = "config"):
        self.config = GitConfig(
            repo_path=Path(repo_path).resolve(),
            config_dir=Path(config_dir)
        )
        self.git_manager = AsyncGitManager(self.config)
        self.logger = logging.getLogger(__name__)
        self.experiments: Dict[str, ExperimentMetadata] = {}
        self._experiment_lock = threading.Lock()
        self._file_cache = {}
        
        # Initialize repository
        self._ensure_git_repo()
    
    def _ensure_git_repo(self):
        """Ensure Git repository exists and is properly configured."""
        try:
            if not self._is_git_repo():
                self._init_git_repo()
            self._setup_gitignore()
        except Exception as e:
            self.logger.error(f"Failed to initialize Git repository: {e}")
            raise
    
    def _is_git_repo(self) -> bool:
        """Check if current directory is a Git repository."""
        try:
            subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.config.repo_path,
                capture_output=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False
    
    def _init_git_repo(self):
        """Initialize Git repository."""
        subprocess.run(["git", "init"], cwd=self.config.repo_path, check=True)
        self.logger.info(f"Initialized Git repository at {self.config.repo_path}")
    
    def _setup_gitignore(self):
        """Setup comprehensive .gitignore for diffusion models."""
        gitignore_content = """# Diffusion Models Production .gitignore

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

# PyTorch and ML
*.pth
*.pt
*.ckpt
*.safetensors
*.bin
models/
checkpoints/
weights/

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
mlruns/

# Configuration
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

# CUDA
*.cubin
*.fatbin

# Profiling
*.prof
*.trace

# Memory dumps
*.hprof

# Production specific
production/
staging/
backup/
"""
        
        gitignore_path = self.config.repo_path / ".gitignore"
        if not gitignore_path.exists():
            with open(gitignore_path, 'w') as f:
                f.write(gitignore_content)
            
            # Initial commit
            asyncio.run(self._initial_commit())
    
    async def _initial_commit(self):
        """Perform initial commit."""
        await self.git_manager.add_files([".gitignore"])
        await self.git_manager.commit_changes("Initial commit: Setup diffusion models project")
    
    @lru_cache(maxsize=128)
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of file."""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    async def save_configuration_snapshot(self, config_data: Dict[str, Any], filename: str) -> bool:
        """Save configuration snapshot with optimization."""
        try:
            # Create config directory
            config_path = self.config.repo_path / self.config.config_dir
            config_path.mkdir(exist_ok=True)
            
            # Generate timestamp and filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            snapshot_filename = f"{filename}_{timestamp}.yaml"
            snapshot_path = config_path / snapshot_filename
            
            # Save configuration with metadata
            config_with_metadata = {
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "git_commit": await self.git_manager.run_git_command(["git", "rev-parse", "HEAD"]),
                    "branch": await self.git_manager.run_git_command(["git", "branch", "--show-current"])
                },
                "config": config_data
            }
            
            with open(snapshot_path, 'w') as f:
                yaml.dump(config_with_metadata, f, default_flow_style=False, indent=2)
            
            # Add and commit
            relative_path = str(snapshot_path.relative_to(self.config.repo_path))
            await self.git_manager.add_files([relative_path])
            await self.git_manager.commit_changes(f"Add configuration snapshot: {snapshot_filename}")
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to save configuration snapshot: {e}")
            return False
    
    async def start_experiment(self, experiment_name: str, config: Dict[str, Any]) -> str:
        """Start a new experiment with optimized tracking."""
        try:
            # Generate experiment ID
            experiment_id = f"{experiment_name}_{int(time.time())}"
            
            # Create experiment branch
            branch_name = f"experiment/{experiment_name}"
            await self.git_manager.create_branch(branch_name)
            
            # Save configuration
            config_hash = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
            await self.save_configuration_snapshot(config, f"config_{experiment_name}")
            
            # Create experiment metadata
            experiment_meta = ExperimentMetadata(
                experiment_id=experiment_id,
                name=experiment_name,
                config_hash=config_hash,
                start_time=datetime.now(),
                git_commit=await self.git_manager.run_git_command(["git", "rev-parse", "HEAD"]),
                branch=branch_name
            )
            
            # Store experiment metadata
            with self._experiment_lock:
                self.experiments[experiment_id] = experiment_meta
            
            self.logger.info(f"Started experiment: {experiment_name} (ID: {experiment_id})")
            return experiment_id
            
        except Exception as e:
            self.logger.error(f"Failed to start experiment: {e}")
            raise ExperimentError(f"Failed to start experiment: {e}")
    
    async def commit_training_progress(self, experiment_id: str, epoch: int, 
                                     metrics: Dict[str, float], checkpoint_path: str = None) -> bool:
        """Commit training progress with optimization."""
        try:
            with self._experiment_lock:
                if experiment_id not in self.experiments:
                    raise ExperimentError(f"Experiment {experiment_id} not found")
                experiment = self.experiments[experiment_id]
            
            # Update experiment metadata
            experiment.metrics[f"epoch_{epoch}"] = metrics
            if checkpoint_path:
                experiment.checkpoints.append(checkpoint_path)
            
            # Save metrics to file
            metrics_file = f"metrics_{experiment.name}_epoch_{epoch}.json"
            metrics_path = self.config.repo_path / metrics_file
            
            metrics_data = {
                "experiment_id": experiment_id,
                "epoch": epoch,
                "timestamp": datetime.now().isoformat(),
                "metrics": metrics,
                "git_commit": await self.git_manager.run_git_command(["git", "rev-parse", "HEAD"])
            }
            
            with open(metrics_path, 'w') as f:
                json.dump(metrics_data, f, indent=2)
            
            # Add and commit
            await self.git_manager.add_files([metrics_file])
            await self.git_manager.commit_changes(f"Training progress - Epoch {epoch} - {experiment.name}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to commit training progress: {e}")
            return False
    
    async def finish_experiment(self, experiment_id: str, final_metrics: Dict[str, Any]) -> bool:
        """Finish experiment with comprehensive cleanup."""
        try:
            with self._experiment_lock:
                if experiment_id not in self.experiments:
                    raise ExperimentError(f"Experiment {experiment_id} not found")
                experiment = self.experiments[experiment_id]
                experiment.status = "completed"
                experiment.metrics["final"] = final_metrics
            
            # Save final metrics
            final_metrics_file = f"final_metrics_{experiment.name}.json"
            final_metrics_path = self.config.repo_path / final_metrics_file
            
            final_data = {
                "experiment_id": experiment_id,
                "final_metrics": final_metrics,
                "total_epochs": len([k for k in experiment.metrics.keys() if k.startswith("epoch_")]),
                "completion_time": datetime.now().isoformat(),
                "git_commit": await self.git_manager.run_git_command(["git", "rev-parse", "HEAD"])
            }
            
            with open(final_metrics_path, 'w') as f:
                json.dump(final_data, f, indent=2)
            
            # Add and commit final state
            await self.git_manager.add_files([final_metrics_file])
            await self.git_manager.commit_changes(f"Finish experiment: {experiment.name}")
            
            # Create experiment tag
            tag_name = f"experiment/{experiment.name}/v1.0.0"
            await self.git_manager.create_tag(tag_name, f"Completed experiment: {experiment.name}")
            
            self.logger.info(f"Finished experiment: {experiment.name} (ID: {experiment_id})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to finish experiment: {e}")
            return False
    
    async def get_experiment_summary(self, experiment_id: str) -> Dict[str, Any]:
        """Get comprehensive experiment summary."""
        try:
            with self._experiment_lock:
                if experiment_id not in self.experiments:
                    raise ExperimentError(f"Experiment {experiment_id} not found")
                experiment = self.experiments[experiment_id]
            
            # Get Git history
            commits = await self.git_manager.run_git_command(
                ["git", "log", "--oneline", "--grep", experiment.name]
            )
            
            # Get file statistics
            config_files = list(self.config.repo_path.glob(f"config/config_{experiment.name}_*.yaml"))
            metrics_files = list(self.config.repo_path.glob(f"metrics_{experiment.name}_*.json"))
            
            return {
                "experiment_id": experiment_id,
                "name": experiment.name,
                "status": experiment.status,
                "start_time": experiment.start_time.isoformat(),
                "git_commit": experiment.git_commit,
                "branch": experiment.branch,
                "config_hash": experiment.config_hash,
                "total_epochs": len([k for k in experiment.metrics.keys() if k.startswith("epoch_")]),
                "checkpoints": len(experiment.checkpoints),
                "config_files": [str(f) for f in config_files],
                "metrics_files": [str(f) for f in metrics_files],
                "git_commits": commits.split('\n') if commits else []
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get experiment summary: {e}")
            return {}
    
    async def cleanup_old_experiments(self, days_old: int = 30) -> int:
        """Clean up old experiment data."""
        try:
            cutoff_time = datetime.now() - timedelta(days=days_old)
            cleaned_count = 0
            
            with self._experiment_lock:
                old_experiments = [
                    exp_id for exp_id, exp in self.experiments.items()
                    if exp.start_time < cutoff_time and exp.status == "completed"
                ]
                
                for exp_id in old_experiments:
                    # Remove from memory
                    del self.experiments[exp_id]
                    cleaned_count += 1
            
            self.logger.info(f"Cleaned up {cleaned_count} old experiments")
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old experiments: {e}")
            return 0

# Production usage example
async def main():
    """Production usage example."""
    # Initialize manager
    vc_manager = OptimizedVersionControlManager()
    
    # Start experiment
    config = {
        "model": "stable-diffusion-v1-5",
        "learning_rate": 1e-4,
        "batch_size": 4,
        "epochs": 100
    }
    
    experiment_id = await vc_manager.start_experiment("production_test", config)
    
    # Simulate training
    for epoch in range(1, 6):
        metrics = {"loss": 0.5 - epoch * 0.05, "accuracy": 0.7 + epoch * 0.03}
        await vc_manager.commit_training_progress(experiment_id, epoch, metrics)
    
    # Finish experiment
    final_metrics = {"final_loss": 0.25, "final_accuracy": 0.85}
    await vc_manager.finish_experiment(experiment_id, final_metrics)
    
    # Get summary
    summary = await vc_manager.get_experiment_summary(experiment_id)
    print(f"Experiment summary: {summary}")

if __name__ == "__main__":
    asyncio.run(main())
