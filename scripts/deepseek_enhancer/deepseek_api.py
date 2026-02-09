"""
DeepSeek API Client
===================
Cliente para interactuar con la API de DeepSeek.
"""

import cv2
import numpy as np
import base64
import requests
import json
import os
from typing import Dict, Any, Optional


class DeepSeekAPI:
    """Cliente para la API de DeepSeek."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializar cliente API.
        
        Args:
            api_key: API key de DeepSeek. Si no se proporciona, se busca en variable de entorno DEEPSEEK_API_KEY.
        
        Raises:
            ValueError: Si no se encuentra API key.
        """
        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY')
        if not self.api_key:
            raise ValueError(
                "DeepSeek API key no encontrada. "
                "Configura la variable de entorno DEEPSEEK_API_KEY o pásala como parámetro. "
                "Ejemplo: export DEEPSEEK_API_KEY='tu_api_key_aqui'"
            )
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
    
    def _image_to_base64(self, image: np.ndarray) -> str:
        """
        Convierte una imagen OpenCV a base64.
        
        Args:
            image: Imagen OpenCV
        
        Returns:
            String base64
        """
        # Redimensionar si es muy grande para evitar problemas con la API
        max_size = 1024
        h, w = image.shape[:2]
        if max(h, w) > max_size:
            scale = max_size / max(h, w)
            new_w = int(w * scale)
            new_h = int(h * scale)
            image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
        
        # Convertir a JPEG
        _, buffer = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, 95])
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        return img_base64
    
    def analyze_face_swap_quality(
        self,
        result_image: np.ndarray,
        source_image: np.ndarray,
        target_image: np.ndarray
    ) -> Dict[str, Any]:
        """
        Analiza la calidad del face swap usando DeepSeek.
        
        Args:
            result_image: Imagen resultante del face swap
            source_image: Imagen fuente
            target_image: Imagen objetivo
        
        Returns:
            Diccionario con análisis y sugerencias
        """
        try:
            # Convertir imágenes a base64
            result_b64 = self._image_to_base64(result_image)
            source_b64 = self._image_to_base64(source_image)
            target_b64 = self._image_to_base64(target_image)
            
            system_prompt = """You are an expert in face swap quality analysis. 
Analyze face swap results and provide specific, actionable improvement suggestions.
Focus on: color matching, blending quality, edge artifacts, lighting consistency, and overall realism.
Return a JSON object with your analysis."""
            
            user_prompt = f"""Analyze this face swap result:

1. Source face (bunny): {source_b64[:100]}...
2. Target face (caylin): {target_b64[:100]}...
3. Result: {result_b64[:100]}...

Provide analysis in this JSON format:
{{
    "quality_score": 0-100,
    "issues": ["issue1", "issue2"],
    "suggestions": ["suggestion1", "suggestion2"],
    "color_match": "good/needs_improvement/poor",
    "blending": "good/needs_improvement/poor",
    "lighting": "good/needs_improvement/poor",
    "specific_improvements": {{
        "brightness_adjustment": -10 to 10,
        "contrast_adjustment": -10 to 10,
        "saturation_adjustment": -10 to 10,
        "blur_edges": true/false,
        "enhance_sharpness": true/false
    }}
}}

Return ONLY the JSON, no explanations."""
            
            response = requests.post(
                self.base_url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 1000
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                
                # Intentar extraer JSON del contenido
                try:
                    json_start = content.find('{')
                    json_end = content.rfind('}') + 1
                    if json_start >= 0 and json_end > json_start:
                        json_str = content[json_start:json_end]
                        analysis = json.loads(json_str)
                        return analysis
                except:
                    pass
            
            # Fallback si la API falla
            return self._get_fallback_analysis()
            
        except Exception as e:
            print(f"⚠ Error en análisis DeepSeek: {e}")
            return self._get_fallback_analysis()
    
    def _get_fallback_analysis(self) -> Dict[str, Any]:
        """Retorna análisis por defecto si la API falla."""
        return {
            "quality_score": 70,
            "issues": ["API analysis unavailable"],
            "suggestions": ["Apply standard enhancements"],
            "color_match": "needs_improvement",
            "blending": "needs_improvement",
            "lighting": "needs_improvement",
            "specific_improvements": {
                "brightness_adjustment": 0,
                "contrast_adjustment": 5,
                "saturation_adjustment": 3,
                "blur_edges": True,
                "enhance_sharpness": True
            }
        }






