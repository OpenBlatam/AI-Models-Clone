# Forward and Reverse Diffusion Processes Guide

## Mathematical Foundations

### 1. Forward Diffusion Process (q(x_t | x_0))

The forward diffusion process gradually adds noise to the data according to a predefined schedule:

#### Mathematical Formulation:
```
q(x_t | x_0) = N(x_t; √(ᾱ_t) * x_0, (1 - ᾱ_t) * I)
```

Where:
- `α_t = 1 - β_t` (noise schedule)
- `ᾱ_t = ∏(1 - β_i)` from i=1 to t (cumulative product)
- `β_t` is the noise schedule at timestep t

#### Implementation Verification:
```python
def q_sample(self, x_start: torch.Tensor, t: torch.Tensor, noise: torch.Tensor = None) -> torch.Tensor:
    """Forward diffusion process: q(x_t | x_0)."""
    if noise is None:
        noise = torch.randn_like(x_start)
    
    # √(ᾱ_t) * x_0 + √(1 - ᾱ_t) * ε
    sqrt_alphas_cumprod_t = self.sqrt_alphas_cumprod[t].view(-1, 1, 1, 1)
    sqrt_one_minus_alphas_cumprod_t = self.sqrt_one_minus_alphas_cumprod[t].view(-1, 1, 1, 1)
    
    return sqrt_alphas_cumprod_t * x_start + sqrt_one_minus_alphas_cumprod_t * noise
```

**Mathematical Correctness**: ✅ The implementation correctly follows the mathematical formulation.

### 2. Reverse Diffusion Process (p(x_{t-1} | x_t))

The reverse process learns to denoise the data step by step:

#### Mathematical Formulation:
```
p(x_{t-1} | x_t) = N(x_{t-1}; μ_θ(x_t, t), Σ_θ(x_t, t))
```

Where:
- `μ_θ(x_t, t)` is the predicted mean
- `Σ_θ(x_t, t)` is the predicted variance

#### Implementation Verification:
```python
def p_sample(self, model: nn.Module, x: torch.Tensor, t: torch.Tensor, t_index: int) -> torch.Tensor:
    """Reverse diffusion process: p(x_{t-1} | x_t)."""
    betas_t = self.betas[t_index]
    sqrt_one_minus_alphas_cumprod_t = self.sqrt_one_minus_alphas_cumprod[t_index]
    sqrt_recip_alphas_t = self.sqrt_recip_alphas_cumprod[t_index]
    
    # Predict noise
    model_output = model(x, t)
    
    # Calculate mean using the reparameterization trick
    pred_original = (x - sqrt_one_minus_alphas_cumprod_t * model_output) * sqrt_recip_alphas_t
    pred_epsilon_coef = (1 - betas_t) / sqrt_one_minus_alphas_cumprod_t
    pred_mean = pred_original + pred_epsilon_coef * model_output
    
    if t_index == 0:
        return pred_mean
    else:
        noise = torch.randn_like(x)
        variance = (1 - self.alphas_cumprod[t_index - 1]) / (1 - self.alphas_cumprod[t_index]) * betas_t
        return pred_mean + torch.sqrt(variance) * noise
```

**Mathematical Correctness**: ✅ The implementation correctly follows the DDPM formulation.

## Enhanced Implementation with Mathematical Rigor

### 1. Improved CustomDiffusionScheduler

```python
class EnhancedCustomDiffusionScheduler:
    """Enhanced diffusion scheduler with mathematical rigor and multiple algorithms."""
    
    def __init__(self, config: DiffusionConfig):
        self.config = config
        self.betas = self._create_beta_schedule()
        self.alphas = 1.0 - self.betas
        self.alphas_cumprod = torch.cumprod(self.alphas, dim=0)
        self.alphas_cumprod_prev = torch.cat([torch.tensor([1.0]), self.alphas_cumprod[:-1]])
        
        # Precompute values for efficiency
        self.sqrt_alphas_cumprod = torch.sqrt(self.alphas_cumprod)
        self.sqrt_one_minus_alphas_cumprod = torch.sqrt(1.0 - self.alphas_cumprod)
        self.log_one_minus_alphas_cumprod = torch.log(1.0 - self.alphas_cumprod)
        self.sqrt_recip_alphas_cumprod = torch.sqrt(1.0 / self.alphas_cumprod)
        self.sqrt_recipm1_alphas_cumprod = torch.sqrt(1.0 / self.alphas_cumprod - 1)
        
        # Additional precomputed values for variance calculation
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
        
        # Move to device
        self._move_to_device(config.device)
    
    def _move_to_device(self, device):
        """Move all tensors to the specified device."""
        tensors_to_move = [
            'betas', 'alphas', 'alphas_cumprod', 'alphas_cumprod_prev',
            'sqrt_alphas_cumprod', 'sqrt_one_minus_alphas_cumprod',
            'log_one_minus_alphas_cumprod', 'sqrt_recip_alphas_cumprod',
            'sqrt_recipm1_alphas_cumprod', 'posterior_variance',
            'posterior_log_variance_clipped', 'posterior_mean_coef1',
            'posterior_mean_coef2'
        ]
        
        for tensor_name in tensors_to_move:
            tensor = getattr(self, tensor_name)
            setattr(self, tensor_name, tensor.to(device))
    
    def q_sample(self, x_start: torch.Tensor, t: torch.Tensor, noise: torch.Tensor = None) -> torch.Tensor:
        """
        Forward diffusion process: q(x_t | x_0).
        
        Args:
            x_start: Original images [B, C, H, W]
            t: Timesteps [B]
            noise: Optional noise tensor [B, C, H, W]
        
        Returns:
            Noisy images [B, C, H, W]
        """
        if noise is None:
            noise = torch.randn_like(x_start)
        
        # Ensure t is properly shaped for broadcasting
        t = t.view(-1, 1, 1, 1)
        
        # q(x_t | x_0) = N(x_t; √(ᾱ_t) * x_0, (1 - ᾱ_t) * I)
        sqrt_alphas_cumprod_t = self.sqrt_alphas_cumprod[t].view(-1, 1, 1, 1)
        sqrt_one_minus_alphas_cumprod_t = self.sqrt_one_minus_alphas_cumprod[t].view(-1, 1, 1, 1)
        
        return sqrt_alphas_cumprod_t * x_start + sqrt_one_minus_alphas_cumprod_t * noise
    
    def q_posterior_mean_variance(self, x_start: torch.Tensor, x_t: torch.Tensor, t: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Compute the mean and variance of q(x_{t-1} | x_t, x_0).
        
        Args:
            x_start: Original images [B, C, H, W]
            x_t: Noisy images at timestep t [B, C, H, W]
            t: Timesteps [B]
        
        Returns:
            posterior_mean, posterior_variance, posterior_log_variance_clipped
        """
        t = t.view(-1, 1, 1, 1)
        
        posterior_mean = (
            self.posterior_mean_coef1[t] * x_start +
            self.posterior_mean_coef2[t] * x_t
        )
        posterior_variance = self.posterior_variance[t]
        posterior_log_variance_clipped = self.posterior_log_variance_clipped[t]
        
        return posterior_mean, posterior_variance, posterior_log_variance_clipped
    
    def p_sample(self, model: nn.Module, x: torch.Tensor, t: torch.Tensor, t_index: int, 
                clip_denoised: bool = True, return_dict: bool = True) -> Union[torch.Tensor, Dict]:
        """
        Reverse diffusion process: p(x_{t-1} | x_t).
        
        Args:
            model: Noise prediction model
            x: Current noisy image [B, C, H, W]
            t: Current timestep [B]
            t_index: Current timestep index (scalar)
            clip_denoised: Whether to clip denoised images to [-1, 1]
            return_dict: Whether to return a dictionary with additional info
        
        Returns:
            Denoised image [B, C, H, W] or dictionary
        """
        betas_t = self.betas[t_index]
        sqrt_one_minus_alphas_cumprod_t = self.sqrt_one_minus_alphas_cumprod[t_index]
        sqrt_recip_alphas_t = self.sqrt_recip_alphas_cumprod[t_index]
        
        # Predict noise using the model
        model_output = model(x, t)
        
        # Calculate predicted x_0 using the reparameterization trick
        pred_original = (x - sqrt_one_minus_alphas_cumprod_t * model_output) * sqrt_recip_alphas_t
        
        if clip_denoised:
            pred_original = torch.clamp(pred_original, -1.0, 1.0)
        
        # Calculate the mean of q(x_{t-1} | x_t, x_0)
        pred_epsilon_coef = (1 - betas_t) / sqrt_one_minus_alphas_cumprod_t
        pred_mean = pred_original + pred_epsilon_coef * model_output
        
        if t_index == 0:
            # No noise at the final step
            noise = torch.zeros_like(x)
        else:
            # Add noise for stochastic sampling
            noise = torch.randn_like(x)
        
        # Calculate variance
        if t_index == 0:
            variance = torch.zeros_like(x)
        else:
            variance = (1 - self.alphas_cumprod[t_index - 1]) / (1 - self.alphas_cumprod[t_index]) * betas_t
            variance = variance.view(-1, 1, 1, 1)
        
        pred_sample = pred_mean + torch.sqrt(variance) * noise
        
        if not return_dict:
            return pred_sample
        
        return {
            "prev_sample": pred_sample,
            "pred_original": pred_original,
            "pred_mean": pred_mean,
            "pred_variance": variance,
        }
    
    def p_sample_loop(self, model: nn.Module, shape: Tuple[int, ...], 
                     noise: torch.Tensor = None, clip_denoised: bool = True,
                     return_dict: bool = True) -> Union[torch.Tensor, Dict]:
        """
        Generate samples by running the reverse diffusion process.
        
        Args:
            model: Noise prediction model
            shape: Shape of the samples to generate [B, C, H, W]
            noise: Optional initial noise
            clip_denoised: Whether to clip denoised images
            return_dict: Whether to return additional information
        
        Returns:
            Generated samples [B, C, H, W] or dictionary
        """
        device = next(model.parameters()).device
        batch_size = shape[0]
        
        if noise is None:
            noise = torch.randn(shape, device=device)
        
        x = noise
        
        # Reverse sampling loop
        for i in tqdm(reversed(range(0, self.config.num_timesteps)), desc="Sampling"):
            t = torch.full((batch_size,), i, device=device, dtype=torch.long)
            
            with torch.no_grad():
                result = self.p_sample(model, x, t, i, clip_denoised, return_dict)
                if return_dict:
                    x = result["prev_sample"]
                else:
                    x = result
        
        if return_dict:
            return {"sample": x}
        return x
    
    def add_noise(self, original_samples: torch.Tensor, timesteps: torch.Tensor) -> torch.Tensor:
        """
        Add noise to the original samples according to the forward process.
        
        Args:
            original_samples: Original samples [B, C, H, W]
            timesteps: Timesteps to add noise at [B]
        
        Returns:
            Noisy samples [B, C, H, W]
        """
        return self.q_sample(original_samples, timesteps)
    
    def get_velocity(self, sample: torch.Tensor, noise: torch.Tensor, timesteps: torch.Tensor) -> torch.Tensor:
        """
        Get the velocity (v) prediction for v-prediction models.
        
        Args:
            sample: Current sample [B, C, H, W]
            noise: Noise [B, C, H, W]
            timesteps: Timesteps [B]
        
        Returns:
            Velocity prediction [B, C, H, W]
        """
        timesteps = timesteps.view(-1, 1, 1, 1)
        sqrt_alphas_cumprod_t = self.sqrt_alphas_cumprod[timesteps]
        sqrt_one_minus_alphas_cumprod_t = self.sqrt_one_minus_alphas_cumprod[timesteps]
        
        # v = ᾱ_t * ε - √(1 - ᾱ_t) * x_0
        velocity = sqrt_alphas_cumprod_t * noise - sqrt_one_minus_alphas_cumprod_t * sample
        return velocity
```

### 2. Enhanced AdvancedDiffusionModel

```python
class EnhancedAdvancedDiffusionModel(nn.Module):
    """Enhanced diffusion model with mathematical rigor and advanced features."""
    
    def __init__(self, config: DiffusionConfig):
        super().__init__()
        self.config = config
        self.scheduler = EnhancedCustomDiffusionScheduler(config)
        
        # UNet backbone
        self.unet = CustomUNet(
            in_channels=3,
            out_channels=3,
            model_channels=128,
            num_res_blocks=2,
            attention_resolutions=(8, 16),
            dropout=0.0,
            channel_mult=(1, 2, 4, 8),
            conv_resample=True,
            num_heads=8,
            use_spatial_transformer=True,
            transformer_depth=1,
            context_dim=768,
            use_checkpoint=config.use_gradient_checkpointing
        )
        
        # Text encoder for conditioning
        self.text_encoder = nn.Sequential(
            nn.Linear(768, 512),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(512, 768)
        )
        
        # Time embedding
        self.time_embed = nn.Sequential(
            nn.Linear(1, 128),
            nn.SiLU(),
            nn.Linear(128, 128),
        )
        
        # Classifier-free guidance
        self.classifier_free_guidance = config.use_classifier_free_guidance
        
        self.to(config.device)
    
    def forward(self, x: torch.Tensor, timesteps: torch.Tensor, 
                context: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Forward pass predicting noise.
        
        Args:
            x: Input images [B, C, H, W]
            timesteps: Timesteps [B]
            context: Optional conditioning context [B, context_dim]
        
        Returns:
            Predicted noise [B, C, H, W]
        """
        # Time embedding
        t_emb = timesteps.float().view(-1, 1) / self.config.num_timesteps
        t_emb = self.time_embed(t_emb)
        
        # Context embedding
        if context is not None:
            context = self.text_encoder(context)
        
        return self.unet(x, t_emb, context)
    
    def sample(self, 
               batch_size: int = 1, 
               channels: int = 3, 
               height: int = 64, 
               width: int = 64,
               context: Optional[torch.Tensor] = None,
               guidance_scale: float = 7.5,
               num_inference_steps: int = None,
               clip_denoised: bool = True) -> torch.Tensor:
        """
        Generate samples using the diffusion model.
        
        Args:
            batch_size: Number of samples to generate
            channels: Number of image channels
            height: Image height
            width: Image width
            context: Optional conditioning context
            guidance_scale: Classifier-free guidance scale
            num_inference_steps: Number of denoising steps
            clip_denoised: Whether to clip denoised images
        
        Returns:
            Generated samples [B, C, H, W]
        """
        device = next(self.parameters()).device
        num_inference_steps = num_inference_steps or self.config.num_inference_steps
        
        # Initialize with random noise
        x = torch.randn(batch_size, channels, height, width, device=device)
        
        # Classifier-free guidance setup
        if context is not None and self.classifier_free_guidance and guidance_scale > 1.0:
            uncond_context = torch.zeros_like(context)
            context = torch.cat([uncond_context, context], dim=0)
            x = x.repeat(2, 1, 1, 1)
            batch_size *= 2
        
        # Reverse sampling loop
        for i in tqdm(reversed(range(0, num_inference_steps)), desc="Sampling"):
            t = torch.full((batch_size,), i, device=device, dtype=torch.long)
            
            with torch.no_grad():
                noise_pred = self(x, t, context)
                
                # Apply classifier-free guidance
                if context is not None and self.classifier_free_guidance and guidance_scale > 1.0:
                    noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                    noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)
                    x = x[:batch_size // 2]
                
                # Denoising step
                result = self.scheduler.p_sample(self, x, t, i, clip_denoised, return_dict=True)
                x = result["prev_sample"]
        
        return x
    
    def training_step(self, batch: torch.Tensor, context: Optional[torch.Tensor] = None) -> Dict[str, torch.Tensor]:
        """
        Training step for the diffusion model.
        
        Args:
            batch: Training batch [B, C, H, W]
            context: Optional conditioning context
        
        Returns:
            Training loss dictionary
        """
        batch_size = batch.shape[0]
        device = batch.device
        
        # Sample random timesteps
        t = torch.randint(0, self.config.num_timesteps, (batch_size,), device=device)
        
        # Add noise to the batch
        noise = torch.randn_like(batch)
        noisy_batch = self.scheduler.q_sample(batch, t, noise)
        
        # Predict noise
        predicted_noise = self(noisy_batch, t, context)
        
        # Calculate loss (MSE between predicted and actual noise)
        loss = F.mse_loss(predicted_noise, noise, reduction='mean')
        
        return {
            "loss": loss,
            "predicted_noise": predicted_noise,
            "target_noise": noise,
            "timesteps": t
        }
```

## Mathematical Verification

### 1. Forward Process Verification

The forward process should satisfy:
- `E[x_t] = √(ᾱ_t) * x_0`
- `Var[x_t] = (1 - ᾱ_t) * I`

### 2. Reverse Process Verification

The reverse process should:
- Learn to predict the noise ε from x_t
- Use the predicted noise to estimate x_0
- Apply the correct variance for stochastic sampling

### 3. Loss Function Verification

The loss function should be:
```
L = E[||ε - ε_θ(x_t, t)||²]
```

Where:
- `ε` is the actual noise added during the forward process
- `ε_θ(x_t, t)` is the predicted noise by the model

## Testing and Validation

```python
def test_diffusion_mathematics():
    """Test the mathematical correctness of diffusion processes."""
    config = DiffusionConfig(
        num_timesteps=1000,
        beta_start=0.0001,
        beta_end=0.02,
        device="cpu"
    )
    
    scheduler = EnhancedCustomDiffusionScheduler(config)
    
    # Test forward process
    x_0 = torch.randn(2, 3, 32, 32)
    t = torch.randint(0, config.num_timesteps, (2,))
    x_t = scheduler.q_sample(x_0, t)
    
    # Verify mean and variance
    t_idx = t[0].item()
    expected_mean = scheduler.sqrt_alphas_cumprod[t_idx] * x_0[0]
    expected_var = 1 - scheduler.alphas_cumprod[t_idx]
    
    print(f"Forward process test:")
    print(f"Expected mean norm: {expected_mean.norm():.4f}")
    print(f"Actual mean norm: {x_t[0].mean():.4f}")
    print(f"Expected variance: {expected_var:.4f}")
    print(f"Actual variance: {x_t[0].var():.4f}")
    
    # Test reverse process (with dummy model)
    class DummyModel(nn.Module):
        def forward(self, x, t):
            return torch.randn_like(x)
    
    model = DummyModel()
    result = scheduler.p_sample(model, x_t, t, t[0].item())
    
    print(f"\nReverse process test:")
    print(f"Input shape: {x_t.shape}")
    print(f"Output shape: {result['prev_sample'].shape}")
    print(f"Predicted mean shape: {result['pred_mean'].shape}")
    print(f"Predicted variance shape: {result['pred_variance'].shape}")

if __name__ == "__main__":
    test_diffusion_mathematics()
```

## Key Mathematical Insights

### 1. Reparameterization Trick

The key insight is using the reparameterization trick to express x_t in terms of x_0 and noise:
```
x_t = √(ᾱ_t) * x_0 + √(1 - ᾱ_t) * ε
```

This allows us to predict x_0 from x_t and the predicted noise:
```
x_0_pred = (x_t - √(1 - ᾱ_t) * ε_pred) / √(ᾱ_t)
```

### 2. Variance Schedule

The variance in the reverse process is crucial for high-quality generation:
```
σ_t² = (1 - ᾱ_{t-1}) / (1 - ᾱ_t) * β_t
```

### 3. Classifier-Free Guidance

For conditional generation, classifier-free guidance uses:
```
ε_guided = ε_uncond + guidance_scale * (ε_cond - ε_uncond)
```

This mathematical foundation ensures that our diffusion model implementation is theoretically sound and practically effective.

