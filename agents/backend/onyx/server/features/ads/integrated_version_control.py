"""
Integrated Version Control System

This module provides seamless integration between version control, configuration management,
and experiment tracking systems. It enables:

- Automatic git commits for experiment changes
- Configuration versioning and rollback
- Experiment reproducibility through git commits
- Branch management for different experiment versions
- Integration with experiment tracking backends
"""
import os
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field, asdict
import logging
from contextlib import contextmanager

from onyx.utils.logger import setup_logger
from onyx.server.features.ads.config_manager import ConfigManager, ConfigType
from onyx.server.features.ads.experiment_tracker import (
    ExperimentTracker, ExperimentMetadata, create_experiment_tracker
)
from onyx.server.features.ads.version_control_manager import (
    VersionControlManager, ExperimentVersionControl, GitCommit, ExperimentVersion
)

logger = setup_logger()

@dataclass
class IntegratedExperimentInfo:
    """Integrated experiment information combining all systems."""
    experiment_id: str
    experiment_name: str
    git_hash: str
    branch: str
    config_hash: str
    code_hash: str
    commit_date: datetime
    commit_message: str
    is_reproducible: bool = True
    dependencies: Dict[str, str] = field(default_factory=dict)
    experiment_metadata: Optional[ExperimentMetadata] = None
    configs: Dict[str, Any] = field(default_factory=dict)
    final_metrics: Optional[Dict[str, float]] = None
    tags: List[str] = field(default_factory=list)

class IntegratedVersionControl:
    """Integrated version control system combining git, config management, and experiment tracking."""
    
    def __init__(self, project_root: str = ".", auto_commit: bool = True):
        self.project_root = Path(project_root).resolve()
        self.auto_commit = auto_commit
        self.logger = logger
        
        # Initialize all systems
        self.vc_manager = VersionControlManager(project_root, auto_commit)
        self.config_manager = ConfigManager(str(self.project_root / "configs"))
        self.exp_vc = ExperimentVersionControl(project_root, auto_commit)
        
        # Track active experiments
        self.active_experiments = {}
    
    def start_integrated_experiment(self,
                                   experiment_id: str,
                                   experiment_name: str,
                                   configs: Dict[str, Any],
                                   create_branch: bool = True,
                                   tracking_backend: str = "local") -> Tuple[str, ExperimentTracker]:
        """Start an experiment with integrated version control and tracking."""
        try:
            # 1. Create experiment branch if requested
            if create_branch:
                self.vc_manager.create_experiment_branch(experiment_id)
            
            # 2. Save configurations
            self._save_configurations(experiment_id, configs)
            
            # 3. Start version control
            commit_hash = self.exp_vc.start_experiment(
                experiment_id=experiment_id,
                experiment_name=experiment_name,
                configs=configs,
                create_branch=create_branch
            )
            
            # 4. Set up experiment tracking
            experiment_config = self._create_experiment_config(
                experiment_id, experiment_name, tracking_backend
            )
            
            tracker = create_experiment_tracker(experiment_config)
            
            # 5. Create experiment metadata
            metadata = ExperimentMetadata(
                experiment_id=experiment_id,
                experiment_name=experiment_name,
                project_name=self._get_project_name(),
                created_at=datetime.now(),
                tags=["integrated", "version_controlled"],
                description=f"Integrated experiment with version control",
                git_commit=commit_hash,
                python_version=self._get_python_version(),
                dependencies=self.vc_manager._get_dependencies(),
                hardware_info=self._get_hardware_info()
            )
            
            # 6. Start experiment tracking
            tracker.start_experiment(metadata)
            
            # 7. Log git information
            tracker.log_hyperparameters({
                "git_hash": commit_hash,
                "branch": self.vc_manager.get_current_branch(),
                "configs": configs
            })
            
            # 8. Track active experiment
            self.active_experiments[experiment_id] = {
                "tracker": tracker,
                "configs": configs,
                "start_commit": commit_hash,
                "start_time": datetime.now()
            }
            
            self.logger.info(f"Started integrated experiment {experiment_id} with commit {commit_hash}")
            return commit_hash, tracker
            
        except Exception as e:
            self.logger.error(f"Failed to start integrated experiment: {e}")
            raise
    
    def commit_experiment_changes(self,
                                 experiment_id: str,
                                 experiment_name: str,
                                 configs: Dict[str, Any],
                                 message: str = "",
                                 log_metrics: Optional[Dict[str, float]] = None) -> str:
        """Commit changes during an experiment with integrated tracking."""
        try:
            # 1. Update configurations if changed
            if configs != self.active_experiments.get(experiment_id, {}).get("configs", {}):
                self._save_configurations(experiment_id, configs)
                self.active_experiments[experiment_id]["configs"] = configs
            
            # 2. Commit to version control
            commit_hash = self.exp_vc.commit_experiment_changes(
                experiment_id=experiment_id,
                experiment_name=experiment_name,
                configs=configs,
                message=message
            )
            
            # 3. Log to experiment tracker if available
            if experiment_id in self.active_experiments:
                tracker = self.active_experiments[experiment_id]["tracker"]
                
                # Log git information
                tracker.log_metrics({
                    "git_hash": commit_hash,
                    "git_branch": self.vc_manager.get_current_branch(),
                    "commit_message": message
                }, step=tracker.current_step)
                
                # Log additional metrics if provided
                if log_metrics:
                    tracker.log_metrics(log_metrics, step=tracker.current_step)
            
            self.logger.info(f"Committed changes for experiment {experiment_id}: {commit_hash}")
            return commit_hash
            
        except Exception as e:
            self.logger.error(f"Failed to commit experiment changes: {e}")
            raise
    
    def end_integrated_experiment(self,
                                 experiment_id: str,
                                 experiment_name: str,
                                 configs: Dict[str, Any],
                                 final_metrics: Dict[str, float],
                                 tag_name: Optional[str] = None) -> str:
        """End an experiment with integrated version control and tracking."""
        try:
            # 1. End experiment tracking
            if experiment_id in self.active_experiments:
                tracker = self.active_experiments[experiment_id]["tracker"]
                
                # Log final metrics
                tracker.log_metrics(final_metrics, step=tracker.current_step)
                
                # End experiment
                tracker.end_experiment()
                
                # Remove from active experiments
                del self.active_experiments[experiment_id]
            
            # 2. End version control
            commit_hash = self.exp_vc.end_experiment(
                experiment_id=experiment_id,
                experiment_name=experiment_name,
                configs=configs,
                final_metrics=final_metrics,
                tag_name=tag_name
            )
            
            # 3. Save final experiment info
            self._save_integrated_experiment_info(
                experiment_id, experiment_name, commit_hash, configs, final_metrics
            )
            
            self.logger.info(f"Ended integrated experiment {experiment_id} with commit {commit_hash}")
            return commit_hash
            
        except Exception as e:
            self.logger.error(f"Failed to end integrated experiment: {e}")
            raise
    
    def reproduce_integrated_experiment(self, experiment_id: str) -> Optional[ExperimentTracker]:
        """Reproduce an experiment from its exact version with integrated tracking."""
        try:
            # 1. Get experiment version info
            version_info = self.vc_manager.get_experiment_version(experiment_id)
            if not version_info:
                self.logger.error(f"Version info not found for experiment {experiment_id}")
                return None
            
            # 2. Reproduce git state
            success = self.vc_manager.reproduce_experiment(experiment_id)
            if not success:
                self.logger.error(f"Failed to reproduce git state for experiment {experiment_id}")
                return None
            
            # 3. Load configurations
            configs = self._load_experiment_configs(experiment_id)
            if not configs:
                self.logger.error(f"Failed to load configs for experiment {experiment_id}")
                return None
            
            # 4. Set up experiment tracking for reproduction
            experiment_config = self._create_experiment_config(
                f"{experiment_id}_reproduced", 
                f"Reproduced {experiment_id}", 
                "local"
            )
            
            tracker = create_experiment_tracker(experiment_config)
            
            # 5. Create reproduction metadata
            metadata = ExperimentMetadata(
                experiment_id=f"{experiment_id}_reproduced",
                experiment_name=f"Reproduced {experiment_id}",
                project_name=self._get_project_name(),
                created_at=datetime.now(),
                tags=["reproduced", "version_controlled"],
                description=f"Reproduced experiment {experiment_id} from commit {version_info.git_hash}",
                git_commit=version_info.git_hash,
                python_version=self._get_python_version(),
                dependencies=version_info.dependencies,
                hardware_info=self._get_hardware_info()
            )
            
            tracker.start_experiment(metadata)
            
            # 6. Log reproduction information
            tracker.log_hyperparameters({
                "original_experiment_id": experiment_id,
                "original_git_hash": version_info.git_hash,
                "original_branch": version_info.branch,
                "reproduction_date": datetime.now().isoformat(),
                "configs": configs
            })
            
            self.logger.info(f"Reproduced experiment {experiment_id} from commit {version_info.git_hash}")
            return tracker
            
        except Exception as e:
            self.logger.error(f"Failed to reproduce integrated experiment: {e}")
            return None
    
    def get_integrated_experiment_info(self, experiment_id: str) -> Optional[IntegratedExperimentInfo]:
        """Get comprehensive information about an integrated experiment."""
        try:
            # Get version info
            version_info = self.vc_manager.get_experiment_version(experiment_id)
            if not version_info:
                return None
            
            # Load configurations
            configs = self._load_experiment_configs(experiment_id)
            
            # Load final metrics
            final_metrics = self._load_experiment_metrics(experiment_id)
            
            # Get experiment tags
            tags = self.vc_manager.get_experiment_tags(experiment_id)
            
            return IntegratedExperimentInfo(
                experiment_id=experiment_id,
                experiment_name=version_info.experiment_id,  # Use experiment_id as name
                git_hash=version_info.git_hash,
                branch=version_info.branch,
                config_hash=version_info.config_hash,
                code_hash=version_info.code_hash,
                commit_date=version_info.commit_date,
                commit_message=version_info.commit_message,
                is_reproducible=version_info.is_reproducible,
                dependencies=version_info.dependencies,
                configs=configs,
                final_metrics=final_metrics,
                tags=tags
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get integrated experiment info: {e}")
            return None
    
    def compare_experiments(self, experiment_ids: List[str]) -> Dict[str, Any]:
        """Compare multiple integrated experiments."""
        comparison = {
            "experiments": {},
            "differences": {},
            "summary": {}
        }
        
        experiment_infos = []
        
        for exp_id in experiment_ids:
            info = self.get_integrated_experiment_info(exp_id)
            if info:
                experiment_infos.append(info)
                comparison["experiments"][exp_id] = asdict(info)
        
        if len(experiment_infos) < 2:
            return comparison
        
        # Compare configurations
        config_differences = self._compare_configurations(experiment_infos)
        comparison["differences"]["configurations"] = config_differences
        
        # Compare metrics
        metric_differences = self._compare_metrics(experiment_infos)
        comparison["differences"]["metrics"] = metric_differences
        
        # Generate summary
        comparison["summary"] = self._generate_comparison_summary(experiment_infos)
        
        return comparison
    
    def create_experiment_snapshot(self, experiment_id: str) -> str:
        """Create a complete snapshot of an experiment."""
        try:
            # Get experiment info
            info = self.get_integrated_experiment_info(experiment_id)
            if not info:
                raise ValueError(f"Experiment {experiment_id} not found")
            
            # Create snapshot directory
            snapshot_dir = self.project_root / "experiment_snapshots" / experiment_id
            snapshot_dir.mkdir(parents=True, exist_ok=True)
            
            # Save experiment info
            snapshot_file = snapshot_dir / "experiment_snapshot.json"
            with open(snapshot_file, 'w') as f:
                json.dump(asdict(info), f, indent=2, default=str)
            
            # Copy configurations
            config_dir = snapshot_dir / "configs"
            config_dir.mkdir(exist_ok=True)
            
            for config_type, config in info.configs.items():
                config_file = config_dir / f"{config_type}_config.yaml"
                with open(config_file, 'w') as f:
                    yaml.dump(config, f, default_flow_style=False, indent=2)
            
            # Create reproduction script
            self._create_reproduction_script(experiment_id, snapshot_dir)
            
            self.logger.info(f"Created experiment snapshot: {snapshot_file}")
            return str(snapshot_file)
            
        except Exception as e:
            self.logger.error(f"Failed to create experiment snapshot: {e}")
            raise
    
    def _save_configurations(self, experiment_id: str, configs: Dict[str, Any]):
        """Save configurations for an experiment."""
        config_dir = self.project_root / "configs" / experiment_id
        config_dir.mkdir(parents=True, exist_ok=True)
        
        for config_type, config in configs.items():
            config_file = config_dir / f"{config_type}_config.yaml"
            with open(config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)
    
    def _load_experiment_configs(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """Load configurations for an experiment."""
        config_dir = self.project_root / "configs" / experiment_id
        
        if not config_dir.exists():
            return None
        
        configs = {}
        for config_file in config_dir.glob("*_config.yaml"):
            config_type = config_file.stem.replace("_config", "")
            with open(config_file, 'r') as f:
                configs[config_type] = yaml.safe_load(f)
        
        return configs
    
    def _load_experiment_metrics(self, experiment_id: str) -> Optional[Dict[str, float]]:
        """Load final metrics for an experiment."""
        metrics_file = self.project_root / "experiment_versions" / f"{experiment_id}_metrics.json"
        
        if not metrics_file.exists():
            return None
        
        try:
            with open(metrics_file, 'r') as f:
                return json.load(f)
        except Exception:
            return None
    
    def _create_experiment_config(self, experiment_id: str, experiment_name: str, tracking_backend: str):
        """Create experiment configuration for tracking."""
        from onyx.server.features.ads.config_manager import ExperimentConfig
        
        return ExperimentConfig(
            experiment_name=experiment_name,
            project_name=self._get_project_name(),
            track_experiments=True,
            tracking_backend=tracking_backend,
            save_checkpoints=True,
            checkpoint_dir=str(self.project_root / "checkpoints"),
            log_metrics=["loss", "accuracy", "f1_score"],
            log_frequency=100,
            checkpoint_frequency=1
        )
    
    def _save_integrated_experiment_info(self, experiment_id: str, experiment_name: str, 
                                       commit_hash: str, configs: Dict[str, Any], 
                                       final_metrics: Dict[str, float]):
        """Save integrated experiment information."""
        info_dir = self.project_root / "integrated_experiments"
        info_dir.mkdir(exist_ok=True)
        
        info = IntegratedExperimentInfo(
            experiment_id=experiment_id,
            experiment_name=experiment_name,
            git_hash=commit_hash,
            branch=self.vc_manager.get_current_branch(),
            config_hash=str(hash(json.dumps(configs, sort_keys=True))),
            code_hash="",  # Will be filled by version control
            commit_date=datetime.now(),
            commit_message=f"End experiment: {experiment_name}",
            is_reproducible=True,
            dependencies=self.vc_manager._get_dependencies(),
            configs=configs,
            final_metrics=final_metrics,
            tags=self.vc_manager.get_experiment_tags(experiment_id)
        )
        
        info_file = info_dir / f"{experiment_id}.json"
        with open(info_file, 'w') as f:
            json.dump(asdict(info), f, indent=2, default=str)
    
    def _compare_configurations(self, experiment_infos: List[IntegratedExperimentInfo]) -> Dict[str, Any]:
        """Compare configurations between experiments."""
        differences = {}
        
        if len(experiment_infos) < 2:
            return differences
        
        # Compare each configuration type
        config_types = set()
        for info in experiment_infos:
            config_types.update(info.configs.keys())
        
        for config_type in config_types:
            configs = {}
            for info in experiment_infos:
                if config_type in info.configs:
                    configs[info.experiment_id] = info.configs[config_type]
            
            if len(configs) > 1:
                differences[config_type] = self._find_config_differences(configs)
        
        return differences
    
    def _compare_metrics(self, experiment_infos: List[IntegratedExperimentInfo]) -> Dict[str, Any]:
        """Compare metrics between experiments."""
        differences = {}
        
        if len(experiment_infos) < 2:
            return differences
        
        # Get all metric keys
        metric_keys = set()
        for info in experiment_infos:
            if info.final_metrics:
                metric_keys.update(info.final_metrics.keys())
        
        # Compare each metric
        for metric_key in metric_keys:
            values = {}
            for info in experiment_infos:
                if info.final_metrics and metric_key in info.final_metrics:
                    values[info.experiment_id] = info.final_metrics[metric_key]
            
            if len(values) > 1:
                differences[metric_key] = {
                    "values": values,
                    "min": min(values.values()),
                    "max": max(values.values()),
                    "range": max(values.values()) - min(values.values())
                }
        
        return differences
    
    def _find_config_differences(self, configs: Dict[str, Any]) -> Dict[str, Any]:
        """Find differences between configurations."""
        differences = {}
        
        # Get all keys
        all_keys = set()
        for config in configs.values():
            all_keys.update(self._flatten_dict(config).keys())
        
        # Compare each key
        for key in all_keys:
            values = {}
            for exp_id, config in configs.items():
                flat_config = self._flatten_dict(config)
                if key in flat_config:
                    values[exp_id] = flat_config[key]
            
            if len(set(values.values())) > 1:
                differences[key] = values
        
        return differences
    
    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        """Flatten a nested dictionary."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    def _generate_comparison_summary(self, experiment_infos: List[IntegratedExperimentInfo]) -> Dict[str, Any]:
        """Generate a summary of experiment comparison."""
        summary = {
            "total_experiments": len(experiment_infos),
            "date_range": {
                "earliest": min(info.commit_date for info in experiment_infos),
                "latest": max(info.commit_date for info in experiment_infos)
            },
            "branches": list(set(info.branch for info in experiment_infos)),
            "reproducible_experiments": sum(1 for info in experiment_infos if info.is_reproducible)
        }
        
        # Best performing experiment
        best_experiment = None
        best_metric = None
        
        for info in experiment_infos:
            if info.final_metrics and "accuracy" in info.final_metrics:
                if best_experiment is None or info.final_metrics["accuracy"] > best_metric:
                    best_experiment = info.experiment_id
                    best_metric = info.final_metrics["accuracy"]
        
        if best_experiment:
            summary["best_experiment"] = {
                "experiment_id": best_experiment,
                "accuracy": best_metric
            }
        
        return summary
    
    def _create_reproduction_script(self, experiment_id: str, snapshot_dir: Path):
        """Create a reproduction script for an experiment."""
        script_content = f'''#!/usr/bin/env python3
"""
Reproduction script for experiment {experiment_id}
Generated automatically by Integrated Version Control System
"""

import os
import sys
import subprocess
from pathlib import Path

def reproduce_experiment():
    """Reproduce the experiment {experiment_id}."""
    
    # Get the project root
    project_root = Path(__file__).parent.parent.parent
    
    # Checkout the correct git commit
    print(f"Checking out git commit for experiment {experiment_id}...")
    subprocess.run(["git", "checkout", "main"], cwd=project_root, check=True)
    
    # Load experiment info
    import json
    with open("{snapshot_dir}/experiment_snapshot.json", 'r') as f:
        experiment_info = json.load(f)
    
    git_hash = experiment_info['git_hash']
    subprocess.run(["git", "checkout", git_hash], cwd=project_root, check=True)
    
    print(f"Successfully checked out commit {git_hash}")
    print("Experiment ready for reproduction!")
    print("\\nTo run the experiment:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Run the experiment script")
    print("3. Check the configurations in configs/{experiment_id}/")

if __name__ == "__main__":
    reproduce_experiment()
'''
        
        script_file = snapshot_dir / "reproduce.py"
        with open(script_file, 'w') as f:
            f.write(script_content)
        
        # Make script executable
        os.chmod(script_file, 0o755)
    
    def _get_project_name(self) -> str:
        """Get the project name from the directory."""
        return self.project_root.name
    
    def _get_python_version(self) -> str:
        """Get the current Python version."""
        import sys
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    def _get_hardware_info(self) -> Dict[str, Any]:
        """Get hardware information."""
        import torch
        
        info = {
            "python_version": self._get_python_version(),
            "platform": os.name
        }
        
        if torch.cuda.is_available():
            info["gpu"] = torch.cuda.get_device_name(0)
            info["cuda_version"] = torch.version.cuda
            info["gpu_memory"] = torch.cuda.get_device_properties(0).total_memory
        else:
            info["gpu"] = "None"
        
        return info

# Utility functions
def create_integrated_vc(project_root: str = ".", auto_commit: bool = True) -> IntegratedVersionControl:
    """Create an integrated version control system."""
    return IntegratedVersionControl(project_root, auto_commit)

@contextmanager
def integrated_experiment_context(experiment_id: str, experiment_name: str, configs: Dict[str, Any]):
    """Context manager for integrated experiments."""
    vc = create_integrated_vc()
    try:
        commit_hash, tracker = vc.start_integrated_experiment(experiment_id, experiment_name, configs)
        yield vc, tracker, commit_hash
    finally:
        pass

# Example usage
if __name__ == "__main__":
    # Create integrated version control
    integrated_vc = create_integrated_vc()
    
    # Example experiment configurations
    configs = {
        "model": {
            "name": "test_model",
            "type": "transformer",
            "architecture": "bert-base-uncased",
            "input_size": 768,
            "output_size": 10
        },
        "training": {
            "batch_size": 32,
            "learning_rate": 2e-5,
            "epochs": 10
        },
        "experiment": {
            "experiment_name": "test_experiment",
            "tracking_backend": "local"
        }
    }
    
    # Start integrated experiment
    commit_hash, tracker = integrated_vc.start_integrated_experiment(
        "exp_001", "Test Integrated Experiment", configs
    )
    
    print(f"Started integrated experiment with commit: {commit_hash}")
    
    # Simulate training
    for step in range(100):
        # Simulate metrics
        metrics = {
            "loss": 1.0 - step * 0.01,
            "accuracy": step * 0.01
        }
        
        # Log metrics
        tracker.log_metrics(metrics, step=step)
        
        # Commit changes periodically
        if step % 20 == 0:
            integrated_vc.commit_experiment_changes(
                "exp_001", "Test Integrated Experiment", configs,
                f"Training step {step}", metrics
            )
    
    # End experiment
    final_metrics = {"loss": 0.1, "accuracy": 0.9}
    final_commit = integrated_vc.end_integrated_experiment(
        "exp_001", "Test Integrated Experiment", configs, final_metrics, "v1.0"
    )
    
    print(f"Ended integrated experiment with commit: {final_commit}")
    
    # Get experiment info
    info = integrated_vc.get_integrated_experiment_info("exp_001")
    if info:
        print(f"Experiment info: {info.experiment_name} - {info.git_hash}")
    
    # Create snapshot
    snapshot_file = integrated_vc.create_experiment_snapshot("exp_001")
    print(f"Created snapshot: {snapshot_file}") 