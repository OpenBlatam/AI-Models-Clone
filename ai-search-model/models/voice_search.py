"""
Voice Search - Sistema de Búsqueda por Voz
Sistema avanzado de reconocimiento y síntesis de voz para búsquedas
"""

import asyncio
import logging
import json
import wave
import io
import base64
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import numpy as np
import speech_recognition as sr
import pyttsx3
from pydub import AudioSegment
from pydub.playback import play
import threading
import queue
import tempfile
import os

logger = logging.getLogger(__name__)

class VoiceSearchSystem:
    """
    Sistema de búsqueda por voz con reconocimiento y síntesis
    """
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.tts_engine = None
        self.audio_queue = queue.Queue()
        self.is_listening = False
        self.language = "es-ES"
        self.voice_settings = {
            "rate": 200,      # Velocidad de habla
            "volume": 0.8,    # Volumen
            "voice_id": 0     # ID de voz
        }
        
        # Configuraciones de reconocimiento
        self.recognition_settings = {
            "energy_threshold": 300,
            "dynamic_energy_threshold": True,
            "pause_threshold": 0.8,
            "phrase_threshold": 0.3,
            "non_speaking_duration": 0.8
        }
        
        # Comandos de voz predefinidos
        self.voice_commands = {
            "buscar": ["buscar", "busca", "encontrar", "encuentra"],
            "explicar": ["explicar", "explica", "qué significa", "definir"],
            "resumir": ["resumir", "resumen", "síntesis"],
            "ayuda": ["ayuda", "help", "cómo usar"],
            "parar": ["parar", "stop", "detener", "salir"]
        }
    
    async def initialize(self):
        """Inicializar sistema de voz"""
        try:
            logger.info("Inicializando sistema de búsqueda por voz...")
            
            # Configurar reconocedor de voz
            self.recognizer.energy_threshold = self.recognition_settings["energy_threshold"]
            self.recognizer.dynamic_energy_threshold = self.recognition_settings["dynamic_energy_threshold"]
            self.recognizer.pause_threshold = self.recognition_settings["pause_threshold"]
            self.recognizer.phrase_threshold = self.recognition_settings["phrase_threshold"]
            self.recognizer.non_speaking_duration = self.recognition_settings["non_speaking_duration"]
            
            # Configurar micrófono
            self.microphone = sr.Microphone()
            
            # Calibrar micrófono
            with self.microphone as source:
                logger.info("Calibrando micrófono...")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                logger.info(f"Umbral de energía ajustado a: {self.recognizer.energy_threshold}")
            
            # Inicializar motor de síntesis de voz
            self.tts_engine = pyttsx3.init()
            self._configure_tts()
            
            logger.info("Sistema de búsqueda por voz inicializado exitosamente")
            
        except Exception as e:
            logger.error(f"Error inicializando sistema de voz: {e}")
            raise
    
    def _configure_tts(self):
        """Configurar motor de síntesis de voz"""
        try:
            # Configurar velocidad
            self.tts_engine.setProperty('rate', self.voice_settings["rate"])
            
            # Configurar volumen
            self.tts_engine.setProperty('volume', self.voice_settings["volume"])
            
            # Configurar voz
            voices = self.tts_engine.getProperty('voices')
            if voices and len(voices) > self.voice_settings["voice_id"]:
                self.tts_engine.setProperty('voice', voices[self.voice_settings["voice_id"]].id)
            
            logger.info("Motor de síntesis de voz configurado")
            
        except Exception as e:
            logger.error(f"Error configurando TTS: {e}")
    
    async def start_listening(self, callback=None) -> str:
        """Iniciar escucha de voz"""
        try:
            if self.is_listening:
                return "Ya estoy escuchando"
            
            self.is_listening = True
            logger.info("Iniciando escucha de voz...")
            
            # Reproducir sonido de inicio
            await self._play_start_sound()
            
            # Escuchar en un hilo separado
            def listen_thread():
                try:
                    with self.microphone as source:
                        # Escuchar audio
                        audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=5)
                        
                        # Reconocer audio
                        try:
                            text = self.recognizer.recognize_google(audio, language=self.language)
                            logger.info(f"Texto reconocido: {text}")
                            
                            # Procesar comando
                            asyncio.run_coroutine_threadsafe(
                                self._process_voice_command(text, callback),
                                asyncio.get_event_loop()
                            )
                            
                        except sr.UnknownValueError:
                            logger.warning("No se pudo entender el audio")
                            asyncio.run_coroutine_threadsafe(
                                self._speak("No pude entender lo que dijiste. ¿Podrías repetir?"),
                                asyncio.get_event_loop()
                            )
                            
                        except sr.RequestError as e:
                            logger.error(f"Error en el servicio de reconocimiento: {e}")
                            asyncio.run_coroutine_threadsafe(
                                self._speak("Error en el servicio de reconocimiento de voz"),
                                asyncio.get_event_loop()
                            )
                
                except Exception as e:
                    logger.error(f"Error en escucha de voz: {e}")
                finally:
                    self.is_listening = False
            
            # Iniciar hilo de escucha
            thread = threading.Thread(target=listen_thread, daemon=True)
            thread.start()
            
            return "Escuchando... Di tu comando"
            
        except Exception as e:
            logger.error(f"Error iniciando escucha: {e}")
            self.is_listening = False
            return f"Error iniciando escucha: {e}"
    
    async def _process_voice_command(self, text: str, callback=None) -> str:
        """Procesar comando de voz"""
        try:
            text_lower = text.lower()
            logger.info(f"Procesando comando de voz: {text}")
            
            # Detectar tipo de comando
            command_type = self._detect_command_type(text_lower)
            
            if command_type == "buscar":
                # Extraer términos de búsqueda
                search_terms = self._extract_search_terms(text_lower)
                if search_terms:
                    await self._speak(f"Buscando información sobre {search_terms}")
                    if callback:
                        await callback("search", search_terms)
                    return f"Búsqueda: {search_terms}"
                else:
                    await self._speak("¿Qué te gustaría buscar?")
                    return "Comando de búsqueda sin términos"
            
            elif command_type == "explicar":
                # Extraer concepto a explicar
                concept = self._extract_concept(text_lower)
                if concept:
                    await self._speak(f"Explicando {concept}")
                    if callback:
                        await callback("explain", concept)
                    return f"Explicación: {concept}"
                else:
                    await self._speak("¿Qué concepto te gustaría que explique?")
                    return "Comando de explicación sin concepto"
            
            elif command_type == "resumir":
                # Extraer tema para resumir
                topic = self._extract_topic(text_lower)
                if topic:
                    await self._speak(f"Generando resumen sobre {topic}")
                    if callback:
                        await callback("summarize", topic)
                    return f"Resumen: {topic}"
                else:
                    await self._speak("¿Sobre qué tema te gustaría un resumen?")
                    return "Comando de resumen sin tema"
            
            elif command_type == "ayuda":
                await self._speak("Puedes decir: buscar, explicar, resumir, o ayuda")
                if callback:
                    await callback("help", None)
                return "Comando de ayuda"
            
            elif command_type == "parar":
                await self._speak("Deteniendo búsqueda por voz")
                if callback:
                    await callback("stop", None)
                return "Comando de parada"
            
            else:
                # Comando no reconocido, intentar búsqueda general
                await self._speak(f"Buscando información sobre {text}")
                if callback:
                    await callback("search", text)
                return f"Búsqueda general: {text}"
            
        except Exception as e:
            logger.error(f"Error procesando comando de voz: {e}")
            await self._speak("Error procesando tu comando")
            return f"Error: {e}"
    
    def _detect_command_type(self, text: str) -> str:
        """Detectar tipo de comando de voz"""
        for command_type, keywords in self.voice_commands.items():
            if any(keyword in text for keyword in keywords):
                return command_type
        return "unknown"
    
    def _extract_search_terms(self, text: str) -> str:
        """Extraer términos de búsqueda del texto"""
        # Remover palabras de comando
        command_words = ["buscar", "busca", "encontrar", "encuentra", "información", "sobre"]
        
        words = text.split()
        search_words = [word for word in words if word not in command_words]
        
        return " ".join(search_words) if search_words else ""
    
    def _extract_concept(self, text: str) -> str:
        """Extraer concepto a explicar del texto"""
        # Remover palabras de comando
        command_words = ["explicar", "explica", "qué", "significa", "definir", "definición"]
        
        words = text.split()
        concept_words = [word for word in words if word not in command_words]
        
        return " ".join(concept_words) if concept_words else ""
    
    def _extract_topic(self, text: str) -> str:
        """Extraer tema para resumir del texto"""
        # Remover palabras de comando
        command_words = ["resumir", "resumen", "síntesis", "sobre", "de"]
        
        words = text.split()
        topic_words = [word for word in words if word not in command_words]
        
        return " ".join(topic_words) if topic_words else ""
    
    async def _speak(self, text: str) -> bool:
        """Sintetizar y reproducir texto"""
        try:
            if not self.tts_engine:
                logger.warning("Motor TTS no inicializado")
                return False
            
            # Reproducir en un hilo separado para no bloquear
            def speak_thread():
                try:
                    self.tts_engine.say(text)
                    self.tts_engine.runAndWait()
                except Exception as e:
                    logger.error(f"Error en síntesis de voz: {e}")
            
            thread = threading.Thread(target=speak_thread, daemon=True)
            thread.start()
            
            logger.info(f"Reproduciendo: {text}")
            return True
            
        except Exception as e:
            logger.error(f"Error en síntesis de voz: {e}")
            return False
    
    async def _play_start_sound(self):
        """Reproducir sonido de inicio"""
        try:
            # Generar tono de inicio simple
            duration = 0.5  # segundos
            sample_rate = 44100
            frequency = 800  # Hz
            
            # Generar onda senoidal
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            wave_data = np.sin(frequency * 2 * np.pi * t)
            
            # Convertir a formato de audio
            wave_data = (wave_data * 32767).astype(np.int16)
            
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                with wave.open(temp_file.name, 'w') as wav_file:
                    wav_file.setnchannels(1)  # Mono
                    wav_file.setsampwidth(2)  # 16-bit
                    wav_file.setframerate(sample_rate)
                    wav_file.writeframes(wave_data.tobytes())
                
                # Reproducir sonido
                audio = AudioSegment.from_wav(temp_file.name)
                play(audio)
                
                # Limpiar archivo temporal
                os.unlink(temp_file.name)
            
        except Exception as e:
            logger.error(f"Error reproduciendo sonido de inicio: {e}")
    
    async def process_audio_file(self, audio_data: bytes, format: str = "wav") -> str:
        """Procesar archivo de audio"""
        try:
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(suffix=f".{format}", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file.flush()
                
                # Cargar audio
                audio = sr.AudioFile(temp_file.name)
                
                with audio as source:
                    # Ajustar para ruido ambiente
                    self.recognizer.adjust_for_ambient_noise(source)
                    
                    # Escuchar audio
                    audio_data = self.recognizer.record(source)
                
                # Reconocer texto
                try:
                    text = self.recognizer.recognize_google(audio_data, language=self.language)
                    logger.info(f"Texto reconocido del archivo: {text}")
                    
                    # Procesar comando
                    result = await self._process_voice_command(text)
                    
                    return result
                    
                except sr.UnknownValueError:
                    return "No se pudo entender el audio del archivo"
                    
                except sr.RequestError as e:
                    return f"Error en el servicio de reconocimiento: {e}"
                
                finally:
                    # Limpiar archivo temporal
                    os.unlink(temp_file.name)
            
        except Exception as e:
            logger.error(f"Error procesando archivo de audio: {e}")
            return f"Error procesando archivo: {e}"
    
    async def convert_text_to_speech(self, text: str, save_to_file: bool = False) -> Optional[bytes]:
        """Convertir texto a audio"""
        try:
            if not self.tts_engine:
                logger.warning("Motor TTS no inicializado")
                return None
            
            if save_to_file:
                # Guardar en archivo
                filename = f"speech_{int(datetime.now().timestamp())}.wav"
                self.tts_engine.save_to_file(text, filename)
                self.tts_engine.runAndWait()
                
                # Leer archivo generado
                with open(filename, 'rb') as f:
                    audio_data = f.read()
                
                # Limpiar archivo
                os.unlink(filename)
                
                return audio_data
            else:
                # Solo reproducir
                await self._speak(text)
                return None
            
        except Exception as e:
            logger.error(f"Error convirtiendo texto a voz: {e}")
            return None
    
    def set_voice_settings(self, rate: int = None, volume: float = None, voice_id: int = None):
        """Configurar parámetros de voz"""
        try:
            if rate is not None:
                self.voice_settings["rate"] = rate
                self.tts_engine.setProperty('rate', rate)
            
            if volume is not None:
                self.voice_settings["volume"] = volume
                self.tts_engine.setProperty('volume', volume)
            
            if voice_id is not None:
                self.voice_settings["voice_id"] = voice_id
                voices = self.tts_engine.getProperty('voices')
                if voices and len(voices) > voice_id:
                    self.tts_engine.setProperty('voice', voices[voice_id].id)
            
            logger.info("Configuración de voz actualizada")
            
        except Exception as e:
            logger.error(f"Error configurando voz: {e}")
    
    def set_recognition_settings(self, **kwargs):
        """Configurar parámetros de reconocimiento"""
        try:
            for key, value in kwargs.items():
                if key in self.recognition_settings:
                    self.recognition_settings[key] = value
                    
                    # Aplicar configuración al reconocedor
                    if hasattr(self.recognizer, key):
                        setattr(self.recognizer, key, value)
            
            logger.info("Configuración de reconocimiento actualizada")
            
        except Exception as e:
            logger.error(f"Error configurando reconocimiento: {e}")
    
    def get_available_voices(self) -> List[Dict[str, Any]]:
        """Obtener voces disponibles"""
        try:
            if not self.tts_engine:
                return []
            
            voices = self.tts_engine.getProperty('voices')
            voice_list = []
            
            for i, voice in enumerate(voices):
                voice_list.append({
                    "id": i,
                    "name": voice.name,
                    "languages": voice.languages,
                    "gender": voice.gender,
                    "age": voice.age
                })
            
            return voice_list
            
        except Exception as e:
            logger.error(f"Error obteniendo voces disponibles: {e}")
            return []
    
    def get_voice_search_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del sistema de voz"""
        return {
            "is_listening": self.is_listening,
            "language": self.language,
            "voice_settings": self.voice_settings,
            "recognition_settings": self.recognition_settings,
            "available_voices": len(self.get_available_voices()),
            "last_updated": datetime.now().isoformat()
        }
    
    async def stop_listening(self):
        """Detener escucha de voz"""
        try:
            self.is_listening = False
            logger.info("Escucha de voz detenida")
            
        except Exception as e:
            logger.error(f"Error deteniendo escucha: {e}")
    
    async def shutdown(self):
        """Cerrar sistema de voz"""
        try:
            self.is_listening = False
            
            if self.tts_engine:
                self.tts_engine.stop()
            
            logger.info("Sistema de voz cerrado")
            
        except Exception as e:
            logger.error(f"Error cerrando sistema de voz: {e}")


























