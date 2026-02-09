"""
Recommendation Engine - Motor de Recomendaciones
Sistema inteligente de recomendaciones basado en comportamiento del usuario
"""

import asyncio
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import pickle
import os

logger = logging.getLogger(__name__)

class RecommendationEngine:
    """
    Motor de recomendaciones que analiza patrones de búsqueda y comportamiento
    para sugerir contenido relevante a los usuarios
    """
    
    def __init__(self):
        self.user_profiles = {}
        self.document_profiles = {}
        self.search_history = []
        self.recommendation_models = {}
        self.collaborative_filter = None
        self.content_based_filter = None
        
    async def initialize(self):
        """Inicializar el motor de recomendaciones"""
        try:
            logger.info("Inicializando motor de recomendaciones...")
            
            # Cargar modelos existentes si están disponibles
            await self._load_models()
            
            logger.info("Motor de recomendaciones inicializado")
            
        except Exception as e:
            logger.error(f"Error inicializando motor de recomendaciones: {e}")
            raise
    
    async def add_search_interaction(self, user_id: str, query: str, 
                                   results: List[Dict], clicked_docs: List[str] = None):
        """Agregar interacción de búsqueda del usuario"""
        try:
            interaction = {
                "user_id": user_id,
                "query": query,
                "results": results,
                "clicked_docs": clicked_docs or [],
                "timestamp": datetime.now().isoformat(),
                "session_id": f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
            
            self.search_history.append(interaction)
            
            # Actualizar perfil del usuario
            await self._update_user_profile(user_id, interaction)
            
            # Actualizar perfiles de documentos
            await self._update_document_profiles(results, clicked_docs)
            
            logger.info(f"Interacción agregada para usuario {user_id}")
            
        except Exception as e:
            logger.error(f"Error agregando interacción: {e}")
    
    async def get_recommendations(self, user_id: str, limit: int = 10, 
                                recommendation_type: str = "hybrid") -> List[Dict[str, Any]]:
        """Obtener recomendaciones para un usuario"""
        try:
            logger.info(f"Generando recomendaciones para usuario {user_id}")
            
            if recommendation_type == "collaborative":
                recommendations = await self._get_collaborative_recommendations(user_id, limit)
            elif recommendation_type == "content_based":
                recommendations = await self._get_content_based_recommendations(user_id, limit)
            elif recommendation_type == "trending":
                recommendations = await self._get_trending_recommendations(limit)
            else:  # hybrid
                recommendations = await self._get_hybrid_recommendations(user_id, limit)
            
            # Agregar metadatos de recomendación
            for rec in recommendations:
                rec["recommendation_type"] = recommendation_type
                rec["generated_at"] = datetime.now().isoformat()
                rec["confidence_score"] = rec.get("score", 0.0)
            
            logger.info(f"Generadas {len(recommendations)} recomendaciones")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generando recomendaciones: {e}")
            return []
    
    async def get_similar_documents(self, document_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Obtener documentos similares a uno dado"""
        try:
            if document_id not in self.document_profiles:
                return []
            
            target_doc = self.document_profiles[document_id]
            similarities = []
            
            for doc_id, doc_profile in self.document_profiles.items():
                if doc_id != document_id:
                    similarity = self._calculate_document_similarity(target_doc, doc_profile)
                    similarities.append({
                        "document_id": doc_id,
                        "similarity_score": similarity,
                        "title": doc_profile.get("title", ""),
                        "content": doc_profile.get("content", "")[:200] + "...",
                        "metadata": doc_profile.get("metadata", {})
                    })
            
            # Ordenar por similitud y devolver los mejores
            similarities.sort(key=lambda x: x["similarity_score"], reverse=True)
            return similarities[:limit]
            
        except Exception as e:
            logger.error(f"Error obteniendo documentos similares: {e}")
            return []
    
    async def get_trending_content(self, time_range: str = "7d", limit: int = 10) -> List[Dict[str, Any]]:
        """Obtener contenido trending"""
        try:
            # Calcular rango de tiempo
            if time_range == "1d":
                cutoff = datetime.now() - timedelta(days=1)
            elif time_range == "7d":
                cutoff = datetime.now() - timedelta(days=7)
            elif time_range == "30d":
                cutoff = datetime.now() - timedelta(days=30)
            else:
                cutoff = datetime.now() - timedelta(days=7)
            
            # Contar interacciones por documento en el rango de tiempo
            doc_interactions = defaultdict(int)
            doc_queries = defaultdict(list)
            
            for interaction in self.search_history:
                interaction_time = datetime.fromisoformat(interaction["timestamp"])
                if interaction_time >= cutoff:
                    for result in interaction["results"]:
                        doc_id = result.get("document_id")
                        if doc_id:
                            doc_interactions[doc_id] += 1
                            doc_queries[doc_id].append(interaction["query"])
            
            # Crear lista de trending
            trending = []
            for doc_id, count in doc_interactions.items():
                if doc_id in self.document_profiles:
                    doc_profile = self.document_profiles[doc_id]
                    trending.append({
                        "document_id": doc_id,
                        "interaction_count": count,
                        "trending_score": count / len(self.search_history) if self.search_history else 0,
                        "title": doc_profile.get("title", ""),
                        "content": doc_profile.get("content", "")[:200] + "...",
                        "metadata": doc_profile.get("metadata", {}),
                        "popular_queries": list(set(doc_queries[doc_id]))[:5]
                    })
            
            # Ordenar por score de trending
            trending.sort(key=lambda x: x["trending_score"], reverse=True)
            return trending[:limit]
            
        except Exception as e:
            logger.error(f"Error obteniendo contenido trending: {e}")
            return []
    
    async def get_search_suggestions(self, partial_query: str, limit: int = 5) -> List[str]:
        """Obtener sugerencias de búsqueda basadas en consultas previas"""
        try:
            if not partial_query or len(partial_query) < 2:
                return []
            
            # Obtener todas las consultas únicas
            all_queries = set()
            for interaction in self.search_history:
                all_queries.add(interaction["query"])
            
            # Filtrar consultas que contengan el texto parcial
            suggestions = []
            partial_lower = partial_query.lower()
            
            for query in all_queries:
                if partial_lower in query.lower():
                    # Calcular relevancia basada en frecuencia y longitud
                    frequency = sum(1 for i in self.search_history if i["query"] == query)
                    relevance = frequency * (1 / len(query))  # Preferir consultas más cortas
                    suggestions.append((query, relevance))
            
            # Ordenar por relevancia
            suggestions.sort(key=lambda x: x[1], reverse=True)
            return [suggestion[0] for suggestion in suggestions[:limit]]
            
        except Exception as e:
            logger.error(f"Error obteniendo sugerencias: {e}")
            return []
    
    async def _get_collaborative_recommendations(self, user_id: str, limit: int) -> List[Dict[str, Any]]:
        """Recomendaciones basadas en filtrado colaborativo"""
        try:
            if user_id not in self.user_profiles:
                return []
            
            user_profile = self.user_profiles[user_id]
            user_interests = user_profile.get("interests", {})
            
            # Encontrar usuarios similares
            similar_users = []
            for other_user_id, other_profile in self.user_profiles.items():
                if other_user_id != user_id:
                    similarity = self._calculate_user_similarity(user_profile, other_profile)
                    if similarity > 0.3:  # Umbral de similitud
                        similar_users.append((other_user_id, similarity))
            
            # Obtener documentos que les gustaron a usuarios similares
            recommended_docs = defaultdict(float)
            for similar_user_id, similarity in similar_users:
                similar_user_profile = self.user_profiles[similar_user_id]
                for doc_id, rating in similar_user_profile.get("document_ratings", {}).items():
                    if doc_id not in user_profile.get("viewed_documents", set()):
                        recommended_docs[doc_id] += rating * similarity
            
            # Convertir a lista de recomendaciones
            recommendations = []
            for doc_id, score in recommended_docs.items():
                if doc_id in self.document_profiles:
                    doc_profile = self.document_profiles[doc_id]
                    recommendations.append({
                        "document_id": doc_id,
                        "score": score,
                        "title": doc_profile.get("title", ""),
                        "content": doc_profile.get("content", "")[:200] + "...",
                        "metadata": doc_profile.get("metadata", {}),
                        "reason": "Usuarios similares también vieron este contenido"
                    })
            
            recommendations.sort(key=lambda x: x["score"], reverse=True)
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Error en recomendaciones colaborativas: {e}")
            return []
    
    async def _get_content_based_recommendations(self, user_id: str, limit: int) -> List[Dict[str, Any]]:
        """Recomendaciones basadas en contenido"""
        try:
            if user_id not in self.user_profiles:
                return []
            
            user_profile = self.user_profiles[user_id]
            user_interests = user_profile.get("interests", {})
            
            # Obtener documentos que el usuario ya ha visto
            viewed_docs = user_profile.get("viewed_documents", set())
            
            # Encontrar documentos similares a los que le gustaron
            recommendations = []
            for viewed_doc_id in viewed_docs:
                if viewed_doc_id in self.document_profiles:
                    similar_docs = await self.get_similar_documents(viewed_doc_id, limit * 2)
                    for similar_doc in similar_docs:
                        if similar_doc["document_id"] not in viewed_docs:
                            recommendations.append({
                                **similar_doc,
                                "reason": "Similar al contenido que te gustó"
                            })
            
            # Eliminar duplicados y ordenar
            seen_docs = set()
            unique_recommendations = []
            for rec in recommendations:
                if rec["document_id"] not in seen_docs:
                    seen_docs.add(rec["document_id"])
                    unique_recommendations.append(rec)
            
            unique_recommendations.sort(key=lambda x: x["similarity_score"], reverse=True)
            return unique_recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Error en recomendaciones basadas en contenido: {e}")
            return []
    
    async def _get_trending_recommendations(self, limit: int) -> List[Dict[str, Any]]:
        """Recomendaciones basadas en contenido trending"""
        try:
            trending = await self.get_trending_content("7d", limit)
            return trending
            
        except Exception as e:
            logger.error(f"Error en recomendaciones trending: {e}")
            return []
    
    async def _get_hybrid_recommendations(self, user_id: str, limit: int) -> List[Dict[str, Any]]:
        """Recomendaciones híbridas que combinan múltiples métodos"""
        try:
            # Obtener recomendaciones de diferentes métodos
            collaborative_recs = await self._get_collaborative_recommendations(user_id, limit)
            content_recs = await self._get_content_based_recommendations(user_id, limit)
            trending_recs = await self._get_trending_recommendations(limit // 2)
            
            # Combinar y puntuar
            combined_scores = defaultdict(float)
            
            # Peso para cada tipo de recomendación
            weights = {
                "collaborative": 0.4,
                "content_based": 0.4,
                "trending": 0.2
            }
            
            # Procesar recomendaciones colaborativas
            for rec in collaborative_recs:
                doc_id = rec["document_id"]
                combined_scores[doc_id] += rec["score"] * weights["collaborative"]
            
            # Procesar recomendaciones basadas en contenido
            for rec in content_recs:
                doc_id = rec["document_id"]
                combined_scores[doc_id] += rec["similarity_score"] * weights["content_based"]
            
            # Procesar recomendaciones trending
            for rec in trending_recs:
                doc_id = rec["document_id"]
                combined_scores[doc_id] += rec["trending_score"] * weights["trending"]
            
            # Crear recomendaciones finales
            final_recommendations = []
            for doc_id, score in combined_scores.items():
                if doc_id in self.document_profiles:
                    doc_profile = self.document_profiles[doc_id]
                    final_recommendations.append({
                        "document_id": doc_id,
                        "score": score,
                        "title": doc_profile.get("title", ""),
                        "content": doc_profile.get("content", "")[:200] + "...",
                        "metadata": doc_profile.get("metadata", {}),
                        "reason": "Recomendación personalizada basada en tu actividad"
                    })
            
            final_recommendations.sort(key=lambda x: x["score"], reverse=True)
            return final_recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Error en recomendaciones híbridas: {e}")
            return []
    
    async def _update_user_profile(self, user_id: str, interaction: Dict[str, Any]):
        """Actualizar perfil del usuario"""
        try:
            if user_id not in self.user_profiles:
                self.user_profiles[user_id] = {
                    "interests": {},
                    "viewed_documents": set(),
                    "document_ratings": {},
                    "search_patterns": [],
                    "created_at": datetime.now().isoformat()
                }
            
            user_profile = self.user_profiles[user_id]
            
            # Actualizar documentos vistos
            for result in interaction["results"]:
                doc_id = result.get("document_id")
                if doc_id:
                    user_profile["viewed_documents"].add(doc_id)
                    
                    # Calcular rating implícito basado en posición y clicks
                    position = result.get("position", 0)
                    is_clicked = doc_id in interaction.get("clicked_docs", [])
                    rating = (1.0 / (position + 1)) * (2.0 if is_clicked else 1.0)
                    
                    if doc_id in user_profile["document_ratings"]:
                        user_profile["document_ratings"][doc_id] = (
                            user_profile["document_ratings"][doc_id] + rating
                        ) / 2
                    else:
                        user_profile["document_ratings"][doc_id] = rating
            
            # Actualizar patrones de búsqueda
            user_profile["search_patterns"].append({
                "query": interaction["query"],
                "timestamp": interaction["timestamp"],
                "results_count": len(interaction["results"])
            })
            
            # Actualizar intereses basados en consultas
            query_words = interaction["query"].lower().split()
            for word in query_words:
                if len(word) > 3:  # Ignorar palabras muy cortas
                    if word in user_profile["interests"]:
                        user_profile["interests"][word] += 1
                    else:
                        user_profile["interests"][word] = 1
            
            # Mantener solo los intereses más relevantes
            sorted_interests = sorted(
                user_profile["interests"].items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            user_profile["interests"] = dict(sorted_interests[:50])
            
        except Exception as e:
            logger.error(f"Error actualizando perfil de usuario: {e}")
    
    async def _update_document_profiles(self, results: List[Dict], clicked_docs: List[str] = None):
        """Actualizar perfiles de documentos"""
        try:
            clicked_docs = clicked_docs or []
            
            for result in results:
                doc_id = result.get("document_id")
                if doc_id and doc_id not in self.document_profiles:
                    self.document_profiles[doc_id] = {
                        "title": result.get("title", ""),
                        "content": result.get("content", ""),
                        "metadata": result.get("metadata", {}),
                        "view_count": 0,
                        "click_count": 0,
                        "avg_position": 0,
                        "queries": [],
                        "created_at": datetime.now().isoformat()
                    }
                
                if doc_id in self.document_profiles:
                    doc_profile = self.document_profiles[doc_id]
                    doc_profile["view_count"] += 1
                    
                    if doc_id in clicked_docs:
                        doc_profile["click_count"] += 1
                    
                    # Actualizar posición promedio
                    position = result.get("position", 0)
                    current_avg = doc_profile["avg_position"]
                    total_views = doc_profile["view_count"]
                    doc_profile["avg_position"] = (current_avg * (total_views - 1) + position) / total_views
                    
        except Exception as e:
            logger.error(f"Error actualizando perfiles de documentos: {e}")
    
    def _calculate_user_similarity(self, user1: Dict, user2: Dict) -> float:
        """Calcular similitud entre usuarios"""
        try:
            # Similitud basada en intereses
            interests1 = set(user1.get("interests", {}).keys())
            interests2 = set(user2.get("interests", {}).keys())
            
            if not interests1 or not interests2:
                return 0.0
            
            intersection = len(interests1.intersection(interests2))
            union = len(interests1.union(interests2))
            
            jaccard_similarity = intersection / union if union > 0 else 0.0
            
            # Similitud basada en documentos vistos
            docs1 = user1.get("viewed_documents", set())
            docs2 = user2.get("viewed_documents", set())
            
            if not docs1 or not docs2:
                return jaccard_similarity
            
            doc_intersection = len(docs1.intersection(docs2))
            doc_union = len(docs1.union(docs2))
            
            doc_similarity = doc_intersection / doc_union if doc_union > 0 else 0.0
            
            # Combinar similitudes
            return (jaccard_similarity * 0.6) + (doc_similarity * 0.4)
            
        except Exception as e:
            logger.error(f"Error calculando similitud de usuarios: {e}")
            return 0.0
    
    def _calculate_document_similarity(self, doc1: Dict, doc2: Dict) -> float:
        """Calcular similitud entre documentos"""
        try:
            # Similitud basada en contenido
            content1 = doc1.get("content", "")
            content2 = doc2.get("content", "")
            
            if not content1 or not content2:
                return 0.0
            
            # Usar TF-IDF para calcular similitud
            vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
            tfidf_matrix = vectorizer.fit_transform([content1, content2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            # Similitud basada en metadatos
            metadata1 = doc1.get("metadata", {})
            metadata2 = doc2.get("metadata", {})
            
            metadata_similarity = 0.0
            if metadata1 and metadata2:
                common_keys = set(metadata1.keys()).intersection(set(metadata2.keys()))
                if common_keys:
                    matches = sum(1 for key in common_keys if metadata1[key] == metadata2[key])
                    metadata_similarity = matches / len(common_keys)
            
            # Combinar similitudes
            return (similarity * 0.8) + (metadata_similarity * 0.2)
            
        except Exception as e:
            logger.error(f"Error calculando similitud de documentos: {e}")
            return 0.0
    
    async def _load_models(self):
        """Cargar modelos guardados"""
        try:
            models_dir = "recommendation_models"
            if not os.path.exists(models_dir):
                os.makedirs(models_dir)
                return
            
            # Cargar perfiles de usuarios
            users_file = os.path.join(models_dir, "user_profiles.pkl")
            if os.path.exists(users_file):
                with open(users_file, 'rb') as f:
                    self.user_profiles = pickle.load(f)
            
            # Cargar perfiles de documentos
            docs_file = os.path.join(models_dir, "document_profiles.pkl")
            if os.path.exists(docs_file):
                with open(docs_file, 'rb') as f:
                    self.document_profiles = pickle.load(f)
            
            # Cargar historial de búsquedas
            history_file = os.path.join(models_dir, "search_history.pkl")
            if os.path.exists(history_file):
                with open(history_file, 'rb') as f:
                    self.search_history = pickle.load(f)
            
            logger.info("Modelos de recomendación cargados")
            
        except Exception as e:
            logger.error(f"Error cargando modelos: {e}")
    
    async def save_models(self):
        """Guardar modelos"""
        try:
            models_dir = "recommendation_models"
            if not os.path.exists(models_dir):
                os.makedirs(models_dir)
            
            # Guardar perfiles de usuarios
            users_file = os.path.join(models_dir, "user_profiles.pkl")
            with open(users_file, 'wb') as f:
                pickle.dump(self.user_profiles, f)
            
            # Guardar perfiles de documentos
            docs_file = os.path.join(models_dir, "document_profiles.pkl")
            with open(docs_file, 'wb') as f:
                pickle.dump(self.document_profiles, f)
            
            # Guardar historial de búsquedas
            history_file = os.path.join(models_dir, "search_history.pkl")
            with open(history_file, 'wb') as f:
                pickle.dump(self.search_history, f)
            
            logger.info("Modelos de recomendación guardados")
            
        except Exception as e:
            logger.error(f"Error guardando modelos: {e}")
    
    def get_recommendation_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del motor de recomendaciones"""
        return {
            "total_users": len(self.user_profiles),
            "total_documents": len(self.document_profiles),
            "total_interactions": len(self.search_history),
            "avg_interactions_per_user": len(self.search_history) / len(self.user_profiles) if self.user_profiles else 0,
            "last_updated": datetime.now().isoformat()
        }


























