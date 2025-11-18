"""
Tests for the Kubernetes Deployment Manager.

This module contains unit tests for the DeploymentManager class in deployment_manager.py.
"""

import unittest
from unittest.mock import patch, MagicMock
from kubernetes.client.rest import ApiException
from deployment_manager import DeploymentManager, DeploymentConfig, DeploymentStatus

class TestDeploymentManager(unittest.TestCase):
    """Test cases for DeploymentManager class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.deployment_config = DeploymentConfig(
            name="test-deployment",
            namespace="default",
            replicas=2,
            image="nginx",
            image_tag="latest",
            ports=[80],
            environment_vars={"ENV": "test"},
            resource_limits={"cpu": "500m", "memory": "512Mi"},
            resource_requests={"cpu": "200m", "memory": "256Mi"},
            health_check_path="/healthz",
            auto_scaling=True,
            min_replicas=1,
            max_replicas=5,
            target_cpu_utilization=70
        )
        
        # Patch the Kubernetes client
        self.patcher = patch('kubernetes.config.load_kube_config')
        self.mock_load_kube_config = self.patcher.start()
        
        # Create a mock for the Kubernetes API clients
        self.mock_apps_v1 = MagicMock()
        self.mock_core_v1 = MagicMock()
        self.mock_autoscaling_v1 = MagicMock()
        
        # Patch the client classes to return our mocks
        with patch('kubernetes.client.AppsV1Api', return_value=self.mock_apps_v1), \
             patch('kubernetes.client.CoreV1Api', return_value=self.mock_core_v1), \
             patch('kubernetes.client.AutoscalingV1Api', return_value=self.mock_autoscaling_v1):
            self.manager = DeploymentManager()
    
    def tearDown(self):
        """Clean up after each test method."""
        self.patcher.stop()
    
    def test_initialization(self):
        """Test that the DeploymentManager initializes correctly."""
        self.mock_load_kube_config.assert_called_once()
        self.assertIsNotNone(self.manager.apps_v1)
        self.assertIsNotNone(self.manager.core_v1)
        self.assertIsNotNone(self.manager.autoscaling_v1)
    
    @patch('deployment_manager.DeploymentManager._create_deployment_object')
    @patch('deployment_manager.DeploymentManager._create_service_object')
    @patch('deployment_manager.DeploymentManager._create_hpa_object')
    def test_create_deployment_success(self, mock_create_hpa, mock_create_service, mock_create_deployment):
        """Test successful deployment creation."""
        # Setup mocks
        mock_deployment = MagicMock()
        mock_create_deployment.return_value = mock_deployment
        
        mock_service = MagicMock()
        mock_create_service.return_value = mock_service
        
        mock_hpa = MagicMock()
        mock_create_hpa.return_value = mock_hpa
        
        # Call the method
        result = self.manager.create_deployment(self.deployment_config)
        
        # Assertions
        self.assertTrue(result)
        self.mock_apps_v1.create_namespaced_deployment.assert_called_once()
        self.mock_core_v1.create_namespaced_service.assert_called_once()
        self.mock_autoscaling_v1.create_namespaced_horizontal_pod_autoscaler.assert_called_once()
    
    @patch('deployment_manager.DeploymentManager._create_deployment_object')
    def test_create_deployment_failure(self, mock_create_deployment):
        """Test deployment creation failure."""
        # Setup mock to raise an exception
        self.mock_apps_v1.create_namespaced_deployment.side_effect = ApiException(status=500)
        
        # Call the method and assert it returns False on failure
        result = self.manager.create_deployment(self.deployment_config)
        self.assertFalse(result)
    
    def test_get_deployment_status(self):
        """Test getting deployment status."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status.ready_replicas = 2
        mock_response.status.replicas = 2
        mock_response.status.available_replicas = 2
        mock_response.status.conditions = [
            MagicMock(type='Available', status='True'),
            MagicMock(type='Progressing', status='True')
        ]
        
        self.mock_apps_v1.read_namespaced_deployment_status.return_value = mock_response
        
        # Call the method
        status = self.manager.get_deployment_status("test-deployment", "default")
        
        # Assertions
        self.assertEqual(status, DeploymentStatus.RUNNING)
        self.mock_apps_v1.read_namespaced_deployment_status.assert_called_once_with(
            name="test-deployment",
            namespace="default"
        )
    
    def test_scale_deployment(self):
        """Test scaling a deployment."""
        # Call the method
        result = self.manager.scale_deployment("test-deployment", "default", 3)
        
        # Assertions
        self.assertTrue(result)
        self.mock_apps_v1.patch_namespaced_deployment_scale.assert_called_once()
    
    def test_delete_deployment(self):
        """Test deleting a deployment."""
        # Call the method
        result = self.manager.delete_deployment("test-deployment", "default")
        
        # Assertions
        self.assertTrue(result)
        self.mock_apps_v1.delete_namespaced_deployment.assert_called_once_with(
            name="test-deployment",
            namespace="default",
            body={
                'apiVersion': 'apps/v1',
                'kind': 'DeleteOptions',
                'propagation_policy': 'Foreground'
            }
        )


if __name__ == '__main__':
    unittest.main()
