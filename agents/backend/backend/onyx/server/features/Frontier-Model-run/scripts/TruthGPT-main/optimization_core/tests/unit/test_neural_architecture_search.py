"""
Neural Architecture Search (NAS) Test Framework for TruthGPT Optimization Core
===============================================================================

This module implements Neural Architecture Search testing capabilities including:
- Automated architecture discovery
- Performance prediction models
- Architecture optimization algorithms
- Multi-objective optimization
- Evolutionary architecture search
"""

import unittest
import numpy as np
import random
import time
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod
import json
from collections import defaultdict
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ArchitectureGene:
    """Represents a gene in the architecture genome"""
    layer_type: str
    parameters: Dict[str, Any]
    connections: List[int]
    performance_score: float
    complexity_score: float

@dataclass
class ArchitectureGenome:
    """Represents a complete neural architecture"""
    genes: List[ArchitectureGene]
    fitness_score: float
    generation: int
    mutation_history: List[str]
    crossover_history: List[str]

@dataclass
class NASResult:
    """Result of Neural Architecture Search"""
    best_architecture: ArchitectureGenome
    search_history: List[ArchitectureGenome]
    performance_metrics: Dict[str, float]
    optimization_time: float
    convergence_generation: int

class ArchitectureSearchSpace:
    """Define the search space for neural architectures"""
    
    def __init__(self):
        self.layer_types = [
            "conv2d", "conv1d", "linear", "attention", "lstm", "gru",
            "batch_norm", "layer_norm", "dropout", "maxpool", "avgpool"
        ]
        self.parameter_ranges = {
            "conv2d": {"kernel_size": [1, 3, 5, 7], "channels": [16, 32, 64, 128, 256]},
            "conv1d": {"kernel_size": [1, 3, 5], "channels": [32, 64, 128, 256]},
            "linear": {"hidden_size": [64, 128, 256, 512, 1024]},
            "attention": {"num_heads": [1, 2, 4, 8], "head_dim": [32, 64, 128]},
            "lstm": {"hidden_size": [64, 128, 256], "num_layers": [1, 2, 3]},
            "gru": {"hidden_size": [64, 128, 256], "num_layers": [1, 2, 3]},
            "batch_norm": {"eps": [1e-5, 1e-4, 1e-3]},
            "layer_norm": {"eps": [1e-5, 1e-4, 1e-3]},
            "dropout": {"p": [0.1, 0.2, 0.3, 0.4, 0.5]},
            "maxpool": {"kernel_size": [2, 3, 4]},
            "avgpool": {"kernel_size": [2, 3, 4]}
        }
        self.connection_constraints = {
            "max_layers": 20,
            "min_layers": 3,
            "max_connections_per_layer": 5,
            "allow_skip_connections": True
        }
    
    def generate_random_architecture(self, num_layers: int = None) -> ArchitectureGenome:
        """Generate a random architecture within the search space"""
        if num_layers is None:
            num_layers = random.randint(
                self.connection_constraints["min_layers"],
                self.connection_constraints["max_layers"]
            )
        
        genes = []
        for i in range(num_layers):
            layer_type = random.choice(self.layer_types)
            parameters = self._generate_random_parameters(layer_type)
            connections = self._generate_random_connections(i, num_layers)
            
            gene = ArchitectureGene(
                layer_type=layer_type,
                parameters=parameters,
                connections=connections,
                performance_score=0.0,
                complexity_score=0.0
            )
            genes.append(gene)
        
        genome = ArchitectureGenome(
            genes=genes,
            fitness_score=0.0,
            generation=0,
            mutation_history=[],
            crossover_history=[]
        )
        
        return genome
    
    def _generate_random_parameters(self, layer_type: str) -> Dict[str, Any]:
        """Generate random parameters for a layer type"""
        if layer_type not in self.parameter_ranges:
            return {}
        
        parameters = {}
        for param_name, param_range in self.parameter_ranges[layer_type].items():
            if isinstance(param_range, list):
                parameters[param_name] = random.choice(param_range)
            else:
                parameters[param_name] = random.uniform(param_range[0], param_range[1])
        
        return parameters
    
    def _generate_random_connections(self, layer_idx: int, total_layers: int) -> List[int]:
        """Generate random connections for a layer"""
        max_connections = self.connection_constraints["max_connections_per_layer"]
        num_connections = random.randint(0, min(max_connections, layer_idx))
        
        if num_connections == 0:
            return []
        
        # Connect to previous layers
        available_layers = list(range(layer_idx))
        connections = random.sample(available_layers, min(num_connections, len(available_layers)))
        
        return connections

class PerformancePredictor:
    """Predict performance of neural architectures without training"""
    
    def __init__(self):
        self.prediction_model = self._initialize_prediction_model()
        self.feature_extractor = ArchitectureFeatureExtractor()
    
    def _initialize_prediction_model(self) -> Dict[str, Any]:
        """Initialize performance prediction model"""
        return {
            "model_type": "random_forest",
            "features": ["complexity", "depth", "width", "connections"],
            "targets": ["accuracy", "latency", "memory_usage"],
            "trained": False
        }
    
    def predict_performance(self, architecture: ArchitectureGenome) -> Dict[str, float]:
        """Predict performance metrics for an architecture"""
        logger.info("Predicting architecture performance")
        
        # Extract features
        features = self.feature_extractor.extract_features(architecture)
        
        # Predict performance (simulated)
        predictions = self._simulate_performance_prediction(features)
        
        return predictions
    
    def _simulate_performance_prediction(self, features: Dict[str, float]) -> Dict[str, float]:
        """Simulate performance prediction"""
        complexity = features.get("complexity", 1.0)
        depth = features.get("depth", 1.0)
        width = features.get("width", 1.0)
        connections = features.get("connections", 1.0)
        
        # Simulate predictions based on features
        accuracy = 0.8 + 0.1 * np.tanh(-complexity / 10) + 0.05 * np.random.normal()
        latency = 0.1 + 0.05 * depth + 0.02 * width + 0.01 * connections
        memory_usage = 0.5 + 0.3 * complexity + 0.1 * depth + 0.05 * width
        
        return {
            "accuracy": max(0.0, min(1.0, accuracy)),
            "latency": max(0.01, latency),
            "memory_usage": max(0.1, memory_usage),
            "throughput": 1.0 / max(0.01, latency)
        }

class ArchitectureFeatureExtractor:
    """Extract features from neural architectures"""
    
    def extract_features(self, architecture: ArchitectureGenome) -> Dict[str, float]:
        """Extract numerical features from architecture"""
        features = {}
        
        # Basic architecture features
        features["num_layers"] = len(architecture.genes)
        features["num_connections"] = sum(len(gene.connections) for gene in architecture.genes)
        features["avg_connections_per_layer"] = features["num_connections"] / max(1, features["num_layers"])
        
        # Layer type distribution
        layer_types = [gene.layer_type for gene in architecture.genes]
        layer_type_counts = defaultdict(int)
        for layer_type in layer_types:
            layer_type_counts[layer_type] += 1
        
        features["conv_ratio"] = (layer_type_counts["conv2d"] + layer_type_counts["conv1d"]) / max(1, features["num_layers"])
        features["attention_ratio"] = layer_type_counts["attention"] / max(1, features["num_layers"])
        features["rnn_ratio"] = (layer_type_counts["lstm"] + layer_type_counts["gru"]) / max(1, features["num_layers"])
        
        # Complexity features
        features["complexity"] = self._calculate_complexity(architecture)
        features["depth"] = features["num_layers"]
        features["width"] = self._calculate_width(architecture)
        features["connections"] = features["num_connections"]
        
        return features
    
    def _calculate_complexity(self, architecture: ArchitectureGenome) -> float:
        """Calculate architecture complexity"""
        complexity = 0.0
        
        for gene in architecture.genes:
            # Base complexity by layer type
            layer_complexity = {
                "conv2d": 2.0, "conv1d": 1.5, "linear": 1.0,
                "attention": 3.0, "lstm": 2.5, "gru": 2.0,
                "batch_norm": 0.5, "layer_norm": 0.5,
                "dropout": 0.1, "maxpool": 0.3, "avgpool": 0.3
            }.get(gene.layer_type, 1.0)
            
            # Add parameter complexity
            param_complexity = sum(len(str(v)) for v in gene.parameters.values()) / 10.0
            
            # Add connection complexity
            connection_complexity = len(gene.connections) * 0.2
            
            complexity += layer_complexity + param_complexity + connection_complexity
        
        return complexity
    
    def _calculate_width(self, architecture: ArchitectureGenome) -> float:
        """Calculate architecture width"""
        widths = []
        
        for gene in architecture.genes:
            if gene.layer_type in ["conv2d", "conv1d"]:
                width = gene.parameters.get("channels", 32)
            elif gene.layer_type == "linear":
                width = gene.parameters.get("hidden_size", 128)
            elif gene.layer_type == "attention":
                width = gene.parameters.get("num_heads", 4) * gene.parameters.get("head_dim", 64)
            elif gene.layer_type in ["lstm", "gru"]:
                width = gene.parameters.get("hidden_size", 128)
            else:
                width = 1.0
            
            widths.append(width)
        
        return np.mean(widths) if widths else 1.0

class EvolutionaryArchitectureSearch:
    """Evolutionary algorithm for architecture search"""
    
    def __init__(self, population_size: int = 50, generations: int = 100):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = 0.1
        self.crossover_rate = 0.8
        self.elite_size = 5
        
        self.search_space = ArchitectureSearchSpace()
        self.performance_predictor = PerformancePredictor()
        self.population = []
        self.best_architecture = None
        self.search_history = []
    
    def search_architecture(self, objectives: List[str] = None) -> NASResult:
        """Perform evolutionary architecture search"""
        logger.info("Starting evolutionary architecture search")
        
        if objectives is None:
            objectives = ["accuracy", "latency", "memory_usage"]
        
        start_time = time.time()
        
        # Initialize population
        self._initialize_population()
        
        # Evolution loop
        for generation in range(self.generations):
            logger.info(f"Generation {generation + 1}/{self.generations}")
            
            # Evaluate fitness
            self._evaluate_population(objectives)
            
            # Select parents
            parents = self._select_parents()
            
            # Create offspring
            offspring = self._create_offspring(parents)
            
            # Update population
            self._update_population(offspring)
            
            # Track best architecture
            self._update_best_architecture()
            
            # Record search history
            self.search_history.append(self.best_architecture)
            
            # Check convergence
            if self._check_convergence():
                logger.info(f"Converged at generation {generation + 1}")
                break
        
        optimization_time = time.time() - start_time
        
        return NASResult(
            best_architecture=self.best_architecture,
            search_history=self.search_history,
            performance_metrics=self._calculate_final_metrics(),
            optimization_time=optimization_time,
            convergence_generation=generation + 1
        )
    
    def _initialize_population(self):
        """Initialize random population"""
        self.population = []
        
        for _ in range(self.population_size):
            architecture = self.search_space.generate_random_architecture()
            architecture.generation = 0
            self.population.append(architecture)
    
    def _evaluate_population(self, objectives: List[str]):
        """Evaluate fitness of all architectures in population"""
        for architecture in self.population:
            # Predict performance
            predictions = self.performance_predictor.predict_performance(architecture)
            
            # Calculate fitness based on objectives
            fitness = self._calculate_fitness(predictions, objectives)
            architecture.fitness_score = fitness
            
            # Update performance scores in genes
            for gene in architecture.genes:
                gene.performance_score = predictions.get("accuracy", 0.0)
                gene.complexity_score = self.performance_predictor.feature_extractor._calculate_complexity(
                    ArchitectureGenome(genes=[gene], fitness_score=0.0, generation=0, mutation_history=[], crossover_history=[])
                )
    
    def _calculate_fitness(self, predictions: Dict[str, float], objectives: List[str]) -> float:
        """Calculate fitness score based on objectives"""
        fitness = 0.0
        
        for objective in objectives:
            if objective == "accuracy":
                fitness += predictions.get("accuracy", 0.0) * 0.4
            elif objective == "latency":
                # Lower latency is better
                latency = predictions.get("latency", 1.0)
                fitness += (1.0 / max(0.01, latency)) * 0.3
            elif objective == "memory_usage":
                # Lower memory usage is better
                memory = predictions.get("memory_usage", 1.0)
                fitness += (1.0 / max(0.01, memory)) * 0.3
        
        return fitness
    
    def _select_parents(self) -> List[ArchitectureGenome]:
        """Select parents for reproduction"""
        # Sort by fitness
        sorted_population = sorted(self.population, key=lambda x: x.fitness_score, reverse=True)
        
        # Tournament selection
        parents = []
        tournament_size = 3
        
        for _ in range(self.population_size):
            tournament = random.sample(sorted_population, min(tournament_size, len(sorted_population)))
            winner = max(tournament, key=lambda x: x.fitness_score)
            parents.append(winner)
        
        return parents
    
    def _create_offspring(self, parents: List[ArchitectureGenome]) -> List[ArchitectureGenome]:
        """Create offspring through crossover and mutation"""
        offspring = []
        
        for i in range(0, len(parents), 2):
            if i + 1 < len(parents):
                parent1, parent2 = parents[i], parents[i + 1]
                
                # Crossover
                if random.random() < self.crossover_rate:
                    child1, child2 = self._crossover(parent1, parent2)
                    offspring.extend([child1, child2])
                else:
                    offspring.extend([parent1, parent2])
            else:
                offspring.append(parents[i])
        
        # Mutation
        for child in offspring:
            if random.random() < self.mutation_rate:
                self._mutate(child)
        
        return offspring
    
    def _crossover(self, parent1: ArchitectureGenome, parent2: ArchitectureGenome) -> Tuple[ArchitectureGenome, ArchitectureGenome]:
        """Perform crossover between two architectures"""
        # Uniform crossover
        child1_genes = []
        child2_genes = []
        
        max_len = max(len(parent1.genes), len(parent2.genes))
        
        for i in range(max_len):
            if i < len(parent1.genes) and i < len(parent2.genes):
                if random.random() < 0.5:
                    child1_genes.append(parent1.genes[i])
                    child2_genes.append(parent2.genes[i])
                else:
                    child1_genes.append(parent2.genes[i])
                    child2_genes.append(parent1.genes[i])
            elif i < len(parent1.genes):
                child1_genes.append(parent1.genes[i])
            else:
                child2_genes.append(parent2.genes[i])
        
        child1 = ArchitectureGenome(
            genes=child1_genes,
            fitness_score=0.0,
            generation=parent1.generation + 1,
            mutation_history=parent1.mutation_history.copy(),
            crossover_history=parent1.crossover_history + ["uniform"]
        )
        
        child2 = ArchitectureGenome(
            genes=child2_genes,
            fitness_score=0.0,
            generation=parent2.generation + 1,
            mutation_history=parent2.mutation_history.copy(),
            crossover_history=parent2.crossover_history + ["uniform"]
        )
        
        return child1, child2
    
    def _mutate(self, architecture: ArchitectureGenome):
        """Mutate an architecture"""
        mutation_type = random.choice(["add_layer", "remove_layer", "modify_layer", "modify_connections"])
        
        if mutation_type == "add_layer" and len(architecture.genes) < self.search_space.connection_constraints["max_layers"]:
            # Add random layer
            new_gene = self.search_space.generate_random_architecture(1).genes[0]
            insert_pos = random.randint(0, len(architecture.genes))
            architecture.genes.insert(insert_pos, new_gene)
            
        elif mutation_type == "remove_layer" and len(architecture.genes) > self.search_space.connection_constraints["min_layers"]:
            # Remove random layer
            remove_pos = random.randint(0, len(architecture.genes) - 1)
            architecture.genes.pop(remove_pos)
            
        elif mutation_type == "modify_layer":
            # Modify random layer
            if architecture.genes:
                modify_pos = random.randint(0, len(architecture.genes) - 1)
                gene = architecture.genes[modify_pos]
                gene.layer_type = random.choice(self.search_space.layer_types)
                gene.parameters = self.search_space._generate_random_parameters(gene.layer_type)
                
        elif mutation_type == "modify_connections":
            # Modify connections
            if architecture.genes:
                modify_pos = random.randint(0, len(architecture.genes) - 1)
                gene = architecture.genes[modify_pos]
                gene.connections = self.search_space._generate_random_connections(modify_pos, len(architecture.genes))
        
        architecture.mutation_history.append(mutation_type)
    
    def _update_population(self, offspring: List[ArchitectureGenome]):
        """Update population with offspring"""
        # Combine parents and offspring
        combined = self.population + offspring
        
        # Sort by fitness
        combined.sort(key=lambda x: x.fitness_score, reverse=True)
        
        # Keep elite and best offspring
        self.population = combined[:self.population_size]
    
    def _update_best_architecture(self):
        """Update best architecture found so far"""
        current_best = max(self.population, key=lambda x: x.fitness_score)
        
        if self.best_architecture is None or current_best.fitness_score > self.best_architecture.fitness_score:
            self.best_architecture = current_best
    
    def _check_convergence(self) -> bool:
        """Check if the search has converged"""
        if len(self.search_history) < 10:
            return False
        
        # Check if fitness has improved in last 10 generations
        recent_fitness = [arch.fitness_score for arch in self.search_history[-10:]]
        improvement = max(recent_fitness) - min(recent_fitness)
        
        return improvement < 0.01  # Converged if improvement < 1%
    
    def _calculate_final_metrics(self) -> Dict[str, float]:
        """Calculate final search metrics"""
        if not self.search_history:
            return {}
        
        fitness_scores = [arch.fitness_score for arch in self.search_history]
        
        return {
            "best_fitness": max(fitness_scores),
            "avg_fitness": np.mean(fitness_scores),
            "fitness_std": np.std(fitness_scores),
            "fitness_improvement": max(fitness_scores) - min(fitness_scores),
            "search_efficiency": len(self.search_history) / self.generations
        }

class NASTestGenerator(unittest.TestCase):
    """Test cases for Neural Architecture Search Framework"""
    
    def setUp(self):
        self.search_space = ArchitectureSearchSpace()
        self.performance_predictor = PerformancePredictor()
        self.feature_extractor = ArchitectureFeatureExtractor()
        self.evolutionary_search = EvolutionaryArchitectureSearch(population_size=10, generations=5)
    
    def test_search_space_initialization(self):
        """Test search space initialization"""
        self.assertIsInstance(self.search_space.layer_types, list)
        self.assertGreater(len(self.search_space.layer_types), 0)
        
        self.assertIsInstance(self.search_space.parameter_ranges, dict)
        self.assertIn("conv2d", self.search_space.parameter_ranges)
        self.assertIn("linear", self.search_space.parameter_ranges)
        
        self.assertIsInstance(self.search_space.connection_constraints, dict)
        self.assertIn("max_layers", self.search_space.connection_constraints)
        self.assertIn("min_layers", self.search_space.connection_constraints)
    
    def test_random_architecture_generation(self):
        """Test random architecture generation"""
        architecture = self.search_space.generate_random_architecture()
        
        self.assertIsInstance(architecture, ArchitectureGenome)
        self.assertIsInstance(architecture.genes, list)
        self.assertGreater(len(architecture.genes), 0)
        
        for gene in architecture.genes:
            self.assertIsInstance(gene, ArchitectureGene)
            self.assertIn(gene.layer_type, self.search_space.layer_types)
            self.assertIsInstance(gene.parameters, dict)
            self.assertIsInstance(gene.connections, list)
    
    def test_architecture_gene(self):
        """Test architecture gene structure"""
        gene = ArchitectureGene(
            layer_type="conv2d",
            parameters={"kernel_size": 3, "channels": 64},
            connections=[0, 1],
            performance_score=0.85,
            complexity_score=2.0
        )
        
        self.assertEqual(gene.layer_type, "conv2d")
        self.assertEqual(gene.parameters["kernel_size"], 3)
        self.assertEqual(gene.parameters["channels"], 64)
        self.assertEqual(gene.connections, [0, 1])
        self.assertEqual(gene.performance_score, 0.85)
        self.assertEqual(gene.complexity_score, 2.0)
    
    def test_architecture_genome(self):
        """Test architecture genome structure"""
        genes = [
            ArchitectureGene("conv2d", {"kernel_size": 3}, [], 0.8, 2.0),
            ArchitectureGene("linear", {"hidden_size": 128}, [0], 0.9, 1.0)
        ]
        
        genome = ArchitectureGenome(
            genes=genes,
            fitness_score=0.85,
            generation=1,
            mutation_history=["add_layer"],
            crossover_history=["uniform"]
        )
        
        self.assertEqual(len(genome.genes), 2)
        self.assertEqual(genome.fitness_score, 0.85)
        self.assertEqual(genome.generation, 1)
        self.assertEqual(genome.mutation_history, ["add_layer"])
        self.assertEqual(genome.crossover_history, ["uniform"])
    
    def test_performance_prediction(self):
        """Test performance prediction"""
        architecture = self.search_space.generate_random_architecture(num_layers=5)
        predictions = self.performance_predictor.predict_performance(architecture)
        
        self.assertIsInstance(predictions, dict)
        self.assertIn("accuracy", predictions)
        self.assertIn("latency", predictions)
        self.assertIn("memory_usage", predictions)
        self.assertIn("throughput", predictions)
        
        # Check value ranges
        self.assertGreaterEqual(predictions["accuracy"], 0.0)
        self.assertLessEqual(predictions["accuracy"], 1.0)
        self.assertGreater(predictions["latency"], 0.0)
        self.assertGreater(predictions["memory_usage"], 0.0)
        self.assertGreater(predictions["throughput"], 0.0)
    
    def test_feature_extraction(self):
        """Test feature extraction from architectures"""
        architecture = self.search_space.generate_random_architecture(num_layers=6)
        features = self.feature_extractor.extract_features(architecture)
        
        self.assertIsInstance(features, dict)
        self.assertIn("num_layers", features)
        self.assertIn("num_connections", features)
        self.assertIn("complexity", features)
        self.assertIn("depth", features)
        self.assertIn("width", features)
        
        # Check feature values
        self.assertEqual(features["num_layers"], 6)
        self.assertGreaterEqual(features["num_connections"], 0)
        self.assertGreater(features["complexity"], 0)
        self.assertEqual(features["depth"], 6)
        self.assertGreater(features["width"], 0)
    
    def test_evolutionary_search(self):
        """Test evolutionary architecture search"""
        result = self.evolutionary_search.search_architecture()
        
        self.assertIsInstance(result, NASResult)
        self.assertIsInstance(result.best_architecture, ArchitectureGenome)
        self.assertIsInstance(result.search_history, list)
        self.assertIsInstance(result.performance_metrics, dict)
        self.assertGreater(result.optimization_time, 0)
        self.assertGreater(result.convergence_generation, 0)
    
    def test_population_initialization(self):
        """Test population initialization"""
        self.evolutionary_search._initialize_population()
        
        self.assertEqual(len(self.evolutionary_search.population), self.evolutionary_search.population_size)
        
        for architecture in self.evolutionary_search.population:
            self.assertIsInstance(architecture, ArchitectureGenome)
            self.assertEqual(architecture.generation, 0)
    
    def test_fitness_calculation(self):
        """Test fitness calculation"""
        predictions = {
            "accuracy": 0.9,
            "latency": 0.1,
            "memory_usage": 0.5,
            "throughput": 10.0
        }
        
        objectives = ["accuracy", "latency", "memory_usage"]
        fitness = self.evolutionary_search._calculate_fitness(predictions, objectives)
        
        self.assertIsInstance(fitness, float)
        self.assertGreater(fitness, 0)
    
    def test_crossover_operation(self):
        """Test crossover operation"""
        parent1 = self.search_space.generate_random_architecture(num_layers=4)
        parent2 = self.search_space.generate_random_architecture(num_layers=5)
        
        child1, child2 = self.evolutionary_search._crossover(parent1, parent2)
        
        self.assertIsInstance(child1, ArchitectureGenome)
        self.assertIsInstance(child2, ArchitectureGenome)
        self.assertEqual(child1.generation, parent1.generation + 1)
        self.assertEqual(child2.generation, parent2.generation + 1)
        self.assertIn("uniform", child1.crossover_history)
        self.assertIn("uniform", child2.crossover_history)
    
    def test_mutation_operation(self):
        """Test mutation operation"""
        architecture = self.search_space.generate_random_architecture(num_layers=5)
        original_genes = len(architecture.genes)
        
        self.evolutionary_search._mutate(architecture)
        
        # Mutation should either keep same number of genes or change it
        self.assertGreaterEqual(len(architecture.genes), 3)  # Min layers constraint
        self.assertLessEqual(len(architecture.genes), 20)   # Max layers constraint
        self.assertGreater(len(architecture.mutation_history), 0)

def run_nas_tests():
    """Run all NAS tests"""
    logger.info("Running Neural Architecture Search tests")
    
    # Create test suite
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(NASTestGenerator))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Log results
    logger.info(f"NAS tests completed: {result.testsRun} tests run")
    logger.info(f"Failures: {len(result.failures)}")
    logger.info(f"Errors: {len(result.errors)}")
    
    return result

if __name__ == "__main__":
    run_nas_tests()

