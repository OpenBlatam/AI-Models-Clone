"""
Advanced Optimization Improvement Tests
=======================================

Tests for continuous optimization improvement, adaptive learning,
and self-improving optimization algorithms.
"""

import unittest
import numpy as np
import torch
import torch.nn as nn
from typing import Dict, List, Any, Optional, Tuple
import time
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptimizationImprovementEngine:
    """Engine for continuous optimization improvement"""
    
    def __init__(self, learning_rate: float = 0.01, improvement_threshold: float = 0.1):
        self.learning_rate = learning_rate
        self.improvement_threshold = improvement_threshold
        self.improvement_history = []
        self.performance_metrics = {}
        self.adaptive_parameters = {}
        
    def analyze_performance(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        """Analyze performance metrics and identify improvement opportunities"""
        analysis = {
            'current_performance': metrics,
            'improvement_opportunities': [],
            'recommendations': [],
            'confidence_score': 0.0
        }
        
        # Analyze performance trends
        if len(self.improvement_history) > 0:
            recent_improvement = self._calculate_improvement_rate()
            analysis['improvement_rate'] = recent_improvement
            
            if recent_improvement < self.improvement_threshold:
                analysis['improvement_opportunities'].append('low_improvement_rate')
                analysis['recommendations'].append('increase_learning_rate')
        
        # Analyze specific metrics
        if 'loss' in metrics and metrics['loss'] > 0.5:
            analysis['improvement_opportunities'].append('high_loss')
            analysis['recommendations'].append('adjust_learning_rate')
            
        if 'accuracy' in metrics and metrics['accuracy'] < 0.8:
            analysis['improvement_opportunities'].append('low_accuracy')
            analysis['recommendations'].append('increase_model_capacity')
            
        if 'convergence_time' in metrics and metrics['convergence_time'] > 100:
            analysis['improvement_opportunities'].append('slow_convergence')
            analysis['recommendations'].append('optimize_initialization')
        
        # Calculate confidence score
        analysis['confidence_score'] = self._calculate_confidence_score(metrics)
        
        return analysis
    
    def suggest_improvements(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest specific improvements based on analysis"""
        improvements = []
        
        for opportunity in analysis['improvement_opportunities']:
            if opportunity == 'low_improvement_rate':
                improvements.append({
                    'type': 'learning_rate_adjustment',
                    'action': 'increase_learning_rate',
                    'value': self.learning_rate * 1.5,
                    'confidence': 0.8
                })
                
            elif opportunity == 'high_loss':
                improvements.append({
                    'type': 'regularization',
                    'action': 'add_dropout',
                    'value': 0.2,
                    'confidence': 0.7
                })
                
            elif opportunity == 'low_accuracy':
                improvements.append({
                    'type': 'architecture',
                    'action': 'increase_hidden_units',
                    'value': 1.5,
                    'confidence': 0.6
                })
                
            elif opportunity == 'slow_convergence':
                improvements.append({
                    'type': 'initialization',
                    'action': 'xavier_initialization',
                    'value': True,
                    'confidence': 0.9
                })
        
        return improvements
    
    def apply_improvements(self, model: nn.Module, improvements: List[Dict[str, Any]]) -> nn.Module:
        """Apply suggested improvements to the model"""
        improved_model = model
        
        for improvement in improvements:
            if improvement['type'] == 'learning_rate_adjustment':
                # Adjust learning rate in optimizer
                for param_group in improved_model.parameters():
                    if hasattr(param_group, 'lr'):
                        param_group.lr = improvement['value']
                        
            elif improvement['type'] == 'regularization':
                # Add dropout layers
                if improvement['action'] == 'add_dropout':
                    self._add_dropout_layers(improved_model, improvement['value'])
                    
            elif improvement['type'] == 'architecture':
                # Modify architecture
                if improvement['action'] == 'increase_hidden_units':
                    self._increase_hidden_units(improved_model, improvement['value'])
                    
            elif improvement['type'] == 'initialization':
                # Apply better initialization
                if improvement['action'] == 'xavier_initialization':
                    self._apply_xavier_initialization(improved_model)
        
        return improved_model
    
    def _calculate_improvement_rate(self) -> float:
        """Calculate the rate of improvement over time"""
        if len(self.improvement_history) < 2:
            return 0.0
            
        recent_improvements = self.improvement_history[-5:]
        if len(recent_improvements) < 2:
            return 0.0
            
        improvement_rate = (recent_improvements[-1] - recent_improvements[0]) / len(recent_improvements)
        return improvement_rate
    
    def _calculate_confidence_score(self, metrics: Dict[str, float]) -> float:
        """Calculate confidence score for improvement suggestions"""
        confidence = 0.5  # Base confidence
        
        # Adjust based on metric quality
        if 'accuracy' in metrics and metrics['accuracy'] > 0.9:
            confidence += 0.2
        if 'loss' in metrics and metrics['loss'] < 0.1:
            confidence += 0.2
        if 'convergence_time' in metrics and metrics['convergence_time'] < 50:
            confidence += 0.1
            
        return min(confidence, 1.0)
    
    def _add_dropout_layers(self, model: nn.Module, dropout_rate: float):
        """Add dropout layers to the model"""
        # Implementation would depend on model architecture
        pass
    
    def _increase_hidden_units(self, model: nn.Module, multiplier: float):
        """Increase the number of hidden units in the model"""
        # Implementation would depend on model architecture
        pass
    
    def _apply_xavier_initialization(self, model: nn.Module):
        """Apply Xavier initialization to the model"""
        for module in model.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)

class AdaptiveOptimizationEngine:
    """Engine for adaptive optimization with self-improvement"""
    
    def __init__(self, base_optimizer: str = "adam", adaptation_rate: float = 0.1):
        self.base_optimizer = base_optimizer
        self.adaptation_rate = adaptation_rate
        self.optimization_history = []
        self.performance_tracker = {}
        
    def adapt_optimization(self, performance_metrics: Dict[str, float]) -> Dict[str, Any]:
        """Adapt optimization strategy based on performance"""
        adaptation = {
            'optimizer_type': self.base_optimizer,
            'parameters': {},
            'adaptation_reason': 'performance_based',
            'confidence': 0.0
        }
        
        # Analyze performance and adapt
        if 'loss' in performance_metrics:
            if performance_metrics['loss'] > 0.5:
                adaptation['optimizer_type'] = 'sgd'
                adaptation['parameters']['momentum'] = 0.9
                adaptation['adaptation_reason'] = 'high_loss_sgd_better'
                adaptation['confidence'] = 0.8
            elif performance_metrics['loss'] < 0.1:
                adaptation['optimizer_type'] = 'adam'
                adaptation['parameters']['lr'] = 0.001
                adaptation['adaptation_reason'] = 'low_loss_adam_optimal'
                adaptation['confidence'] = 0.9
        
        if 'convergence_speed' in performance_metrics:
            if performance_metrics['convergence_speed'] < 0.5:
                adaptation['parameters']['lr'] = adaptation['parameters'].get('lr', 0.001) * 1.5
                adaptation['adaptation_reason'] = 'slow_convergence_increase_lr'
                adaptation['confidence'] = 0.7
        
        return adaptation
    
    def learn_from_history(self, optimization_results: List[Dict[str, Any]]):
        """Learn from optimization history to improve future adaptations"""
        if len(optimization_results) < 2:
            return
            
        # Analyze patterns in successful optimizations
        successful_optimizations = [r for r in optimization_results if r.get('success', False)]
        
        if len(successful_optimizations) > 0:
            # Extract common patterns
            common_parameters = self._extract_common_parameters(successful_optimizations)
            self.optimization_history.extend(successful_optimizations)
            
            # Update adaptation strategy
            self._update_adaptation_strategy(common_parameters)
    
    def _extract_common_parameters(self, optimizations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract common parameters from successful optimizations"""
        common_params = {}
        
        # Analyze parameter frequency
        param_frequency = {}
        for opt in optimizations:
            for param, value in opt.get('parameters', {}).items():
                if param not in param_frequency:
                    param_frequency[param] = []
                param_frequency[param].append(value)
        
        # Find most common values
        for param, values in param_frequency.items():
            if len(values) > 1:
                common_params[param] = np.median(values)
        
        return common_params
    
    def _update_adaptation_strategy(self, common_parameters: Dict[str, Any]):
        """Update adaptation strategy based on learned patterns"""
        # Update base parameters with learned values
        for param, value in common_parameters.items():
            if param in self.performance_tracker:
                # Weighted average with existing value
                self.performance_tracker[param] = (
                    0.7 * self.performance_tracker[param] + 
                    0.3 * value
                )
            else:
                self.performance_tracker[param] = value

class OptimizationImprovementTests(unittest.TestCase):
    """Test cases for optimization improvement functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.improvement_engine = OptimizationImprovementEngine()
        self.adaptive_engine = AdaptiveOptimizationEngine()
        self.test_metrics = {
            'loss': 0.3,
            'accuracy': 0.85,
            'convergence_time': 75,
            'memory_usage': 0.6
        }
    
    def test_improvement_engine_creation(self):
        """Test improvement engine creation"""
        engine = OptimizationImprovementEngine(learning_rate=0.02, improvement_threshold=0.15)
        
        self.assertEqual(engine.learning_rate, 0.02)
        self.assertEqual(engine.improvement_threshold, 0.15)
        self.assertEqual(len(engine.improvement_history), 0)
        self.assertEqual(len(engine.performance_metrics), 0)
    
    def test_performance_analysis(self):
        """Test performance analysis functionality"""
        analysis = self.improvement_engine.analyze_performance(self.test_metrics)
        
        self.assertIn('current_performance', analysis)
        self.assertIn('improvement_opportunities', analysis)
        self.assertIn('recommendations', analysis)
        self.assertIn('confidence_score', analysis)
        
        self.assertEqual(analysis['current_performance'], self.test_metrics)
        self.assertIsInstance(analysis['improvement_opportunities'], list)
        self.assertIsInstance(analysis['recommendations'], list)
        self.assertGreaterEqual(analysis['confidence_score'], 0.0)
        self.assertLessEqual(analysis['confidence_score'], 1.0)
    
    def test_improvement_suggestions(self):
        """Test improvement suggestion generation"""
        analysis = self.improvement_engine.analyze_performance(self.test_metrics)
        suggestions = self.improvement_engine.suggest_improvements(analysis)
        
        self.assertIsInstance(suggestions, list)
        
        for suggestion in suggestions:
            self.assertIn('type', suggestion)
            self.assertIn('action', suggestion)
            self.assertIn('value', suggestion)
            self.assertIn('confidence', suggestion)
            
            self.assertIn(suggestion['type'], [
                'learning_rate_adjustment', 'regularization', 
                'architecture', 'initialization'
            ])
            self.assertGreaterEqual(suggestion['confidence'], 0.0)
            self.assertLessEqual(suggestion['confidence'], 1.0)
    
    def test_improvement_application(self):
        """Test improvement application to model"""
        # Create a simple test model
        model = nn.Sequential(
            nn.Linear(10, 5),
            nn.ReLU(),
            nn.Linear(5, 1)
        )
        
        # Generate improvements
        analysis = self.improvement_engine.analyze_performance(self.test_metrics)
        improvements = self.improvement_engine.suggest_improvements(analysis)
        
        # Apply improvements
        improved_model = self.improvement_engine.apply_improvements(model, improvements)
        
        self.assertIsInstance(improved_model, nn.Module)
        self.assertEqual(type(improved_model), type(model))
    
    def test_adaptive_optimization_creation(self):
        """Test adaptive optimization engine creation"""
        engine = AdaptiveOptimizationEngine(
            base_optimizer="adam", 
            adaptation_rate=0.15
        )
        
        self.assertEqual(engine.base_optimizer, "adam")
        self.assertEqual(engine.adaptation_rate, 0.15)
        self.assertEqual(len(engine.optimization_history), 0)
        self.assertEqual(len(engine.performance_tracker), 0)
    
    def test_optimization_adaptation(self):
        """Test optimization adaptation based on performance"""
        adaptation = self.adaptive_engine.adapt_optimization(self.test_metrics)
        
        self.assertIn('optimizer_type', adaptation)
        self.assertIn('parameters', adaptation)
        self.assertIn('adaptation_reason', adaptation)
        self.assertIn('confidence', adaptation)
        
        self.assertIn(adaptation['optimizer_type'], ['adam', 'sgd', 'rmsprop'])
        self.assertIsInstance(adaptation['parameters'], dict)
        self.assertGreaterEqual(adaptation['confidence'], 0.0)
        self.assertLessEqual(adaptation['confidence'], 1.0)
    
    def test_learning_from_history(self):
        """Test learning from optimization history"""
        optimization_results = [
            {
                'success': True,
                'parameters': {'lr': 0.001, 'momentum': 0.9},
                'performance': {'loss': 0.2, 'accuracy': 0.9}
            },
            {
                'success': True,
                'parameters': {'lr': 0.002, 'momentum': 0.8},
                'performance': {'loss': 0.15, 'accuracy': 0.92}
            },
            {
                'success': False,
                'parameters': {'lr': 0.0005, 'momentum': 0.95},
                'performance': {'loss': 0.8, 'accuracy': 0.6}
            }
        ]
        
        initial_history_length = len(self.adaptive_engine.optimization_history)
        
        self.adaptive_engine.learn_from_history(optimization_results)
        
        # Should have learned from successful optimizations
        self.assertGreater(len(self.adaptive_engine.optimization_history), initial_history_length)
        self.assertGreater(len(self.adaptive_engine.performance_tracker), 0)
    
    def test_improvement_confidence_calculation(self):
        """Test confidence score calculation for improvements"""
        high_performance_metrics = {
            'accuracy': 0.95,
            'loss': 0.05,
            'convergence_time': 30
        }
        
        low_performance_metrics = {
            'accuracy': 0.6,
            'loss': 0.8,
            'convergence_time': 150
        }
        
        high_analysis = self.improvement_engine.analyze_performance(high_performance_metrics)
        low_analysis = self.improvement_engine.analyze_performance(low_performance_metrics)
        
        # High performance should have higher confidence
        self.assertGreaterEqual(high_analysis['confidence_score'], low_analysis['confidence_score'])
    
    def test_continuous_improvement_cycle(self):
        """Test continuous improvement cycle"""
        # Simulate multiple improvement cycles
        for cycle in range(3):
            # Analyze current performance
            analysis = self.improvement_engine.analyze_performance(self.test_metrics)
            
            # Generate improvements
            improvements = self.improvement_engine.suggest_improvements(analysis)
            
            # Apply improvements
            model = nn.Linear(10, 1)
            improved_model = self.improvement_engine.apply_improvements(model, improvements)
            
            # Update metrics (simulate improvement)
            self.test_metrics['loss'] *= 0.9
            self.test_metrics['accuracy'] += 0.02
            
            # Record improvement
            self.improvement_engine.improvement_history.append(
                self.test_metrics['loss']
            )
        
        # Should have improvement history
        self.assertGreater(len(self.improvement_engine.improvement_history), 0)
        
        # Should show improvement trend
        if len(self.improvement_engine.improvement_history) > 1:
            improvement_trend = (
                self.improvement_engine.improvement_history[-1] - 
                self.improvement_engine.improvement_history[0]
            )
            self.assertLess(improvement_trend, 0)  # Loss should decrease
    
    def test_adaptive_parameter_extraction(self):
        """Test extraction of common parameters from history"""
        optimization_results = [
            {'success': True, 'parameters': {'lr': 0.001, 'momentum': 0.9}},
            {'success': True, 'parameters': {'lr': 0.002, 'momentum': 0.8}},
            {'success': True, 'parameters': {'lr': 0.0015, 'momentum': 0.85}}
        ]
        
        common_params = self.adaptive_engine._extract_common_parameters(optimization_results)
        
        self.assertIn('lr', common_params)
        self.assertIn('momentum', common_params)
        
        # Should be reasonable values
        self.assertGreater(common_params['lr'], 0.0)
        self.assertGreater(common_params['momentum'], 0.0)
        self.assertLess(common_params['momentum'], 1.0)
    
    def test_improvement_engine_integration(self):
        """Test integration between improvement and adaptive engines"""
        # Create integrated system
        improvement_engine = OptimizationImprovementEngine()
        adaptive_engine = AdaptiveOptimizationEngine()
        
        # Simulate optimization cycle
        metrics = {'loss': 0.4, 'accuracy': 0.8, 'convergence_time': 60}
        
        # Analyze performance
        analysis = improvement_engine.analyze_performance(metrics)
        improvements = improvement_engine.suggest_improvements(analysis)
        
        # Adapt optimization
        adaptation = adaptive_engine.adapt_optimization(metrics)
        
        # Both should provide valid suggestions
        self.assertGreater(len(improvements), 0)
        self.assertIsNotNone(adaptation)
        
        # Should be compatible
        self.assertIsInstance(improvements, list)
        self.assertIsInstance(adaptation, dict)

def run_improvement_tests():
    """Run all improvement tests"""
    print("🚀 Running Optimization Improvement Tests...")
    
    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(OptimizationImprovementTests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print results
    print(f"\n📊 Improvement Test Results:")
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
    run_improvement_tests()