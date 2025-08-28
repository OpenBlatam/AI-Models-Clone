"""
Sistema de Machine Learning Distribuido para Arquitectura Modular
Implementa entrenamiento distribuido y federado con PyTorch
"""

import asyncio
import json
import logging
import time
import uuid
import torch
import torch.nn as nn
import torch.optim as optim
import torch.distributed as dist
import torch.multiprocessing as mp
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional, Callable, Tuple
import numpy as np
from pathlib import Path
import pickle
import hashlib

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLTaskType(Enum):
    """Tipos de tareas de ML."""
    TRAINING = "training"
    INFERENCE = "inference"
    EVALUATION = "evaluation"
    FEDERATED_LEARNING = "federated_learning"
    TRANSFER_LEARNING = "transfer_learning"
    HYPERPARAMETER_TUNING = "hyperparameter_tuning"

class ModelStatus(Enum):
    """Estados de los modelos."""
    INITIALIZED = "initialized"
    TRAINING = "training"
    TRAINED = "trained"
    EVALUATING = "evaluating"
    READY = "ready"
    ERROR = "error"
    DEPLOYED = "deployed"

@dataclass
class ModelConfig:
    """Configuración del modelo."""
    model_id: str
    model_type: str
    architecture: Dict[str, Any]
    hyperparameters: Dict[str, Any]
    data_config: Dict[str, Any]
    training_config: Dict[str, Any]
    distributed_config: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TrainingMetrics:
    """Métricas de entrenamiento."""
    epoch: int
    loss: float
    accuracy: float
    learning_rate: float
    gradient_norm: float
    timestamp: float
    node_id: str

@dataclass
class ModelInfo:
    """Información del modelo."""
    model_id: str
    status: ModelStatus
    config: ModelConfig
    metrics: List[TrainingMetrics] = field(default_factory=list)
    checkpoints: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)

class BaseModel(ABC):
    """Clase base para modelos de ML."""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.model = None
        self.optimizer = None
        self.criterion = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.status = ModelStatus.INITIALIZED
        
        # Inicializar modelo
        self._build_model()
        self._setup_training()
    
    @abstractmethod
    def _build_model(self):
        """Construir la arquitectura del modelo."""
        pass
    
    @abstractmethod
    def _setup_training(self):
        """Configurar componentes de entrenamiento."""
        pass
    
    @abstractmethod
    def forward(self, x):
        """Forward pass del modelo."""
        pass
    
    def save_checkpoint(self, path: str, epoch: int, metrics: Dict[str, Any]):
        """Guardar checkpoint del modelo."""
        try:
            checkpoint = {
                'epoch': epoch,
                'model_state_dict': self.model.state_dict(),
                'optimizer_state_dict': self.optimizer.state_dict(),
                'metrics': metrics,
                'config': self.config
            }
            
            torch.save(checkpoint, path)
            logger.info(f"✅ Checkpoint guardado: {path}")
            
        except Exception as e:
            logger.error(f"Error guardando checkpoint: {e}")
    
    def load_checkpoint(self, path: str):
        """Cargar checkpoint del modelo."""
        try:
            checkpoint = torch.load(path, map_location=self.device)
            
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            
            logger.info(f"✅ Checkpoint cargado: {path}")
            return checkpoint
            
        except Exception as e:
            logger.error(f"Error cargando checkpoint: {e}")
            return None

class SimpleNeuralNetwork(BaseModel):
    """Red neuronal simple para demostración."""
    
    def _build_model(self):
        """Construir red neuronal simple."""
        layers = []
        input_size = self.config.architecture.get('input_size', 784)
        hidden_sizes = self.config.architecture.get('hidden_sizes', [512, 256])
        output_size = self.config.architecture.get('output_size', 10)
        
        # Capa de entrada
        layers.append(nn.Linear(input_size, hidden_sizes[0]))
        layers.append(nn.ReLU())
        layers.append(nn.Dropout(0.2))
        
        # Capas ocultas
        for i in range(len(hidden_sizes) - 1):
            layers.append(nn.Linear(hidden_sizes[i], hidden_sizes[i + 1]))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(0.2))
        
        # Capa de salida
        layers.append(nn.Linear(hidden_sizes[-1], output_size))
        
        self.model = nn.Sequential(*layers).to(self.device)
        logger.info(f"✅ Modelo construido: {self.model}")
    
    def _setup_training(self):
        """Configurar entrenamiento."""
        # Optimizador
        lr = self.config.hyperparameters.get('learning_rate', 0.001)
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
        
        # Función de pérdida
        self.criterion = nn.CrossEntropyLoss()
        
        logger.info(f"✅ Entrenamiento configurado: lr={lr}")
    
    def forward(self, x):
        """Forward pass."""
        return self.model(x)

class DistributedTrainingManager:
    """Gestor de entrenamiento distribuido."""
    
    def __init__(self, world_size: int = 4):
        self.world_size = world_size
        self.running = False
        self.models: Dict[str, BaseModel] = {}
        self.training_processes: Dict[str, mp.Process] = {}
        
        # Configurar multiprocessing
        mp.set_start_method('spawn', force=True)
    
    async def start(self):
        """Iniciar gestor de entrenamiento distribuido."""
        if self.running:
            return
        
        self.running = True
        logger.info("🚀 Gestor de entrenamiento distribuido iniciado")
    
    async def stop(self):
        """Detener gestor de entrenamiento distribuido."""
        if not self.running:
            return
        
        # Detener todos los procesos de entrenamiento
        for process in self.training_processes.values():
            if process.is_alive():
                process.terminate()
                process.join()
        
        self.running = False
        logger.info("🛑 Gestor de entrenamiento distribuido detenido")
    
    async def start_distributed_training(self, model_id: str, model: BaseModel) -> bool:
        """Iniciar entrenamiento distribuido."""
        try:
            # Crear proceso de entrenamiento
            process = mp.Process(
                target=self._run_distributed_training,
                args=(model_id, model, self.world_size)
            )
            
            process.start()
            self.training_processes[model_id] = process
            self.models[model_id] = model
            
            logger.info(f"✅ Entrenamiento distribuido iniciado para modelo {model_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error iniciando entrenamiento distribuido: {e}")
            return False
    
    def _run_distributed_training(self, model_id: str, model: BaseModel, world_size: int):
        """Ejecutar entrenamiento distribuido."""
        try:
            # Inicializar proceso distribuido
            dist.init_process_group(backend='nccl', init_method='tcp://localhost:12355',
                                  world_size=world_size, rank=0)
            
            # Configurar modelo para entrenamiento distribuido
            model.model = nn.parallel.DistributedDataParallel(model.model)
            
            # Ejecutar entrenamiento
            self._train_model(model)
            
            # Limpiar
            dist.destroy_process_group()
            
        except Exception as e:
            logger.error(f"Error en entrenamiento distribuido: {e}")
    
    def _train_model(self, model: BaseModel):
        """Entrenar modelo."""
        try:
            # Generar datos sintéticos para demostración
            num_epochs = model.config.training_config.get('num_epochs', 10)
            batch_size = model.config.training_config.get('batch_size', 32)
            
            for epoch in range(num_epochs):
                # Simular entrenamiento
                loss = self._simulate_training_step(model, epoch)
                
                # Guardar métricas
                metrics = TrainingMetrics(
                    epoch=epoch,
                    loss=loss,
                    accuracy=np.random.random(),
                    learning_rate=model.optimizer.param_groups[0]['lr'],
                    gradient_norm=np.random.random(),
                    timestamp=time.time(),
                    node_id=f"node_{dist.get_rank()}"
                )
                
                # Actualizar estado
                model.status = ModelStatus.TRAINING
                
                logger.info(f"Epoch {epoch}: Loss = {loss:.4f}")
                
                # Guardar checkpoint periódicamente
                if epoch % 5 == 0:
                    checkpoint_path = f"checkpoints/model_{model.config.model_id}_epoch_{epoch}.pt"
                    model.save_checkpoint(checkpoint_path, epoch, {'loss': loss})
            
            # Marcar como entrenado
            model.status = ModelStatus.TRAINED
            
        except Exception as e:
            logger.error(f"Error entrenando modelo: {e}")
            model.status = ModelStatus.ERROR
    
    def _simulate_training_step(self, model: BaseModel, epoch: int) -> float:
        """Simular paso de entrenamiento."""
        # Simular pérdida decreciente
        base_loss = 2.0
        decay = 0.1
        noise = np.random.normal(0, 0.1)
        
        loss = base_loss * np.exp(-decay * epoch) + noise
        return max(loss, 0.01)  # Mínimo de 0.01
    
    def get_training_status(self, model_id: str) -> Optional[ModelStatus]:
        """Obtener estado de entrenamiento."""
        if model_id in self.models:
            return self.models[model_id].status
        return None
    
    def get_all_models(self) -> Dict[str, BaseModel]:
        """Obtener todos los modelos."""
        return self.models.copy()

class FederatedLearningManager:
    """Gestor de aprendizaje federado."""
    
    def __init__(self, num_clients: int = 3):
        self.num_clients = num_clients
        self.running = False
        self.global_model: Optional[BaseModel] = None
        self.client_models: Dict[str, BaseModel] = {}
        self.federation_rounds = 0
        
        # Configurar directorio para checkpoints
        Path("federated_checkpoints").mkdir(exist_ok=True)
    
    async def start(self):
        """Iniciar gestor de aprendizaje federado."""
        if self.running:
            return
        
        self.running = True
        logger.info("🚀 Gestor de aprendizaje federado iniciado")
    
    async def stop(self):
        """Detener gestor de aprendizaje federado."""
        self.running = False
        logger.info("🛑 Gestor de aprendizaje federado detenido")
    
    async def initialize_federation(self, global_model: BaseModel):
        """Inicializar federación con modelo global."""
        self.global_model = global_model
        
        # Crear modelos de clientes
        for i in range(self.num_clients):
            client_id = f"client_{i}"
            
            # Clonar modelo global
            client_config = ModelConfig(
                model_id=client_id,
                model_type=global_model.config.model_type,
                architecture=global_model.config.architecture,
                hyperparameters=global_model.config.hyperparameters,
                data_config=global_model.config.data_config,
                training_config=global_model.config.training_config
            )
            
            client_model = SimpleNeuralNetwork(client_config)
            self.client_models[client_id] = client_model
        
        logger.info(f"✅ Federación inicializada con {self.num_clients} clientes")
    
    async def run_federation_round(self) -> Dict[str, Any]:
        """Ejecutar una ronda de federación."""
        if not self.global_model:
            logger.error("Modelo global no inicializado")
            return {}
        
        try:
            self.federation_rounds += 1
            logger.info(f"🔄 Iniciando ronda de federación {self.federation_rounds}")
            
            # Entrenar modelos de clientes
            client_results = {}
            for client_id, client_model in self.client_models.items():
                logger.info(f"📚 Entrenando cliente {client_id}")
                
                # Simular entrenamiento local
                await self._train_client_model(client_model)
                
                # Guardar resultados
                client_results[client_id] = {
                    'status': client_model.status.value,
                    'final_loss': self._get_final_loss(client_model)
                }
            
            # Agregar modelos de clientes al modelo global
            await self._aggregate_models()
            
            # Guardar checkpoint de federación
            checkpoint_path = f"federated_checkpoints/global_model_round_{self.federation_rounds}.pt"
            self.global_model.save_checkpoint(checkpoint_path, self.federation_rounds, {
                'federation_round': self.federation_rounds,
                'client_results': client_results
            })
            
            logger.info(f"✅ Ronda de federación {self.federation_rounds} completada")
            
            return {
                'round': self.federation_rounds,
                'client_results': client_results,
                'global_model_updated': True
            }
            
        except Exception as e:
            logger.error(f"Error en ronda de federación: {e}")
            return {'error': str(e)}
    
    async def _train_client_model(self, client_model: BaseModel):
        """Entrenar modelo de cliente."""
        try:
            # Simular entrenamiento local
            num_epochs = client_model.config.training_config.get('num_epochs', 5)
            
            for epoch in range(num_epochs):
                loss = self._simulate_training_step(client_model, epoch)
                logger.debug(f"Cliente {client_model.config.model_id}, Epoch {epoch}: Loss = {loss:.4f}")
            
            client_model.status = ModelStatus.TRAINED
            
        except Exception as e:
            logger.error(f"Error entrenando modelo de cliente: {e}")
            client_model.status = ModelStatus.ERROR
    
    async def _aggregate_models(self):
        """Agregar modelos de clientes al modelo global."""
        try:
            # Obtener parámetros de todos los clientes
            client_params = []
            for client_model in self.client_models.values():
                if client_model.status == ModelStatus.TRAINED:
                    params = [p.clone() for p in client_model.model.parameters()]
                    client_params.append(params)
            
            if not client_params:
                logger.warning("No hay modelos de clientes para agregar")
                return
            
            # Agregar parámetros (promedio simple)
            global_params = list(self.global_model.model.parameters())
            
            for i, param in enumerate(global_params):
                # Calcular promedio de parámetros
                avg_param = torch.zeros_like(param)
                for client_param in client_params:
                    avg_param += client_param[i]
                
                avg_param /= len(client_params)
                
                # Actualizar parámetro global
                param.data.copy_(avg_param.data)
            
            logger.info("✅ Modelos de clientes agregados al modelo global")
            
        except Exception as e:
            logger.error(f"Error agregando modelos: {e}")
    
    def _simulate_training_step(self, model: BaseModel, epoch: int) -> float:
        """Simular paso de entrenamiento."""
        base_loss = 1.5
        decay = 0.15
        noise = np.random.normal(0, 0.05)
        
        loss = base_loss * np.exp(-decay * epoch) + noise
        return max(loss, 0.01)
    
    def _get_final_loss(self, model: BaseModel) -> float:
        """Obtener pérdida final del modelo."""
        return np.random.uniform(0.1, 0.5)  # Simulado
    
    def get_federation_status(self) -> Dict[str, Any]:
        """Obtener estado de la federación."""
        return {
            'federation_rounds': self.federation_rounds,
            'num_clients': self.num_clients,
            'global_model_ready': self.global_model is not None,
            'clients_status': {
                client_id: model.status.value
                for client_id, model in self.client_models.items()
            }
        }

class DistributedMLOrchestrator:
    """Orquestador principal del sistema de ML distribuido."""
    
    def __init__(self):
        self.distributed_manager = DistributedTrainingManager()
        self.federated_manager = FederatedLearningManager()
        self.running = False
        self.models: Dict[str, ModelInfo] = {}
        
        # Configurar directorio para checkpoints
        Path("checkpoints").mkdir(exist_ok=True)
    
    async def start(self):
        """Iniciar orquestador de ML distribuido."""
        if self.running:
            return
        
        logger.info("🚀 Iniciando orquestador de ML distribuido...")
        
        # Iniciar gestores
        await self.distributed_manager.start()
        await self.federated_manager.start()
        
        self.running = True
        logger.info("✅ Orquestador de ML distribuido iniciado")
    
    async def stop(self):
        """Detener orquestador de ML distribuido."""
        if not self.running:
            return
        
        logger.info("🛑 Deteniendo orquestador de ML distribuido...")
        
        # Detener gestores
        await self.distributed_manager.stop()
        await self.federated_manager.stop()
        
        self.running = False
        logger.info("✅ Orquestador de ML distribuido detenido")
    
    async def create_model(self, config: ModelConfig) -> str:
        """Crear un nuevo modelo."""
        try:
            # Crear instancia del modelo
            if config.model_type == "simple_nn":
                model = SimpleNeuralNetwork(config)
            else:
                raise ValueError(f"Tipo de modelo no soportado: {config.model_type}")
            
            # Crear información del modelo
            model_info = ModelInfo(
                model_id=config.model_id,
                status=ModelStatus.INITIALIZED,
                config=config
            )
            
            self.models[config.model_id] = model_info
            
            logger.info(f"✅ Modelo creado: {config.model_id}")
            return config.model_id
            
        except Exception as e:
            logger.error(f"Error creando modelo: {e}")
            return ""
    
    async def start_distributed_training(self, model_id: str) -> bool:
        """Iniciar entrenamiento distribuido."""
        if model_id not in self.models:
            logger.error(f"Modelo {model_id} no encontrado")
            return False
        
        try:
            # Crear modelo para entrenamiento
            config = self.models[model_id].config
            model = SimpleNeuralNetwork(config)
            
            # Iniciar entrenamiento distribuido
            success = await self.distributed_manager.start_distributed_training(model_id, model)
            
            if success:
                self.models[model_id].status = ModelStatus.TRAINING
                logger.info(f"✅ Entrenamiento distribuido iniciado para {model_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error iniciando entrenamiento distribuido: {e}")
            return False
    
    async def start_federated_learning(self, model_id: str) -> bool:
        """Iniciar aprendizaje federado."""
        if model_id not in self.models:
            logger.error(f"Modelo {model_id} no encontrado")
            return False
        
        try:
            # Crear modelo global
            config = self.models[model_id].config
            global_model = SimpleNeuralNetwork(config)
            
            # Inicializar federación
            await self.federated_manager.initialize_federation(global_model)
            
            # Ejecutar ronda de federación
            result = await self.federated_manager.run_federation_round()
            
            if 'error' not in result:
                self.models[model_id].status = ModelStatus.TRAINED
                logger.info(f"✅ Aprendizaje federado completado para {model_id}")
                return True
            else:
                logger.error(f"Error en aprendizaje federado: {result['error']}")
                return False
            
        except Exception as e:
            logger.error(f"Error iniciando aprendizaje federado: {e}")
            return False
    
    def get_model_status(self, model_id: str) -> Optional[ModelStatus]:
        """Obtener estado de un modelo."""
        if model_id in self.models:
            return self.models[model_id].status
        return None
    
    def get_all_models_info(self) -> Dict[str, ModelInfo]:
        """Obtener información de todos los modelos."""
        return self.models.copy()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado del sistema."""
        return {
            'orchestrator_running': self.running,
            'models_count': len(self.models),
            'models_status': {
                model_id: info.status.value
                for model_id, info in self.models.items()
            },
            'distributed_status': self.distributed_manager.get_training_status("") is not None,
            'federated_status': self.federated_manager.get_federation_status()
        }

async def run_distributed_ml_demo():
    """Ejecutar demostración del sistema de ML distribuido."""
    logger.info("🎯 Iniciando demostración del sistema de ML distribuido...")
    
    # Crear orquestador
    orchestrator = DistributedMLOrchestrator()
    
    try:
        # Iniciar orquestador
        await orchestrator.start()
        
        # Crear modelo
        model_config = ModelConfig(
            model_id="demo_model_1",
            model_type="simple_nn",
            architecture={
                'input_size': 784,
                'hidden_sizes': [512, 256],
                'output_size': 10
            },
            hyperparameters={
                'learning_rate': 0.001,
                'batch_size': 32
            },
            data_config={
                'dataset': 'synthetic',
                'num_samples': 10000
            },
            training_config={
                'num_epochs': 10,
                'batch_size': 32
            }
        )
        
        model_id = await orchestrator.create_model(model_config)
        
        if model_id:
            # Simular operaciones
            await asyncio.sleep(2)
            
            # Obtener estado del sistema
            status = orchestrator.get_system_status()
            logger.info(f"Estado del sistema: {json.dumps(status, indent=2)}")
            
            # Iniciar entrenamiento distribuido
            logger.info("🚀 Iniciando entrenamiento distribuido...")
            await orchestrator.start_distributed_training(model_id)
            
            # Esperar un poco
            await asyncio.sleep(5)
            
            # Iniciar aprendizaje federado
            logger.info("🤝 Iniciando aprendizaje federado...")
            await orchestrator.start_federated_learning(model_id)
            
            # Mantener sistema ejecutándose
            await asyncio.sleep(10)
        
    finally:
        # Detener orquestador
        await orchestrator.stop()
    
    logger.info("✅ Demostración del sistema de ML distribuido completada")

if __name__ == "__main__":
    # Ejecutar demostración
    asyncio.run(run_distributed_ml_demo())
