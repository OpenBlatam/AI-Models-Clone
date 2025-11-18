"""
Multi-Language Support - Sistema de Soporte Multiidioma
Sistema avanzado de detección, traducción y procesamiento multiidioma
"""

import asyncio
import logging
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
import numpy as np
from langdetect import detect, detect_langs, LangDetectException
from googletrans import Translator
import spacy
from sentence_transformers import SentenceTransformer
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import SnowballStemmer
import unicodedata
import requests
import os

logger = logging.getLogger(__name__)

@dataclass
class LanguageDetection:
    """Resultado de detección de idioma"""
    language: str
    confidence: float
    alternative_languages: List[Dict[str, float]]
    is_reliable: bool

@dataclass
class TranslationResult:
    """Resultado de traducción"""
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    confidence: float
    detected_language: str

@dataclass
class MultiLanguageDocument:
    """Documento multiidioma"""
    document_id: str
    original_content: str
    detected_language: str
    translations: Dict[str, str]
    language_specific_features: Dict[str, Any]
    processing_metadata: Dict[str, Any]

class MultiLanguageSystem:
    """
    Sistema de soporte multiidioma para procesamiento de documentos
    """
    
    def __init__(self):
        self.translator = Translator()
        self.language_models = {}
        self.stemmers = {}
        self.stop_words = {}
        self.language_codes = {
            'en': 'english',
            'es': 'spanish',
            'fr': 'french',
            'de': 'german',
            'it': 'italian',
            'pt': 'portuguese',
            'ru': 'russian',
            'zh': 'chinese',
            'ja': 'japanese',
            'ko': 'korean',
            'ar': 'arabic',
            'hi': 'hindi',
            'nl': 'dutch',
            'sv': 'swedish',
            'da': 'danish',
            'no': 'norwegian',
            'fi': 'finnish',
            'pl': 'polish',
            'tr': 'turkish',
            'th': 'thai'
        }
        
        # Modelos de embeddings por idioma
        self.embedding_models = {
            'en': 'all-MiniLM-L6-v2',
            'es': 'paraphrase-multilingual-MiniLM-L12-v2',
            'fr': 'paraphrase-multilingual-MiniLM-L12-v2',
            'de': 'paraphrase-multilingual-MiniLM-L12-v2',
            'it': 'paraphrase-multilingual-MiniLM-L12-v2',
            'pt': 'paraphrase-multilingual-MiniLM-L12-v2',
            'ru': 'paraphrase-multilingual-MiniLM-L12-v2',
            'zh': 'paraphrase-multilingual-MiniLM-L12-v2',
            'ja': 'paraphrase-multilingual-MiniLM-L12-v2',
            'ko': 'paraphrase-multilingual-MiniLM-L12-v2',
            'ar': 'paraphrase-multilingual-MiniLM-L12-v2',
            'hi': 'paraphrase-multilingual-MiniLM-L12-v2',
            'default': 'paraphrase-multilingual-MiniLM-L12-v2'
        }
        
        # Configuraciones de procesamiento por idioma
        self.language_configs = {
            'en': {'stemmer': 'english', 'stop_words': 'english'},
            'es': {'stemmer': 'spanish', 'stop_words': 'spanish'},
            'fr': {'stemmer': 'french', 'stop_words': 'french'},
            'de': {'stemmer': 'german', 'stop_words': 'german'},
            'it': {'stemmer': 'italian', 'stop_words': 'italian'},
            'pt': {'stemmer': 'portuguese', 'stop_words': 'portuguese'},
            'ru': {'stemmer': 'russian', 'stop_words': 'russian'},
            'default': {'stemmer': 'english', 'stop_words': 'english'}
        }
    
    async def initialize(self):
        """Inicializar sistema multiidioma"""
        try:
            logger.info("Inicializando sistema multiidioma...")
            
            # Descargar recursos de NLTK
            await self._download_nltk_resources()
            
            # Inicializar stemmers
            await self._initialize_stemmers()
            
            # Inicializar stop words
            await self._initialize_stop_words()
            
            # Inicializar modelos de spaCy
            await self._initialize_spacy_models()
            
            # Inicializar modelos de embeddings
            await self._initialize_embedding_models()
            
            logger.info("Sistema multiidioma inicializado exitosamente")
            
        except Exception as e:
            logger.error(f"Error inicializando sistema multiidioma: {e}")
            raise
    
    async def _download_nltk_resources(self):
        """Descargar recursos de NLTK"""
        try:
            import nltk
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            
        except Exception as e:
            logger.warning(f"Error descargando recursos NLTK: {e}")
    
    async def _initialize_stemmers(self):
        """Inicializar stemmers por idioma"""
        try:
            for lang_code, lang_name in self.language_codes.items():
                try:
                    if lang_name in SnowballStemmer.languages:
                        self.stemmers[lang_code] = SnowballStemmer(lang_name)
                    else:
                        # Usar stemmer inglés como fallback
                        self.stemmers[lang_code] = SnowballStemmer('english')
                except Exception as e:
                    logger.warning(f"Error inicializando stemmer para {lang_code}: {e}")
                    self.stemmers[lang_code] = SnowballStemmer('english')
            
            logger.info(f"Stemmers inicializados para {len(self.stemmers)} idiomas")
            
        except Exception as e:
            logger.error(f"Error inicializando stemmers: {e}")
    
    async def _initialize_stop_words(self):
        """Inicializar stop words por idioma"""
        try:
            for lang_code, lang_name in self.language_codes.items():
                try:
                    if lang_name in stopwords.fileids():
                        self.stop_words[lang_code] = set(stopwords.words(lang_name))
                    else:
                        # Usar stop words en inglés como fallback
                        self.stop_words[lang_code] = set(stopwords.words('english'))
                except Exception as e:
                    logger.warning(f"Error cargando stop words para {lang_code}: {e}")
                    self.stop_words[lang_code] = set(stopwords.words('english'))
            
            logger.info(f"Stop words cargadas para {len(self.stop_words)} idiomas")
            
        except Exception as e:
            logger.error(f"Error inicializando stop words: {e}")
    
    async def _initialize_spacy_models(self):
        """Inicializar modelos de spaCy"""
        try:
            # Modelos de spaCy por idioma
            spacy_models = {
                'en': 'en_core_web_sm',
                'es': 'es_core_news_sm',
                'fr': 'fr_core_news_sm',
                'de': 'de_core_news_sm',
                'it': 'it_core_news_sm',
                'pt': 'pt_core_news_sm',
                'ru': 'ru_core_news_sm',
                'zh': 'zh_core_web_sm',
                'ja': 'ja_core_news_sm',
                'ko': 'ko_core_news_sm',
                'ar': 'ar_core_news_sm',
                'hi': 'hi_core_news_sm',
                'nl': 'nl_core_news_sm',
                'sv': 'sv_core_news_sm',
                'da': 'da_core_news_sm',
                'no': 'nb_core_news_sm',
                'fi': 'fi_core_news_sm',
                'pl': 'pl_core_news_sm',
                'tr': 'tr_core_news_sm',
                'th': 'th_core_news_sm'
            }
            
            for lang_code, model_name in spacy_models.items():
                try:
                    self.language_models[lang_code] = spacy.load(model_name)
                    logger.info(f"Modelo spaCy cargado para {lang_code}: {model_name}")
                except OSError:
                    logger.warning(f"Modelo spaCy no encontrado para {lang_code}: {model_name}")
                except Exception as e:
                    logger.warning(f"Error cargando modelo spaCy para {lang_code}: {e}")
            
            logger.info(f"Modelos spaCy cargados para {len(self.language_models)} idiomas")
            
        except Exception as e:
            logger.error(f"Error inicializando modelos spaCy: {e}")
    
    async def _initialize_embedding_models(self):
        """Inicializar modelos de embeddings"""
        try:
            # Cargar modelo multilingüe por defecto
            self.embedding_model = SentenceTransformer(self.embedding_models['default'])
            logger.info("Modelo de embeddings multilingüe cargado")
            
        except Exception as e:
            logger.error(f"Error inicializando modelo de embeddings: {e}")
    
    async def detect_language(self, text: str) -> LanguageDetection:
        """Detectar idioma del texto"""
        try:
            if not text or len(text.strip()) < 10:
                return LanguageDetection(
                    language='unknown',
                    confidence=0.0,
                    alternative_languages=[],
                    is_reliable=False
                )
            
            # Limpiar texto
            cleaned_text = self._clean_text_for_detection(text)
            
            # Detectar idioma principal
            try:
                detected_lang = detect(cleaned_text)
                confidence = 1.0  # langdetect no proporciona confianza directa
            except LangDetectException:
                detected_lang = 'unknown'
                confidence = 0.0
            
            # Obtener idiomas alternativos
            try:
                lang_probabilities = detect_langs(cleaned_text)
                alternative_languages = [
                    {"language": lang.lang, "probability": lang.prob}
                    for lang in lang_probabilities[:3]
                ]
            except LangDetectException:
                alternative_languages = []
            
            # Determinar si la detección es confiable
            is_reliable = (
                confidence > 0.5 and 
                detected_lang != 'unknown' and 
                len(cleaned_text) > 50
            )
            
            result = LanguageDetection(
                language=detected_lang,
                confidence=confidence,
                alternative_languages=alternative_languages,
                is_reliable=is_reliable
            )
            
            logger.info(f"Idioma detectado: {detected_lang} (confianza: {confidence})")
            return result
            
        except Exception as e:
            logger.error(f"Error detectando idioma: {e}")
            return LanguageDetection(
                language='unknown',
                confidence=0.0,
                alternative_languages=[],
                is_reliable=False
            )
    
    def _clean_text_for_detection(self, text: str) -> str:
        """Limpiar texto para detección de idioma"""
        try:
            # Remover caracteres especiales y números
            cleaned = re.sub(r'[^\w\s]', ' ', text)
            cleaned = re.sub(r'\d+', '', cleaned)
            
            # Normalizar espacios
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            
            # Remover URLs y emails
            cleaned = re.sub(r'http[s]?://\S+', '', cleaned)
            cleaned = re.sub(r'\S+@\S+', '', cleaned)
            
            return cleaned
            
        except Exception as e:
            logger.error(f"Error limpiando texto: {e}")
            return text
    
    async def translate_text(self, text: str, target_language: str, 
                           source_language: str = None) -> TranslationResult:
        """Traducir texto"""
        try:
            if not text or len(text.strip()) < 1:
                return TranslationResult(
                    original_text=text,
                    translated_text=text,
                    source_language=source_language or 'unknown',
                    target_language=target_language,
                    confidence=0.0,
                    detected_language=source_language or 'unknown'
                )
            
            # Detectar idioma fuente si no se proporciona
            if not source_language:
                detection = await self.detect_language(text)
                source_language = detection.language
            
            # Si el idioma fuente y destino son iguales, no traducir
            if source_language == target_language:
                return TranslationResult(
                    original_text=text,
                    translated_text=text,
                    source_language=source_language,
                    target_language=target_language,
                    confidence=1.0,
                    detected_language=source_language
                )
            
            # Realizar traducción
            try:
                translation = self.translator.translate(
                    text, 
                    src=source_language, 
                    dest=target_language
                )
                
                result = TranslationResult(
                    original_text=text,
                    translated_text=translation.text,
                    source_language=source_language,
                    target_language=target_language,
                    confidence=0.8,  # Google Translate no proporciona confianza directa
                    detected_language=source_language
                )
                
                logger.info(f"Texto traducido de {source_language} a {target_language}")
                return result
                
            except Exception as e:
                logger.error(f"Error en traducción: {e}")
                return TranslationResult(
                    original_text=text,
                    translated_text=text,
                    source_language=source_language,
                    target_language=target_language,
                    confidence=0.0,
                    detected_language=source_language
                )
            
        except Exception as e:
            logger.error(f"Error traduciendo texto: {e}")
            return TranslationResult(
                original_text=text,
                translated_text=text,
                source_language=source_language or 'unknown',
                target_language=target_language,
                confidence=0.0,
                detected_language=source_language or 'unknown'
            )
    
    async def process_multilingual_document(self, document: Dict[str, Any], 
                                          target_languages: List[str] = None) -> MultiLanguageDocument:
        """Procesar documento multiidioma"""
        try:
            content = document.get("content", "")
            doc_id = document.get("id", "unknown")
            
            # Detectar idioma
            language_detection = await self.detect_language(content)
            detected_language = language_detection.language
            
            # Determinar idiomas objetivo
            if not target_languages:
                target_languages = ['en', 'es', 'fr', 'de']  # Idiomas por defecto
            
            # Traducir a idiomas objetivo
            translations = {}
            for target_lang in target_languages:
                if target_lang != detected_language:
                    translation_result = await self.translate_text(
                        content, target_lang, detected_language
                    )
                    translations[target_lang] = translation_result.translated_text
            
            # Procesar características específicas del idioma
            language_features = await self._extract_language_specific_features(
                content, detected_language
            )
            
            # Crear documento multiidioma
            multilingual_doc = MultiLanguageDocument(
                document_id=doc_id,
                original_content=content,
                detected_language=detected_language,
                translations=translations,
                language_specific_features=language_features,
                processing_metadata={
                    "detection_confidence": language_detection.confidence,
                    "is_reliable": language_detection.is_reliable,
                    "alternative_languages": language_detection.alternative_languages,
                    "processed_at": datetime.now().isoformat()
                }
            )
            
            logger.info(f"Documento multiidioma procesado: {doc_id} ({detected_language})")
            return multilingual_doc
            
        except Exception as e:
            logger.error(f"Error procesando documento multiidioma: {e}")
            raise
    
    async def _extract_language_specific_features(self, text: str, 
                                                language: str) -> Dict[str, Any]:
        """Extraer características específicas del idioma"""
        try:
            features = {}
            
            # Tokenización
            tokens = word_tokenize(text)
            features["token_count"] = len(tokens)
            features["unique_tokens"] = len(set(tokens))
            
            # Análisis con spaCy si está disponible
            if language in self.language_models:
                try:
                    nlp = self.language_models[language]
                    doc = nlp(text)
                    
                    # Partes del discurso
                    pos_counts = {}
                    for token in doc:
                        pos = token.pos_
                        pos_counts[pos] = pos_counts.get(pos, 0) + 1
                    features["pos_distribution"] = pos_counts
                    
                    # Entidades nombradas
                    entities = [(ent.text, ent.label_) for ent in doc.ents]
                    features["named_entities"] = entities
                    features["entity_count"] = len(entities)
                    
                    # Lemmatización
                    lemmas = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
                    features["lemmas"] = lemmas[:50]  # Limitar a 50 lemas
                    
                except Exception as e:
                    logger.warning(f"Error en análisis spaCy para {language}: {e}")
            
            # Stemming
            if language in self.stemmers:
                try:
                    stemmer = self.stemmers[language]
                    stems = [stemmer.stem(token) for token in tokens if token.isalpha()]
                    features["stems"] = stems[:50]  # Limitar a 50 stems
                except Exception as e:
                    logger.warning(f"Error en stemming para {language}: {e}")
            
            # Stop words
            if language in self.stop_words:
                try:
                    stop_words_set = self.stop_words[language]
                    stop_word_count = sum(1 for token in tokens if token.lower() in stop_words_set)
                    features["stop_word_ratio"] = stop_word_count / len(tokens) if tokens else 0
                except Exception as e:
                    logger.warning(f"Error analizando stop words para {language}: {e}")
            
            # Características de texto
            features["sentence_count"] = len(sent_tokenize(text))
            features["average_sentence_length"] = len(tokens) / features["sentence_count"] if features["sentence_count"] > 0 else 0
            features["average_word_length"] = np.mean([len(word) for word in tokens if word.isalpha()]) if tokens else 0
            
            return features
            
        except Exception as e:
            logger.error(f"Error extrayendo características específicas del idioma: {e}")
            return {}
    
    async def generate_multilingual_embeddings(self, text: str, 
                                             language: str = None) -> np.ndarray:
        """Generar embeddings multilingües"""
        try:
            # Detectar idioma si no se proporciona
            if not language:
                detection = await self.detect_language(text)
                language = detection.language
            
            # Usar modelo de embeddings multilingüe
            embeddings = self.embedding_model.encode([text])
            
            return embeddings[0]
            
        except Exception as e:
            logger.error(f"Error generando embeddings multilingües: {e}")
            return np.array([])
    
    async def search_multilingual(self, query: str, documents: List[MultiLanguageDocument], 
                                target_language: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Búsqueda multilingüe"""
        try:
            # Detectar idioma de la consulta
            query_detection = await self.detect_language(query)
            query_language = query_detection.language
            
            # Generar embedding de la consulta
            query_embedding = await self.generate_multilingual_embeddings(query, query_language)
            
            if len(query_embedding) == 0:
                return []
            
            # Calcular similitudes
            similarities = []
            for doc in documents:
                # Usar contenido en el idioma más apropiado
                content_to_use = doc.original_content
                
                if target_language and target_language in doc.translations:
                    content_to_use = doc.translations[target_language]
                elif query_language in doc.translations:
                    content_to_use = doc.translations[query_language]
                
                # Generar embedding del documento
                doc_embedding = await self.generate_multilingual_embeddings(
                    content_to_use, doc.detected_language
                )
                
                if len(doc_embedding) > 0:
                    # Calcular similitud coseno
                    similarity = np.dot(query_embedding, doc_embedding) / (
                        np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
                    )
                    
                    similarities.append({
                        "document_id": doc.document_id,
                        "similarity": float(similarity),
                        "language": doc.detected_language,
                        "content": content_to_use[:200] + "..." if len(content_to_use) > 200 else content_to_use
                    })
            
            # Ordenar por similitud
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            
            return similarities[:limit]
            
        except Exception as e:
            logger.error(f"Error en búsqueda multilingüe: {e}")
            return []
    
    async def get_supported_languages(self) -> Dict[str, Any]:
        """Obtener idiomas soportados"""
        return {
            "detection_languages": list(self.language_codes.keys()),
            "translation_languages": list(self.language_codes.keys()),
            "spacy_models": list(self.language_models.keys()),
            "stemmers": list(self.stemmers.keys()),
            "stop_words": list(self.stop_words.keys()),
            "embedding_models": list(self.embedding_models.keys())
        }
    
    def get_multilingual_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del sistema multilingüe"""
        return {
            "supported_languages": len(self.language_codes),
            "loaded_spacy_models": len(self.language_models),
            "available_stemmers": len(self.stemmers),
            "available_stop_words": len(self.stop_words),
            "embedding_model": self.embedding_models['default'],
            "last_updated": datetime.now().isoformat()
        }


























