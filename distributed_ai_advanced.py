# 🚀 **SISTEMA DE IA DISTRIBUIDA AVANZADA**
# Sistema de inteligencia artificial distribuida con federated learning

import asyncio
import logging
import torch
import torch.nn as nn
from dataclasses import dataclass
from typing import Dict, List, Any
import numpy as np
from datetime import datetime

@dataclass
class FederatedConfig:
    num_nodes: int = 4
    rounds: int = 10
    local_epochs: int = 5
    learning_rate: float = 0.01

class FederatedNeuralNetwork(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, output_size: int):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, output_size)
        )
    
    def forward(self, x):
        return self.network(x)

class DistributedAISystem:
    def __init__(self, config: FederatedConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Modelos distribuidos
        self.global_model = FederatedNeuralNetwork(10, 64, 1).to(self.device)
        self.local_models = []
        
        # Estado del sistema
        self.is_running = False
        self.training_history = []
        
        self._initialize_local_models()
    
    def _initialize_local_models(self):
        """Inicializar modelos locales."""
        for i in range(self.config.num_nodes):
            local_model = FederatedNeuralNetwork(10, 64, 1).to(self.device)
            local_model.load_state_dict(self.global_model.state_dict())
            self.local_models.append(local_model)
    
    async def start(self):
        """Iniciar sistema distribuido."""
        self.is_running = True
        self.logger.info("🚀 Sistema de IA distribuida iniciado")
    
    async def stop(self):
        """Detener sistema."""
        self.is_running = False
        self.logger.info("🛑 Sistema distribuido detenido")
    
    async def federated_training(self):
        """Entrenamiento federado."""
        try:
            self.logger.info("🎯 Iniciando entrenamiento federado")
            
            for round_num in range(self.config.rounds):
                # Entrenamiento local en cada nodo
                local_weights = []
                
                for node_id in range(self.config.num_nodes):
                    weights = await self._train_local_model(node_id)
                    local_weights.append(weights)
                
                # Agregación de modelos
                await self._aggregate_models(local_weights)
                
                # Evaluación global
                global_loss = await self._evaluate_global_model()
                
                self.training_history.append({
                    'round': round_num,
                    'global_loss': global_loss,
                    'timestamp': datetime.now()
                })
                
                self.logger.info(f"Ronda {round_num}: Pérdida global = {global_loss:.6f}")
            
            return self.training_history
            
        except Exception as e:
            self.logger.error(f"❌ Error en entrenamiento federado: {e}")
            return []
    
    async def _train_local_model(self, node_id: int) -> Dict[str, torch.Tensor]:
        """Entrenar modelo local."""
        model = self.local_models[node_id]
        optimizer = torch.optim.Adam(model.parameters(), lr=self.config.learning_rate)
        criterion = nn.MSELoss()
        
        # Datos sintéticos para entrenamiento
        X = torch.randn(100, 10).to(self.device)
        y = torch.randn(100, 1).to(self.device)
        
        model.train()
        for epoch in range(self.config.local_epochs):
            optimizer.zero_grad()
            outputs = model(X)
            loss = criterion(outputs, y)
            loss.backward()
            optimizer.step()
        
        return {name: param.clone() for name, param in model.state_dict().items()}
    
    async def _aggregate_models(self, local_weights: List[Dict[str, torch.Tensor]]):
        """Agregar modelos locales al global."""
        global_state = self.global_model.state_dict()
        
        for param_name in global_state.keys():
            # Promedio de pesos
            avg_weight = torch.stack([weights[param_name] for weights in local_weights]).mean(0)
            global_state[param_name] = avg_weight
        
        self.global_model.load_state_dict(global_state)
        
        # Actualizar modelos locales
        for local_model in self.local_models:
            local_model.load_state_dict(global_state)
    
    async def _evaluate_global_model(self) -> float:
        """Evaluar modelo global."""
        self.global_model.eval()
        criterion = nn.MSELoss()
        
        X_test = torch.randn(50, 10).to(self.device)
        y_test = torch.randn(50, 1).to(self.device)
        
        with torch.no_grad():
            outputs = self.global_model(X_test)
            loss = criterion(outputs, y_test)
        
        return loss.item()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado del sistema."""
        return {
            'is_running': self.is_running,
            'num_nodes': self.config.num_nodes,
            'training_rounds': len(self.training_history),
            'device': str(self.device)
        }

async def main():
    """Función principal."""
    config = FederatedConfig()
    system = DistributedAISystem(config)
    
    try:
        await system.start()
        history = await system.federated_training()
        print(f"✅ Entrenamiento completado: {len(history)} rondas")
        print(f"📊 Estado: {system.get_system_status()}")
        
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo sistema...")
    finally:
        await system.stop()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
