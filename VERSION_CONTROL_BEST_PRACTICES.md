# 🔄 Version Control Best Practices for Diffusion Models

## Overview

This guide provides comprehensive best practices for using Git version control with diffusion models, including code tracking, configuration management, experiment versioning, and collaboration workflows.

## 📋 Table of Contents

1. [Git Repository Setup](#git-repository-setup)
2. [File Organization](#file-organization)
3. [Branching Strategy](#branching-strategy)
4. [Commit Conventions](#commit-conventions)
5. [Configuration Management](#configuration-management)
6. [Experiment Tracking](#experiment-tracking)
7. [Model Checkpointing](#model-checkpointing)
8. [Collaboration Workflows](#collaboration-workflows)
9. [Security Considerations](#security-considerations)
10. [Automation and CI/CD](#automation-and-cicd)

## 🚀 Git Repository Setup

### Initial Setup

```bash
# Initialize repository
git init

# Configure user
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Create comprehensive .gitignore
# (See version_control_manager.py for complete .gitignore)
```

### Repository Structure

```
diffusion-models-project/
├── .git/
├── .gitignore
├── README.md
├── requirements.txt
├── setup.py
├── config/
│   ├── default.yaml
│   ├── experiments/
│   └── local/
├── core/
│   ├── __init__.py
│   ├── diffusion_models.py
│   ├── diffusion_training.py
│   └── version_control_manager.py
├── data/
│   ├── raw/
│   ├── processed/
│   └── .gitkeep
├── models/
│   ├── checkpoints/
│   └── .gitkeep
├── experiments/
│   ├── experiment_001/
│   └── experiment_002/
├── logs/
├── tests/
├── docs/
└── scripts/
```

## 📁 File Organization

### Code Files

- **Core modules**: `core/diffusion_*.py`
- **Training scripts**: `scripts/train_*.py`
- **Evaluation scripts**: `scripts/evaluate_*.py`
- **Utility functions**: `utils/`

### Configuration Files

- **Default configs**: `config/default.yaml`
- **Experiment configs**: `config/experiments/`
- **Local overrides**: `config/local/` (gitignored)

### Data and Models

- **Raw data**: `data/raw/` (gitignored)
- **Processed data**: `data/processed/`
- **Model checkpoints**: `models/checkpoints/` (gitignored)
- **Experiment outputs**: `experiments/`

## 🌿 Branching Strategy

### Main Branches

```
main (or master)
├── develop
├── feature/diffusion-pipeline
├── feature/training-optimization
├── experiment/stable-diffusion-v1-5
├── experiment/stable-diffusion-xl
└── hotfix/critical-bug-fix
```

### Branch Naming Conventions

```bash
# Feature branches
feature/diffusion-pipeline
feature/training-optimization
feature/gradio-interface

# Experiment branches
experiment/stable-diffusion-v1-5
experiment/stable-diffusion-xl
experiment/custom-dataset

# Bug fixes
bugfix/memory-leak
hotfix/critical-training-issue

# Release branches
release/v1.0.0
release/v1.1.0
```

### Branch Workflow

```python
# Using VersionControlManager
vc_manager = VersionControlManager()

# Create feature branch
vc_manager._git_branch("feature/new-diffusion-model")

# Create experiment branch
vc_manager.create_experiment_branch("stable-diffusion-xl")

# Create backup branch
vc_manager.create_backup_branch("backup_before_major_changes")
```

## 💬 Commit Conventions

### Commit Message Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes
- **refactor**: Code refactoring
- **test**: Test changes
- **chore**: Maintenance tasks

### Examples

```bash
# Feature commits
feat(diffusion): add stable diffusion XL pipeline
feat(training): implement gradient accumulation
feat(gradio): create interactive demo interface

# Bug fixes
fix(memory): resolve CUDA memory leak in training
fix(config): correct learning rate scheduler config
fix(data): handle missing image files gracefully

# Documentation
docs(readme): update installation instructions
docs(api): add docstrings to diffusion models

# Configuration
config(experiment): update hyperparameters for experiment_001
config(model): add new model configuration
```

### Automated Commit Messages

```python
# Using VersionControlManager
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Configuration changes
vc_manager.commit_configuration_changes(
    ["config/experiment_001.yaml"],
    f"Update experiment configuration - {timestamp}"
)

# Model changes
vc_manager.commit_model_changes(
    ["core/diffusion_models.py"],
    "stable-diffusion-xl"
)
```

## ⚙️ Configuration Management

### Configuration File Structure

```yaml
# config/default.yaml
model:
  name: "stable-diffusion-v1-5"
  pretrained: true
  device: "cuda"

training:
  learning_rate: 1e-4
  batch_size: 4
  epochs: 100
  optimizer: "adamw"
  scheduler: "cosine"

data:
  dataset_path: "data/processed"
  image_size: 512
  num_workers: 4

experiment:
  name: "default_experiment"
  tracking: "wandb"
  checkpoint_dir: "models/checkpoints"
```

### Environment-Specific Configs

```yaml
# config/local/override.yaml (gitignored)
training:
  batch_size: 2  # Override for local GPU
  device: "cuda:0"

data:
  dataset_path: "/local/path/to/dataset"
```

### Configuration Versioning

```python
# Save configuration snapshots
config = {
    "model": "stable-diffusion-v1-5",
    "learning_rate": 1e-4,
    "batch_size": 4
}

vc_manager.save_configuration_snapshot(config, "experiment_001")
```

## 🧪 Experiment Tracking

### Experiment Lifecycle

```python
# Initialize experiment tracker
experiment_tracker = DiffusionExperimentTracker(vc_manager)

# Start experiment
config = {
    "model": "stable-diffusion-v1-5",
    "learning_rate": 1e-4,
    "batch_size": 4
}

experiment_tracker.start_experiment("stable-diffusion-v1-5", config)

# Commit training progress
for epoch in range(num_epochs):
    metrics = {"loss": loss_value, "accuracy": accuracy_value}
    experiment_tracker.commit_training_progress(epoch, metrics)

# Finish experiment
final_metrics = {"final_loss": final_loss, "final_accuracy": final_accuracy}
experiment_tracker.finish_experiment(final_metrics)
```

### Experiment Tags

```python
# Create experiment tags
vc_manager.tag_experiment("stable-diffusion-v1-5", "v1.0.0")
vc_manager.tag_experiment("stable-diffusion-xl", "v2.0.0")

# Create release tags
vc_manager.create_release_tag("1.0.0", "First stable release")
vc_manager.create_release_tag("1.1.0", "Performance improvements")
```

## 💾 Model Checkpointing

### Checkpoint Management

```python
# Track model checkpoints
checkpoint_path = "models/checkpoints/model_epoch_100.pt"
vc_manager.track_model_checkpoint(checkpoint_path, "stable-diffusion-v1-5")

# Checkpoint naming convention
# {experiment_name}_{model_name}_{epoch}_{timestamp}.pt
# stable-diffusion-v1-5_unet_100_20231201_143022.pt
```

### Checkpoint Versioning

```python
# Save checkpoint with metadata
checkpoint_data = {
    "model_state_dict": model.state_dict(),
    "optimizer_state_dict": optimizer.state_dict(),
    "epoch": epoch,
    "loss": loss,
    "config": config,
    "git_commit": vc_manager.get_current_commit(),
    "timestamp": datetime.now().isoformat()
}

torch.save(checkpoint_data, checkpoint_path)
```

## 👥 Collaboration Workflows

### Team Workflow

1. **Fork and Clone**
   ```bash
   git clone https://github.com/team/diffusion-models.git
   git remote add upstream https://github.com/team/diffusion-models.git
   ```

2. **Feature Development**
   ```bash
   git checkout -b feature/new-diffusion-model
   # Make changes
   git add .
   git commit -m "feat(diffusion): add new diffusion model"
   git push origin feature/new-diffusion-model
   ```

3. **Pull Request**
   - Create PR from feature branch to develop
   - Code review and testing
   - Merge to develop

4. **Release Process**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b release/v1.0.0
   # Update version numbers
   git commit -m "chore(release): prepare v1.0.0"
   git tag v1.0.0
   git push origin release/v1.0.0 --tags
   ```

### Code Review Checklist

- [ ] Code follows project conventions
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Configuration changes documented
- [ ] No sensitive data committed
- [ ] Performance impact considered

## 🔒 Security Considerations

### Sensitive Data Protection

```bash
# .gitignore additions
config/local/
*.env
.env.local
secrets/
api_keys/
```

### API Key Management

```python
# Use environment variables
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("HUGGINGFACE_API_KEY")
```

### Large File Management

```bash
# Use Git LFS for large files
git lfs track "*.safetensors"
git lfs track "*.bin"
git lfs track "data/raw/*.zip"
```

## 🤖 Automation and CI/CD

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

### GitHub Actions

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          python -m pytest tests/
      - name: Check code style
        run: |
          black --check .
          flake8 .
```

### Automated Version Control

```python
# Automated commit on training completion
def auto_commit_training_results(experiment_name, metrics, checkpoint_path):
    """Automatically commit training results."""
    vc_manager = VersionControlManager()
    
    # Commit metrics
    metrics_file = f"experiments/{experiment_name}/metrics.json"
    with open(metrics_file, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    vc_manager._git_add([metrics_file])
    vc_manager._git_commit(f"Auto-commit: Training results for {experiment_name}")
    
    # Track checkpoint
    if checkpoint_path:
        vc_manager.track_model_checkpoint(checkpoint_path, experiment_name)
```

## 📊 Monitoring and Analytics

### Git Analytics

```python
# Get repository statistics
def get_repo_stats():
    """Get repository statistics."""
    vc_manager = VersionControlManager()
    
    # Get commit history
    commits = vc_manager.get_experiment_history()
    
    # Get file changes
    status = vc_manager.get_status()
    
    # Get experiment summary
    experiment_summary = experiment_tracker.get_experiment_summary("stable-diffusion-v1-5")
    
    return {
        "total_commits": len(commits),
        "current_branch": status.get("branch"),
        "modified_files": status.get("modified_files", []),
        "experiment_files": experiment_summary
    }
```

### Experiment Comparison

```python
# Compare experiments
def compare_experiments(exp1, exp2):
    """Compare two experiments."""
    vc_manager = VersionControlManager()
    
    summary1 = experiment_tracker.get_experiment_summary(exp1)
    summary2 = experiment_tracker.get_experiment_summary(exp2)
    
    # Compare configurations
    config1 = load_config(summary1["config_files"][-1])
    config2 = load_config(summary2["config_files"][-1])
    
    # Compare metrics
    metrics1 = load_metrics(summary1["metrics_files"][-1])
    metrics2 = load_metrics(summary2["metrics_files"][-1])
    
    return {
        "config_diff": compare_configs(config1, config2),
        "metrics_diff": compare_metrics(metrics1, metrics2)
    }
```

## 🎯 Best Practices Summary

### Do's ✅

- Use descriptive commit messages
- Create feature branches for new development
- Tag releases and experiments
- Track configuration changes
- Use .gitignore for sensitive data
- Implement automated testing
- Document changes in README
- Use semantic versioning

### Don'ts ❌

- Commit large files directly
- Commit sensitive data (API keys, passwords)
- Use generic commit messages
- Work directly on main branch
- Ignore merge conflicts
- Forget to update documentation
- Commit broken code
- Use force push on shared branches

### Tools and Resources

- **Git LFS**: For large file management
- **Pre-commit hooks**: For code quality
- **GitHub Actions**: For CI/CD
- **DVC**: For data versioning
- **Weights & Biases**: For experiment tracking
- **MLflow**: For model versioning

## 📚 Additional Resources

- [Git Documentation](https://git-scm.com/doc)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/)
- [GitHub Flow](https://guides.github.com/introduction/flow/)
- [Git LFS](https://git-lfs.github.com/)

---

*This guide provides a comprehensive framework for version control in diffusion models projects. Adapt these practices to your specific needs and team requirements.*
