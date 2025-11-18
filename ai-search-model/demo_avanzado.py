#!/usr/bin/env python3
"""
Demo Avanzado del Sistema de Búsqueda AI
Demuestra todas las funcionalidades avanzadas del sistema
"""

import asyncio
import json
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import random
import string

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedDemo:
    """Demo avanzado del sistema de búsqueda AI"""
    
    def __init__(self):
        self.demo_data = []
        self.users = ["user1", "user2", "user3", "user4", "user5"]
        self.documents = []
        
    async def initialize_systems(self):
        """Inicializar todos los sistemas"""
        try:
            logger.info("🚀 Inicializando sistemas avanzados...")
            
            # Importar sistemas
            from models.search_engine import AISearchEngine
            from models.document_processor import DocumentProcessor
            from database.vector_db import VectorDatabase
            from models.analytics_engine import AnalyticsEngine
            from models.recommendation_engine import RecommendationEngine
            from models.notification_system import NotificationSystem
            from models.cache_system import CacheSystem
            from models.batch_processor import BatchProcessor
            from models.export_import import ExportImportSystem
            
            # Inicializar sistemas
            self.vector_db = VectorDatabase()
            await self.vector_db.initialize()
            
            self.document_processor = DocumentProcessor()
            await self.document_processor.initialize()
            
            self.search_engine = AISearchEngine()
            await self.search_engine.initialize()
            
            self.analytics_engine = AnalyticsEngine()
            await self.analytics_engine.initialize()
            
            self.recommendation_engine = RecommendationEngine()
            await self.recommendation_engine.initialize()
            
            self.notification_system = NotificationSystem()
            await self.notification_system.initialize()
            
            self.cache_system = CacheSystem()
            self.cache_system.start_cleanup_thread()
            
            self.batch_processor = BatchProcessor()
            await self.batch_processor.initialize()
            
            self.export_import = ExportImportSystem()
            await self.export_import.initialize()
            
            logger.info("✅ Sistemas inicializados exitosamente")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando sistemas: {e}")
            raise
    
    def generate_demo_documents(self, count: int = 20) -> List[Dict[str, Any]]:
        """Generar documentos de demostración"""
        logger.info(f"📄 Generando {count} documentos de demostración...")
        
        topics = [
            "Machine Learning", "Artificial Intelligence", "Data Science",
            "Web Development", "Mobile Development", "Cloud Computing",
            "Cybersecurity", "Blockchain", "IoT", "DevOps",
            "Python Programming", "JavaScript", "React", "Node.js",
            "Database Design", "API Development", "Microservices",
            "Docker", "Kubernetes", "AWS", "Azure", "Google Cloud"
        ]
        
        document_types = ["pdf", "docx", "txt", "md", "html"]
        authors = ["Dr. Smith", "Prof. Johnson", "Ing. García", "Lic. Martínez", "Dr. Brown"]
        
        documents = []
        for i in range(count):
            topic = random.choice(topics)
            doc_type = random.choice(document_types)
            author = random.choice(authors)
            
            # Generar contenido relacionado al tema
            content = self._generate_content_for_topic(topic)
            
            document = {
                "id": f"doc_{i+1:03d}",
                "title": f"{topic}: Guía Completa {i+1}",
                "content": content,
                "metadata": {
                    "author": author,
                    "type": doc_type,
                    "topic": topic,
                    "created_at": (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
                    "tags": [topic.lower().replace(" ", "_"), f"guide_{i+1}", "tutorial"],
                    "word_count": len(content.split()),
                    "language": "es"
                }
            }
            
            documents.append(document)
        
        self.documents = documents
        logger.info(f"✅ {len(documents)} documentos generados")
        return documents
    
    def _generate_content_for_topic(self, topic: str) -> str:
        """Generar contenido específico para un tema"""
        content_templates = {
            "Machine Learning": f"""
            {topic} es una rama de la inteligencia artificial que se enfoca en el desarrollo de algoritmos 
            que pueden aprender y hacer predicciones basadas en datos. Los algoritmos de {topic} incluyen 
            regresión lineal, árboles de decisión, redes neuronales, y algoritmos de clustering. 
            Las aplicaciones de {topic} incluyen reconocimiento de imágenes, procesamiento de lenguaje natural, 
            sistemas de recomendación, y análisis predictivo. Para implementar {topic} efectivamente, 
            es importante entender conceptos como overfitting, cross-validation, feature engineering, 
            y evaluación de modelos.
            """,
            "Web Development": f"""
            {topic} involucra la creación de aplicaciones web utilizando tecnologías como HTML, CSS, 
            JavaScript, y frameworks modernos como React, Vue.js, o Angular. El desarrollo web incluye 
            tanto frontend (interfaz de usuario) como backend (lógica del servidor). Las mejores prácticas 
            en {topic} incluyen diseño responsivo, optimización de rendimiento, seguridad web, 
            y accesibilidad. Las herramientas modernas como Webpack, Babel, y ESLint ayudan a 
            automatizar tareas y mantener código de calidad.
            """,
            "Data Science": f"""
            {topic} combina estadística, programación, y conocimiento del dominio para extraer 
            insights de datos. Los científicos de datos utilizan herramientas como Python, R, 
            SQL, y bibliotecas como Pandas, NumPy, Scikit-learn, y TensorFlow. El proceso de 
            {topic} incluye recolección de datos, limpieza, exploración, modelado, y visualización. 
            Las técnicas incluyen análisis estadístico, machine learning, deep learning, 
            y big data analytics.
            """
        }
        
        # Usar template específico o genérico
        if topic in content_templates:
            return content_templates[topic]
        else:
            return f"""
            {topic} es un campo importante en la tecnología moderna que abarca múltiples aspectos 
            y aplicaciones. Este documento proporciona una guía completa sobre {topic}, incluyendo 
            conceptos fundamentales, mejores prácticas, y casos de uso reales. Los profesionales 
            en {topic} deben mantenerse actualizados con las últimas tendencias y tecnologías 
            para mantenerse competitivos en el mercado.
            """
    
    async def demo_document_processing(self):
        """Demostrar procesamiento de documentos"""
        logger.info("📄 Demostrando procesamiento de documentos...")
        
        for doc in self.documents[:5]:  # Procesar solo los primeros 5
            try:
                # Procesar documento
                processed = await self.document_processor.process_document(
                    doc["content"], 
                    doc["metadata"]
                )
                
                # Agregar a base de datos
                await self.vector_db.add_document(
                    doc["id"],
                    processed["content"],
                    processed["metadata"]
                )
                
                logger.info(f"✅ Documento procesado: {doc['title']}")
                
            except Exception as e:
                logger.error(f"❌ Error procesando documento {doc['id']}: {e}")
    
    async def demo_search_functionality(self):
        """Demostrar funcionalidades de búsqueda"""
        logger.info("🔍 Demostrando funcionalidades de búsqueda...")
        
        queries = [
            "machine learning algorithms",
            "web development best practices",
            "data science techniques",
            "artificial intelligence applications",
            "cloud computing services"
        ]
        
        for query in queries:
            try:
                logger.info(f"🔍 Buscando: '{query}'")
                
                # Búsqueda semántica
                start_time = time.time()
                semantic_results = await self.search_engine.semantic_search(query, limit=5)
                semantic_time = time.time() - start_time
                
                # Búsqueda por palabras clave
                start_time = time.time()
                keyword_results = await self.search_engine.keyword_search(query, limit=5)
                keyword_time = time.time() - start_time
                
                # Búsqueda híbrida
                start_time = time.time()
                hybrid_results = await self.search_engine.hybrid_search(query, limit=5)
                hybrid_time = time.time() - start_time
                
                logger.info(f"  📊 Semántica: {len(semantic_results)} resultados en {semantic_time:.3f}s")
                logger.info(f"  📊 Keywords: {len(keyword_results)} resultados en {keyword_time:.3f}s")
                logger.info(f"  📊 Híbrida: {len(hybrid_results)} resultados en {hybrid_time:.3f}s")
                
                # Simular interacciones de usuario
                for user_id in self.users[:2]:
                    await self.recommendation_engine.add_search_interaction(
                        user_id, query, hybrid_results, 
                        clicked_docs=[r["document_id"] for r in hybrid_results[:2]]
                    )
                
            except Exception as e:
                logger.error(f"❌ Error en búsqueda '{query}': {e}")
    
    async def demo_recommendation_system(self):
        """Demostrar sistema de recomendaciones"""
        logger.info("🎯 Demostrando sistema de recomendaciones...")
        
        for user_id in self.users:
            try:
                # Obtener recomendaciones colaborativas
                collaborative_recs = await self.recommendation_engine.get_recommendations(
                    user_id, limit=5, recommendation_type="collaborative"
                )
                
                # Obtener recomendaciones basadas en contenido
                content_recs = await self.recommendation_engine.get_recommendations(
                    user_id, limit=5, recommendation_type="content_based"
                )
                
                # Obtener recomendaciones híbridas
                hybrid_recs = await self.recommendation_engine.get_recommendations(
                    user_id, limit=5, recommendation_type="hybrid"
                )
                
                logger.info(f"👤 Usuario {user_id}:")
                logger.info(f"  🤝 Colaborativas: {len(collaborative_recs)} recomendaciones")
                logger.info(f"  📄 Basadas en contenido: {len(content_recs)} recomendaciones")
                logger.info(f"  🔄 Híbridas: {len(hybrid_recs)} recomendaciones")
                
            except Exception as e:
                logger.error(f"❌ Error obteniendo recomendaciones para {user_id}: {e}")
    
    async def demo_analytics_system(self):
        """Demostrar sistema de analytics"""
        logger.info("📊 Demostrando sistema de analytics...")
        
        try:
            # Generar analytics de búsqueda
            search_analytics = await self.analytics_engine.generate_search_analytics()
            logger.info(f"📈 Analytics de búsqueda generados: {len(search_analytics.get('queries', []))} consultas")
            
            # Generar analytics de usuarios
            user_analytics = await self.analytics_engine.generate_user_analytics()
            logger.info(f"👥 Analytics de usuarios generados: {user_analytics.get('total_users', 0)} usuarios")
            
            # Generar analytics de contenido
            content_analytics = await self.analytics_engine.generate_content_analytics()
            logger.info(f"📄 Analytics de contenido generados: {content_analytics.get('total_documents', 0)} documentos")
            
            # Generar analytics de rendimiento
            performance_analytics = await self.analytics_engine.generate_performance_analytics()
            logger.info(f"⚡ Analytics de rendimiento generados")
            
        except Exception as e:
            logger.error(f"❌ Error generando analytics: {e}")
    
    async def demo_notification_system(self):
        """Demostrar sistema de notificaciones"""
        logger.info("🔔 Demostrando sistema de notificaciones...")
        
        try:
            # Enviar diferentes tipos de notificaciones
            notification_types = [
                ("search_completed", "Búsqueda Completada", "Se encontraron 5 resultados para 'machine learning'"),
                ("document_uploaded", "Documento Subido", "El documento 'AI Guide.pdf' ha sido procesado"),
                ("recommendation_ready", "Recomendaciones Listas", "Tienes 3 nuevas recomendaciones personalizadas"),
                ("system_update", "Actualización del Sistema", "El sistema ha sido actualizado a la versión 2.0"),
                ("analytics_update", "Analytics Actualizados", "Los datos de analytics han sido actualizados")
            ]
            
            for notif_type, title, message in notification_types:
                await self.notification_system.send_notification(
                    type=notif_type,
                    priority="medium",
                    title=title,
                    message=message,
                    user_id=random.choice(self.users)
                )
                logger.info(f"📤 Notificación enviada: {title}")
            
            # Obtener notificaciones de un usuario
            user_notifications = await self.notification_system.get_user_notifications(
                self.users[0], limit=10
            )
            logger.info(f"📥 Notificaciones del usuario {self.users[0]}: {len(user_notifications)}")
            
        except Exception as e:
            logger.error(f"❌ Error en sistema de notificaciones: {e}")
    
    async def demo_cache_system(self):
        """Demostrar sistema de cache"""
        logger.info("💾 Demostrando sistema de cache...")
        
        try:
            # Probar operaciones básicas de cache
            test_data = {
                "search_results": [{"id": 1, "title": "Test Document"}],
                "user_profile": {"id": "user1", "preferences": ["AI", "ML"]},
                "analytics_data": {"queries": 100, "users": 50}
            }
            
            # Almacenar en cache
            for key, value in test_data.items():
                await self.cache_system.set(key, value, ttl=300, tags=["demo"])
                logger.info(f"💾 Almacenado en cache: {key}")
            
            # Recuperar del cache
            for key in test_data.keys():
                cached_value = await self.cache_system.get(key)
                if cached_value:
                    logger.info(f"📥 Recuperado del cache: {key}")
                else:
                    logger.warning(f"⚠️ No encontrado en cache: {key}")
            
            # Obtener estadísticas del cache
            cache_stats = self.cache_system.get_stats()
            logger.info(f"📊 Estadísticas del cache: {cache_stats.get('hit_rate_percent', 0):.1f}% hit rate")
            
        except Exception as e:
            logger.error(f"❌ Error en sistema de cache: {e}")
    
    async def demo_batch_processing(self):
        """Demostrar procesamiento por lotes"""
        logger.info("⚙️ Demostrando procesamiento por lotes...")
        
        try:
            # Crear lote de documentos
            batch_documents = self.documents[5:10]  # Usar documentos 6-10
            
            # Procesar lote
            batch_id = f"batch_{int(time.time())}"
            result = await self.batch_processor.process_batch(
                batch_id, batch_documents, "demo_user"
            )
            
            logger.info(f"📦 Lote procesado: {batch_id}")
            logger.info(f"  📄 Documentos procesados: {result.get('processed_count', 0)}")
            logger.info(f"  ✅ Estado: {result.get('status', 'unknown')}")
            
        except Exception as e:
            logger.error(f"❌ Error en procesamiento por lotes: {e}")
    
    async def demo_export_import(self):
        """Demostrar funcionalidades de export/import"""
        logger.info("📤📥 Demostrando export/import...")
        
        try:
            # Exportar datos
            export_data = await self.export_import.export_data(
                format="json", include_embeddings=True
            )
            logger.info(f"📤 Datos exportados: {len(export_data)} registros")
            
            # Simular importación
            import_result = await self.export_import.import_data(
                export_data, format="json", validate=True
            )
            logger.info(f"📥 Datos importados: {import_result.get('imported_count', 0)} registros")
            
        except Exception as e:
            logger.error(f"❌ Error en export/import: {e}")
    
    async def demo_performance_metrics(self):
        """Demostrar métricas de rendimiento"""
        logger.info("⚡ Demostrando métricas de rendimiento...")
        
        try:
            # Obtener estadísticas de todos los sistemas
            systems_stats = {
                "vector_db": await self.vector_db.get_statistics(),
                "recommendation_engine": self.recommendation_engine.get_recommendation_stats(),
                "notification_system": self.notification_system.get_notification_stats(),
                "cache_system": self.cache_system.get_stats()
            }
            
            logger.info("📊 Estadísticas del sistema:")
            for system, stats in systems_stats.items():
                logger.info(f"  🔧 {system}:")
                for key, value in stats.items():
                    if isinstance(value, (int, float)):
                        logger.info(f"    {key}: {value}")
                    else:
                        logger.info(f"    {key}: {type(value).__name__}")
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo métricas: {e}")
    
    async def cleanup(self):
        """Limpiar recursos"""
        try:
            logger.info("🧹 Limpiando recursos...")
            
            if hasattr(self, 'cache_system'):
                self.cache_system.stop_cleanup_thread()
            
            if hasattr(self, 'notification_system'):
                await self.notification_system.shutdown()
            
            logger.info("✅ Limpieza completada")
            
        except Exception as e:
            logger.error(f"❌ Error en limpieza: {e}")
    
    async def run_complete_demo(self):
        """Ejecutar demo completo"""
        try:
            logger.info("🎬 Iniciando Demo Avanzado del Sistema de Búsqueda AI")
            logger.info("=" * 60)
            
            # Inicializar sistemas
            await self.initialize_systems()
            
            # Generar datos de demostración
            self.generate_demo_documents(20)
            
            # Ejecutar demos
            await self.demo_document_processing()
            await self.demo_search_functionality()
            await self.demo_recommendation_system()
            await self.demo_analytics_system()
            await self.demo_notification_system()
            await self.demo_cache_system()
            await self.demo_batch_processing()
            await self.demo_export_import()
            await self.demo_performance_metrics()
            
            logger.info("=" * 60)
            logger.info("🎉 Demo completado exitosamente!")
            logger.info("📚 Revisa la documentación en SISTEMA_AVANZADO_COMPLETO.md")
            logger.info("🚀 El sistema está listo para usar en producción")
            
        except Exception as e:
            logger.error(f"❌ Error en demo: {e}")
        finally:
            await self.cleanup()

async def main():
    """Función principal"""
    demo = AdvancedDemo()
    await demo.run_complete_demo()

if __name__ == "__main__":
    asyncio.run(main())


























