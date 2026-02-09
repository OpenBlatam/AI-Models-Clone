"""
Tests de Integración - Face Swap Modules
==========================================
Tests para validar la integración entre módulos.
"""

import unittest
import numpy as np
import cv2
from pathlib import Path

from face_swap_modules import (
    FaceDetector, LandmarkExtractor, FaceAnalyzer,
    ColorCorrector, BlendingEngine, QualityEnhancer,
    PostProcessor, FaceSwapPipeline
)
from face_swap_modules.base import LandmarkFormatHandler, ImageProcessor


class TestIntegration(unittest.TestCase):
    """Tests de integración entre módulos."""
    
    def setUp(self):
        """Configuración inicial."""
        # Crear imagen de prueba sintética
        self.test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        # Agregar "rostro" simulado
        cv2.rectangle(self.test_image, (200, 150), (440, 350), (200, 180, 160), -1)
        
        self.detector = FaceDetector()
        self.extractor = LandmarkExtractor()
        self.analyzer = FaceAnalyzer()
        self.color_corrector = ColorCorrector()
        self.blender = BlendingEngine()
        self.enhancer = QualityEnhancer()
        self.processor = PostProcessor()
    
    def test_detection_to_landmarks(self):
        """Test: Detección → Landmarks."""
        bbox = self.detector.detect(self.test_image)
        if bbox:
            landmarks = self.extractor.detect(self.test_image)
            self.assertIsNotNone(landmarks, "Landmarks deberían extraerse después de detección")
    
    def test_landmarks_to_analysis(self):
        """Test: Landmarks → Análisis."""
        landmarks = self.extractor.detect(self.test_image)
        if landmarks is not None:
            regions = self.analyzer.analyze_face_regions(self.test_image, landmarks)
            self.assertIsInstance(regions, dict, "Regiones deberían ser un diccionario")
    
    def test_color_correction_pipeline(self):
        """Test: Pipeline de corrección de color."""
        source = self.test_image.copy()
        target = cv2.flip(self.test_image, 1)
        mask = np.ones((source.shape[0], source.shape[1]), dtype=np.float32) * 0.8
        
        corrected = self.color_corrector.correct_color_dual(source, target, mask)
        self.assertIsNotNone(corrected, "Corrección de color debería retornar resultado")
        self.assertEqual(corrected.shape, source.shape, "Forma debería mantenerse")
    
    def test_blending_pipeline(self):
        """Test: Pipeline de blending."""
        source = self.test_image.copy()
        target = cv2.flip(self.test_image, 1)
        mask = np.ones((source.shape[0], source.shape[1]), dtype=np.float32) * 0.8
        
        blended = self.blender.blend_advanced(source, target, mask)
        self.assertIsNotNone(blended, "Blending debería retornar resultado")
        self.assertEqual(blended.shape, source.shape, "Forma debería mantenerse")
    
    def test_full_pipeline(self):
        """Test: Pipeline completo."""
        source = self.test_image.copy()
        target = cv2.flip(self.test_image, 1)
        
        pipeline = FaceSwapPipeline(quality_mode='fast')
        
        try:
            result = pipeline.process(source, target)
            self.assertIsNotNone(result, "Pipeline debería retornar resultado")
            self.assertEqual(result.shape, target.shape, "Forma debería coincidir con target")
        except Exception as e:
            # Pipeline puede fallar si no detecta caras, eso está bien
            self.assertIn("cara", str(e).lower() or "landmark", str(e).lower())
    
    def test_landmark_format_handler_integration(self):
        """Test: Integración con LandmarkFormatHandler."""
        landmarks = self.extractor.detect(self.test_image)
        if landmarks is not None:
            format_type = LandmarkFormatHandler.get_landmark_format(landmarks)
            self.assertIsNotNone(format_type, "Formato debería detectarse")
            
            is_valid = LandmarkFormatHandler.is_valid_landmarks(landmarks)
            self.assertTrue(is_valid, "Landmarks deberían ser válidos")
    
    def test_image_processor_integration(self):
        """Test: Integración con ImageProcessor."""
        mask_2d = np.ones((100, 100), dtype=np.float32) * 0.5
        mask_3d = ImageProcessor.create_3d_mask(mask_2d)
        
        self.assertEqual(mask_3d.shape, (100, 100, 3), "Máscara 3D debería tener forma correcta")
        
        mask_uint8 = ImageProcessor.convert_to_uint8(mask_2d)
        self.assertEqual(mask_uint8.dtype, np.uint8, "Debería convertir a uint8")
    
    def test_quality_enhancement_pipeline(self):
        """Test: Pipeline de mejora de calidad."""
        landmarks = self.extractor.detect(self.test_image)
        if landmarks is not None:
            enhanced = self.enhancer.enhance_facial_features(self.test_image, landmarks)
            self.assertIsNotNone(enhanced, "Mejora debería retornar resultado")
            self.assertEqual(enhanced.shape, self.test_image.shape, "Forma debería mantenerse")
    
    def test_post_processing_pipeline(self):
        """Test: Pipeline de post-procesamiento."""
        target = self.test_image.copy()
        mask = np.ones((self.test_image.shape[0], self.test_image.shape[1]), dtype=np.float32)
        
        processed = self.processor.advanced_post_processing(self.test_image, target, mask)
        self.assertIsNotNone(processed, "Post-procesamiento debería retornar resultado")
        self.assertEqual(processed.shape, self.test_image.shape, "Forma debería mantenerse")


class TestPipelineModes(unittest.TestCase):
    """Tests para diferentes modos del pipeline."""
    
    def setUp(self):
        """Configuración inicial."""
        self.test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        cv2.rectangle(self.test_image, (200, 150), (440, 350), (200, 180, 160), -1)
    
    def test_fast_mode(self):
        """Test: Modo fast."""
        pipeline = FaceSwapPipeline(quality_mode='fast')
        self.assertEqual(pipeline.quality_mode, 'fast')
        self.assertFalse(pipeline.use_advanced_enhancements)
    
    def test_high_mode(self):
        """Test: Modo high."""
        pipeline = FaceSwapPipeline(quality_mode='high')
        self.assertEqual(pipeline.quality_mode, 'high')
        self.assertTrue(pipeline.use_quality_enhancement)
    
    def test_ultra_mode(self):
        """Test: Modo ultra."""
        pipeline = FaceSwapPipeline(quality_mode='ultra', use_advanced_enhancements=True)
        self.assertEqual(pipeline.quality_mode, 'ultra')
        self.assertTrue(pipeline.use_advanced_enhancements)


if __name__ == '__main__':
    unittest.main()








