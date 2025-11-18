"""
Voice Routes - Rutas de Búsqueda por Voz
API endpoints para el sistema de búsqueda por voz
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Query
from typing import List, Dict, Any, Optional
import logging
import json
import base64
from datetime import datetime

from models.voice_search import VoiceSearchSystem

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/voice", tags=["voice"])

# Instancia global (se inicializará en main.py)
voice_system: Optional[VoiceSearchSystem] = None

def get_voice_system() -> VoiceSearchSystem:
    """Dependency para obtener el sistema de voz"""
    if voice_system is None:
        raise HTTPException(status_code=503, detail="Voice system not initialized")
    return voice_system

@router.post("/start-listening")
async def start_voice_listening(
    user_id: str = Form(...),
    voice_system: VoiceSearchSystem = Depends(get_voice_system)
):
    """Iniciar escucha de voz"""
    try:
        result = await voice_system.start_listening()
        
        return {
            "success": True,
            "message": result,
            "user_id": user_id,
            "is_listening": voice_system.is_listening,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error iniciando escucha de voz: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop-listening")
async def stop_voice_listening(
    voice_system: VoiceSearchSystem = Depends(get_voice_system)
):
    """Detener escucha de voz"""
    try:
        await voice_system.stop_listening()
        
        return {
            "success": True,
            "message": "Escucha de voz detenida",
            "is_listening": voice_system.is_listening,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error deteniendo escucha de voz: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-audio")
async def process_audio_file(
    audio_file: UploadFile = File(...),
    user_id: str = Form(...),
    voice_system: VoiceSearchSystem = Depends(get_voice_system)
):
    """Procesar archivo de audio"""
    try:
        # Verificar tipo de archivo
        if not audio_file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="El archivo debe ser de audio")
        
        # Leer datos del archivo
        audio_data = await audio_file.read()
        
        # Determinar formato
        file_format = audio_file.filename.split('.')[-1].lower() if audio_file.filename else 'wav'
        
        # Procesar audio
        result = await voice_system.process_audio_file(audio_data, file_format)
        
        return {
            "success": True,
            "result": result,
            "user_id": user_id,
            "filename": audio_file.filename,
            "file_size": len(audio_data),
            "format": file_format,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error procesando archivo de audio: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/text-to-speech")
async def convert_text_to_speech(
    text: str = Form(...),
    save_to_file: bool = Form(False),
    voice_system: VoiceSearchSystem = Depends(get_voice_system)
):
    """Convertir texto a voz"""
    try:
        if not text or len(text.strip()) < 1:
            raise HTTPException(status_code=400, detail="El texto no puede estar vacío")
        
        # Convertir texto a voz
        audio_data = await voice_system.convert_text_to_speech(text, save_to_file)
        
        if save_to_file and audio_data:
            # Codificar audio en base64 para envío
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            return {
                "success": True,
                "text": text,
                "audio_data": audio_base64,
                "audio_size": len(audio_data),
                "format": "wav",
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Solo reproducir, no devolver datos
            return {
                "success": True,
                "text": text,
                "message": "Texto convertido a voz y reproducido",
                "timestamp": datetime.now().isoformat()
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error convirtiendo texto a voz: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/voices")
async def get_available_voices(
    voice_system: VoiceSearchSystem = Depends(get_voice_system)
):
    """Obtener voces disponibles"""
    try:
        voices = voice_system.get_available_voices()
        
        return {
            "voices": voices,
            "count": len(voices),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo voces disponibles: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/voice-settings")
async def update_voice_settings(
    rate: Optional[int] = Form(None),
    volume: Optional[float] = Form(None),
    voice_id: Optional[int] = Form(None),
    voice_system: VoiceSearchSystem = Depends(get_voice_system)
):
    """Actualizar configuración de voz"""
    try:
        # Validar parámetros
        if rate is not None and (rate < 50 or rate > 300):
            raise HTTPException(status_code=400, detail="Rate debe estar entre 50 y 300")
        
        if volume is not None and (volume < 0.0 or volume > 1.0):
            raise HTTPException(status_code=400, detail="Volume debe estar entre 0.0 y 1.0")
        
        # Actualizar configuración
        voice_system.set_voice_settings(rate, volume, voice_id)
        
        return {
            "success": True,
            "message": "Configuración de voz actualizada",
            "current_settings": voice_system.voice_settings,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando configuración de voz: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/recognition-settings")
async def update_recognition_settings(
    energy_threshold: Optional[int] = Form(None),
    pause_threshold: Optional[float] = Form(None),
    phrase_threshold: Optional[float] = Form(None),
    voice_system: VoiceSearchSystem = Depends(get_voice_system)
):
    """Actualizar configuración de reconocimiento"""
    try:
        # Validar parámetros
        if energy_threshold is not None and energy_threshold < 0:
            raise HTTPException(status_code=400, detail="Energy threshold debe ser positivo")
        
        if pause_threshold is not None and (pause_threshold < 0.1 or pause_threshold > 2.0):
            raise HTTPException(status_code=400, detail="Pause threshold debe estar entre 0.1 y 2.0")
        
        if phrase_threshold is not None and (phrase_threshold < 0.1 or phrase_threshold > 2.0):
            raise HTTPException(status_code=400, detail="Phrase threshold debe estar entre 0.1 y 2.0")
        
        # Actualizar configuración
        settings = {}
        if energy_threshold is not None:
            settings["energy_threshold"] = energy_threshold
        if pause_threshold is not None:
            settings["pause_threshold"] = pause_threshold
        if phrase_threshold is not None:
            settings["phrase_threshold"] = phrase_threshold
        
        voice_system.set_recognition_settings(**settings)
        
        return {
            "success": True,
            "message": "Configuración de reconocimiento actualizada",
            "current_settings": voice_system.recognition_settings,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando configuración de reconocimiento: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_voice_stats(
    voice_system: VoiceSearchSystem = Depends(get_voice_system)
):
    """Obtener estadísticas del sistema de voz"""
    try:
        stats = voice_system.get_voice_search_stats()
        
        return {
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas de voz: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/commands")
async def get_voice_commands():
    """Obtener comandos de voz disponibles"""
    commands = {
        "search": {
            "keywords": ["buscar", "busca", "encontrar", "encuentra"],
            "description": "Buscar información en documentos",
            "example": "buscar información sobre machine learning"
        },
        "explain": {
            "keywords": ["explicar", "explica", "qué significa", "definir"],
            "description": "Explicar conceptos y definiciones",
            "example": "explica qué es inteligencia artificial"
        },
        "summarize": {
            "keywords": ["resumir", "resumen", "síntesis"],
            "description": "Crear resúmenes de documentos",
            "example": "resumir el documento sobre Python"
        },
        "help": {
            "keywords": ["ayuda", "help", "cómo usar"],
            "description": "Obtener ayuda sobre el sistema",
            "example": "ayuda"
        },
        "stop": {
            "keywords": ["parar", "stop", "detener", "salir"],
            "description": "Detener la búsqueda por voz",
            "example": "parar"
        }
    }
    
    return {
        "commands": commands,
        "count": len(commands),
        "timestamp": datetime.now().isoformat()
    }

@router.post("/test-microphone")
async def test_microphone(
    voice_system: VoiceSearchSystem = Depends(get_voice_system)
):
    """Probar micrófono"""
    try:
        if not voice_system.microphone:
            raise HTTPException(status_code=503, detail="Micrófono no disponible")
        
        # Probar acceso al micrófono
        try:
            with voice_system.microphone as source:
                # Intentar leer del micrófono por un breve momento
                import time
                time.sleep(0.1)
            
            return {
                "success": True,
                "message": "Micrófono funcionando correctamente",
                "microphone_available": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error accediendo al micrófono: {str(e)}",
                "microphone_available": False,
                "timestamp": datetime.now().isoformat()
            }
        
    except Exception as e:
        logger.error(f"Error probando micrófono: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_voice_system_status(
    voice_system: VoiceSearchSystem = Depends(get_voice_system)
):
    """Obtener estado del sistema de voz"""
    try:
        status = {
            "is_listening": voice_system.is_listening,
            "microphone_available": voice_system.microphone is not None,
            "tts_engine_available": voice_system.tts_engine is not None,
            "recognizer_available": voice_system.recognizer is not None,
            "language": voice_system.language,
            "voice_settings": voice_system.voice_settings,
            "recognition_settings": voice_system.recognition_settings
        }
        
        return {
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estado del sistema de voz: {e}")
        raise HTTPException(status_code=500, detail=str(e))


























