"""
Fast Quality Inspector with Optimizations
"""

import torch
import numpy as np
import cv2
from typing import Optional, Dict, Union
import logging
from concurrent.futures import ThreadPoolExecutor
import time

from ..config.camera_config import CameraConfig
from ..config.detection_config import DetectionConfig
from ..core.models.optimized_models import create_fast_autoencoder, optimize_for_inference
from ..utils.fast_inference import FastPreprocessor, BatchProcessor
from ..services.quality_inspector import QualityInspector

logger = logging.getLogger(__name__)


class FastQualityInspector(QualityInspector):
    """Optimized quality inspector for fast inference"""
    
    def __init__(
        self,
        camera_config: Optional[CameraConfig] = None,
        detection_config: Optional[DetectionConfig] = None,
        use_fast_models: bool = True,
        batch_size: int = 8,
        num_threads: int = 4
    ):
        super().__init__(camera_config, detection_config)
        
        self.use_fast_models = use_fast_models
        self.batch_size = batch_size
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Fast models
        if use_fast_models:
            self.fast_autoencoder = create_fast_autoencoder(device=self.device)
            # Optimize
            example_input = torch.randn(1, 3, 224, 224).to(self.device)
            self.fast_autoencoder = optimize_for_inference(
                self.fast_autoencoder, example_input
            )
        
        # Preprocessor
        self.preprocessor = FastPreprocessor(device=self.device)
        
        # Thread pool for async processing
        self.executor = ThreadPoolExecutor(max_workers=num_threads)
        
        # Cache
        self._cache = {}
        
        logger.info(f"FastQualityInspector initialized on {self.device}")
    
    def inspect_frame_fast(self, image: Optional[np.ndarray] = None) -> Dict:
        """Fast frame inspection"""
        start_time = time.time()
        
        # Capture or load image
        if image is None:
            image = self.camera.capture_frame()
            if image is None:
                return {"success": False, "error": "Failed to capture frame"}
        else:
            image = self.image_utils.load_image(image)
            if image is None:
                return {"success": False, "error": "Failed to load image"}
        
        # Fast preprocessing
        preprocessed = self.preprocessor.preprocess(image)
        
        # Fast inference
        with torch.no_grad():
            if self.use_fast_models and self.fast_autoencoder is not None:
                # Use fast autoencoder
                reconstructed, latent = self.fast_autoencoder(preprocessed)
                recon_error = F.mse_loss(reconstructed, preprocessed, reduction='mean')
                
                # Quick anomaly detection
                anomalies = self._quick_anomaly_detection(image, recon_error.item())
            else:
                # Fallback to standard
                return super().inspect_frame(image)
        
        # Quick defect classification
        defects = self._quick_defect_classification(image, anomalies)
        
        # Calculate quality score
        quality_score = self._calculate_quality_score_fast(anomalies, defects)
        
        inference_time = time.time() - start_time
        
        result = {
            "success": True,
            "quality_score": quality_score,
            "anomalies_detected": len(anomalies),
            "defects_detected": len(defects),
            "anomalies": anomalies,
            "defects": defects,
            "inference_time_ms": inference_time * 1000,
            "summary": {
                "status": "excellent" if quality_score >= 90 else 
                         "good" if quality_score >= 75 else
                         "acceptable" if quality_score >= 60 else "poor"
            }
        }
        
        return result
    
    def _quick_anomaly_detection(self, image: np.ndarray, recon_error: float) -> list:
        """Fast anomaly detection"""
        anomalies = []
        
        if recon_error > 0.1:  # Threshold
            # Quick edge detection
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours[:10]:  # Limit to top 10
                area = cv2.contourArea(contour)
                if area > 100:
                    x, y, w, h = cv2.boundingRect(contour)
                    anomalies.append({
                        "type": "anomaly",
                        "confidence": min(1.0, recon_error * 10),
                        "location": (x, y, w, h),
                        "severity": "high" if recon_error > 0.2 else "medium"
                    })
        
        return anomalies
    
    def _quick_defect_classification(self, image: np.ndarray, anomalies: list) -> list:
        """Fast defect classification"""
        defects = []
        
        for anomaly in anomalies:
            x, y, w, h = anomaly["location"]
            roi = image[y:y+h, x:x+w]
            
            if roi.size > 0:
                # Quick classification based on shape
                gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
                edges = cv2.Canny(gray, 50, 150)
                
                # Simple heuristics
                if np.sum(edges) > 1000:
                    defect_type = "scratch" if w > h * 2 else "crack"
                else:
                    defect_type = "other"
                
                defects.append({
                    "type": defect_type,
                    "confidence": anomaly["confidence"],
                    "location": anomaly["location"],
                    "severity": anomaly["severity"]
                })
        
        return defects
    
    def _calculate_quality_score_fast(self, anomalies: list, defects: list) -> float:
        """Fast quality score calculation"""
        score = 100.0
        
        for anomaly in anomalies:
            if anomaly["severity"] == "high":
                score -= 10
            elif anomaly["severity"] == "medium":
                score -= 5
            else:
                score -= 2
        
        for defect in defects:
            if defect["severity"] == "high":
                score -= 15
            elif defect["severity"] == "medium":
                score -= 8
            else:
                score -= 3
        
        return max(0.0, min(100.0, score))
    
    def inspect_batch_fast(self, images: List[np.ndarray]) -> List[Dict]:
        """Fast batch inspection"""
        if self.use_fast_models and self.fast_autoencoder is not None:
            processor = BatchProcessor(
                self.fast_autoencoder,
                batch_size=self.batch_size,
                device=self.device
            )
            
            # Process in batches
            results = []
            for i in range(0, len(images), self.batch_size):
                batch = images[i:i+self.batch_size]
                batch_results = processor.process_batch(batch)
                
                for img, result in zip(batch, batch_results):
                    # Convert result to inspection format
                    inspection = self.inspect_frame_fast(img)
                    results.append(inspection)
            
            return results
        else:
            return super().inspect_batch(images)
    
    def release(self):
        """Release resources"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True)
        super().release()

