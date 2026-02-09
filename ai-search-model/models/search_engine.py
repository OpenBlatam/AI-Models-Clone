"""
AI Search Engine - Motor de búsqueda inteligente
Implementa búsqueda semántica, por palabras clave e híbrida
"""

import asyncio
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import json
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class AISearchEngine:
    """
    Motor de búsqueda inteligente que combina múltiples técnicas:
    - Búsqueda semántica con embeddings
    - Búsqueda por palabras clave con TF-IDF
    - Búsqueda híbrida que combina ambos métodos
    """
    
    def __init__(self):
        self.semantic_model = None
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self.document_embeddings = None
        self.documents = []
        self.document_metadata = {}
        self.is_initialized = False
        
        # Configuración
        self.embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self.max_query_length = 512
        self.snippet_length = 200
        
    async def initialize(self):
        """Inicializar el motor de búsqueda"""
        try:
            logger.info("Inicializando AI Search Engine...")
            
            # Cargar modelo de embeddings semánticos
            logger.info("Cargando modelo de embeddings...")
            self.semantic_model = SentenceTransformer(self.embedding_model_name)
            
            # Inicializar vectorizador TF-IDF
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=10000,
                stop_words='english',
                ngram_range=(1, 2),
                lowercase=True,
                strip_accents='unicode'
            )
            
            self.is_initialized = True
            logger.info("AI Search Engine inicializado correctamente")
            
        except Exception as e:
            logger.error(f"Error al inicializar AI Search Engine: {e}")
            raise
    
    async def add_documents(self, documents: List[Dict[str, Any]]):
        """Agregar documentos al índice de búsqueda"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            logger.info(f"Agregando {len(documents)} documentos al índice...")
            
            # Procesar documentos
            processed_docs = []
            for doc in documents:
                processed_doc = self._preprocess_document(doc)
                processed_docs.append(processed_doc)
                self.documents.append(processed_doc)
                self.document_metadata[doc['document_id']] = doc.get('metadata', {})
            
            # Actualizar embeddings semánticos
            await self._update_semantic_embeddings(processed_docs)
            
            # Actualizar matriz TF-IDF
            await self._update_tfidf_matrix()
            
            logger.info(f"Documentos agregados exitosamente. Total: {len(self.documents)}")
            
        except Exception as e:
            logger.error(f"Error al agregar documentos: {e}")
            raise
    
    async def search(
        self, 
        query: str, 
        limit: int = 10, 
        filters: Optional[Dict[str, Any]] = None,
        search_type: str = "semantic"
    ) -> List[Dict[str, Any]]:
        """
        Realizar búsqueda en los documentos
        
        Args:
            query: Consulta de búsqueda
            limit: Número máximo de resultados
            filters: Filtros adicionales
            search_type: Tipo de búsqueda (semantic, keyword, hybrid)
        """
        try:
            if not self.is_initialized:
                await self.initialize()
            
            if not self.documents:
                return []
            
            logger.info(f"Realizando búsqueda: '{query}' (tipo: {search_type})")
            
            # Preprocesar consulta
            processed_query = self._preprocess_query(query)
            
            # Realizar búsqueda según el tipo
            if search_type == "semantic":
                results = await self._semantic_search(processed_query, limit)
            elif search_type == "keyword":
                results = await self._keyword_search(processed_query, limit)
            elif search_type == "hybrid":
                results = await self._hybrid_search(processed_query, limit)
            else:
                raise ValueError(f"Tipo de búsqueda no válido: {search_type}")
            
            # Aplicar filtros si se especifican
            if filters:
                results = self._apply_filters(results, filters)
            
            # Generar snippets para los resultados
            results = self._generate_snippets(results, query)
            
            logger.info(f"Búsqueda completada: {len(results)} resultados")
            return results
            
        except Exception as e:
            logger.error(f"Error en búsqueda: {e}")
            raise
    
    async def _semantic_search(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Búsqueda semántica usando embeddings"""
        try:
            # Generar embedding de la consulta
            query_embedding = self.semantic_model.encode([query])
            
            # Calcular similitudes
            similarities = cosine_similarity(query_embedding, self.document_embeddings)[0]
            
            # Obtener índices ordenados por similitud
            sorted_indices = np.argsort(similarities)[::-1]
            
            # Construir resultados
            results = []
            for idx in sorted_indices[:limit]:
                if similarities[idx] > 0.1:  # Umbral mínimo de similitud
                    doc = self.documents[idx]
                    results.append({
                        "document_id": doc["document_id"],
                        "title": doc["title"],
                        "content": doc["content"],
                        "score": float(similarities[idx]),
                        "metadata": self.document_metadata.get(doc["document_id"], {}),
                        "search_type": "semantic"
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error en búsqueda semántica: {e}")
            raise
    
    async def _keyword_search(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Búsqueda por palabras clave usando TF-IDF"""
        try:
            # Transformar consulta
            query_vector = self.tfidf_vectorizer.transform([query])
            
            # Calcular similitudes
            similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
            
            # Obtener índices ordenados por similitud
            sorted_indices = np.argsort(similarities)[::-1]
            
            # Construir resultados
            results = []
            for idx in sorted_indices[:limit]:
                if similarities[idx] > 0.01:  # Umbral mínimo de similitud
                    doc = self.documents[idx]
                    results.append({
                        "document_id": doc["document_id"],
                        "title": doc["title"],
                        "content": doc["content"],
                        "score": float(similarities[idx]),
                        "metadata": self.document_metadata.get(doc["document_id"], {}),
                        "search_type": "keyword"
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error en búsqueda por palabras clave: {e}")
            raise
    
    async def _hybrid_search(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Búsqueda híbrida que combina semántica y palabras clave"""
        try:
            # Realizar ambas búsquedas
            semantic_results = await self._semantic_search(query, limit * 2)
            keyword_results = await self._keyword_search(query, limit * 2)
            
            # Combinar y puntuar resultados
            combined_scores = {}
            
            # Peso para búsqueda semántica (0.7) y palabras clave (0.3)
            semantic_weight = 0.7
            keyword_weight = 0.3
            
            # Procesar resultados semánticos
            for result in semantic_results:
                doc_id = result["document_id"]
                combined_scores[doc_id] = {
                    "document": result,
                    "semantic_score": result["score"],
                    "keyword_score": 0.0,
                    "combined_score": result["score"] * semantic_weight
                }
            
            # Procesar resultados de palabras clave
            for result in keyword_results:
                doc_id = result["document_id"]
                if doc_id in combined_scores:
                    combined_scores[doc_id]["keyword_score"] = result["score"]
                    combined_scores[doc_id]["combined_score"] += result["score"] * keyword_weight
                else:
                    combined_scores[doc_id] = {
                        "document": result,
                        "semantic_score": 0.0,
                        "keyword_score": result["score"],
                        "combined_score": result["score"] * keyword_weight
                    }
            
            # Ordenar por puntuación combinada
            sorted_results = sorted(
                combined_scores.values(),
                key=lambda x: x["combined_score"],
                reverse=True
            )
            
            # Construir resultados finales
            results = []
            for item in sorted_results[:limit]:
                doc = item["document"]
                doc["score"] = item["combined_score"]
                doc["search_type"] = "hybrid"
                doc["semantic_score"] = item["semantic_score"]
                doc["keyword_score"] = item["keyword_score"]
                results.append(doc)
            
            return results
            
        except Exception as e:
            logger.error(f"Error en búsqueda híbrida: {e}")
            raise
    
    def _preprocess_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocesar documento para indexación"""
        try:
            # Limpiar y normalizar contenido
            content = self._clean_text(document["content"])
            title = self._clean_text(document["title"])
            
            return {
                "document_id": document["document_id"],
                "title": title,
                "content": content,
                "original_content": document["content"],
                "original_title": document["title"]
            }
            
        except Exception as e:
            logger.error(f"Error al preprocesar documento: {e}")
            raise
    
    def _preprocess_query(self, query: str) -> str:
        """Preprocesar consulta de búsqueda"""
        try:
            # Limpiar y normalizar consulta
            cleaned_query = self._clean_text(query)
            
            # Truncar si es muy larga
            if len(cleaned_query) > self.max_query_length:
                cleaned_query = cleaned_query[:self.max_query_length]
            
            return cleaned_query
            
        except Exception as e:
            logger.error(f"Error al preprocesar consulta: {e}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """Limpiar y normalizar texto"""
        if not text:
            return ""
        
        # Convertir a minúsculas
        text = text.lower()
        
        # Remover caracteres especiales excesivos
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-]', ' ', text)
        
        # Normalizar espacios en blanco
        text = re.sub(r'\s+', ' ', text)
        
        # Remover espacios al inicio y final
        text = text.strip()
        
        return text
    
    async def _update_semantic_embeddings(self, documents: List[Dict[str, Any]]):
        """Actualizar embeddings semánticos"""
        try:
            # Preparar textos para embedding
            texts = []
            for doc in documents:
                # Combinar título y contenido para el embedding
                combined_text = f"{doc['title']} {doc['content']}"
                texts.append(combined_text)
            
            # Generar embeddings
            new_embeddings = self.semantic_model.encode(texts)
            
            # Actualizar matriz de embeddings
            if self.document_embeddings is None:
                self.document_embeddings = new_embeddings
            else:
                self.document_embeddings = np.vstack([self.document_embeddings, new_embeddings])
            
            logger.info(f"Embeddings semánticos actualizados: {len(self.document_embeddings)} documentos")
            
        except Exception as e:
            logger.error(f"Error al actualizar embeddings semánticos: {e}")
            raise
    
    async def _update_tfidf_matrix(self):
        """Actualizar matriz TF-IDF"""
        try:
            # Preparar textos para TF-IDF
            texts = []
            for doc in self.documents:
                combined_text = f"{doc['title']} {doc['content']}"
                texts.append(combined_text)
            
            # Actualizar matriz TF-IDF
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
            
            logger.info(f"Matriz TF-IDF actualizada: {self.tfidf_matrix.shape}")
            
        except Exception as e:
            logger.error(f"Error al actualizar matriz TF-IDF: {e}")
            raise
    
    def _apply_filters(self, results: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Aplicar filtros a los resultados"""
        try:
            filtered_results = []
            
            for result in results:
                metadata = result.get("metadata", {})
                include_result = True
                
                # Aplicar filtros
                for key, value in filters.items():
                    if key in metadata:
                        if isinstance(value, list):
                            if metadata[key] not in value:
                                include_result = False
                                break
                        else:
                            if metadata[key] != value:
                                include_result = False
                                break
                    else:
                        # Si el filtro no existe en metadata, excluir resultado
                        include_result = False
                        break
                
                if include_result:
                    filtered_results.append(result)
            
            return filtered_results
            
        except Exception as e:
            logger.error(f"Error al aplicar filtros: {e}")
            return results
    
    def _generate_snippets(self, results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Generar snippets destacados para los resultados"""
        try:
            query_words = set(query.lower().split())
            
            for result in results:
                content = result["content"]
                
                # Buscar la mejor sección que contenga palabras de la consulta
                sentences = content.split('. ')
                best_sentence = ""
                max_matches = 0
                
                for sentence in sentences:
                    sentence_words = set(sentence.lower().split())
                    matches = len(query_words.intersection(sentence_words))
                    if matches > max_matches:
                        max_matches = matches
                        best_sentence = sentence
                
                # Si no se encuentra una buena coincidencia, tomar el inicio
                if not best_sentence:
                    best_sentence = content[:self.snippet_length]
                
                # Truncar snippet si es muy largo
                if len(best_sentence) > self.snippet_length:
                    best_sentence = best_sentence[:self.snippet_length] + "..."
                
                result["snippet"] = best_sentence
            
            return results
            
        except Exception as e:
            logger.error(f"Error al generar snippets: {e}")
            # Si hay error, usar contenido truncado como snippet
            for result in results:
                content = result["content"]
                result["snippet"] = content[:self.snippet_length] + "..." if len(content) > self.snippet_length else content
            return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas del motor de búsqueda"""
        try:
            return {
                "total_documents": len(self.documents),
                "embedding_model": self.embedding_model_name,
                "embedding_dimensions": self.document_embeddings.shape[1] if self.document_embeddings is not None else 0,
                "tfidf_features": self.tfidf_matrix.shape[1] if self.tfidf_matrix is not None else 0,
                "is_initialized": self.is_initialized,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error al obtener estadísticas: {e}")
            return {}



























