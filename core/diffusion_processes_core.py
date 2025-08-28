#!/usr/bin/env python3
"""
Core Diffusion Processes Implementation

This module provides comprehensive implementations of forward and reverse diffusion processes,
including proper noise schedulers and sampling methods. It focuses on the mathematical
foundations and core algorithms that underlie diffusion models.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import math
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
import time
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class NoiseScheduleType(Enum):
    """Types of noise schedules for diffusion models."""
    LINEAR = "linear"
    COSINE = "cosine"
    COSINE_BETA = "cosine_beta"
    SIGMOID = "sigmoid"
    QUADRATIC = "quadratic"
    EXPONENTIAL = "exponential"
    SCALED_LINEAR = "scaled_linear"
    PIECEWISE_LINEAR = "piecewise_linear"

class SamplingMethod(Enum):
    """Types of sampling methods for reverse diffusion."""
    DDPM = "ddpm"
    DDIM = "ddim"
    DPM_SOLVER = "dpm_solver"
    DPM_SOLVER_PP = "dpm_solver_pp"
    EULER = "euler"
    HEUN = "heun"
    LMS = "lms"
    UNIPC = "unipc"
    EULER_ANCESTRAL = "euler_ancestral"
    HEUN_ANCESTRAL = "heun_ancestral"
    DPM_MULTISTEP = "dpm_multistep"
    DPM_SINGLESTEP = "dpm_singlestep"

class PredictionType(Enum):
    """Types of predictions that can be made by the model."""
    EPSILON = "epsilon"  # Predict noise
    X0 = "x0"           # Predict original image
    V = "v"             # Predict velocity (v-prediction)

@dataclass
class DiffusionConfig:
    """Configuration for diffusion processes."""
    num_timesteps: int = 1000
    beta_start: float = 0.0001
    beta_end: float = 0.02
    schedule_type: NoiseScheduleType = NoiseScheduleType.LINEAR
    sampling_method: SamplingMethod = SamplingMethod.DDPM
    prediction_type: PredictionType = PredictionType.EPSILON
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Advanced parameters
    clip_denoised: bool = True
    use_clipped_model_output: bool = False
    eta: float = 0.0  # For DDIM
    ddim_num_steps: int = 50
    ddim_discretize: str = "uniform"
    ddim_eta: float = 0.0
    
    # DPM-Solver parameters
    algorithm_type: str = "dpmsolver++"
    solver_type: str = "midpoint"
    lower_order_final: bool = True
    use_karras_sigmas: bool = False
    timestep_spacing: str = "linspace"
    steps_offset: int = 0

class NoiseScheduler:
    """
    Comprehensive noise scheduler for diffusion models.
    
    This class implements various noise schedules and provides methods for
    forward and reverse diffusion processes.
    """
    
    def __init__(self, config: DiffusionConfig):
        self.config = config
        self.device = torch.device(config.device)
        self.num_timesteps = config.num_timesteps
        
        # Initialize noise schedule
        self._setup_noise_schedule()
        self._precompute_values()
    
    def _setup_noise_schedule(self):
        """Setup the noise schedule based on configuration."""
        if self.config.schedule_type == NoiseScheduleType.LINEAR:
            self.betas = self._linear_beta_schedule()
        elif self.config.schedule_type == NoiseScheduleType.COSINE:
            self.betas = self._cosine_beta_schedule()
        elif self.config.schedule_type == NoiseScheduleType.COSINE_BETA:
            self.betas = self._cosine_beta_schedule_beta()
        elif self.config.schedule_type == NoiseScheduleType.SIGMOID:
            self.betas = self._sigmoid_beta_schedule()
        elif self.config.schedule_type == NoiseScheduleType.QUADRATIC:
            self.betas = self._quadratic_beta_schedule()
        elif self.config.schedule_type == NoiseScheduleType.EXPONENTIAL:
            self.betas = self._exponential_beta_schedule()
        elif self.config.schedule_type == NoiseScheduleType.SCALED_LINEAR:
            self.betas = self._scaled_linear_beta_schedule()
        elif self.config.schedule_type == NoiseScheduleType.PIECEWISE_LINEAR:
            self.betas = self._piecewise_linear_beta_schedule()
        else:
            raise ValueError(f"Unknown schedule type: {self.config.schedule_type}")
        
        self.betas = self.betas.to(self.device)
    
    def _linear_beta_schedule(self) -> torch.Tensor:
        """Linear beta schedule."""
        return torch.linspace(self.config.beta_start, self.config.beta_end, self.num_timesteps)
    
    def _cosine_beta_schedule(self) -> torch.Tensor:
        """Cosine beta schedule (Improved DDPM)."""
        steps = self.num_timesteps + 1
        x = torch.linspace(0, self.num_timesteps, steps)
        alphas_cumprod = torch.cos(((x / self.num_timesteps) + 0.008) / 1.008 * math.pi * 0.5) ** 2
        alphas_cumprod = alphas_cumprod / alphas_cumprod[0]
        betas = 1 - (alphas_cumprod[1:] / alphas_cumprod[:-1])
        return torch.clip(betas, 0, 0.999)
    
    def _cosine_beta_schedule_beta(self) -> torch.Tensor:
        """Cosine beta schedule with beta values."""
        return 0.5 * (1 + torch.cos(torch.linspace(0, math.pi, self.num_timesteps)))
    
    def _sigmoid_beta_schedule(self) -> torch.Tensor:
        """Sigmoid beta schedule."""
        betas = torch.sigmoid(torch.linspace(-6, 6, self.num_timesteps))
        return self.config.beta_start + (self.config.beta_end - self.config.beta_start) * betas
    
    def _quadratic_beta_schedule(self) -> torch.Tensor:
        """Quadratic beta schedule."""
        t = torch.linspace(0, 1, self.num_timesteps)
        return self.config.beta_start + (self.config.beta_end - self.config.beta_start) * t ** 2
    
    def _exponential_beta_schedule(self) -> torch.Tensor:
        """Exponential beta schedule."""
        t = torch.linspace(0, 1, self.num_timesteps)
        return self.config.beta_start * (self.config.beta_end / self.config.beta_start) ** t
    
    def _scaled_linear_beta_schedule(self) -> torch.Tensor:
        """Scaled linear beta schedule."""
        scale = 1000 / self.num_timesteps
        beta_start = self.config.beta_start * scale
        beta_end = self.config.beta_end * scale
        return torch.linspace(beta_start, beta_end, self.num_timesteps)
    
    def _piecewise_linear_beta_schedule(self) -> torch.Tensor:
        """Piecewise linear beta schedule."""
        # Define breakpoints
        breakpoints = [0, 0.25, 0.5, 0.75, 1.0]
        values = [self.config.beta_start, 0.005, 0.01, 0.015, self.config.beta_end]
        
        t = torch.linspace(0, 1, self.num_timesteps)
        betas = torch.zeros_like(t)
        
        for i in range(len(breakpoints) - 1):
            mask = (t >= breakpoints[i]) & (t <= breakpoints[i + 1])
            if mask.any():
                t_segment = (t[mask] - breakpoints[i]) / (breakpoints[i + 1] - breakpoints[i])
                betas[mask] = values[i] + (values[i + 1] - values[i]) * t_segment
        
        return betas
    
    def _precompute_values(self):
        """Precompute values for efficiency."""
        # Alphas
        self.alphas = 1.0 - self.betas
        self.alphas_cumprod = torch.cumprod(self.alphas, dim=0)
        self.alphas_cumprod_prev = F.pad(self.alphas_cumprod[:-1], (1, 0), value=1.0)
        
        # Square roots
        self.sqrt_alphas_cumprod = torch.sqrt(self.alphas_cumprod)
        self.sqrt_one_minus_alphas_cumprod = torch.sqrt(1.0 - self.alphas_cumprod)
        self.sqrt_recip_alphas_cumprod = torch.sqrt(1.0 / self.alphas_cumprod)
        self.sqrt_recipm1_alphas_cumprod = torch.sqrt(1.0 / self.alphas_cumprod - 1)
        
        # Variances
        self.posterior_variance = (
            self.betas * (1.0 - self.alphas_cumprod_prev) / (1.0 - self.alphas_cumprod)
        )
        self.posterior_log_variance_clipped = torch.log(
            torch.cat([self.posterior_variance[1:2], self.posterior_variance[1:]])
        )
        self.posterior_mean_coef1 = (
            self.betas * torch.sqrt(self.alphas_cumprod_prev) / (1.0 - self.alphas_cumprod)
        )
        self.posterior_mean_coef2 = (
            (1.0 - self.alphas_cumprod_prev) * torch.sqrt(self.alphas) / (1.0 - self.alphas_cumprod)
        )

class ForwardProcess:
    """
    Forward diffusion process implementation.
    
    This class implements the forward process q(x_t | x_0) that gradually
    adds noise to the original data according to the noise schedule.
    """
    
    def __init__(self, scheduler: NoiseScheduler):
        self.scheduler = scheduler
    
    def q_sample(self, x_start: torch.Tensor, t: torch.Tensor, noise: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Forward diffusion process: q(x_t | x_0).
        
        Args:
            x_start: Original image [B, C, H, W]
            t: Timesteps [B]
            noise: Optional noise tensor, if None will be sampled
            
        Returns:
            Noisy image at timestep t
        """
        if noise is None:
            noise = torch.randn_like(x_start)
        
        # Get schedule values for timestep t
        sqrt_alphas_cumprod_t = self.scheduler.sqrt_alphas_cumprod[t].view(-1, 1, 1, 1)
        sqrt_one_minus_alphas_cumprod_t = self.scheduler.sqrt_one_minus_alphas_cumprod[t].view(-1, 1, 1, 1)
        
        # Forward diffusion equation: x_t = sqrt(ᾱ_t) * x_0 + sqrt(1 - ᾱ_t) * ε
        return sqrt_alphas_cumprod_t * x_start + sqrt_one_minus_alphas_cumprod_t * noise
    
    def q_posterior_mean_variance(self, x_start: torch.Tensor, x_t: torch.Tensor, t: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Compute q(x_{t-1} | x_t, x_0).
        
        Args:
            x_start: Original image
            x_t: Noisy image at timestep t
            t: Timesteps
            
        Returns:
            Tuple of (posterior_mean, posterior_variance, posterior_log_variance)
        """
        posterior_mean = (
            self.scheduler.posterior_mean_coef1[t].view(-1, 1, 1, 1) * x_start +
            self.scheduler.posterior_mean_coef2[t].view(-1, 1, 1, 1) * x_t
        )
        posterior_variance = self.scheduler.posterior_variance[t].view(-1, 1, 1, 1)
        posterior_log_variance = self.scheduler.posterior_log_variance_clipped[t].view(-1, 1, 1, 1)
        
        return posterior_mean, posterior_variance, posterior_log_variance
    
    def q_mean_variance(self, x_start: torch.Tensor, t: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Compute q(x_t | x_0) mean and variance.
        
        Args:
            x_start: Original image
            t: Timesteps
            
        Returns:
            Tuple of (mean, variance)
        """
        mean = self.scheduler.sqrt_alphas_cumprod[t].view(-1, 1, 1, 1) * x_start
        variance = 1.0 - self.scheduler.alphas_cumprod[t].view(-1, 1, 1, 1)
        
        return mean, variance

class ReverseProcess:
    """
    Reverse diffusion process implementation.
    
    This class implements the reverse process p(x_{t-1} | x_t) that gradually
    denoises the data using the learned model.
    """
    
    def __init__(self, scheduler: NoiseScheduler, model: nn.Module, config: DiffusionConfig):
        self.scheduler = scheduler
        self.model = model
        self.config = config
        self.forward_process = ForwardProcess(scheduler)
    
    def p_mean_variance(self, x: torch.Tensor, t: torch.Tensor, condition: Optional[torch.Tensor] = None) -> Dict[str, torch.Tensor]:
        """
        Compute p(x_{t-1} | x_t) mean and variance.
        
        Args:
            x: Noisy image at timestep t
            t: Timesteps
            condition: Optional conditioning information
            
        Returns:
            Dictionary with mean, variance, and log_variance
        """
        # Get model prediction
        model_output = self.model(x, t, condition)
        
        # Extract prediction based on prediction type
        if self.config.prediction_type == PredictionType.EPSILON:
            pred_epsilon = model_output
            pred_x_start = self._predict_xstart_from_epsilon(x, t, pred_epsilon)
        elif self.config.prediction_type == PredictionType.X0:
            pred_x_start = model_output
            pred_epsilon = self._predict_epsilon_from_xstart(x, t, pred_x_start)
        elif self.config.prediction_type == PredictionType.V:
            pred_v = model_output
            pred_epsilon = self._predict_epsilon_from_v(x, t, pred_v)
            pred_x_start = self._predict_xstart_from_epsilon(x, t, pred_epsilon)
        else:
            raise ValueError(f"Unknown prediction type: {self.config.prediction_type}")
        
        # Compute posterior mean and variance
        posterior_mean, posterior_variance, posterior_log_variance = self.forward_process.q_posterior_mean_variance(
            pred_x_start, x, t
        )
        
        return {
            "mean": posterior_mean,
            "variance": posterior_variance,
            "log_variance": posterior_log_variance,
            "pred_x_start": pred_x_start,
            "pred_epsilon": pred_epsilon
        }
    
    def p_sample(self, x: torch.Tensor, t: torch.Tensor, condition: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Sample from p(x_{t-1} | x_t) using DDPM.
        
        Args:
            x: Noisy image at timestep t
            t: Timesteps
            condition: Optional conditioning information
            
        Returns:
            Denoised image at timestep t-1
        """
        p_mean_var = self.p_mean_variance(x, t, condition)
        
        # Sample from posterior
        noise = torch.randn_like(x) if t[0] > 0 else torch.zeros_like(x)
        return p_mean_var["mean"] + torch.sqrt(p_mean_var["variance"]) * noise
    
    def p_sample_ddim(self, x: torch.Tensor, t: torch.Tensor, t_prev: torch.Tensor, 
                     condition: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Sample from p(x_{t-1} | x_t) using DDIM.
        
        Args:
            x: Noisy image at timestep t
            t: Current timesteps
            t_prev: Previous timesteps
            condition: Optional conditioning information
            
        Returns:
            Denoised image at timestep t-1
        """
        p_mean_var = self.p_mean_variance(x, t, condition)
        
        # DDIM equation
        alpha_cumprod_t = self.scheduler.alphas_cumprod[t].view(-1, 1, 1, 1)
        alpha_cumprod_prev = self.scheduler.alphas_cumprod_prev[t_prev].view(-1, 1, 1, 1)
        
        sigma_t = self.config.ddim_eta * torch.sqrt(
            (1 - alpha_cumprod_prev) / (1 - alpha_cumprod_t) * (1 - alpha_cumprod_t / alpha_cumprod_prev)
        )
        
        # DDIM sampling equation
        pred_epsilon = p_mean_var["pred_epsilon"]
        pred_x_start = p_mean_var["pred_x_start"]
        
        x_prev = (
            torch.sqrt(alpha_cumprod_prev) * pred_x_start +
            torch.sqrt(1 - alpha_cumprod_prev - sigma_t ** 2) * pred_epsilon +
            sigma_t * torch.randn_like(x)
        )
        
        return x_prev
    
    def p_sample_loop(self, shape: Tuple[int, ...], condition: Optional[torch.Tensor] = None,
                     timesteps: Optional[List[int]] = None) -> torch.Tensor:
        """
        Complete reverse process sampling loop.
        
        Args:
            shape: Shape of the image to generate
            condition: Optional conditioning information
            timesteps: Optional custom timesteps
            
        Returns:
            Generated image
        """
        device = next(self.model.parameters()).device
        batch_size = shape[0]
        
        # Initialize x_T
        x = torch.randn(shape, device=device)
        
        # Set timesteps
        if timesteps is None:
            timesteps = list(range(self.scheduler.num_timesteps - 1, -1, -1))
        
        # Reverse process
        for i, t in enumerate(timesteps):
            t_tensor = torch.full((batch_size,), t, device=device, dtype=torch.long)
            
            if self.config.sampling_method == SamplingMethod.DDIM:
                t_prev = timesteps[i + 1] if i + 1 < len(timesteps) else 0
                t_prev_tensor = torch.full((batch_size,), t_prev, device=device, dtype=torch.long)
                x = self.p_sample_ddim(x, t_tensor, t_prev_tensor, condition)
            else:
                x = self.p_sample(x, t_tensor, condition)
        
        return x
    
    def _predict_xstart_from_epsilon(self, x: torch.Tensor, t: torch.Tensor, epsilon: torch.Tensor) -> torch.Tensor:
        """Predict x_0 from predicted epsilon."""
        return (
            x - self.scheduler.sqrt_one_minus_alphas_cumprod[t].view(-1, 1, 1, 1) * epsilon
        ) / self.scheduler.sqrt_alphas_cumprod[t].view(-1, 1, 1, 1)
    
    def _predict_epsilon_from_xstart(self, x: torch.Tensor, t: torch.Tensor, x_start: torch.Tensor) -> torch.Tensor:
        """Predict epsilon from predicted x_0."""
        return (
            x - self.scheduler.sqrt_alphas_cumprod[t].view(-1, 1, 1, 1) * x_start
        ) / self.scheduler.sqrt_one_minus_alphas_cumprod[t].view(-1, 1, 1, 1)
    
    def _predict_epsilon_from_v(self, x: torch.Tensor, t: torch.Tensor, v: torch.Tensor) -> torch.Tensor:
        """Predict epsilon from predicted v."""
        alpha_cumprod_t = self.scheduler.alphas_cumprod[t].view(-1, 1, 1, 1)
        return torch.sqrt(alpha_cumprod_t) * v + torch.sqrt(1 - alpha_cumprod_t) * x

class DiffusionProcesses:
    """
    Main class for diffusion processes.
    
    This class provides a unified interface for forward and reverse diffusion
    processes with various noise schedulers and sampling methods.
    """
    
    def __init__(self, config: DiffusionConfig, model: Optional[nn.Module] = None):
        self.config = config
        self.scheduler = NoiseScheduler(config)
        self.forward_process = ForwardProcess(self.scheduler)
        self.reverse_process = None
        if model is not None:
            self.set_model(model)
    
    def set_model(self, model: nn.Module):
        """Set the denoising model."""
        self.reverse_process = ReverseProcess(self.scheduler, model, self.config)
    
    def forward_diffusion(self, x_start: torch.Tensor, t: torch.Tensor, 
                         noise: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Forward diffusion process.
        
        Args:
            x_start: Original image
            t: Timesteps
            noise: Optional noise
            
        Returns:
            Noisy image at timestep t
        """
        return self.forward_process.q_sample(x_start, t, noise)
    
    def reverse_diffusion(self, x: torch.Tensor, t: torch.Tensor,
                         condition: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Reverse diffusion process.
        
        Args:
            x: Noisy image
            t: Timesteps
            condition: Optional conditioning
            
        Returns:
            Denoised image
        """
        if self.reverse_process is None:
            raise ValueError("Model not set. Call set_model() first.")
        
        return self.reverse_process.p_sample(x, t, condition)
    
    def sample(self, shape: Tuple[int, ...], condition: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Generate samples using the reverse process.
        
        Args:
            shape: Shape of the image to generate
            condition: Optional conditioning information
            
        Returns:
            Generated image
        """
        if self.reverse_process is None:
            raise ValueError("Model not set. Call set_model() first.")
        
        return self.reverse_process.p_sample_loop(shape, condition)
    
    def get_noise_schedule_info(self) -> Dict[str, Any]:
        """Get information about the noise schedule."""
        return {
            "num_timesteps": self.scheduler.num_timesteps,
            "beta_start": self.config.beta_start,
            "beta_end": self.config.beta_end,
            "schedule_type": self.config.schedule_type.value,
            "sampling_method": self.config.sampling_method.value,
            "prediction_type": self.config.prediction_type.value,
            "betas": self.scheduler.betas.cpu().numpy().tolist(),
            "alphas": self.scheduler.alphas.cpu().numpy().tolist(),
            "alphas_cumprod": self.scheduler.alphas_cumprod.cpu().numpy().tolist()
        }

# Example usage and testing
if __name__ == "__main__":
    # Test configuration
    config = DiffusionConfig(
        num_timesteps=1000,
        beta_start=0.0001,
        beta_end=0.02,
        schedule_type=NoiseScheduleType.COSINE,
        sampling_method=SamplingMethod.DDPM,
        prediction_type=PredictionType.EPSILON
    )
    
    # Create diffusion processes
    diffusion = DiffusionProcesses(config)
    
    # Print noise schedule info
    info = diffusion.get_noise_schedule_info()
    print("Noise Schedule Info:")
    for key, value in info.items():
        if key not in ["betas", "alphas", "alphas_cumprod"]:
            print(f"  {key}: {value}")
    
    print("✅ Diffusion processes core implementation completed!")
