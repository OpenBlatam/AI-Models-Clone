import gradio as gr
import torch
import torch.nn.functional as F
import numpy as np
from PIL import Image
import io
import logging
import traceback
from typing import Optional, Tuple, Dict, Any, List
import os
import time
from pathlib import Path
import gc
import psutil
import threading
from contextlib import contextmanager

# Import our optimized model
from optimized_model import create_optimized_model, ModelOptimizer
from advanced_loss_functions import AdvancedLossFunctions
from performance_monitor import PerformanceMonitor

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gradio_demo.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedGradioImageProcessor:
    """Enhanced Gradio interface with advanced debugging and error handling"""
    
    def __init__(self, model_config: Optional[Dict[str, Any]] = None):
        self.device = self._setup_device()
        self.model = None
        self.model_config = model_config or {}
        self.performance_monitor = PerformanceMonitor(monitor_interval=1.0)
        self.loss_functions = AdvancedLossFunctions(device=self.device)
        
        # Enhanced performance tracking
        self.inference_times = []
        self.error_count = 0
        self.memory_usage = []
        self.gpu_memory_usage = []
        
        # Debug mode
        self.debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
        
        # Initialize model with error handling
        self._initialize_model()
        
        # Start performance monitoring
        self._start_performance_monitoring()
        
        logger.info(f"EnhancedGradioImageProcessor initialized on {self.device}")
    
    def _setup_device(self) -> torch.device:
        """Setup optimal device with comprehensive error handling"""
        try:
            if torch.cuda.is_available():
                device = torch.device('cuda')
                
                # Enable comprehensive debugging tools
                if self.debug_mode:
                    torch.autograd.set_detect_anomaly(True)
                    torch.backends.cudnn.deterministic = True
                    torch.backends.cudnn.benchmark = False
                    logger.info("Debug mode: CUDA anomaly detection enabled")
                else:
                    torch.backends.cudnn.benchmark = True
                    torch.backends.cudnn.deterministic = False
                
                # Set memory fraction to prevent OOM
                torch.cuda.set_per_process_memory_fraction(0.8)
                
                # Get device info
                device_name = torch.cuda.get_device_name(0)
                memory_total = torch.cuda.get_device_properties(0).total_memory / 1e9
                logger.info(f"CUDA device: {device_name} ({memory_total:.1f} GB)")
                
            elif torch.backends.mps.is_available():
                device = torch.device('mps')
                logger.info("MPS device available")
                
            else:
                device = torch.device('cpu')
                logger.info("Using CPU device")
                
            return device
            
        except Exception as e:
            logger.error(f"Device setup failed: {e}")
            logger.error(traceback.format_exc())
            return torch.device('cpu')
    
    def _initialize_model(self):
        """Initialize the optimized model with comprehensive error handling"""
        try:
            # Create model
            self.model = create_optimized_model(self.model_config)
            
            # Move to device
            self.model.to(self.device)
            self.model.eval()
            
            # Optimize for inference
            self.model = ModelOptimizer.optimize_for_inference(self.model)
            
            # Calculate model complexity
            complexity = ModelOptimizer.get_model_complexity(self.model)
            logger.info(f"Model complexity: {complexity['params']:,} parameters, {complexity['flops']:,} FLOPs")
            
            logger.info("Model initialized successfully")
            
        except Exception as e:
            logger.error(f"Model initialization failed: {e}")
            logger.error(traceback.format_exc())
            raise
    
    def _start_performance_monitoring(self):
        """Start background performance monitoring"""
        def monitor_loop():
            while True:
                try:
                    # Monitor system resources
                    cpu_percent = psutil.cpu_percent(interval=1)
                    memory_percent = psutil.virtual_memory().percent
                    
                    # Monitor GPU if available
                    if torch.cuda.is_available():
                        gpu_memory_allocated = torch.cuda.memory_allocated() / 1e9
                        gpu_memory_reserved = torch.cuda.memory_reserved() / 1e9
                        self.gpu_memory_usage.append({
                            'timestamp': time.time(),
                            'allocated_gb': gpu_memory_allocated,
                            'reserved_gb': gpu_memory_reserved
                        })
                    
                    self.memory_usage.append({
                        'timestamp': time.time(),
                        'cpu_percent': cpu_percent,
                        'memory_percent': memory_percent
                    })
                    
                    # Keep only last 100 entries
                    if len(self.memory_usage) > 100:
                        self.memory_usage = self.memory_usage[-100:]
                    if len(self.gpu_memory_usage) > 100:
                        self.gpu_memory_usage = self.gpu_memory_usage[-100:]
                    
                    time.sleep(5)  # Monitor every 5 seconds
                    
                except Exception as e:
                    logger.error(f"Performance monitoring error: {e}")
                    time.sleep(10)
        
        # Start monitoring in background thread
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
    
    @contextmanager
    def _memory_management(self):
        """Context manager for memory management"""
        try:
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()
            yield
        finally:
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()
    
    def _validate_input_image(self, image: Image.Image) -> Tuple[bool, str]:
        """Validate input image with comprehensive checks"""
        try:
            # Check if image exists
            if image is None:
                return False, "No image provided"
            
            # Check image format
            if hasattr(image, 'format') and image.format not in ['JPEG', 'PNG', 'BMP', 'TIFF', None]:
                return False, f"Unsupported image format: {image.format}"
            
            # Check image size
            width, height = image.size
            if width < 64 or height < 64:
                return False, f"Image too small: {width}x{height}. Minimum: 64x64"
            if width > 2048 or height > 2048:
                return False, f"Image too large: {width}x{height}. Maximum: 2048x2048"
            
            # Check image mode
            if image.mode not in ['RGB', 'L', 'RGBA']:
                return False, f"Unsupported color mode: {image.mode}"
            
            # Check if image is corrupted
            try:
                image.verify()
            except Exception:
                return False, "Image appears to be corrupted"
            
            return True, "Image validation passed"
            
        except Exception as e:
            return False, f"Image validation error: {str(e)}"
    
    def _preprocess_image(self, image: Image.Image) -> torch.Tensor:
        """Preprocess image with comprehensive error handling"""
        try:
            # Convert RGBA to RGB if needed
            if image.mode == 'RGBA':
                # Create white background
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1])
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize to model input size
            target_size = (256, 256)
            image = image.resize(target_size, Image.LANCZOS)
            
            # Convert to tensor
            image_array = np.array(image)
            if image_array.dtype != np.uint8:
                image_array = image_array.astype(np.uint8)
            
            image_tensor = torch.from_numpy(image_array).float() / 255.0
            image_tensor = image_tensor.permute(2, 0, 1).unsqueeze(0)
            
            # Validate tensor values
            if torch.isnan(image_tensor).any() or torch.isinf(image_tensor).any():
                raise ValueError("Invalid tensor values detected")
            
            # Normalize
            mean = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)
            std = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)
            image_tensor = (image_tensor - mean) / std
            
            return image_tensor
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            logger.error(traceback.format_exc())
            raise
    
    def _postprocess_image(self, tensor: torch.Tensor) -> Image.Image:
        """Postprocess tensor to image with comprehensive error handling"""
        try:
            # Validate input tensor
            if torch.isnan(tensor).any() or torch.isinf(tensor).any():
                raise ValueError("Invalid tensor values in output")
            
            # Denormalize
            mean = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)
            std = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)
            tensor = tensor * std + mean
            
            # Clamp values
            tensor = torch.clamp(tensor, 0, 1)
            
            # Convert to PIL
            tensor = tensor.squeeze(0).permute(1, 2, 0)
            image_array = (tensor.cpu().numpy() * 255).astype(np.uint8)
            
            # Validate output array
            if np.isnan(image_array).any() or np.isinf(image_array).any():
                raise ValueError("Invalid values in output array")
            
            return Image.fromarray(image_array)
            
        except Exception as e:
            logger.error(f"Image postprocessing failed: {e}")
            logger.error(traceback.format_exc())
            raise
    
    def process_image(self, input_image: Image.Image, 
                     processing_mode: str = "enhance",
                     quality_level: str = "high") -> Tuple[Image.Image, Dict[str, Any]]:
        """Process image with comprehensive error handling and debugging"""
        
        start_time = time.time()
        result_info = {}
        
        try:
            # Input validation
            is_valid, validation_msg = self._validate_input_image(input_image)
            if not is_valid:
                raise ValueError(validation_msg)
            
            # Preprocess with memory management
            with self._memory_management():
                input_tensor = self._preprocess_image(input_image)
                input_tensor = input_tensor.to(self.device)
            
            # Model inference with comprehensive error handling
            with torch.no_grad():
                try:
                    # Enable anomaly detection if in debug mode
                    if self.debug_mode:
                        with torch.autograd.detect_anomaly():
                            output_tensor = self.model(input_tensor)
                    else:
                        output_tensor = self.model(input_tensor)
                        
                except RuntimeError as e:
                    error_msg = str(e)
                    if "out of memory" in error_msg.lower():
                        # Handle OOM error
                        torch.cuda.empty_cache()
                        gc.collect()
                        raise RuntimeError("GPU out of memory. Try with a smaller image or restart the application.")
                    elif "cuda" in error_msg.lower():
                        raise RuntimeError(f"CUDA error: {error_msg}. Try restarting the application.")
                    else:
                        raise RuntimeError(f"Model inference error: {error_msg}")
                        
                except Exception as e:
                    logger.error(f"Unexpected inference error: {e}")
                    logger.error(traceback.format_exc())
                    raise RuntimeError(f"Unexpected error during inference: {str(e)}")
            
            # Postprocess
            output_image = self._postprocess_image(output_tensor)
            
            # Calculate processing metrics
            processing_time = time.time() - start_time
            self.inference_times.append(processing_time)
            
            # Calculate quality metrics
            quality_metrics = self._calculate_quality_metrics(input_tensor, output_tensor)
            
            # Memory usage info
            memory_info = self._get_memory_info()
            
            result_info = {
                "processing_time": f"{processing_time:.3f}s",
                "input_size": f"{input_image.size[0]}x{input_image.size[1]}",
                "output_size": f"{output_image.size[0]}x{output_image.size[1]}",
                "quality_score": f"{quality_metrics['overall_quality']:.3f}",
                "psnr": f"{quality_metrics['psnr']:.2f} dB",
                "ssim": f"{quality_metrics['ssim']:.3f}",
                "gpu_memory": f"{memory_info['gpu_memory']:.2f} GB",
                "system_memory": f"{memory_info['system_memory']:.1f}%",
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
                "error_message": error_msg,
                "error_type": type(e).__name__
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
    
    def _get_memory_info(self) -> Dict[str, float]:
        """Get current memory usage information"""
        try:
            info = {
                "system_memory": psutil.virtual_memory().percent,
                "gpu_memory": 0.0
            }
            
            if torch.cuda.is_available():
                info["gpu_memory"] = torch.cuda.memory_allocated() / 1e9
            
            return info
        except Exception as e:
            logger.warning(f"Memory info retrieval failed: {e}")
            return {"system_memory": 0.0, "gpu_memory": 0.0}
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        try:
            if not self.inference_times:
                return {"message": "No processing data available"}
            
            # Basic stats
            avg_time = np.mean(self.inference_times)
            min_time = np.min(self.inference_times)
            max_time = np.max(self.inference_times)
            std_time = np.std(self.inference_times)
            
            # Memory stats
            memory_stats = self._get_memory_info()
            
            # Error rate
            total_processed = len(self.inference_times)
            error_rate = (self.error_count / (self.error_count + total_processed)) * 100
            
            # Recent performance (last 10)
            recent_times = self.inference_times[-10:] if len(self.inference_times) >= 10 else self.inference_times
            recent_avg = np.mean(recent_times) if recent_times else 0
            
            return {
                "total_processed": total_processed,
                "average_time": f"{avg_time:.3f}s",
                "min_time": f"{min_time:.3f}s",
                "max_time": f"{max_time:.3f}s",
                "std_time": f"{std_time:.3f}s",
                "recent_average": f"{recent_avg:.3f}s",
                "error_rate": f"{error_rate:.1f}%",
                "device": str(self.device),
                "current_gpu_memory": f"{memory_stats['gpu_memory']:.2f} GB",
                "current_system_memory": f"{memory_stats['system_memory']:.1f}%",
                "debug_mode": self.debug_mode
            }
        except Exception as e:
            logger.error(f"Performance stats calculation failed: {e}")
            return {"error": "Failed to calculate performance stats"}
    
    def get_detailed_debug_info(self) -> Dict[str, Any]:
        """Get detailed debugging information"""
        try:
            debug_info = {
                "device_info": str(self.device),
                "model_loaded": self.model is not None,
                "debug_mode": self.debug_mode,
                "torch_version": torch.__version__,
                "cuda_available": torch.cuda.is_available(),
                "cudnn_enabled": torch.backends.cudnn.enabled,
                "anomaly_detection": torch.autograd.detect_anomaly.is_enabled() if hasattr(torch.autograd, 'detect_anomaly') else False
            }
            
            if torch.cuda.is_available():
                debug_info.update({
                    "cuda_device_count": torch.cuda.device_count(),
                    "cuda_device_name": torch.cuda.get_device_name(0),
                    "cuda_compute_capability": torch.cuda.get_device_capability(0),
                    "cuda_memory_allocated": f"{torch.cuda.memory_allocated() / 1e9:.2f} GB",
                    "cuda_memory_reserved": f"{torch.cuda.memory_reserved() / 1e9:.2f} GB",
                    "cuda_memory_total": f"{torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB"
                })
            
            return debug_info
            
        except Exception as e:
            logger.error(f"Debug info retrieval failed: {e}")
            return {"error": "Failed to retrieve debug info"}

def create_enhanced_gradio_interface():
    """Create the enhanced Gradio interface with comprehensive features"""
    
    # Initialize processor
    try:
        processor = EnhancedGradioImageProcessor({
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
    with gr.Blocks(title="Enhanced Image Processing System", theme=gr.themes.Soft()) as interface:
        
        gr.Markdown("""
        # 🚀 Enhanced Image Processing System
        
        **Production-ready AI-powered image enhancement with advanced debugging, error handling, and performance monitoring.**
        
        ### Features:
        - 🎯 **Multi-scale Processing**: Handles images at different scales
        - 🧠 **Attention Mechanisms**: Focuses on important image regions
        - 📡 **Frequency Enhancement**: Optimizes radio frequency characteristics
        - ⚡ **GPU Acceleration**: Automatic CUDA/MPS/CPU detection
        - 🛡️ **Comprehensive Error Handling**: Validation, recovery, and debugging
        - 📊 **Real-time Monitoring**: Performance, memory, and resource tracking
        - 🔍 **Debug Tools**: PyTorch anomaly detection and detailed diagnostics
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
                
                # Debug info
                gr.Markdown("### 🔍 Debug Information")
                debug_btn = gr.Button("🐛 Debug Info")
                debug_output = gr.JSON(label="Debug Data")
            
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
        ### ⚠️ Supported Formats & Debugging
        
        **Image Support:**
        - **Types**: JPEG, PNG, BMP, TIFF
        - **Size Range**: 64x64 to 2048x2048 pixels
        - **Color Modes**: RGB, Grayscale, RGBA (auto-converted)
        
        **Debug Features:**
        - PyTorch anomaly detection
        - Memory usage monitoring
        - Performance profiling
        - Comprehensive error logging
        """)
        
        # Event handlers with enhanced error handling
        def process_image_wrapper(image, mode, quality):
            """Wrapper for image processing with enhanced error handling"""
            if image is None:
                return None, {"status": "error", "error_message": "No image uploaded"}
            
            try:
                return processor.process_image(image, mode, quality)
            except Exception as e:
                logger.error(f"Processing wrapper error: {e}")
                logger.error(traceback.format_exc())
                return image, {
                    "status": "error", 
                    "error_message": str(e),
                    "error_type": type(e).__name__
                }
        
        def get_stats():
            """Get performance statistics with error handling"""
            try:
                return processor.get_performance_stats()
            except Exception as e:
                logger.error(f"Stats error: {e}")
                return {"error": str(e), "error_type": type(e).__name__}
        
        def get_debug_info():
            """Get debug information with error handling"""
            try:
                return processor.get_detailed_debug_info()
            except Exception as e:
                logger.error(f"Debug info error: {e}")
                return {"error": str(e), "error_type": type(e).__name__}
        
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
        
        debug_btn.click(
            fn=get_debug_info,
            outputs=debug_output
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
    """Main function to launch the enhanced Gradio interface"""
    try:
        # Set environment variables for debugging
        if os.getenv('DEBUG_MODE') is None:
            os.environ['DEBUG_MODE'] = 'False'
        
        # Create and launch interface
        interface = create_enhanced_gradio_interface()
        
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
        logger.error(f"Failed to launch enhanced Gradio interface: {e}")
        logger.error(traceback.format_exc())
        raise

if __name__ == "__main__":
    main()


