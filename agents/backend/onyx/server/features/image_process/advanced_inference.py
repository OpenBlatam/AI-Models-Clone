import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
import logging
import argparse
import os
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List, Union
import time
import json
import numpy as np
from PIL import Image
import cv2
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from queue import Queue
import gc

# Import our custom modules
from main_integration import AdvancedImageProcessor, ImageProcessingModel
from advanced_loss_functions import AdvancedLossFunctions
from performance_monitor import PerformanceMonitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class QualityAssessment:
    """Advanced quality assessment for processed images"""
    
    def __init__(self, device: str = 'auto'):
        self.device = torch.device(device if device != 'auto' else
                                  ('cuda' if torch.cuda.is_available() else 'cpu'))
        self.loss_functions = AdvancedLossFunctions(device=self.device)
    
    def assess_image_quality(self, 
                           original: torch.Tensor, 
                           processed: torch.Tensor) -> Dict[str, float]:
        """Comprehensive image quality assessment"""
        
        # Ensure tensors are on same device
        original = original.to(self.device)
        processed = processed.to(self.device)
        
        # Calculate various quality metrics
        metrics = {}
        
        # PSNR (Peak Signal-to-Noise Ratio)
        metrics['psnr'] = self._calculate_psnr(original, processed)
        
        # SSIM (Structural Similarity Index)
        metrics['ssim'] = self._calculate_ssim(original, processed)
        
        # Frequency domain quality
        metrics['frequency_quality'] = self._calculate_frequency_quality(original, processed)
        
        # Edge preservation quality
        metrics['edge_quality'] = self._calculate_edge_quality(original, processed)
        
        # Color fidelity
        metrics['color_fidelity'] = self._calculate_color_fidelity(original, processed)
        
        # Overall quality score (weighted average)
        weights = {
            'psnr': 0.25,
            'ssim': 0.30,
            'frequency_quality': 0.20,
            'edge_quality': 0.15,
            'color_fidelity': 0.10
        }
        
        metrics['overall_quality'] = sum(
            metrics[key] * weights[key] for key in weights.keys()
        )
        
        return metrics
    
    def _calculate_psnr(self, original: torch.Tensor, processed: torch.Tensor) -> float:
        """Calculate PSNR"""
        mse = F.mse_loss(original, processed)
        if mse == 0:
            return float('inf')
        max_pixel = 1.0
        psnr = 20 * torch.log10(max_pixel / torch.sqrt(mse))
        return psnr.item()
    
    def _calculate_ssim(self, original: torch.Tensor, processed: torch.Tensor) -> float:
        """Calculate SSIM using our loss function"""
        ssim_loss = self.loss_functions.structural_similarity_loss(processed, original)
        # Convert loss to similarity score (1 - loss)
        return (1.0 - ssim_loss.item())
    
    def _calculate_frequency_quality(self, original: torch.Tensor, processed: torch.Tensor) -> float:
        """Calculate frequency domain quality"""
        freq_loss = self.loss_functions.frequency_domain_loss(processed, original)
        # Convert loss to quality score (1 - normalized loss)
        return max(0.0, 1.0 - freq_loss.item() / 10.0)  # Normalize by expected max loss
    
    def _calculate_edge_quality(self, original: torch.Tensor, processed: torch.Tensor) -> float:
        """Calculate edge preservation quality"""
        edge_loss = self.loss_functions.edge_preserving_loss(processed, original)
        # Convert loss to quality score
        return max(0.0, 1.0 - edge_loss.item() / 5.0)
    
    def _calculate_color_fidelity(self, original: torch.Tensor, processed: torch.Tensor) -> float:
        """Calculate color fidelity"""
        # Calculate color histogram similarity
        orig_hist = self._calculate_color_histogram(original)
        proc_hist = self._calculate_color_histogram(processed)
        
        # Histogram intersection
        intersection = torch.minimum(orig_hist, proc_hist).sum()
        union = torch.maximum(orig_hist, proc_hist).sum()
        
        if union == 0:
            return 1.0
        
        return (intersection / union).item()
    
    def _calculate_color_histogram(self, image: torch.Tensor, bins: int = 256) -> torch.Tensor:
        """Calculate color histogram for each channel"""
        # Convert to 0-255 range
        image_255 = (image * 255).clamp(0, 255).long()
        
        histograms = []
        for channel in range(image.shape[1]):
            hist = torch.histc(image_255[:, channel], bins=bins, min=0, max=255)
            hist = hist / hist.sum()  # Normalize
            histograms.append(hist)
        
        return torch.stack(histograms)

class BatchProcessor:
    """Efficient batch processing for multiple images"""
    
    def __init__(self, 
                 model: ImageProcessingModel,
                 device: str = 'auto',
                 batch_size: int = 8,
                 max_workers: int = 4):
        
        self.model = model
        self.device = torch.device(device if device != 'auto' else
                                  ('cuda' if torch.cuda.is_available() else 'cpu'))
        self.batch_size = batch_size
        self.max_workers = max_workers
        
        # Move model to device
        self.model.to(self.device)
        self.model.eval()
        
        # Quality assessment
        self.quality_assessor = QualityAssessment(device=self.device)
        
        # Performance monitoring
        self.performance_monitor = PerformanceMonitor(monitor_interval=5.0)
        
        logger.info(f"BatchProcessor initialized on {self.device}")
    
    def process_batch(self, 
                     image_paths: List[str],
                     output_dir: str,
                     save_quality_report: bool = True) -> Dict[str, Any]:
        """Process a batch of images"""
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Start performance monitoring
        self.performance_monitor.start_monitoring()
        
        results = {
            'processed_images': [],
            'quality_metrics': [],
            'processing_times': [],
            'errors': []
        }
        
        # Process images in batches
        for i in range(0, len(image_paths), self.batch_size):
            batch_paths = image_paths[i:i + self.batch_size]
            batch_results = self._process_single_batch(batch_paths, output_dir)
            
            # Merge results
            results['processed_images'].extend(batch_results['processed_images'])
            results['quality_metrics'].extend(batch_results['quality_metrics'])
            results['processing_times'].extend(batch_results['processing_times'])
            results['errors'].extend(batch_results['errors'])
            
            # Memory cleanup
            if self.device.type == 'cuda':
                torch.cuda.empty_cache()
        
        # Stop monitoring
        self.performance_monitor.stop_monitoring()
        
        # Generate summary
        results['summary'] = self._generate_summary(results)
        
        # Save quality report
        if save_quality_report:
            self._save_quality_report(results, output_dir)
        
        return results
    
    def _process_single_batch(self, 
                             image_paths: List[str], 
                             output_dir: str) -> Dict[str, Any]:
        """Process a single batch of images"""
        
        batch_results = {
            'processed_images': [],
            'quality_metrics': [],
            'processing_times': [],
            'errors': []
        }
        
        try:
            # Load and preprocess images
            images, valid_paths = self._load_batch_images(image_paths)
            
            if len(images) == 0:
                return batch_results
            
            # Process batch
            start_time = time.time()
            
            with torch.no_grad():
                processed_images = self.model(images.to(self.device))
            
            processing_time = time.time() - start_time
            
            # Post-process and save
            for i, (image_path, processed_image) in enumerate(zip(valid_paths, processed_images)):
                try:
                    # Save processed image
                    output_path = self._save_processed_image(
                        processed_image, image_path, output_dir
                    )
                    
                    # Calculate quality metrics
                    original_image = images[i].unsqueeze(0)
                    quality_metrics = self.quality_assessor.assess_image_quality(
                        original_image, processed_image.unsqueeze(0)
                    )
                    
                    # Store results
                    batch_results['processed_images'].append(str(output_path))
                    batch_results['quality_metrics'].append(quality_metrics)
                    batch_results['processing_times'].append(processing_time / len(valid_paths))
                    
                except Exception as e:
                    error_msg = f"Error processing {image_path}: {str(e)}"
                    batch_results['errors'].append(error_msg)
                    logger.error(error_msg)
            
        except Exception as e:
            error_msg = f"Batch processing error: {str(e)}"
            batch_results['errors'].append(error_msg)
            logger.error(error_msg)
        
        return batch_results
    
    def _load_batch_images(self, image_paths: List[str]) -> Tuple[torch.Tensor, List[str]]:
        """Load and preprocess a batch of images"""
        
        images = []
        valid_paths = []
        
        for image_path in image_paths:
            try:
                # Load image
                image = Image.open(image_path).convert('RGB')
                
                # Preprocess
                transform = self._get_preprocessing_transform()
                image_tensor = transform(image)
                
                images.append(image_tensor)
                valid_paths.append(image_path)
                
            except Exception as e:
                logger.warning(f"Failed to load {image_path}: {e}")
                continue
        
        if len(images) == 0:
            return torch.empty(0), []
        
        # Stack into batch
        batch_tensor = torch.stack(images)
        return batch_tensor, valid_paths
    
    def _get_preprocessing_transform(self):
        """Get preprocessing transform"""
        import torchvision.transforms as transforms
        
        return transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
    
    def _save_processed_image(self, 
                             processed_tensor: torch.Tensor, 
                             original_path: str, 
                             output_dir: str) -> Path:
        """Save processed image"""
        
        # Post-process
        processed_tensor = processed_tensor.cpu()
        processed_tensor = torch.clamp(processed_tensor, 0, 1)
        
        # Convert to PIL
        import torchvision.transforms as transforms
        processed_image = transforms.ToPILImage()(processed_tensor)
        
        # Generate output path
        original_filename = Path(original_path).stem
        output_path = Path(output_dir) / f"{original_filename}_processed.png"
        
        # Save
        processed_image.save(output_path)
        
        return output_path
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate processing summary"""
        
        if not results['quality_metrics']:
            return {'error': 'No successful processing'}
        
        # Calculate average metrics
        avg_metrics = {}
        for metric in results['quality_metrics'][0].keys():
            values = [qm[metric] for qm in results['quality_metrics']]
            avg_metrics[metric] = {
                'mean': np.mean(values),
                'std': np.std(values),
                'min': np.min(values),
                'max': np.max(values)
            }
        
        summary = {
            'total_images': len(results['processed_images']),
            'successful_processing': len(results['processed_images']),
            'errors': len(results['errors']),
            'average_processing_time': np.mean(results['processing_times']),
            'quality_metrics': avg_metrics
        }
        
        return summary
    
    def _save_quality_report(self, results: Dict[str, Any], output_dir: str):
        """Save quality report to JSON"""
        
        report_path = Path(output_dir) / "quality_report.json"
        
        # Convert numpy types to native Python types for JSON serialization
        def convert_numpy_types(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {key: convert_numpy_types(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            else:
                return obj
        
        serializable_results = convert_numpy_types(results)
        
        with open(report_path, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        
        logger.info(f"Quality report saved to {report_path}")

class RealTimeProcessor:
    """Real-time image processing with streaming capabilities"""
    
    def __init__(self, 
                 model: ImageProcessingModel,
                 device: str = 'auto',
                 buffer_size: int = 10):
        
        self.model = model
        self.device = torch.device(device if device != 'auto' else
                                  ('cuda' if torch.cuda.is_available() else 'cpu'))
        self.buffer_size = buffer_size
        
        # Move model to device
        self.model.to(self.device)
        self.model.eval()
        
        # Processing queue
        self.input_queue = Queue(maxsize=buffer_size)
        self.output_queue = Queue(maxsize=buffer_size)
        
        # Processing thread
        self.processing_thread = None
        self.running = False
        
        # Performance monitoring
        self.performance_monitor = PerformanceMonitor(monitor_interval=1.0)
        
        logger.info(f"RealTimeProcessor initialized on {self.device}")
    
    def start_processing(self):
        """Start real-time processing"""
        if self.running:
            logger.warning("Processing already running")
            return
        
        self.running = True
        self.processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
        self.processing_thread.start()
        
        # Start performance monitoring
        self.performance_monitor.start_monitoring()
        
        logger.info("Real-time processing started")
    
    def stop_processing(self):
        """Stop real-time processing"""
        self.running = False
        
        if self.processing_thread:
            self.processing_thread.join()
        
        # Stop monitoring
        self.performance_monitor.stop_monitoring()
        
        logger.info("Real-time processing stopped")
    
    def add_image(self, image: Union[str, Image.Image, torch.Tensor], 
                  image_id: Optional[str] = None) -> bool:
        """Add image to processing queue"""
        
        if image_id is None:
            image_id = str(time.time())
        
        try:
            # Preprocess image if needed
            if isinstance(image, str):
                image = Image.open(image).convert('RGB')
            
            if isinstance(image, Image.Image):
                image = self._preprocess_image(image)
            
            # Add to queue
            self.input_queue.put((image_id, image), timeout=1.0)
            return True
            
        except Exception as e:
            logger.error(f"Failed to add image {image_id}: {e}")
            return False
    
    def get_processed_image(self, timeout: float = 1.0) -> Optional[Tuple[str, torch.Tensor]]:
        """Get processed image from output queue"""
        
        try:
            return self.input_queue.get(timeout=timeout)
        except:
            return None
    
    def _processing_loop(self):
        """Main processing loop"""
        
        while self.running:
            try:
                # Get image from input queue
                try:
                    image_id, image = self.input_queue.get(timeout=0.1)
                except:
                    continue
                
                # Process image
                start_time = time.time()
                
                with torch.no_grad():
                    processed_image = self.model(image.unsqueeze(0).to(self.device))
                    processed_image = processed_image.squeeze(0)
                
                processing_time = time.time() - start_time
                
                # Add to output queue
                try:
                    self.output_queue.put((image_id, processed_image), timeout=1.0)
                    
                    # Log performance
                    logger.debug(f"Processed {image_id} in {processing_time:.3f}s")
                    
                except:
                    logger.warning(f"Output queue full, dropping {image_id}")
                
            except Exception as e:
                logger.error(f"Processing error: {e}")
                continue
    
    def _preprocess_image(self, image: Image.Image) -> torch.Tensor:
        """Preprocess PIL image"""
        import torchvision.transforms as transforms
        
        transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
        
        return transform(image)

class AdvancedInferenceSystem:
    """Main inference system integrating all components"""
    
    def __init__(self, 
                 model_path: str,
                 device: str = 'auto',
                 config: Optional[Dict[str, Any]] = None):
        
        self.device = torch.device(device if device != 'auto' else
                                  ('cuda' if torch.cuda.is_available() else 'cpu'))
        
        # Load model
        self.model = self._load_model(model_path)
        
        # Initialize components
        self.batch_processor = BatchProcessor(
            self.model, device=self.device
        )
        
        self.real_time_processor = RealTimeProcessor(
            self.model, device=self.device
        )
        
        self.quality_assessor = QualityAssessment(device=self.device)
        
        # Configuration
        self.config = config or {}
        
        logger.info("AdvancedInferenceSystem initialized")
    
    def _load_model(self, model_path: str) -> ImageProcessingModel:
        """Load trained model from checkpoint"""
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        # Load checkpoint
        checkpoint = torch.load(model_path, map_location=self.device)
        
        # Extract model configuration
        if 'config' in checkpoint:
            model_config = checkpoint['config']
        else:
            model_config = {
                'input_channels': 3,
                'output_channels': 3,
                'base_channels': 64,
                'num_blocks': 8
            }
        
        # Create model
        model = ImageProcessingModel(**model_config)
        
        # Load weights
        if 'model_state_dict' in checkpoint:
            model.load_state_dict(checkpoint['model_state_dict'])
        else:
            model.load_state_dict(checkpoint)
        
        logger.info(f"Model loaded from {model_path}")
        return model
    
    def process_single_image(self, 
                           image_path: str, 
                           output_path: str,
                           assess_quality: bool = True) -> Dict[str, Any]:
        """Process a single image"""
        
        try:
            # Load image
            image = Image.open(image_path).convert('RGB')
            
            # Preprocess
            transform = self.batch_processor._get_preprocessing_transform()
            input_tensor = transform(image).unsqueeze(0)
            
            # Process
            start_time = time.time()
            
            with torch.no_grad():
                output_tensor = self.model(input_tensor.to(self.device))
            
            processing_time = time.time() - start_time
            
            # Post-process
            output_tensor = output_tensor.squeeze(0).cpu()
            output_tensor = torch.clamp(output_tensor, 0, 1)
            
            # Save
            import torchvision.transforms as transforms
            output_image = transforms.ToPILImage()(output_tensor)
            output_image.save(output_path)
            
            # Quality assessment
            quality_metrics = None
            if assess_quality:
                quality_metrics = self.quality_assessor.assess_image_quality(
                    input_tensor, output_tensor.unsqueeze(0)
                )
            
            results = {
                'input_path': image_path,
                'output_path': output_path,
                'processing_time': processing_time,
                'quality_metrics': quality_metrics,
                'success': True
            }
            
            logger.info(f"Image processed successfully: {output_path}")
            return results
            
        except Exception as e:
            error_msg = f"Failed to process {image_path}: {str(e)}"
            logger.error(error_msg)
            
            return {
                'input_path': image_path,
                'output_path': output_path,
                'processing_time': 0.0,
                'quality_metrics': None,
                'success': False,
                'error': str(e)
            }
    
    def process_directory(self, 
                         input_dir: str, 
                         output_dir: str,
                         batch_size: int = 8,
                         save_quality_report: bool = True) -> Dict[str, Any]:
        """Process all images in a directory"""
        
        # Get image files
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
        image_paths = []
        
        input_path = Path(input_dir)
        for ext in image_extensions:
            image_paths.extend(input_path.glob(f"*{ext}"))
            image_paths.extend(input_path.glob(f"*{ext.upper()}"))
        
        image_paths = [str(p) for p in image_paths]
        
        if not image_paths:
            logger.warning(f"No images found in {input_dir}")
            return {'error': 'No images found'}
        
        logger.info(f"Found {len(image_paths)} images to process")
        
        # Process using batch processor
        return self.batch_processor.process_batch(
            image_paths, output_dir, save_quality_report
        )
    
    def start_real_time_processing(self):
        """Start real-time processing"""
        self.real_time_processor.start_processing()
    
    def stop_real_time_processing(self):
        """Stop real-time processing"""
        self.real_time_processor.stop_processing()
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        return {
            'device': str(self.device),
            'model_parameters': sum(p.numel() for p in self.model.parameters()),
            'performance_metrics': self.batch_processor.performance_monitor.get_metrics_summary()
        }

def main():
    """Main inference script"""
    parser = argparse.ArgumentParser(description='Advanced Image Processing Inference')
    
    # Input/Output
    parser.add_argument('--input', type=str, required=True, 
                       help='Input image path or directory')
    parser.add_argument('--output', type=str, required=True, 
                       help='Output path or directory')
    parser.add_argument('--model', type=str, required=True, 
                       help='Path to trained model checkpoint')
    
    # Processing options
    parser.add_argument('--mode', type=str, default='single', 
                       choices=['single', 'batch', 'realtime'],
                       help='Processing mode')
    parser.add_argument('--batch_size', type=int, default=8, 
                       help='Batch size for batch processing')
    parser.add_argument('--assess_quality', action='store_true',
                       help='Assess output image quality')
    parser.add_argument('--save_quality_report', action='store_true',
                       help='Save quality assessment report')
    
    # System options
    parser.add_argument('--device', type=str, default='auto', 
                       help='Device to use')
    
    args = parser.parse_args()
    
    try:
        # Initialize inference system
        inference_system = AdvancedInferenceSystem(
            model_path=args.model,
            device=args.device
        )
        
        # Process based on mode
        if args.mode == 'single':
            if os.path.isfile(args.input):
                results = inference_system.process_single_image(
                    args.input, args.output, args.assess_quality
                )
                print(f"Processing results: {results}")
            else:
                print(f"Input path is not a file: {args.input}")
        
        elif args.mode == 'batch':
            if os.path.isdir(args.input):
                results = inference_system.process_directory(
                    args.input, args.output, args.batch_size, args.save_quality_report
                )
                print(f"Batch processing results: {results}")
            else:
                print(f"Input path is not a directory: {args.input}")
        
        elif args.mode == 'realtime':
            print("Starting real-time processing...")
            inference_system.start_real_time_processing()
            
            try:
                # Keep running until interrupted
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("Stopping real-time processing...")
                inference_system.stop_real_time_processing()
        
        # Print performance summary
        summary = inference_system.get_performance_summary()
        print(f"\nPerformance Summary: {summary}")
        
    except Exception as e:
        logger.error(f"Inference failed: {e}")
        raise

if __name__ == "__main__":
    main()


