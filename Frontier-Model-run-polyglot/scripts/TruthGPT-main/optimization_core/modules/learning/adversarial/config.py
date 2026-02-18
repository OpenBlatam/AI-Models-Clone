"""
Adversarial Learning Configuration
==================================

Configuration for attacks, GAN training, and defense mechanisms.
"""
from dataclasses import dataclass, field
from .enums import AdversarialAttackType, GANType, DefenseStrategy

@dataclass
class AdversarialConfig:
    """Configuration for adversarial learning system"""
    # Strategy selection
    attack_type: AdversarialAttackType = AdversarialAttackType.FGSM
    gan_type: GANType = GANType.VANILLA_GAN
    defense_strategy: DefenseStrategy = DefenseStrategy.ADVERSARIAL_TRAINING
    
    # Attack parameters
    attack_epsilon: float = 0.1
    attack_alpha: float = 0.01
    attack_iterations: int = 10
    attack_norm: str = "inf"
    attack_targeted: bool = False
    
    # GAN parameters
    generator_lr: float = 0.0002
    discriminator_lr: float = 0.0002
    gan_beta1: float = 0.5
    gan_beta2: float = 0.999
    gan_latent_dim: int = 100
    
    # Defense parameters
    defense_epsilon: float = 0.1
    defense_alpha: float = 0.01
    defense_iterations: int = 10
    defense_norm: str = "inf"
    
    # Global training settings
    batch_size: int = 64
    num_epochs: int = 100
    learning_rate: float = 0.001
    
    # Features toggle
    enable_robustness_analysis: bool = True
    enable_attack_generation: bool = True
    enable_defense_training: bool = True
    enable_adversarial_training: bool = True
    
    def __post_init__(self):
        """Validate adversarial configuration"""
        if self.attack_epsilon <= 0:
            raise ValueError("Attack epsilon must be positive")
        if self.attack_alpha <= 0:
            raise ValueError("Attack alpha must be positive")
        if self.attack_iterations <= 0:
            raise ValueError("Attack iterations must be positive")
        if self.generator_lr <= 0:
            raise ValueError("Generator learning rate must be positive")
        if self.batch_size <= 0:
            raise ValueError("Batch size must be positive")
