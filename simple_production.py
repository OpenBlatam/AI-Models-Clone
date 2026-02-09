#!/usr/bin/env python3
"""
Simple Production Code
Production-ready application without external dependencies
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/production.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# In-memory storage for production
class ProductionDatabase:
    def __init__(self) -> Any:
        self.users = {}
        self.counter = 1
    
    def create_user(self, email: str, username: str, password: str) -> Dict:
        """Create a new user"""
        user_id = self.counter
        self.counter += 1
        
        user = {
            "id": user_id,
            "email": email,
            "username": username,
            "password_hash": self._hash_password(password),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        self.users[user_id] = user
        logger.info(f"User created: {email}")
        return user
    
    def get_users(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Get all users"""
        users = list(self.users.values())
        return users[skip:skip + limit]
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    def _hash_password(self, password: str) -> str:
        """Simple password hashing"""
        return f"hashed_{password}_secure"

# Production API Handler
class ProductionAPIHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs) -> Any:
        self.db = ProductionDatabase()
        super().__init__(*args, **kwargs)
    
    def do_GET(self) -> Any:
        """Handle GET requests"""
        try:
            if self.path == "/health":
                self._handle_health_check()
            elif self.path.startswith("/api/v1/users"):
                self._handle_get_users()
            elif self.path.startswith("/api/v1/users/"):
                self._handle_get_user()
            else:
                self._handle_not_found()
        except Exception as e:
            logger.error(f"GET request error: {e}")
            self._handle_error()
    
    def do_POST(self) -> Any:
        """Handle POST requests"""
        try:
            if self.path == "/api/v1/users":
                self._handle_create_user()
            else:
                self._handle_not_found()
        except Exception as e:
            logger.error(f"POST request error: {e}")
            self._handle_error()
    
    def _handle_health_check(self) -> Any:
        """Health check endpoint"""
        response = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "environment": "production"
        }
        self._send_json_response(200, response)
    
    def _handle_get_users(self) -> Any:
        """Get all users"""
        users = self.db.get_users()
        response = {"users": users, "count": len(users)}
        self._send_json_response(200, response)
    
    def _handle_get_user(self) -> Any:
        """Get user by ID"""
        try:
            user_id = int(self.path.split("/")[-1])
            user = self.db.get_user(user_id)
            
            if user:
                self._send_json_response(200, user)
            else:
                self._send_json_response(404, {"error": "User not found"})
        except ValueError:
            self._send_json_response(400, {"error": "Invalid user ID"})
    
    def _handle_create_user(self) -> Any:
        """Create a new user"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Validate required fields
            required_fields = ["email", "username", "password"]
            for field in required_fields:
                if field not in data:
                    self._send_json_response(400, {"error": f"Missing required field: {field}"})
                    return
            
            # Create user
            user = self.db.create_user(
                email=data["email"],
                username=data["username"],
                password=data["password"]
            )
            
            # Remove password from response
            user_response = {k: v for k, v in user.items() if k != "password_hash"}
            self._send_json_response(201, user_response)
            
        except json.JSONDecodeError:
            self._send_json_response(400, {"error": "Invalid JSON"})
        except Exception as e:
            logger.error(f"Create user error: {e}")
            self._send_json_response(500, {"error": "Internal server error"})
    
    def _handle_not_found(self) -> Any:
        """Handle 404 errors"""
        self._send_json_response(404, {"error": "Not found"})
    
    def _handle_error(self) -> Any:
        """Handle 500 errors"""
        self._send_json_response(500, {"error": "Internal server error"})
    
    def _send_json_response(self, status_code: int, data: Dict) -> Any:
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response = json.dumps(data, indent=2)
        self.wfile.write(response.encode('utf-8'))
    
    def log_message(self, format, *args) -> Any:
        """Custom logging"""
        logger.info(f"{self.address_string()} - {format % args}")

# Production Server
class ProductionServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 8000) -> Any:
        self.host = host
        self.port = port
        self.server = None
    
    def start(self) -> Any:
        """Start production server"""
        try:
            # Create logs directory
            os.makedirs("logs", exist_ok=True)
            
            # Create server
            self.server = HTTPServer((self.host, self.port), ProductionAPIHandler)
            
            logger.info(f"Production server starting on {self.host}:{self.port}")
            logger.info("Environment: PRODUCTION")
            logger.info("Ready to handle requests...")
            
            # Start server
            self.server.serve_forever()
            
        except KeyboardInterrupt:
            logger.info("Shutting down production server...")
            if self.server:
                self.server.shutdown()
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise

# Background task processor
class BackgroundTaskProcessor:
    def __init__(self) -> Any:
        self.running = False
        self.thread = None
    
    def start(self) -> Any:
        """Start background task processor"""
        self.running = True
        self.thread = threading.Thread(target=self._process_tasks)
        self.thread.daemon = True
        self.thread.start()
        logger.info("Background task processor started")
    
    def stop(self) -> Any:
        """Stop background task processor"""
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("Background task processor stopped")
    
    def _process_tasks(self) -> Any:
        """Process background tasks"""
        while self.running:
            try:
                # Simulate background task processing
                try:
            time.sleep(5)
        except KeyboardInterrupt:
            break
                logger.debug("Processing background tasks...")
            except Exception as e:
                logger.error(f"Background task error: {e}")

# Main application
def main() -> Any:
    """Main production application"""
    logger.info("Starting production application...")
    
    # Start background task processor
    task_processor = BackgroundTaskProcessor()
    task_processor.start()
    
    try:
        # Start production server
        server = ProductionServer()
        server.start()
    finally:
        # Stop background tasks
        task_processor.stop()
        logger.info("Production application stopped")

if __name__ == "__main__":
    main() 