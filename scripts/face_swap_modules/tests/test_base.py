"""
Tests Unitarios - Clases Base
==============================
Tests básicos para validar funcionalidad de clases base y utilidades.
"""

import unittest
import numpy as np
from pathlib import Path
import sys

# Agregar directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from face_swap_modules.base import (
    LandmarkFormatHandler,
    ImageProcessor
)


class TestLandmarkFormatHandler(unittest.TestCase):
    """Tests para LandmarkFormatHandler."""
    
    def setUp(self):
        """Preparar datos de prueba."""
        # Landmarks InsightFace (106 puntos)
        self.landmarks_106 = np.random.rand(106, 2) * 100
        
        # Landmarks face-alignment (68 puntos)
        self.landmarks_68 = np.random.rand(68, 2) * 100
        
        # Landmarks MediaPipe (468 puntos)
        self.landmarks_468 = np.random.rand(468, 2) * 100
        
        # Landmarks inválidos
        self.landmarks_invalid = np.random.rand(10, 2) * 100
    
    def test_get_landmark_format(self):
        """Test detección de formato de landmarks."""
        self.assertEqual(
            LandmarkFormatHandler.get_landmark_format(self.landmarks_106),
            106
        )
        self.assertEqual(
            LandmarkFormatHandler.get_landmark_format(self.landmarks_68),
            68
        )
        self.assertEqual(
            LandmarkFormatHandler.get_landmark_format(self.landmarks_468),
            468
        )
        self.assertIsNone(
            LandmarkFormatHandler.get_landmark_format(self.landmarks_invalid)
        )
    
    def test_is_valid_landmarks(self):
        """Test validación de landmarks."""
        self.assertTrue(
            LandmarkFormatHandler.is_valid_landmarks(self.landmarks_106)
        )
        self.assertTrue(
            LandmarkFormatHandler.is_valid_landmarks(self.landmarks_68)
        )
        self.assertFalse(
            LandmarkFormatHandler.is_valid_landmarks(self.landmarks_invalid)
        )
        self.assertFalse(
            LandmarkFormatHandler.is_valid_landmarks(None)
        )
    
    def test_get_feature_region(self):
        """Test obtención de regiones de características."""
        # Test con formato 106
        left_eye = LandmarkFormatHandler.get_feature_region(
            self.landmarks_106, 'left_eye'
        )
        self.assertIsNotNone(left_eye)
        self.assertEqual(len(left_eye), 6)  # 6 puntos para ojo
        
        # Test con formato 68
        right_eye = LandmarkFormatHandler.get_feature_region(
            self.landmarks_68, 'right_eye'
        )
        self.assertIsNotNone(right_eye)
        self.assertEqual(len(right_eye), 6)
        
        # Test con característica inválida
        invalid = LandmarkFormatHandler.get_feature_region(
            self.landmarks_106, 'invalid_feature'
        )
        self.assertIsNone(invalid)
    
    def test_get_feature_point(self):
        """Test obtención de puntos específicos."""
        # Test con formato 106
        nose_tip = LandmarkFormatHandler.get_feature_point(
            self.landmarks_106, 'nose_tip'
        )
        self.assertIsNotNone(nose_tip)
        self.assertEqual(len(nose_tip), 2)  # [x, y]
        
        # Test con formato 68
        face_center = LandmarkFormatHandler.get_feature_point(
            self.landmarks_68, 'face_center'
        )
        self.assertIsNotNone(face_center)
        self.assertEqual(len(face_center), 2)
        
        # Test con punto inválido
        invalid = LandmarkFormatHandler.get_feature_point(
            self.landmarks_106, 'invalid_point'
        )
        self.assertIsNone(invalid)


class TestImageProcessor(unittest.TestCase):
    """Tests para ImageProcessor."""
    
    def setUp(self):
        """Preparar datos de prueba."""
        self.mask_2d = np.ones((100, 100), dtype=np.float32) * 0.5
        self.mask_uint8 = np.ones((100, 100), dtype=np.uint8) * 128
    
    def test_create_3d_mask(self):
        """Test conversión de máscara 2D a 3D."""
        mask_3d = ImageProcessor.create_3d_mask(self.mask_2d)
        
        self.assertEqual(mask_3d.shape, (100, 100, 3))
        self.assertTrue(np.allclose(mask_3d[:, :, 0], self.mask_2d))
        self.assertTrue(np.allclose(mask_3d[:, :, 1], self.mask_2d))
        self.assertTrue(np.allclose(mask_3d[:, :, 2], self.mask_2d))
    
    def test_convert_to_uint8(self):
        """Test conversión de float a uint8."""
        mask_float = np.array([[0.0, 0.5, 1.0]], dtype=np.float32)
        mask_uint8 = ImageProcessor.convert_to_uint8(mask_float)
        
        self.assertEqual(mask_uint8.dtype, np.uint8)
        self.assertEqual(mask_uint8[0, 0], 0)
        self.assertEqual(mask_uint8[0, 1], 127)  # 0.5 * 255 ≈ 127
        self.assertEqual(mask_uint8[0, 2], 255)
    
    def test_ensure_bounds(self):
        """Test validación de coordenadas."""
        # Coordenadas dentro de límites
        x, y = ImageProcessor.ensure_bounds(50, 50, 100, 100)
        self.assertEqual(x, 50)
        self.assertEqual(y, 50)
        
        # Coordenadas fuera de límites (negativas)
        x, y = ImageProcessor.ensure_bounds(-10, -5, 100, 100)
        self.assertEqual(x, 0)
        self.assertEqual(y, 0)
        
        # Coordenadas fuera de límites (mayores)
        x, y = ImageProcessor.ensure_bounds(150, 200, 100, 100)
        self.assertEqual(x, 100)
        self.assertEqual(y, 100)


class TestIntegration(unittest.TestCase):
    """Tests de integración entre componentes."""
    
    def test_landmark_handler_with_image_processor(self):
        """Test integración LandmarkFormatHandler + ImageProcessor."""
        landmarks = np.random.rand(106, 2) * 100
        
        # Obtener región de ojo
        eye_region = LandmarkFormatHandler.get_feature_region(landmarks, 'left_eye')
        self.assertIsNotNone(eye_region)
        
        # Validar coordenadas
        for point in eye_region:
            x, y = ImageProcessor.ensure_bounds(
                int(point[0]), int(point[1]), 200, 200
            )
            self.assertGreaterEqual(x, 0)
            self.assertGreaterEqual(y, 0)
            self.assertLessEqual(x, 200)
            self.assertLessEqual(y, 200)


if __name__ == '__main__':
    unittest.main()








