"""
Test Suite para el Sistema de Integración Modular
Valida la integración entre todos los módulos modulares
"""

import asyncio
import unittest
import tempfile
import json
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Importar sistema de integración
from modular_integration_system import (
    ModularIntegrationSystem,
    IntegrationConfig,
    IntegrationEvent,
    IntegrationObserver,
    IntegrationLogger,
    IntegrationMetrics,
    create_integration_system
)

class TestIntegrationConfig(unittest.TestCase):
    """Tests para la configuración de integración."""
    
    def test_default_config(self):
        """Test configuración por defecto."""
        config = IntegrationConfig()
        
        self.assertTrue(config.enable_optimization)
        self.assertTrue(config.enable_monitoring)
        self.assertTrue(config.enable_config_management)
        self.assertTrue(config.auto_reload_config)
        self.assertEqual(config.log_level, "INFO")
        self.assertEqual(config.metrics_interval, 1.0)
        self.assertEqual(config.optimization_interval, 5.0)
    
    def test_custom_config(self):
        """Test configuración personalizada."""
        config = IntegrationConfig(
            enable_optimization=False,
            enable_monitoring=False,
            log_level="DEBUG",
            metrics_interval=2.0
        )
        
        self.assertFalse(config.enable_optimization)
        self.assertFalse(config.enable_monitoring)
        self.assertEqual(config.log_level, "DEBUG")
        self.assertEqual(config.metrics_interval, 2.0)

class TestIntegrationEvent(unittest.TestCase):
    """Tests para eventos de integración."""
    
    def test_event_creation(self):
        """Test creación de eventos."""
        data = {"test": "data"}
        event = IntegrationEvent("test_event", data)
        
        self.assertEqual(event.event_type, "test_event")
        self.assertEqual(event.data, data)
        self.assertIsNotNone(event.timestamp)
    
    def test_event_string_representation(self):
        """Test representación en string del evento."""
        event = IntegrationEvent("test_event", {"key": "value"})
        event_str = str(event)
        
        self.assertIn("test_event", event_str)
        self.assertIn("key", event_str)
        self.assertIn("value", event_str)

class TestIntegrationObserver(unittest.TestCase):
    """Tests para observadores de integración."""
    
    def test_observer_interface(self):
        """Test que IntegrationObserver es una clase abstracta."""
        with self.assertRaises(TypeError):
            IntegrationObserver()
    
    def test_integration_logger(self):
        """Test logger de integración."""
        logger = IntegrationLogger("INFO")
        self.assertIsNotNone(logger.logger)
        self.assertEqual(logger.logger.level, 20)  # INFO level
    
    def test_integration_metrics(self):
        """Test métricas de integración."""
        metrics = IntegrationMetrics()
        
        # Verificar estado inicial
        initial_metrics = metrics.get_metrics()
        self.assertEqual(initial_metrics['total_events'], 0)
        self.assertIsNone(initial_metrics['latest_event'])

class TestModularIntegrationSystem(unittest.TestCase):
    """Tests para el sistema principal de integración."""
    
    def setUp(self):
        """Configurar test."""
        self.config = IntegrationConfig(
            enable_optimization=True,
            enable_monitoring=True,
            enable_config_management=True
        )
        self.system = ModularIntegrationSystem(self.config)
    
    def test_system_initialization(self):
        """Test inicialización del sistema."""
        self.assertIsNotNone(self.system.optimizer)
        self.assertIsNotNone(self.system.monitoring)
        self.assertIsNotNone(self.system.config_manager)
        self.assertFalse(self.system.running)
        self.assertEqual(len(self.system.observers), 2)  # Logger + Metrics
    
    def test_add_observer(self):
        """Test agregar observador."""
        initial_count = len(self.system.observers)
        
        mock_observer = Mock(spec=IntegrationObserver)
        self.system.add_observer(mock_observer)
        
        self.assertEqual(len(self.system.observers), initial_count + 1)
        self.assertIn(mock_observer, self.system.observers)
    
    def test_get_system_status(self):
        """Test obtener estado del sistema."""
        status = self.system.get_system_status()
        
        self.assertFalse(status['running'])
        self.assertTrue(status['components']['optimizer'])
        self.assertTrue(status['components']['monitoring'])
        self.assertTrue(status['components']['config_manager'])
        self.assertEqual(status['observers_count'], 2)
    
    @patch('modular_integration_system.asyncio.create_task')
    @patch('modular_integration_system.asyncio.Queue')
    async def test_system_start(self, mock_queue, mock_create_task):
        """Test iniciar sistema."""
        mock_queue_instance = Mock()
        mock_queue.return_value = mock_queue_instance
        
        await self.system.start()
        
        self.assertTrue(self.system.running)
        mock_create_task.assert_called()
    
    @patch('modular_integration_system.asyncio.Queue')
    async def test_system_stop(self, mock_queue):
        """Test detener sistema."""
        mock_queue_instance = Mock()
        mock_queue.return_value = mock_queue_instance
        
        # Iniciar sistema primero
        await self.system.start()
        self.assertTrue(self.system.running)
        
        # Detener sistema
        await self.system.stop()
        self.assertFalse(self.system.running)

class TestIntegrationSystemAsync(unittest.IsolatedAsyncioTestCase):
    """Tests asíncronos para el sistema de integración."""
    
    async def asyncSetUp(self):
        """Configurar test asíncrono."""
        self.config = IntegrationConfig(
            enable_optimization=True,
            enable_monitoring=True,
            enable_config_management=True
        )
        self.system = ModularIntegrationSystem(self.config)
    
    async def test_emit_event(self):
        """Test emitir evento."""
        event_type = "test_event"
        data = {"test": "data"}
        
        await self.system.emit_event(event_type, data)
        
        # Verificar que el evento se agregó a la cola
        self.assertEqual(self.system.event_queue.qsize(), 1)
    
    async def test_apply_optimization(self):
        """Test aplicar optimización manual."""
        context = {"memory_pressure": 0.9, "computation_load": 0.8}
        
        # Mock del optimizador
        mock_result = {"optimization": "applied"}
        self.system.optimizer.optimize = Mock(return_value=mock_result)
        
        result = await self.system.apply_optimization(context)
        
        self.assertEqual(result, mock_result)
        self.system.optimizer.optimize.assert_called_once_with(context)
    
    async def test_apply_optimization_no_optimizer(self):
        """Test aplicar optimización sin optimizador disponible."""
        self.system.optimizer = None
        
        with self.assertRaises(RuntimeError):
            await self.system.apply_optimization({})
    
    async def test_get_system_context(self):
        """Test obtener contexto del sistema."""
        context = await self.system._get_system_context()
        
        self.assertIn('timestamp', context)
        self.assertIn('system_status', context)
        self.assertIn('memory_usage', context)
        self.assertIn('cpu_usage', context)
        self.assertIn('gpu_usage', context)
        self.assertIn('needs_optimization', context)
    
    async def test_get_system_metrics(self):
        """Test obtener métricas del sistema."""
        metrics = await self.system.get_system_metrics()
        
        self.assertIn('timestamp', metrics)
        self.assertIn('system_status', metrics)
        self.assertIn('IntegrationMetrics_metrics', metrics)

class TestIntegrationSystemCreation(unittest.IsolatedAsyncioTestCase):
    """Tests para creación del sistema de integración."""
    
    async def test_create_integration_system_default(self):
        """Test crear sistema con configuración por defecto."""
        system = await create_integration_system()
        
        self.assertIsInstance(system, ModularIntegrationSystem)
        self.assertTrue(system.config.enable_optimization)
        self.assertTrue(system.config.enable_monitoring)
    
    async def test_create_integration_system_from_yaml(self):
        """Test crear sistema desde archivo YAML."""
        # Crear archivo YAML temporal
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml_content = """
enable_optimization: false
enable_monitoring: false
log_level: DEBUG
metrics_interval: 2.0
"""
            f.write(yaml_content)
            yaml_file = f.name
        
        try:
            system = await create_integration_system(yaml_file)
            
            self.assertFalse(system.config.enable_optimization)
            self.assertFalse(system.config.enable_monitoring)
            self.assertEqual(system.config.log_level, "DEBUG")
            self.assertEqual(system.config.metrics_interval, 2.0)
        
        finally:
            # Limpiar archivo temporal
            Path(yaml_file).unlink()
    
    async def test_create_integration_system_from_json(self):
        """Test crear sistema desde archivo JSON."""
        # Crear archivo JSON temporal
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json_content = {
                "enable_optimization": False,
                "enable_monitoring": False,
                "log_level": "WARNING",
                "optimization_interval": 10.0
            }
            json.dump(json_content, f)
            json_file = f.name
        
        try:
            system = await create_integration_system(json_file)
            
            self.assertFalse(system.config.enable_optimization)
            self.assertFalse(system.config.enable_monitoring)
            self.assertEqual(system.config.log_level, "WARNING")
            self.assertEqual(system.config.optimization_interval, 10.0)
        
        finally:
            # Limpiar archivo temporal
            Path(json_file).unlink()
    
    async def test_create_integration_system_invalid_file(self):
        """Test crear sistema con archivo inválido."""
        system = await create_integration_system("nonexistent_file.yaml")
        
        # Debería usar configuración por defecto
        self.assertTrue(system.config.enable_optimization)
        self.assertTrue(system.config.enable_monitoring)

class TestIntegrationDemo(unittest.IsolatedAsyncioTestCase):
    """Tests para la demostración del sistema."""
    
    @patch('modular_integration_system.logging')
    async def test_run_integration_demo(self, mock_logging):
        """Test ejecutar demostración del sistema."""
        from modular_integration_system import run_integration_demo
        
        # Mock del logger
        mock_logger = Mock()
        mock_logging.getLogger.return_value = mock_logger
        
        # Ejecutar demostración
        await run_integration_demo()
        
        # Verificar que se llamaron los métodos del logger
        mock_logger.info.assert_called()

def run_integration_tests():
    """Ejecutar todos los tests de integración."""
    print("🧪 Ejecutando Test Suite de Integración Modular...")
    print("=" * 60)
    
    # Crear test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Agregar tests
    test_classes = [
        TestIntegrationConfig,
        TestIntegrationEvent,
        TestIntegrationObserver,
        TestModularIntegrationSystem,
        TestIntegrationSystemAsync,
        TestIntegrationSystemCreation,
        TestIntegrationDemo
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Mostrar resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE TESTS DE INTEGRACIÓN")
    print("=" * 60)
    print(f"Tests ejecutados: {result.testsRun}")
    print(f"Fallos: {len(result.failures)}")
    print(f"Errores: {len(result.errors)}")
    print(f"Exitosos: {result.testsRun - len(result.failures) - len(result.errors)}")
    
    if result.failures:
        print("\n❌ TESTS FALLIDOS:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n🚨 TESTS CON ERRORES:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n✅ TODOS LOS TESTS DE INTEGRACIÓN PASARON EXITOSAMENTE!")
    else:
        print("\n❌ ALGUNOS TESTS DE INTEGRACIÓN FALLARON")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    # Ejecutar tests
    success = run_integration_tests()
    
    # Código de salida
    exit(0 if success else 1)
