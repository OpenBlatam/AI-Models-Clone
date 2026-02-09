"""
Face Analyzer Module
=====================
Módulo para análisis facial: expresiones, simetría, geometría, características.
Refactorizado para seguir principios SOLID y DRY.
"""

import cv2
import numpy as np
from typing import Optional, Dict

from .base import LandmarkFormatHandler, ImageProcessor


class FaceAnalyzer:
    """Analizador facial para expresiones, simetría, geometría y características."""
    
    def analyze_face_regions(self, image: np.ndarray, landmarks: np.ndarray) -> dict:
        """Analiza regiones faciales (ojos, nariz, boca, mejillas)."""
        regions = {}
        if not LandmarkFormatHandler.is_valid_landmarks(landmarks):
            return regions
        
        try:
            # Use utility class to get feature regions
            left_eye = LandmarkFormatHandler.get_feature_region(landmarks, 'left_eye')
            right_eye = LandmarkFormatHandler.get_feature_region(landmarks, 'right_eye')
            nose = LandmarkFormatHandler.get_feature_region(landmarks, 'nose')
            mouth = LandmarkFormatHandler.get_feature_region(landmarks, 'mouth')
            
            if left_eye is not None:
                regions['left_eye'] = left_eye
            if right_eye is not None:
                regions['right_eye'] = right_eye
            if nose is not None:
                regions['nose'] = nose
            if mouth is not None:
                regions['mouth'] = mouth
            
        except Exception:
            pass
        
        return regions
    
    def analyze_facial_expression(self, landmarks: np.ndarray) -> dict:
        """Analiza expresión facial (apertura de ojos, boca, posición de cejas)."""
        expression = {}
        if not LandmarkFormatHandler.is_valid_landmarks(landmarks):
            return expression
        
        try:
            # Get eye regions using utility
            left_eye_region = LandmarkFormatHandler.get_feature_region(landmarks, 'left_eye')
            right_eye_region = LandmarkFormatHandler.get_feature_region(landmarks, 'right_eye')
            mouth_region = LandmarkFormatHandler.get_feature_region(landmarks, 'mouth')
            
            if left_eye_region is not None and len(left_eye_region) >= 2:
                # Calculate eye openness from region
                left_eye_top = left_eye_region[0]
                left_eye_bottom = left_eye_region[-1] if len(left_eye_region) > 1 else left_eye_region[0]
                left_eye_openness = np.linalg.norm(left_eye_bottom - left_eye_top)
            else:
                left_eye_openness = 0.0
            
            if right_eye_region is not None and len(right_eye_region) >= 2:
                right_eye_top = right_eye_region[0]
                right_eye_bottom = right_eye_region[-1] if len(right_eye_region) > 1 else right_eye_region[0]
                right_eye_openness = np.linalg.norm(right_eye_bottom - right_eye_top)
            else:
                right_eye_openness = 0.0
            
            expression['eye_openness'] = (left_eye_openness + right_eye_openness) / 2.0
            
            # Calculate mouth openness
            if mouth_region is not None and len(mouth_region) >= 2:
                mouth_top = mouth_region[0]
                mouth_bottom = mouth_region[len(mouth_region) // 2] if len(mouth_region) > 1 else mouth_region[0]
                mouth_openness = np.linalg.norm(mouth_bottom - mouth_top)
                expression['mouth_openness'] = float(mouth_openness)
            else:
                expression['mouth_openness'] = 0.0
            
        except Exception:
            pass
        
        return expression
    
    def analyze_facial_features_deep(self, image: np.ndarray, landmarks: np.ndarray) -> dict:
        """Análisis profundo de características faciales."""
        features = {}
        if not LandmarkFormatHandler.is_valid_landmarks(landmarks):
            return features
        
        try:
            lab = ImageProcessor.convert_bgr_to_lab(image)
            l_channel = lab[:, :, 0].astype(np.float32)
            
            # Get face center using utility
            face_center = LandmarkFormatHandler.get_feature_point(landmarks, 'face_center')
            if face_center is None:
                return features
            
            x, y = ImageProcessor.ensure_bounds(
                int(face_center[0]), 
                int(face_center[1]), 
                image.shape[1], 
                image.shape[0]
            )
            
            # Extract skin region around center
            h, w = image.shape[:2]
            skin_region = l_channel[max(0, y-10):min(h, y+10), max(0, x-10):min(w, x+10)]
            features['skin_tone'] = float(np.mean(skin_region))
            
            # Analyze facial proportions using utility
            left_eye_pt = LandmarkFormatHandler.get_feature_point(landmarks, 'left_eye_center')
            right_eye_pt = LandmarkFormatHandler.get_feature_point(landmarks, 'right_eye_center')
            chin_pt = LandmarkFormatHandler.get_feature_point(landmarks, 'chin')
            
            if left_eye_pt is not None and right_eye_pt is not None and chin_pt is not None:
                eye_distance = np.linalg.norm(right_eye_pt - left_eye_pt)
                face_height = np.linalg.norm(chin_pt - (left_eye_pt + right_eye_pt) / 2)
                features['face_aspect_ratio'] = float(eye_distance / (face_height + 1e-6))
                features['face_size'] = float(eye_distance)
            
        except Exception:
            pass
        
        return features
    
    def analyze_geometric_structure(self, landmarks: np.ndarray) -> dict:
        """Análisis de estructura geométrica facial."""
        structure = {}
        if not LandmarkFormatHandler.is_valid_landmarks(landmarks):
            return structure
        
        try:
            # Get key points using utility
            left_eye_pt = LandmarkFormatHandler.get_feature_point(landmarks, 'left_eye_center')
            right_eye_pt = LandmarkFormatHandler.get_feature_point(landmarks, 'right_eye_center')
            nose_pt = LandmarkFormatHandler.get_feature_point(landmarks, 'nose_tip')
            mouth_left_pt = LandmarkFormatHandler.get_feature_point(landmarks, 'mouth_left')
            mouth_right_pt = LandmarkFormatHandler.get_feature_point(landmarks, 'mouth_right')
            
            if not all([left_eye_pt is not None, right_eye_pt is not None, 
                       nose_pt is not None, mouth_left_pt is not None, 
                       mouth_right_pt is not None]):
                return structure
            
            # Distance between eyes
            eye_distance = np.linalg.norm(right_eye_pt - left_eye_pt)
            structure['eye_distance'] = float(eye_distance)
            
            # Nose to eye ratio
            nose_to_eye = np.linalg.norm(nose_pt - (left_eye_pt + right_eye_pt) / 2)
            structure['nose_to_eye_ratio'] = float(nose_to_eye / (eye_distance + 1e-6))
            
            # Mouth to nose ratio
            mouth_center = (mouth_left_pt + mouth_right_pt) / 2
            mouth_to_nose = np.linalg.norm(mouth_center - nose_pt)
            structure['mouth_to_nose_ratio'] = float(mouth_to_nose / (eye_distance + 1e-6))
            
            # Eye angle
            eye_angle = np.arctan2(right_eye_pt[1] - left_eye_pt[1], 
                                  right_eye_pt[0] - left_eye_pt[0])
            structure['eye_angle'] = float(eye_angle)
            
            # Face center
            face_center = (left_eye_pt + right_eye_pt + nose_pt + mouth_center) / 4
            structure['face_center'] = face_center.astype(np.float32)
            
        except Exception:
            pass
        
        return structure
    
    def analyze_facial_symmetry(self, image: np.ndarray, landmarks: np.ndarray) -> dict:
        """Análisis de simetría facial."""
        symmetry = {}
        if not LandmarkFormatHandler.is_valid_landmarks(landmarks):
            return symmetry
        
        try:
            # Get key points using utility
            left_eye_pt = LandmarkFormatHandler.get_feature_point(landmarks, 'left_eye_center')
            right_eye_pt = LandmarkFormatHandler.get_feature_point(landmarks, 'right_eye_center')
            nose_tip_pt = LandmarkFormatHandler.get_feature_point(landmarks, 'nose_tip')
            mouth_left_pt = LandmarkFormatHandler.get_feature_point(landmarks, 'mouth_left')
            mouth_right_pt = LandmarkFormatHandler.get_feature_point(landmarks, 'mouth_right')
            
            if not all([left_eye_pt is not None, right_eye_pt is not None, 
                       nose_tip_pt is not None, mouth_left_pt is not None, 
                       mouth_right_pt is not None]):
                return symmetry
            
            # Calculate symmetry center line
            center_x = (left_eye_pt[0] + right_eye_pt[0]) / 2.0
            symmetry['center_x'] = float(center_x)
            
            # Calculate eye asymmetry
            eye_distance_left = np.sqrt((left_eye_pt[0] - center_x)**2 + 
                                       (left_eye_pt[1] - nose_tip_pt[1])**2)
            eye_distance_right = np.sqrt((right_eye_pt[0] - center_x)**2 + 
                                        (right_eye_pt[1] - nose_tip_pt[1])**2)
            eye_asymmetry = abs(eye_distance_left - eye_distance_right) / \
                          max(eye_distance_left, eye_distance_right, 1e-6)
            symmetry['eye_asymmetry'] = float(eye_asymmetry)
            
            # Calculate mouth asymmetry
            mouth_distance_left = np.sqrt((mouth_left_pt[0] - center_x)**2 + 
                                        (mouth_left_pt[1] - nose_tip_pt[1])**2)
            mouth_distance_right = np.sqrt((mouth_right_pt[0] - center_x)**2 + 
                                         (mouth_right_pt[1] - nose_tip_pt[1])**2)
            mouth_asymmetry = abs(mouth_distance_left - mouth_distance_right) / \
                            max(mouth_distance_left, mouth_distance_right, 1e-6)
            symmetry['mouth_asymmetry'] = float(mouth_asymmetry)
            
            # Calculate overall symmetry
            symmetry['overall_symmetry'] = float(1.0 - (eye_asymmetry + mouth_asymmetry) / 2.0)
            
        except Exception:
            pass
        
        return symmetry








