# Version Control System for Key Messages ML Pipeline

A comprehensive version control system that provides Git integration, configuration versioning, model versioning, and change tracking for the ML pipeline.

## Features

- **Git Integration**: Programmatic Git operations with automatic commit management
- **Configuration Versioning**: Snapshot, compare, and restore configuration changes
- **Model Versioning**: Register, track, and manage ML model versions
- **Change Tracking**: Log and monitor all changes to the pipeline
- **Automated Workflows**: Integrated version control for ML operations
- **Search and Filtering**: Advanced search capabilities across all versioned items
- **Export/Import**: Backup and restore version control data
- **Statistics and Analytics**: Comprehensive reporting on changes and usage

## Architecture

```
version_control/
├── __init__.py              # Main module exports and convenience functions
├── git_manager.py           # Git operations and repository management
├── config_versioning.py     # Configuration snapshots and versioning
├── model_versioning.py      # Model registration and version management
├── change_tracking.py       # Change logging and tracking
├── tests/                   # Comprehensive test suite
│   └── test_version_control.py
└── README.md               # This documentation
```

## Installation

The version control system is included with the ML pipeline. No additional installation is required.

## Quick Start

### 1. Basic Setup

```python
from ml.version_control import (
    create_git_manager,
    create_config_version_manager,
    create_model_version_manager,
    create_change_tracker
)

# Initialize version control components
git_manager = create_git_manager()
config_manager = create_config_version_manager()
model_manager = create_model_version_manager()
change_tracker = create_change_tracker()
```

### 2. Git Repository Management

```python
# Initialize Git repository
if not git_manager.is_repo():
    git_manager.init_repo()

# Stage and commit changes
git_manager.stage_all()
commit_hash = git_manager.commit("Update model configuration")

# Create tags for releases
git_manager.create_tag("v1.0.0", "Release version 1.0.0")

# Push changes
git_manager.push()
```

### 3. Configuration Versioning

```python
# Create configuration snapshot
config = {
    "models": {"gpt2": {"learning_rate": 1e-4}},
    "training": {"epochs": 10}
}

snapshot = config_manager.create_snapshot(
    config=config,
    description="Initial configuration",
    author="ML Engineer",
    tags=["production", "gpt2"]
)

# Compare configurations
diff = config_manager.compare_versions("v1.0.0", "v1.1.0")
print(f"Changes: {diff.get_change_count()}")

# Restore previous configuration
restored_config = config_manager.restore_version("v1.0.0")
```

### 4. Model Versioning

```python
# Register a new model version
model_version = model_manager.register_model(
    model_path="./models/gpt2_key_messages.pt",
    model_name="gpt2_key_messages",
    version="1.0.0",
    metadata={
        "architecture": "gpt2",
        "dataset": "key_messages_v1",
        "accuracy": 0.85,
        "training_time": "2h 30m"
    },
    tags=["production", "gpt2"]
)

# List model versions
versions = model_manager.list_versions("gpt2_key_messages")
for version in versions:
    print(f"Version {version.version}: {version.metadata.accuracy}")

# Load specific model version
model = model_manager.load_model("gpt2_key_messages", "1.0.0")
```

### 5. Change Tracking

```python
# Log configuration changes
change_tracker.log_config_update(
    old_config=old_config,
    new_config=new_config,
    description="Updated learning rate from 1e-4 to 5e-5"
)

# Log model training
change_tracker.log_model_training(
    model_name="gpt2_key_messages",
    model_path="./models/gpt2_v2.pt",
    metrics={"accuracy": 0.87, "loss": 0.13},
    training_time="3h 15m"
)

# Get change history
changes = change_tracker.get_changes(
    change_type=ChangeType.CONFIG_UPDATE,
    limit=10
)
```

## Configuration

### Git Configuration

```yaml
version_control:
  git:
    repo_path: "./ml_pipeline"
    user_name: "ML Pipeline"
    user_email: "ml-pipeline@example.com"
    auto_commit: true
    auto_push: false
    commit_message_template: "Auto-commit: {change_type} - {description}"
    branch: "main"
    remote: "origin"
```

### Configuration Versioning

```yaml
version_control:
  config_versioning:
    config_dir: "./config_versions"
    auto_snapshot: true
    max_history: 50
    compression: true
```

### Model Versioning

```yaml
version_control:
  model_versioning:
    registry_path: "./model_registry"
    auto_version: true
    version_scheme: "semantic"  # semantic, timestamp, hash
    compression: true
    metadata_schema:
      required_fields: ["architecture", "dataset", "accuracy"]
      optional_fields: ["training_time", "parameters", "description"]
```

### Change Tracking

```yaml
version_control:
  change_tracking:
    log_file: "./change_log.json"
    auto_log: true
    include_metadata: true
    max_entries: 1000
```

## Advanced Usage

### 1. Integrated Workflow

```python
from ml.version_control import VersionControlWorkflow

class MLVersionControl:
    def __init__(self, config):
        self.workflow = VersionControlWorkflow(config["version_control"])
    
    def update_configuration(self, new_config, description):
        """Update configuration with automatic versioning."""
        # Create config snapshot
        snapshot = self.workflow.config_manager.create_snapshot(
            config=new_config,
            description=description
        )
        
        # Log change
        self.workflow.change_tracker.log_change(
            change_type=ChangeType.CONFIG_UPDATE,
            description=description,
            affected_files=["config.yaml"]
        )
        
        # Git operations
        self.workflow.git_manager.stage_all()
        self.workflow.git_manager.commit(f"Config update: {description}")
        
        return snapshot.version
    
    def register_model(self, model_path, model_name, version, metadata):
        """Register model with automatic versioning."""
        # Register model version
        model_version = self.workflow.model_manager.register_model(
            model_path=model_path,
            model_name=model_name,
            version=version,
            metadata=metadata
        )
        
        # Log change
        self.workflow.change_tracker.log_change(
            change_type=ChangeType.MODEL_REGISTRATION,
            description=f"Registered {model_name} v{version}",
            affected_files=[model_path]
        )
        
        # Git operations
        self.workflow.git_manager.stage_all()
        self.workflow.git_manager.commit(f"Model registration: {model_name} v{version}")
        
        return model_version

# Usage
ml_vc = MLVersionControl(config)

# Update configuration
config_version = ml_vc.update_configuration(
    new_config=updated_config,
    description="Optimized hyperparameters for production"
)

# Register model
model_version = ml_vc.register_model(
    model_path="./models/gpt2_final.pt",
    model_name="gpt2_key_messages",
    version="1.1.0",
    metadata={"accuracy": 0.89, "training_time": "4h 30m"}
)
```

### 2. Automated Version Control

```python
from ml.version_control import VersionControlWorkflow
from ml.experiment_tracking import create_tracker

class AutomatedVersionControl:
    def __init__(self, config):
        self.workflow = VersionControlWorkflow(config["version_control"])
        self.tracker = create_tracker(config["experiment_tracking"])
    
    def on_config_change(self, old_config, new_config):
        """Automatically version configuration changes."""
        diff = self._compute_config_diff(old_config, new_config)
        
        if diff.has_changes():
            version = self.workflow.update_configuration(
                new_config=new_config,
                description=f"Config update: {diff.summary()}"
            )
            
            # Log to experiment tracker
            self.tracker.log_metrics({
                "config_version": version,
                "config_changes": len(diff.changes)
            })
    
    def on_model_save(self, model_path, model_name, metadata):
        """Automatically version model saves."""
        version = self._generate_version(model_name)
        
        model_version = self.workflow.register_model(
            model_path=model_path,
            model_name=model_name,
            version=version,
            metadata=metadata
        )
        
        # Log to experiment tracker
        self.tracker.log_metrics({
            "model_version": version,
            "model_accuracy": metadata.get("accuracy", 0)
        })
        
        return model_version
```

### 3. Model Registry API

```python
from ml.version_control import ModelRegistry

# Initialize registry
registry = ModelRegistry("./model_registry")

# Register model
registry.register(
    name="gpt2_key_messages",
    version="1.0.0",
    path="./models/gpt2.pt",
    metadata={
        "architecture": "gpt2",
        "dataset": "key_messages_v1",
        "accuracy": 0.85,
        "training_time": "2h 30m",
        "framework": "pytorch",
        "python_version": "3.9"
    }
)

# List models
models = registry.list_models()
for model in models:
    print(f"{model.name}: {model.latest_version}")

# Get model info
model_info = registry.get_model("gpt2_key_messages")
print(f"Versions: {model_info.versions}")
print(f"Latest: {model_info.latest_version}")

# Load model
model = registry.load_model("gpt2_key_messages", "1.0.0")
```

### 4. Configuration Diff Visualization

```python
from ml.version_control import ConfigDiff

# Create diff
diff = ConfigDiff(old_config, new_config)

# Print human-readable diff
print("Configuration Changes:")
for change in diff.changes:
    print(f"  {change.path}: {change.old_value} -> {change.new_value}")

# Generate diff report
report = diff.generate_report()
print(f"Total changes: {report.total_changes}")
print(f"Breaking changes: {report.breaking_changes}")

# Export diff to file
diff.export_to_file("config_diff.json")
```

## API Reference

### GitManager

#### Methods

- `init_repo()`: Initialize a new Git repository
- `is_repo()`: Check if directory is a Git repository
- `stage_file(file_path)`: Stage a specific file
- `stage_all()`: Stage all changes
- `commit(message, author)`: Create a commit
- `push(branch, remote)`: Push changes to remote
- `pull(branch, remote)`: Pull changes from remote
- `create_branch(branch_name, checkout)`: Create a new branch
- `checkout_branch(branch_name)`: Checkout a branch
- `create_tag(tag_name, message)`: Create a tag
- `list_branches()`: List all branches
- `list_tags()`: List all tags
- `get_commit_history(limit)`: Get commit history
- `get_file_history(file_path, limit)`: Get file history
- `diff_file(file_path, commit1, commit2)`: Get file diff
- `diff_all(commit1, commit2)`: Get all changes diff
- `status()`: Get repository status
- `get_repo_info()`: Get comprehensive repository information

### ConfigVersionManager

#### Methods

- `create_snapshot(config, description, author, tags, version)`: Create configuration snapshot
- `load_snapshot(version)`: Load configuration snapshot
- `get_history(limit)`: Get configuration history
- `compare_versions(version1, version2)`: Compare two versions
- `restore_version(version)`: Restore configuration to version
- `delete_version(version)`: Delete a version
- `search_versions(query)`: Search for versions
- `get_version_info(version)`: Get version information
- `export_version(version, export_path)`: Export version
- `import_version(import_path)`: Import version
- `cleanup_old_versions(keep_count)`: Clean up old versions

### ModelVersionManager

#### Methods

- `register_model(model_path, model_name, metadata, version, tags)`: Register model
- `get_model_info(model_name)`: Get model information
- `list_models()`: List all models
- `list_versions(model_name)`: List model versions
- `get_metadata(model_name, version)`: Get model metadata
- `load_model(model_name, version, device)`: Load model
- `delete_version(model_name, version)`: Delete model version
- `search_models(query)`: Search for models
- `export_model(model_name, version, export_path)`: Export model
- `import_model(model_path, model_name, metadata, version)`: Import model
- `cleanup_old_versions(model_name, keep_count)`: Clean up old versions

### ChangeTracker

#### Methods

- `log_change(change_type, description, author, affected_files, metadata, tags, severity)`: Log change
- `log_config_update(old_config, new_config, description, author)`: Log config update
- `log_model_training(model_name, model_path, metrics, training_time, description, author)`: Log model training
- `log_model_registration(model_name, version, metadata, description, author)`: Log model registration
- `log_code_change(files_changed, commit_hash, description, author)`: Log code change
- `log_experiment_run(experiment_name, metrics, description, author)`: Log experiment run
- `get_changes(change_type, author, severity, limit, start_time, end_time)`: Get filtered changes
- `get_change_log(limit)`: Get complete change log
- `get_entry(entry_id)`: Get specific entry
- `delete_entry(entry_id)`: Delete entry
- `update_entry(entry_id, **kwargs)`: Update entry
- `search_changes(query)`: Search for changes
- `get_statistics()`: Get change statistics
- `export_log(export_path, format)`: Export log
- `import_log(import_path, format)`: Import log
- `clear_log()`: Clear all entries

## Data Models

### GitConfig

```python
@dataclass
class GitConfig:
    repo_path: str = "."
    user_name: str = "ML Pipeline"
    user_email: str = "ml-pipeline@example.com"
    auto_commit: bool = True
    auto_push: bool = False
    commit_message_template: str = "Auto-commit: {change_type} - {description}"
    branch: str = "main"
    remote: str = "origin"
```

### ConfigSnapshot

```python
@dataclass
class ConfigSnapshot:
    version: str
    config: Dict[str, Any]
    description: str
    timestamp: float
    author: str
    tags: List[str]
    hash: str
    file_path: str
```

### ModelVersion

```python
@dataclass
class ModelVersion:
    name: str
    version: str
    path: str
    metadata: ModelMetadata
    hash: str
    file_size: int
    created_at: float
```

### ChangeEntry

```python
@dataclass
class ChangeEntry:
    id: str
    change_type: ChangeType
    description: str
    timestamp: float
    author: str
    affected_files: List[str]
    metadata: Dict[str, Any]
    tags: List[str]
    severity: str = "info"
```

## Best Practices

### 1. Git Workflow

- Always initialize the repository before using version control
- Use descriptive commit messages
- Create tags for important releases
- Regularly push changes to remote repository
- Use branches for feature development

### 2. Configuration Management

- Create snapshots before making significant changes
- Use descriptive tags for easy identification
- Regularly clean up old versions
- Export important configurations for backup
- Document breaking changes

### 3. Model Versioning

- Register models immediately after training
- Include comprehensive metadata
- Use semantic versioning for production models
- Tag models with appropriate labels
- Regularly clean up old model versions

### 4. Change Tracking

- Log all significant changes
- Use appropriate change types and severity levels
- Include relevant metadata
- Search and analyze change patterns
- Export logs for compliance and auditing

### 5. Integration

- Integrate version control into your ML workflow
- Automate versioning where possible
- Use consistent naming conventions
- Monitor version control statistics
- Regular backups of version control data

## Troubleshooting

### Common Issues

1. **Git repository not initialized**
   ```python
   if not git_manager.is_repo():
       git_manager.init_repo()
   ```

2. **Configuration snapshot creation fails**
   - Check file permissions
   - Ensure config directory exists
   - Verify configuration format

3. **Model registration fails**
   - Check model file exists
   - Verify metadata format
   - Ensure registry directory exists

4. **Change tracking not working**
   - Check log file permissions
   - Verify log directory exists
   - Check for disk space issues

### Error Handling

```python
try:
    snapshot = config_manager.create_snapshot(config, "Test snapshot")
except Exception as e:
    logger.error(f"Failed to create snapshot: {e}")
    # Handle error appropriately
```

### Debugging

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance Considerations

### 1. Large Configurations

- Use compression for large configuration files
- Limit history size to prevent disk space issues
- Consider incremental snapshots for large changes

### 2. Model Storage

- Use compression for large model files
- Implement cleanup strategies for old versions
- Consider external storage for very large models

### 3. Change Logging

- Limit log size to prevent performance issues
- Use appropriate log levels
- Implement log rotation

### 4. Git Operations

- Batch Git operations when possible
- Use appropriate Git configuration
- Consider shallow clones for large repositories

## Security Considerations

### 1. Access Control

- Implement appropriate file permissions
- Use secure authentication for Git operations
- Restrict access to version control data

### 2. Data Protection

- Encrypt sensitive configuration data
- Implement secure model storage
- Use secure change logging

### 3. Audit Trail

- Maintain comprehensive change logs
- Implement access logging
- Regular security audits

## Future Enhancements

### Planned Features

1. **Distributed Version Control**: Support for distributed repositories
2. **Cloud Integration**: Integration with cloud storage services
3. **Advanced Analytics**: Enhanced reporting and analytics
4. **Web Interface**: Web-based version control interface
5. **API Enhancements**: RESTful API for version control operations
6. **Plugin System**: Extensible plugin architecture
7. **Real-time Collaboration**: Real-time collaboration features
8. **Advanced Search**: Full-text search capabilities

### Contributing

To contribute to the version control system:

1. Follow the existing code style
2. Add comprehensive tests
3. Update documentation
4. Submit pull requests with detailed descriptions

## Support

For support and questions:

1. Check the troubleshooting section
2. Review the API documentation
3. Examine the test cases for examples
4. Create an issue with detailed information

## License

This version control system is part of the Key Messages ML Pipeline and follows the same license terms. 