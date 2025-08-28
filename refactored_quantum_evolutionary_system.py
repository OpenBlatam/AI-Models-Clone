# 🚀 **SISTEMA CUÁNTICO-EVOLUTIVO REFACTORIZADO**
# Arquitectura limpia con patrones de diseño avanzados

import asyncio
import logging
import torch
import torch.nn as nn
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Any, Tuple, Callable, Optional, Protocol
from datetime import datetime
import random
import copy
from abc import ABC, abstractmethod
from enum import Enum
import weakref

# ============================================================================
# ENUMERACIONES Y TIPOS
# ============================================================================

class OptimizationStrategy(Enum):
    """Estrategias de optimización disponibles."""
    QUANTUM_FIRST = "quantum_first"
    EVOLUTIONARY_FIRST = "evolutionary_first"
    HYBRID_BALANCED = "hybrid_balanced"
    ADAPTIVE = "adaptive"

class FitnessMetric(Enum):
    """Métricas de fitness disponibles."""
    ENTROPY = "entropy"
    ENTANGLEMENT = "entanglement"
    DIVERSITY = "diversity"
    COMPLEXITY = "complexity"
    HYBRID = "hybrid"

# ============================================================================
# INTERFACES Y PROTOCOLOS
# ============================================================================

class FitnessEvaluator(Protocol):
    """Protocolo para evaluadores de fitness."""
    
    def evaluate(self, individual: 'QuantumEvolutionaryIndividual', 
                quantum_states: List[torch.Tensor]) -> float:
        """Evaluar fitness de un individuo."""
        ...

class QuantumProcessor(Protocol):
    """Protocolo para procesadores cuánticos."""
    
    def process(self, input_data: torch.Tensor) -> torch.Tensor:
        """Procesar datos con lógica cuántica."""
        ...
    
    def measure(self, quantum_state: torch.Tensor) -> Dict[str, Any]:
        """Realizar medición cuántica."""
        ...

class EvolutionaryOperator(Protocol):
    """Protocolo para operadores evolutivos."""
    
    def mutate(self, individual: 'QuantumEvolutionaryIndividual') -> None:
        """Mutación del individuo."""
        ...
    
    def crossover(self, parent1: 'QuantumEvolutionaryIndividual', 
                 parent2: 'QuantumEvolutionaryIndividual') -> 'QuantumEvolutionaryIndividual':
        """Cruce entre dos padres."""
        ...

# ============================================================================
# CONFIGURACIONES
# ============================================================================

@dataclass
class QuantumConfig:
    """Configuración para componentes cuánticos."""
    qubits: int = 8
    shots: int = 2000
    noise_level: float = 0.1
    decoherence_rate: float = 0.05

@dataclass
class EvolutionaryConfig:
    """Configuración para componentes evolutivos."""
    population_size: int = 50
    generations: int = 100
    mutation_rate: float = 0.15
    crossover_rate: float = 0.85
    elite_size: int = 10
    tournament_size: int = 5
    selection_pressure: float = 2.5

@dataclass
class HybridConfig:
    """Configuración para el sistema híbrido."""
    quantum: QuantumConfig = field(default_factory=QuantumConfig)
    evolutionary: EvolutionaryConfig = field(default_factory=EvolutionaryConfig)
    neural_neurons: int = 256
    hybrid_layers: int = 4
    learning_rate: float = 0.001
    optimization_strategy: OptimizationStrategy = OptimizationStrategy.HYBRID_BALANCED
    fitness_metrics: List[FitnessMetric] = field(default_factory=lambda: [FitnessMetric.HYBRID])

# ============================================================================
# COMPONENTES CUÁNTICOS REFACTORIZADOS
# ============================================================================

class QuantumCircuit(nn.Module):
    """Circuito cuántico simulado optimizado."""
    
    def __init__(self, input_size: int, qubits: int, config: QuantumConfig):
        super().__init__()
        self.config = config
        self.qubits = qubits
        
        # Capas cuánticas optimizadas
        self.quantum_layers = nn.Sequential(
            nn.Linear(input_size, qubits * 2),
            nn.Tanh(),
            nn.Dropout(0.1),
            nn.Linear(qubits * 2, qubits),
            nn.ReLU(),
            nn.BatchNorm1d(qubits)
        )
        
        # Parámetros cuánticos
        self.quantum_weights = nn.Parameter(torch.randn(qubits, qubits))
        self.quantum_bias = nn.Parameter(torch.randn(qubits))
        
        # Estado cuántico
        self.quantum_state = None
        self.measurement_history = []
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass cuántico."""
        # Procesamiento cuántico
        quantum_output = self.quantum_layers(x)
        
        # Aplicar transformación cuántica
        quantum_state = torch.matmul(quantum_output, self.quantum_weights) + self.quantum_bias
        
        # Simular decoherencia cuántica
        if self.training:
            noise = torch.randn_like(quantum_state) * self.config.noise_level
            quantum_state = quantum_state + noise
        
        self.quantum_state = quantum_state
        return quantum_state
    
    def measure(self) -> Dict[str, Any]:
        """Realizar medición cuántica."""
        if self.quantum_state is None:
            return {}
        
        with torch.no_grad():
            # Calcular probabilidades
            probs = torch.softmax(self.quantum_state, dim=1)
            
            # Simular medición
            measurements = torch.multinomial(probs, 1)
            
            # Calcular entropía
            entropy = -torch.sum(probs * torch.log(probs + 1e-8), dim=1)
            avg_entropy = torch.mean(entropy).item()
            
            # Calcular entrelazamiento
            correlation = torch.corrcoef(self.quantum_state.t())
            entanglement = torch.mean(torch.abs(correlation)).item()
            
            measurement_data = {
                'probabilities': probs.cpu().numpy(),
                'measurements': measurements.cpu().numpy(),
                'entropy': avg_entropy,
                'entanglement': entanglement,
                'timestamp': datetime.now()
            }
            
            self.measurement_history.append(measurement_data)
            return measurement_data

class QuantumProcessorImpl:
    """Implementación del procesador cuántico."""
    
    def __init__(self, config: QuantumConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def process(self, input_data: torch.Tensor) -> torch.Tensor:
        """Procesar datos con lógica cuántica."""
        # Simular procesamiento cuántico
        quantum_output = torch.tanh(input_data)
        
        # Aplicar ruido cuántico
        noise = torch.randn_like(quantum_output) * self.config.noise_level
        quantum_output = quantum_output + noise
        
        return quantum_output
    
    def measure(self, quantum_state: torch.Tensor) -> Dict[str, Any]:
        """Realizar medición cuántica."""
        try:
            # Calcular métricas cuánticas
            probs = torch.softmax(quantum_state, dim=1)
            entropy = -torch.sum(probs * torch.log(probs + 1e-8), dim=1)
            
            return {
                'entropy': torch.mean(entropy).item(),
                'coherence': torch.mean(torch.abs(quantum_state)).item(),
                'timestamp': datetime.now()
            }
        except Exception as e:
            self.logger.error(f"Error en medición cuántica: {e}")
            return {}

# ============================================================================
# COMPONENTES EVOLUTIVOS REFACTORIZADOS
# ============================================================================

class EvolutionaryIndividual:
    """Individuo evolutivo optimizado."""
    
    def __init__(self, config: EvolutionaryConfig):
        self.config = config
        self.fitness: float = 0.0
        self.generation: int = 0
        self.mutations: int = 0
        self.parents: List[int] = []
        self.birth_timestamp = datetime.now()
        
        # Historial de fitness
        self.fitness_history: List[Tuple[int, float]] = []
    
    def update_fitness(self, fitness: float, generation: int) -> None:
        """Actualizar fitness del individuo."""
        self.fitness = fitness
        self.generation = generation
        self.fitness_history.append((generation, fitness))
    
    def get_fitness_trend(self) -> float:
        """Obtener tendencia del fitness."""
        if len(self.fitness_history) < 2:
            return 0.0
        
        recent_fitness = [f for _, f in self.fitness_history[-5:]]
        if len(recent_fitness) < 2:
            return 0.0
        
        return (recent_fitness[-1] - recent_fitness[0]) / len(recent_fitness)

class MutationOperator:
    """Operador de mutación optimizado."""
    
    def __init__(self, config: EvolutionaryConfig):
        self.config = config
    
    def mutate(self, individual: EvolutionaryIndividual) -> None:
        """Aplicar mutación al individuo."""
        individual.mutations += 1
        
        # Mutación adaptativa basada en el historial
        if individual.get_fitness_trend() < 0:
            # Aumentar tasa de mutación si el fitness está decayendo
            mutation_strength = self.config.mutation_rate * 1.5
        else:
            mutation_strength = self.config.mutation_rate
        
        # Aplicar mutación
        if random.random() < mutation_strength:
            # Lógica de mutación específica
            pass

class CrossoverOperator:
    """Operador de cruce optimizado."""
    
    def __init__(self, config: EvolutionaryConfig):
        self.config = config
    
    def crossover(self, parent1: EvolutionaryIndividual, 
                 parent2: EvolutionaryIndividual) -> EvolutionaryIndividual:
        """Realizar cruce entre dos padres."""
        if random.random() > self.config.crossover_rate:
            return copy.deepcopy(parent1)
        
        # Crear hijo
        child = EvolutionaryIndividual(self.config)
        child.parents = [id(parent1), id(parent2)]
        child.generation = max(parent1.generation, parent2.generation) + 1
        
        # Lógica de cruce específica
        return child

# ============================================================================
# SISTEMA HÍBRIDO REFACTORIZADO
# ============================================================================

class QuantumEvolutionaryLayer(nn.Module):
    """Capa híbrida cuántico-evolutiva refactorizada."""
    
    def __init__(self, input_size: int, output_size: int, config: HybridConfig):
        super().__init__()
        self.config = config
        self.input_size = input_size
        self.output_size = output_size
        
        # Componente cuántico
        self.quantum_circuit = QuantumCircuit(
            input_size, 
            config.quantum.qubits, 
            config.quantum
        )
        
        # Componente evolutivo
        self.evolutionary_weights = nn.Parameter(torch.randn(output_size, config.quantum.qubits))
        self.evolutionary_bias = nn.Parameter(torch.randn(output_size))
        
        # Componente híbrido
        self.hybrid_mixer = nn.Linear(output_size + config.quantum.qubits, output_size)
        
        # Estado de la capa
        self.quantum_measurements: List[Dict[str, Any]] = []
        self.evolutionary_fitness: float = 0.0
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass híbrido."""
        # Procesamiento cuántico
        quantum_output = self.quantum_circuit(x)
        
        # Procesamiento evolutivo
        evolutionary_output = torch.matmul(self.evolutionary_weights, quantum_output.t()).t() + self.evolutionary_bias
        
        # Combinación híbrida
        combined = torch.cat([evolutionary_output, quantum_output], dim=1)
        hybrid_output = self.hybrid_mixer(combined)
        
        # Registrar medición cuántica
        if self.training:
            measurement = self.quantum_circuit.measure()
            if measurement:
                self.quantum_measurements.append(measurement)
        
        return hybrid_output, quantum_output
    
    def get_layer_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de la capa."""
        return {
            'quantum_measurements_count': len(self.quantum_measurements),
            'evolutionary_fitness': self.evolutionary_fitness,
            'quantum_entropy': np.mean([m.get('entropy', 0) for m in self.quantum_measurements[-10:]]) if self.quantum_measurements else 0.0
        }

class QuantumEvolutionaryNetwork(nn.Module):
    """Red neuronal cuántico-evolutiva refactorizada."""
    
    def __init__(self, config: HybridConfig):
        super().__init__()
        self.config = config
        
        # Capas híbridas
        self.hybrid_layers = nn.ModuleList([
            QuantumEvolutionaryLayer(
                config.neural_neurons if i == 0 else config.neural_neurons,
                config.neural_neurons,
                config
            ) for i in range(config.hybrid_layers)
        ])
        
        # Capa de salida
        self.output_layer = nn.Linear(config.neural_neurons, 10)
        
        # Estado de la red
        self.fitness: float = 0.0
        self.generation: int = 0
        self.quantum_measurements: List[Dict[str, Any]] = []
        self.training_history: List[Dict[str, Any]] = []
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, List[torch.Tensor]]:
        """Forward pass de la red."""
        quantum_states = []
        
        # Procesamiento híbrido
        hybrid_output = x
        for layer in self.hybrid_layers:
            hybrid_output, quantum_state = layer(hybrid_output)
            quantum_states.append(quantum_state)
            hybrid_output = torch.relu(hybrid_output)
        
        # Salida final
        final_output = self.output_layer(hybrid_output)
        
        # Acumular mediciones cuánticas
        for layer in self.hybrid_layers:
            self.quantum_measurements.extend(layer.quantum_measurements)
        
        return final_output, quantum_states
    
    def get_network_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de la red."""
        layer_stats = [layer.get_layer_stats() for layer in self.hybrid_layers]
        
        return {
            'fitness': self.fitness,
            'generation': self.generation,
            'quantum_measurements_count': len(self.quantum_measurements),
            'layer_stats': layer_stats,
            'training_history_length': len(self.training_history)
        }

# ============================================================================
# EVALUADORES DE FITNESS REFACTORIZADOS
# ============================================================================

class HybridFitnessEvaluator:
    """Evaluador de fitness híbrido optimizado."""
    
    def __init__(self, config: HybridConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def evaluate(self, individual: QuantumEvolutionaryNetwork, 
                quantum_states: List[torch.Tensor]) -> float:
        """Evaluar fitness híbrido."""
        try:
            # Fitness clásico
            classical_fitness = self._evaluate_classical(individual)
            
            # Fitness cuántico
            quantum_fitness = self._evaluate_quantum(quantum_states)
            
            # Fitness evolutivo
            evolutionary_fitness = self._evaluate_evolutionary(individual)
            
            # Combinación híbrida
            if self.config.optimization_strategy == OptimizationStrategy.QUANTUM_FIRST:
                hybrid_fitness = quantum_fitness * 0.5 + classical_fitness * 0.3 + evolutionary_fitness * 0.2
            elif self.config.optimization_strategy == OptimizationStrategy.EVOLUTIONARY_FIRST:
                hybrid_fitness = evolutionary_fitness * 0.5 + classical_fitness * 0.3 + quantum_fitness * 0.2
            else:  # HYBRID_BALANCED
                hybrid_fitness = (quantum_fitness + classical_fitness + evolutionary_fitness) / 3
            
            return hybrid_fitness
            
        except Exception as e:
            self.logger.error(f"Error evaluando fitness: {e}")
            return 0.0
    
    def _evaluate_classical(self, individual: QuantumEvolutionaryNetwork) -> float:
        """Evaluar fitness clásico."""
        # Simular evaluación clásica
        return random.uniform(0.1, 0.9)
    
    def _evaluate_quantum(self, quantum_states: List[torch.Tensor]) -> float:
        """Evaluar fitness cuántico."""
        if not quantum_states:
            return 0.0
        
        total_entropy = 0.0
        total_entanglement = 0.0
        
        for state in quantum_states:
            # Calcular entropía
            probs = torch.softmax(state, dim=1)
            entropy = -torch.sum(probs * torch.log(probs + 1e-8), dim=1)
            total_entropy += torch.mean(entropy).item()
            
            # Calcular entrelazamiento
            correlation = torch.corrcoef(state.t())
            entanglement = torch.mean(torch.abs(correlation)).item()
            total_entanglement += entanglement
        
        # Normalizar
        avg_entropy = total_entropy / len(quantum_states)
        avg_entanglement = total_entanglement / len(quantum_states)
        
        return avg_entropy * 0.6 + avg_entanglement * 0.4
    
    def _evaluate_evolutionary(self, individual: QuantumEvolutionaryNetwork) -> float:
        """Evaluar fitness evolutivo."""
        # Simular evaluación evolutiva
        return random.uniform(0.1, 0.9)

# ============================================================================
# SISTEMA PRINCIPAL REFACTORIZADO
# ============================================================================

class QuantumEvolutionaryHybridSystem:
    """Sistema híbrido cuántico-evolutivo refactorizado."""
    
    def __init__(self, config: HybridConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Componentes del sistema
        self.fitness_evaluator = HybridFitnessEvaluator(config)
        self.quantum_processor = QuantumProcessorImpl(config.quantum)
        
        # Estado del sistema
        self.population: List[QuantumEvolutionaryNetwork] = []
        self.best_individual: Optional[QuantumEvolutionaryNetwork] = None
        self.generation_history: List[Dict[str, Any]] = []
        self.is_running: bool = False
        self.current_generation: int = 0
        
        # Métricas del sistema
        self.performance_metrics: Dict[str, List[float]] = {
            'best_fitness': [],
            'avg_fitness': [],
            'quantum_entropy': [],
            'evolutionary_diversity': []
        }
        
        self.logger.info("🧬⚛️ Sistema cuántico-evolutivo híbrido refactorizado inicializado")
    
    async def start(self) -> None:
        """Iniciar sistema híbrido."""
        self.is_running = True
        self.logger.info("🚀 Sistema cuántico-evolutivo híbrido refactorizado iniciado")
    
    async def stop(self) -> None:
        """Detener sistema."""
        self.is_running = False
        self.logger.info("🛑 Sistema híbrido refactorizado detenido")
    
    def initialize_population(self) -> None:
        """Inicializar población cuántico-evolutiva."""
        self.population = []
        
        for i in range(self.config.evolutionary.population_size):
            individual = QuantumEvolutionaryNetwork(self.config).to(self.device)
            individual.generation = 0
            self.population.append(individual)
        
        self.logger.info(f"🧬⚛️ Población inicializada: {len(self.population)} individuos")
    
    async def quantum_evolutionary_optimization(self, num_generations: Optional[int] = None) -> Optional[QuantumEvolutionaryNetwork]:
        """Optimización cuántico-evolutiva principal refactorizada."""
        try:
            generations = num_generations or self.config.evolutionary.generations
            self.logger.info(f"🎯 Iniciando optimización cuántico-evolutiva: {generations} generaciones")
            
            # Inicializar población
            self.initialize_population()
            
            for generation in range(generations):
                self.current_generation = generation
                
                # Evaluar fitness cuántico-evolutivo
                await self._evaluate_quantum_population()
                
                # Seleccionar élite cuántica
                elite = self._select_quantum_elite()
                
                # Generar nueva población híbrida
                new_population = await self._generate_quantum_population(elite)
                
                # Actualizar población
                self.population = new_population
                
                # Registrar estadísticas cuánticas
                await self._record_quantum_stats(generation)
                
                # Log del progreso
                if generation % 10 == 0:
                    await self._log_generation_progress(generation)
            
            # Encontrar mejor individuo final
            self.best_individual = max(self.population, key=lambda x: x.fitness)
            
            return self.best_individual
            
        except Exception as e:
            self.logger.error(f"❌ Error en optimización cuántico-evolutiva: {e}")
            return None
    
    async def _evaluate_quantum_population(self) -> None:
        """Evaluar fitness de población con mediciones cuánticas."""
        for individual in self.population:
            try:
                # Generar datos de prueba
                test_data = torch.randn(100, self.config.neural_neurons).to(self.device)
                
                # Evaluar rendimiento cuántico-evolutivo
                individual.eval()
                with torch.no_grad():
                    output, quantum_states = individual(test_data)
                    
                    # Calcular fitness híbrido
                    fitness = self.fitness_evaluator.evaluate(individual, quantum_states)
                    individual.fitness = fitness
                    
                    # Registrar historial de entrenamiento
                    individual.training_history.append({
                        'generation': self.current_generation,
                        'fitness': fitness,
                        'timestamp': datetime.now()
                    })
                
            except Exception as e:
                self.logger.error(f"❌ Error evaluando individuo: {e}")
                individual.fitness = 0.0
    
    def _select_quantum_elite(self) -> List[QuantumEvolutionaryNetwork]:
        """Seleccionar élite cuántico-evolutiva."""
        # Ordenar por fitness
        sorted_population = sorted(self.population, key=lambda x: x.fitness, reverse=True)
        
        # Seleccionar élite (20% de la población)
        elite_size = max(5, len(sorted_population) // 5)
        elite = sorted_population[:elite_size]
        
        return elite
    
    async def _generate_quantum_population(self, elite: List[QuantumEvolutionaryNetwork]) -> List[QuantumEvolutionaryNetwork]:
        """Generar nueva población cuántico-evolutiva."""
        new_population = []
        
        # Mantener élite
        for individual in elite:
            new_individual = copy.deepcopy(individual)
            new_individual.generation = self.current_generation + 1
            new_population.append(new_individual)
        
        # Generar nuevos individuos
        while len(new_population) < self.config.evolutionary.population_size:
            # Selección de padres cuánticos
            parent1 = self._quantum_tournament_selection()
            parent2 = self._quantum_tournament_selection()
            
            # Crear hijo híbrido
            child = copy.deepcopy(parent1)
            child.generation = self.current_generation + 1
            
            # Aplicar cruce cuántico-evolutivo
            self._apply_crossover(child, parent2)
            
            # Aplicar mutación cuántica
            self._apply_mutation(child)
            
            new_population.append(child)
        
        return new_population
    
    def _quantum_tournament_selection(self) -> QuantumEvolutionaryNetwork:
        """Selección por torneo cuántico."""
        tournament_size = self.config.evolutionary.tournament_size
        tournament = random.sample(self.population, tournament_size)
        
        # Selección con presión cuántica
        fitnesses = [ind.fitness for ind in tournament]
        probabilities = np.array(fitnesses) ** self.config.evolutionary.selection_pressure
        probabilities = probabilities / np.sum(probabilities)
        
        winner_idx = np.random.choice(len(tournament), p=probabilities)
        return tournament[winner_idx]
    
    def _apply_crossover(self, child: QuantumEvolutionaryNetwork, 
                        parent2: QuantumEvolutionaryNetwork) -> None:
        """Aplicar cruce entre dos individuos."""
        if random.random() > self.config.evolutionary.crossover_rate:
            return
        
        # Cruce de capas híbridas
        for layer1, layer2 in zip(child.hybrid_layers, parent2.hybrid_layers):
            if random.random() < 0.5:
                # Intercambiar parámetros
                for param1, param2 in zip(layer1.parameters(), layer2.parameters()):
                    if random.random() < 0.5:
                        temp = param1.data.clone()
                        param1.data = param2.data.clone()
                        param2.data = temp
    
    def _apply_mutation(self, individual: QuantumEvolutionaryNetwork) -> None:
        """Aplicar mutación al individuo."""
        for layer in individual.hybrid_layers:
            for param in layer.parameters():
                if random.random() < self.config.evolutionary.mutation_rate:
                    noise = torch.randn_like(param) * 0.1
                    param.data += noise
    
    async def _record_quantum_stats(self, generation: int) -> None:
        """Registrar estadísticas cuántico-evolutivas."""
        fitnesses = [ind.fitness for ind in self.population]
        
        # Calcular estadísticas cuánticas
        quantum_entropies = []
        for individual in self.population:
            if individual.quantum_measurements:
                latest_measurements = individual.quantum_measurements[-10:]  # Últimas 10 mediciones
                avg_entropy = np.mean([m.get('entropy', 0) for m in latest_measurements])
                quantum_entropies.append(avg_entropy)
        
        stats = {
            'generation': generation,
            'best_fitness': max(fitnesses),
            'avg_fitness': np.mean(fitnesses),
            'std_fitness': np.std(fitnesses),
            'quantum_entropy': np.mean(quantum_entropies) if quantum_entropies else 0.0,
            'population_size': len(self.population),
            'timestamp': datetime.now()
        }
        
        self.generation_history.append(stats)
        
        # Actualizar métricas de rendimiento
        self.performance_metrics['best_fitness'].append(stats['best_fitness'])
        self.performance_metrics['avg_fitness'].append(stats['avg_fitness'])
        self.performance_metrics['quantum_entropy'].append(stats['quantum_entropy'])
    
    async def _log_generation_progress(self, generation: int) -> None:
        """Registrar progreso de la generación."""
        best_fitness = max(ind.fitness for ind in self.population)
        avg_fitness = np.mean([ind.fitness for ind in self.population])
        
        self.logger.info(f"Generación {generation}: Mejor={best_fitness:.4f}, Promedio={avg_fitness:.4f}")
    
    async def quantum_evolutionary_inference(self, input_data: torch.Tensor) -> Dict[str, Any]:
        """Inferencia cuántico-evolutiva refactorizada."""
        try:
            if not self.best_individual:
                return {}
            
            self.best_individual.eval()
            
            with torch.no_grad():
                output, quantum_states = self.best_individual(input_data)
                
                # Procesamiento clásico
                classical_probs = torch.softmax(output, dim=1)
                classical_prediction = torch.argmax(classical_probs, dim=1)
                
                # Procesamiento cuántico
                quantum_predictions = []
                quantum_entropies = []
                
                for state in quantum_states:
                    quantum_probs = torch.softmax(state, dim=1)
                    quantum_pred = torch.argmax(quantum_probs, dim=1)
                    quantum_predictions.append(quantum_pred)
                    
                    # Calcular entropía cuántica
                    entropy = -torch.sum(quantum_probs * torch.log(quantum_probs + 1e-8), dim=1)
                    quantum_entropies.append(torch.mean(entropy).item())
                
                # Combinación híbrida
                hybrid_probs = classical_probs
                for quantum_pred in quantum_predictions:
                    quantum_one_hot = torch.zeros_like(classical_probs)
                    quantum_one_hot.scatter_(1, quantum_pred.unsqueeze(1), 1)
                    hybrid_probs = (hybrid_probs + quantum_one_hot) / 2
                
                hybrid_prediction = torch.argmax(hybrid_probs, dim=1)
                
                return {
                    'classical_prediction': classical_prediction.cpu().numpy(),
                    'quantum_predictions': [q.cpu().numpy() for q in quantum_predictions],
                    'hybrid_prediction': hybrid_prediction.cpu().numpy(),
                    'classical_confidence': torch.max(classical_probs, dim=1)[0].cpu().numpy(),
                    'hybrid_confidence': torch.max(hybrid_probs, dim=1)[0].cpu().numpy(),
                    'quantum_entropy': quantum_entropies,
                    'best_individual_stats': self.best_individual.get_network_stats()
                }
                
        except Exception as e:
            self.logger.error(f"❌ Error en inferencia cuántico-evolutiva: {e}")
            return {}
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del sistema."""
        if not self.generation_history:
            return {}
        
        latest_stats = self.generation_history[-1]
        
        return {
            'current_generation': self.current_generation,
            'population_size': len(self.population),
            'best_fitness': latest_stats['best_fitness'],
            'avg_fitness': latest_stats['avg_fitness'],
            'quantum_entropy': latest_stats['quantum_entropy'],
            'generations_completed': len(self.generation_history),
            'best_individual_generation': self.best_individual.generation if self.best_individual else 0,
            'quantum_qubits': self.config.quantum.qubits,
            'performance_metrics': self.performance_metrics
        }

# ============================================================================
# FUNCIÓN PRINCIPAL REFACTORIZADA
# ============================================================================

async def main():
    """Función principal refactorizada."""
    # Configuración del sistema
    config = HybridConfig(
        quantum=QuantumConfig(qubits=8, shots=2000),
        evolutionary=EvolutionaryConfig(population_size=50, generations=100),
        neural_neurons=256,
        hybrid_layers=4,
        optimization_strategy=OptimizationStrategy.HYBRID_BALANCED
    )
    
    # Crear sistema
    system = QuantumEvolutionaryHybridSystem(config)
    
    try:
        await system.start()
        
        # Optimización cuántico-evolutiva
        best_individual = await system.quantum_evolutionary_optimization(50)
        
        if best_individual:
            print(f"✅ Optimización cuántico-evolutiva refactorizada completada")
            print(f"🏆 Mejor individuo: Fitness={best_individual.fitness:.4f}")
            
            # Inferencia de prueba
            test_data = torch.randn(10, config.neural_neurons).to(system.device)
            inference_result = await system.quantum_evolutionary_inference(test_data)
            print(f"🧬⚛️ Inferencia cuántico-evolutiva refactorizada: {inference_result}")
            
            print(f"📊 Estadísticas del sistema: {system.get_system_stats()}")
        
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo sistema cuántico-evolutivo refactorizado...")
    finally:
        await system.stop()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
