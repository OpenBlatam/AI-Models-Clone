#!/usr/bin/env python3
"""
Deployment API Server
RESTful API for managing deployments
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime

# Import local modules
try:
    from deployment_monitor import DeploymentMonitor
    from deployment_metrics import DeploymentMetrics
    from backup_manager import BackupManager
    from health_checker import HealthChecker
    from config import DeploymentConfig
except ImportError as e:
    print(f"Warning: Could not import modules: {e}")
    DeploymentMonitor = None
    DeploymentMetrics = None
    BackupManager = None
    HealthChecker = None
    DeploymentConfig = None


logger = logging.getLogger(__name__)


class DeploymentAPIHandler(BaseHTTPRequestHandler):
    """HTTP handler for Deployment API"""
    
    def __init__(self, *args, **kwargs):
        # Initialize services
        self.monitor = DeploymentMonitor() if DeploymentMonitor else None
        self.metrics = DeploymentMetrics() if DeploymentMetrics else None
        self.backup_manager = BackupManager() if BackupManager else None
        self.health_checker = HealthChecker({
            'health_check_url': os.environ.get('HEALTH_CHECK_URL', 'http://localhost:8000/health'),
            'health_check_timeout': 60,
            'project_dir': os.environ.get('PROJECT_DIR', '/opt/blatam-academy')
        }) if HealthChecker else None
        
        super().__init__(*args, **kwargs)
    
    def _send_json_response(self, status_code: int, data: Dict[str, Any]) -> None:
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        response = json.dumps(data, indent=2)
        self.send_header('Content-Length', str(len(response)))
        self.end_headers()
        self.wfile.write(response.encode('utf-8'))
    
    def _parse_path(self) -> tuple[str, Dict[str, str]]:
        """Parse request path and query parameters"""
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        params = {k: v[0] if v else '' for k, v in query.items()}
        return path, params
    
    def do_GET(self) -> None:
        """Handle GET requests"""
        path, params = self._parse_path()
        
        try:
            if path == '/api/status' or path == '/api/':
                self._handle_status()
            elif path == '/api/deployments':
                self._handle_list_deployments(params)
            elif path == '/api/metrics':
                self._handle_metrics()
            elif path == '/api/health':
                self._handle_health_check()
            elif path == '/api/backups':
                self._handle_list_backups()
            elif path.startswith('/api/backup/'):
                backup_name = path.split('/')[-1]
                self._handle_backup_info(backup_name)
            else:
                self._send_json_response(404, {'error': 'Not found'})
        except Exception as e:
            logger.error(f"Error handling GET request: {e}", exc_info=True)
            self._send_json_response(500, {'error': str(e)})
    
    def do_POST(self) -> None:
        """Handle POST requests"""
        path, params = self._parse_path()
        
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
            data = json.loads(body) if body else {}
            
            if path == '/api/deploy':
                self._handle_deploy(data)
            elif path == '/api/backup':
                self._handle_create_backup(data)
            elif path.startswith('/api/restore/'):
                backup_name = path.split('/')[-1]
                self._handle_restore_backup(backup_name, data)
            else:
                self._send_json_response(404, {'error': 'Not found'})
        except json.JSONDecodeError:
            self._send_json_response(400, {'error': 'Invalid JSON'})
        except Exception as e:
            logger.error(f"Error handling POST request: {e}", exc_info=True)
            self._send_json_response(500, {'error': str(e)})
    
    def _handle_status(self) -> None:
        """Handle status endpoint"""
        status = {
            'service': 'deployment-api',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        }
        
        if self.monitor:
            status['monitor'] = self.monitor.get_status()
        
        self._send_json_response(200, status)
    
    def _handle_list_deployments(self, params: Dict[str, str]) -> None:
        """Handle list deployments endpoint"""
        if not self.monitor:
            self._send_json_response(503, {'error': 'Monitor service not available'})
            return
        
        limit = int(params.get('limit', 10))
        status = self.monitor.get_status()
        
        deployments = status.get('recent_deployments', [])[:limit]
        self._send_json_response(200, {
            'deployments': deployments,
            'total': status.get('stats', {}).get('total', 0)
        })
    
    def _handle_metrics(self) -> None:
        """Handle metrics endpoint"""
        if not self.metrics:
            self._send_json_response(503, {'error': 'Metrics service not available'})
            return
        
        summary = self.metrics.get_metrics_summary()
        self._send_json_response(200, summary)
    
    def _handle_health_check(self) -> None:
        """Handle health check endpoint"""
        if not self.health_checker:
            self._send_json_response(503, {'error': 'Health checker not available'})
            return
        
        results = self.health_checker.run_all_checks()
        self._send_json_response(200, results)
    
    def _handle_list_backups(self) -> None:
        """Handle list backups endpoint"""
        if not self.backup_manager:
            self._send_json_response(503, {'error': 'Backup manager not available'})
            return
        
        backups = self.backup_manager.list_backups()
        self._send_json_response(200, {'backups': backups})
    
    def _handle_backup_info(self, backup_name: str) -> None:
        """Handle backup info endpoint"""
        if not self.backup_manager:
            self._send_json_response(503, {'error': 'Backup manager not available'})
            return
        
        info = self.backup_manager.get_backup_info(backup_name)
        if info:
            self._send_json_response(200, info)
        else:
            self._send_json_response(404, {'error': 'Backup not found'})
    
    def _handle_deploy(self, data: Dict[str, Any]) -> None:
        """Handle deploy endpoint"""
        # This would trigger a deployment
        # For now, just return a message
        self._send_json_response(200, {
            'message': 'Deployment triggered',
            'note': 'Use integrated_deployment.py for actual deployment'
        })
    
    def _handle_create_backup(self, data: Dict[str, Any]) -> None:
        """Handle create backup endpoint"""
        if not self.backup_manager:
            self._send_json_response(503, {'error': 'Backup manager not available'})
            return
        
        source_dir = data.get('source_dir', os.environ.get('PROJECT_DIR', '/opt/blatam-academy'))
        backup_name = data.get('name')
        
        backup_path = self.backup_manager.create_backup(source_dir, backup_name)
        if backup_path:
            self._send_json_response(200, {
                'message': 'Backup created',
                'path': backup_path
            })
        else:
            self._send_json_response(500, {'error': 'Failed to create backup'})
    
    def _handle_restore_backup(self, backup_name: str, data: Dict[str, Any]) -> None:
        """Handle restore backup endpoint"""
        if not self.backup_manager:
            self._send_json_response(503, {'error': 'Backup manager not available'})
            return
        
        target_dir = data.get('target_dir', os.environ.get('PROJECT_DIR', '/opt/blatam-academy'))
        
        success = self.backup_manager.restore_backup(backup_name, target_dir)
        if success:
            self._send_json_response(200, {'message': 'Backup restored successfully'})
        else:
            self._send_json_response(500, {'error': 'Failed to restore backup'})
    
    def log_message(self, format: str, *args) -> None:
        """Override to use custom logging"""
        logger.info(f"{self.address_string()} - {format % args}")


def main():
    """Main function"""
    port = int(os.environ.get('API_PORT', 9002))
    server = HTTPServer(('0.0.0.0', port), DeploymentAPIHandler)
    
    logger.info(f"Starting Deployment API on port {port}")
    logger.info(f"API endpoints:")
    logger.info(f"  GET  /api/status - Service status")
    logger.info(f"  GET  /api/deployments - List deployments")
    logger.info(f"  GET  /api/metrics - Get metrics")
    logger.info(f"  GET  /api/health - Health check")
    logger.info(f"  GET  /api/backups - List backups")
    logger.info(f"  POST /api/backup - Create backup")
    logger.info(f"  POST /api/restore/<name> - Restore backup")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Stopping Deployment API...")
        server.shutdown()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s'
    )
    main()
