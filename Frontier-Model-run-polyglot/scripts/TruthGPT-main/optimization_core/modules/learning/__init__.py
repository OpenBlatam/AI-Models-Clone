"""
Learning Algorithms Module
===========================

Collection of advanced learning algorithms for optimization core.
Includes evolutionary computing, causal inference, and more.
"""

from __future__ import annotations
from optimization_core.utils.dependency_manager import resolve_lazy_import

_LAZY_IMPORTS = {
    # Evolutionary Computing
    'EvolutionaryOptimizer': '.evolutionary',
    'EvolutionaryConfig': '.evolutionary',
    'EvolutionaryAlgorithm': '.evolutionary',
    'create_evolutionary_config': '.evolutionary',
    'create_individual': '.evolutionary',
    'create_population': '.evolutionary',
    'create_evolutionary_optimizer': '.evolutionary',
    'evolutionary_computing': '.evolutionary',
    
    # Causal Inference
    'CausalInferenceEngine': '.causal',
    'CausalConfig': '.causal',
    'CausalInferenceSystem': '.causal',
    'CausalMethod': '.causal',
    'CausalEffectType': '.causal',
    'causal_inference': '.causal',
    
    # Active Learning
    'ActiveLearningStrategy': '.active',
    'ActiveLearningConfig': '.active',
    'ActiveLearningSampler': '.active',
    'ActiveLearningSystem': '.active',
    'active_learning': '.active',
    
    # Adaptive Learning
    'AdaptiveLearningSystem': '.adaptive_learning',
    'AdaptiveLearningConfig': '.adaptive_learning',
    'adaptive_learning': '.adaptive_learning',
    
    # Adversarial Learning
    'AdversarialTrainer': '.adversarial_learning',
    'AdversarialConfig': '.adversarial_learning',
    'AdversarialAttackType': '.adversarial_learning',
    'GANType': '.adversarial_learning',
    'DefenseStrategy': '.adversarial_learning',
    'create_adversarial_learning_system': '.adversarial_learning',
    'create_adversarial_config': '.adversarial_learning',
    'create_adversarial_attacker': '.adversarial_learning',
    'create_gan_trainer': '.adversarial_learning',
    'create_adversarial_defense': '.adversarial_learning',
    'create_robustness_analyzer': '.adversarial_learning',
    'adversarial_learning': '.adversarial_learning',
    
    # Bayesian Optimization
    'BayesianOptimizer': '.bayesian_optimization',
    'BayesianConfig': '.bayesian_optimization',
    'bayesian_optimization': '.bayesian_optimization',
    
    # Continual Learning
    'ContinualLearner': '.continual_learning',
    'ContinualConfig': '.continual_learning',
    'continual_learning': '.continual_learning',
    
    # Ensemble Learning
    'EnsembleManager': '.ensemble_learning',
    'EnsembleConfig': '.ensemble_learning',
    'ensemble_learning': '.ensemble_learning',
    
    # Federated Learning
    'FederatedServer': '.federated_learning',
    'FederatedClient': '.federated_learning',
    'FederatedConfig': '.federated_learning',
    'federated_learning': '.federated_learning',
    
    # Hyperparameter Optimization
    'HyperparameterOptimizer': '.hyperparameter_optimization',
    'HPOConfig': '.hyperparameter_optimization',
    'hyperparameter_optimization': '.hyperparameter_optimization',
    
    # Meta Learning
    'MetaLearner': '.meta',
    'MetaConfig': '.meta',
    'meta_learning': '.meta',
    
    # Multitask Learning
    'MultitaskModel': '.multitask_learning',
    'MultitaskConfig': '.multitask_learning',
    'multitask_learning': '.multitask_learning',
    
    # NAS
    'NeuralArchitectureSearch': '.nas',
    'NASConfig': '.nas',
    'nas': '.nas',
    
    # Reinforcement Learning
    'RLAgent': '.reinforcement',
    'RLConfig': '.reinforcement',
    'RLBuffer': '.reinforcement',
    'RLSystem': '.reinforcement',
    'reinforcement_learning': '.reinforcement',
    
    # Self-Supervised Learning
    'SelfSupervisedTrainer': '.self_supervised_learning',
    'SelfSupervisedConfig': '.self_supervised_learning',
    'self_supervised_learning': '.self_supervised_learning',
    
    # Transfer Learning
    'TransferLearningManager': '.transfer_learning',
    'TransferLearningConfig': '.transfer_learning',
    'transfer_learning': '.transfer_learning',
}

def __getattr__(name: str):
    """Lazy import system for learning module."""
    return resolve_lazy_import(name, __package__ or 'learning', _LAZY_IMPORTS)

__all__ = list(_LAZY_IMPORTS.keys())
