"""
🧪 Test Suite para el Sistema de Gestión de Recursos Inteligente
Pruebas completas de todas las funcionalidades del sistema
"""

import asyncio
import unittest
import time
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
import sys
import traceback

# Importar el sistema de gestión de recursos
from intelligent_resource_manager import (
    ResourceType, ResourceConfig, ResourceMetrics, OptimizationAction,
    BaseResourceManager, CPUMemoryManager, GPUMemoryManager,
    IntelligentResourceOrchestrator
)

class TestResourceTypes(unittest.TestCase):
    """Pruebas para tipos de recursos."""
    
    def test_resource_type_enum(self):
        """Probar enumeración de tipos de recursos."""
        self.assertEqual(ResourceType.CPU.value, "cpu")
        self.assertEqual(ResourceType.MEMORY.value, "memory")
        self.assertEqual(ResourceType.GPU.value, "gpu")
        self.assertEqual(ResourceType.NETWORK.value, "network")
        self.assertEqual(ResourceType.STORAGE.value, "storage")

class TestResourceConfig(unittest.TestCase):
    """Pruebas para configuración de recursos."""
    
    def test_resource_config_defaults(self):
        """Probar valores por defecto de configuración."""
        config = ResourceConfig(ResourceType.MEMORY)
        
        self.assertEqual(config.resource_type, ResourceType.MEMORY)
        self.assertEqual(config.max_usage, 0.9)
        self.assertEqual(config.optimal_usage, 0.7)
        self.assertEqual(config.critical_threshold, 0.95)
        self.assertTrue(config.auto_optimize)
        self.assertEqual(config.prediction_horizon, 300)
    
    def test_resource_config_custom(self):
        """Probar configuración personalizada."""
        config = ResourceConfig(
            resource_type=ResourceType.GPU,
            max_usage=0.8,
            optimal_usage=0.6,
            critical_threshold=0.9,
            auto_optimize=False,
            prediction_horizon=180
        )
        
        self.assertEqual(config.resource_type, ResourceType.GPU)
        self.assertEqual(config.max_usage, 0.8)
        self.assertEqual(config.optimal_usage, 0.6)
        self.assertEqual(config.critical_threshold, 0.9)
        self.assertFalse(config.auto_optimize)
        self.assertEqual(config.prediction_horizon, 180)

class TestResourceMetrics(unittest.TestCase):
    """Pruebas para métricas de recursos."""
    
    def test_resource_metrics_creation(self):
        """Probar creación de métricas de recursos."""
        timestamp = time.time()
        metrics = ResourceMetrics(
            current_usage=0.75,
            peak_usage=0.85,
            average_usage=0.70,
            trend=0.05,
            prediction=0.80,
            timestamp=timestamp
        )
        
        self.assertEqual(metrics.current_usage, 0.75)
        self.assertEqual(metrics.peak_usage, 0.85)
        self.assertEqual(metrics.average_usage, 0.70)
        self.assertEqual(metrics.trend, 0.05)
        self.assertEqual(metrics.prediction, 0.80)
        self.assertEqual(metrics.timestamp, timestamp)

class TestOptimizationAction(unittest.TestCase):
    """Pruebas para acciones de optimización."""
    
    def test_optimization_action_creation(self):
        """Probar creación de acciones de optimización."""
        action = OptimizationAction(
            action_type="emergency_cleanup",
            resource=ResourceType.MEMORY,
            priority=1,
            expected_improvement=0.2,
            parameters={"force_gc": True, "clear_cache": True}
        )
        
        self.assertEqual(action.action_type, "emergency_cleanup")
        self.assertEqual(action.resource, ResourceType.MEMORY)
        self.assertEqual(action.priority, 1)
        self.assertEqual(action.expected_improvement, 0.2)
        self.assertEqual(action.parameters["force_gc"], True)
        self.assertEqual(action.parameters["clear_cache"], True)

class TestBaseResourceManager(unittest.TestCase):
    """Pruebas para gestor de recursos base."""
    
    def test_base_resource_manager_initialization(self):
        """Probar inicialización del gestor base."""
        config = ResourceConfig(ResourceType.MEMORY)
        manager = BaseResourceManager(config)
        
        self.assertEqual(manager.config, config)
        self.assertEqual(len(manager.metrics_history), 0)
        self.assertEqual(len(manager.optimization_history), 0)
        self.assertIsNone(manager.current_metrics)
    
    def test_base_resource_manager_abstract_methods(self):
        """Probar que los métodos abstractos no están implementados."""
        config = ResourceConfig(ResourceType.MEMORY)
        manager = BaseResourceManager(config)
        
        # collect_metrics debería lanzar NotImplementedError
        with self.assertRaises(NotImplementedError):
            asyncio.run(manager.collect_metrics())
        
        # optimize debería lanzar NotImplementedError
        with self.assertRaises(NotImplementedError):
            asyncio.run(manager.optimize())
    
    def test_base_resource_manager_metrics_summary_empty(self):
        """Probar resumen de métricas cuando no hay historial."""
        config = ResourceConfig(ResourceType.MEMORY)
        manager = BaseResourceManager(config)
        
        summary = manager.get_metrics_summary()
        self.assertEqual(summary, {})
    
    def test_base_resource_manager_metrics_summary_with_data(self):
        """Probar resumen de métricas con datos."""
        config = ResourceConfig(ResourceType.MEMORY)
        manager = BaseResourceManager(config)
        
        # Simular métricas
        manager.current_metrics = ResourceMetrics(
            current_usage=0.75,
            peak_usage=0.85,
            average_usage=0.70,
            trend=0.05,
            prediction=0.80,
            timestamp=time.time()
        )
        
        manager.metrics_history = [manager.current_metrics]
        manager.optimization_history = [Mock()]
        
        summary = manager.get_metrics_summary()
        
        self.assertEqual(summary['resource_type'], 'memory')
        self.assertEqual(summary['current_usage'], 0.75)
        self.assertEqual(summary['peak_usage'], 0.85)
        self.assertEqual(summary['average_usage'], 0.70)
        self.assertEqual(summary['trend'], 0.05)
        self.assertEqual(summary['optimization_count'], 1)

class TestCPUMemoryManager(unittest.TestCase):
    """Pruebas para gestor de CPU y memoria."""
    
    def setUp(self):
        """Configurar para cada prueba."""
        self.config = ResourceConfig(ResourceType.MEMORY)
        self.manager = CPUMemoryManager(self.config)
    
    @patch('psutil.cpu_percent')
    @patch('psutil.cpu_count')
    @patch('psutil.virtual_memory')
    def test_collect_metrics(self, mock_virtual_memory, mock_cpu_count, mock_cpu_percent):
        """Probar recolección de métricas de CPU y memoria."""
        # Mock de psutil
        mock_cpu_percent.return_value = 45.0
        mock_cpu_count.return_value = 8
        
        mock_memory = Mock()
        mock_memory.percent = 75.0
        mock_virtual_memory.return_value = mock_memory
        
        # Ejecutar recolección
        metrics = asyncio.run(self.manager.collect_metrics())
        
        # Verificar métricas
        self.assertEqual(metrics.current_usage, 0.75)
        self.assertEqual(metrics.peak_usage, 0.75)
        self.assertEqual(metrics.average_usage, 0.75)
        self.assertEqual(metrics.trend, 0.0)
        self.assertEqual(metrics.prediction, 0.75)
        
        # Verificar que se guardó en el historial
        self.assertEqual(len(self.manager.metrics_history), 1)
        self.assertEqual(self.manager.current_metrics, metrics)
    
    def test_optimize_emergency(self):
        """Probar optimización de emergencia."""
        # Simular métricas críticas
        self.manager.current_metrics = ResourceMetrics(
            current_usage=0.85,
            peak_usage=0.90,
            average_usage=0.80,
            trend=0.1,
            prediction=0.96,  # Por encima del umbral crítico
            timestamp=time.time()
        )
        
        action = asyncio.run(self.manager.optimize())
        
        self.assertEqual(action.action_type, "emergency_cleanup")
        self.assertEqual(action.priority, 1)
        self.assertEqual(action.expected_improvement, 0.2)
        self.assertTrue(action.parameters['force_garbage_collection'])
        self.assertTrue(action.parameters['clear_caches'])
        self.assertTrue(action.parameters['kill_non_essential_processes'])
        self.assertTrue(action.parameters['memory_compression'])
    
    def test_optimize_aggressive(self):
        """Probar optimización agresiva."""
        # Simular métricas altas
        self.manager.current_metrics = ResourceMetrics(
            current_usage=0.80,
            peak_usage=0.85,
            average_usage=0.75,
            trend=0.05,
            prediction=0.92,  # Por encima del máximo
            timestamp=time.time()
        )
        
        action = asyncio.run(self.manager.optimize())
        
        self.assertEqual(action.action_type, "aggressive_optimization")
        self.assertEqual(action.priority, 2)
        self.assertEqual(action.expected_improvement, 0.15)
        self.assertTrue(action.parameters['garbage_collection'])
        self.assertTrue(action.parameters['clear_caches'])
        self.assertTrue(action.parameters['memory_compression'])
        self.assertTrue(action.parameters['process_priority_adjustment'])
    
    def test_optimize_preventive(self):
        """Probar optimización preventiva."""
        # Simular métricas moderadas
        self.manager.current_metrics = ResourceMetrics(
            current_usage=0.75,
            peak_usage=0.80,
            average_usage=0.70,
            trend=0.02,
            prediction=0.78,  # Por encima del óptimo
            timestamp=time.time()
        )
        
        action = asyncio.run(self.manager.optimize())
        
        self.assertEqual(action.action_type, "preventive_optimization")
        self.assertEqual(action.priority, 3)
        self.assertEqual(action.expected_improvement, 0.1)
        self.assertTrue(action.parameters['garbage_collection'])
        self.assertFalse(action.parameters['clear_caches'])
        self.assertFalse(action.parameters['memory_compression'])
        self.assertFalse(action.parameters['process_priority_adjustment'])
    
    def test_optimize_maintenance(self):
        """Probar optimización de mantenimiento."""
        # Simular métricas bajas
        self.manager.current_metrics = ResourceMetrics(
            current_usage=0.60,
            peak_usage=0.70,
            average_usage=0.65,
            trend=0.01,
            prediction=0.62,  # Por debajo del óptimo
            timestamp=time.time()
        )
        
        action = asyncio.run(self.manager.optimize())
        
        self.assertEqual(action.action_type, "maintenance_optimization")
        self.assertEqual(action.priority, 4)
        self.assertEqual(action.expected_improvement, 0.05)
        self.assertFalse(action.parameters['garbage_collection'])
        self.assertFalse(action.parameters['clear_caches'])
        self.assertFalse(action.parameters['memory_compression'])
        self.assertFalse(action.parameters['process_priority_adjustment'])

class TestGPUMemoryManager(unittest.TestCase):
    """Pruebas para gestor de GPU."""
    
    def setUp(self):
        """Configurar para cada prueba."""
        self.config = ResourceConfig(ResourceType.GPU)
        self.manager = GPUMemoryManager(self.config)
    
    @patch('intelligent_resource_manager.GPUtil')
    def test_collect_metrics_with_gpu(self, mock_gputil):
        """Probar recolección de métricas con GPU disponible."""
        # Mock de GPU
        mock_gpu = Mock()
        mock_gpu.memoryUtil = 0.65
        mock_gpu.memoryUsed = 8192
        mock_gpu.memoryTotal = 16384
        
        mock_gputil.getGPUs.return_value = [mock_gpu]
        
        # Ejecutar recolección
        metrics = asyncio.run(self.manager.collect_metrics())
        
        # Verificar métricas
        self.assertEqual(metrics.current_usage, 0.65)
        self.assertEqual(metrics.peak_usage, 0.65)
        self.assertEqual(metrics.average_usage, 0.65)
        self.assertEqual(metrics.trend, 0.0)
        self.assertEqual(metrics.prediction, 0.65)
    
    @patch('intelligent_resource_manager.GPUtil')
    def test_collect_metrics_no_gpu(self, mock_gputil):
        """Probar recolección de métricas sin GPU."""
        # No hay GPU disponible
        mock_gputil.getGPUs.return_value = []
        
        # Ejecutar recolección
        metrics = asyncio.run(self.manager.collect_metrics())
        
        # Verificar métricas simuladas
        self.assertEqual(metrics.current_usage, 0.0)
        self.assertEqual(metrics.peak_usage, 0.0)
        self.assertEqual(metrics.average_usage, 0.0)
        self.assertEqual(metrics.trend, 0.0)
        self.assertEqual(metrics.prediction, 0.0)
    
    def test_optimize_gpu_emergency(self):
        """Probar optimización de emergencia de GPU."""
        # Simular métricas críticas de GPU
        self.manager.current_metrics = ResourceMetrics(
            current_usage=0.85,
            peak_usage=0.90,
            average_usage=0.80,
            trend=0.1,
            prediction=0.96,  # Por encima del umbral crítico
            timestamp=time.time()
        )
        
        action = asyncio.run(self.manager.optimize())
        
        self.assertEqual(action.action_type, "gpu_emergency_cleanup")
        self.assertEqual(action.priority, 1)
        self.assertEqual(action.expected_improvement, 0.25)
        self.assertTrue(action.parameters['clear_gpu_cache'])
        self.assertTrue(action.parameters['reset_gpu_context'])
        self.assertTrue(action.parameters['kill_gpu_processes'])
        self.assertTrue(action.parameters['memory_compression'])

class TestIntelligentResourceOrchestrator(unittest.TestCase):
    """Pruebas para el orquestador de recursos."""
    
    def setUp(self):
        """Configurar para cada prueba."""
        self.orchestrator = IntelligentResourceOrchestrator()
    
    def test_orchestrator_initialization(self):
        """Probar inicialización del orquestador."""
        self.assertFalse(self.orchestrator.running)
        self.assertEqual(len(self.orchestrator.resource_managers), 2)
        self.assertIn('cpu_memory', self.orchestrator.resource_managers)
        self.assertIn('gpu', self.orchestrator.resource_managers)
        self.assertEqual(len(self.orchestrator.optimization_queue), 0)
        self.assertEqual(len(self.orchestrator.prediction_models), 0)
    
    def test_setup_resource_managers(self):
        """Probar configuración de gestores de recursos."""
        # Verificar que se configuraron correctamente
        cpu_manager = self.orchestrator.resource_managers['cpu_memory']
        gpu_manager = self.orchestrator.resource_managers['gpu']
        
        self.assertIsInstance(cpu_manager, CPUMemoryManager)
        self.assertIsInstance(gpu_manager, GPUMemoryManager)
        self.assertEqual(cpu_manager.config.resource_type, ResourceType.MEMORY)
        self.assertEqual(gpu_manager.config.resource_type, ResourceType.GPU)
    
    async def test_start_stop(self):
        """Probar inicio y detención del orquestador."""
        # Iniciar
        await self.orchestrator.start()
        self.assertTrue(self.orchestrator.running)
        
        # Detener
        await self.orchestrator.stop()
        self.assertFalse(self.orchestrator.running)
    
    async def test_collect_all_metrics(self):
        """Probar recolección de métricas de todos los recursos."""
        metrics = await self.orchestrator.collect_all_metrics()
        
        self.assertIn('cpu_memory', metrics)
        self.assertIn('gpu', metrics)
        self.assertIsInstance(metrics['cpu_memory'], ResourceMetrics)
        self.assertIsInstance(metrics['gpu'], ResourceMetrics)
    
    async def test_optimize_all_resources(self):
        """Probar optimización de todos los recursos."""
        optimizations = await self.orchestrator.optimize_all_resources()
        
        self.assertIn('cpu_memory', optimizations)
        self.assertIn('gpu', optimizations)
        self.assertIsInstance(optimizations['cpu_memory'], OptimizationAction)
        self.assertIsInstance(optimizations['gpu'], OptimizationAction)
        
        # Verificar que se agregaron a la cola
        self.assertGreater(len(self.orchestrator.optimization_queue), 0)
    
    async def test_get_resource_summary(self):
        """Probar obtención de resumen de recursos."""
        summary = await self.orchestrator.get_resource_summary()
        
        self.assertIn('resources', summary)
        self.assertIn('cpu_memory', summary['resources'])
        self.assertIn('gpu', summary['resources'])
        self.assertIn('optimization_queue_size', summary)
        self.assertIn('total_optimizations', summary)
    
    async def test_analyze_and_predict_critical(self):
        """Probar análisis y predicción de problemas críticos."""
        # Simular métricas críticas
        critical_metrics = {
            'cpu_memory': ResourceMetrics(
                current_usage=0.85,
                peak_usage=0.90,
                average_usage=0.80,
                trend=0.1,
                prediction=0.96,  # Crítico
                timestamp=time.time()
            )
        }
        
        # Ejecutar análisis
        await self.orchestrator._analyze_and_predict(critical_metrics)
        
        # Verificar que se programó optimización de emergencia
        self.assertGreater(len(self.orchestrator.optimization_queue), 0)
        emergency_action = self.orchestrator.optimization_queue[0]
        self.assertEqual(emergency_action.priority, 0)  # Máxima prioridad

class TestIntegration(unittest.TestCase):
    """Pruebas de integración del sistema completo."""
    
    async def test_full_system_workflow(self):
        """Probar flujo completo del sistema."""
        orchestrator = IntelligentResourceOrchestrator()
        
        try:
            # 1. Iniciar sistema
            await orchestrator.start()
            self.assertTrue(orchestrator.running)
            
            # 2. Recolectar métricas iniciales
            initial_metrics = await orchestrator.collect_all_metrics()
            self.assertGreater(len(initial_metrics), 0)
            
            # 3. Ejecutar optimización
            optimizations = await orchestrator.optimize_all_resources()
            self.assertGreater(len(optimizations), 0)
            
            # 4. Obtener resumen
            summary = await orchestrator.get_resource_summary()
            self.assertIn('resources', summary)
            self.assertIn('optimization_queue_size', summary)
            
            # 5. Verificar que las optimizaciones se procesan
            await asyncio.sleep(1)  # Dar tiempo para procesar
            
        finally:
            await orchestrator.stop()
            self.assertFalse(orchestrator.running)

def run_tests():
    """Ejecutar todas las pruebas."""
    print("🧪 Ejecutando Test Suite del Sistema de Gestión de Recursos Inteligente")
    print("=" * 80)
    
    # Crear suite de pruebas
    test_suite = unittest.TestSuite()
    
    # Agregar pruebas
    test_classes = [
        TestResourceTypes,
        TestResourceConfig,
        TestResourceMetrics,
        TestOptimizationAction,
        TestBaseResourceManager,
        TestCPUMemoryManager,
        TestGPUMemoryManager,
        TestIntelligentResourceOrchestrator,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Ejecutar pruebas
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Resumen
    print("\n" + "=" * 80)
    print("📊 RESUMEN DE PRUEBAS")
    print(f"   Pruebas ejecutadas: {result.testsRun}")
    print(f"   Fallos: {len(result.failures)}")
    print(f"   Errores: {len(result.errors)}")
    print(f"   Exitosas: {result.testsRun - len(result.failures) - len(result.errors)}")
    
    if result.failures:
        print("\n❌ FALLOS:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback}")
    
    if result.errors:
        print("\n🚨 ERRORES:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
        return True
    else:
        print("\n💥 Algunas pruebas fallaron.")
        return False

if __name__ == "__main__":
    # Ejecutar pruebas
    success = asyncio.run(run_tests())
    
    # Código de salida
    sys.exit(0 if success else 1)
