"""
Advanced Optimization Evolution Tests
====================================

Tests for evolutionary optimization algorithms, genetic programming,
and self-evolving optimization strategies.
"""

import unittest
import numpy as np
import torch
import torch.nn as nn
from typing import Dict, List, Any, Optional, Tuple, Callable
import time
import json
import logging
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EvolutionaryOptimizationEngine:
    """Engine for evolutionary optimization algorithms"""
    
    def __init__(self, population_size: int = 50, mutation_rate: float = 0.1, 
                 crossover_rate: float = 0.8, elitism_rate: float = 0.1):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elitism_rate = elitism_rate
        self.population = []
        self.fitness_history = []
        self.generation = 0
        
    def initialize_population(self, parameter_space: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Initialize population with random parameters"""
        population = []
        
        for _ in range(self.population_size):
            individual = {}
            for param_name, param_config in parameter_space.items():
                if param_config['type'] == 'float':
                    individual[param_name] = random.uniform(
                        param_config['min'], param_config['max']
                    )
                elif param_config['type'] == 'int':
                    individual[param_name] = random.randint(
                        param_config['min'], param_config['max']
                    )
                elif param_config['type'] == 'choice':
                    individual[param_name] = random.choice(param_config['options'])
                elif param_config['type'] == 'bool':
                    individual[param_name] = random.choice([True, False])
            
            population.append(individual)
        
        self.population = population
        return population
    
    def evaluate_fitness(self, individual: Dict[str, Any], 
                        fitness_function: Callable) -> float:
        """Evaluate fitness of an individual"""
        try:
            fitness = fitness_function(individual)
            return fitness
        except Exception as e:
            logger.warning(f"Fitness evaluation failed: {e}")
            return 0.0
    
    def selection(self, fitness_scores: List[float]) -> List[Dict[str, Any]]:
        """Select parents for next generation"""
        # Tournament selection
        selected = []
        tournament_size = 3
        
        for _ in range(self.population_size):
            tournament_indices = random.sample(range(len(self.population)), tournament_size)
            tournament_fitness = [fitness_scores[i] for i in tournament_indices]
            winner_index = tournament_indices[np.argmax(tournament_fitness)]
            selected.append(self.population[winner_index])
        
        return selected
    
    def crossover(self, parent1: Dict[str, Any], parent2: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Perform crossover between two parents"""
        if random.random() > self.crossover_rate:
            return parent1.copy(), parent2.copy()
        
        child1 = {}
        child2 = {}
        
        for key in parent1:
            if random.random() < 0.5:
                child1[key] = parent1[key]
                child2[key] = parent2[key]
            else:
                child1[key] = parent2[key]
                child2[key] = parent1[key]
        
        return child1, child2
    
    def mutation(self, individual: Dict[str, Any], parameter_space: Dict[str, Any]) -> Dict[str, Any]:
        """Apply mutation to an individual"""
        mutated = individual.copy()
        
        for param_name, param_config in parameter_space.items():
            if random.random() < self.mutation_rate:
                if param_config['type'] == 'float':
                    # Gaussian mutation
                    noise = np.random.normal(0, 0.1)
                    mutated[param_name] = np.clip(
                        mutated[param_name] + noise,
                        param_config['min'], param_config['max']
                    )
                elif param_config['type'] == 'int':
                    # Random walk mutation
                    step = random.choice([-1, 1])
                    mutated[param_name] = np.clip(
                        mutated[param_name] + step,
                        param_config['min'], param_config['max']
                    )
                elif param_config['type'] == 'choice':
                    # Random choice mutation
                    mutated[param_name] = random.choice(param_config['options'])
                elif param_config['type'] == 'bool':
                    # Flip mutation
                    mutated[param_name] = not mutated[param_name]
        
        return mutated
    
    def evolve_generation(self, fitness_function: Callable, 
                        parameter_space: Dict[str, Any]) -> Dict[str, Any]:
        """Evolve one generation"""
        # Evaluate fitness
        fitness_scores = []
        for individual in self.population:
            fitness = self.evaluate_fitness(individual, fitness_function)
            fitness_scores.append(fitness)
        
        # Record fitness history
        self.fitness_history.append({
            'generation': self.generation,
            'best_fitness': max(fitness_scores),
            'avg_fitness': np.mean(fitness_scores),
            'worst_fitness': min(fitness_scores)
        })
        
        # Selection
        selected = self.selection(fitness_scores)
        
        # Elitism
        elite_count = int(self.elitism_rate * self.population_size)
        elite_indices = np.argsort(fitness_scores)[-elite_count:]
        elite = [self.population[i] for i in elite_indices]
        
        # Crossover and mutation
        new_population = elite.copy()
        
        while len(new_population) < self.population_size:
            parent1 = random.choice(selected)
            parent2 = random.choice(selected)
            
            child1, child2 = self.crossover(parent1, parent2)
            child1 = self.mutation(child1, parameter_space)
            child2 = self.mutation(child2, parameter_space)
            
            new_population.extend([child1, child2])
        
        # Trim to population size
        self.population = new_population[:self.population_size]
        self.generation += 1
        
        return {
            'generation': self.generation,
            'best_fitness': max(fitness_scores),
            'avg_fitness': np.mean(fitness_scores),
            'population': self.population
        }
    
    def run_evolution(self, parameter_space: Dict[str, Any], 
                     fitness_function: Callable, generations: int = 100) -> Dict[str, Any]:
        """Run complete evolution process"""
        # Initialize population
        self.initialize_population(parameter_space)
        
        # Evolve generations
        for gen in range(generations):
            result = self.evolve_generation(fitness_function, parameter_space)
            
            # Log progress
            if gen % 10 == 0:
                logger.info(f"Generation {gen}: Best fitness = {result['best_fitness']:.4f}")
        
        # Return final results
        final_fitness = [self.evaluate_fitness(ind, fitness_function) for ind in self.population]
        best_index = np.argmax(final_fitness)
        
        return {
            'best_individual': self.population[best_index],
            'best_fitness': final_fitness[best_index],
            'fitness_history': self.fitness_history,
            'final_population': self.population
        }

class GeneticProgrammingEngine:
    """Engine for genetic programming optimization"""
    
    def __init__(self, max_depth: int = 5, function_set: List[str] = None):
        self.max_depth = max_depth
        self.function_set = function_set or ['+', '-', '*', '/', 'sin', 'cos', 'exp', 'log']
        self.terminal_set = ['x', 'y', 'z', '1', '2', '3']
        self.population = []
        self.fitness_history = []
        
    def create_random_tree(self, depth: int = 0) -> Dict[str, Any]:
        """Create a random expression tree"""
        if depth >= self.max_depth or random.random() < 0.3:
            # Terminal node
            return {
                'type': 'terminal',
                'value': random.choice(self.terminal_set)
            }
        else:
            # Function node
            function = random.choice(self.function_set)
            arity = self._get_function_arity(function)
            
            children = []
            for _ in range(arity):
                child = self.create_random_tree(depth + 1)
                children.append(child)
            
            return {
                'type': 'function',
                'value': function,
                'children': children
            }
    
    def _get_function_arity(self, function: str) -> int:
        """Get arity of a function"""
        if function in ['+', '-', '*', '/']:
            return 2
        elif function in ['sin', 'cos', 'exp', 'log']:
            return 1
        else:
            return 1
    
    def evaluate_tree(self, tree: Dict[str, Any], variables: Dict[str, float]) -> float:
        """Evaluate expression tree"""
        if tree['type'] == 'terminal':
            value = tree['value']
            if value in variables:
                return variables[value]
            else:
                return float(value)
        else:
            function = tree['value']
            children_values = [self.evaluate_tree(child, variables) for child in tree['children']]
            
            if function == '+':
                return sum(children_values)
            elif function == '-':
                return children_values[0] - children_values[1] if len(children_values) > 1 else -children_values[0]
            elif function == '*':
                result = 1
                for val in children_values:
                    result *= val
                return result
            elif function == '/':
                return children_values[0] / children_values[1] if children_values[1] != 0 else 1
            elif function == 'sin':
                return np.sin(children_values[0])
            elif function == 'cos':
                return np.cos(children_values[0])
            elif function == 'exp':
                return np.exp(children_values[0])
            elif function == 'log':
                return np.log(abs(children_values[0]) + 1e-8)
            else:
                return 0.0
    
    def crossover_trees(self, tree1: Dict[str, Any], tree2: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Perform crossover between two trees"""
        # Simple crossover: swap random subtrees
        def get_random_subtree(tree):
            if tree['type'] == 'terminal':
                return tree
            else:
                if random.random() < 0.5:
                    return tree
                else:
                    return random.choice(tree['children'])
        
        subtree1 = get_random_subtree(tree1)
        subtree2 = get_random_subtree(tree2)
        
        # Create new trees by swapping subtrees
        new_tree1 = self._replace_subtree(tree1, subtree1, subtree2)
        new_tree2 = self._replace_subtree(tree2, subtree2, subtree1)
        
        return new_tree1, new_tree2
    
    def _replace_subtree(self, tree: Dict[str, Any], old_subtree: Dict[str, Any], 
                        new_subtree: Dict[str, Any]) -> Dict[str, Any]:
        """Replace a subtree in a tree"""
        if tree == old_subtree:
            return new_subtree
        elif tree['type'] == 'function':
            new_children = []
            for child in tree['children']:
                new_child = self._replace_subtree(child, old_subtree, new_subtree)
                new_children.append(new_child)
            return {
                'type': 'function',
                'value': tree['value'],
                'children': new_children
            }
        else:
            return tree
    
    def mutate_tree(self, tree: Dict[str, Any]) -> Dict[str, Any]:
        """Apply mutation to a tree"""
        if random.random() < 0.1:  # 10% chance of mutation
            # Replace with random subtree
            return self.create_random_tree()
        else:
            return tree

class OptimizationEvolutionTests(unittest.TestCase):
    """Test cases for optimization evolution functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.evolution_engine = EvolutionaryOptimizationEngine()
        self.gp_engine = GeneticProgrammingEngine()
        self.parameter_space = {
            'learning_rate': {'type': 'float', 'min': 0.001, 'max': 0.1},
            'batch_size': {'type': 'int', 'min': 16, 'max': 128},
            'optimizer': {'type': 'choice', 'options': ['adam', 'sgd', 'rmsprop']},
            'use_dropout': {'type': 'bool'}
        }
    
    def test_evolution_engine_creation(self):
        """Test evolution engine creation"""
        engine = EvolutionaryOptimizationEngine(
            population_size=100, mutation_rate=0.15, crossover_rate=0.9
        )
        
        self.assertEqual(engine.population_size, 100)
        self.assertEqual(engine.mutation_rate, 0.15)
        self.assertEqual(engine.crossover_rate, 0.9)
        self.assertEqual(len(engine.population), 0)
        self.assertEqual(len(engine.fitness_history), 0)
        self.assertEqual(engine.generation, 0)
    
    def test_population_initialization(self):
        """Test population initialization"""
        population = self.evolution_engine.initialize_population(self.parameter_space)
        
        self.assertEqual(len(population), self.evolution_engine.population_size)
        
        for individual in population:
            self.assertIn('learning_rate', individual)
            self.assertIn('batch_size', individual)
            self.assertIn('optimizer', individual)
            self.assertIn('use_dropout', individual)
            
            # Check parameter ranges
            self.assertGreaterEqual(individual['learning_rate'], 0.001)
            self.assertLessEqual(individual['learning_rate'], 0.1)
            self.assertGreaterEqual(individual['batch_size'], 16)
            self.assertLessEqual(individual['batch_size'], 128)
            self.assertIn(individual['optimizer'], ['adam', 'sgd', 'rmsprop'])
            self.assertIsInstance(individual['use_dropout'], bool)
    
    def test_fitness_evaluation(self):
        """Test fitness evaluation"""
        def simple_fitness(individual):
            # Simple fitness function
            return individual['learning_rate'] * 10 + individual['batch_size'] / 100
        
        individual = {
            'learning_rate': 0.01,
            'batch_size': 32,
            'optimizer': 'adam',
            'use_dropout': True
        }
        
        fitness = self.evolution_engine.evaluate_fitness(individual, simple_fitness)
        self.assertGreater(fitness, 0)
        self.assertIsInstance(fitness, float)
    
    def test_selection(self):
        """Test parent selection"""
        # Initialize population
        self.evolution_engine.initialize_population(self.parameter_space)
        
        # Create fitness scores
        fitness_scores = [random.random() for _ in range(self.evolution_engine.population_size)]
        
        # Test selection
        selected = self.evolution_engine.selection(fitness_scores)
        
        self.assertEqual(len(selected), self.evolution_engine.population_size)
        self.assertIsInstance(selected[0], dict)
    
    def test_crossover(self):
        """Test crossover operation"""
        parent1 = {
            'learning_rate': 0.01,
            'batch_size': 32,
            'optimizer': 'adam',
            'use_dropout': True
        }
        
        parent2 = {
            'learning_rate': 0.05,
            'batch_size': 64,
            'optimizer': 'sgd',
            'use_dropout': False
        }
        
        child1, child2 = self.evolution_engine.crossover(parent1, parent2)
        
        self.assertIsInstance(child1, dict)
        self.assertIsInstance(child2, dict)
        self.assertIn('learning_rate', child1)
        self.assertIn('batch_size', child1)
        self.assertIn('optimizer', child1)
        self.assertIn('use_dropout', child1)
    
    def test_mutation(self):
        """Test mutation operation"""
        individual = {
            'learning_rate': 0.01,
            'batch_size': 32,
            'optimizer': 'adam',
            'use_dropout': True
        }
        
        mutated = self.evolution_engine.mutation(individual, self.parameter_space)
        
        self.assertIsInstance(mutated, dict)
        self.assertIn('learning_rate', mutated)
        self.assertIn('batch_size', mutated)
        self.assertIn('optimizer', mutated)
        self.assertIn('use_dropout', mutated)
    
    def test_generation_evolution(self):
        """Test single generation evolution"""
        def fitness_function(individual):
            return individual['learning_rate'] * 10 + individual['batch_size'] / 100
        
        # Initialize population
        self.evolution_engine.initialize_population(self.parameter_space)
        
        # Evolve one generation
        result = self.evolution_engine.evolve_generation(fitness_function, self.parameter_space)
        
        self.assertIn('generation', result)
        self.assertIn('best_fitness', result)
        self.assertIn('avg_fitness', result)
        self.assertIn('population', result)
        
        self.assertEqual(result['generation'], 1)
        self.assertGreater(result['best_fitness'], 0)
        self.assertGreater(result['avg_fitness'], 0)
        self.assertEqual(len(result['population']), self.evolution_engine.population_size)
    
    def test_complete_evolution(self):
        """Test complete evolution process"""
        def fitness_function(individual):
            return individual['learning_rate'] * 10 + individual['batch_size'] / 100
        
        # Run evolution
        result = self.evolution_engine.run_evolution(
            self.parameter_space, fitness_function, generations=10
        )
        
        self.assertIn('best_individual', result)
        self.assertIn('best_fitness', result)
        self.assertIn('fitness_history', result)
        self.assertIn('final_population', result)
        
        self.assertGreater(result['best_fitness'], 0)
        self.assertGreater(len(result['fitness_history']), 0)
        self.assertEqual(len(result['final_population']), self.evolution_engine.population_size)
    
    def test_genetic_programming_creation(self):
        """Test genetic programming engine creation"""
        engine = GeneticProgrammingEngine(max_depth=3, function_set=['+', '-', '*'])
        
        self.assertEqual(engine.max_depth, 3)
        self.assertIn('+', engine.function_set)
        self.assertIn('-', engine.function_set)
        self.assertIn('*', engine.function_set)
        self.assertEqual(len(engine.population), 0)
        self.assertEqual(len(engine.fitness_history), 0)
    
    def test_random_tree_creation(self):
        """Test random tree creation"""
        tree = self.gp_engine.create_random_tree()
        
        self.assertIn('type', tree)
        self.assertIn('value', tree)
        self.assertIn(tree['type'], ['terminal', 'function'])
        
        if tree['type'] == 'function':
            self.assertIn('children', tree)
            self.assertIsInstance(tree['children'], list)
    
    def test_tree_evaluation(self):
        """Test tree evaluation"""
        # Create a simple tree: x + y
        tree = {
            'type': 'function',
            'value': '+',
            'children': [
                {'type': 'terminal', 'value': 'x'},
                {'type': 'terminal', 'value': 'y'}
            ]
        }
        
        variables = {'x': 2.0, 'y': 3.0}
        result = self.gp_engine.evaluate_tree(tree, variables)
        
        self.assertEqual(result, 5.0)
    
    def test_tree_crossover(self):
        """Test tree crossover"""
        tree1 = {
            'type': 'function',
            'value': '+',
            'children': [
                {'type': 'terminal', 'value': 'x'},
                {'type': 'terminal', 'value': '1'}
            ]
        }
        
        tree2 = {
            'type': 'function',
            'value': '*',
            'children': [
                {'type': 'terminal', 'value': 'y'},
                {'type': 'terminal', 'value': '2'}
            ]
        }
        
        child1, child2 = self.gp_engine.crossover_trees(tree1, tree2)
        
        self.assertIsInstance(child1, dict)
        self.assertIsInstance(child2, dict)
        self.assertIn('type', child1)
        self.assertIn('value', child1)
        self.assertIn('type', child2)
        self.assertIn('value', child2)
    
    def test_tree_mutation(self):
        """Test tree mutation"""
        tree = {
            'type': 'function',
            'value': '+',
            'children': [
                {'type': 'terminal', 'value': 'x'},
                {'type': 'terminal', 'value': '1'}
            ]
        }
        
        mutated = self.gp_engine.mutate_tree(tree)
        
        self.assertIsInstance(mutated, dict)
        self.assertIn('type', mutated)
        self.assertIn('value', mutated)
    
    def test_evolution_convergence(self):
        """Test evolution convergence"""
        def fitness_function(individual):
            # Fitness function that rewards higher learning rates
            return individual['learning_rate'] * 100
        
        # Run evolution
        result = self.evolution_engine.run_evolution(
            self.parameter_space, fitness_function, generations=20
        )
        
        # Check convergence
        fitness_history = result['fitness_history']
        if len(fitness_history) > 1:
            # Best fitness should generally improve
            best_fitnesses = [gen['best_fitness'] for gen in fitness_history]
            self.assertGreaterEqual(best_fitnesses[-1], best_fitnesses[0])
    
    def test_evolution_diversity(self):
        """Test population diversity maintenance"""
        def fitness_function(individual):
            return random.random()  # Random fitness to test diversity
        
        # Run evolution
        result = self.evolution_engine.run_evolution(
            self.parameter_space, fitness_function, generations=10
        )
        
        # Check population diversity
        final_population = result['final_population']
        learning_rates = [ind['learning_rate'] for ind in final_population]
        
        # Should have some diversity in learning rates
        self.assertGreater(max(learning_rates) - min(learning_rates), 0.001)

def run_evolution_tests():
    """Run all evolution tests"""
    print("🚀 Running Optimization Evolution Tests...")
    
    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(OptimizationEvolutionTests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print results
    print(f"\n📊 Evolution Test Results:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   {test}: {traceback}")
    
    if result.errors:
        print(f"\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"   {test}: {traceback}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    run_evolution_tests()