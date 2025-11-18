# Documentation Index

## 📚 Guías Principales

### Arquitectura y Estructura
- **[PROJECT_STRUCTURE.md](../PROJECT_STRUCTURE.md)**: Estructura del proyecto
- **[MODULAR_ARCHITECTURE_V2.md](../MODULAR_ARCHITECTURE_V2.md)**: Arquitectura modular
- **[HEXAGONAL_ARCHITECTURE.md](../HEXAGONAL_ARCHITECTURE.md)**: Arquitectura hexagonal

### Machine Learning
- **[ML_IMPROVEMENTS_V2.md](../ML_IMPROVEMENTS_V2.md)**: Mejoras de ML
- **[ADVANCED_TRAINING_GUIDE.md](../ADVANCED_TRAINING_GUIDE.md)**: Guía de entrenamiento avanzado

### Performance
- **[PERFORMANCE_OPTIMIZATIONS.md](../PERFORMANCE_OPTIMIZATIONS.md)**: Optimizaciones básicas
- **[ULTIMATE_OPTIMIZATION_GUIDE.md](../ULTIMATE_OPTIMIZATION_GUIDE.md)**: Optimizaciones avanzadas

### Deployment
- **[DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md)**: Guía de deployment
- **[QUICK_START.md](../QUICK_START.md)**: Inicio rápido

## 🎯 Por Tarea

### Empezar
1. [QUICK_START.md](../QUICK_START.md)
2. [PROJECT_STRUCTURE.md](../PROJECT_STRUCTURE.md)
3. [README.md](../README.md)

### Entrenar Modelos
1. [ML_IMPROVEMENTS_V2.md](../ML_IMPROVEMENTS_V2.md)
2. [ADVANCED_TRAINING_GUIDE.md](../ADVANCED_TRAINING_GUIDE.md)
3. [MODULAR_ARCHITECTURE_V2.md](../MODULAR_ARCHITECTURE_V2.md)

### Optimizar Performance
1. [PERFORMANCE_OPTIMIZATIONS.md](../PERFORMANCE_OPTIMIZATIONS.md)
2. [ULTIMATE_OPTIMIZATION_GUIDE.md](../ULTIMATE_OPTIMIZATION_GUIDE.md)

### Deployment
1. [DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md)
2. [Dockerfile](../Dockerfile)
3. [docker-compose.yml](../docker-compose.yml)

## 📖 Referencias Rápidas

### Imports Comunes

```python
# ML Components
from ml import ViTSkinAnalyzer, Trainer, SkinDataset

# Training
from ml.training import Trainer, MultiTaskLoss, get_optimizer

# Data
from ml.data import SkinDataset, get_train_transforms

# Inference
from ml.inference import FastInferenceEngine

# Experiments
from ml.experiments import ExperimentTracker

# Optimization
from utils.optimization import compile_model
from utils.advanced_optimization import enable_all_optimizations
```

### Configuración

```python
from config import load_config

config = load_config("config/model_config.yaml")
```








