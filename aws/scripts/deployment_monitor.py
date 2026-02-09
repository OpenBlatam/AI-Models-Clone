#!/usr/bin/env python3
"""
Deployment Monitor Service
Monitors deployment status and provides metrics/status endpoints
"""

import os
import json
import time
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler


logger = logging.getLogger(__name__)


class DeploymentMonitor:
    """Monitors deployment status and history"""
    
    def __init__(self, state_file: str = '/var/lib/deployment-monitor/state.json'):
        self.state_file = Path(state_file)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self._load_state()
    
    def _load_state(self) -> None:
        """Load state from file"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    self.state = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load state: {e}")
                self.state = {
                    'deployments': [],
                    'last_deployment': None,
                    'stats': {
                        'total': 0,
                        'successful': 0,
                        'failed': 0
                    }
                }
        else:
            self.state = {
                'deployments': [],
                'last_deployment': None,
                'stats': {
                    'total': 0,
                    'successful': 0,
                    'failed': 0
                }
            }
    
    def _save_state(self) -> None:
        """Save state to file"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
    
    def record_deployment(self, success: bool, message: str = '', commit_hash: str = '') -> None:
        """Record a deployment attempt"""
        deployment = {
            'timestamp': datetime.now().isoformat(),
            'success': success,
            'message': message[:500],  # Limit message size
            'commit_hash': commit_hash[:40],
            'duration': None  # Can be set if available
        }
        
        self.state['deployments'].append(deployment)
        self.state['last_deployment'] = deployment
        self.state['stats']['total'] += 1
        
        if success:
            self.state['stats']['successful'] += 1
        else:
            self.state['stats']['failed'] += 1
        
        # Keep only last 100 deployments
        if len(self.state['deployments']) > 100:
            self.state['deployments'] = self.state['deployments'][-100:]
        
        self._save_state()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current deployment status"""
        return {
            'last_deployment': self.state['last_deployment'],
            'stats': self.state['stats'],
            'recent_deployments': self.state['deployments'][-10:],  # Last 10
            'uptime': self._get_uptime()
        }
    
    def _get_uptime(self) -> Optional[str]:
        """Get system uptime"""
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.read().split()[0])
                return str(timedelta(seconds=int(uptime_seconds)))
        except:
            return None


class MonitorHandler(BaseHTTPRequestHandler):
    """HTTP handler for deployment monitor"""
    
    def __init__(self, *args, monitor: DeploymentMonitor, **kwargs):
        self.monitor = monitor
        super().__init__(*args, **kwargs)
    
    def _send_json_response(self, status_code: int, data: Dict[str, Any]) -> None:
        """Helper method to send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        response = json.dumps(data)
        self.send_header('Content-Length', str(len(response)))
        self.end_headers()
        self.wfile.write(response.encode('utf-8'))
    
    def do_GET(self) -> None:
        """Handle GET requests"""
        if self.path == '/status' or self.path == '/':
            status = self.monitor.get_status()
            self._send_json_response(200, status)
        elif self.path == '/health':
            self._send_json_response(200, {'status': 'ok'})
        else:
            self._send_json_response(404, {'error': 'Not found'})
    
    def log_message(self, format: str, *args) -> None:
        """Override to use custom logging"""
        logger.info(f"{self.address_string()} - {format % args}")


def create_monitor_handler(monitor: DeploymentMonitor):
    """Factory function to create monitor handler"""
    def handler(*args, **kwargs):
        return MonitorHandler(*args, monitor=monitor, **kwargs)
    return handler


def main():
    """Main function"""
    monitor = DeploymentMonitor()
    
    port = int(os.environ.get('MONITOR_PORT', 9001))
    handler_factory = create_monitor_handler(monitor)
    server = HTTPServer(('0.0.0.0', port), handler_factory)
    
    logger.info(f"Starting deployment monitor on port {port}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Stopping deployment monitor...")
        server.shutdown()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s'
    )
    main()
