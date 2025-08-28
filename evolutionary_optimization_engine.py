# 🚀 **MOTOR DE OPTIMIZACIÓN EVOLUTIVA AVANZADA**
# Algoritmos genéticos y evolución neural

import asyncio
import logging
import torch
import torch.nn as nn
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Any, Tuple, Callable
from datetime import datetime
import random
import copy

@dataclass
class EvolutionaryConfig:
    population_size: int = 100
    generations: int = 50
    mutation_rate: float = 0.1
    crossover_rate: float = 0.8
    elite_size: int = 10
    neural_layers: int = 3
    neural_neurons: int = 64
    selection_pressure: float = 2.0

class EvolutionaryNeuralNetwork(nn.Module):
    """Red neuronal evolutiva."""
    
    def __init__(self, input_size: int, output_size: int, config: EvolutionaryConfig):
        super().__init__()
        self.config = config
        
        # Arquitectura evolutiva
        layers = []
        prev_size = input_size
        
        for i in range(config.neural_layers):
            current_size = config.neural_neurons // (2 ** i) if i > 0 else config.neural_neurons
            layers.extend([
                nn.Linear(prev_size, current_size),
                nn.ReLU(),
                nn.Dropout(0.2)
            ])
            prev_size = current_size
        
        layers.append(nn.Linear(prev_size, output_size))
        self.network = nn.Sequential(*layers)
        
        # Parámetros evolutivos
        self.fitness = 0.0
        self.generation = 0
        self.mutations = 0
    
    def forward(self, x):
        return self.network(x)
    
    def mutate(self):
        """Mutación de la red neuronal."""
        self.mutations += 1
        
        for param in self.parameters():
            if random.random() < self.config.mutation_rate:
                # Mutación gaussiana
                noise = torch.randn_like(param) * 0.1
                param.data += noise
    
    def crossover(self, other: 'EvolutionaryNeuralNetwork'):
        """Cruce con otra red neuronal."""
        if random.random() > self.config.crossover_rate:
            return
        
        for param1, param2 in zip(self.parameters(), other.parameters()):
            if random.random() < 0.5:
                # Intercambio de pesos
                temp = param1.data.clone()
                param1.data = param2.data.clone()
                param2.data = temp

class EvolutionaryOptimizationEngine:
    """Motor de optimización evolutiva avanzada."""
    
    def __init__(self, config: EvolutionaryConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Población evolutiva
        self.population = []
        self.best_individual = None
        self.generation_history = []
        
        # Estado del sistema
        self.is_running = False
        self.current_generation = 0
        
        self.logger.info("🧬 Motor de optimización evolutiva inicializado")
    
    async def start(self):
        """Iniciar motor evolutivo."""
        self.is_running = True
        self.logger.info("🚀 Motor evolutivo iniciado")
    
    async def stop(self):
        """Detener motor."""
        self.is_running = False
        self.logger.info("🛑 Motor evolutivo detenido")
    
    def initialize_population(self, input_size: int, output_size: int):
        """Inicializar población evolutiva."""
        self.population = []
        
        for i in range(self.config.population_size):
            individual = EvolutionaryNeuralNetwork(input_size, output_size, self.config).to(self.device)
            individual.generation = 0
            self.population.append(individual)
        
        self.logger.info(f"🧬 Población inicializada: {len(self.population)} individuos")
    
    async def evolutionary_optimization(self, fitness_function: Callable, input_size: int, output_size: int):
        """Optimización evolutiva principal."""
        try:
            self.logger.info("🎯 Iniciando optimización evolutiva")
            
            # Inicializar población
            self.initialize_population(input_size, output_size)
            
            for generation in range(self.config.generations):
                self.current_generation = generation
                
                # Evaluar fitness de la población
                await self._evaluate_population(fitness_function)
                
                # Seleccionar mejores individuos
                elite = self._select_elite()
                
                # Generar nueva población
                new_population = await self._generate_new_population(elite)
                
                # Actualizar población
                self.population = new_population
                
                # Registrar estadísticas
                await self._record_generation_stats(generation)
                
                # Log del progreso
                if generation % 10 == 0:
                    best_fitness = max(ind.fitness for ind in self.population)
                    avg_fitness = np.mean([ind.fitness for ind in self.population])
                    self.logger.info(f"Generación {generation}: Mejor={best_fitness:.4f}, Promedio={avg_fitness:.4f}")
            
            # Encontrar mejor individuo final
            self.best_individual = max(self.population, key=lambda x: x.fitness)
            
            return self.best_individual
            
        except Exception as e:
            self.logger.error(f"❌ Error en optimización evolutiva: {e}")
            return None
    
    async def _evaluate_population(self, fitness_function: Callable):
        """Evaluar fitness de toda la población."""
        for individual in self.population:
            try:
                # Generar datos de prueba
                test_data = torch.randn(100, individual.network[0].in_features).to(self.device)
                
                # Evaluar rendimiento
                individual.eval()
                with torch.no_grad():
                    output = individual(test_data)
                    fitness = fitness_function(output, test_data)
                    individual.fitness = fitness
                
            except Exception as e:
                self.logger.error(f"❌ Error evaluando individuo: {e}")
                individual.fitness = 0.0
    
    def _select_elite(self) -> List[EvolutionaryNeuralNetwork]:
        """Seleccionar individuos élite."""
        # Ordenar por fitness
        sorted_population = sorted(self.population, key=lambda x: x.fitness, reverse=True)
        
        # Seleccionar élite
        elite = sorted_population[:self.config.elite_size]
        
        return elite
    
    async def _generate_new_population(self, elite: List[EvolutionaryNeuralNetwork]) -> List[EvolutionaryNeuralNetwork]:
        """Generar nueva población."""
        new_population = []
        
        # Mantener élite
        for individual in elite:
            new_individual = copy.deepcopy(individual)
            new_individual.generation = self.current_generation + 1
            new_population.append(new_individual)
        
        # Generar nuevos individuos
        while len(new_population) < self.config.population_size:
            # Selección de padres
            parent1 = self._tournament_selection()
            parent2 = self._tournament_selection()
            
            # Crear hijo
            child = copy.deepcopy(parent1)
            child.generation = self.current_generation + 1
            
            # Aplicar cruce
            child.crossover(parent2)
            
            # Aplicar mutación
            child.mutate()
            
            new_population.append(child)
        
        return new_population
    
    def _tournament_selection(self) -> EvolutionaryNeuralNetwork:
        """Selección por torneo."""
        tournament_size = 3
        tournament = random.sample(self.population, tournament_size)
        
        # Selección con presión de selección
        fitnesses = [ind.fitness for ind in tournament]
        probabilities = np.array(fitnesses) ** self.config.selection_pressure
        probabilities = probabilities / np.sum(probabilities)
        
        winner_idx = np.random.choice(len(tournament), p=probabilities)
        return tournament[winner_idx]
    
    async def _record_generation_stats(self, generation: int):
        """Registrar estadísticas de la generación."""
        fitnesses = [ind.fitness for ind in self.population]
        
        stats = {
            'generation': generation,
            'best_fitness': max(fitnesses),
            'avg_fitness': np.mean(fitnesses),
            'std_fitness': np.std(fitnesses),
            'min_fitness': min(fitnesses),
            'timestamp': datetime.now()
        }
        
        self.generation_history.append(stats)
    
    async def adaptive_evolution(self, fitness_function: Callable, input_size: int, output_size: int):
        """Evolución adaptativa con parámetros dinámicos."""
        try:
            self.logger.info("🔄 Iniciando evolución adaptativa")
            
            # Inicializar población
            self.initialize_population(input_size, output_size)
            
            stagnation_counter = 0
            best_fitness_history = []
            
            for generation in range(self.config.generations):
                # Evaluar población
                await self._evaluate_population(fitness_function)
                
                # Obtener mejor fitness
                best_fitness = max(ind.fitness for ind in self.population)
                best_fitness_history.append(best_fitness)
                
                # Detectar estancamiento
                if len(best_fitness_history) > 10:
                    recent_improvement = best_fitness - best_fitness_history[-10]
                    if recent_improvement < 0.01:
                        stagnation_counter += 1
                    else:
                        stagnation_counter = 0
                
                # Adaptar parámetros
                if stagnation_counter > 5:
                    self._adapt_parameters()
                    stagnation_counter = 0
                
                # Continuar evolución
                elite = self._select_elite()
                new_population = await self._generate_new_population(elite)
                self.population = new_population
                
                await self._record_generation_stats(generation)
                
                if generation % 10 == 0:
                    self.logger.info(f"Generación {generation}: Mejor={best_fitness:.4f}, Estancamiento={stagnation_counter}")
            
            self.best_individual = max(self.population, key=lambda x: x.fitness)
            return self.best_individual
            
        except Exception as e:
            self.logger.error(f"❌ Error en evolución adaptativa: {e}")
            return None
    
    def _adapt_parameters(self):
        """Adaptar parámetros evolutivos dinámicamente."""
        # Aumentar tasa de mutación
        self.config.mutation_rate = min(0.3, self.config.mutation_rate * 1.2)
        
        # Aumentar presión de selección
        self.config.selection_pressure = min(5.0, self.config.selection_pressure * 1.1)
        
        # Reducir tamaño de élite temporalmente
        self.config.elite_size = max(5, self.config.elite_size - 1)
        
        self.logger.info(f"🔧 Parámetros adaptados: Mutación={self.config.mutation_rate:.3f}, Presión={self.config.selection_pressure:.2f}")
    
    def get_evolution_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de evolución."""
        if not self.generation_history:
            return {}
        
        latest_stats = self.generation_history[-1]
        
        return {
            'current_generation': self.current_generation,
            'population_size': len(self.population),
            'best_fitness': latest_stats['best_fitness'],
            'avg_fitness': latest_stats['avg_fitness'],
            'generations_completed': len(self.generation_history),
            'best_individual_generation': self.best_individual.generation if self.best_individual else 0,
            'best_individual_mutations': self.best_individual.mutations if self.best_individual else 0
        }

async def main():
    """Función principal."""
    config = EvolutionaryConfig()
    engine = EvolutionaryOptimizationEngine(config)
    
    try:
        await engine.start()
        
        # Función de fitness de ejemplo
        def fitness_function(output, input_data):
            # Simular función de fitness basada en complejidad y precisión
            complexity_penalty = torch.mean(torch.abs(output)).item()
            diversity_bonus = torch.std(output).item()
            return diversity_bonus - 0.1 * complexity_penalty
        
        # Optimización evolutiva
        best_individual = await engine.evolutionary_optimization(fitness_function, 10, 5)
        
        if best_individual:
            print(f"✅ Optimización evolutiva completada")
            print(f"🏆 Mejor individuo: Fitness={best_individual.fitness:.4f}")
            print(f"📊 Estadísticas: {engine.get_evolution_stats()}")
        
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo motor evolutivo...")
    finally:
        await engine.stop()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
