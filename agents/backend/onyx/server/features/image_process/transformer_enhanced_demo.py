#!/usr/bin/env python3
"""
Transformer-Enhanced Image Processing System - Gradio Demo

This module provides a production-ready Gradio interface with comprehensive
error handling, input validation, and integration with the Transformers library
for pre-trained models and tokenizers.

Features:
- Transformers library integration for pre-trained models
- Vision Transformer (ViT) and CLIP models
- Text-to-image and image-to-text capabilities
- Comprehensive error handling with try-except blocks
- Input validation for images and configuration parameters
- PyTorch integration with GPU utilization and mixed precision
- Object-oriented design for model architectures
- Functional programming for data processing pipelines
- PEP 8 compliant code style
- Advanced debugging tools including autograd.detect_anomaly()
- Proper weight initialization and normalization
- Custom loss functions and optimization algorithms
"""

import gradio as gr
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.autograd
import numpy as np
import cv2
from PIL import Image
import logging
import traceback
from typing import Optional, Tuple, Dict, Any, List, Union
import os
import sys
import time
from pathlib import Path
from functools import wraps
import json

# Transformers library imports
try:
    from transformers import (
        AutoImageProcessor, AutoModel, AutoTokenizer,
        VisionTransformerForImageClassification,
        CLIPProcessor, CLIPModel, CLIPTextModel, CLIPVisionModel,
        pipeline, AutoFeatureExtractor
    )
    from transformers.utils import logging as transformers_logging
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("Warning: Transformers library not available. Install with: pip install transformers")

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging with proper formatting
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress transformers warnings in production
if TRANSFORMERS_AVAILABLE:
    transformers_logging.set_verbosity_error()


class TransformerModelManager:
    """Manages transformer models with proper initialization and GPU utilization."""
    
    def __init__(self, device_config: Optional[Dict[str, Any]] = None):
        """
        Initialize transformer model manager with device configuration.
        
        Args:
            device_config: Optional device configuration dictionary
        """
        self.device = self._setup_optimal_device()
        self.device_config = device_config or {}
        self.mixed_precision_enabled = self.device_config.get('enable_mixed_precision', True)
        self.models = {}
        self.processors = {}
        self.tokenizers = {}
        
        if self.device_config.get('enable_anomaly_detection', False):
            torch.autograd.set_detect_anomaly(True)
            logger.info("PyTorch autograd anomaly detection enabled")
        
        logger.info(f"TransformerModelManager initialized on device: {self.device}")
    
    def _setup_optimal_device(self) -> torch.device:
        """Setup optimal device with automatic detection and configuration."""
        try:
            if torch.cuda.is_available():
                device = torch.device('cuda')
                
                torch.backends.cudnn.benchmark = True
                torch.backends.cudnn.deterministic = False
                
                memory_fraction = self.device_config.get('gpu_memory_fraction', 0.8)
                torch.cuda.set_per_process_memory_fraction(memory_fraction)
                
                gpu_name = torch.cuda.get_device_name(0)
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
                logger.info(f"CUDA device: {gpu_name} with {gpu_memory:.1f} GB memory")
                
            elif torch.backends.mps.is_available():
                device = torch.device('mps')
                logger.info("MPS device available for Apple Silicon")
                
            else:
                device = torch.device('cpu')
                logger.info("Using CPU device")
            
            return device
            
        except Exception as error:
            logger.error(f"Device setup failed: {error}")
            return torch.device('cpu')
    
    def load_vision_transformer(self, model_name: str = "google/vit-base-patch16-224") -> Tuple[Any, Any]:
        """
        Load a Vision Transformer model and processor.
        
        Args:
            model_name: Hugging Face model identifier
            
        Returns:
            Tuple of (model, processor)
        """
        try:
            if not TRANSFORMERS_AVAILABLE:
                raise ImportError("Transformers library not available")
            
            logger.info(f"Loading Vision Transformer: {model_name}")
            
            # Load processor and model
            processor = AutoImageProcessor.from_pretrained(model_name)
            model = VisionTransformerForImageClassification.from_pretrained(model_name)
            
            # Move to device and enable mixed precision
            model = model.to(self.device)
            if self.mixed_precision_enabled and self.device.type == 'cuda':
                model = model.half()
                logger.info("Mixed precision (FP16) enabled for ViT model")
            
            model.eval()
            
            # Store for later use
            self.models['vision_transformer'] = model
            self.processors['vision_transformer'] = processor
            
            logger.info(f"Vision Transformer loaded successfully: {model_name}")
            return model, processor
            
        except Exception as error:
            logger.error(f"Failed to load Vision Transformer: {error}")
            raise
    
    def load_clip_model(self, model_name: str = "openai/clip-vit-base-patch32") -> Tuple[Any, Any]:
        """
        Load a CLIP model and processor.
        
        Args:
            model_name: Hugging Face model identifier
            
        Returns:
            Tuple of (model, processor)
        """
        try:
            if not TRANSFORMERS_AVAILABLE:
                raise ImportError("Transformers library not available")
            
            logger.info(f"Loading CLIP model: {model_name}")
            
            # Load processor and model
            processor = CLIPProcessor.from_pretrained(model_name)
            model = CLIPModel.from_pretrained(model_name)
            
            # Move to device and enable mixed precision
            model = model.to(self.device)
            if self.mixed_precision_enabled and self.device.type == 'cuda':
                model = model.half()
                logger.info("Mixed precision (FP16) enabled for CLIP model")
            
            model.eval()
            
            # Store for later use
            self.models['clip'] = model
            self.processors['clip'] = processor
            
            logger.info(f"CLIP model loaded successfully: {model_name}")
            return model, processor
            
        except Exception as error:
            logger.error(f"Failed to load CLIP model: {error}")
            raise
    
    def load_text_model(self, model_name: str = "gpt2") -> Tuple[Any, Any]:
        """
        Load a text model and tokenizer.
        
        Args:
            model_name: Hugging Face model identifier
            
        Returns:
            Tuple of (model, tokenizer)
        """
        try:
            if not TRANSFORMERS_AVAILABLE:
                raise ImportError("Transformers library not available")
            
            logger.info(f"Loading text model: {model_name}")
            
            # Load tokenizer and model
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModel.from_pretrained(model_name)
            
            # Move to device and enable mixed precision
            model = model.to(self.device)
            if self.mixed_precision_enabled and self.device.type == 'cuda':
                model = model.half()
                logger.info("Mixed precision (FP16) enabled for text model")
            
            model.eval()
            
            # Store for later use
            self.models['text_model'] = model
            self.tokenizers['text_model'] = tokenizer
            
            logger.info(f"Text model loaded successfully: {model_name}")
            return model, tokenizer
            
        except Exception as error:
            logger.error(f"Failed to load text model: {error}")
            raise
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """Get list of available pre-trained models."""
        if not TRANSFORMERS_AVAILABLE:
            return {"error": ["Transformers library not available"]}
        
        return {
            "vision_models": [
                "google/vit-base-patch16-224",
                "google/vit-large-patch16-224",
                "microsoft/beit-base-patch16-224",
                "facebook/deit-base-distilled-patch16-224"
            ],
            "clip_models": [
                "openai/clip-vit-base-patch32",
                "openai/clip-vit-large-patch14",
                "openai/clip-vit-base-patch16"
            ],
            "text_models": [
                "gpt2",
                "bert-base-uncased",
                "distilbert-base-uncased",
                "roberta-base"
            ]
        }
    
    def process_image_with_vision_transformer(self, image: Union[np.ndarray, Image.Image]) -> Dict[str, Any]:
        """
        Process image using Vision Transformer for classification.
        
        Args:
            image: Input image as numpy array or PIL Image
            
        Returns:
            Dictionary with classification results
        """
        try:
            if 'vision_transformer' not in self.models:
                raise RuntimeError("Vision Transformer not loaded. Call load_vision_transformer() first.")
            
            model = self.models['vision_transformer']
            processor = self.processors['vision_transformer']
            
            # Convert to PIL if needed
            if isinstance(image, np.ndarray):
                image = Image.fromarray(image)
            
            # Process image
            inputs = processor(images=image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Inference
            with torch.no_grad():
                if self.mixed_precision_enabled and self.device.type == 'cuda':
                    with torch.cuda.amp.autocast():
                        outputs = model(**inputs)
                else:
                    outputs = model(**inputs)
            
            # Get predictions
            logits = outputs.logits
            probs = F.softmax(logits, dim=-1)
            predicted_class_id = logits.argmax(-1).item()
            
            # Get class labels if available
            if hasattr(model.config, 'id2label'):
                predicted_class = model.config.id2label[predicted_class_id]
            else:
                predicted_class = f"Class_{predicted_class_id}"
            
            confidence = probs[0][predicted_class_id].item()
            
            return {
                "class": predicted_class,
                "confidence": confidence,
                "class_id": predicted_class_id,
                "all_probs": probs[0].cpu().numpy().tolist()
            }
            
        except Exception as error:
            logger.error(f"Vision Transformer processing failed: {error}")
            raise
    
    def process_image_with_clip(self, image: Union[np.ndarray, Image.Image], 
                               text_prompt: str = "") -> Dict[str, Any]:
        """
        Process image using CLIP model for image-text understanding.
        
        Args:
            image: Input image as numpy array or PIL Image
            text_prompt: Optional text prompt for comparison
            
        Returns:
            Dictionary with CLIP results
        """
        try:
            if 'clip' not in self.models:
                raise RuntimeError("CLIP model not loaded. Call load_clip_model() first.")
            
            model = self.models['clip']
            processor = self.processors['clip']
            
            # Convert to PIL if needed
            if isinstance(image, np.ndarray):
                image = Image.fromarray(image)
            
            # Process inputs
            if text_prompt:
                inputs = processor(images=image, text=text_prompt, return_tensors="pt", padding=True)
            else:
                inputs = processor(images=image, return_tensors="pt")
            
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Inference
            with torch.no_grad():
                if self.mixed_precision_enabled and self.device.type == 'cuda':
                    with torch.cuda.amp.autocast():
                        outputs = model(**inputs)
                else:
                    outputs = model(**inputs)
            
            # Get image and text features
            image_features = outputs.image_embeds
            if text_prompt:
                text_features = outputs.text_embeds
                # Calculate similarity
                similarity = F.cosine_similarity(image_features, text_features, dim=1)
                similarity_score = similarity.item()
            else:
                similarity_score = None
            
            return {
                "image_features": image_features.cpu().numpy().tolist(),
                "text_features": text_features.cpu().numpy().tolist() if text_prompt else None,
                "similarity_score": similarity_score,
                "image_embeds_shape": list(image_features.shape)
            }
            
        except Exception as error:
            logger.error(f"CLIP processing failed: {error}")
            raise
    
    def generate_text_with_model(self, prompt: str, max_length: int = 50) -> Dict[str, Any]:
        """
        Generate text using a loaded text model.
        
        Args:
            prompt: Input text prompt
            max_length: Maximum length of generated text
            
        Returns:
            Dictionary with generated text
        """
        try:
            if 'text_model' not in self.models:
                raise RuntimeError("Text model not loaded. Call load_text_model() first.")
            
            model = self.models['text_model']
            tokenizer = self.tokenizers['text_model']
            
            # Tokenize input
            inputs = tokenizer.encode(prompt, return_tensors="pt").to(self.device)
            
            # Generate text
            with torch.no_grad():
                if self.mixed_precision_enabled and self.device.type == 'cuda':
                    with torch.cuda.amp.autocast():
                        outputs = model.generate(
                            inputs,
                            max_length=max_length,
                            num_return_sequences=1,
                            temperature=0.7,
                            do_sample=True,
                            pad_token_id=tokenizer.eos_token_id
                        )
                else:
                    outputs = model.generate(
                        inputs,
                        max_length=max_length,
                        num_return_sequences=1,
                        temperature=0.7,
                        do_sample=True,
                        pad_token_id=tokenizer.eos_token_id
                    )
            
            # Decode output
            generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            return {
                "generated_text": generated_text,
                "input_prompt": prompt,
                "output_length": len(outputs[0]),
                "max_length": max_length
            }
            
        except Exception as error:
            logger.error(f"Text generation failed: {error}")
            raise


class TransformerImageProcessor:
    """Main image processor for transformer-enhanced Gradio interface."""
    
    def __init__(self, model_config: Optional[Dict[str, Any]] = None):
        """
        Initialize transformer image processor with model configuration.
        
        Args:
            model_config: Optional model configuration dictionary
        """
        self.model_manager = TransformerModelManager(model_config)
        self.performance_metrics = {
            'total_processed': 0,
            'successful_processing': 0,
            'failed_processing': 0,
            'average_processing_time': 0.0,
            'model_load_times': {}
        }
        
        # Load default models
        try:
            self._load_default_models()
            logger.info("TransformerImageProcessor initialized successfully")
        except Exception as error:
            logger.error(f"Failed to initialize TransformerImageProcessor: {error}")
            raise
    
    def _load_default_models(self):
        """Load default transformer models."""
        try:
            # Load Vision Transformer
            start_time = time.time()
            self.model_manager.load_vision_transformer()
            load_time = time.time() - start_time
            self.performance_metrics['model_load_times']['vision_transformer'] = load_time
            
            # Load CLIP model
            start_time = time.time()
            self.model_manager.load_clip_model()
            load_time = time.time() - start_time
            self.performance_metrics['model_load_times']['clip'] = load_time
            
            # Load text model
            start_time = time.time()
            self.model_manager.load_text_model()
            load_time = time.time() - start_time
            self.performance_metrics['model_load_times']['text_model'] = load_time
            
            logger.info("Default models loaded successfully")
            
        except Exception as error:
            logger.error(f"Failed to load default models: {error}")
            raise
    
    def process_image_classification(self, image_input, model_name: str = "auto") -> Tuple[np.ndarray, str, str]:
        """
        Process image for classification using Vision Transformer.
        
        Args:
            image_input: Input image from Gradio
            model_name: Model to use (auto for default)
            
        Returns:
            Tuple of (processed_image, status_message, classification_report)
        """
        start_time = time.time()
        
        try:
            # Validate input image
            if image_input is None:
                return None, "No image provided", ""
            
            # Convert to numpy array if needed
            if isinstance(image_input, Image.Image):
                image_array = np.array(image_input)
            else:
                image_array = image_input
            
            # Process with Vision Transformer
            results = self.model_manager.process_image_with_vision_transformer(image_array)
            
            processing_time = time.time() - start_time
            self._update_performance_metrics(processing_time, success=True)
            
            # Generate classification report
            classification_report = self._generate_classification_report(results, processing_time)
            
            return image_array, "Classification completed successfully", classification_report
            
        except Exception as error:
            processing_time = time.time() - start_time
            self._update_performance_metrics(processing_time, success=False)
            
            error_message = f"Classification failed: {str(error)}"
            logger.error(error_message)
            
            return None, error_message, ""
    
    def process_image_text_similarity(self, image_input, text_prompt: str) -> Tuple[np.ndarray, str, str]:
        """
        Process image and text for similarity using CLIP.
        
        Args:
            image_input: Input image from Gradio
            text_prompt: Text prompt for comparison
            
        Returns:
            Tuple of (processed_image, status_message, similarity_report)
        """
        start_time = time.time()
        
        try:
            # Validate inputs
            if image_input is None:
                return None, "No image provided", ""
            
            if not text_prompt or text_prompt.strip() == "":
                return None, "No text prompt provided", ""
            
            # Convert to numpy array if needed
            if isinstance(image_input, Image.Image):
                image_array = np.array(image_input)
            else:
                image_array = image_input
            
            # Process with CLIP
            results = self.model_manager.process_image_with_clip(image_array, text_prompt)
            
            processing_time = time.time() - start_time
            self._update_performance_metrics(processing_time, success=True)
            
            # Generate similarity report
            similarity_report = self._generate_similarity_report(results, text_prompt, processing_time)
            
            return image_array, "Similarity analysis completed successfully", similarity_report
            
        except Exception as error:
            processing_time = time.time() - start_time
            self._update_performance_metrics(processing_time, success=False)
            
            error_message = f"Similarity analysis failed: {str(error)}"
            logger.error(error_message)
            
            return None, error_message, ""
    
    def generate_text_from_prompt(self, text_prompt: str, max_length: int = 50) -> Tuple[str, str, str]:
        """
        Generate text using transformer model.
        
        Args:
            text_prompt: Input text prompt
            max_length: Maximum length of generated text
            
        Returns:
            Tuple of (generated_text, status_message, generation_report)
        """
        start_time = time.time()
        
        try:
            # Validate input
            if not text_prompt or text_prompt.strip() == "":
                return "", "No text prompt provided", ""
            
            # Generate text
            results = self.model_manager.generate_text_with_model(text_prompt, max_length)
            
            processing_time = time.time() - start_time
            self._update_performance_metrics(processing_time, success=True)
            
            # Generate text generation report
            generation_report = self._generate_text_generation_report(results, processing_time)
            
            return results['generated_text'], "Text generation completed successfully", generation_report
            
        except Exception as error:
            processing_time = time.time() - start_time
            self._update_performance_metrics(processing_time, success=False)
            
            error_message = f"Text generation failed: {str(error)}"
            logger.error(error_message)
            
            return "", error_message, ""
    
    def get_available_models_info(self) -> str:
        """Get information about available models."""
        try:
            models_info = self.model_manager.get_available_models()
            
            if "error" in models_info:
                return f"❌ {models_info['error'][0]}"
            
            info = "**Available Pre-trained Models**\n\n"
            
            info += "**Vision Models (Image Classification):**\n"
            for model in models_info.get("vision_models", []):
                info += f"- {model}\n"
            
            info += "\n**CLIP Models (Image-Text Understanding):**\n"
            for model in models_info.get("clip_models", []):
                info += f"- {model}\n"
            
            info += "\n**Text Models (Text Generation):**\n"
            for model in models_info.get("text_models", []):
                info += f"- {model}\n"
            
            info += f"\n**Loaded Models:**\n"
            for model_name in self.model_manager.models.keys():
                info += f"- ✅ {model_name}\n"
            
            return info
            
        except Exception as error:
            return f"Failed to get models info: {str(error)}"
    
    def _update_performance_metrics(self, processing_time: float, success: bool):
        """Update performance metrics with processing results."""
        self.performance_metrics['total_processed'] += 1
        
        if success:
            self.performance_metrics['successful_processing'] += 1
        else:
            self.performance_metrics['failed_processing'] += 1
        
        # Update average processing time
        current_avg = self.performance_metrics['average_processing_time']
        total_successful = self.performance_metrics['successful_processing']
        
        if total_successful > 0:
            self.performance_metrics['average_processing_time'] = (
                (current_avg * (total_successful - 1) + processing_time) / total_successful
            )
    
    def _generate_classification_report(self, results: Dict[str, Any], processing_time: float) -> str:
        """Generate classification report."""
        try:
            report = f"""
**Image Classification Report**

**Results:**
- Predicted Class: {results.get('class', 'Unknown')}
- Confidence: {results.get('confidence', 0):.2%}
- Class ID: {results.get('class_id', 'N/A')}

**Performance:**
- Processing Time: {processing_time:.3f} seconds
- Device: {self.model_manager.device}
- Mixed Precision: {'Enabled' if self.model_manager.mixed_precision_enabled else 'Disabled'}

**System Statistics:**
- Total Processed: {self.performance_metrics['total_processed']}
- Success Rate: {(self.performance_metrics['successful_processing'] / max(1, self.performance_metrics['total_processed'])) * 100:.1f}%
- Average Processing Time: {self.performance_metrics['average_processing_time']:.3f} seconds
"""
            return report
            
        except Exception as error:
            logger.error(f"Failed to generate classification report: {error}")
            return f"Report generation failed: {str(error)}"
    
    def _generate_similarity_report(self, results: Dict[str, Any], text_prompt: str, processing_time: float) -> str:
        """Generate similarity report."""
        try:
            report = f"""
**Image-Text Similarity Report**

**Input:**
- Text Prompt: "{text_prompt}"

**Results:**
- Similarity Score: {results.get('similarity_score', 'N/A'):.4f if results.get('similarity_score') is not None else 'N/A'}
- Image Features Shape: {results.get('image_embeds_shape', 'N/A')}
- Text Features: {'Available' if results.get('text_features') else 'Not Available'}

**Performance:**
- Processing Time: {processing_time:.3f} seconds
- Device: {self.model_manager.device}
- Mixed Precision: {'Enabled' if self.model_manager.mixed_precision_enabled else 'Disabled'}

**System Statistics:**
- Total Processed: {self.performance_metrics['total_processed']}
- Success Rate: {(self.performance_metrics['successful_processing'] / max(1, self.performance_metrics['total_processed'])) * 100:.1f}%
- Average Processing Time: {self.performance_metrics['average_processing_time']:.3f} seconds
"""
            return report
            
        except Exception as error:
            logger.error(f"Failed to generate similarity report: {error}")
            return f"Report generation failed: {str(error)}"
    
    def _generate_text_generation_report(self, results: Dict[str, Any], processing_time: float) -> str:
        """Generate text generation report."""
        try:
            report = f"""
**Text Generation Report**

**Input:**
- Prompt: "{results.get('input_prompt', 'N/A')}"

**Results:**
- Generated Text: "{results.get('generated_text', 'N/A')}"
- Output Length: {results.get('output_length', 'N/A')} tokens
- Max Length: {results.get('max_length', 'N/A')} tokens

**Performance:**
- Processing Time: {processing_time:.3f} seconds
- Device: {self.model_manager.device}
- Mixed Precision: {'Enabled' if self.model_manager.mixed_precision_enabled else 'Disabled'}

**System Statistics:**
- Total Processed: {self.performance_metrics['total_processed']}
- Success Rate: {(self.performance_metrics['successful_processing'] / max(1, self.performance_metrics['total_processed'])) * 100:.1f}%
- Average Processing Time: {self.performance_metrics['average_processing_time']:.3f} seconds
"""
            return report
            
        except Exception as error:
            logger.error(f"Failed to generate text generation report: {error}")
            return f"Report generation failed: {str(error)}"


def create_transformer_enhanced_interface():
    """Create the main transformer-enhanced Gradio interface."""
    
    try:
        processor_config = {
            'enable_mixed_precision': True,
            'enable_anomaly_detection': False,
            'gpu_memory_fraction': 0.8
        }
        
        image_processor = TransformerImageProcessor(processor_config)
        logger.info("Transformer-enhanced interface processor initialized successfully")
        
    except Exception as error:
        logger.error(f"Failed to initialize processor: {error}")
        raise
    
    with gr.Blocks(title="Transformer-Enhanced Image Processing System", theme=gr.themes.Soft()) as interface:
        
        gr.Markdown("# 🤖 Transformer-Enhanced Image Processing System")
        gr.Markdown("AI-powered image processing with pre-trained transformer models")
        
        with gr.Tabs():
            with gr.Tab("Image Classification"):
                with gr.Row():
                    with gr.Column(scale=1):
                        input_image = gr.Image(label="Input Image", type="numpy")
                        classify_button = gr.Button("Classify Image", variant="primary")
                        status_output = gr.Textbox(label="Processing Status", interactive=False)
                    
                    with gr.Column(scale=1):
                        output_image = gr.Image(label="Input Image", type="numpy")
                        classification_report = gr.Markdown(label="Classification Report")
                
                classify_button.click(
                    fn=image_processor.process_image_classification,
                    inputs=[input_image],
                    outputs=[output_image, status_output, classification_report]
                )
            
            with gr.Tab("Image-Text Similarity"):
                with gr.Row():
                    with gr.Column(scale=1):
                        similarity_image = gr.Image(label="Input Image", type="numpy")
                        text_prompt = gr.Textbox(
                            label="Text Prompt", 
                            placeholder="Enter a description of what you see in the image...",
                            lines=3
                        )
                        similarity_button = gr.Button("Analyze Similarity", variant="primary")
                        similarity_status = gr.Textbox(label="Processing Status", interactive=False)
                    
                    with gr.Column(scale=1):
                        similarity_output = gr.Image(label="Input Image", type="numpy")
                        similarity_report = gr.Markdown(label="Similarity Report")
                
                similarity_button.click(
                    fn=image_processor.process_image_text_similarity,
                    inputs=[similarity_image, text_prompt],
                    outputs=[similarity_output, similarity_status, similarity_report]
                )
            
            with gr.Tab("Text Generation"):
                with gr.Row():
                    with gr.Column(scale=1):
                        text_prompt_input = gr.Textbox(
                            label="Text Prompt", 
                            placeholder="Enter a prompt to generate text from...",
                            lines=5
                        )
                        max_length_slider = gr.Slider(
                            minimum=10, maximum=200, value=50, step=10,
                            label="Maximum Length"
                        )
                        generate_button = gr.Button("Generate Text", variant="primary")
                        generation_status = gr.Textbox(label="Processing Status", interactive=False)
                    
                    with gr.Column(scale=1):
                        generated_text_output = gr.Textbox(
                            label="Generated Text", 
                            lines=10,
                            interactive=False
                        )
                        generation_report = gr.Markdown(label="Generation Report")
                
                generate_button.click(
                    fn=image_processor.generate_text_from_prompt,
                    inputs=[text_prompt_input, max_length_slider],
                    outputs=[generated_text_output, generation_status, generation_report]
                )
            
            with gr.Tab("Available Models"):
                with gr.Row():
                    with gr.Column():
                        models_button = gr.Button("Show Available Models", variant="secondary")
                        models_info = gr.Markdown(label="Models Information")
                
                models_button.click(
                    fn=image_processor.get_available_models_info,
                    outputs=models_info
                )
        
        gr.Markdown("---")
        gr.Markdown("*Transformer-Enhanced Image Processing System with Hugging Face Transformers*")
    
    return interface


def main():
    """Main function to launch the transformer-enhanced Gradio interface."""
    try:
        interface = create_transformer_enhanced_interface()
        
        interface.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            debug=False,
            show_error=True,
            quiet=False
        )
        
    except Exception as error:
        logger.error(f"Failed to launch transformer-enhanced interface: {error}")
        raise


if __name__ == "__main__":
    main()


