import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock
import subprocess
import json
import tempfile
import shutil
from pathlib import Path
from expo_managed_workflow import (
    ExpoManagedWorkflow,
    ExpoDevelopmentWorkflow,
    ExpoDeploymentWorkflow,
    ExpoConfig
)

class TestExpoConfig(unittest.TestCase):
    def setUp(self):
        self.config_data = {
            "expo": {
                "name": "TestApp",
                "slug": "test-app",
                "version": "1.0.0",
                "platforms": ["ios", "android"],
                "icon": "./assets/icon.png",
                "splash": {
                    "image": "./assets/splash.png",
                    "resizeMode": "contain",
                    "backgroundColor": "#ffffff"
                },
                "updates": {
                    "enabled": True,
                    "fallbackToCacheTimeout": 0
                },
                "runtimeVersion": "1.0.0",
                "jsEngine": "hermes"
            }
        }
    
    def test_config_creation(self):
        """Test ExpoConfig creation from dictionary."""
        config = ExpoConfig(
            name="TestApp",
            slug="test-app",
            version="1.0.0",
            platform=["ios", "android"],
            icon="./assets/icon.png",
            splash={},
            updates={},
            runtime_version="1.0.0"
        )
        
        self.assertEqual(config.name, "TestApp")
        self.assertEqual(config.slug, "test-app")
        self.assertEqual(config.version, "1.0.0")
        self.assertEqual(config.platform, ["ios", "android"])
        self.assertEqual(config.js_engine, "hermes")

class TestExpoManagedWorkflow(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir) / "test-project"
        self.project_path.mkdir()
        
        # Create mock app.json
        self.app_json = {
            "expo": {
                "name": "TestApp",
                "slug": "test-app",
                "version": "1.0.0",
                "platforms": ["ios", "android"],
                "icon": "./assets/icon.png",
                "splash": {},
                "updates": {},
                "runtimeVersion": "1.0.0"
            }
        }
        
        with open(self.project_path / "app.json", 'w') as f:
            json.dump(self.app_json, f)
        
        self.workflow = ExpoManagedWorkflow(str(self.project_path))
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_load_config(self):
        """Test loading configuration from app.json."""
        config = self.workflow.config
        
        self.assertEqual(config.name, "TestApp")
        self.assertEqual(config.slug, "test-app")
        self.assertEqual(config.version, "1.0.0")
        self.assertEqual(config.platform, ["ios", "android"])
    
    def test_load_config_file_not_found(self):
        """Test handling of missing app.json."""
        shutil.rmtree(self.project_path)
        
        with self.assertRaises(FileNotFoundError):
            ExpoManagedWorkflow(str(self.project_path))
    
    @patch('subprocess.run')
    def test_initialize_project_success(self, mock_run):
        """Test successful project initialization."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Project created successfully"
        
        result = self.workflow.initialize_project("test-app", "blank")
        
        self.assertTrue(result)
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_initialize_project_failure(self, mock_run):
        """Test failed project initialization."""
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Error creating project"
        
        result = self.workflow.initialize_project("test-app", "blank")
        
        self.assertFalse(result)
    
    @patch('subprocess.run')
    def test_install_dependencies_success(self, mock_run):
        """Test successful dependency installation."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Dependencies installed"
        
        dependencies = ["expo", "react-native"]
        result = self.workflow.install_dependencies(dependencies)
        
        self.assertTrue(result)
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_install_dependencies_failure(self, mock_run):
        """Test failed dependency installation."""
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Installation failed"
        
        dependencies = ["invalid-package"]
        result = self.workflow.install_dependencies(dependencies)
        
        self.assertFalse(result)
    
    @patch('subprocess.Popen')
    def test_start_development_server_success(self, mock_popen):
        """Test successful development server start."""
        mock_process = Mock()
        mock_popen.return_value = mock_process
        
        result = self.workflow.start_development_server(8081)
        
        self.assertTrue(result)
        mock_popen.assert_called_once()
    
    @patch('subprocess.run')
    def test_build_development_build_ios_success(self, mock_run):
        """Test successful iOS development build."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Build completed"
        
        result = self.workflow.build_development_build("ios")
        
        self.assertTrue(result)
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_build_development_build_android_success(self, mock_run):
        """Test successful Android development build."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Build completed"
        
        result = self.workflow.build_development_build("android")
        
        self.assertTrue(result)
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_create_eas_build_success(self, mock_run):
        """Test successful EAS build creation."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Build created"
        
        result = self.workflow.create_eas_build("ios", "development")
        
        self.assertTrue(result)
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_submit_to_store_success(self, mock_run):
        """Test successful app store submission."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Submitted successfully"
        
        result = self.workflow.submit_to_store("ios", "production")
        
        self.assertTrue(result)
        mock_run.assert_called_once()
    
    def test_configure_updates_success(self):
        """Test successful updates configuration."""
        with patch.object(self.workflow, 'install_dependencies') as mock_install:
            mock_install.return_value = True
            
            result = self.workflow.configure_updates("default")
            
            self.assertTrue(result)
            mock_install.assert_called_once_with(["expo-updates"])
    
    @patch('subprocess.run')
    def test_publish_update_success(self, mock_run):
        """Test successful update publishing."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Update published"
        
        result = self.workflow.publish_update("Bug fixes")
        
        self.assertTrue(result)
        mock_run.assert_called_once()
    
    def test_configure_notifications_success(self):
        """Test successful notifications configuration."""
        with patch.object(self.workflow, 'install_dependencies') as mock_install:
            mock_install.return_value = True
            
            result = self.workflow.configure_notifications()
            
            self.assertTrue(result)
            mock_install.assert_called_once_with(["expo-notifications"])
    
    def test_configure_analytics_success(self):
        """Test successful analytics configuration."""
        with patch.object(self.workflow, 'install_dependencies') as mock_install:
            mock_install.return_value = True
            
            result = self.workflow.configure_analytics()
            
            self.assertTrue(result)
            mock_install.assert_called_once_with(["expo-analytics"])
    
    @patch('subprocess.run')
    def test_configure_eas_success(self, mock_run):
        """Test successful EAS configuration."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "EAS initialized"
        
        result = self.workflow.configure_eas()
        
        self.assertTrue(result)
        mock_run.assert_called_once()
        
        # Check if eas.json was created
        eas_path = self.project_path / "eas.json"
        self.assertTrue(eas_path.exists())

class TestExpoDevelopmentWorkflow(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir) / "test-project"
        self.project_path.mkdir()
        
        # Create mock app.json
        self.app_json = {
            "expo": {
                "name": "TestApp",
                "slug": "test-app",
                "version": "1.0.0",
                "platforms": ["ios", "android"],
                "icon": "./assets/icon.png",
                "splash": {},
                "updates": {},
                "runtimeVersion": "1.0.0"
            }
        }
        
        with open(self.project_path / "app.json", 'w') as f:
            json.dump(self.app_json, f)
        
        self.dev_workflow = ExpoDevelopmentWorkflow(str(self.project_path))
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_setup_development_environment_success(self):
        """Test successful development environment setup."""
        with patch.object(self.dev_workflow.expo_manager, 'install_dependencies') as mock_install, \
             patch.object(self.dev_workflow.expo_manager, 'configure_eas') as mock_eas, \
             patch.object(self.dev_workflow.expo_manager, 'configure_updates') as mock_updates, \
             patch.object(self.dev_workflow.expo_manager, 'configure_notifications') as mock_notifications, \
             patch.object(self.dev_workflow.expo_manager, 'configure_analytics') as mock_analytics:
            
            mock_install.return_value = True
            mock_eas.return_value = True
            mock_updates.return_value = True
            mock_notifications.return_value = True
            mock_analytics.return_value = True
            
            result = self.dev_workflow.setup_development_environment()
            
            self.assertTrue(result)
    
    def test_start_development_success(self):
        """Test successful development start."""
        with patch.object(self.dev_workflow.expo_manager, 'start_development_server') as mock_start:
            mock_start.return_value = True
            
            result = self.dev_workflow.start_development(8081)
            
            self.assertTrue(result)
            mock_start.assert_called_once_with(8081)
    
    def test_build_and_test_success(self):
        """Test successful build and test."""
        with patch.object(self.dev_workflow.expo_manager, 'build_development_build') as mock_build, \
             patch.object(self.dev_workflow, '_run_tests') as mock_tests:
            
            mock_build.return_value = True
            mock_tests.return_value = True
            
            result = self.dev_workflow.build_and_test("ios")
            
            self.assertTrue(result)
            mock_build.assert_called_once_with("ios")
            mock_tests.assert_called_once()
    
    @patch('subprocess.run')
    def test_run_tests_success(self, mock_run):
        """Test successful test execution."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Tests passed"
        
        result = self.dev_workflow._run_tests()
        
        self.assertTrue(result)
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_run_tests_failure(self, mock_run):
        """Test failed test execution."""
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Tests failed"
        
        result = self.dev_workflow._run_tests()
        
        self.assertFalse(result)

class TestExpoDeploymentWorkflow(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir) / "test-project"
        self.project_path.mkdir()
        
        # Create mock app.json
        self.app_json = {
            "expo": {
                "name": "TestApp",
                "slug": "test-app",
                "version": "1.0.0",
                "platforms": ["ios", "android"],
                "icon": "./assets/icon.png",
                "splash": {},
                "updates": {},
                "runtimeVersion": "1.0.0"
            }
        }
        
        with open(self.project_path / "app.json", 'w') as f:
            json.dump(self.app_json, f)
        
        self.deploy_workflow = ExpoDeploymentWorkflow(str(self.project_path))
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_prepare_production_build_success(self):
        """Test successful production build preparation."""
        with patch.object(self.deploy_workflow, '_update_version') as mock_version, \
             patch.object(self.deploy_workflow.expo_manager, 'create_eas_build') as mock_build:
            
            mock_version.return_value = True
            mock_build.return_value = True
            
            result = self.deploy_workflow.prepare_production_build("ios")
            
            self.assertTrue(result)
            mock_version.assert_called_once()
            mock_build.assert_called_once_with("ios", "production")
    
    def test_deploy_to_store_success(self):
        """Test successful store deployment."""
        with patch.object(self.deploy_workflow.expo_manager, 'submit_to_store') as mock_submit:
            mock_submit.return_value = True
            
            result = self.deploy_workflow.deploy_to_store("ios")
            
            self.assertTrue(result)
            mock_submit.assert_called_once_with("ios", "production")
    
    def test_publish_update_success(self):
        """Test successful update publishing."""
        with patch.object(self.deploy_workflow.expo_manager, 'publish_update') as mock_publish:
            mock_publish.return_value = True
            
            result = self.deploy_workflow.publish_update("Bug fixes")
            
            self.assertTrue(result)
            mock_publish.assert_called_once_with("Bug fixes")
    
    def test_update_version_success(self):
        """Test successful version update."""
        result = self.deploy_workflow._update_version()
        
        self.assertTrue(result)
        
        # Check if version was incremented
        with open(self.project_path / "app.json", 'r') as f:
            updated_config = json.load(f)
        
        self.assertEqual(updated_config['expo']['version'], "1.0.1")

# Integration tests
class TestExpoWorkflowIntegration(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir) / "test-project"
        self.project_path.mkdir()
        
        # Create mock app.json
        self.app_json = {
            "expo": {
                "name": "TestApp",
                "slug": "test-app",
                "version": "1.0.0",
                "platforms": ["ios", "android"],
                "icon": "./assets/icon.png",
                "splash": {},
                "updates": {},
                "runtimeVersion": "1.0.0"
            }
        }
        
        with open(self.project_path / "app.json", 'w') as f:
            json.dump(self.app_json, f)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_complete_workflow_integration(self):
        """Test complete workflow integration."""
        # Initialize workflows
        expo_workflow = ExpoManagedWorkflow(str(self.project_path))
        dev_workflow = ExpoDevelopmentWorkflow(str(self.project_path))
        deploy_workflow = ExpoDeploymentWorkflow(str(self.project_path))
        
        # Test configuration loading
        self.assertEqual(expo_workflow.config.name, "TestApp")
        self.assertEqual(expo_workflow.config.slug, "test-app")
        self.assertEqual(expo_workflow.config.version, "1.0.0")
        
        # Test development setup
        with patch.object(dev_workflow.expo_manager, 'install_dependencies') as mock_install, \
             patch.object(dev_workflow.expo_manager, 'configure_eas') as mock_eas, \
             patch.object(dev_workflow.expo_manager, 'configure_updates') as mock_updates, \
             patch.object(dev_workflow.expo_manager, 'configure_notifications') as mock_notifications, \
             patch.object(dev_workflow.expo_manager, 'configure_analytics') as mock_analytics:
            
            mock_install.return_value = True
            mock_eas.return_value = True
            mock_updates.return_value = True
            mock_notifications.return_value = True
            mock_analytics.return_value = True
            
            result = dev_workflow.setup_development_environment()
            self.assertTrue(result)
        
        # Test deployment preparation
        with patch.object(deploy_workflow, '_update_version') as mock_version, \
             patch.object(deploy_workflow.expo_manager, 'create_eas_build') as mock_build:
            
            mock_version.return_value = True
            mock_build.return_value = True
            
            result = deploy_workflow.prepare_production_build("ios")
            self.assertTrue(result)

# Performance tests
class TestExpoWorkflowPerformance(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir) / "test-project"
        self.project_path.mkdir()
        
        # Create mock app.json
        self.app_json = {
            "expo": {
                "name": "TestApp",
                "slug": "test-app",
                "version": "1.0.0",
                "platforms": ["ios", "android"],
                "icon": "./assets/icon.png",
                "splash": {},
                "updates": {},
                "runtimeVersion": "1.0.0"
            }
        }
        
        with open(self.project_path / "app.json", 'w') as f:
            json.dump(self.app_json, f)
        
        self.workflow = ExpoManagedWorkflow(str(self.project_path))
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_config_loading_performance(self):
        """Test configuration loading performance."""
        import time
        
        start_time = time.time()
        
        for _ in range(100):
            config = self.workflow._load_config()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete within 1 second
        self.assertLess(execution_time, 1.0)
    
    def test_version_update_performance(self):
        """Test version update performance."""
        import time
        
        deploy_workflow = ExpoDeploymentWorkflow(str(self.project_path))
        
        start_time = time.time()
        
        for _ in range(50):
            deploy_workflow._update_version()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete within 0.5 seconds
        self.assertLess(execution_time, 0.5)

# Error handling tests
class TestExpoWorkflowErrorHandling(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir) / "test-project"
        self.project_path.mkdir()
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_missing_app_json_handling(self):
        """Test handling of missing app.json."""
        with self.assertRaises(FileNotFoundError):
            ExpoManagedWorkflow(str(self.project_path))
    
    def test_invalid_json_handling(self):
        """Test handling of invalid JSON in app.json."""
        # Create invalid JSON
        with open(self.project_path / "app.json", 'w') as f:
            f.write("{ invalid json }")
        
        with self.assertRaises(json.JSONDecodeError):
            ExpoManagedWorkflow(str(self.project_path))
    
    def test_missing_expo_config_handling(self):
        """Test handling of missing expo configuration."""
        # Create app.json without expo config
        app_json = {"name": "TestApp"}
        
        with open(self.project_path / "app.json", 'w') as f:
            json.dump(app_json, f)
        
        # Should not raise error, should use defaults
        workflow = ExpoManagedWorkflow(str(self.project_path))
        self.assertIsNotNone(workflow.config)

if __name__ == '__main__':
    unittest.main() 