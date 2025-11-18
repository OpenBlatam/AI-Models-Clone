#!/usr/bin/env python3
"""
AI Search Model - Script de Demostración
Demuestra las capacidades del sistema de búsqueda IA
"""

import asyncio
import json
import time
from datetime import datetime
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.search_engine import AISearchEngine
from models.document_processor import DocumentProcessor
from database.vector_db import VectorDatabase

class AISearchDemo:
    """Demostración del sistema de búsqueda IA"""
    
    def __init__(self):
        self.search_engine = None
        self.document_processor = None
        self.vector_db = None
        
        # Documentos de ejemplo
        self.sample_documents = [
            {
                "title": "Introducción a la Inteligencia Artificial",
                "content": """
                La inteligencia artificial (IA) es una rama de la informática que se ocupa de crear 
                sistemas capaces de realizar tareas que normalmente requieren inteligencia humana. 
                Estos sistemas pueden aprender, razonar, percibir y tomar decisiones.
                
                Los principales tipos de IA incluyen:
                - Aprendizaje automático (Machine Learning)
                - Redes neuronales artificiales
                - Procesamiento del lenguaje natural
                - Visión por computadora
                - Sistemas expertos
                
                La IA tiene aplicaciones en múltiples campos como medicina, finanzas, 
                transporte, entretenimiento y muchos más.
                """,
                "metadata": {
                    "category": "tecnologia",
                    "difficulty": "principiante",
                    "tags": ["IA", "inteligencia artificial", "tecnologia"]
                }
            },
            {
                "title": "Machine Learning y Deep Learning",
                "content": """
                El machine learning es un subcampo de la inteligencia artificial que se enfoca 
                en el desarrollo de algoritmos que pueden aprender y hacer predicciones o 
                decisiones basadas en datos.
                
                Deep Learning es una rama del machine learning que utiliza redes neuronales 
                con múltiples capas (de ahí el término "deep") para modelar y entender 
                patrones complejos en los datos.
                
                Algoritmos populares de machine learning:
                - Regresión lineal y logística
                - Árboles de decisión
                - Random Forest
                - Support Vector Machines
                - K-means clustering
                
                Frameworks populares:
                - TensorFlow
                - PyTorch
                - Scikit-learn
                - Keras
                """,
                "metadata": {
                    "category": "tecnologia",
                    "difficulty": "intermedio",
                    "tags": ["machine learning", "deep learning", "algoritmos"]
                }
            },
            {
                "title": "Python para Ciencia de Datos",
                "content": """
                Python se ha convertido en uno de los lenguajes más populares para ciencia de datos 
                debido a su simplicidad, versatilidad y la gran cantidad de librerías disponibles.
                
                Librerías esenciales de Python para ciencia de datos:
                - NumPy: Computación numérica
                - Pandas: Manipulación de datos
                - Matplotlib: Visualización
                - Seaborn: Visualización estadística
                - Scikit-learn: Machine learning
                - TensorFlow/PyTorch: Deep learning
                
                Python es ideal para:
                - Análisis exploratorio de datos
                - Limpieza y transformación de datos
                - Modelado estadístico
                - Visualización de datos
                - Implementación de algoritmos de ML
                """,
                "metadata": {
                    "category": "programacion",
                    "difficulty": "principiante",
                    "tags": ["python", "ciencia de datos", "programacion"]
                }
            },
            {
                "title": "Bases de Datos y SQL",
                "content": """
                Las bases de datos son sistemas de almacenamiento organizados que permiten 
                guardar, recuperar y manipular grandes cantidades de datos de manera eficiente.
                
                SQL (Structured Query Language) es el lenguaje estándar para interactuar 
                con bases de datos relacionales.
                
                Tipos de bases de datos:
                - Relacionales (MySQL, PostgreSQL, SQLite)
                - NoSQL (MongoDB, Cassandra, Redis)
                - Bases de datos vectoriales (para IA)
                - Bases de datos de grafos (Neo4j)
                
                Operaciones básicas de SQL:
                - SELECT: Consultar datos
                - INSERT: Insertar datos
                - UPDATE: Actualizar datos
                - DELETE: Eliminar datos
                - CREATE: Crear tablas
                - ALTER: Modificar estructura
                """,
                "metadata": {
                    "category": "programacion",
                    "difficulty": "intermedio",
                    "tags": ["bases de datos", "SQL", "programacion"]
                }
            },
            {
                "title": "Desarrollo Web con React",
                "content": """
                React es una librería de JavaScript desarrollada por Facebook para crear 
                interfaces de usuario interactivas y reutilizables.
                
                Características principales de React:
                - Componentes reutilizables
                - Virtual DOM para mejor rendimiento
                - JSX para escribir HTML en JavaScript
                - Estado y props para manejo de datos
                - Hooks para funcionalidad avanzada
                
                Conceptos importantes:
                - Componentes funcionales y de clase
                - Estado local y global
                - Props y comunicación entre componentes
                - Ciclo de vida de componentes
                - Hooks (useState, useEffect, useContext)
                
                React es ampliamente usado en aplicaciones web modernas y se integra 
                bien con otras tecnologías como Node.js, Express y bases de datos.
                """,
                "metadata": {
                    "category": "programacion",
                    "difficulty": "intermedio",
                    "tags": ["react", "javascript", "desarrollo web"]
                }
            }
        ]
    
    async def initialize(self):
        """Inicializar todos los componentes"""
        print("🚀 Inicializando sistema de búsqueda IA...")
        
        try:
            # Inicializar procesador de documentos
            print("📄 Inicializando procesador de documentos...")
            self.document_processor = DocumentProcessor()
            
            # Inicializar base de datos vectorial
            print("🗄️  Inicializando base de datos vectorial...")
            self.vector_db = VectorDatabase()
            await self.vector_db.initialize()
            
            # Inicializar motor de búsqueda
            print("🧠 Inicializando motor de búsqueda IA...")
            self.search_engine = AISearchEngine()
            await self.search_engine.initialize()
            
            print("✅ Sistema inicializado correctamente")
            
        except Exception as e:
            print(f"❌ Error al inicializar: {e}")
            raise
    
    async def load_sample_documents(self):
        """Cargar documentos de ejemplo"""
        print("\n📚 Cargando documentos de ejemplo...")
        
        processed_documents = []
        
        for i, doc in enumerate(self.sample_documents):
            print(f"  Procesando documento {i+1}: {doc['title']}")
            
            # Procesar documento
            processed_doc = await self.document_processor.process_document(
                title=doc["title"],
                content=doc["content"],
                metadata=doc["metadata"],
                document_type="text"
            )
            
            # Agregar a base de datos
            await self.vector_db.add_document(processed_doc)
            processed_documents.append(processed_doc)
        
        # Agregar documentos al motor de búsqueda
        await self.search_engine.add_documents(processed_documents)
        
        print(f"✅ {len(processed_documents)} documentos cargados")
    
    async def run_search_demo(self):
        """Ejecutar demostración de búsquedas"""
        print("\n🔍 Demostración de búsquedas IA")
        print("=" * 50)
        
        # Consultas de ejemplo
        queries = [
            {
                "query": "inteligencia artificial",
                "type": "semantic",
                "description": "Búsqueda semántica por IA"
            },
            {
                "query": "machine learning",
                "type": "keyword",
                "description": "Búsqueda por palabras clave"
            },
            {
                "query": "python programación",
                "type": "hybrid",
                "description": "Búsqueda híbrida"
            },
            {
                "query": "bases de datos SQL",
                "type": "semantic",
                "description": "Búsqueda semántica por bases de datos"
            },
            {
                "query": "react javascript",
                "type": "hybrid",
                "description": "Búsqueda híbrida por React"
            }
        ]
        
        for i, search in enumerate(queries, 1):
            print(f"\n🔎 Búsqueda {i}: {search['description']}")
            print(f"Consulta: '{search['query']}'")
            print(f"Tipo: {search['type']}")
            print("-" * 40)
            
            start_time = time.time()
            
            try:
                # Realizar búsqueda
                results = await self.search_engine.search(
                    query=search["query"],
                    search_type=search["type"],
                    limit=3
                )
                
                end_time = time.time()
                search_time = (end_time - start_time) * 1000  # en milisegundos
                
                print(f"⏱️  Tiempo de búsqueda: {search_time:.1f}ms")
                print(f"📊 Resultados encontrados: {len(results)}")
                
                # Mostrar resultados
                for j, result in enumerate(results, 1):
                    print(f"\n  {j}. {result['title']}")
                    print(f"     Puntuación: {result['score']:.3f}")
                    print(f"     Snippet: {result['snippet'][:100]}...")
                    if 'semantic_score' in result and 'keyword_score' in result:
                        print(f"     Semántica: {result['semantic_score']:.3f}, Keywords: {result['keyword_score']:.3f}")
                
            except Exception as e:
                print(f"❌ Error en búsqueda: {e}")
            
            print("-" * 40)
    
    async def show_statistics(self):
        """Mostrar estadísticas del sistema"""
        print("\n📊 Estadísticas del Sistema")
        print("=" * 50)
        
        try:
            # Estadísticas de la base de datos
            db_stats = await self.vector_db.get_statistics()
            print("🗄️  Base de Datos:")
            print(f"  - Total documentos: {db_stats.get('total_documents', 0)}")
            print(f"  - Tamaño BD: {db_stats.get('database_size_bytes', 0) / 1024:.1f} KB")
            print(f"  - Tamaño embeddings: {db_stats.get('embeddings_size_bytes', 0) / 1024:.1f} KB")
            
            # Estadísticas del motor de búsqueda
            search_stats = self.search_engine.get_statistics()
            print("\n🧠 Motor de Búsqueda:")
            print(f"  - Modelo: {search_stats.get('embedding_model', 'N/A')}")
            print(f"  - Dimensiones: {search_stats.get('embedding_dimensions', 0)}")
            print(f"  - Características TF-IDF: {search_stats.get('tfidf_features', 0)}")
            
            # Estadísticas del procesador
            processor_stats = self.document_processor.get_processing_statistics()
            print("\n📄 Procesador de Documentos:")
            print(f"  - Tipos soportados: {', '.join(processor_stats.get('supported_types', []))}")
            print(f"  - Longitud máxima: {processor_stats.get('max_content_length', 0)} caracteres")
            
        except Exception as e:
            print(f"❌ Error al obtener estadísticas: {e}")
    
    async def cleanup(self):
        """Limpiar recursos"""
        print("\n🧹 Limpiando recursos...")
        
        if self.vector_db:
            await self.vector_db.close()
        
        print("✅ Limpieza completada")
    
    async def run_demo(self):
        """Ejecutar demostración completa"""
        try:
            print("🤖 AI Search Model - Demostración")
            print("=" * 50)
            print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 50)
            
            # Inicializar sistema
            await self.initialize()
            
            # Cargar documentos de ejemplo
            await self.load_sample_documents()
            
            # Mostrar estadísticas
            await self.show_statistics()
            
            # Ejecutar demostración de búsquedas
            await self.run_search_demo()
            
            print("\n🎉 Demostración completada exitosamente!")
            print("=" * 50)
            print("💡 Para usar el sistema completo:")
            print("   1. Ejecuta: python start.py")
            print("   2. Abre: http://localhost:3000")
            print("   3. API: http://localhost:8000/docs")
            
        except Exception as e:
            print(f"❌ Error en demostración: {e}")
            return 1
        
        finally:
            await self.cleanup()
        
        return 0

async def main():
    """Función principal"""
    demo = AISearchDemo()
    return await demo.run_demo()

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)



























