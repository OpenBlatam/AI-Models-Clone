#!/bin/bash

###############################################################################
# GitHub Webhook Listener for Auto-Deployment
# This script sets up a simple webhook listener that triggers deployments
# when GitHub sends a webhook event on push to main branch
###############################################################################

set -euo pipefail

PROJECT_NAME="${PROJECT_NAME:-blatam-academy}"
WEBHOOK_PORT="${WEBHOOK_PORT:-9000}"
WEBHOOK_SECRET="${WEBHOOK_SECRET:-}"
DEPLOY_SCRIPT="/opt/${PROJECT_NAME}/aws/scripts/auto_deploy.sh"
LOG_FILE="/var/log/${PROJECT_NAME}-webhook.log"

log() {
    local message="$@"
    local timestamp=$(date +'%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] ${message}" | tee -a "${LOG_FILE}"
}

# Check if Python is available
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    log "ERROR: Python is not installed. Cannot run webhook listener."
    exit 1
fi

# Create webhook listener script
cat > /tmp/webhook_listener.py << 'PYTHON_SCRIPT'
#!/usr/bin/env python3
"""
Simple GitHub Webhook Listener for Auto-Deployment
Listens for push events and triggers deployment script
"""

import http.server
import json
import hmac
import hashlib
import subprocess
import logging
import os
from urllib.parse import urlparse, parse_qs

# Configuration
WEBHOOK_PORT = int(os.environ.get('WEBHOOK_PORT', '9000'))
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', '')
DEPLOY_SCRIPT = os.environ.get('DEPLOY_SCRIPT', '/opt/blatam-academy/aws/scripts/auto_deploy.sh')
PROJECT_NAME = os.environ.get('PROJECT_NAME', 'blatam-academy')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'/var/log/{PROJECT_NAME}-webhook.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WebhookHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info("%s - - [%s] %s" % (self.address_string(), self.log_date_time_string(), format % args))

    def do_GET(self):
        """Handle GET requests (health check)"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = json.dumps({
            'status': 'ok',
            'service': 'webhook-listener',
            'project': PROJECT_NAME
        })
        self.wfile.write(response.encode())

    def do_POST(self):
        """Handle POST requests (webhook events)"""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            # Verify webhook secret if provided
            if WEBHOOK_SECRET:
                signature = self.headers.get('X-Hub-Signature-256', '')
                if not self.verify_signature(body, signature):
                    logger.warning("Invalid webhook signature")
                    self.send_response(401)
                    self.end_headers()
                    return
            
            # Parse JSON payload
            try:
                payload = json.loads(body.decode('utf-8'))
            except json.JSONDecodeError:
                logger.error("Invalid JSON payload")
                self.send_response(400)
                self.end_headers()
                return
            
            # Check if this is a push event to main branch
            ref = payload.get('ref', '')
            if ref == 'refs/heads/main' or ref.endswith('/main'):
                logger.info(f"Push event detected to main branch. Commit: {payload.get('head_commit', {}).get('id', 'unknown')}")
                
                # Trigger deployment
                self.trigger_deployment()
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = json.dumps({'status': 'deployment_triggered'})
                self.wfile.write(response.encode())
            else:
                logger.info(f"Ignoring push event to branch: {ref}")
                self.send_response(200)
                self.end_headers()
                
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            self.send_response(500)
            self.end_headers()

    def verify_signature(self, payload, signature):
        """Verify GitHub webhook signature"""
        if not signature:
            return False
        
        # Remove 'sha256=' prefix if present
        if signature.startswith('sha256='):
            signature = signature[7:]
        
        # Calculate expected signature
        expected_signature = hmac.new(
            WEBHOOK_SECRET.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)

    def trigger_deployment(self):
        """Trigger deployment script"""
        logger.info("Triggering deployment...")
        try:
            # Run deployment script in background
            subprocess.Popen(
                ['/bin/bash', DEPLOY_SCRIPT, 'deploy'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            logger.info("Deployment script started")
        except Exception as e:
            logger.error(f"Failed to trigger deployment: {str(e)}")


def run_server():
    """Start the webhook server"""
    server_address = ('', WEBHOOK_PORT)
    httpd = http.server.HTTPServer(server_address, WebhookHandler)
    logger.info(f"Webhook listener started on port {WEBHOOK_PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Webhook listener stopped")
        httpd.shutdown()


if __name__ == '__main__':
    run_server()
PYTHON_SCRIPT

# Make script executable
chmod +x /tmp/webhook_listener.py

# Install required Python packages if needed
${PYTHON_CMD} -c "import hmac" 2>/dev/null || {
    log "Installing required Python packages..."
    ${PYTHON_CMD} -m pip install --quiet --upgrade pip || true
}

# Start webhook listener
log "Starting webhook listener on port ${WEBHOOK_PORT}..."
exec ${PYTHON_CMD} /tmp/webhook_listener.py



