#!/usr/bin/env python3
"""
GitHub Webhook Listener for Auto-Deployment
Listens for GitHub webhook events and triggers deployment on EC2

This service provides a secure HTTP endpoint that receives GitHub webhooks
and automatically triggers deployments when changes are pushed to the main branch.
"""

import os
import sys
import json
import hmac
import hashlib
import logging
from typing import Tuple, Dict, Any, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

# Import local modules
try:
    from config import DeploymentConfig
    from utils import run_command
except ImportError:
    # Fallback if modules not available
    DeploymentConfig = None
    run_command = None


###############################################################################
# Security & Validation
###############################################################################

class SecurityManager:
    """Handles security operations including signature verification"""
    
    def __init__(self, secret: Optional[str]):
        self.secret = secret or ''
    
    def verify_signature(self, payload_body: str, signature_header: str) -> bool:
        """
        Verify GitHub webhook signature using HMAC SHA256
        
        Args:
            payload_body: Raw request body as string
            signature_header: X-Hub-Signature-256 header value
            
        Returns:
            True if signature is valid, False otherwise
        """
        if not self.secret:
            logger.warning("No webhook secret configured, skipping signature verification")
            return True  # Skip verification if no secret configured
        
        if not signature_header:
            logger.error("No signature header provided")
            return False
        
        # Remove 'sha256=' prefix if present
        if signature_header.startswith('sha256='):
            signature_header = signature_header[7:]
        
        # Calculate expected signature
        hash_object = hmac.new(
            self.secret.encode('utf-8'),
            msg=payload_body.encode('utf-8'),
            digestmod=hashlib.sha256
        )
        expected_signature = hash_object.hexdigest()
        
        # Compare signatures using constant-time comparison
        return hmac.compare_digest(expected_signature, signature_header)


###############################################################################
# Deployment Management
###############################################################################

class DeploymentManager:
    """Manages deployment operations"""
    
    def __init__(self, config: DeploymentConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.DeploymentManager")
    
    def trigger_deployment(self) -> Tuple[bool, str]:
        """
        Trigger deployment script
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        self.logger.info("Triggering deployment...")
        
        # Prepare environment variables
        env = dict(os.environ, **{
            'GITHUB_BRANCH': self.config.github_branch,
            'PROJECT_DIR': self.config.project_dir,
            'PROJECT_NAME': self.config.project_name
        })
        
        # Run deployment script
        if run_command:
            success, stdout, stderr = run_command(
                ['bash', self.config.deploy_script, 'deploy'],
                cwd=self.config.project_dir,
                timeout=self.config.deployment_timeout,
                env=env
            )
            
            if success:
                self.logger.info("Deployment successful")
                return True, stdout
            else:
                self.logger.error(f"Deployment failed: {stderr}")
                return False, stderr
        else:
            # Fallback to subprocess if utils not available
            import subprocess
            try:
                result = subprocess.run(
                    ['bash', self.config.deploy_script, 'deploy'],
                    cwd=self.config.project_dir,
                    capture_output=True,
                    text=True,
                    timeout=self.config.deployment_timeout,
                    env=env
                )
                
                if result.returncode == 0:
                    self.logger.info("Deployment successful")
                    return True, result.stdout
                else:
                    self.logger.error(f"Deployment failed: {result.stderr}")
                    return False, result.stderr
            except subprocess.TimeoutExpired:
                self.logger.error(f"Deployment timed out after {self.config.deployment_timeout} seconds")
                return False, "Deployment timed out"
            except Exception as e:
                self.logger.error(f"Exception during deployment: {str(e)}", exc_info=True)
                return False, str(e)


###############################################################################
# Webhook Handler
###############################################################################

class WebhookHandler(BaseHTTPRequestHandler):
    """HTTP request handler for GitHub webhooks"""
    
    def __init__(self, *args, security_manager: SecurityManager, 
                 deployment_manager: DeploymentManager, **kwargs):
        self.security_manager = security_manager
        self.deployment_manager = deployment_manager
        super().__init__(*args, **kwargs)
    
    def _send_json_response(self, status_code: int, data: Dict[str, Any]) -> None:
        """Helper method to send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(json.dumps(data))))
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def _handle_push_event(self, payload: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Handle push event and check if deployment should be triggered"""
        ref = payload.get('ref', '')
        target_ref = f'refs/heads/{self.config.github_branch}'
        
        if ref == target_ref or (ref.endswith(f'/{self.config.github_branch}')):
            logger.info(f"Push to {self.config.github_branch} branch detected, triggering deployment...")
            
            # Trigger deployment
            success, message = self.deployment_manager.trigger_deployment()
            
            if success:
                return True, {
                    'status': 'success',
                    'message': 'Deployment triggered successfully',
                    'output': message[:1000] if message else ''  # Limit output size
                }
            else:
                return False, {
                    'status': 'error',
                    'message': 'Deployment failed',
                    'error': message[:1000] if message else 'Unknown error'  # Limit error size
                }
        else:
            logger.info(f"Ignoring event for ref: {ref}")
            return True, {
                'status': 'ignored',
                'message': f'Event for ref {ref} ignored (only {self.config.github_branch} branch triggers deployment)'
            }
    
    def do_POST(self) -> None:
        """Handle POST requests (webhook events)"""
        try:
            # Read payload
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self._send_json_response(400, {'error': 'Empty payload'})
                return
            
            payload_body = self.rfile.read(content_length).decode('utf-8')
            
            # Get signature header
            signature = (
                self.headers.get('X-Hub-Signature-256', '') or 
                self.headers.get('X-Hub-Signature', '')
            )
            
            # Verify signature
            if not self.security_manager.verify_signature(payload_body, signature):
                logger.error("Invalid webhook signature")
                self._send_json_response(401, {'error': 'Invalid signature'})
                return
            
            # Parse payload
            try:
                payload = json.loads(payload_body)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON payload: {e}")
                self._send_json_response(400, {'error': 'Invalid JSON payload'})
                return
            
            # Get event type
            event_type = self.headers.get('X-GitHub-Event', '')
            logger.info(f"Received {event_type} event")
            
            # Handle push events
            if event_type == 'push':
                success, response_data = self._handle_push_event(payload)
                status_code = 200 if success else 500
                self._send_json_response(status_code, response_data)
            else:
                logger.info(f"Ignoring {event_type} event (only push events are handled)")
                self._send_json_response(200, {
                    'status': 'ignored',
                    'message': f'{event_type} events are not handled'
                })
                
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
            self._send_json_response(500, {'error': str(e)})
    
    def do_GET(self) -> None:
        """Handle GET requests (health check)"""
        self._send_json_response(200, {
            'status': 'ok',
            'service': 'github-webhook-listener',
            'timestamp': datetime.now().isoformat(),
            'project_dir': config.project_dir,
            'deploy_script': config.deploy_script,
            'target_branch': config.target_branch
        })
    
    def log_message(self, format: str, *args) -> None:
        """Override to use custom logging"""
        logger.info(f"{self.address_string()} - {format % args}")


###############################################################################
# Server Factory
###############################################################################

def create_webhook_handler(security_manager: SecurityManager, 
                          deployment_manager: DeploymentManager,
                          config: 'DeploymentConfig'):
    """Factory function to create webhook handler with dependencies"""
    def handler(*args, **kwargs):
        return WebhookHandler(
            *args,
            security_manager=security_manager,
            deployment_manager=deployment_manager,
            config=config,
            **kwargs
        )
    return handler


###############################################################################
# Logging Setup
###############################################################################

def setup_logging(log_file: str) -> None:
    """Configure logging"""
    from pathlib import Path
    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )


###############################################################################
# Main Application
###############################################################################

def main() -> None:
    """Main function to start the webhook listener server"""
    global config, logger
    
    # Initialize configuration
    try:
        config = Config()
    except FileNotFoundError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Setup logging
    setup_logging(config)
    logger = logging.getLogger(__name__)
    
    # Initialize managers
    security_manager = SecurityManager(config.webhook_secret)
    deployment_manager = DeploymentManager(config)
    
    # Create handler factory
    handler_factory = create_webhook_handler(security_manager, deployment_manager)
    
    # Start server
    server = HTTPServer(('0.0.0.0', config.webhook_port), handler_factory)
    
    logger.info("=" * 60)
    logger.info("Starting GitHub webhook listener")
    logger.info(f"Port: {config.webhook_port}")
    logger.info(f"Project directory: {config.project_dir}")
    logger.info(f"Deploy script: {config.deploy_script}")
    logger.info(f"Target branch: {config.target_branch}")
    logger.info(f"Webhook secret configured: {'Yes' if config.is_secret_configured() else 'No'}")
    logger.info("=" * 60)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Stopping webhook listener...")
        server.shutdown()
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
