"""
🚀 Sistema de Inteligencia Artificial Distribuida Avanzado
Integrado con la Arquitectura Modular Extrema

Este sistema implementa:
- Inteligencia artificial distribuida
- Aprendizaje federado avanzado
- Optimización automática de hiperparámetros
- Gestión inteligente de recursos
- Auto-scaling basado en IA
"""

import asyncio
import logging
import uuid
import json
import time
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import optuna
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import psutil
import GPUtil

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIStrategyType(Enum):
    """Tipos de estrategias de IA."""
    FEDERATED_LEARNING = "federated_learning"
    DISTRIBUTED_TRAINING = "distributed_training"
    HYPERPARAMETER_OPTIMIZATION = "hyperparameter_optimization"
    AUTO_SCALING = "auto_scaling"
    RESOURCE_OPTIMIZATION = "resource_optimization"
    INTELLIGENT_ROUTING = "intelligent_routing"

class AIOptimizationType(Enum):
    """Tipos de optimización de IA."""
    BAYESIAN_OPTIMIZATION = "bayesian_optimization"
    GENETIC_ALGORITHM = "genetic_algorithm"
    REINFORCEMENT_LEARNING = "reinforcement_learning"
    NEURAL_ARCHITECTURE_SEARCH = "neural_architecture_search"
    META_LEARNING = "meta_learning"

@dataclass
class AIStrategyConfig:
    """Configuración de estrategia de IA."""
    strategy_type: AIStrategyType
    optimization_type: AIOptimizationType
    parameters: Dict[str, Any] = field(default_factory=dict)
    auto_tune: bool = True
    performance_threshold: float = 0.8
    resource_limit: float = 0.9

@dataclass
class AITrainingMetrics:
    """Métricas de entrenamiento de IA."""
    accuracy: float = 0.0
    loss: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    training_time: float = 0.0
    resource_usage: float = 0.0
    convergence_rate: float = 0.0

@dataclass
class AIResourceMetrics:
    """Métricas de recursos de IA."""
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    gpu_usage: float = 0.0
    network_usage: float = 0.0
    storage_usage: float = 0.0
    energy_consumption: float = 0.0

class AIStrategy(ABC):
    """Estrategia base de IA."""
    
    def __init__(self, config: AIStrategyConfig):
        self.config = config
        self.metrics = AITrainingMetrics()
        self.resource_metrics = AIResourceMetrics()
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecutar estrategia de IA."""
        pass
    
    @abstractmethod
    async def optimize(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Optimizar estrategia de IA."""
        pass
    
    async def collect_metrics(self) -> Dict[str, Any]:
        """Recolectar métricas de la estrategia."""
        return {
            'training_metrics': self.metrics.__dict__,
            'resource_metrics': self.resource_metrics.__dict__,
            'strategy_type': self.config.strategy_type.value,
            'optimization_type': self.config.optimization_type.value
        }

class FederatedLearningStrategy(AIStrategy):
    """Estrategia de aprendizaje federado."""
    
    def __init__(self, config: AIStrategyConfig):
        super().__init__(config)
        self.clients: List[Dict[str, Any]] = []
        self.global_model: Optional[nn.Module] = None
        self.rounds = 0
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecutar aprendizaje federado."""
        logger.info("🚀 Ejecutando aprendizaje federado...")
        
        # Configurar clientes
        await self._setup_clients(context)
        
        # Entrenamiento federado
        start_time = time.time()
        for round_num in range(self.config.parameters.get('max_rounds', 10)):
            self.rounds = round_num + 1
            logger.info(f"🔄 Ronda federada {round_num + 1}")
            
            # Entrenar en clientes
            client_models = await self._train_clients()
            
            # Agregar modelos
            await self._aggregate_models(client_models)
            
            # Evaluar modelo global
            metrics = await self._evaluate_global_model()
            
            # Verificar convergencia
            if self._check_convergence(metrics):
                logger.info("✅ Convergencia alcanzada")
                break
        
        training_time = time.time() - start_time
        self.metrics.training_time = training_time
        
        return {
            'status': 'completed',
            'rounds': self.rounds,
            'final_metrics': metrics,
            'training_time': training_time
        }
    
    async def optimize(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Optimizar estrategia federada."""
        logger.info("🔧 Optimizando estrategia federada...")
        
        # Optimizar hiperparámetros
        study = optuna.create_study(direction='maximize')
        study.optimize(
            lambda trial: self._objective_function(trial, context),
            n_trials=self.config.parameters.get('optimization_trials', 20)
        )
        
        # Aplicar mejores parámetros
        best_params = study.best_params
        self.config.parameters.update(best_params)
        
        return {
            'status': 'optimized',
            'best_params': best_params,
            'best_value': study.best_value
        }
    
    async def _setup_clients(self, context: Dict[str, Any]):
        """Configurar clientes federados."""
        num_clients = self.config.parameters.get('num_clients', 5)
        
        for i in range(num_clients):
            client = {
                'id': f"client_{i}",
                'data': self._generate_synthetic_data(),
                'model': self._create_client_model(),
                'optimizer': optim.Adam(self._create_client_model().parameters())
            }
            self.clients.append(client)
    
    async def _train_clients(self) -> List[nn.Module]:
        """Entrenar modelos en clientes."""
        client_models = []
        
        for client in self.clients:
            # Entrenar modelo local
            model = client['model']
            optimizer = client['optimizer']
            data = client['data']
            
            model.train()
            for epoch in range(self.config.parameters.get('local_epochs', 3)):
                for batch_x, batch_y in data:
                    optimizer.zero_grad()
                    output = model(batch_x)
                    loss = nn.CrossEntropyLoss()(output, batch_y)
                    loss.backward()
                    optimizer.step()
            
            client_models.append(model)
        
        return client_models
    
    async def _aggregate_models(self, client_models: List[nn.Module]):
        """Agregar modelos de clientes."""
        if not client_models:
            return
        
        # Promedio simple de parámetros
        with torch.no_grad():
            for param in self.global_model.parameters():
                param.data.zero_()
            
            for client_model in client_models:
                for global_param, client_param in zip(
                    self.global_model.parameters(), 
                    client_model.parameters()
                ):
                    global_param.data += client_param.data
            
            for param in self.global_model.parameters():
                param.data /= len(client_models)
    
    async def _evaluate_global_model(self) -> Dict[str, float]:
        """Evaluar modelo global."""
        self.global_model.eval()
        
        # Generar datos de prueba
        test_data = self._generate_synthetic_data()
        
        predictions = []
        targets = []
        
        with torch.no_grad():
            for batch_x, batch_y in test_data:
                output = self.global_model(batch_x)
                pred = torch.argmax(output, dim=1)
                predictions.extend(pred.cpu().numpy())
                targets.extend(batch_y.cpu().numpy())
        
        # Calcular métricas
        accuracy = accuracy_score(targets, predictions)
        precision, recall, f1, _ = precision_recall_fscore_support(
            targets, predictions, average='weighted'
        )
        
        self.metrics.accuracy = accuracy
        self.metrics.precision = precision
        self.metrics.recall = recall
        self.metrics.f1_score = f1
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1
        }
    
    def _check_convergence(self, metrics: Dict[str, float]) -> bool:
        """Verificar convergencia."""
        return metrics['accuracy'] >= self.config.performance_threshold
    
    def _objective_function(self, trial, context: Dict[str, Any]) -> float:
        """Función objetivo para optimización."""
        # Parámetros a optimizar
        learning_rate = trial.suggest_float('learning_rate', 1e-5, 1e-2, log=True)
        batch_size = trial.suggest_categorical('batch_size', [16, 32, 64, 128])
        local_epochs = trial.suggest_int('local_epochs', 1, 10)
        
        # Aplicar parámetros
        self.config.parameters['learning_rate'] = learning_rate
        self.config.parameters['batch_size'] = batch_size
        self.config.parameters['local_epochs'] = local_epochs
        
        # Ejecutar estrategia
        result = asyncio.run(self.execute(context))
        
        # Retornar métrica de optimización
        return result.get('final_metrics', {}).get('accuracy', 0.0)
    
    def _generate_synthetic_data(self) -> DataLoader:
        """Generar datos sintéticos para entrenamiento."""
        # Crear datos sintéticos
        num_samples = 1000
        input_size = 10
        num_classes = 3
        
        X = torch.randn(num_samples, input_size)
        y = torch.randint(0, num_classes, (num_samples,))
        
        dataset = TensorDataset(X, y)
        return DataLoader(dataset, batch_size=32, shuffle=True)
    
    def _create_client_model(self) -> nn.Module:
        """Crear modelo para cliente."""
        return nn.Sequential(
            nn.Linear(10, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, 3)
        )

class HyperparameterOptimizationStrategy(AIStrategy):
    """Estrategia de optimización de hiperparámetros."""
    
    def __init__(self, config: AIStrategyConfig):
        super().__init__(config)
        self.study: Optional[optuna.Study] = None
        self.best_params: Dict[str, Any] = {}
        self.optimization_history: List[Dict[str, Any]] = []
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecutar optimización de hiperparámetros."""
        logger.info("🚀 Ejecutando optimización de hiperparámetros...")
        
        # Crear estudio de optimización
        self.study = optuna.create_study(
            direction='maximize',
            sampler=optuna.samplers.TPESampler(),
            pruner=optuna.pruners.MedianPruner()
        )
        
        # Ejecutar optimización
        start_time = time.time()
        self.study.optimize(
            lambda trial: self._objective_function(trial, context),
            n_trials=self.config.parameters.get('n_trials', 50),
            timeout=self.config.parameters.get('timeout', 300)
        )
        
        optimization_time = time.time() - start_time
        
        # Obtener mejores resultados
        self.best_params = self.study.best_params
        best_value = self.study.best_value
        
        return {
            'status': 'completed',
            'best_params': self.best_params,
            'best_value': best_value,
            'optimization_time': optimization_time,
            'n_trials': len(self.study.trials)
        }
    
    async def optimize(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Optimizar la estrategia de optimización."""
        logger.info("🔧 Optimizando estrategia de optimización...")
        
        # Optimizar parámetros de la optimización
        optimization_study = optuna.create_study(direction='maximize')
        optimization_study.optimize(
            lambda trial: self._optimization_objective(trial, context),
            n_trials=20
        )
        
        # Aplicar mejores parámetros
        best_optimization_params = optimization_study.best_params
        self.config.parameters.update(best_optimization_params)
        
        return {
            'status': 'optimized',
            'best_optimization_params': best_optimization_params,
            'best_optimization_value': optimization_study.best_value
        }
    
    def _objective_function(self, trial, context: Dict[str, Any]) -> float:
        """Función objetivo para optimización de hiperparámetros."""
        # Parámetros a optimizar
        learning_rate = trial.suggest_float('learning_rate', 1e-5, 1e-1, log=True)
        batch_size = trial.suggest_categorical('batch_size', [16, 32, 64, 128, 256])
        hidden_size = trial.suggest_categorical('hidden_size', [32, 64, 128, 256])
        dropout = trial.suggest_float('dropout', 0.1, 0.5)
        num_layers = trial.suggest_int('num_layers', 1, 5)
        
        # Crear y entrenar modelo
        model = self._create_model(hidden_size, num_layers, dropout)
        optimizer = optim.Adam(model.parameters(), lr=learning_rate)
        
        # Entrenamiento
        train_loader = self._create_data_loader(batch_size)
        val_loader = self._create_data_loader(batch_size)
        
        best_val_acc = 0.0
        for epoch in range(10):
            # Entrenamiento
            train_acc = self._train_epoch(model, optimizer, train_loader)
            
            # Validación
            val_acc = self._validate_epoch(model, val_loader)
            
            # Pruning
            trial.report(val_acc, epoch)
            if trial.should_prune():
                raise optuna.TrialPruned()
            
            best_val_acc = max(best_val_acc, val_acc)
        
        return best_val_acc
    
    def _optimization_objective(self, trial, context: Dict[str, Any]) -> float:
        """Función objetivo para optimizar la optimización."""
        # Parámetros de la optimización
        n_trials = trial.suggest_int('n_trials', 20, 100)
        timeout = trial.suggest_int('timeout', 60, 600)
        
        # Aplicar parámetros
        self.config.parameters['n_trials'] = n_trials
        self.config.parameters['timeout'] = timeout
        
        # Ejecutar optimización
        result = asyncio.run(self.execute(context))
        
        return result.get('best_value', 0.0)
    
    def _create_model(self, hidden_size: int, num_layers: int, dropout: float) -> nn.Module:
        """Crear modelo para optimización."""
        layers = []
        input_size = 10
        
        for i in range(num_layers):
            if i == 0:
                layers.append(nn.Linear(input_size, hidden_size))
            else:
                layers.append(nn.Linear(hidden_size, hidden_size))
            
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout))
        
        layers.append(nn.Linear(hidden_size, 3))
        
        return nn.Sequential(*layers)
    
    def _create_data_loader(self, batch_size: int) -> DataLoader:
        """Crear data loader para entrenamiento."""
        # Datos sintéticos
        num_samples = 1000
        X = torch.randn(num_samples, 10)
        y = torch.randint(0, 3, (num_samples,))
        
        dataset = TensorDataset(X, y)
        return DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    def _train_epoch(self, model: nn.Module, optimizer: optim.Optimizer, train_loader: DataLoader) -> float:
        """Entrenar una época."""
        model.train()
        correct = 0
        total = 0
        
        for batch_x, batch_y in train_loader:
            optimizer.zero_grad()
            output = model(batch_x)
            loss = nn.CrossEntropyLoss()(output, batch_y)
            loss.backward()
            optimizer.step()
            
            pred = torch.argmax(output, dim=1)
            correct += (pred == batch_y).sum().item()
            total += batch_y.size(0)
        
        return correct / total
    
    def _validate_epoch(self, model: nn.Module, val_loader: DataLoader) -> float:
        """Validar una época."""
        model.eval()
        correct = 0
        total = 0
        
        with torch.no_grad():
            for batch_x, batch_y in val_loader:
                output = model(batch_x)
                pred = torch.argmax(output, dim=1)
                correct += (pred == batch_y).sum().item()
                total += batch_y.size(0)
        
        return correct / total

class AutoScalingStrategy(AIStrategy):
    """Estrategia de auto-scaling basada en IA."""
    
    def __init__(self, config: AIStrategyConfig):
        super().__init__(config)
        self.scaling_history: List[Dict[str, Any]] = []
        self.current_scale = 1
        self.scaling_thresholds = {
            'cpu_high': 0.8,
            'cpu_low': 0.3,
            'memory_high': 0.85,
            'memory_low': 0.4,
            'gpu_high': 0.9,
            'gpu_low': 0.5
        }
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecutar auto-scaling."""
        logger.info("🚀 Ejecutando auto-scaling basado en IA...")
        
        # Monitorear recursos
        resource_metrics = await self._collect_resource_metrics()
        
        # Analizar patrones de uso
        usage_patterns = await self._analyze_usage_patterns()
        
        # Predecir demanda futura
        predicted_demand = await self._predict_demand(usage_patterns)
        
        # Tomar decisión de scaling
        scaling_decision = await self._make_scaling_decision(
            resource_metrics, predicted_demand
        )
        
        # Aplicar scaling
        if scaling_decision['should_scale']:
            await self._apply_scaling(scaling_decision)
        
        return {
            'status': 'completed',
            'scaling_decision': scaling_decision,
            'resource_metrics': resource_metrics,
            'predicted_demand': predicted_demand
        }
    
    async def optimize(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Optimizar estrategia de auto-scaling."""
        logger.info("🔧 Optimizando estrategia de auto-scaling...")
        
        # Optimizar umbrales de scaling
        study = optuna.create_study(direction='minimize')
        study.optimize(
            lambda trial: self._scaling_objective(trial, context),
            n_trials=30
        )
        
        # Aplicar mejores umbrales
        best_thresholds = study.best_params
        self.scaling_thresholds.update(best_thresholds)
        
        return {
            'status': 'optimized',
            'best_thresholds': best_thresholds,
            'best_value': study.best_value
        }
    
    async def _collect_resource_metrics(self) -> AIResourceMetrics:
        """Recolectar métricas de recursos."""
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memoria
        memory = psutil.virtual_memory()
        memory_percent = memory.percent / 100.0
        
        # GPU
        gpu_percent = 0.0
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu_percent = gpus[0].load
        except:
            pass
        
        # Red
        network = psutil.net_io_counters()
        network_usage = (network.bytes_sent + network.bytes_recv) / (1024 * 1024 * 1024)  # GB
        
        # Almacenamiento
        disk = psutil.disk_usage('/')
        storage_percent = disk.percent / 100.0
        
        self.resource_metrics = AIResourceMetrics(
            cpu_usage=cpu_percent / 100.0,
            memory_usage=memory_percent,
            gpu_usage=gpu_percent,
            network_usage=network_usage,
            storage_usage=storage_percent
        )
        
        return self.resource_metrics
    
    async def _analyze_usage_patterns(self) -> Dict[str, Any]:
        """Analizar patrones de uso."""
        # Simular análisis de patrones
        patterns = {
            'hourly_trend': np.random.normal(0.5, 0.1),
            'daily_trend': np.random.normal(0.6, 0.15),
            'weekly_trend': np.random.normal(0.55, 0.12),
            'seasonality': np.random.normal(0.1, 0.05)
        }
        
        return patterns
    
    async def _predict_demand(self, usage_patterns: Dict[str, Any]) -> float:
        """Predecir demanda futura."""
        # Simular predicción basada en patrones
        base_demand = 0.5
        hourly_factor = usage_patterns['hourly_trend']
        daily_factor = usage_patterns['daily_trend']
        weekly_factor = usage_patterns['weekly_trend']
        seasonal_factor = usage_patterns['seasonality']
        
        predicted_demand = (
            base_demand + 
            hourly_factor * 0.2 + 
            daily_factor * 0.3 + 
            weekly_factor * 0.3 + 
            seasonal_factor * 0.2
        )
        
        return max(0.0, min(1.0, predicted_demand))
    
    async def _make_scaling_decision(
        self, 
        resource_metrics: AIResourceMetrics, 
        predicted_demand: float
    ) -> Dict[str, Any]:
        """Tomar decisión de scaling."""
        should_scale_up = False
        should_scale_down = False
        scale_factor = 1.0
        
        # Verificar umbrales
        if (resource_metrics.cpu_usage > self.scaling_thresholds['cpu_high'] or
            resource_metrics.memory_usage > self.scaling_thresholds['memory_high'] or
            resource_metrics.gpu_usage > self.scaling_thresholds['gpu_high'] or
            predicted_demand > 0.8):
            
            should_scale_up = True
            scale_factor = min(2.0, self.current_scale * 1.5)
        
        elif (resource_metrics.cpu_usage < self.scaling_thresholds['cpu_low'] and
              resource_metrics.memory_usage < self.scaling_thresholds['memory_low'] and
              resource_metrics.gpu_usage < self.scaling_thresholds['gpu_low'] and
              predicted_demand < 0.3):
            
            should_scale_down = True
            scale_factor = max(0.5, self.current_scale * 0.8)
        
        return {
            'should_scale': should_scale_up or should_scale_down,
            'should_scale_up': should_scale_up,
            'should_scale_down': should_scale_down,
            'scale_factor': scale_factor,
            'reason': self._get_scaling_reason(
                resource_metrics, predicted_demand, should_scale_up, should_scale_down
            )
        }
    
    def _get_scaling_reason(
        self, 
        resource_metrics: AIResourceMetrics, 
        predicted_demand: float,
        scale_up: bool,
        scale_down: bool
    ) -> str:
        """Obtener razón del scaling."""
        if scale_up:
            reasons = []
            if resource_metrics.cpu_usage > self.scaling_thresholds['cpu_high']:
                reasons.append(f"CPU alto: {resource_metrics.cpu_usage:.2%}")
            if resource_metrics.memory_usage > self.scaling_thresholds['memory_high']:
                reasons.append(f"Memoria alta: {resource_metrics.memory_usage:.2%}")
            if resource_metrics.gpu_usage > self.scaling_thresholds['gpu_high']:
                reasons.append(f"GPU alta: {resource_metrics.gpu_usage:.2%}")
            if predicted_demand > 0.8:
                reasons.append(f"Demanda predicha alta: {predicted_demand:.2%}")
            
            return f"Escalado hacia arriba: {', '.join(reasons)}"
        
        elif scale_down:
            reasons = []
            if resource_metrics.cpu_usage < self.scaling_thresholds['cpu_low']:
                reasons.append(f"CPU bajo: {resource_metrics.cpu_usage:.2%}")
            if resource_metrics.memory_usage < self.scaling_thresholds['memory_low']:
                reasons.append(f"Memoria baja: {resource_metrics.memory_usage:.2%}")
            if resource_metrics.gpu_usage < self.scaling_thresholds['gpu_low']:
                reasons.append(f"GPU baja: {resource_metrics.gpu_usage:.2%}")
            if predicted_demand < 0.3:
                reasons.append(f"Demanda predicha baja: {predicted_demand:.2%}")
            
            return f"Escalado hacia abajo: {', '.join(reasons)}"
        
        return "No se requiere scaling"
    
    async def _apply_scaling(self, scaling_decision: Dict[str, Any]):
        """Aplicar scaling."""
        if scaling_decision['should_scale']:
            old_scale = self.current_scale
            self.current_scale = scaling_decision['scale_factor']
            
            logger.info(f"🔄 Aplicando scaling: {old_scale} -> {self.current_scale}")
            logger.info(f"📊 Razón: {scaling_decision['reason']}")
            
            # Registrar scaling
            self.scaling_history.append({
                'timestamp': time.time(),
                'old_scale': old_scale,
                'new_scale': self.current_scale,
                'reason': scaling_decision['reason'],
                'resource_metrics': self.resource_metrics.__dict__
            })
    
    def _scaling_objective(self, trial, context: Dict[str, Any]) -> float:
        """Función objetivo para optimizar umbrales de scaling."""
        # Parámetros a optimizar
        cpu_high = trial.suggest_float('cpu_high', 0.6, 0.95)
        cpu_low = trial.suggest_float('cpu_low', 0.1, 0.5)
        memory_high = trial.suggest_float('memory_high', 0.7, 0.95)
        memory_low = trial.suggest_float('memory_low', 0.2, 0.6)
        gpu_high = trial.suggest_float('gpu_high', 0.7, 0.95)
        gpu_low = trial.suggest_float('gpu_low', 0.3, 0.7)
        
        # Aplicar umbrales
        self.scaling_thresholds.update({
            'cpu_high': cpu_high,
            'cpu_low': cpu_low,
            'memory_high': memory_high,
            'memory_low': memory_low,
            'gpu_high': gpu_high,
            'gpu_low': gpu_low
        })
        
        # Simular métricas de performance
        # En un caso real, esto se evaluaría con datos históricos
        performance_score = self._evaluate_scaling_performance()
        
        return -performance_score  # Minimizar (negativo para maximizar)
    
    def _evaluate_scaling_performance(self) -> float:
        """Evaluar performance del scaling."""
        # Simular evaluación basada en umbrales
        # En un caso real, esto se basaría en métricas históricas
        
        # Penalizar umbrales muy cercanos
        cpu_range = self.scaling_thresholds['cpu_high'] - self.scaling_thresholds['cpu_low']
        memory_range = self.scaling_thresholds['memory_high'] - self.scaling_thresholds['memory_low']
        gpu_range = self.scaling_thresholds['gpu_high'] - self.scaling_thresholds['gpu_low']
        
        if cpu_range < 0.2 or memory_range < 0.2 or gpu_range < 0.2:
            return 0.0
        
        # Calcular score basado en rangos
        score = (cpu_range + memory_range + gpu_range) / 3.0
        
        return score

class DistributedAIOrchestrator:
    """Orquestador principal del sistema de IA distribuida."""
    
    def __init__(self):
        self.strategies: Dict[str, AIStrategy] = {}
        self.running = False
        self.optimization_history: List[Dict[str, Any]] = []
        
        # Configurar estrategias por defecto
        self._setup_default_strategies()
    
    def _setup_default_strategies(self):
        """Configurar estrategias por defecto."""
        # Estrategia de aprendizaje federado
        federated_config = AIStrategyConfig(
            strategy_type=AIStrategyType.FEDERATED_LEARNING,
            optimization_type=AIOptimizationType.BAYESIAN_OPTIMIZATION,
            parameters={
                'num_clients': 5,
                'max_rounds': 10,
                'local_epochs': 3,
                'learning_rate': 0.001,
                'batch_size': 32
            }
        )
        
        # Estrategia de optimización de hiperparámetros
        hyperopt_config = AIStrategyConfig(
            strategy_type=AIStrategyType.HYPERPARAMETER_OPTIMIZATION,
            optimization_type=AIOptimizationType.BAYESIAN_OPTIMIZATION,
            parameters={
                'n_trials': 50,
                'timeout': 300
            }
        )
        
        # Estrategia de auto-scaling
        autoscaling_config = AIStrategyConfig(
            strategy_type=AIStrategyType.AUTO_SCALING,
            optimization_type=AIOptimizationType.BAYESIAN_OPTIMIZATION,
            parameters={
                'scaling_interval': 30,
                'prediction_horizon': 300
            }
        )
        
        # Crear estrategias
        self.strategies['federated_learning'] = FederatedLearningStrategy(federated_config)
        self.strategies['hyperparameter_optimization'] = HyperparameterOptimizationStrategy(hyperopt_config)
        self.strategies['auto_scaling'] = AutoScalingStrategy(autoscaling_config)
    
    async def start(self):
        """Iniciar orquestador de IA distribuida."""
        if self.running:
            return
        
        logger.info("🚀 Iniciando orquestador de IA distribuida...")
        self.running = True
        
        # Iniciar monitoreo continuo
        asyncio.create_task(self._continuous_monitoring())
        
        logger.info("✅ Orquestador de IA distribuida iniciado")
    
    async def stop(self):
        """Detener orquestador de IA distribuida."""
        if not self.running:
            return
        
        logger.info("🛑 Deteniendo orquestador de IA distribuida...")
        self.running = False
        
        logger.info("✅ Orquestador de IA distribuida detenido")
    
    async def execute_strategy(self, strategy_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecutar estrategia específica."""
        if strategy_name not in self.strategies:
            raise ValueError(f"Estrategia '{strategy_name}' no encontrada")
        
        strategy = self.strategies[strategy_name]
        logger.info(f"🚀 Ejecutando estrategia: {strategy_name}")
        
        # Ejecutar estrategia
        result = await strategy.execute(context)
        
        # Registrar resultado
        self.optimization_history.append({
            'timestamp': time.time(),
            'strategy': strategy_name,
            'result': result
        })
        
        return result
    
    async def optimize_strategy(self, strategy_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Optimizar estrategia específica."""
        if strategy_name not in self.strategies:
            raise ValueError(f"Estrategia '{strategy_name}' no encontrada")
        
        strategy = self.strategies[strategy_name]
        logger.info(f"🔧 Optimizando estrategia: {strategy_name}")
        
        # Optimizar estrategia
        result = await strategy.optimize(context)
        
        # Registrar optimización
        self.optimization_history.append({
            'timestamp': time.time(),
            'strategy': f"{strategy_name}_optimization",
            'result': result
        })
        
        return result
    
    async def get_strategy_metrics(self, strategy_name: str) -> Dict[str, Any]:
        """Obtener métricas de estrategia específica."""
        if strategy_name not in self.strategies:
            raise ValueError(f"Estrategia '{strategy_name}' no encontrada")
        
        strategy = self.strategies[strategy_name]
        return await strategy.collect_metrics()
    
    async def get_all_metrics(self) -> Dict[str, Any]:
        """Obtener métricas de todas las estrategias."""
        all_metrics = {}
        
        for name, strategy in self.strategies.items():
            all_metrics[name] = await strategy.collect_metrics()
        
        return all_metrics
    
    async def _continuous_monitoring(self):
        """Monitoreo continuo del sistema."""
        while self.running:
            try:
                # Ejecutar auto-scaling
                if 'auto_scaling' in self.strategies:
                    context = {'timestamp': time.time()}
                    await self.execute_strategy('auto_scaling', context)
                
                # Esperar intervalo
                await asyncio.sleep(30)  # 30 segundos
                
            except Exception as e:
                logger.error(f"Error en monitoreo continuo: {e}")
                await asyncio.sleep(5)

async def main():
    """Función principal de demostración."""
    print("🚀 Sistema de Inteligencia Artificial Distribuida Avanzado")
    print("=" * 80)
    
    # Crear orquestador
    orchestrator = DistributedAIOrchestrator()
    
    try:
        # Iniciar orquestador
        await orchestrator.start()
        
        # Contexto de ejemplo
        context = {
            'model_type': 'neural_network',
            'dataset_size': 10000,
            'target_accuracy': 0.9,
            'resource_constraints': {
                'max_memory': '8GB',
                'max_gpu': 1,
                'max_cpu': 4
            }
        }
        
        print("\n🔬 Ejecutando estrategias de IA...")
        
        # Ejecutar aprendizaje federado
        print("\n1️⃣ Aprendizaje Federado:")
        federated_result = await orchestrator.execute_strategy('federated_learning', context)
        print(f"   Resultado: {federated_result['status']}")
        print(f"   Rondas: {federated_result['rounds']}")
        print(f"   Tiempo: {federated_result['training_time']:.2f}s")
        
        # Ejecutar optimización de hiperparámetros
        print("\n2️⃣ Optimización de Hiperparámetros:")
        hyperopt_result = await orchestrator.execute_strategy('hyperparameter_optimization', context)
        print(f"   Resultado: {hyperopt_result['status']}")
        print(f"   Mejores parámetros: {hyperopt_result['best_params']}")
        print(f"   Mejor valor: {hyperopt_result['best_value']:.4f}")
        
        # Ejecutar auto-scaling
        print("\n3️⃣ Auto-Scaling:")
        autoscaling_result = await orchestrator.execute_strategy('auto_scaling', context)
        print(f"   Resultado: {autoscaling_result['status']}")
        print(f"   Decisión: {autoscaling_result['scaling_decision']['reason']}")
        
        # Obtener métricas
        print("\n📊 Métricas del Sistema:")
        all_metrics = await orchestrator.get_all_metrics()
        for strategy_name, metrics in all_metrics.items():
            print(f"   {strategy_name}: {metrics['strategy_type']}")
        
        # Optimizar estrategias
        print("\n🔧 Optimizando estrategias...")
        
        for strategy_name in ['federated_learning', 'hyperparameter_optimization', 'auto_scaling']:
            print(f"   Optimizando {strategy_name}...")
            optimization_result = await orchestrator.optimize_strategy(strategy_name, context)
            print(f"   ✅ {strategy_name} optimizado")
        
        print("\n🎉 ¡Todas las estrategias optimizadas exitosamente!")
        
        # Esperar un poco para ver el monitoreo continuo
        print("\n⏳ Monitoreo continuo activo (30s)...")
        await asyncio.sleep(30)
        
    except Exception as e:
        logger.error(f"Error en demostración: {e}")
    
    finally:
        # Detener orquestador
        await orchestrator.stop()
        print("\n✅ Sistema detenido")

if __name__ == "__main__":
    asyncio.run(main())
