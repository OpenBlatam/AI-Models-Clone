"""
AI Chatbot - Chatbot de IA para Asistencia de Documentos
Sistema de chatbot inteligente que puede responder preguntas sobre documentos
"""

import asyncio
import logging
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import openai
from sentence_transformers import SentenceTransformer
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer

logger = logging.getLogger(__name__)

@dataclass
class ChatMessage:
    """Estructura de un mensaje de chat"""
    id: str
    user_id: str
    message: str
    response: str
    timestamp: str
    message_type: str = "user"  # user, assistant, system
    confidence_score: float = 0.0
    source_documents: List[str] = None
    intent: str = None
    entities: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.source_documents is None:
            self.source_documents = []
        if self.entities is None:
            self.entities = {}

@dataclass
class ChatSession:
    """Sesión de chat"""
    session_id: str
    user_id: str
    messages: List[ChatMessage]
    context: Dict[str, Any]
    created_at: str
    last_activity: str
    is_active: bool = True

class AIChatbot:
    """
    Chatbot de IA avanzado para asistencia con documentos
    """
    
    def __init__(self, openai_api_key: str = None):
        self.openai_api_key = openai_api_key
        self.sessions: Dict[str, ChatSession] = {}
        self.document_knowledge_base: Dict[str, str] = {}
        self.intent_classifier = None
        self.entity_extractor = None
        self.sentence_transformer = None
        self.lemmatizer = None
        self.stop_words = set()
        
        # Configurar OpenAI si está disponible
        if openai_api_key:
            openai.api_key = openai_api_key
        
        # Inicializar NLTK
        self._initialize_nltk()
    
    async def initialize(self):
        """Inicializar el chatbot"""
        try:
            logger.info("Inicializando chatbot de IA...")
            
            # Inicializar modelo de embeddings
            self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Inicializar lemmatizer
            self.lemmatizer = WordNetLemmatizer()
            
            # Cargar stop words
            self.stop_words = set(stopwords.words('english'))
            
            # Entrenar clasificador de intenciones
            await self._train_intent_classifier()
            
            logger.info("Chatbot de IA inicializado exitosamente")
            
        except Exception as e:
            logger.error(f"Error inicializando chatbot: {e}")
            raise
    
    def _initialize_nltk(self):
        """Inicializar recursos de NLTK"""
        try:
            import nltk
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
        except Exception as e:
            logger.warning(f"No se pudieron descargar recursos de NLTK: {e}")
    
    async def _train_intent_classifier(self):
        """Entrenar clasificador de intenciones"""
        try:
            # Intenciones predefinidas con ejemplos
            intent_examples = {
                "search_document": [
                    "buscar documento", "encontrar información", "buscar en", "dónde está",
                    "necesito información sobre", "busca", "encuentra"
                ],
                "explain_concept": [
                    "qué significa", "explica", "definir", "qué es", "cómo funciona",
                    "puedes explicar", "ayúdame a entender"
                ],
                "summarize": [
                    "resumen", "resumir", "síntesis", "puntos principales",
                    "haz un resumen de", "cuéntame en pocas palabras"
                ],
                "compare": [
                    "comparar", "diferencias", "similitudes", "vs", "versus",
                    "cuál es mejor", "diferencias entre"
                ],
                "recommend": [
                    "recomendar", "sugerir", "qué me recomiendas", "cuál prefieres",
                    "mejor opción", "debería usar"
                ],
                "help": [
                    "ayuda", "help", "cómo usar", "tutorial", "guía",
                    "no entiendo", "cómo funciona esto"
                ]
            }
            
            # Crear vectorizador TF-IDF
            all_texts = []
            all_intents = []
            
            for intent, examples in intent_examples.items():
                for example in examples:
                    all_texts.append(example)
                    all_intents.append(intent)
            
            self.intent_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
            intent_vectors = self.intent_vectorizer.fit_transform(all_texts)
            
            # Crear diccionario de intenciones
            self.intent_examples = intent_examples
            self.intent_vectors = intent_vectors
            self.intent_labels = all_intents
            
            logger.info("Clasificador de intenciones entrenado")
            
        except Exception as e:
            logger.error(f"Error entrenando clasificador de intenciones: {e}")
    
    async def create_session(self, user_id: str) -> str:
        """Crear nueva sesión de chat"""
        try:
            session_id = f"session_{user_id}_{int(datetime.now().timestamp())}"
            
            session = ChatSession(
                session_id=session_id,
                user_id=user_id,
                messages=[],
                context={},
                created_at=datetime.now().isoformat(),
                last_activity=datetime.now().isoformat()
            )
            
            self.sessions[session_id] = session
            
            # Mensaje de bienvenida
            welcome_message = ChatMessage(
                id=f"msg_{int(datetime.now().timestamp())}",
                user_id=user_id,
                message="",
                response="¡Hola! Soy tu asistente de IA. Puedo ayudarte a buscar información en tus documentos, explicar conceptos, hacer resúmenes y mucho más. ¿En qué puedo ayudarte?",
                timestamp=datetime.now().isoformat(),
                message_type="assistant"
            )
            
            session.messages.append(welcome_message)
            
            logger.info(f"Sesión de chat creada: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Error creando sesión de chat: {e}")
            raise
    
    async def send_message(self, session_id: str, message: str, 
                          search_engine=None, vector_db=None) -> ChatMessage:
        """Enviar mensaje al chatbot"""
        try:
            if session_id not in self.sessions:
                raise ValueError(f"Sesión no encontrada: {session_id}")
            
            session = self.sessions[session_id]
            
            # Crear mensaje del usuario
            user_message = ChatMessage(
                id=f"msg_{int(datetime.now().timestamp())}",
                user_id=session.user_id,
                message=message,
                response="",
                timestamp=datetime.now().isoformat(),
                message_type="user"
            )
            
            # Procesar mensaje
            response = await self._process_message(
                message, session, search_engine, vector_db
            )
            
            # Crear respuesta del asistente
            assistant_message = ChatMessage(
                id=f"msg_{int(datetime.now().timestamp())}",
                user_id=session.user_id,
                message=message,
                response=response["response"],
                timestamp=datetime.now().isoformat(),
                message_type="assistant",
                confidence_score=response["confidence"],
                source_documents=response.get("sources", []),
                intent=response.get("intent"),
                entities=response.get("entities", {})
            )
            
            # Agregar mensajes a la sesión
            session.messages.append(user_message)
            session.messages.append(assistant_message)
            session.last_activity = datetime.now().isoformat()
            
            # Mantener solo los últimos 20 mensajes
            if len(session.messages) > 20:
                session.messages = session.messages[-20:]
            
            logger.info(f"Mensaje procesado en sesión {session_id}")
            return assistant_message
            
        except Exception as e:
            logger.error(f"Error procesando mensaje: {e}")
            raise
    
    async def _process_message(self, message: str, session: ChatSession,
                              search_engine=None, vector_db=None) -> Dict[str, Any]:
        """Procesar mensaje del usuario"""
        try:
            # Detectar intención
            intent = await self._detect_intent(message)
            
            # Extraer entidades
            entities = await self._extract_entities(message)
            
            # Generar respuesta basada en la intención
            if intent == "search_document":
                response = await self._handle_search_intent(
                    message, entities, search_engine, vector_db
                )
            elif intent == "explain_concept":
                response = await self._handle_explain_intent(
                    message, entities, search_engine, vector_db
                )
            elif intent == "summarize":
                response = await self._handle_summarize_intent(
                    message, entities, search_engine, vector_db
                )
            elif intent == "compare":
                response = await self._handle_compare_intent(
                    message, entities, search_engine, vector_db
                )
            elif intent == "recommend":
                response = await self._handle_recommend_intent(
                    message, entities, search_engine, vector_db
                )
            elif intent == "help":
                response = await self._handle_help_intent(message)
            else:
                response = await self._handle_general_intent(
                    message, search_engine, vector_db
                )
            
            return {
                "response": response["text"],
                "confidence": response["confidence"],
                "sources": response.get("sources", []),
                "intent": intent,
                "entities": entities
            }
            
        except Exception as e:
            logger.error(f"Error procesando mensaje: {e}")
            return {
                "response": "Lo siento, hubo un error procesando tu mensaje. ¿Podrías intentar de nuevo?",
                "confidence": 0.0,
                "sources": [],
                "intent": "error",
                "entities": {}
            }
    
    async def _detect_intent(self, message: str) -> str:
        """Detectar intención del mensaje"""
        try:
            if not hasattr(self, 'intent_vectorizer'):
                return "general"
            
            # Vectorizar mensaje
            message_vector = self.intent_vectorizer.transform([message])
            
            # Calcular similitud con ejemplos de intenciones
            similarities = cosine_similarity(message_vector, self.intent_vectors)[0]
            
            # Encontrar la intención más similar
            max_similarity_idx = np.argmax(similarities)
            max_similarity = similarities[max_similarity_idx]
            
            # Si la similitud es muy baja, usar intención general
            if max_similarity < 0.3:
                return "general"
            
            return self.intent_labels[max_similarity_idx]
            
        except Exception as e:
            logger.error(f"Error detectando intención: {e}")
            return "general"
    
    async def _extract_entities(self, message: str) -> Dict[str, Any]:
        """Extraer entidades del mensaje"""
        try:
            entities = {}
            
            # Extraer palabras clave importantes
            words = word_tokenize(message.lower())
            important_words = [word for word in words 
                             if word not in self.stop_words and len(word) > 2]
            
            entities["keywords"] = important_words
            
            # Detectar números
            numbers = re.findall(r'\d+', message)
            if numbers:
                entities["numbers"] = numbers
            
            # Detectar fechas (formato básico)
            date_patterns = [
                r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
                r'\d{1,2}/\d{1,2}/\d{4}',  # MM/DD/YYYY
                r'\d{1,2}-\d{1,2}-\d{4}'   # MM-DD-YYYY
            ]
            
            dates = []
            for pattern in date_patterns:
                dates.extend(re.findall(pattern, message))
            
            if dates:
                entities["dates"] = dates
            
            # Detectar URLs
            url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            urls = re.findall(url_pattern, message)
            if urls:
                entities["urls"] = urls
            
            return entities
            
        except Exception as e:
            logger.error(f"Error extrayendo entidades: {e}")
            return {}
    
    async def _handle_search_intent(self, message: str, entities: Dict[str, Any],
                                   search_engine=None, vector_db=None) -> Dict[str, Any]:
        """Manejar intención de búsqueda"""
        try:
            if not search_engine or not vector_db:
                return {
                    "text": "No tengo acceso al motor de búsqueda en este momento.",
                    "confidence": 0.0
                }
            
            # Extraer términos de búsqueda
            search_terms = entities.get("keywords", [])
            if not search_terms:
                search_terms = message.split()
            
            query = " ".join(search_terms)
            
            # Realizar búsqueda
            results = await search_engine.hybrid_search(query, limit=5)
            
            if not results:
                return {
                    "text": f"No encontré documentos relacionados con '{query}'. ¿Podrías ser más específico?",
                    "confidence": 0.3
                }
            
            # Formatear respuesta
            response_text = f"Encontré {len(results)} documentos relacionados con '{query}':\n\n"
            
            for i, result in enumerate(results[:3], 1):
                title = result.get("title", "Sin título")
                content = result.get("content", "")[:200] + "..."
                score = result.get("score", 0)
                
                response_text += f"{i}. **{title}** (Relevancia: {score:.2f})\n"
                response_text += f"   {content}\n\n"
            
            if len(results) > 3:
                response_text += f"Y {len(results) - 3} documentos más..."
            
            return {
                "text": response_text,
                "confidence": 0.8,
                "sources": [r.get("document_id") for r in results]
            }
            
        except Exception as e:
            logger.error(f"Error manejando intención de búsqueda: {e}")
            return {
                "text": "Hubo un error buscando en los documentos.",
                "confidence": 0.0
            }
    
    async def _handle_explain_intent(self, message: str, entities: Dict[str, Any],
                                    search_engine=None, vector_db=None) -> Dict[str, Any]:
        """Manejar intención de explicación"""
        try:
            # Extraer concepto a explicar
            keywords = entities.get("keywords", [])
            if not keywords:
                return {
                    "text": "¿Qué concepto te gustaría que explique?",
                    "confidence": 0.3
                }
            
            concept = " ".join(keywords[:3])  # Usar las primeras 3 palabras clave
            
            # Buscar información sobre el concepto
            if search_engine and vector_db:
                results = await search_engine.semantic_search(concept, limit=3)
                
                if results:
                    # Combinar información de los documentos
                    explanation_parts = []
                    sources = []
                    
                    for result in results:
                        content = result.get("content", "")
                        # Extraer oraciones relevantes
                        sentences = sent_tokenize(content)
                        relevant_sentences = [s for s in sentences 
                                            if any(keyword in s.lower() for keyword in keywords)]
                        
                        if relevant_sentences:
                            explanation_parts.extend(relevant_sentences[:2])
                            sources.append(result.get("document_id"))
                    
                    if explanation_parts:
                        explanation = " ".join(explanation_parts[:3])
                        response_text = f"**{concept.title()}**:\n\n{explanation}"
                        
                        return {
                            "text": response_text,
                            "confidence": 0.7,
                            "sources": sources
                        }
            
            # Respuesta genérica si no se encuentra información específica
            return {
                "text": f"Basándome en los documentos disponibles, {concept} es un concepto importante. Te recomiendo buscar más información específica sobre este tema.",
                "confidence": 0.4
            }
            
        except Exception as e:
            logger.error(f"Error manejando intención de explicación: {e}")
            return {
                "text": "No pude generar una explicación en este momento.",
                "confidence": 0.0
            }
    
    async def _handle_summarize_intent(self, message: str, entities: Dict[str, Any],
                                      search_engine=None, vector_db=None) -> Dict[str, Any]:
        """Manejar intención de resumen"""
        try:
            # Extraer tema para resumir
            keywords = entities.get("keywords", [])
            if not keywords:
                return {
                    "text": "¿Sobre qué tema te gustaría que haga un resumen?",
                    "confidence": 0.3
                }
            
            topic = " ".join(keywords)
            
            # Buscar documentos relacionados
            if search_engine and vector_db:
                results = await search_engine.semantic_search(topic, limit=5)
                
                if results:
                    # Combinar contenido de los documentos
                    all_content = []
                    sources = []
                    
                    for result in results:
                        content = result.get("content", "")
                        all_content.append(content)
                        sources.append(result.get("document_id"))
                    
                    # Crear resumen simple (primeras oraciones de cada documento)
                    summary_parts = []
                    for content in all_content[:3]:
                        sentences = sent_tokenize(content)
                        if sentences:
                            summary_parts.append(sentences[0])
                    
                    if summary_parts:
                        summary = " ".join(summary_parts)
                        response_text = f"**Resumen sobre {topic}**:\n\n{summary}"
                        
                        return {
                            "text": response_text,
                            "confidence": 0.6,
                            "sources": sources
                        }
            
            return {
                "text": f"No pude generar un resumen sobre '{topic}' con la información disponible.",
                "confidence": 0.3
            }
            
        except Exception as e:
            logger.error(f"Error manejando intención de resumen: {e}")
            return {
                "text": "No pude generar un resumen en este momento.",
                "confidence": 0.0
            }
    
    async def _handle_compare_intent(self, message: str, entities: Dict[str, Any],
                                    search_engine=None, vector_db=None) -> Dict[str, Any]:
        """Manejar intención de comparación"""
        try:
            # Extraer elementos a comparar
            keywords = entities.get("keywords", [])
            if len(keywords) < 2:
                return {
                    "text": "¿Qué elementos te gustaría comparar? Por ejemplo: 'comparar Python vs Java'",
                    "confidence": 0.3
                }
            
            # Buscar información sobre cada elemento
            comparisons = []
            all_sources = []
            
            for keyword in keywords[:2]:  # Comparar máximo 2 elementos
                if search_engine and vector_db:
                    results = await search_engine.semantic_search(keyword, limit=2)
                    
                    if results:
                        content = results[0].get("content", "")
                        sentences = sent_tokenize(content)
                        relevant_sentences = [s for s in sentences 
                                            if keyword.lower() in s.lower()][:2]
                        
                        if relevant_sentences:
                            comparisons.append({
                                "item": keyword,
                                "description": " ".join(relevant_sentences)
                            })
                            all_sources.append(results[0].get("document_id"))
            
            if len(comparisons) >= 2:
                response_text = f"**Comparación entre {comparisons[0]['item']} y {comparisons[1]['item']}**:\n\n"
                response_text += f"**{comparisons[0]['item']}**: {comparisons[0]['description']}\n\n"
                response_text += f"**{comparisons[1]['item']}**: {comparisons[1]['description']}"
                
                return {
                    "text": response_text,
                    "confidence": 0.6,
                    "sources": all_sources
                }
            
            return {
                "text": "No pude encontrar suficiente información para hacer una comparación detallada.",
                "confidence": 0.3
            }
            
        except Exception as e:
            logger.error(f"Error manejando intención de comparación: {e}")
            return {
                "text": "No pude realizar la comparación en este momento.",
                "confidence": 0.0
            }
    
    async def _handle_recommend_intent(self, message: str, entities: Dict[str, Any],
                                      search_engine=None, vector_db=None) -> Dict[str, Any]:
        """Manejar intención de recomendación"""
        try:
            # Extraer contexto para la recomendación
            keywords = entities.get("keywords", [])
            
            if not keywords:
                return {
                    "text": "¿Sobre qué tema te gustaría una recomendación?",
                    "confidence": 0.3
                }
            
            topic = " ".join(keywords)
            
            # Buscar documentos relacionados para hacer recomendaciones
            if search_engine and vector_db:
                results = await search_engine.semantic_search(topic, limit=5)
                
                if results:
                    # Seleccionar los mejores documentos
                    top_results = results[:3]
                    
                    response_text = f"**Recomendaciones sobre {topic}**:\n\n"
                    
                    for i, result in enumerate(top_results, 1):
                        title = result.get("title", "Sin título")
                        score = result.get("score", 0)
                        
                        response_text += f"{i}. **{title}** (Relevancia: {score:.2f})\n"
                    
                    response_text += f"\nEstos son los documentos más relevantes sobre '{topic}' en tu colección."
                    
                    return {
                        "text": response_text,
                        "confidence": 0.7,
                        "sources": [r.get("document_id") for r in top_results]
                    }
            
            return {
                "text": f"No encontré documentos específicos sobre '{topic}' para hacer recomendaciones.",
                "confidence": 0.3
            }
            
        except Exception as e:
            logger.error(f"Error manejando intención de recomendación: {e}")
            return {
                "text": "No pude generar recomendaciones en este momento.",
                "confidence": 0.0
            }
    
    async def _handle_help_intent(self, message: str) -> Dict[str, Any]:
        """Manejar intención de ayuda"""
        help_text = """
**¿Cómo puedo ayudarte?**

Puedo asistirte con las siguientes tareas:

🔍 **Búsqueda**: "buscar información sobre machine learning"
📖 **Explicaciones**: "qué significa deep learning"
📝 **Resúmenes**: "resumir el documento sobre IA"
⚖️ **Comparaciones**: "comparar Python vs Java"
💡 **Recomendaciones**: "recomiéndame documentos sobre web development"
❓ **Ayuda**: "cómo usar el sistema"

**Ejemplos de preguntas:**
- "Busca documentos sobre inteligencia artificial"
- "Explica qué es machine learning"
- "Haz un resumen de los documentos sobre Python"
- "Compara React vs Vue"
- "Recomiéndame algo sobre bases de datos"

¿En qué más puedo ayudarte?
        """
        
        return {
            "text": help_text,
            "confidence": 1.0
        }
    
    async def _handle_general_intent(self, message: str, search_engine=None, 
                                    vector_db=None) -> Dict[str, Any]:
        """Manejar intención general"""
        try:
            # Intentar búsqueda general
            if search_engine and vector_db:
                results = await search_engine.semantic_search(message, limit=3)
                
                if results:
                    response_text = f"Encontré información relacionada con tu consulta:\n\n"
                    
                    for i, result in enumerate(results, 1):
                        title = result.get("title", "Sin título")
                        content = result.get("content", "")[:150] + "..."
                        
                        response_text += f"{i}. **{title}**\n{content}\n\n"
                    
                    return {
                        "text": response_text,
                        "confidence": 0.5,
                        "sources": [r.get("document_id") for r in results]
                    }
            
            # Respuesta genérica
            return {
                "text": "Entiendo tu consulta. ¿Podrías ser más específico sobre lo que necesitas? Por ejemplo, puedes pedirme que busque información, explique conceptos, o haga resúmenes.",
                "confidence": 0.3
            }
            
        except Exception as e:
            logger.error(f"Error manejando intención general: {e}")
            return {
                "text": "No pude procesar tu consulta. ¿Podrías intentar de nuevo?",
                "confidence": 0.0
            }
    
    async def get_session_history(self, session_id: str, limit: int = 10) -> List[ChatMessage]:
        """Obtener historial de una sesión"""
        try:
            if session_id not in self.sessions:
                return []
            
            session = self.sessions[session_id]
            return session.messages[-limit:] if limit else session.messages
            
        except Exception as e:
            logger.error(f"Error obteniendo historial de sesión: {e}")
            return []
    
    async def end_session(self, session_id: str) -> bool:
        """Terminar sesión de chat"""
        try:
            if session_id in self.sessions:
                self.sessions[session_id].is_active = False
                del self.sessions[session_id]
                logger.info(f"Sesión terminada: {session_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error terminando sesión: {e}")
            return False
    
    def get_active_sessions(self) -> List[str]:
        """Obtener sesiones activas"""
        return [session_id for session_id, session in self.sessions.items() 
                if session.is_active]
    
    def get_chatbot_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del chatbot"""
        try:
            total_messages = sum(len(session.messages) for session in self.sessions.values())
            active_sessions = len(self.get_active_sessions())
            
            # Contar intenciones
            intent_counts = {}
            for session in self.sessions.values():
                for message in session.messages:
                    if message.intent:
                        intent_counts[message.intent] = intent_counts.get(message.intent, 0) + 1
            
            return {
                "total_sessions": len(self.sessions),
                "active_sessions": active_sessions,
                "total_messages": total_messages,
                "intent_distribution": intent_counts,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas del chatbot: {e}")
            return {}


























