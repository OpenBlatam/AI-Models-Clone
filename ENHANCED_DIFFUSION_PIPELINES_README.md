# Enhanced Diffusion Pipelines System

## Overview

The Enhanced Diffusion Pipelines System is a comprehensive implementation that provides deep understanding and correct implementation of different diffusion model pipelines using the Hugging Face Diffusers library. This system goes beyond basic model loading to provide pipeline-specific handling, analysis, and optimization.

## 🎯 Key Features

### Pipeline Types Supported
- **Text-to-Image**: Standard diffusion models (SD v1.5, v2.1, SDXL)
- **Image-to-Image**: Transform existing images with new prompts
- **Inpainting**: Fill masked areas with new content
- **ControlNet**: Controlled generation using conditioning inputs
- **Refiner**: High-quality refinement of base model outputs
- **Cascade**: Multi-stage generation pipelines

### Enhanced Capabilities
- **Pipeline-Specific Handling**: Each pipeline type has dedicated generation logic
- **Smart Parameter Management**: Automatic parameter selection based on pipeline type
- **Memory Optimization**: Built-in attention slicing, VAE slicing, and model offloading
- **Comprehensive Analysis**: Deep pipeline inspection and capability detection
- **Flexible Configuration**: Extensive configuration options for each pipeline type

## 🚀 Quick Start

### Installation

```bash
# Install required dependencies
pip install torch diffusers transformers accelerate xformers
pip install pillow matplotlib numpy
```

### Basic Usage

```python
from core.diffusion_models_system import DiffusionModelManager, GenerationConfig

# Initialize manager
manager = DiffusionModelManager()

# Load different pipeline types
sd_model = manager.load_model("stable-diffusion-v1-5")      # Text-to-image
sdxl_model = manager.load_model("stable-diffusion-xl-base") # SDXL text-to-image
img2img_model = manager.load_model("stable-diffusion-img2img") # Image-to-image
inpaint_model = manager.load_model("stable-diffusion-inpaint") # Inpainting

# Generate with text-to-image pipeline
config = GenerationConfig(
    prompt="A beautiful sunset over the mountains",
    num_inference_steps=30,
    guidance_scale=7.5
)
images = manager.generate_image("stable-diffusion-v1-5", config)
```

## 🔧 Pipeline Types Deep Dive

### 1. Text-to-Image Pipeline

The most common pipeline type, generating images from text prompts.

```python
# Standard SD v1.5
config = GenerationConfig(
    prompt="A majestic dragon flying over mountains",
    negative_prompt="blurry, low quality",
    height=512,
    width=512,
    num_inference_steps=50,
    guidance_scale=7.5
)

# SDXL with enhanced prompts
config = GenerationConfig(
    prompt="A futuristic city with flying cars",
    prompt_2="Detailed, high quality, masterpiece",
    negative_prompt="blurry, low quality, distorted",
    height=1024,
    width=1024,
    num_inference_steps=30,
    guidance_scale=8.0
)
```

**Key Features:**
- Automatic SDXL parameter handling
- Dual prompt system for SDXL
- Flexible resolution settings
- Comprehensive negative prompting

### 2. Image-to-Image Pipeline

Transform existing images using text prompts and strength control.

```python
from PIL import Image

# Load input image
input_image = Image.open("input.jpg")

config = GenerationConfig(
    prompt="Transform into a watercolor painting style",
    image=input_image,
    strength=0.7,  # How much to change (0.0 = no change, 1.0 = completely new)
    num_inference_steps=30,
    guidance_scale=7.5
)

images = manager.generate_image("stable-diffusion-img2img", config)
```

**Key Features:**
- Strength parameter for transformation control
- Automatic image preprocessing
- Maintains input image structure
- Flexible transformation levels

### 3. Inpainting Pipeline

Fill masked areas with new content while preserving the rest of the image.

```python
# Create or load mask (white = fill area, black = preserve)
mask_image = Image.open("mask.png")

config = GenerationConfig(
    prompt="Fill with beautiful flowers and butterflies",
    image=input_image,
    mask_image=mask_image,
    num_inference_steps=30,
    guidance_scale=7.5
)

images = manager.generate_image("stable-diffusion-inpaint", config)
```

**Key Features:**
- Mask-based area selection
- Seamless content integration
- Preserves unmasked areas
- Flexible mask shapes and sizes

### 4. ControlNet Pipeline

Controlled generation using conditioning inputs like edges, depth maps, or poses.

```python
config = GenerationConfig(
    prompt="A detailed portrait of a wise wizard",
    height=512,
    width=512,
    num_inference_steps=30,
    guidance_scale=7.5,
    controlnet_conditioning_scale=1.0,  # How much to follow control signal
    control_guidance_start=0.0,         # When to start control guidance
    control_guidance_end=1.0            # When to end control guidance
)

images = manager.generate_image("stable-diffusion-controlnet", config)
```

**Key Features:**
- Conditioning scale control
- Temporal guidance control
- Multiple control signal types
- Precise generation control

### 5. Refiner Pipeline

High-quality refinement of base model outputs, typically used with SDXL.

```python
config = GenerationConfig(
    prompt="Refine this image to high quality",
    height=1024,
    width=1024,
    num_inference_steps=20,
    guidance_scale=5.0
)

images = manager.generate_image("stable-diffusion-xl-refiner", config)
```

**Key Features:**
- Works with base model latents
- High-quality refinement
- Reduced inference steps
- Optimized for quality over speed

## ⚙️ Configuration Options

### DiffusionModelConfig

```python
@dataclass
class DiffusionModelConfig:
    model_name: str
    model_type: DiffusionModelType
    pipeline_type: PipelineType
    scheduler_type: SchedulerType
    torch_dtype: str = "float16"
    
    # Memory optimization
    enable_attention_slicing: bool = True
    enable_vae_slicing: bool = True
    enable_xformers_memory_efficient_attention: bool = True
    
    # Pipeline-specific
    controlnet_conditioning_scale: float = 1.0
    refiner_strength: float = 0.8
    cascade_guidance_scale: float = 3.0
```

### GenerationConfig

```python
@dataclass
class GenerationConfig:
    prompt: str
    negative_prompt: str = ""
    height: int = 512
    width: int = 512
    num_inference_steps: int = 50
    guidance_scale: float = 7.5
    
    # SDXL specific
    prompt_2: Optional[str] = None
    negative_prompt_2: Optional[str] = None
    
    # Image-to-image
    image: Optional[Image.Image] = None
    strength: float = 0.8
    
    # Inpainting
    mask_image: Optional[Image.Image] = None
    
    # ControlNet
    controlnet_conditioning_scale: float = 1.0
    control_guidance_start: float = 0.0
    control_guidance_end: float = 1.0
```

## 🔍 Pipeline Analysis

### Analyze Pipeline Capabilities

```python
# Get comprehensive pipeline analysis
analysis = manager.analyze_pipeline("stable-diffusion-v1-5")

print(f"Pipeline Type: {analysis['pipeline_type']}")
print(f"Model Type: {analysis['model_type']}")
print(f"Supports Img2Img: {analysis['supports_img2img']}")
print(f"Supports Inpainting: {analysis['supports_inpainting']}")
print(f"Supports ControlNet: {analysis['supports_controlnet']}")
print(f"Text Encoder: {analysis['text_encoder_type']}")
print(f"VAE: {analysis['vae_type']}")
print(f"UNet: {analysis['unet_type']}")
```

### Pipeline Comparison

```python
# Compare multiple pipelines
pipelines = ["stable-diffusion-v1-5", "stable-diffusion-xl-base", "stable-diffusion-img2img"]

for name in pipelines:
    analysis = manager.analyze_pipeline(name)
    print(f"\n{name}:")
    print(f"  Type: {analysis['pipeline_type']}")
    print(f"  Capabilities: {[k for k, v in analysis.items() if k.startswith('supports_') and v]}")
```

## 🚀 Advanced Usage

### Custom Pipeline Configuration

```python
# Create custom pipeline config
custom_config = DiffusionModelConfig(
    model_name="custom/model/path",
    model_type=DiffusionModelType.CUSTOM,
    pipeline_type=PipelineType.TEXT_TO_IMAGE,
    scheduler_type=SchedulerType.EULER,
    enable_attention_slicing=True,
    enable_vae_slicing=True
)

# Load custom model
custom_model = manager.load_model("custom-model", custom_config)
```

### Batch Generation

```python
# Generate multiple images with different configs
configs = [
    GenerationConfig(prompt="A cat", guidance_scale=7.0),
    GenerationConfig(prompt="A dog", guidance_scale=8.0),
    GenerationConfig(prompt="A bird", guidance_scale=9.0)
]

all_images = manager.generate_image_batch("stable-diffusion-v1-5", configs)
```

### Memory Optimization

```python
# Configure memory optimization
config = DiffusionModelConfig(
    model_name="stabilityai/stable-diffusion-xl-base-1.0",
    enable_attention_slicing=True,
    enable_vae_slicing=True,
    enable_model_cpu_offload=True,
    enable_xformers_memory_efficient_attention=True
)

# Load optimized model
optimized_model = manager.load_model("sdxl-optimized", config)
```

## 📊 Performance Optimization

### Scheduler Selection

```python
# Different schedulers for different use cases
schedulers = {
    "fast": SchedulerType.DPM_SOLVER_SINGLESTEP,    # Fast generation
    "quality": SchedulerType.EULER,                  # High quality
    "stable": SchedulerType.DDIM,                    # Stable results
    "creative": SchedulerType.DPM_SOLVER_MULTISTEP   # Creative variations
}

for name, scheduler in schedulers.items():
    config = DiffusionModelConfig(
        model_name="runwayml/stable-diffusion-v1-5",
        scheduler_type=scheduler
    )
    model = manager.load_model(f"sd-{name}", config)
```

### Memory Management

```python
# Progressive memory optimization
config = DiffusionModelConfig(
    model_name="stabilityai/stable-diffusion-xl-base-1.0",
    enable_attention_slicing=True,      # Reduce memory usage
    enable_vae_slicing=True,            # VAE memory optimization
    enable_model_cpu_offload=True,      # Offload to CPU when possible
    enable_xformers_memory_efficient_attention=True  # Use xformers if available
)
```

## 🧪 Testing and Validation

### Run Demo Script

```bash
# Run the comprehensive demo
python run_enhanced_diffusion_pipelines_demo.py
```

The demo script will:
1. Load different pipeline types
2. Generate sample images with each pipeline
3. Analyze pipeline capabilities
4. Compare pipeline features
5. Save demo images for inspection

### Expected Output

```
🚀 Starting Enhanced Diffusion Pipelines Demo

📥 Loading different pipeline types...
✅ Loaded stable-diffusion-v1-5: text_to_image
✅ Loaded stable-diffusion-xl-base: text_to_image
✅ Loaded stable-diffusion-img2img: image_to_image
✅ Loaded stable-diffusion-inpaint: inpainting
✅ Loaded stable-diffusion-controlnet: controlnet

🎨 Demo 1: Text-to-Image Pipeline
Using TEXT_TO_IMAGE pipeline handler
Text-to-image kwargs: ['prompt', 'negative_prompt', 'height', 'width', ...]
✅ Generated 2 images with SD v1.5

🌟 Demo 2: SDXL Pipeline
Using TEXT_TO_IMAGE pipeline handler
✅ Generated 1 images with SDXL

🔄 Demo 3: Image-to-Image Pipeline
Using IMAGE_TO_IMAGE pipeline handler
Image-to-image kwargs: ['prompt', 'negative_prompt', 'image', 'strength', ...]
✅ Generated 1 images with img2img pipeline

🎭 Demo 4: Inpainting Pipeline
Using INPAINTING pipeline handler
Inpainting kwargs: ['prompt', 'negative_prompt', 'image', 'mask_image', ...]
✅ Generated 1 images with inpainting pipeline

🎯 Demo 5: ControlNet Pipeline
Using CONTROLNET pipeline handler
ControlNet kwargs: ['prompt', 'negative_prompt', 'height', 'width', ...]
✅ Generated 1 images with ControlNet pipeline

🔍 Demo 6: Pipeline Analysis
📊 Analysis for stable-diffusion-v1-5:
  model_name: stable-diffusion-v1-5
  pipeline_type: text_to_image
  model_type: stable_diffusion
  scheduler_type: ddim
  ...

⚖️ Demo 7: Pipeline Comparison
📋 Pipeline Comparison Table:
Name                           Type                 Model                Img2Img    Inpaint    ControlNet
----------------------------------------------------------------------------------------------------
stable-diffusion-v1-5         text_to_image        stable_diffusion     False      False      False
stable-diffusion-xl-base      text_to_image        stable_diffusion_xl  False      False      False
stable-diffusion-img2img      image_to_image       stable_diffusion_im  True       False      False
stable-diffusion-inpaint      inpainting           stable_diffusion_in  False      True       False
stable-diffusion-controlnet   controlnet           stable_diffusion_co  False      False      True

🎉 Enhanced Diffusion Pipelines Demo Completed!
📁 Generated demo images have been saved to the current directory
```

## 🔧 Troubleshooting

### Common Issues

1. **Import Errors with Diffusers**
   ```bash
   # Ensure proper installation
   pip install --upgrade diffusers transformers
   ```

2. **Memory Issues**
   ```python
   # Enable memory optimization
   config = DiffusionModelConfig(
       enable_attention_slicing=True,
       enable_vae_slicing=True,
       enable_model_cpu_offload=True
   )
   ```

3. **Pipeline Type Mismatch**
   ```python
   # Check pipeline type before generation
   config = manager.get_model_config(model_name)
   if config.pipeline_type != PipelineType.TEXT_TO_IMAGE:
       raise ValueError(f"Model {model_name} is not a text-to-image pipeline")
   ```

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# This will show detailed pipeline operations
manager = DiffusionModelManager()
```

## 📚 API Reference

### Core Classes

- **`DiffusionModelManager`**: Main manager for loading and using models
- **`PipelineManager`**: Handles different pipeline types
- **`DiffusionModelConfig`**: Configuration for model loading
- **`GenerationConfig`**: Configuration for image generation

### Key Methods

- **`load_model(name, config)`**: Load a diffusion model
- **`generate_image(name, config)`**: Generate images with pipeline-specific handling
- **`analyze_pipeline(name)`**: Analyze pipeline capabilities
- **`get_model_config(name)`**: Get model configuration

### Pipeline Types

- **`PipelineType.TEXT_TO_IMAGE`**: Standard text-to-image generation
- **`PipelineType.IMAGE_TO_IMAGE`**: Transform existing images
- **`PipelineType.INPAINTING`**: Fill masked areas
- **`PipelineType.CONTROLNET`**: Controlled generation
- **`PipelineType.REFINER`**: High-quality refinement
- **`PipelineType.CASCADE`**: Multi-stage generation

## 🤝 Contributing

This system is designed to be extensible. To add new pipeline types:

1. Extend the `PipelineType` enum
2. Add pipeline-specific configuration to `DiffusionModelConfig`
3. Implement handler in `PipelineManager`
4. Add default configurations in `_setup_default_models`
5. Update documentation and tests

## 📄 License

This project is part of the Blatam Academy diffusion models implementation.

## 🙏 Acknowledgments

- Hugging Face Diffusers library for the foundation
- Stability AI for Stable Diffusion models
- The open-source AI community for continuous improvements

---

**Note**: This system provides a comprehensive understanding of different diffusion pipelines. For production use, ensure proper model licensing and consider using the actual Diffusers library instead of the mock implementations in the demo script.
