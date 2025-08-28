import gradio as gr
import torch
import torch.nn.functional as F
import numpy as np
from PIL import Image
import io
import logging
import traceback
from typing import Optional, Tuple, Dict, Any
import os
import time
from pathlib import Path

# Import our optimized model
from optimized_model import create_optimized_model, ModelOptimizer
from advanced_loss_functions import AdvancedLossFunctions
from performance_monitor import PerformanceMonitor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GradioImageProcessor:
    """Production-ready Gradio interface for image processing"""
    
    def __init__(self, model_config: Optional[Dict[str, Any]] = None):
        self.device = self._setup_device()
        self.model = None
        self.model_config = model_config or {}
        self.performance_monitor = PerformanceMonitor(monitor_interval=2.0)
        self.loss_functions = AdvancedLossFunctions(device=self.device)
        
        # Initialize model
        self._initialize_model()
        
        # Performance tracking
        self.inference_times = []
        self.error_count = 0
        
        logger.info(f"GradioImageProcessor initialized on {self.device}")
    
    def _setup_device(self) -> torch.device:
        """Setup optimal device with error handling"""
        try:
            if torch.cuda.is_available():
                device = torch.device('cuda')
                # Enable anomaly detection for debugging
                torch.autograd.set_detect_anomaly(True)
                logger.info(f"CUDA device: {torch.cuda.get_device_name(0)}")
            elif torch.backends.mps.is_available():
                device = torch.device('mps')
                logger.info("MPS device available")
            else:
                device = torch.device('cpu')
                logger.info("Using CPU device")
            return device
        except Exception as e:
            logger.error(f"Device setup failed: {e}")
            return torch.device('cpu')
    
    def _initialize_model(self):
        """Initialize the optimized model with error handling"""
        try:
            self.model = create_optimized_model(self.model_config)
            self.model.to(self.device)
            self.model.eval()
            
            # Optimize for inference
            self.model = ModelOptimizer.optimize_for_inference(self.model)
            
            logger.info("Model initialized successfully")
        except Exception as e:
            logger.error(f"Model initialization failed: {e}")
            raise
    
    def _validate_input_image(self, image: Image.Image) -> Tuple[bool, str]:
        """Validate input image with comprehensive checks"""
        try:
            # Check image format
            if image.format not in ['JPEG', 'PNG', 'BMP', 'TIFF']:
                return False, f"Unsupported image format: {image.format}"
            
            # Check image size
            width, height = image.size
            if width < 64 or height < 64:
                return False, f"Image too small: {width}x{height}. Minimum: 64x64"
            if width > 2048 or height > 2048:
                return False, f"Image too large: {width}x{height}. Maximum: 2048x2048"
            
            # Check image mode
            if image.mode not in ['RGB', 'L']:
                return False, f"Unsupported color mode: {image.mode}"
            
            return True, "Image validation passed"
            
        except Exception as e:
            return False, f"Image validation error: {str(e)}"
    
    def _preprocess_image(self, image: Image.Image) -> torch.Tensor:
        """Preprocess image with error handling"""
        try:
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize to model input size
            target_size = (256, 256)
            image = image.resize(target_size, Image.LANCZOS)
            
            # Convert to tensor
            image_tensor = torch.from_numpy(np.array(image)).float() / 255.0
            image_tensor = image_tensor.permute(2, 0, 1).unsqueeze(0)
            
            # Normalize
            mean = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)
            std = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)
            image_tensor = (image_tensor - mean) / std
            
            return image_tensor
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            raise
    
    def _postprocess_image(self, tensor: torch.Tensor) -> Image.Image:
        """Postprocess tensor to image with error handling"""
        try:
            # Denormalize
            mean = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)
            std = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)
            tensor = tensor * std + mean
            
            # Clamp values
            tensor = torch.clamp(tensor, 0, 1)
            
            # Convert to PIL
            tensor = tensor.squeeze(0).permute(1, 2, 0)
            image_array = (tensor.cpu().numpy() * 255).astype(np.uint8)
            
            return Image.fromarray(image_array)
            
        except Exception as e:
            logger.error(f"Image postprocessing failed: {e}")
            raise
    
    def process_image(self, input_image: Image.Image, 
                     processing_mode: str = "enhance",
                     quality_level: str = "high") -> Tuple[Image.Image, Dict[str, Any]]:
        """Process image with comprehensive error handling"""
        
        start_time = time.time()
        result_info = {}
        
        try:
            # Input validation
            is_valid, validation_msg = self._validate_input_image(input_image)
            if not is_valid:
                raise ValueError(validation_msg)
            
            # Preprocess
            input_tensor = self._preprocess_image(input_image)
            input_tensor = input_tensor.to(self.device)
            
            # Model inference with error handling
            with torch.no_grad():
                try:
                    output_tensor = self.model(input_tensor)
                except RuntimeError as e:
                    if "out of memory" in str(e):
                        # Handle OOM error
                        torch.cuda.empty_cache()
                        raise RuntimeError("GPU out of memory. Try with a smaller image or restart the application.")
                    else:
                        raise
            
            # Postprocess
            output_image = self._postprocess_image(output_tensor)
            
            # Calculate processing metrics
            processing_time = time.time() - start_time
            self.inference_times.append(processing_time)
            
            # Calculate quality metrics
            quality_metrics = self._calculate_quality_metrics(input_tensor, output_tensor)
            
            result_info = {
                "processing_time": f"{processing_time:.3f}s",
                "input_size": f"{input_image.size[0]}x{input_image.size[1]}",
                "output_size": f"{output_image.size[0]}x{output_image.size[1]}",
                "quality_score": f"{quality_metrics['overall_quality']:.3f}",
                "psnr": f"{quality_metrics['psnr']:.2f} dB",
                "ssim": f"{quality_metrics['ssim']:.3f}",
                "status": "success"
            }
            
            logger.info(f"Image processed successfully in {processing_time:.3f}s")
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.error_count += 1
            
            error_msg = f"Processing failed: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            
            result_info = {
                "processing_time": f"{processing_time:.3f}s",
                "status": "error",
                "error_message": error_msg
            }
            
            # Return original image on error
            output_image = input_image
        
        return output_image, result_info
    
    def _calculate_quality_metrics(self, input_tensor: torch.Tensor, 
                                 output_tensor: torch.Tensor) -> Dict[str, float]:
        """Calculate quality metrics with error handling"""
        try:
            return self.loss_functions.assess_image_quality(input_tensor, output_tensor)
        except Exception as e:
            logger.warning(f"Quality metrics calculation failed: {e}")
            return {
                "overall_quality": 0.0,
                "psnr": 0.0,
                "ssim": 0.0
            }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        try:
            if not self.inference_times:
                return {"message": "No processing data available"}
            
            avg_time = np.mean(self.inference_times)
            min_time = np.min(self.inference_times)
            max_time = np.max(self.inference_times)
            
            return {
                "total_processed": len(self.inference_times),
                "average_time": f"{avg_time:.3f}s",
                "min_time": f"{min_time:.3f}s",
                "max_time": f"{max_time:.3f}s",
                "error_rate": f"{self.error_count / (self.error_count + len(self.inference_times)) * 100:.1f}%",
                "device": str(self.device)
            }
        except Exception as e:
            logger.error(f"Performance stats calculation failed: {e}")
            return {"error": "Failed to calculate performance stats"}

def create_gradio_interface():
    """Create the Gradio interface with comprehensive features"""
    
    # Initialize processor
    try:
        processor = GradioImageProcessor({
            'model_type': 'optimized',
            'base_channels': 64,
            'num_blocks': 8,
            'use_attention': True,
            'use_multiscale': True,
            'use_frequency': True
        })
    except Exception as e:
        logger.error(f"Failed to initialize processor: {e}")
        raise
    
    # Define interface components
    with gr.Blocks(title="Advanced Image Processing System", theme=gr.themes.Soft()) as interface:
        
        gr.Markdown("""
        # 🚀 Advanced Image Processing System
        
        **Optimized AI-powered image enhancement with advanced error handling and performance monitoring.**
        
        ### Features:
        - 🎯 **Multi-scale Processing**: Handles images at different scales
        - 🧠 **Attention Mechanisms**: Focuses on important image regions
        - 📡 **Frequency Enhancement**: Optimizes radio frequency characteristics
        - ⚡ **GPU Acceleration**: Automatic CUDA/MPS/CPU detection
        - 🛡️ **Error Handling**: Comprehensive validation and error recovery
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                # Input section
                gr.Markdown("### 📥 Input Image")
                input_image = gr.Image(
                    label="Upload Image",
                    type="pil",
                    height=300
                )
                
                # Processing options
                gr.Markdown("### ⚙️ Processing Options")
                processing_mode = gr.Dropdown(
                    choices=["enhance", "denoise", "sharpen", "restore"],
                    value="enhance",
                    label="Processing Mode"
                )
                
                quality_level = gr.Dropdown(
                    choices=["fast", "balanced", "high"],
                    value="high",
                    label="Quality Level"
                )
                
                process_btn = gr.Button(
                    "🚀 Process Image",
                    variant="primary",
                    size="lg"
                )
                
                # Performance stats
                gr.Markdown("### 📊 Performance Statistics")
                stats_btn = gr.Button("📈 Show Stats")
                stats_output = gr.JSON(label="Performance Data")
            
            with gr.Column(scale=1):
                # Output section
                gr.Markdown("### 📤 Processed Image")
                output_image = gr.Image(
                    label="Result",
                    height=300
                )
                
                # Results info
                gr.Markdown("### 📋 Processing Results")
                results_output = gr.JSON(label="Results")
                
                # Download button
                download_btn = gr.DownloadButton(
                    label="💾 Download Result",
                    variant="secondary"
                )
        
        # Error handling and validation
        gr.Markdown("""
        ### ⚠️ Supported Formats
        - **Image Types**: JPEG, PNG, BMP, TIFF
        - **Size Range**: 64x64 to 2048x2048 pixels
        - **Color Modes**: RGB, Grayscale
        """)
        
        # Event handlers
        def process_image_wrapper(image, mode, quality):
            """Wrapper for image processing with error handling"""
            if image is None:
                return None, {"status": "error", "error_message": "No image uploaded"}
            
            try:
                return processor.process_image(image, mode, quality)
            except Exception as e:
                logger.error(f"Processing wrapper error: {e}")
                return image, {"status": "error", "error_message": str(e)}
        
        def get_stats():
            """Get performance statistics"""
            try:
                return processor.get_performance_stats()
            except Exception as e:
                logger.error(f"Stats error: {e}")
                return {"error": str(e)}
        
        # Connect components
        process_btn.click(
            fn=process_image_wrapper,
            inputs=[input_image, processing_mode, quality_level],
            outputs=[output_image, results_output]
        )
        
        stats_btn.click(
            fn=get_stats,
            outputs=stats_output
        )
        
        # Download functionality
        download_btn.click(
            fn=lambda: None,
            inputs=[],
            outputs=[],
            _js="() => { const link = document.createElement('a'); link.download = 'processed_image.png'; link.href = document.querySelector('.output-image img').src; link.click(); }"
        )
        
        # Input validation
        input_image.change(
            fn=lambda img: gr.update(value=img) if img is not None else gr.update(value=None),
            inputs=[input_image],
            outputs=[input_image]
        )
    
    return interface

def main():
    """Main function to launch the Gradio interface"""
    try:
        # Create and launch interface
        interface = create_gradio_interface()
        
        # Launch with production settings
        interface.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            debug=False,
            show_error=True,
            quiet=False
        )
        
    except Exception as e:
        logger.error(f"Failed to launch Gradio interface: {e}")
        raise

if __name__ == "__main__":
    main()


