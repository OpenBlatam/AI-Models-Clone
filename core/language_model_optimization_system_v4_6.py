"""
Sistema de Optimización de Modelos de Lenguaje v4.6
HeyGen AI - Sistema de Monitoreo Inteligente con IA Avanzada

Este sistema proporciona capacidades avanzadas de optimización de LLMs incluyendo:
- Fine-tuning inteligente de modelos
- Ingeniería de prompts avanzada
- Optimización de rendimiento
- Evaluación y benchmarking
- Compresión y cuantización
- Adaptación de dominio
"""

import asyncio
import time
import json
import logging
import random
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelType(Enum):
    """Tipos de modelos de lenguaje"""
    GPT = "gpt"
    BERT = "bert"
    T5 = "t5"
    LLAMA = "llama"
    CUSTOM = "custom"

class OptimizationStrategy(Enum):
    """Estrategias de optimización"""
    FINE_TUNING = "fine_tuning"
    PROMPT_ENGINEERING = "prompt_engineering"
    QUANTIZATION = "quantization"
    PRUNING = "pruning"
    KNOWLEDGE_DISTILLATION = "knowledge_distillation"
    ADAPTIVE_LEARNING = "adaptive_learning"

class PerformanceMetric(Enum):
    """Métricas de rendimiento"""
    ACCURACY = "accuracy"
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    MEMORY_USAGE = "memory_usage"
    INFERENCE_TIME = "inference_time"
    QUALITY_SCORE = "quality_score"

@dataclass
class ModelConfiguration:
    """Configuración del modelo"""
    model_id: str
    model_type: ModelType
    base_model: str
    parameters: Dict[str, Any]
    hyperparameters: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"
    
    def __post_init__(self):
        if not self.model_id:
            self.model_id = hashlib.md5(f"{self.base_model}{time.time()}".encode()).hexdigest()[:8]

@dataclass
class TrainingDataset:
    """Dataset de entrenamiento"""
    id: str
    name: str
    description: str
    data_samples: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)
    size: int = 0
    
    def __post_init__(self):
        if not self.id:
            self.id = hashlib.md5(f"{self.name}{time.time()}".encode()).hexdigest()[:8]
        self.size = len(self.data_samples)

@dataclass
class OptimizationResult:
    """Resultado de optimización"""
    model_id: str
    strategy: OptimizationStrategy
    performance_metrics: Dict[str, float]
    training_time: float
    improvement_percentage: float
    metadata: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool = True
    error_message: Optional[str] = None

@dataclass
class PromptTemplate:
    """Plantilla de prompt optimizada"""
    id: str
    name: str
    template: str
    variables: List[str]
    performance_score: float
    usage_count: int
    created_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None

class IntelligentFineTuner:
    """Fine-tuner inteligente de modelos"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.training_history = []
        self.optimization_strategies = {
            'low_resource': {'learning_rate': 1e-5, 'batch_size': 8, 'epochs': 3},
            'balanced': {'learning_rate': 5e-5, 'batch_size': 16, 'epochs': 5},
            'high_quality': {'learning_rate': 1e-4, 'batch_size': 32, 'epochs': 10}
        }
        
    async def fine_tune_model(self, model_config: ModelConfiguration, 
                            dataset: TrainingDataset, 
                            strategy: str = 'balanced') -> OptimizationResult:
        """Fine-tune del modelo con estrategia inteligente"""
        start_time = time.time()
        
        try:
            # Simulate fine-tuning process
            training_params = self.optimization_strategies.get(strategy, self.optimization_strategies['balanced'])
            
            # Simulate training progress
            epochs = training_params['epochs']
            for epoch in range(epochs):
                await asyncio.sleep(0.5)  # Simulate training time
                logger.info(f"🔄 Epoch {epoch + 1}/{epochs} - Entrenando modelo...")
            
            training_time = time.time() - start_time
            
            # Simulate performance improvement
            base_accuracy = random.uniform(0.7, 0.85)
            improved_accuracy = base_accuracy + random.uniform(0.05, 0.15)
            improvement = ((improved_accuracy - base_accuracy) / base_accuracy) * 100
            
            result = OptimizationResult(
                model_id=model_config.model_id,
                strategy=OptimizationStrategy.FINE_TUNING,
                performance_metrics={
                    'accuracy': improved_accuracy,
                    'latency': random.uniform(50, 150),
                    'throughput': random.uniform(100, 500),
                    'memory_usage': random.uniform(2.0, 8.0)
                },
                training_time=training_time,
                improvement_percentage=improvement,
                metadata={
                    'strategy': strategy,
                    'training_params': training_params,
                    'dataset_size': dataset.size,
                    'base_accuracy': base_accuracy
                }
            )
            
            self.training_history.append(result)
            return result
            
        except Exception as e:
            return OptimizationResult(
                model_id=model_config.model_id,
                strategy=OptimizationStrategy.FINE_TUNING,
                performance_metrics={},
                training_time=time.time() - start_time,
                improvement_percentage=0.0,
                metadata={},
                success=False,
                error_message=str(e)
            )

class AdvancedPromptEngineer:
    """Ingeniero de prompts avanzado"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.prompt_templates = []
        self.optimization_history = []
        self.prompt_patterns = {
            'instruction': "Instrucción clara y específica",
            'few_shot': "Ejemplos de entrada-salida",
            'chain_of_thought': "Razonamiento paso a paso",
            'role_based': "Definición de rol y contexto"
        }
        
    async def optimize_prompt(self, original_prompt: str, 
                            target_task: str, 
                            model_type: ModelType) -> PromptTemplate:
        """Optimizar prompt para tarea específica"""
        try:
            # Analyze prompt and apply optimization strategies
            if "clasificación" in target_task.lower():
                optimized_template = f"""Tarea: {target_task}

Instrucción: {original_prompt}

Formato de respuesta esperado:
- Clasificación: [CATEGORÍA]
- Confianza: [0.0-1.0]
- Justificación: [EXPLICACIÓN BREVE]

Ejemplos:
Entrada: "Este producto es excelente"
Salida: Clasificación: Positivo, Confianza: 0.95, Justificación: Expresa satisfacción clara

Entrada: "No me gustó nada"
Salida: Clasificación: Negativo, Confianza: 0.90, Justificación: Expresa desagrado directo

Ahora clasifica: {original_prompt}"""
                
            elif "generación" in target_task.lower():
                optimized_template = f"""Tarea: {target_task}

Contexto: {original_prompt}

Instrucciones:
1. Mantén el tono y estilo apropiados
2. Estructura la respuesta de manera clara
3. Incluye detalles relevantes
4. Asegura coherencia y fluidez

Genera contenido basado en: {original_prompt}"""
                
            else:
                optimized_template = f"""Tarea: {target_task}

Prompt: {original_prompt}

Requisitos:
- Respuesta precisa y relevante
- Formato apropiado para la tarea
- Calidad profesional y clara

Responde a: {original_prompt}"""
            
            # Create optimized template
            template = PromptTemplate(
                id=hashlib.md5(f"{original_prompt}{time.time()}".encode()).hexdigest()[:8],
                name=f"Optimized_{target_task}_{model_type.value}",
                template=optimized_template,
                variables=[target_task, original_prompt],
                performance_score=random.uniform(0.8, 0.95),
                usage_count=0
            )
            
            self.prompt_templates.append(template)
            return template
            
        except Exception as e:
            logger.error(f"Error optimizing prompt: {e}")
            # Return basic template as fallback
            return PromptTemplate(
                id="",
                name="Fallback_Template",
                template=original_prompt,
                variables=[],
                performance_score=0.5,
                usage_count=0
            )

class ModelPerformanceOptimizer:
    """Optimizador de rendimiento de modelos"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.optimization_history = []
        self.performance_baselines = {}
        
    async def optimize_model_performance(self, model_config: ModelConfiguration,
                                      target_metrics: List[PerformanceMetric]) -> OptimizationResult:
        """Optimizar rendimiento del modelo"""
        start_time = time.time()
        
        try:
            # Simulate performance optimization
            optimization_techniques = []
            
            if PerformanceMetric.LATENCY in target_metrics:
                optimization_techniques.append("Quantización INT8")
                optimization_techniques.append("Optimización de kernels")
                
            if PerformanceMetric.MEMORY_USAGE in target_metrics:
                optimization_techniques.append("Pruning adaptativo")
                optimization_techniques.append("Compresión de pesos")
                
            if PerformanceMetric.THROUGHPUT in target_metrics:
                optimization_techniques.append("Batching inteligente")
                optimization_techniques.append("Paralelización")
            
            # Simulate optimization process
            for technique in optimization_techniques:
                await asyncio.sleep(0.3)
                logger.info(f"🔧 Aplicando: {technique}")
            
            optimization_time = time.time() - start_time
            
            # Simulate performance improvements
            improvements = {}
            for metric in target_metrics:
                if metric == PerformanceMetric.LATENCY:
                    improvements['latency'] = random.uniform(20, 60)  # ms
                elif metric == PerformanceMetric.MEMORY_USAGE:
                    improvements['memory_usage'] = random.uniform(1.5, 4.0)  # GB
                elif metric == PerformanceMetric.THROUGHPUT:
                    improvements['throughput'] = random.uniform(200, 800)  # requests/sec
                elif metric == PerformanceMetric.ACCURACY:
                    improvements['accuracy'] = random.uniform(0.85, 0.95)
            
            # Calculate overall improvement
            improvement_percentage = random.uniform(15, 45)
            
            result = OptimizationResult(
                model_id=model_config.model_id,
                strategy=OptimizationStrategy.QUANTIZATION,
                performance_metrics=improvements,
                training_time=optimization_time,
                improvement_percentage=improvement_percentage,
                metadata={
                    'techniques_applied': optimization_techniques,
                    'target_metrics': [m.value for m in target_metrics],
                    'model_type': model_config.model_type.value
                }
            )
            
            self.optimization_history.append(result)
            return result
            
        except Exception as e:
            return OptimizationResult(
                model_id=model_config.model_id,
                strategy=OptimizationStrategy.QUANTIZATION,
                performance_metrics={},
                training_time=time.time() - start_time,
                improvement_percentage=0.0,
                metadata={},
                success=False,
                error_message=str(e)
            )

class ModelEvaluator:
    """Evaluador de modelos"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.evaluation_history = []
        self.benchmark_datasets = {
            'general': 'Dataset general de evaluación',
            'domain_specific': 'Dataset específico del dominio',
            'edge_cases': 'Casos límite y excepcionales',
            'performance': 'Dataset de rendimiento'
        }
        
    async def evaluate_model(self, model_config: ModelConfiguration,
                           dataset: TrainingDataset,
                           evaluation_type: str = 'comprehensive') -> Dict[str, Any]:
        """Evaluar modelo con métricas completas"""
        try:
            # Simulate comprehensive evaluation
            evaluation_metrics = {}
            
            if evaluation_type == 'comprehensive':
                # Simulate different evaluation aspects
                await asyncio.sleep(1)  # Simulate evaluation time
                
                evaluation_metrics = {
                    'accuracy': random.uniform(0.75, 0.95),
                    'precision': random.uniform(0.70, 0.93),
                    'recall': random.uniform(0.72, 0.94),
                    'f1_score': random.uniform(0.73, 0.94),
                    'latency_p50': random.uniform(30, 120),
                    'latency_p95': random.uniform(80, 200),
                    'latency_p99': random.uniform(150, 300),
                    'throughput': random.uniform(150, 600),
                    'memory_usage': random.uniform(2.0, 8.0),
                    'gpu_utilization': random.uniform(0.6, 0.95),
                    'error_rate': random.uniform(0.01, 0.08)
                }
                
                # Calculate composite scores
                evaluation_metrics['quality_score'] = (
                    evaluation_metrics['accuracy'] * 0.4 +
                    evaluation_metrics['f1_score'] * 0.3 +
                    (1 - evaluation_metrics['error_rate']) * 0.3
                )
                
                evaluation_metrics['performance_score'] = (
                    (1 / evaluation_metrics['latency_p50']) * 0.4 +
                    evaluation_metrics['throughput'] / 1000 * 0.3 +
                    (1 - evaluation_metrics['memory_usage'] / 10) * 0.3
                )
                
                evaluation_metrics['overall_score'] = (
                    evaluation_metrics['quality_score'] * 0.6 +
                    evaluation_metrics['performance_score'] * 0.4
                )
            
            evaluation_result = {
                'model_id': model_config.model_id,
                'evaluation_type': evaluation_type,
                'dataset_size': dataset.size,
                'metrics': evaluation_metrics,
                'timestamp': datetime.now().isoformat(),
                'recommendations': self._generate_recommendations(evaluation_metrics)
            }
            
            self.evaluation_history.append(evaluation_result)
            return evaluation_result
            
        except Exception as e:
            logger.error(f"Error evaluating model: {e}")
            return {'error': str(e)}
    
    def _generate_recommendations(self, metrics: Dict[str, float]) -> List[str]:
        """Generar recomendaciones basadas en métricas"""
        recommendations = []
        
        if metrics.get('accuracy', 0) < 0.8:
            recommendations.append("Considerar fine-tuning adicional con más datos")
            
        if metrics.get('latency_p95', 0) > 150:
            recommendations.append("Optimizar inferencia con cuantización o pruning")
            
        if metrics.get('memory_usage', 0) > 6.0:
            recommendations.append("Reducir tamaño del modelo o usar compresión")
            
        if metrics.get('error_rate', 0) > 0.05:
            recommendations.append("Mejorar manejo de casos límite y validación")
        
        if not recommendations:
            recommendations.append("Modelo funcionando bien, mantener configuración actual")
            
        return recommendations

class DomainAdapter:
    """Adaptador de dominio para modelos"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.domain_knowledge = {}
        self.adaptation_history = []
        
    async def adapt_model_to_domain(self, model_config: ModelConfiguration,
                                  domain_data: TrainingDataset,
                                  domain_name: str) -> OptimizationResult:
        """Adaptar modelo a dominio específico"""
        start_time = time.time()
        
        try:
            # Simulate domain adaptation process
            adaptation_steps = [
                "Análisis de características del dominio",
                "Identificación de patrones específicos",
                "Ajuste de parámetros del modelo",
                "Validación con datos del dominio",
                "Optimización final"
            ]
            
            for step in adaptation_steps:
                await asyncio.sleep(0.4)
                logger.info(f"🔄 {step}")
            
            adaptation_time = time.time() - start_time
            
            # Simulate domain-specific improvements
            domain_accuracy = random.uniform(0.80, 0.96)
            general_accuracy = random.uniform(0.70, 0.85)
            improvement = ((domain_accuracy - general_accuracy) / general_accuracy) * 100
            
            result = OptimizationResult(
                model_id=model_config.model_id,
                strategy=OptimizationStrategy.ADAPTIVE_LEARNING,
                performance_metrics={
                    'domain_accuracy': domain_accuracy,
                    'general_accuracy': general_accuracy,
                    'domain_specific_improvement': improvement,
                    'adaptation_confidence': random.uniform(0.75, 0.95)
                },
                training_time=adaptation_time,
                improvement_percentage=improvement,
                metadata={
                    'domain_name': domain_name,
                    'domain_data_size': domain_data.size,
                    'adaptation_steps': adaptation_steps,
                    'model_type': model_config.model_type.value
                }
            )
            
            self.adaptation_history.append(result)
            return result
            
        except Exception as e:
            return OptimizationResult(
                model_id=model_config.model_id,
                strategy=OptimizationStrategy.ADAPTIVE_LEARNING,
                performance_metrics={},
                training_time=time.time() - start_time,
                improvement_percentage=0.0,
                metadata={},
                success=False,
                error_message=str(e)
            )

class LanguageModelOptimizationSystem:
    """Sistema principal de optimización de modelos de lenguaje v4.6"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.is_running = False
        
        # Initialize components
        self.fine_tuner = IntelligentFineTuner(config)
        self.prompt_engineer = AdvancedPromptEngineer(config)
        self.performance_optimizer = ModelPerformanceOptimizer(config)
        self.model_evaluator = ModelEvaluator(config)
        self.domain_adapter = DomainAdapter(config)
        
        # System state
        self.optimization_queue = []
        self.completed_optimizations = []
        self.performance_metrics = {
            'total_optimizations': 0,
            'successful_optimizations': 0,
            'average_improvement': 0.0,
            'total_training_time': 0.0
        }
        
        logger.info("🚀 Sistema de Optimización de Modelos de Lenguaje v4.6 inicializado")
    
    async def start(self):
        """Iniciar el sistema"""
        if self.is_running:
            logger.warning("⚠️ Sistema ya está ejecutándose")
            return
        
        self.is_running = True
        logger.info("🚀 Sistema de Optimización de Modelos de Lenguaje v4.6 iniciado")
        
        # Start background tasks
        asyncio.create_task(self._process_optimization_queue())
        asyncio.create_task(self._update_performance_metrics())
    
    async def stop(self):
        """Detener el sistema"""
        self.is_running = False
        logger.info("🛑 Sistema de Optimización de Modelos de Lenguaje v4.6 detenido")
    
    async def optimize_model(self, model_config: ModelConfiguration,
                           dataset: TrainingDataset,
                           optimization_type: OptimizationStrategy,
                           **kwargs) -> OptimizationResult:
        """Optimizar modelo con estrategia específica"""
        try:
            if optimization_type == OptimizationStrategy.FINE_TUNING:
                strategy = kwargs.get('strategy', 'balanced')
                return await self.fine_tuner.fine_tune_model(model_config, dataset, strategy)
                
            elif optimization_type == OptimizationStrategy.PROMPT_ENGINEERING:
                target_task = kwargs.get('target_task', 'general')
                return await self._optimize_prompts(model_config, dataset, target_task)
                
            elif optimization_type == OptimizationStrategy.QUANTIZATION:
                target_metrics = kwargs.get('target_metrics', [PerformanceMetric.LATENCY])
                return await self.performance_optimizer.optimize_model_performance(
                    model_config, target_metrics
                )
                
            elif optimization_type == OptimizationStrategy.ADAPTIVE_LEARNING:
                domain_name = kwargs.get('domain_name', 'general')
                return await self.domain_adapter.adapt_model_to_domain(
                    model_config, dataset, domain_name
                )
                
            else:
                raise ValueError(f"Estrategia de optimización no soportada: {optimization_type}")
                
        except Exception as e:
            logger.error(f"Error optimizing model: {e}")
            return OptimizationResult(
                model_id=model_config.model_id,
                strategy=optimization_type,
                performance_metrics={},
                training_time=0.0,
                improvement_percentage=0.0,
                metadata={'error': str(e)},
                success=False,
                error_message=str(e)
            )
    
    async def _optimize_prompts(self, model_config: ModelConfiguration,
                               dataset: TrainingDataset,
                               target_task: str) -> OptimizationResult:
        """Optimizar prompts para el modelo"""
        start_time = time.time()
        
        try:
            # Create sample prompts from dataset
            sample_prompts = [f"Sample prompt {i}" for i in range(min(5, dataset.size))]
            
            # Optimize each prompt
            optimized_templates = []
            for prompt in sample_prompts:
                template = await self.prompt_engineer.optimize_prompt(
                    prompt, target_task, model_config.model_type
                )
                optimized_templates.append(template)
            
            optimization_time = time.time() - start_time
            
            # Calculate average improvement
            avg_performance = sum(t.performance_score for t in optimized_templates) / len(optimized_templates)
            improvement = (avg_performance - 0.5) * 100  # Assuming 0.5 as baseline
            
            return OptimizationResult(
                model_id=model_config.model_id,
                strategy=OptimizationStrategy.PROMPT_ENGINEERING,
                performance_metrics={
                    'prompt_quality_score': avg_performance,
                    'templates_created': len(optimized_templates),
                    'optimization_confidence': random.uniform(0.7, 0.95)
                },
                training_time=optimization_time,
                improvement_percentage=improvement,
                metadata={
                    'target_task': target_task,
                    'optimized_templates': [t.name for t in optimized_templates],
                    'model_type': model_config.model_type.value
                }
            )
            
        except Exception as e:
            return OptimizationResult(
                model_id=model_config.model_id,
                strategy=OptimizationStrategy.PROMPT_ENGINEERING,
                performance_metrics={},
                training_time=time.time() - start_time,
                improvement_percentage=0.0,
                metadata={},
                success=False,
                error_message=str(e)
            )
    
    async def evaluate_model_performance(self, model_config: ModelConfiguration,
                                       dataset: TrainingDataset,
                                       evaluation_type: str = 'comprehensive') -> Dict[str, Any]:
        """Evaluar rendimiento del modelo"""
        return await self.model_evaluator.evaluate_model(
            model_config, dataset, evaluation_type
        )
    
    async def _process_optimization_queue(self):
        """Procesar cola de optimización en background"""
        while self.is_running:
            if self.optimization_queue:
                # Process optimization requests
                await asyncio.sleep(1)
            
            await asyncio.sleep(1)
    
    async def _update_performance_metrics(self):
        """Actualizar métricas de rendimiento"""
        while self.is_running:
            if self.completed_optimizations:
                total_improvement = sum(o.improvement_percentage for o in self.completed_optimizations)
                total_time = sum(o.training_time for o in self.completed_optimizations)
                
                self.performance_metrics.update({
                    'total_optimizations': len(self.completed_optimizations),
                    'successful_optimizations': len([o for o in self.completed_optimizations if o.success]),
                    'average_improvement': total_improvement / len(self.completed_optimizations),
                    'total_training_time': total_time
                })
            
            await asyncio.sleep(30)  # Update every 30 seconds
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado del sistema"""
        return {
            'system_name': 'Sistema de Optimización de Modelos de Lenguaje v4.6',
            'status': 'running' if self.is_running else 'stopped',
            'performance_metrics': self.performance_metrics,
            'queue_size': len(self.optimization_queue),
            'completed_optimizations': len(self.completed_optimizations),
            'timestamp': datetime.now().isoformat()
        }
    
    async def get_optimization_history(self, limit: int = 100) -> List[OptimizationResult]:
        """Obtener historial de optimizaciones"""
        return self.completed_optimizations[-limit:] if self.completed_optimizations else []

# Example usage and testing
async def main():
    """Función principal de ejemplo"""
    config = {
        'max_concurrent_optimizations': 5,
        'evaluation_timeout': 120,
        'optimization_quality_threshold': 0.7
    }
    
    system = LanguageModelOptimizationSystem(config)
    await system.start()
    
    # Example model configuration
    model_config = ModelConfiguration(
        model_id="",
        model_type=ModelType.GPT,
        base_model="gpt-3.5-turbo",
        parameters={'max_tokens': 1000, 'temperature': 0.7},
        hyperparameters={'learning_rate': 1e-5, 'batch_size': 16}
    )
    
    # Example training dataset
    dataset = TrainingDataset(
        id="",
        name="Domain_Specific_Data",
        description="Dataset para adaptación de dominio",
        data_samples=[{"input": f"Sample {i}", "output": f"Response {i}"} for i in range(100)],
        metadata={'domain': 'technical', 'language': 'spanish'}
    )
    
    # Run different optimization strategies
    optimizations = await asyncio.gather(
        system.optimize_model(model_config, dataset, OptimizationStrategy.FINE_TUNING, strategy='balanced'),
        system.optimize_model(model_config, dataset, OptimizationStrategy.PROMPT_ENGINEERING, target_task='clasificación'),
        system.optimize_model(model_config, dataset, OptimizationStrategy.QUANTIZATION, target_metrics=[PerformanceMetric.LATENCY, PerformanceMetric.MEMORY_USAGE])
    )
    
    # Display results
    for i, result in enumerate(optimizations):
        print(f"\n🎯 Optimización {i+1}:")
        print(f"Estrategia: {result.strategy.value}")
        print(f"Mejora: {result.improvement_percentage:.2f}%")
        print(f"Tiempo: {result.training_time:.2f}s")
        print(f"Métricas: {json.dumps(result.performance_metrics, indent=2)}")
    
    # Evaluate model performance
    evaluation = await system.evaluate_model_performance(model_config, dataset)
    print(f"\n📊 Evaluación del Modelo: {json.dumps(evaluation, indent=2, default=str)}")
    
    # Get system status
    status = await system.get_system_status()
    print(f"\n📊 Estado del Sistema: {json.dumps(status, indent=2, default=str)}")
    
    await system.stop()

if __name__ == "__main__":
    asyncio.run(main())
