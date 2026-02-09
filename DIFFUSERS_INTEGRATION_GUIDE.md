# 🎨 Diffusers Integration Guide for Enhanced AI Model Demos System

## 🎯 Overview

This guide covers the integration of Hugging Face Diffusers library with your Enhanced AI Model Demos System, enabling:

- **Text-to-Image Generation**: Stable Diffusion, DALL-E style models
- **Image-to-Image Translation**: Style transfer, image editing
- **Inpainting & Outpainting**: Image completion and extension
- **ControlNet & Conditioning**: Advanced image control
- **Video Generation**: Text-to-video, video editing
- **Audio Diffusion**: Text-to-audio, audio generation

## 📦 Core Dependencies

### **Essential Diffusers Packages**
```bash
# Core diffusers library
diffusers>=0.28.0

# Transformers with torch support
transformers[torch]>=4.42.0

# Training acceleration
accelerate>=0.31.0

# Safe model loading
safetensors>=0.4.3
```

### **Image Processing & Generation**
```bash
# Core image processing
Pillow>=10.0.0
opencv-python>=4.8.0

# Image I/O and video
imageio>=2.31.0
imageio-ffmpeg>=0.4.9

# Text processing utilities
ftfy>=6.1.0
regex>=2023.8.0
```

## 🚀 Installation

### **Quick Install**
```bash
pip install diffusers transformers[torch] accelerate
```

### **Full Install with Dependencies**
```bash
pip install -r requirements-enhanced-system.txt
```

### **GPU Support (Optional)**
```bash
# For CUDA support
pip install diffusers transformers[torch] torch torchvision --index-url https://download.pytorch.org/whl/cu118

# For specific features
pip install diffusers[torch,flax,tf]
```

## 🔧 Basic Usage

### **1. Text-to-Image Generation**
```python
from diffusers import StableDiffusionPipeline
import torch

# Load the pipeline
pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16,
    use_safetensors=True
)

# Move to GPU if available
if torch.cuda.is_available():
    pipe = pipe.to("cuda")

# Generate image
prompt = "A beautiful sunset over mountains, digital art"
image = pipe(prompt).images[0]

# Save the image
image.save("generated_image.png")
```

### **2. Image-to-Image Translation**
```python
from diffusers import StableDiffusionImg2ImgPipeline
from PIL import Image

# Load the pipeline
pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16
)

# Load input image
init_image = Image.open("input_image.jpg").convert("RGB")
init_image = init_image.resize((768, 512))

# Generate new image
prompt = "Turn this into a watercolor painting"
image = pipe(
    prompt=prompt,
    image=init_image,
    strength=0.75,
    guidance_scale=7.5
).images[0]

image.save("watercolor_image.png")
```

### **3. Inpainting (Image Completion)**
```python
from diffusers import StableDiffusionInpaintPipeline
from PIL import Image
import numpy as np

# Load the pipeline
pipe = StableDiffusionInpaintPipeline.from_pretrained(
    "runwayml/stable-diffusion-inpainting",
    torch_dtype=torch.float16
)

# Load image and mask
image = Image.open("image_with_hole.jpg")
mask = Image.open("mask.png")

# Inpaint the masked area
prompt = "A beautiful flower garden"
inpainted_image = pipe(
    prompt=prompt,
    image=image,
    mask_image=mask,
    num_inference_steps=50
).images[0]

inpainted_image.save("inpainted_image.png")
```

## 🎨 Advanced Features

### **1. ControlNet for Precise Control**
```python
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel
from diffusers.utils import load_image
import cv2
import numpy as np

# Load ControlNet model
controlnet = ControlNetModel.from_pretrained(
    "lllyasviel/sd-controlnet-canny",
    torch_dtype=torch.float16
)

# Load the pipeline
pipe = StableDiffusionControlNetPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    controlnet=controlnet,
    torch_dtype=torch.float16
)

# Load and process image
image = load_image("input_image.jpg")
image = np.array(image)

# Detect edges
low_threshold = 100
high_threshold = 200
canny = cv2.Canny(image, low_threshold, high_threshold)
canny = canny[:, :, None]
canny = np.concatenate([canny, canny, canny], axis=2)
canny = Image.fromarray(canny)

# Generate with edge control
prompt = "A beautiful landscape, oil painting"
image = pipe(
    prompt,
    image=canny,
    num_inference_steps=50
).images[0]

image.save("controlled_image.png")
```

### **2. Custom Training & Fine-tuning**
```python
from diffusers import StableDiffusionPipeline, DDPMScheduler
from diffusers.training_utils import EMAModel
import torch

# Load base model
model_id = "runwayml/stable-diffusion-v1-5"
pipe = StableDiffusionPipeline.from_pretrained(model_id)

# Setup training components
noise_scheduler = DDPMScheduler.from_config(model_id)
ema_model = EMAModel(pipe.unet.parameters())

# Training loop
optimizer = torch.optim.AdamW(pipe.unet.parameters(), lr=1e-5)

for epoch in range(num_epochs):
    for batch in train_dataloader:
        # Training step
        optimizer.zero_grad()
        
        # Forward pass
        noise_pred = pipe.unet(batch["latents"], batch["timesteps"])
        loss = torch.nn.functional.mse_loss(noise_pred, batch["noise"])
        
        # Backward pass
        loss.backward()
        optimizer.step()
        
        # Update EMA
        ema_model.step(pipe.unet.parameters())
```

### **3. Video Generation**
```python
from diffusers import DiffusionPipeline, DPMSolverMultistepScheduler
import torch

# Load video generation pipeline
pipe = DiffusionPipeline.from_pretrained(
    "damo-vilab/text-to-video-ms-1.7b",
    torch_dtype=torch.float16,
    variant="fp16"
)

# Use DPM-Solver++ scheduler for faster inference
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)

# Generate video
prompt = "A cat walking in the rain"
video_frames = pipe(
    prompt,
    num_inference_steps=25,
    num_frames=16
).frames

# Save video frames
for i, frame in enumerate(video_frames):
    frame.save(f"frame_{i:03d}.png")
```

### **4. Audio Diffusion**
```python
from diffusers import AudioDiffusionPipeline
import torch

# Load audio pipeline
pipe = AudioDiffusionPipeline.from_pretrained(
    "teticio/audio-diffusion-256",
    torch_dtype=torch.float16
)

# Generate audio
prompt = "A peaceful piano melody"
audio = pipe(prompt, num_inference_steps=50)

# Save audio
audio.save("generated_audio.wav")
```

## 🔍 Model Types & Use Cases

### **Diffusion Models**
| Model Type | Use Case | Example Models |
|------------|----------|----------------|
| **Text-to-Image** | Image generation from text | Stable Diffusion, DALL-E |
| **Image-to-Image** | Style transfer, editing | ControlNet, InstructPix2Pix |
| **Inpainting** | Image completion | Stable Diffusion Inpainting |
| **Video Generation** | Text-to-video | Text2Video-Zero, ModelScope |
| **Audio Generation** | Text-to-audio | Audio Diffusion, MusicLM |

### **Specialized Pipelines**
```python
# InstructPix2Pix for image editing
from diffusers import StableDiffusionInstructPix2PixPipeline

pipe = StableDiffusionInstructPix2PixPipeline.from_pretrained(
    "timbrooks/instruct-pix2pix",
    torch_dtype=torch.float16
)

# Edit image with instructions
image = pipe(
    "Make the sky more dramatic",
    image=init_image,
    num_inference_steps=20,
    image_guidance_scale=1.5,
    guidance_scale=7.5
).images[0]

# DreamBooth for personalization
from diffusers import DiffusionPipeline

pipe = DiffusionPipeline.from_pretrained(
    "CompVis/stable-diffusion-v1-4",
    torch_dtype=torch.float16
)

# Load fine-tuned model
pipe.unet.load_attn_procs("path/to/dreambooth/model")
```

## 🚀 Performance Optimization

### **1. Memory Optimization**
```python
# Enable attention slicing
pipe.enable_attention_slicing()

# Enable memory efficient attention
pipe.enable_xformers_memory_efficient_attention()

# Use CPU offloading
pipe.enable_model_cpu_offload()

# Enable sequential CPU offloading
pipe.enable_sequential_cpu_offload()
```

### **2. Speed Optimization**
```python
# Use faster scheduler
from diffusers import DPMSolverMultistepScheduler

pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)

# Reduce inference steps
image = pipe(
    prompt,
    num_inference_steps=20,  # Default is 50
    guidance_scale=7.5
).images[0]

# Use torch.compile (PyTorch 2.0+)
pipe.unet = torch.compile(pipe.unet, mode="reduce-overhead")
```

### **3. Batch Processing**
```python
# Generate multiple images
prompts = [
    "A beautiful sunset",
    "A mountain landscape",
    "A city skyline at night"
]

images = pipe(prompts, num_images_per_prompt=1).images

# Save all images
for i, image in enumerate(images):
    image.save(f"generated_image_{i}.png")
```

## 🧪 Testing & Validation

### **1. Model Loading Test**
```python
def test_diffusers_models():
    """Test if diffusers models can be loaded successfully."""
    models_to_test = [
        "runwayml/stable-diffusion-v1-5",
        "CompVis/stable-diffusion-v1-4",
        "stabilityai/stable-diffusion-2-1"
    ]
    
    for model_name in models_to_test:
        try:
            print(f"Testing {model_name}...")
            pipe = StableDiffusionPipeline.from_pretrained(model_name)
            print(f"✅ {model_name} loaded successfully")
        except Exception as e:
            print(f"❌ {model_name} failed: {e}")

# Run test
test_diffusers_models()
```

### **2. Generation Test**
```python
def test_image_generation():
    """Test basic image generation."""
    try:
        pipe = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype=torch.float16
        )
        
        if torch.cuda.is_available():
            pipe = pipe.to("cuda")
        
        # Generate test image
        prompt = "A simple red circle on white background"
        image = pipe(prompt, num_inference_steps=20).images[0]
        
        # Save test image
        image.save("test_generation.png")
        print("✅ Image generation test passed")
        return True
        
    except Exception as e:
        print(f"❌ Image generation test failed: {e}")
        return False
```

## 🔧 Integration with Your System

### **1. Enhanced UI Demos Integration**
```python
# Add to your enhanced_ui_demos_with_validation.py
from diffusers import StableDiffusionPipeline
import torch

class DiffusersDemo:
    def __init__(self):
        self.pipe = None
        self.model_loaded = False
    
    def load_model(self, model_name="runwayml/stable-diffusion-v1-5"):
        """Load a diffusers model."""
        try:
            self.pipe = StableDiffusionPipeline.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                use_safetensors=True
            )
            
            if torch.cuda.is_available():
                self.pipe = pipe.to("cuda")
            
            self.model_loaded = True
            return {"status": "success", "message": f"Model {model_name} loaded"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def generate_image(self, prompt, num_steps=50, guidance_scale=7.5):
        """Generate image from prompt."""
        if not self.model_loaded:
            return {"status": "error", "message": "Model not loaded"}
        
        try:
            image = self.pipe(
                prompt,
                num_inference_steps=num_steps,
                guidance_scale=guidance_scale
            ).images[0]
            
            # Save image
            filename = f"generated_{hash(prompt) % 10000}.png"
            image.save(filename)
            
            return {
                "status": "success",
                "image_path": filename,
                "prompt": prompt
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
```

### **2. Performance Monitoring Integration**
```python
# Integrate with your PerformanceOptimizer
class DiffusersPerformanceOptimizer:
    def __init__(self, model_name):
        self.model_name = model_name
        self.pipe = None
    
    def load_model(self):
        """Load model with performance optimizations."""
        self.pipe = StableDiffusionPipeline.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16
        )
        
        # Apply optimizations
        self.pipe.enable_attention_slicing()
        self.pipe.enable_xformers_memory_efficient_attention()
        
        if torch.cuda.is_available():
            self.pipe = self.pipe.to("cuda")
    
    def optimize_generation(self, prompt, **kwargs):
        """Optimized generation with performance monitoring."""
        start_time = time.time()
        start_memory = torch.cuda.memory_allocated() if torch.cuda.is_available() else 0
        
        # Generate image
        image = self.pipe(prompt, **kwargs).images[0]
        
        end_time = time.time()
        end_memory = torch.cuda.memory_allocated() if torch.cuda.is_available() else 0
        
        return {
            "image": image,
            "generation_time": end_time - start_time,
            "memory_delta_mb": (end_memory - start_memory) / 1024**2
        }
```

## 📊 Model Selection Guide

### **For Production Use**
- **Fast Generation**: Stable Diffusion 2.1, SDXL Turbo
- **High Quality**: Stable Diffusion XL, DeepFloyd IF
- **Specialized**: ControlNet, InstructPix2Pix
- **Video**: Text2Video-Zero, ModelScope

### **For Development**
- **Easy to Use**: Stable Diffusion 1.5, CompVis SD
- **Well Documented**: All official Hugging Face models
- **Flexible**: Custom pipelines, fine-tuning

### **For Research**
- **Latest Models**: SDXL, DeepFloyd, Imagen
- **Custom Architectures**: Custom diffusion models
- **Experimental Features**: Latest diffusers features

## 🚨 Common Issues & Solutions

### **1. Out of Memory**
```python
# Problem: Model too large for GPU
# Solution: Enable memory optimizations
pipe.enable_attention_slicing()
pipe.enable_xformers_memory_efficient_attention()
pipe.enable_model_cpu_offload()

# Or use smaller model
pipe = StableDiffusionPipeline.from_pretrained(
    "CompVis/stable-diffusion-v1-4",  # Smaller than SDXL
    torch_dtype=torch.float16
)
```

### **2. Slow Generation**
```python
# Problem: Generation takes too long
# Solution: Use faster scheduler and fewer steps
from diffusers import DPMSolverMultistepScheduler

pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)

image = pipe(
    prompt,
    num_inference_steps=20,  # Reduce from 50
    guidance_scale=7.5
).images[0]
```

### **3. Quality Issues**
```python
# Problem: Generated images are poor quality
# Solution: Adjust parameters
image = pipe(
    prompt,
    num_inference_steps=50,      # More steps = better quality
    guidance_scale=7.5,          # Higher = more prompt adherence
    negative_prompt="blurry, low quality"  # Avoid unwanted features
).images[0]
```

## 🎯 Next Steps

1. **Install Dependencies**: `pip install -r requirements-enhanced-system.txt`
2. **Test Basic Models**: Run the test scripts
3. **Integrate with Demos**: Add diffusers to your UI
4. **Customize Models**: Fine-tune for your specific use case
5. **Optimize Performance**: Use the performance tips

## 📚 Resources

- **Official Docs**: [huggingface.co/docs/diffusers](https://huggingface.co/docs/diffusers)
- **Model Hub**: [huggingface.co/models?pipeline_tag=text-to-image](https://huggingface.co/models?pipeline_tag=text-to-image)
- **Examples**: [github.com/huggingface/diffusers](https://github.com/huggingface/diffusers)
- **Community**: [discord.gg/huggingface](https://discord.gg/huggingface)

---

**Diffusers is now fully integrated into your Enhanced AI Model Demos System!** 🎉
