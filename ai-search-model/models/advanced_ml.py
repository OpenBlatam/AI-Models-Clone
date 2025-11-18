"""
Advanced ML - Sistema de Machine Learning Avanzado
Sistema de clustering, clasificación y análisis avanzado de documentos
"""

import asyncio
import logging
import json
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.decomposition import PCA, LatentDirichletAllocation, TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, silhouette_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import seaborn as sns
from sentence_transformers import SentenceTransformer
import joblib
import os
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

@dataclass
class ClusterResult:
    """Resultado de clustering"""
    cluster_id: int
    documents: List[str]
    centroid: List[float]
    size: int
    keywords: List[str]
    description: str
    quality_score: float

@dataclass
class ClassificationResult:
    """Resultado de clasificación"""
    document_id: str
    predicted_class: str
    confidence: float
    probabilities: Dict[str, float]
    features_importance: Dict[str, float]

@dataclass
class TopicModelingResult:
    """Resultado de modelado de temas"""
    topic_id: int
    topic_words: List[str]
    topic_weight: float
    documents: List[str]
    coherence_score: float

class AdvancedMLSystem:
    """
    Sistema de Machine Learning avanzado para análisis de documentos
    """
    
    def __init__(self):
        self.sentence_transformer = None
        self.vectorizer = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        
        # Modelos entrenados
        self.clustering_models = {}
        self.classification_models = {}
        self.topic_models = {}
        
        # Datos procesados
        self.document_embeddings = {}
        self.document_features = {}
        self.document_labels = {}
        
        # Configuraciones
        self.clustering_config = {
            "kmeans": {"n_clusters": 5, "random_state": 42},
            "dbscan": {"eps": 0.5, "min_samples": 5},
            "agglomerative": {"n_clusters": 5, "linkage": "ward"}
        }
        
        self.classification_config = {
            "naive_bayes": {"alpha": 1.0},
            "svm": {"kernel": "rbf", "C": 1.0, "random_state": 42},
            "random_forest": {"n_estimators": 100, "random_state": 42}
        }
        
        self.topic_modeling_config = {
            "lda": {"n_components": 10, "random_state": 42},
            "svd": {"n_components": 10, "random_state": 42}
        }
    
    async def initialize(self):
        """Inicializar sistema de ML"""
        try:
            logger.info("Inicializando sistema de Machine Learning avanzado...")
            
            # Inicializar modelo de embeddings
            self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Inicializar vectorizador
            self.vectorizer = TfidfVectorizer(
                max_features=5000,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.95
            )
            
            # Cargar modelos guardados si existen
            await self._load_saved_models()
            
            logger.info("Sistema de Machine Learning inicializado exitosamente")
            
        except Exception as e:
            logger.error(f"Error inicializando sistema de ML: {e}")
            raise
    
    async def _load_saved_models(self):
        """Cargar modelos guardados"""
        try:
            models_dir = "ml_models"
            if not os.path.exists(models_dir):
                os.makedirs(models_dir)
                return
            
            # Cargar modelos de clustering
            for model_name in ["kmeans", "dbscan", "agglomerative"]:
                model_path = os.path.join(models_dir, f"{model_name}_model.pkl")
                if os.path.exists(model_path):
                    self.clustering_models[model_name] = joblib.load(model_path)
            
            # Cargar modelos de clasificación
            for model_name in ["naive_bayes", "svm", "random_forest"]:
                model_path = os.path.join(models_dir, f"{model_name}_classifier.pkl")
                if os.path.exists(model_path):
                    self.classification_models[model_name] = joblib.load(model_path)
            
            # Cargar modelos de topic modeling
            for model_name in ["lda", "svd"]:
                model_path = os.path.join(models_dir, f"{model_name}_topic_model.pkl")
                if os.path.exists(model_path):
                    self.topic_models[model_name] = joblib.load(model_path)
            
            logger.info("Modelos guardados cargados exitosamente")
            
        except Exception as e:
            logger.error(f"Error cargando modelos guardados: {e}")
    
    async def _save_models(self):
        """Guardar modelos entrenados"""
        try:
            models_dir = "ml_models"
            if not os.path.exists(models_dir):
                os.makedirs(models_dir)
            
            # Guardar modelos de clustering
            for model_name, model in self.clustering_models.items():
                model_path = os.path.join(models_dir, f"{model_name}_model.pkl")
                joblib.dump(model, model_path)
            
            # Guardar modelos de clasificación
            for model_name, model in self.classification_models.items():
                model_path = os.path.join(models_dir, f"{model_name}_classifier.pkl")
                joblib.dump(model, model_path)
            
            # Guardar modelos de topic modeling
            for model_name, model in self.topic_models.items():
                model_path = os.path.join(models_dir, f"{model_name}_topic_model.pkl")
                joblib.dump(model, model_path)
            
            logger.info("Modelos guardados exitosamente")
            
        except Exception as e:
            logger.error(f"Error guardando modelos: {e}")
    
    async def prepare_document_data(self, documents: List[Dict[str, Any]]) -> Tuple[np.ndarray, np.ndarray]:
        """Preparar datos de documentos para ML"""
        try:
            logger.info(f"Preparando datos de {len(documents)} documentos...")
            
            # Extraer contenido y metadatos
            contents = []
            metadata_list = []
            
            for doc in documents:
                content = doc.get("content", "")
                metadata = doc.get("metadata", {})
                
                contents.append(content)
                metadata_list.append(metadata)
            
            # Generar embeddings semánticos
            embeddings = self.sentence_transformer.encode(contents)
            
            # Generar características TF-IDF
            tfidf_matrix = self.vectorizer.fit_transform(contents)
            
            # Combinar características
            combined_features = np.hstack([
                embeddings,
                tfidf_matrix.toarray()
            ])
            
            # Normalizar características
            combined_features = self.scaler.fit_transform(combined_features)
            
            # Guardar datos procesados
            for i, doc in enumerate(documents):
                doc_id = doc.get("id", f"doc_{i}")
                self.document_embeddings[doc_id] = embeddings[i]
                self.document_features[doc_id] = combined_features[i]
            
            logger.info("Datos de documentos preparados exitosamente")
            return combined_features, embeddings
            
        except Exception as e:
            logger.error(f"Error preparando datos de documentos: {e}")
            raise
    
    async def perform_clustering(self, documents: List[Dict[str, Any]], 
                                method: str = "kmeans", n_clusters: int = None) -> List[ClusterResult]:
        """Realizar clustering de documentos"""
        try:
            logger.info(f"Realizando clustering con método {method}...")
            
            # Preparar datos
            features, embeddings = await self.prepare_document_data(documents)
            
            # Configurar número de clusters
            if n_clusters:
                self.clustering_config[method]["n_clusters"] = n_clusters
            
            # Entrenar modelo de clustering
            if method == "kmeans":
                model = KMeans(**self.clustering_config["kmeans"])
            elif method == "dbscan":
                model = DBSCAN(**self.clustering_config["dbscan"])
            elif method == "agglomerative":
                model = AgglomerativeClustering(**self.clustering_config["agglomerative"])
            else:
                raise ValueError(f"Método de clustering no soportado: {method}")
            
            # Ajustar modelo
            cluster_labels = model.fit_predict(features)
            
            # Guardar modelo
            self.clustering_models[method] = model
            
            # Procesar resultados
            clusters = await self._process_clustering_results(
                documents, cluster_labels, embeddings, method
            )
            
            # Calcular métricas de calidad
            if method != "dbscan":  # DBSCAN no tiene centroides
                silhouette_avg = silhouette_score(features, cluster_labels)
                logger.info(f"Silhouette Score: {silhouette_avg:.3f}")
            
            logger.info(f"Clustering completado: {len(clusters)} clusters encontrados")
            return clusters
            
        except Exception as e:
            logger.error(f"Error en clustering: {e}")
            raise
    
    async def _process_clustering_results(self, documents: List[Dict[str, Any]], 
                                        cluster_labels: np.ndarray, 
                                        embeddings: np.ndarray, 
                                        method: str) -> List[ClusterResult]:
        """Procesar resultados de clustering"""
        try:
            clusters = []
            unique_labels = np.unique(cluster_labels)
            
            for cluster_id in unique_labels:
                if cluster_id == -1:  # Ruido en DBSCAN
                    continue
                
                # Obtener documentos del cluster
                cluster_mask = cluster_labels == cluster_id
                cluster_docs = [documents[i] for i in range(len(documents)) if cluster_mask[i]]
                cluster_embeddings = embeddings[cluster_mask]
                
                # Calcular centroide
                centroid = np.mean(cluster_embeddings, axis=0)
                
                # Extraer palabras clave del cluster
                cluster_contents = [doc.get("content", "") for doc in cluster_docs]
                keywords = await self._extract_cluster_keywords(cluster_contents)
                
                # Generar descripción del cluster
                description = await self._generate_cluster_description(keywords, cluster_contents)
                
                # Calcular score de calidad
                quality_score = await self._calculate_cluster_quality(
                    cluster_embeddings, centroid
                )
                
                cluster_result = ClusterResult(
                    cluster_id=int(cluster_id),
                    documents=[doc.get("id", f"doc_{i}") for i, doc in enumerate(cluster_docs)],
                    centroid=centroid.tolist(),
                    size=len(cluster_docs),
                    keywords=keywords,
                    description=description,
                    quality_score=quality_score
                )
                
                clusters.append(cluster_result)
            
            return clusters
            
        except Exception as e:
            logger.error(f"Error procesando resultados de clustering: {e}")
            raise
    
    async def _extract_cluster_keywords(self, contents: List[str]) -> List[str]:
        """Extraer palabras clave de un cluster"""
        try:
            # Combinar todo el contenido del cluster
            combined_content = " ".join(contents)
            
            # Usar TF-IDF para extraer palabras clave
            vectorizer = TfidfVectorizer(
                max_features=20,
                stop_words='english',
                ngram_range=(1, 2)
            )
            
            tfidf_matrix = vectorizer.fit_transform([combined_content])
            feature_names = vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]
            
            # Obtener las palabras con mayor score
            keyword_indices = np.argsort(scores)[-10:][::-1]
            keywords = [feature_names[i] for i in keyword_indices if scores[i] > 0]
            
            return keywords
            
        except Exception as e:
            logger.error(f"Error extrayendo palabras clave: {e}")
            return []
    
    async def _generate_cluster_description(self, keywords: List[str], 
                                          contents: List[str]) -> str:
        """Generar descripción del cluster"""
        try:
            if not keywords:
                return "Cluster sin palabras clave identificadas"
            
            # Usar las primeras palabras clave para generar descripción
            top_keywords = keywords[:5]
            description = f"Cluster relacionado con: {', '.join(top_keywords)}"
            
            return description
            
        except Exception as e:
            logger.error(f"Error generando descripción: {e}")
            return "Descripción no disponible"
    
    async def _calculate_cluster_quality(self, embeddings: np.ndarray, 
                                       centroid: np.ndarray) -> float:
        """Calcular calidad del cluster"""
        try:
            if len(embeddings) < 2:
                return 0.0
            
            # Calcular distancia promedio al centroide
            distances = np.linalg.norm(embeddings - centroid, axis=1)
            avg_distance = np.mean(distances)
            
            # Convertir a score de calidad (menor distancia = mayor calidad)
            quality_score = max(0, 1 - avg_distance)
            
            return float(quality_score)
            
        except Exception as e:
            logger.error(f"Error calculando calidad del cluster: {e}")
            return 0.0
    
    async def train_classifier(self, documents: List[Dict[str, Any]], 
                              labels: List[str], method: str = "random_forest") -> Dict[str, Any]:
        """Entrenar clasificador de documentos"""
        try:
            logger.info(f"Entrenando clasificador {method}...")
            
            # Preparar datos
            features, _ = await self.prepare_document_data(documents)
            
            # Codificar etiquetas
            encoded_labels = self.label_encoder.fit_transform(labels)
            
            # Dividir datos
            X_train, X_test, y_train, y_test = train_test_split(
                features, encoded_labels, test_size=0.2, random_state=42
            )
            
            # Entrenar modelo
            if method == "naive_bayes":
                model = MultinomialNB(**self.classification_config["naive_bayes"])
            elif method == "svm":
                model = SVC(**self.classification_config["svm"], probability=True)
            elif method == "random_forest":
                model = RandomForestClassifier(**self.classification_config["random_forest"])
            else:
                raise ValueError(f"Método de clasificación no soportado: {method}")
            
            # Entrenar modelo
            model.fit(X_train, y_train)
            
            # Evaluar modelo
            y_pred = model.predict(X_test)
            accuracy = model.score(X_test, y_test)
            
            # Validación cruzada
            cv_scores = cross_val_score(model, features, encoded_labels, cv=5)
            
            # Reporte de clasificación
            class_names = self.label_encoder.classes_
            classification_rep = classification_report(
                y_test, y_pred, target_names=class_names, output_dict=True
            )
            
            # Guardar modelo
            self.classification_models[method] = model
            
            # Guardar modelos
            await self._save_models()
            
            results = {
                "method": method,
                "accuracy": float(accuracy),
                "cv_mean": float(cv_scores.mean()),
                "cv_std": float(cv_scores.std()),
                "classification_report": classification_rep,
                "classes": class_names.tolist(),
                "training_samples": len(X_train),
                "test_samples": len(X_test)
            }
            
            logger.info(f"Clasificador entrenado - Accuracy: {accuracy:.3f}")
            return results
            
        except Exception as e:
            logger.error(f"Error entrenando clasificador: {e}")
            raise
    
    async def classify_document(self, document: Dict[str, Any], 
                               method: str = "random_forest") -> ClassificationResult:
        """Clasificar un documento"""
        try:
            if method not in self.classification_models:
                raise ValueError(f"Modelo {method} no está entrenado")
            
            # Preparar datos del documento
            features, _ = await self.prepare_document_data([document])
            
            # Obtener modelo
            model = self.classification_models[method]
            
            # Realizar predicción
            prediction = model.predict(features)[0]
            probabilities = model.predict_proba(features)[0]
            
            # Decodificar predicción
            predicted_class = self.label_encoder.inverse_transform([prediction])[0]
            confidence = float(max(probabilities))
            
            # Obtener probabilidades para todas las clases
            class_probabilities = {}
            for i, class_name in enumerate(self.label_encoder.classes_):
                class_probabilities[class_name] = float(probabilities[i])
            
            # Obtener importancia de características (si está disponible)
            features_importance = {}
            if hasattr(model, 'feature_importances_'):
                # Para Random Forest
                top_features = np.argsort(model.feature_importances_)[-10:][::-1]
                for i, feature_idx in enumerate(top_features):
                    features_importance[f"feature_{feature_idx}"] = float(
                        model.feature_importances_[feature_idx]
                    )
            
            result = ClassificationResult(
                document_id=document.get("id", "unknown"),
                predicted_class=predicted_class,
                confidence=confidence,
                probabilities=class_probabilities,
                features_importance=features_importance
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error clasificando documento: {e}")
            raise
    
    async def perform_topic_modeling(self, documents: List[Dict[str, Any]], 
                                   method: str = "lda", n_topics: int = None) -> List[TopicModelingResult]:
        """Realizar modelado de temas"""
        try:
            logger.info(f"Realizando topic modeling con método {method}...")
            
            # Extraer contenido
            contents = [doc.get("content", "") for doc in documents]
            
            # Configurar número de temas
            if n_topics:
                self.topic_modeling_config[method]["n_components"] = n_topics
            
            # Preparar datos
            if method == "lda":
                vectorizer = CountVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=(1, 2)
                )
                doc_term_matrix = vectorizer.fit_transform(contents)
                model = LatentDirichletAllocation(**self.topic_modeling_config["lda"])
            elif method == "svd":
                vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=(1, 2)
                )
                doc_term_matrix = vectorizer.fit_transform(contents)
                model = TruncatedSVD(**self.topic_modeling_config["svd"])
            else:
                raise ValueError(f"Método de topic modeling no soportado: {method}")
            
            # Entrenar modelo
            model.fit(doc_term_matrix)
            
            # Guardar modelo
            self.topic_models[method] = model
            
            # Procesar resultados
            topics = await self._process_topic_modeling_results(
                documents, model, vectorizer, doc_term_matrix, method
            )
            
            logger.info(f"Topic modeling completado: {len(topics)} temas encontrados")
            return topics
            
        except Exception as e:
            logger.error(f"Error en topic modeling: {e}")
            raise
    
    async def _process_topic_modeling_results(self, documents: List[Dict[str, Any]], 
                                            model, vectorizer, doc_term_matrix, 
                                            method: str) -> List[TopicModelingResult]:
        """Procesar resultados de topic modeling"""
        try:
            topics = []
            feature_names = vectorizer.get_feature_names_out()
            
            if method == "lda":
                # Para LDA
                topic_word_distributions = model.components_
                doc_topic_distributions = model.transform(doc_term_matrix)
                
                for topic_idx in range(model.n_components):
                    # Obtener palabras del tema
                    topic_words_idx = np.argsort(topic_word_distributions[topic_idx])[-10:][::-1]
                    topic_words = [feature_names[i] for i in topic_words_idx]
                    
                    # Obtener documentos del tema
                    topic_weights = doc_topic_distributions[:, topic_idx]
                    top_doc_indices = np.argsort(topic_weights)[-5:][::-1]
                    topic_documents = [documents[i].get("id", f"doc_{i}") 
                                     for i in top_doc_indices if topic_weights[i] > 0.1]
                    
                    # Calcular peso promedio del tema
                    topic_weight = float(np.mean(topic_weights))
                    
                    # Calcular coherencia del tema (simplificado)
                    coherence_score = await self._calculate_topic_coherence(topic_words)
                    
                    topic_result = TopicModelingResult(
                        topic_id=topic_idx,
                        topic_words=topic_words,
                        topic_weight=topic_weight,
                        documents=topic_documents,
                        coherence_score=coherence_score
                    )
                    
                    topics.append(topic_result)
            
            elif method == "svd":
                # Para SVD
                components = model.components_
                doc_topic_distributions = model.transform(doc_term_matrix)
                
                for topic_idx in range(model.n_components):
                    # Obtener palabras del tema
                    topic_words_idx = np.argsort(np.abs(components[topic_idx]))[-10:][::-1]
                    topic_words = [feature_names[i] for i in topic_words_idx]
                    
                    # Obtener documentos del tema
                    topic_weights = np.abs(doc_topic_distributions[:, topic_idx])
                    top_doc_indices = np.argsort(topic_weights)[-5:][::-1]
                    topic_documents = [documents[i].get("id", f"doc_{i}") 
                                     for i in top_doc_indices if topic_weights[i] > 0.1]
                    
                    # Calcular peso promedio del tema
                    topic_weight = float(np.mean(topic_weights))
                    
                    # Calcular coherencia del tema
                    coherence_score = await self._calculate_topic_coherence(topic_words)
                    
                    topic_result = TopicModelingResult(
                        topic_id=topic_idx,
                        topic_words=topic_words,
                        topic_weight=topic_weight,
                        documents=topic_documents,
                        coherence_score=coherence_score
                    )
                    
                    topics.append(topic_result)
            
            return topics
            
        except Exception as e:
            logger.error(f"Error procesando resultados de topic modeling: {e}")
            raise
    
    async def _calculate_topic_coherence(self, topic_words: List[str]) -> float:
        """Calcular coherencia de un tema (simplificado)"""
        try:
            # Coherencia simplificada basada en la diversidad de palabras
            unique_words = len(set(topic_words))
            total_words = len(topic_words)
            
            if total_words == 0:
                return 0.0
            
            # Coherencia = ratio de palabras únicas
            coherence = unique_words / total_words
            
            return float(coherence)
            
        except Exception as e:
            logger.error(f"Error calculando coherencia del tema: {e}")
            return 0.0
    
    async def perform_dimensionality_reduction(self, documents: List[Dict[str, Any]], 
                                             method: str = "pca", n_components: int = 2) -> Dict[str, Any]:
        """Realizar reducción de dimensionalidad"""
        try:
            logger.info(f"Realizando reducción de dimensionalidad con {method}...")
            
            # Preparar datos
            features, embeddings = await self.prepare_document_data(documents)
            
            # Aplicar reducción de dimensionalidad
            if method == "pca":
                reducer = PCA(n_components=n_components, random_state=42)
            elif method == "tsne":
                reducer = TSNE(n_components=n_components, random_state=42, perplexity=30)
            else:
                raise ValueError(f"Método de reducción no soportado: {method}")
            
            # Ajustar y transformar
            reduced_features = reducer.fit_transform(features)
            
            # Preparar resultados
            results = {
                "method": method,
                "n_components": n_components,
                "original_dimensions": features.shape[1],
                "reduced_dimensions": reduced_features.shape[1],
                "explained_variance_ratio": None,
                "coordinates": reduced_features.tolist(),
                "document_ids": [doc.get("id", f"doc_{i}") for i, doc in enumerate(documents)]
            }
            
            # Agregar información específica del método
            if method == "pca":
                results["explained_variance_ratio"] = reducer.explained_variance_ratio_.tolist()
                results["total_variance_explained"] = float(np.sum(reducer.explained_variance_ratio_))
            
            logger.info(f"Reducción de dimensionalidad completada")
            return results
            
        except Exception as e:
            logger.error(f"Error en reducción de dimensionalidad: {e}")
            raise
    
    async def generate_ml_report(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generar reporte completo de ML"""
        try:
            logger.info("Generando reporte completo de ML...")
            
            # Preparar datos
            features, embeddings = await self.prepare_document_data(documents)
            
            # Análisis básico
            basic_stats = {
                "total_documents": len(documents),
                "feature_dimensions": features.shape[1],
                "embedding_dimensions": embeddings.shape[1],
                "average_document_length": np.mean([len(doc.get("content", "").split()) 
                                                  for doc in documents])
            }
            
            # Análisis de clustering
            clustering_results = {}
            for method in ["kmeans", "dbscan", "agglomerative"]:
                try:
                    clusters = await self.perform_clustering(documents, method)
                    clustering_results[method] = {
                        "n_clusters": len(clusters),
                        "clusters": [asdict(cluster) for cluster in clusters]
                    }
                except Exception as e:
                    logger.warning(f"Error en clustering {method}: {e}")
                    clustering_results[method] = {"error": str(e)}
            
            # Análisis de topic modeling
            topic_results = {}
            for method in ["lda", "svd"]:
                try:
                    topics = await self.perform_topic_modeling(documents, method)
                    topic_results[method] = {
                        "n_topics": len(topics),
                        "topics": [asdict(topic) for topic in topics]
                    }
                except Exception as e:
                    logger.warning(f"Error en topic modeling {method}: {e}")
                    topic_results[method] = {"error": str(e)}
            
            # Reducción de dimensionalidad
            dimensionality_results = {}
            for method in ["pca", "tsne"]:
                try:
                    reduced = await self.perform_dimensionality_reduction(documents, method)
                    dimensionality_results[method] = reduced
                except Exception as e:
                    logger.warning(f"Error en reducción {method}: {e}")
                    dimensionality_results[method] = {"error": str(e)}
            
            # Compilar reporte
            report = {
                "timestamp": datetime.now().isoformat(),
                "basic_statistics": basic_stats,
                "clustering_analysis": clustering_results,
                "topic_modeling_analysis": topic_results,
                "dimensionality_reduction": dimensionality_results,
                "recommendations": await self._generate_ml_recommendations(
                    basic_stats, clustering_results, topic_results
                )
            }
            
            logger.info("Reporte de ML generado exitosamente")
            return report
            
        except Exception as e:
            logger.error(f"Error generando reporte de ML: {e}")
            raise
    
    async def _generate_ml_recommendations(self, basic_stats: Dict[str, Any], 
                                         clustering_results: Dict[str, Any], 
                                         topic_results: Dict[str, Any]) -> List[str]:
        """Generar recomendaciones basadas en análisis ML"""
        try:
            recommendations = []
            
            # Recomendaciones basadas en estadísticas básicas
            if basic_stats["total_documents"] < 50:
                recommendations.append("Considera agregar más documentos para mejorar la calidad del análisis")
            
            if basic_stats["average_document_length"] < 100:
                recommendations.append("Los documentos son cortos, considera documentos más detallados")
            
            # Recomendaciones basadas en clustering
            for method, result in clustering_results.items():
                if "error" not in result:
                    n_clusters = result["n_clusters"]
                    if n_clusters < 3:
                        recommendations.append(f"El clustering {method} sugiere poca diversidad en los documentos")
                    elif n_clusters > 10:
                        recommendations.append(f"El clustering {method} sugiere demasiada fragmentación")
            
            # Recomendaciones basadas en topic modeling
            for method, result in topic_results.items():
                if "error" not in result:
                    n_topics = result["n_topics"]
                    if n_topics < 3:
                        recommendations.append(f"El topic modeling {method} sugiere temas limitados")
            
            if not recommendations:
                recommendations.append("El análisis sugiere una buena diversidad y estructura en los documentos")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generando recomendaciones: {e}")
            return ["Error generando recomendaciones"]
    
    def get_ml_system_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del sistema ML"""
        return {
            "trained_clustering_models": list(self.clustering_models.keys()),
            "trained_classification_models": list(self.classification_models.keys()),
            "trained_topic_models": list(self.topic_models.keys()),
            "processed_documents": len(self.document_embeddings),
            "feature_dimensions": len(self.document_features.get(list(self.document_features.keys())[0], [])) if self.document_features else 0,
            "last_updated": datetime.now().isoformat()
        }


























