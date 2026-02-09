"""
Analytics Engine - Motor de Análisis Avanzado
Proporciona insights, métricas y análisis inteligente del sistema
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import json
import re
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import io
import base64

logger = logging.getLogger(__name__)

class AnalyticsEngine:
    """
    Motor de análisis avanzado que proporciona insights inteligentes
    sobre el contenido, patrones de búsqueda y rendimiento del sistema
    """
    
    def __init__(self):
        self.search_history = []
        self.document_analytics = {}
        self.user_behavior = {}
        self.performance_metrics = {}
        self.content_insights = {}
        
    async def analyze_search_patterns(self, search_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analizar patrones de búsqueda"""
        try:
            logger.info("Analizando patrones de búsqueda...")
            
            if not search_data:
                return {"error": "No hay datos de búsqueda disponibles"}
            
            # Convertir a DataFrame para análisis
            df = pd.DataFrame(search_data)
            
            # Análisis de consultas más populares
            query_counts = df['query'].value_counts().head(20)
            
            # Análisis por tipo de búsqueda
            search_type_distribution = df['search_type'].value_counts()
            
            # Análisis temporal
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.day_name()
            
            hourly_patterns = df['hour'].value_counts().sort_index()
            daily_patterns = df['day_of_week'].value_counts()
            
            # Análisis de rendimiento
            avg_search_time = df['search_time'].mean()
            search_time_distribution = df['search_time'].describe()
            
            # Análisis de resultados
            avg_results = df['total_results'].mean()
            results_distribution = df['total_results'].describe()
            
            # Patrones de consultas
            query_lengths = df['query'].str.len()
            avg_query_length = query_lengths.mean()
            
            # Palabras más comunes en consultas
            all_queries = ' '.join(df['query'].str.lower())
            words = re.findall(r'\b\w+\b', all_queries)
            word_frequency = Counter(words).most_common(50)
            
            analysis = {
                "search_patterns": {
                    "total_searches": len(df),
                    "unique_queries": df['query'].nunique(),
                    "avg_query_length": round(avg_query_length, 2),
                    "most_popular_queries": query_counts.to_dict(),
                    "search_type_distribution": search_type_distribution.to_dict(),
                    "word_frequency": dict(word_frequency[:20])
                },
                "temporal_patterns": {
                    "hourly_distribution": hourly_patterns.to_dict(),
                    "daily_distribution": daily_patterns.to_dict(),
                    "peak_hour": hourly_patterns.idxmax(),
                    "peak_day": daily_patterns.idxmax()
                },
                "performance_analysis": {
                    "avg_search_time_ms": round(avg_search_time * 1000, 2),
                    "search_time_stats": search_time_distribution.to_dict(),
                    "avg_results_per_search": round(avg_results, 2),
                    "results_distribution": results_distribution.to_dict()
                },
                "insights": self._generate_search_insights(df)
            }
            
            logger.info("Análisis de patrones de búsqueda completado")
            return analysis
            
        except Exception as e:
            logger.error(f"Error en análisis de patrones de búsqueda: {e}")
            return {"error": str(e)}
    
    async def analyze_document_content(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analizar contenido de documentos"""
        try:
            logger.info("Analizando contenido de documentos...")
            
            if not documents:
                return {"error": "No hay documentos disponibles"}
            
            # Análisis básico
            total_docs = len(documents)
            total_words = sum(doc.get('word_count', 0) for doc in documents)
            total_chars = sum(doc.get('content_length', 0) for doc in documents)
            
            # Análisis por tipo
            type_distribution = Counter(doc.get('document_type', 'unknown') for doc in documents)
            
            # Análisis de longitud
            word_counts = [doc.get('word_count', 0) for doc in documents]
            char_counts = [doc.get('content_length', 0) for doc in documents]
            
            # Análisis de contenido
            all_content = ' '.join(doc.get('content', '') for doc in documents)
            
            # Palabras más frecuentes
            words = re.findall(r'\b[a-zA-Z]{3,}\b', all_content.lower())
            word_frequency = Counter(words).most_common(100)
            
            # Análisis de metadatos
            categories = [doc.get('metadata', {}).get('category') for doc in documents if doc.get('metadata', {}).get('category')]
            category_distribution = Counter(categories)
            
            tags = []
            for doc in documents:
                doc_tags = doc.get('metadata', {}).get('tags', [])
                if isinstance(doc_tags, list):
                    tags.extend(doc_tags)
            tag_distribution = Counter(tags).most_common(20)
            
            # Análisis de complejidad
            avg_sentence_length = self._calculate_avg_sentence_length(all_content)
            readability_score = self._calculate_readability_score(all_content)
            
            # Análisis temporal
            creation_dates = []
            for doc in documents:
                if doc.get('created_at'):
                    try:
                        creation_dates.append(datetime.fromisoformat(doc['created_at'].replace('Z', '+00:00')))
                    except:
                        pass
            
            temporal_analysis = {}
            if creation_dates:
                creation_dates.sort()
                temporal_analysis = {
                    "oldest_document": creation_dates[0].isoformat(),
                    "newest_document": creation_dates[-1].isoformat(),
                    "documents_per_month": self._analyze_temporal_distribution(creation_dates)
                }
            
            analysis = {
                "content_overview": {
                    "total_documents": total_docs,
                    "total_words": total_words,
                    "total_characters": total_chars,
                    "avg_words_per_doc": round(total_words / total_docs, 2) if total_docs > 0 else 0,
                    "avg_chars_per_doc": round(total_chars / total_docs, 2) if total_docs > 0 else 0
                },
                "type_distribution": dict(type_distribution),
                "content_analysis": {
                    "word_frequency": dict(word_frequency[:30]),
                    "avg_sentence_length": round(avg_sentence_length, 2),
                    "readability_score": round(readability_score, 2),
                    "vocabulary_richness": len(set(words)) / len(words) if words else 0
                },
                "metadata_analysis": {
                    "category_distribution": dict(category_distribution),
                    "tag_distribution": dict(tag_distribution),
                    "documents_with_metadata": sum(1 for doc in documents if doc.get('metadata'))
                },
                "temporal_analysis": temporal_analysis,
                "insights": self._generate_content_insights(documents)
            }
            
            logger.info("Análisis de contenido completado")
            return analysis
            
        except Exception as e:
            logger.error(f"Error en análisis de contenido: {e}")
            return {"error": str(e)}
    
    async def generate_insights(self, search_data: List[Dict], documents: List[Dict]) -> Dict[str, Any]:
        """Generar insights inteligentes combinados"""
        try:
            logger.info("Generando insights inteligentes...")
            
            # Análisis individuales
            search_analysis = await self.analyze_search_patterns(search_data)
            content_analysis = await self.analyze_document_content(documents)
            
            # Insights combinados
            combined_insights = {
                "search_analysis": search_analysis,
                "content_analysis": content_analysis,
                "recommendations": self._generate_recommendations(search_analysis, content_analysis),
                "trends": self._identify_trends(search_data, documents),
                "optimization_suggestions": self._suggest_optimizations(search_analysis, content_analysis)
            }
            
            logger.info("Insights generados exitosamente")
            return combined_insights
            
        except Exception as e:
            logger.error(f"Error generando insights: {e}")
            return {"error": str(e)}
    
    async def create_visualizations(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Crear visualizaciones de datos"""
        try:
            logger.info("Creando visualizaciones...")
            
            visualizations = {}
            
            # Configurar estilo
            plt.style.use('seaborn-v0_8')
            sns.set_palette("husl")
            
            # 1. Distribución de tipos de búsqueda
            if 'search_analysis' in data and 'search_patterns' in data['search_analysis']:
                search_types = data['search_analysis']['search_patterns'].get('search_type_distribution', {})
                if search_types:
                    fig, ax = plt.subplots(figsize=(8, 6))
                    ax.pie(search_types.values(), labels=search_types.keys(), autopct='%1.1f%%')
                    ax.set_title('Distribución de Tipos de Búsqueda')
                    visualizations['search_types'] = self._fig_to_base64(fig)
                    plt.close(fig)
            
            # 2. Patrones temporales
            if 'search_analysis' in data and 'temporal_patterns' in data['search_analysis']:
                hourly = data['search_analysis']['temporal_patterns'].get('hourly_distribution', {})
                if hourly:
                    fig, ax = plt.subplots(figsize=(12, 6))
                    hours = list(range(24))
                    values = [hourly.get(str(h), 0) for h in hours]
                    ax.plot(hours, values, marker='o')
                    ax.set_xlabel('Hora del día')
                    ax.set_ylabel('Número de búsquedas')
                    ax.set_title('Patrones de Búsqueda por Hora')
                    ax.grid(True, alpha=0.3)
                    visualizations['hourly_patterns'] = self._fig_to_base64(fig)
                    plt.close(fig)
            
            # 3. Distribución de tipos de documento
            if 'content_analysis' in data and 'type_distribution' in data['content_analysis']:
                doc_types = data['content_analysis']['type_distribution']
                if doc_types:
                    fig, ax = plt.subplots(figsize=(8, 6))
                    ax.bar(doc_types.keys(), doc_types.values())
                    ax.set_xlabel('Tipo de Documento')
                    ax.set_ylabel('Cantidad')
                    ax.set_title('Distribución de Tipos de Documento')
                    plt.xticks(rotation=45)
                    visualizations['document_types'] = self._fig_to_base64(fig)
                    plt.close(fig)
            
            # 4. Word Cloud
            if 'content_analysis' in data and 'content_analysis' in data['content_analysis']:
                word_freq = data['content_analysis']['content_analysis'].get('word_frequency', {})
                if word_freq:
                    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_freq)
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wordcloud, interpolation='bilinear')
                    ax.axis('off')
                    ax.set_title('Palabras Más Frecuentes')
                    visualizations['wordcloud'] = self._fig_to_base64(fig)
                    plt.close(fig)
            
            logger.info(f"Visualizaciones creadas: {len(visualizations)}")
            return visualizations
            
        except Exception as e:
            logger.error(f"Error creando visualizaciones: {e}")
            return {"error": str(e)}
    
    def _generate_search_insights(self, df: pd.DataFrame) -> List[str]:
        """Generar insights de búsqueda"""
        insights = []
        
        try:
            # Insight sobre tipo de búsqueda preferido
            if 'search_type' in df.columns:
                most_used_type = df['search_type'].mode().iloc[0] if not df['search_type'].empty else None
                if most_used_type:
                    insights.append(f"El tipo de búsqueda más utilizado es '{most_used_type}'")
            
            # Insight sobre rendimiento
            if 'search_time' in df.columns:
                avg_time = df['search_time'].mean()
                if avg_time < 0.1:
                    insights.append("El sistema muestra excelente rendimiento con búsquedas muy rápidas")
                elif avg_time < 0.5:
                    insights.append("El rendimiento del sistema es bueno")
                else:
                    insights.append("Se recomienda optimizar el rendimiento de búsqueda")
            
            # Insight sobre resultados
            if 'total_results' in df.columns:
                avg_results = df['total_results'].mean()
                if avg_results < 5:
                    insights.append("Las búsquedas tienden a devolver pocos resultados - considera expandir el contenido")
                elif avg_results > 50:
                    insights.append("Las búsquedas devuelven muchos resultados - considera mejorar la precisión")
            
            # Insight sobre consultas
            if 'query' in df.columns:
                avg_length = df['query'].str.len().mean()
                if avg_length < 10:
                    insights.append("Las consultas son cortas - los usuarios podrían beneficiarse de búsquedas más específicas")
                elif avg_length > 50:
                    insights.append("Las consultas son muy largas - considera sugerir consultas más concisas")
            
        except Exception as e:
            logger.error(f"Error generando insights de búsqueda: {e}")
        
        return insights
    
    def _generate_content_insights(self, documents: List[Dict]) -> List[str]:
        """Generar insights de contenido"""
        insights = []
        
        try:
            # Insight sobre diversidad de contenido
            doc_types = set(doc.get('document_type', 'unknown') for doc in documents)
            if len(doc_types) > 3:
                insights.append("El sistema tiene buena diversidad de tipos de documento")
            elif len(doc_types) == 1:
                insights.append("Todos los documentos son del mismo tipo - considera diversificar el contenido")
            
            # Insight sobre metadatos
            docs_with_metadata = sum(1 for doc in documents if doc.get('metadata'))
            metadata_percentage = (docs_with_metadata / len(documents)) * 100 if documents else 0
            
            if metadata_percentage > 80:
                insights.append("Excelente cobertura de metadatos en los documentos")
            elif metadata_percentage < 50:
                insights.append("Se recomienda agregar más metadatos a los documentos para mejorar la búsqueda")
            
            # Insight sobre longitud de contenido
            word_counts = [doc.get('word_count', 0) for doc in documents if doc.get('word_count')]
            if word_counts:
                avg_words = sum(word_counts) / len(word_counts)
                if avg_words < 100:
                    insights.append("Los documentos son cortos - considera agregar más contenido detallado")
                elif avg_words > 2000:
                    insights.append("Los documentos son largos - considera dividirlos en secciones más pequeñas")
            
        except Exception as e:
            logger.error(f"Error generando insights de contenido: {e}")
        
        return insights
    
    def _generate_recommendations(self, search_analysis: Dict, content_analysis: Dict) -> List[str]:
        """Generar recomendaciones basadas en análisis"""
        recommendations = []
        
        try:
            # Recomendaciones basadas en patrones de búsqueda
            if 'search_patterns' in search_analysis:
                search_types = search_analysis['search_patterns'].get('search_type_distribution', {})
                if 'semantic' in search_types and search_types['semantic'] > search_types.get('keyword', 0) * 2:
                    recommendations.append("Los usuarios prefieren búsqueda semántica - optimiza el modelo de embeddings")
                
                if 'keyword' in search_types and search_types['keyword'] > search_types.get('semantic', 0) * 2:
                    recommendations.append("Los usuarios prefieren búsqueda por palabras clave - mejora el índice TF-IDF")
            
            # Recomendaciones basadas en contenido
            if 'content_analysis' in content_analysis:
                type_dist = content_analysis.get('type_distribution', {})
                if len(type_dist) == 1:
                    recommendations.append("Diversifica los tipos de documento para mejorar la cobertura")
                
                if 'content_analysis' in content_analysis:
                    readability = content_analysis['content_analysis'].get('readability_score', 0)
                    if readability < 30:
                        recommendations.append("El contenido es complejo - considera simplificar para mejor comprensión")
                    elif readability > 80:
                        recommendations.append("El contenido es muy simple - considera agregar más profundidad técnica")
            
            # Recomendaciones de rendimiento
            if 'performance_analysis' in search_analysis:
                avg_time = search_analysis['performance_analysis'].get('avg_search_time_ms', 0)
                if avg_time > 500:
                    recommendations.append("Optimiza el rendimiento de búsqueda - considera cache o índices adicionales")
            
        except Exception as e:
            logger.error(f"Error generando recomendaciones: {e}")
        
        return recommendations
    
    def _identify_trends(self, search_data: List[Dict], documents: List[Dict]) -> List[str]:
        """Identificar tendencias en los datos"""
        trends = []
        
        try:
            # Tendencias temporales en búsquedas
            if search_data:
                df = pd.DataFrame(search_data)
                if 'timestamp' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    df['date'] = df['timestamp'].dt.date
                    
                    daily_searches = df.groupby('date').size()
                    if len(daily_searches) > 7:
                        recent_avg = daily_searches.tail(7).mean()
                        older_avg = daily_searches.head(7).mean()
                        
                        if recent_avg > older_avg * 1.2:
                            trends.append("Tendencia creciente en el uso del sistema")
                        elif recent_avg < older_avg * 0.8:
                            trends.append("Tendencia decreciente en el uso del sistema")
            
            # Tendencias en tipos de consulta
            if search_data:
                df = pd.DataFrame(search_data)
                if 'search_type' in df.columns:
                    recent_searches = df.tail(50) if len(df) > 50 else df
                    type_trends = recent_searches['search_type'].value_counts()
                    
                    if 'hybrid' in type_trends and type_trends['hybrid'] > type_trends.get('semantic', 0):
                        trends.append("Los usuarios están adoptando búsqueda híbrida")
            
        except Exception as e:
            logger.error(f"Error identificando tendencias: {e}")
        
        return trends
    
    def _suggest_optimizations(self, search_analysis: Dict, content_analysis: Dict) -> List[str]:
        """Sugerir optimizaciones del sistema"""
        optimizations = []
        
        try:
            # Optimizaciones de rendimiento
            if 'performance_analysis' in search_analysis:
                avg_time = search_analysis['performance_analysis'].get('avg_search_time_ms', 0)
                if avg_time > 200:
                    optimizations.append("Implementar cache de resultados frecuentes")
                    optimizations.append("Optimizar índices de base de datos")
                
                avg_results = search_analysis['performance_analysis'].get('avg_results_per_search', 0)
                if avg_results > 100:
                    optimizations.append("Implementar paginación más eficiente")
            
            # Optimizaciones de contenido
            if 'content_analysis' in content_analysis:
                content_overview = content_analysis.get('content_overview', {})
                total_docs = content_overview.get('total_documents', 0)
                
                if total_docs > 1000:
                    optimizations.append("Considerar sharding de la base de datos")
                    optimizations.append("Implementar indexación incremental")
                
                if total_docs < 50:
                    optimizations.append("Agregar más contenido para mejorar la cobertura de búsqueda")
            
            # Optimizaciones de modelo
            if 'search_patterns' in search_analysis:
                search_types = search_analysis['search_patterns'].get('search_type_distribution', {})
                if 'semantic' in search_types and search_types['semantic'] > 0.7:
                    optimizations.append("Considerar un modelo de embeddings más avanzado")
                    optimizations.append("Implementar fine-tuning del modelo")
        
        except Exception as e:
            logger.error(f"Error sugiriendo optimizaciones: {e}")
        
        return optimizations
    
    def _calculate_avg_sentence_length(self, text: str) -> float:
        """Calcular longitud promedio de oraciones"""
        try:
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            if not sentences:
                return 0
            
            total_words = sum(len(s.split()) for s in sentences)
            return total_words / len(sentences)
        except:
            return 0
    
    def _calculate_readability_score(self, text: str) -> float:
        """Calcular score de legibilidad simplificado"""
        try:
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if not sentences:
                return 0
            
            words = re.findall(r'\b\w+\b', text.lower())
            syllables = sum(self._count_syllables(word) for word in words)
            
            avg_sentence_length = len(words) / len(sentences)
            avg_syllables_per_word = syllables / len(words) if words else 0
            
            # Fórmula simplificada de legibilidad
            score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
            return max(0, min(100, score))
        except:
            return 0
    
    def _count_syllables(self, word: str) -> int:
        """Contar sílabas en una palabra"""
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllable_count += 1
            prev_was_vowel = is_vowel
        
        if word.endswith('e'):
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    def _analyze_temporal_distribution(self, dates: List[datetime]) -> Dict[str, int]:
        """Analizar distribución temporal de documentos"""
        try:
            monthly_counts = defaultdict(int)
            for date in dates:
                month_key = date.strftime('%Y-%m')
                monthly_counts[month_key] += 1
            
            return dict(monthly_counts)
        except:
            return {}
    
    def _fig_to_base64(self, fig) -> str:
        """Convertir figura de matplotlib a base64"""
        try:
            buffer = io.BytesIO()
            fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            buffer.close()
            return f"data:image/png;base64,{image_base64}"
        except Exception as e:
            logger.error(f"Error convirtiendo figura a base64: {e}")
            return ""



























