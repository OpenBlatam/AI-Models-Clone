#!/usr/bin/env python3
"""
AI Search Model - Script de Prueba del Sistema
Verifica que todos los componentes funcionen correctamente
"""

import asyncio
import sys
import os
import time
import json
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.search_engine import AISearchEngine
from models.document_processor import DocumentProcessor
from database.vector_db import VectorDatabase
from config.settings import Settings

class SystemTester:
    """Probador del sistema completo"""
    
    def __init__(self):
        self.search_engine = None
        self.document_processor = None
        self.vector_db = None
        self.settings = None
        self.test_results = []
        
    async def initialize_components(self):
        """Inicializar todos los componentes del sistema"""
        print("🔧 Inicializando componentes del sistema...")
        
        try:
            # Inicializar configuración
            self.settings = Settings()
            if not self.settings.validate_config():
                raise Exception("Configuración inválida")
            
            # Inicializar procesador de documentos
            self.document_processor = DocumentProcessor()
            
            # Inicializar base de datos vectorial
            self.vector_db = VectorDatabase()
            await self.vector_db.initialize()
            
            # Inicializar motor de búsqueda
            self.search_engine = AISearchEngine()
            await self.search_engine.initialize()
            
            self.add_test_result("Inicialización", True, "Todos los componentes inicializados correctamente")
            print("✅ Componentes inicializados correctamente")
            
        except Exception as e:
            self.add_test_result("Inicialización", False, f"Error: {e}")
            print(f"❌ Error en inicialización: {e}")
            raise
    
    def add_test_result(self, test_name, success, message):
        """Agregar resultado de prueba"""
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    
    async def test_document_processing(self):
        """Probar procesamiento de documentos"""
        print("\n📄 Probando procesamiento de documentos...")
        
        test_documents = [
            {
                "title": "Test Document 1",
                "content": "Este es un documento de prueba para verificar el procesamiento de texto.",
                "metadata": {"category": "test", "tags": ["prueba", "test"]},
                "document_type": "text"
            },
            {
                "title": "Test Markdown",
                "content": "# Título\n\nEste es un documento **Markdown** con *formato*.",
                "metadata": {"category": "test"},
                "document_type": "markdown"
            }
        ]
        
        try:
            processed_docs = []
            for doc in test_documents:
                processed = await self.document_processor.process_document(
                    title=doc["title"],
                    content=doc["content"],
                    metadata=doc["metadata"],
                    document_type=doc["document_type"]
                )
                processed_docs.append(processed)
            
            self.add_test_result("Procesamiento de Documentos", True, f"{len(processed_docs)} documentos procesados")
            print(f"✅ {len(processed_docs)} documentos procesados correctamente")
            return processed_docs
            
        except Exception as e:
            self.add_test_result("Procesamiento de Documentos", False, f"Error: {e}")
            print(f"❌ Error en procesamiento: {e}")
            return []
    
    async def test_database_operations(self, documents):
        """Probar operaciones de base de datos"""
        print("\n🗄️  Probando operaciones de base de datos...")
        
        try:
            # Agregar documentos
            for doc in documents:
                await self.vector_db.add_document(doc)
            
            # Listar documentos
            doc_list = await self.vector_db.list_documents(limit=10)
            
            # Obtener estadísticas
            stats = await self.vector_db.get_statistics()
            
            # Buscar documentos
            search_results = await self.vector_db.search_documents("test", limit=5)
            
            self.add_test_result("Base de Datos", True, f"{len(doc_list)} documentos en BD, {len(search_results)} resultados de búsqueda")
            print(f"✅ Base de datos: {len(doc_list)} documentos, {len(search_results)} resultados de búsqueda")
            
        except Exception as e:
            self.add_test_result("Base de Datos", False, f"Error: {e}")
            print(f"❌ Error en base de datos: {e}")
    
    async def test_search_engine(self, documents):
        """Probar motor de búsqueda"""
        print("\n🔍 Probando motor de búsqueda...")
        
        try:
            # Agregar documentos al motor de búsqueda
            await self.search_engine.add_documents(documents)
            
            # Probar diferentes tipos de búsqueda
            search_queries = [
                {"query": "documento prueba", "type": "semantic"},
                {"query": "test", "type": "keyword"},
                {"query": "markdown formato", "type": "hybrid"}
            ]
            
            search_results = []
            for search in search_queries:
                results = await self.search_engine.search(
                    query=search["query"],
                    search_type=search["type"],
                    limit=3
                )
                search_results.extend(results)
            
            # Obtener estadísticas del motor
            engine_stats = self.search_engine.get_statistics()
            
            self.add_test_result("Motor de Búsqueda", True, f"{len(search_results)} resultados de búsqueda, {engine_stats.get('total_documents', 0)} documentos indexados")
            print(f"✅ Motor de búsqueda: {len(search_results)} resultados, {engine_stats.get('total_documents', 0)} documentos indexados")
            
        except Exception as e:
            self.add_test_result("Motor de Búsqueda", False, f"Error: {e}")
            print(f"❌ Error en motor de búsqueda: {e}")
    
    async def test_performance(self):
        """Probar rendimiento del sistema"""
        print("\n⚡ Probando rendimiento...")
        
        try:
            # Probar tiempo de búsqueda
            start_time = time.time()
            results = await self.search_engine.search("test", limit=10)
            search_time = (time.time() - start_time) * 1000  # en ms
            
            # Probar procesamiento en lote
            batch_docs = [
                {
                    "title": f"Batch Document {i}",
                    "content": f"Contenido del documento de lote número {i}",
                    "metadata": {"batch": True},
                    "document_type": "text"
                }
                for i in range(5)
            ]
            
            start_time = time.time()
            processed_batch = await self.document_processor.batch_process_documents(batch_docs)
            batch_time = (time.time() - start_time) * 1000  # en ms
            
            performance_ok = search_time < 1000 and batch_time < 2000  # Límites razonables
            
            self.add_test_result("Rendimiento", performance_ok, f"Búsqueda: {search_time:.1f}ms, Lote: {batch_time:.1f}ms")
            print(f"✅ Rendimiento: Búsqueda {search_time:.1f}ms, Procesamiento lote {batch_time:.1f}ms")
            
        except Exception as e:
            self.add_test_result("Rendimiento", False, f"Error: {e}")
            print(f"❌ Error en prueba de rendimiento: {e}")
    
    async def test_error_handling(self):
        """Probar manejo de errores"""
        print("\n🛡️  Probando manejo de errores...")
        
        try:
            # Probar búsqueda con consulta vacía
            try:
                await self.search_engine.search("", limit=5)
                error_handling_ok = False
                error_msg = "No se detectó error con consulta vacía"
            except:
                error_handling_ok = True
                error_msg = "Manejo correcto de consulta vacía"
            
            # Probar documento inválido
            try:
                await self.document_processor.process_document("", "", {}, "invalid_type")
                error_handling_ok = False
                error_msg = "No se detectó error con tipo inválido"
            except:
                error_handling_ok = True
                error_msg = "Manejo correcto de tipo inválido"
            
            self.add_test_result("Manejo de Errores", error_handling_ok, error_msg)
            print(f"✅ Manejo de errores: {error_msg}")
            
        except Exception as e:
            self.add_test_result("Manejo de Errores", False, f"Error: {e}")
            print(f"❌ Error en prueba de manejo de errores: {e}")
    
    async def cleanup(self):
        """Limpiar recursos"""
        print("\n🧹 Limpiando recursos...")
        
        try:
            if self.vector_db:
                await self.vector_db.close()
            print("✅ Limpieza completada")
        except Exception as e:
            print(f"⚠️  Error en limpieza: {e}")
    
    def generate_report(self):
        """Generar reporte de pruebas"""
        print("\n📊 Generando reporte de pruebas...")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "timestamp": datetime.now().isoformat()
            },
            "results": self.test_results
        }
        
        # Guardar reporte
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Mostrar resumen
        print("\n" + "="*60)
        print("📋 REPORTE DE PRUEBAS DEL SISTEMA")
        print("="*60)
        print(f"Total de pruebas: {total_tests}")
        print(f"Exitosas: {passed_tests} ✅")
        print(f"Fallidas: {failed_tests} ❌")
        print(f"Tasa de éxito: {report['summary']['success_rate']:.1f}%")
        print("="*60)
        
        # Mostrar detalles
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}: {result['message']}")
        
        print("="*60)
        print(f"📄 Reporte detallado guardado en: {report_file}")
        
        return report
    
    async def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        try:
            print("🧪 AI Search Model - Pruebas del Sistema")
            print("="*60)
            print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*60)
            
            # Inicializar componentes
            await self.initialize_components()
            
            # Probar procesamiento de documentos
            documents = await self.test_document_processing()
            
            if documents:
                # Probar base de datos
                await self.test_database_operations(documents)
                
                # Probar motor de búsqueda
                await self.test_search_engine(documents)
                
                # Probar rendimiento
                await self.test_performance()
            
            # Probar manejo de errores
            await self.test_error_handling()
            
            # Generar reporte
            report = self.generate_report()
            
            # Determinar si las pruebas fueron exitosas
            success_rate = report['summary']['success_rate']
            if success_rate >= 80:
                print("\n🎉 ¡Sistema funcionando correctamente!")
                return 0
            else:
                print("\n⚠️  Sistema con problemas, revisar reporte")
                return 1
            
        except Exception as e:
            print(f"\n❌ Error crítico en las pruebas: {e}")
            return 1
        
        finally:
            await self.cleanup()

async def main():
    """Función principal"""
    tester = SystemTester()
    return await tester.run_all_tests()

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)



























