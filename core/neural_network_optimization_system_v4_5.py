"""
Sistema de Optimización de Redes Neuronales v4.5
HeyGen AI - Sistema de Monitoreo Inteligente con IA Avanzada

Este sistema implementa optimización avanzada de redes neuronales con:
- Cuantización inteligente (INT8, FP16, mixed precision)
- Pruning adaptativo y dinámico
- Distillation de conocimiento
- Optimización de learning rate adaptativo
- Compresión de modelos
- Análisis de arquitectura neural
"""

import asyncio
import time
import json
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Callable, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics
import math
import threading
import queue
import pickle
import hashlib
import random
import os
import sys
from pathlib import Path

# Neural Network Optimization Components
@dataclass
class ModelArchitecture:
    """Neural network model architecture information"""
    model_id: str
    total_parameters: int
    trainable_parameters: int
    layers: List[Dict[str, Any]]
    input_shape: Tuple[int, ...]
    output_shape: Tuple[int, ...]
    model_size_mb: float
    created_at: datetime
    framework: str  # 'pytorch', 'tensorflow', 'onnx'
    version: str

@dataclass
class OptimizationResult:
    """Result of an optimization operation"""
    optimization_id: str
    model_id: str
    optimization_type: str
    original_size_mb: float
    optimized_size_mb: float
    compression_ratio: float
    accuracy_loss: float
    inference_speedup: float
    memory_reduction: float
    timestamp: datetime
    parameters: Dict[str, Any]

@dataclass
class QuantizationConfig:
    """Configuration for model quantization"""
    precision: str  # 'INT8', 'FP16', 'mixed'
    calibration_samples: int
    calibration_method: str  # 'min_max', 'kl_divergence', 'entropy'
    symmetric: bool
    per_channel: bool
    dynamic_range: bool

@dataclass
class PruningConfig:
    """Configuration for model pruning"""
    pruning_method: str  # 'magnitude', 'structured', 'dynamic'
    sparsity_target: float
    importance_metric: str  # 'l1_norm', 'l2_norm', 'gradient'
    gradual_pruning: bool
    min_remaining_weights: float

@dataclass
class DistillationConfig:
    """Configuration for knowledge distillation"""
    teacher_model_id: str
    temperature: float
    alpha: float  # Weight for distillation loss
    distillation_layers: List[str]
    student_architecture: Dict[str, Any]

class IntelligentQuantizer:
    """Advanced model quantization system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.quantization_history: List[OptimizationResult] = []
        self.calibration_data: Dict[str, np.ndarray] = {}
        self.quantization_cache: Dict[str, Any] = {}
        
    async def quantize_model(self, model: Any, config: QuantizationConfig, 
                           model_id: str) -> OptimizationResult:
        """Quantize a neural network model"""
        optimization_id = f"quant_{len(self.quantization_history)}_{int(time.time())}"
        
        # Measure original model
        original_size = self._get_model_size(model)
        original_accuracy = await self._evaluate_model_accuracy(model)
        
        # Perform quantization
        quantized_model = await self._apply_quantization(model, config)
        
        # Measure quantized model
        quantized_size = self._get_model_size(quantized_model)
        quantized_accuracy = await self._evaluate_model_accuracy(quantized_model)
        
        # Calculate metrics
        compression_ratio = quantized_size / original_size
        accuracy_loss = original_accuracy - quantized_accuracy
        inference_speedup = await self._measure_inference_speedup(model, quantized_model)
        memory_reduction = 1 - compression_ratio
        
        result = OptimizationResult(
            optimization_id=optimization_id,
            model_id=model_id,
            optimization_type='quantization',
            original_size_mb=original_size,
            optimized_size_mb=quantized_size,
            compression_ratio=compression_ratio,
            accuracy_loss=accuracy_loss,
            inference_speedup=inference_speedup,
            memory_reduction=memory_reduction,
            timestamp=datetime.now(),
            parameters={
                'precision': config.precision,
                'calibration_method': config.calibration_method,
                'symmetric': config.symmetric,
                'per_channel': config.per_channel
            }
        )
        
        self.quantization_history.append(result)
        return result
    
    async def _apply_quantization(self, model: Any, config: QuantizationConfig) -> Any:
        """Apply quantization to the model"""
        if config.precision == 'INT8':
            return await self._quantize_to_int8(model, config)
        elif config.precision == 'FP16':
            return await self._quantize_to_fp16(model, config)
        elif config.precision == 'mixed':
            return await self._quantize_mixed_precision(model, config)
        else:
            raise ValueError(f"Unsupported precision: {config.precision}")
    
    async def _quantize_to_int8(self, model: Any, config: QuantizationConfig) -> Any:
        """Quantize model to INT8 precision"""
        # Simulate INT8 quantization
        logging.info(f"🔢 Cuantizando modelo a INT8 con {config.calibration_samples} muestras")
        
        # In a real implementation, this would use PyTorch/TensorFlow quantization
        # For now, we simulate the process
        await asyncio.sleep(1)  # Simulate processing time
        
        # Return simulated quantized model
        return {
            'type': 'quantized_int8',
            'original_model': model,
            'precision': 'INT8',
            'calibrated': True
        }
    
    async def _quantize_to_fp16(self, model: Any, config: QuantizationConfig) -> Any:
        """Quantize model to FP16 precision"""
        logging.info(f"🔢 Cuantizando modelo a FP16")
        
        await asyncio.sleep(0.5)  # Simulate processing time
        
        return {
            'type': 'quantized_fp16',
            'original_model': model,
            'precision': 'FP16',
            'calibrated': False
        }
    
    async def _quantize_mixed_precision(self, model: Any, config: QuantizationConfig) -> Any:
        """Apply mixed precision quantization"""
        logging.info(f"🔢 Aplicando cuantización de precisión mixta")
        
        await asyncio.sleep(1.5)  # Simulate processing time
        
        return {
            'type': 'quantized_mixed',
            'original_model': model,
            'precision': 'mixed',
            'calibrated': True
        }
    
    def _get_model_size(self, model: Any) -> float:
        """Get model size in MB"""
        # Simulate model size calculation
        if isinstance(model, dict) and 'type' in model:
            if 'quantized' in model['type']:
                return random.uniform(10.0, 50.0)  # Simulated quantized size
            else:
                return random.uniform(50.0, 200.0)  # Simulated original size
        return random.uniform(50.0, 200.0)
    
    async def _evaluate_model_accuracy(self, model: Any) -> float:
        """Evaluate model accuracy (simulated)"""
        # Simulate accuracy evaluation
        await asyncio.sleep(0.1)
        return random.uniform(0.85, 0.98)
    
    async def _measure_inference_speedup(self, original_model: Any, 
                                       quantized_model: Any) -> float:
        """Measure inference speedup from quantization"""
        # Simulate speed measurement
        await asyncio.sleep(0.2)
        
        if isinstance(quantized_model, dict) and 'quantized' in quantized_model['type']:
            if 'int8' in quantized_model['type']:
                return random.uniform(1.5, 3.0)  # INT8 speedup
            elif 'fp16' in quantized_model['type']:
                return random.uniform(1.2, 2.0)  # FP16 speedup
            else:
                return random.uniform(1.3, 2.5)  # Mixed precision speedup
        
        return 1.0

class AdaptivePruner:
    """Intelligent model pruning system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.pruning_history: List[OptimizationResult] = []
        self.importance_scores: Dict[str, np.ndarray] = {}
        self.pruning_masks: Dict[str, np.ndarray] = {}
        
    async def prune_model(self, model: Any, config: PruningConfig, 
                         model_id: str) -> OptimizationResult:
        """Prune a neural network model"""
        optimization_id = f"prune_{len(self.pruning_history)}_{int(time.time())}"
        
        # Measure original model
        original_size = self._get_model_size(model)
        original_accuracy = await self._evaluate_model_accuracy(model)
        
        # Perform pruning
        pruned_model = await self._apply_pruning(model, config)
        
        # Measure pruned model
        pruned_size = self._get_model_size(pruned_model)
        pruned_accuracy = await self._evaluate_model_accuracy(pruned_model)
        
        # Calculate metrics
        compression_ratio = pruned_size / original_size
        accuracy_loss = original_accuracy - pruned_accuracy
        inference_speedup = await self._measure_inference_speedup(model, pruned_model)
        memory_reduction = 1 - compression_ratio
        
        result = OptimizationResult(
            optimization_id=optimization_id,
            model_id=model_id,
            optimization_type='pruning',
            original_size_mb=original_size,
            optimized_size_mb=pruned_size,
            compression_ratio=compression_ratio,
            accuracy_loss=accuracy_loss,
            inference_speedup=inference_speedup,
            memory_reduction=memory_reduction,
            timestamp=datetime.now(),
            parameters={
                'pruning_method': config.pruning_method,
                'sparsity_target': config.sparsity_target,
                'importance_metric': config.importance_metric,
                'gradual_pruning': config.gradual_pruning
            }
        )
        
        self.pruning_history.append(result)
        return result
    
    async def _apply_pruning(self, model: Any, config: PruningConfig) -> Any:
        """Apply pruning to the model"""
        if config.pruning_method == 'magnitude':
            return await self._magnitude_pruning(model, config)
        elif config.pruning_method == 'structured':
            return await self._structured_pruning(model, config)
        elif config.pruning_method == 'dynamic':
            return await self._dynamic_pruning(model, config)
        else:
            raise ValueError(f"Unsupported pruning method: {config.pruning_method}")
    
    async def _magnitude_pruning(self, model: Any, config: PruningConfig) -> Any:
        """Apply magnitude-based pruning"""
        logging.info(f"✂️ Aplicando pruning por magnitud con sparsity {config.sparsity_target:.2%}")
        
        # Simulate magnitude pruning
        await asyncio.sleep(1)
        
        return {
            'type': 'pruned_magnitude',
            'original_model': model,
            'sparsity': config.sparsity_target,
            'method': 'magnitude'
        }
    
    async def _structured_pruning(self, model: Any, config: PruningConfig) -> Any:
        """Apply structured pruning"""
        logging.info(f"✂️ Aplicando pruning estructurado con sparsity {config.sparsity_target:.2%}")
        
        await asyncio.sleep(1.2)
        
        return {
            'type': 'pruned_structured',
            'original_model': model,
            'sparsity': config.sparsity_target,
            'method': 'structured'
        }
    
    async def _dynamic_pruning(self, model: Any, config: PruningConfig) -> Any:
        """Apply dynamic pruning"""
        logging.info(f"✂️ Aplicando pruning dinámico con sparsity {config.sparsity_target:.2%}")
        
        await asyncio.sleep(1.5)
        
        return {
            'type': 'pruned_dynamic',
            'original_model': model,
            'sparsity': config.sparsity_target,
            'method': 'dynamic'
        }
    
    def _get_model_size(self, model: Any) -> float:
        """Get model size in MB"""
        if isinstance(model, dict) and 'pruned' in model['type']:
            sparsity = model.get('sparsity', 0.5)
            # Simulate size reduction based on sparsity
            base_size = random.uniform(50.0, 200.0)
            return base_size * (1 - sparsity)
        return random.uniform(50.0, 200.0)
    
    async def _evaluate_model_accuracy(self, model: Any) -> float:
        """Evaluate model accuracy (simulated)"""
        await asyncio.sleep(0.1)
        
        if isinstance(model, dict) and 'pruned' in model['type']:
            sparsity = model.get('sparsity', 0.5)
            # Simulate accuracy degradation based on sparsity
            base_accuracy = random.uniform(0.90, 0.98)
            accuracy_loss = sparsity * 0.1  # 10% max loss
            return max(0.7, base_accuracy - accuracy_loss)
        
        return random.uniform(0.85, 0.98)
    
    async def _measure_inference_speedup(self, original_model: Any, 
                                       pruned_model: Any) -> float:
        """Measure inference speedup from pruning"""
        await asyncio.sleep(0.2)
        
        if isinstance(pruned_model, dict) and 'pruned' in pruned_model['type']:
            sparsity = pruned_model.get('sparsity', 0.5)
            # Simulate speedup based on sparsity
            return 1 + (sparsity * 0.5)  # Up to 50% speedup
        
        return 1.0

class KnowledgeDistiller:
    """Knowledge distillation system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.distillation_history: List[OptimizationResult] = []
        self.teacher_models: Dict[str, Any] = {}
        self.student_models: Dict[str, Any] = {}
        
    async def distill_knowledge(self, teacher_model: Any, student_model: Any,
                               config: DistillationConfig, model_id: str) -> OptimizationResult:
        """Perform knowledge distillation"""
        optimization_id = f"distill_{len(self.distillation_history)}_{int(time.time())}"
        
        # Measure original student model
        original_size = self._get_model_size(student_model)
        original_accuracy = await self._evaluate_model_accuracy(student_model)
        
        # Perform distillation
        distilled_model = await self._apply_distillation(teacher_model, student_model, config)
        
        # Measure distilled model
        distilled_size = self._get_model_size(distilled_model)
        distilled_accuracy = await self._evaluate_model_accuracy(distilled_model)
        
        # Calculate metrics
        compression_ratio = distilled_size / original_size
        accuracy_gain = distilled_accuracy - original_accuracy
        inference_speedup = await self._measure_inference_speedup(student_model, distilled_model)
        memory_reduction = 1 - compression_ratio
        
        result = OptimizationResult(
            optimization_id=optimization_id,
            model_id=model_id,
            optimization_type='distillation',
            original_size_mb=original_size,
            optimized_size_mb=distilled_size,
            compression_ratio=compression_ratio,
            accuracy_loss=-accuracy_gain,  # Negative because it's a gain
            inference_speedup=inference_speedup,
            memory_reduction=memory_reduction,
            timestamp=datetime.now(),
            parameters={
                'temperature': config.temperature,
                'alpha': config.alpha,
                'distillation_layers': config.distillation_layers
            }
        )
        
        self.distillation_history.append(result)
        return result
    
    async def _apply_distillation(self, teacher_model: Any, student_model: Any,
                                 config: DistillationConfig) -> Any:
        """Apply knowledge distillation"""
        logging.info(f"🎓 Aplicando distillation con temperatura {config.temperature}")
        
        # Simulate distillation process
        await asyncio.sleep(2)
        
        return {
            'type': 'distilled',
            'teacher_model': teacher_model,
            'student_model': student_model,
            'temperature': config.temperature,
            'alpha': config.alpha,
            'distilled': True
        }
    
    def _get_model_size(self, model: Any) -> float:
        """Get model size in MB"""
        if isinstance(model, dict) and 'distilled' in model['type']:
            # Distilled models are typically smaller
            return random.uniform(20.0, 80.0)
        return random.uniform(50.0, 200.0)
    
    async def _evaluate_model_accuracy(self, model: Any) -> float:
        """Evaluate model accuracy (simulated)"""
        await asyncio.sleep(0.1)
        
        if isinstance(model, dict) and 'distilled' in model['type']:
            # Distilled models often have better accuracy
            return random.uniform(0.92, 0.99)
        
        return random.uniform(0.85, 0.98)
    
    async def _measure_inference_speedup(self, original_model: Any, 
                                       distilled_model: Any) -> float:
        """Measure inference speedup from distillation"""
        await asyncio.sleep(0.2)
        
        if isinstance(distilled_model, dict) and 'distilled' in distilled_model['type']:
            # Distilled models are typically faster
            return random.uniform(1.2, 2.0)
        
        return 1.0

class AdaptiveLearningRateOptimizer:
    """Adaptive learning rate optimization system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.lr_history: List[Dict[str, Any]] = []
        self.optimization_schedules: Dict[str, Dict[str, Any]] = {}
        self.performance_metrics: Dict[str, List[float]] = defaultdict(list)
        
    async def optimize_learning_rate(self, model_id: str, 
                                   current_lr: float,
                                   performance_metrics: Dict[str, float]) -> float:
        """Optimize learning rate based on performance"""
        # Store performance metrics
        for metric, value in performance_metrics.items():
            self.performance_metrics[metric].append(value)
        
        # Analyze performance trends
        lr_adjustment = await self._analyze_performance_trends(model_id, performance_metrics)
        
        # Calculate new learning rate
        new_lr = current_lr * (1 + lr_adjustment)
        
        # Ensure learning rate stays within bounds
        min_lr = self.config.get('min_learning_rate', 1e-6)
        max_lr = self.config.get('max_learning_rate', 1e-1)
        new_lr = max(min_lr, min(max_lr, new_lr))
        
        # Store learning rate history
        self.lr_history.append({
            'model_id': model_id,
            'timestamp': datetime.now(),
            'old_lr': current_lr,
            'new_lr': new_lr,
            'adjustment': lr_adjustment,
            'performance_metrics': performance_metrics
        })
        
        logging.info(f"📈 LR optimizado: {current_lr:.2e} → {new_lr:.2e} (ajuste: {lr_adjustment:+.2%})")
        
        return new_lr
    
    async def _analyze_performance_trends(self, model_id: str, 
                                        current_metrics: Dict[str, float]) -> float:
        """Analyze performance trends to determine LR adjustment"""
        if len(self.performance_metrics['loss']) < 2:
            return 0.0
        
        # Get recent performance data
        recent_losses = self.performance_metrics['loss'][-5:]  # Last 5 iterations
        recent_accuracies = self.performance_metrics.get('accuracy', [])
        
        # Calculate loss trend
        if len(recent_losses) >= 2:
            loss_trend = (recent_losses[-1] - recent_losses[0]) / len(recent_losses)
            
            # Adjust learning rate based on loss trend
            if loss_trend < -0.01:  # Loss decreasing (good)
                return 0.05  # Increase LR by 5%
            elif loss_trend > 0.01:  # Loss increasing (bad)
                return -0.1  # Decrease LR by 10%
            else:  # Loss stable
                return 0.0
        
        # Check accuracy trend if available
        if len(recent_accuracies) >= 2:
            accuracy_trend = (recent_accuracies[-1] - recent_accuracies[0]) / len(recent_accuracies)
            
            if accuracy_trend > 0.01:  # Accuracy increasing (good)
                return 0.03  # Increase LR by 3%
            elif accuracy_trend < -0.01:  # Accuracy decreasing (bad)
                return -0.08  # Decrease LR by 8%
        
        return 0.0
    
    async def get_learning_rate_schedule(self, model_id: str) -> Dict[str, Any]:
        """Get optimized learning rate schedule for a model"""
        if model_id not in self.optimization_schedules:
            # Create default schedule
            self.optimization_schedules[model_id] = {
                'initial_lr': 1e-3,
                'decay_factor': 0.9,
                'decay_epochs': 10,
                'min_lr': 1e-6,
                'warmup_epochs': 5
            }
        
        return self.optimization_schedules[model_id]
    
    async def update_learning_rate_schedule(self, model_id: str, 
                                          new_schedule: Dict[str, Any]):
        """Update learning rate schedule for a model"""
        self.optimization_schedules[model_id] = new_schedule
        logging.info(f"📋 Horario de LR actualizado para modelo {model_id}")

class NeuralNetworkOptimizationSystem:
    """Main neural network optimization system v4.5"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.quantizer = IntelligentQuantizer(config)
        self.pruner = AdaptivePruner(config)
        self.distiller = KnowledgeDistiller(config)
        self.lr_optimizer = AdaptiveLearningRateOptimizer(config)
        
        self.optimization_history: List[OptimizationResult] = []
        self.model_registry: Dict[str, ModelArchitecture] = {}
        self.optimization_queue: queue.Queue = queue.Queue()
        self.is_running = False
        
        # Performance tracking
        self.total_optimizations = 0
        self.successful_optimizations = 0
        self.average_compression_ratio = 0.0
        self.average_accuracy_loss = 0.0
        
    async def start(self):
        """Start the neural network optimization system"""
        self.is_running = True
        logging.info("🚀 Sistema de Optimización de Redes Neuronales v4.5 iniciado")
        
        # Start optimization worker
        asyncio.create_task(self._optimization_worker())
        
        logging.info("✅ Worker de optimización iniciado")
    
    async def stop(self):
        """Stop the neural network optimization system"""
        self.is_running = False
        logging.info("🛑 Sistema de Optimización de Redes Neuronales v4.5 detenido")
    
    async def _optimization_worker(self):
        """Background worker for processing optimization tasks"""
        while self.is_running:
            try:
                # Process optimization tasks
                if not self.optimization_queue.empty():
                    task = self.optimization_queue.get_nowait()
                    await self._process_optimization_task(task)
                
                await asyncio.sleep(1)  # Check every second
            except Exception as e:
                logging.error(f"Error en worker de optimización: {e}")
    
    async def _process_optimization_task(self, task: Dict[str, Any]):
        """Process an optimization task"""
        try:
            task['status'] = 'processing'
            
            if task['type'] == 'quantization':
                result = await self.quantizer.quantize_model(
                    task['model'], task['config'], task['model_id']
                )
            elif task['type'] == 'pruning':
                result = await self.pruner.prune_model(
                    task['model'], task['config'], task['model_id']
                )
            elif task['type'] == 'distillation':
                result = await self.distiller.distill_knowledge(
                    task['teacher_model'], task['student_model'], 
                    task['config'], task['model_id']
                )
            else:
                raise ValueError(f"Tipo de optimización no soportado: {task['type']}")
            
            # Store result
            self.optimization_history.append(result)
            self.total_optimizations += 1
            self.successful_optimizations += 1
            
            # Update performance metrics
            self._update_performance_metrics(result)
            
            task['status'] = 'completed'
            task['result'] = result
            
            logging.info(f"✅ Optimización {task['type']} completada para modelo {task['model_id']}")
            
        except Exception as e:
            task['status'] = 'failed'
            task['error'] = str(e)
            logging.error(f"❌ Error en optimización {task['type']}: {e}")
    
    def _update_performance_metrics(self, result: OptimizationResult):
        """Update system performance metrics"""
        # Update average compression ratio
        if self.total_optimizations > 0:
            self.average_compression_ratio = (
                (self.average_compression_ratio * (self.total_optimizations - 1) + 
                 result.compression_ratio) / self.total_optimizations
            )
        
        # Update average accuracy loss
        if self.total_optimizations > 0:
            self.average_accuracy_loss = (
                (self.average_accuracy_loss * (self.total_optimizations - 1) + 
                 result.accuracy_loss) / self.total_optimizations
            )
    
    async def register_model(self, model: Any, model_id: str, 
                           framework: str = 'pytorch') -> str:
        """Register a new model for optimization"""
        # Analyze model architecture
        architecture = await self._analyze_model_architecture(model, model_id, framework)
        
        # Store in registry
        self.model_registry[model_id] = architecture
        
        logging.info(f"📝 Modelo {model_id} registrado: {architecture.total_parameters:,} parámetros")
        
        return model_id
    
    async def _analyze_model_architecture(self, model: Any, model_id: str, 
                                        framework: str) -> ModelArchitecture:
        """Analyze model architecture"""
        # Simulate architecture analysis
        await asyncio.sleep(0.5)
        
        total_params = random.randint(1000000, 10000000)  # 1M to 10M params
        trainable_params = int(total_params * random.uniform(0.8, 1.0))
        
        architecture = ModelArchitecture(
            model_id=model_id,
            total_parameters=total_params,
            trainable_parameters=trainable_params,
            layers=[],  # Would contain actual layer info
            input_shape=(1, 3, 224, 224),  # Simulated input shape
            output_shape=(1, 1000),  # Simulated output shape
            model_size_mb=total_params * 4 / (1024 * 1024),  # 4 bytes per param
            created_at=datetime.now(),
            framework=framework,
            version='1.0.0'
        )
        
        return architecture
    
    async def queue_quantization(self, model: Any, config: QuantizationConfig, 
                                model_id: str):
        """Queue a quantization optimization task"""
        task = {
            'type': 'quantization',
            'model': model,
            'config': config,
            'model_id': model_id,
            'status': 'queued',
            'timestamp': datetime.now()
        }
        
        self.optimization_queue.put(task)
        logging.info(f"📋 Tarea de cuantización encolada para modelo {model_id}")
    
    async def queue_pruning(self, model: Any, config: PruningConfig, 
                           model_id: str):
        """Queue a pruning optimization task"""
        task = {
            'type': 'pruning',
            'model': model,
            'config': config,
            'model_id': model_id,
            'status': 'queued',
            'timestamp': datetime.now()
        }
        
        self.optimization_queue.put(task)
        logging.info(f"📋 Tarea de pruning encolada para modelo {model_id}")
    
    async def queue_distillation(self, teacher_model: Any, student_model: Any,
                                config: DistillationConfig, model_id: str):
        """Queue a knowledge distillation task"""
        task = {
            'type': 'distillation',
            'teacher_model': teacher_model,
            'student_model': student_model,
            'config': config,
            'model_id': model_id,
            'status': 'queued',
            'timestamp': datetime.now()
        }
        
        self.optimization_queue.put(task)
        logging.info(f"📋 Tarea de distillation encolada para modelo {model_id}")
    
    async def get_optimization_stats(self) -> Dict[str, Any]:
        """Get comprehensive optimization statistics"""
        return {
            'system_status': {
                'is_running': self.is_running,
                'total_optimizations': self.total_optimizations,
                'successful_optimizations': self.successful_optimizations,
                'success_rate': self.successful_optimizations / max(self.total_optimizations, 1)
            },
            'performance_metrics': {
                'average_compression_ratio': self.average_compression_ratio,
                'average_accuracy_loss': self.average_accuracy_loss,
                'total_models_registered': len(self.model_registry)
            },
            'optimization_history': {
                'quantization_count': len(self.quantizer.quantization_history),
                'pruning_count': len(self.pruner.pruning_history),
                'distillation_count': len(self.distiller.distillation_history)
            },
            'queue_status': {
                'pending_tasks': self.optimization_queue.qsize(),
                'recent_tasks': len(self.optimization_history[-10:]) if self.optimization_history else 0
            }
        }
    
    async def get_model_architecture(self, model_id: str) -> Optional[ModelArchitecture]:
        """Get model architecture information"""
        return self.model_registry.get(model_id)
    
    async def list_registered_models(self) -> List[str]:
        """List all registered model IDs"""
        return list(self.model_registry.keys())

# Configuration for the system
DEFAULT_CONFIG = {
    'min_learning_rate': 1e-6,
    'max_learning_rate': 1e-1,
    'lr_optimization_interval': 10,
    'performance_analysis_window': 5,
    'quantization_cache_size': 100,
    'pruning_evaluation_samples': 1000,
    'distillation_training_epochs': 10
}

if __name__ == "__main__":
    # Demo configuration
    config = DEFAULT_CONFIG.copy()
    
    async def demo():
        system = NeuralNetworkOptimizationSystem(config)
        await system.start()
        
        # Simulate model registration
        model_id = await system.register_model("dummy_model", "test_model_001", "pytorch")
        print(f"Modelo registrado: {model_id}")
        
        # Simulate optimization tasks
        quant_config = QuantizationConfig(
            precision='INT8',
            calibration_samples=1000,
            calibration_method='kl_divergence',
            symmetric=True,
            per_channel=True,
            dynamic_range=False
        )
        
        await system.queue_quantization("dummy_model", quant_config, model_id)
        
        # Wait for processing
        await asyncio.sleep(3)
        
        # Get stats
        stats = await system.get_optimization_stats()
        print(f"Estadísticas: {json.dumps(stats, indent=2, default=str)}")
        
        await system.stop()
    
    asyncio.run(demo())
