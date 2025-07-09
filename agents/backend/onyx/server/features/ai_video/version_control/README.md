# Version Control System

A comprehensive version control system for AI video generation projects, providing git integration, configuration versioning, and change tracking.

## Features

- **Git Management**: Automated git operations, branch management, and commit tracking
- **Configuration Versioning**: Track changes to configuration files with diff generation
- **Change Tracking**: Monitor file system changes with detailed history
- **Integrated Workflow**: Combine all features for seamless version control
- **Experiment Tracking**: Specialized support for ML experiments
- **Backup & Restore**: Automatic configuration backup and restoration

## Quick Start

```python
from version_control import create_version_control_system

# Initialize the system
vcs = create_version_control_system()

# Version a configuration
version_id, success = vcs.version_config_and_commit(
    "config.yaml",
    "Updated model parameters",
    author="developer"
)

# Start an experiment
exp_version = vcs.create_experiment_branch(
    "hyperparameter_optimization",
    "config.yaml",
    "Optimize hyperparameters"
)
```

## Components

### 1. Git Manager (`git_manager.py`)

Handles git repository operations with automation and best practices.

#### Key Features:
- Automated git operations
- Branch management (feature, experiment, hotfix)
- Commit message generation
- Configuration backup and restore
- Repository status monitoring

#### Usage:
```python
from version_control import GitManager

# Create git manager
git_mgr = GitManager()

# Create feature branch
git_mgr.create_branch("new_model", "feature")

# Stage and commit changes
git_mgr.stage_all_changes()
git_mgr.commit_changes("Add new model architecture", "feature")

# Push changes
git_mgr.push_changes()
```

### 2. Configuration Versioning (`config_versioning.py`)

Tracks changes to configuration files with detailed version history.

#### Key Features:
- Configuration change tracking
- Diff generation and visualization
- Version history and rollback
- Configuration validation
- Automatic backup and restore

#### Usage:
```python
from version_control import ConfigVersioning

# Create versioning system
config_versioning = ConfigVersioning()

# Version a configuration
version_id = config_versioning.create_version(
    "model_config.yaml",
    "Updated hyperparameters",
    author="researcher",
    tags=["optimization", "hyperparameters"]
)

# Compare versions
diff = config_versioning.compare_versions(version_id1, version_id2)

# Restore version
config_versioning.restore_version(version_id, "restored_config.yaml")
```

### 3. Change Tracker (`change_tracker.py`)

Monitors file system changes and provides detailed change history.

#### Key Features:
- File change monitoring
- Diff generation and visualization
- Change history with metadata
- Automatic change detection
- Change analytics and reporting

#### Usage:
```python
from version_control import ChangeTracker

# Create change tracker
change_tracker = ChangeTracker()

# Start monitoring
change_tracker.start_monitoring(["./models", "./config"])

# Track manual changes
change = change_tracker.track_file_change(
    "model.py",
    "modified",
    "Added new layer"
)

# Create change set
change_set_id = change_tracker.create_change_set(
    "Model architecture update",
    author="developer"
)
```

### 4. Integrated System (`__init__.py`)

Combines all components for seamless version control workflow.

#### Key Features:
- Unified interface for all version control operations
- Experiment-specific workflows
- Automated git integration
- Comprehensive project history

#### Usage:
```python
from version_control import VersionControlSystem

# Create integrated system
vcs = VersionControlSystem()

# Version config and commit
version_id, success = vcs.version_config_and_commit(
    "config.yaml",
    "Initial configuration",
    author="developer"
)

# Start experiment
exp_version = vcs.create_experiment_branch(
    "experiment_name",
    "config.yaml",
    "Experiment description"
)

# Finish experiment
results = {"loss": 0.1, "accuracy": 0.95}
success = vcs.finish_experiment("experiment_name", results)
```

## Advanced Usage

### Experiment Workflow

```python
# Start experiment
exp_version = start_experiment(
    "hyperparameter_optimization",
    "config.yaml",
    "Find optimal hyperparameters"
)

# ... run experiment ...

# Finish experiment
results = {
    "final_loss": 0.0234,
    "accuracy": 0.9456,
    "training_time": "2h 15m",
    "best_epoch": 87
}

success = finish_experiment("hyperparameter_optimization", results)
```

### Configuration Management

```python
# Quick version config
version_id = quick_version_config(
    "model_config.yaml",
    "Updated learning rate",
    author="developer"
)

# Backup configuration
backup_file = config_versioning.backup_config("config.yaml")

# Restore configuration
config_versioning.restore_config(backup_file, "config.yaml")
```

### Change Monitoring

```python
# Start monitoring specific directories
change_tracker.start_monitoring([
    "./models",
    "./config", 
    "./data"
])

# Get change statistics
stats = change_tracker.get_change_statistics()
print(f"Total changes: {stats['total_changes']}")

# Export changes
change_tracker.export_changes(
    "changes_export.json",
    since="2024-01-01T00:00:00"
)
```

## Configuration

### Git Configuration

```python
from version_control import GitConfig

config = GitConfig(
    repo_path=".",
    auto_commit=True,
    auto_push=False,
    main_branch="main",
    feature_branch_prefix="feature/",
    experiment_branch_prefix="experiment/"
)
```

### Change Tracking Configuration

```python
# Configure file monitoring
change_tracker.start_monitoring(
    paths=["./models", "./config"],
    recursive=True
)

# Set debounce time for file changes
change_tracker.file_handler.debounce_time = 2.0
```

## Best Practices

### 1. Git Workflow

- Use descriptive commit messages
- Create feature branches for new development
- Use experiment branches for ML experiments
- Tag important versions
- Regular pushes to remote repository

### 2. Configuration Management

- Version all configuration changes
- Use descriptive version descriptions
- Tag configurations with meaningful labels
- Regular backups of important configurations
- Document configuration changes

### 3. Change Tracking

- Monitor all important directories
- Create change sets for related changes
- Use descriptive change descriptions
- Regular cleanup of old changes
- Export changes for backup

### 4. Experiment Management

- Use experiment branches for ML experiments
- Version configurations at experiment start
- Document experiment results
- Tag successful experiments
- Merge experiments to main when validated

## File Structure

```
version_control/
├── __init__.py              # Main module with integrated system
├── git_manager.py           # Git repository management
├── config_versioning.py     # Configuration versioning
├── change_tracker.py        # File change tracking
├── example_usage.py         # Comprehensive examples
└── README.md               # This documentation
```

## Dependencies

- `git` (system command)
- `watchdog` (for file monitoring)
- `pyyaml` (for YAML configuration files)
- `difflib` (for diff generation)

## Installation

```bash
# Install dependencies
pip install watchdog pyyaml

# Ensure git is available
git --version
```

## Examples

See `example_usage.py` for comprehensive examples demonstrating all features.

## Troubleshooting

### Common Issues

1. **Git not initialized**: The system will automatically initialize git if needed
2. **File monitoring not working**: Ensure `watchdog` is installed and paths exist
3. **Permission errors**: Check file and directory permissions
4. **Large diffs**: Consider excluding large files from tracking

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Follow the existing code style
2. Add tests for new features
3. Update documentation
4. Use meaningful commit messages

## License

This module is part of the AI Video system and follows the same license terms. 