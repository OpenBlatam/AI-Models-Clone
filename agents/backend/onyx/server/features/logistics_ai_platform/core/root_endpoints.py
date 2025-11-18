"""
Root endpoints

This module provides root-level endpoints for the application.
"""

import time
from fastapi import FastAPI


def setup_root_endpoints(app: FastAPI) -> None:
    """Register root-level endpoints"""
    
    @app.get("/")
    async def root():
        """Root endpoint with API information"""
        return {
            "service": "Logistics AI Platform",
            "version": "1.0.0",
            "status": "running",
            "description": "Comprehensive freight forwarding and logistics management system",
            "endpoints": {
                "forwarding": {
                    "quotes": "/forwarding/quotes",
                    "bookings": "/forwarding/bookings",
                    "shipments": "/forwarding/shipments",
                    "containers": "/forwarding/containers"
                },
                "tracking": {
                    "track_shipment": "/tracking/shipment/{shipment_id}",
                    "track_container": "/tracking/container/{container_id}",
                    "tracking_history": "/tracking/shipment/{shipment_id}/history",
                    "summary": "/tracking/summary"
                },
                "invoices": {
                    "create": "/invoices",
                    "list": "/invoices",
                    "get": "/invoices/{invoice_id}",
                    "by_shipment": "/invoices/shipment/{shipment_id}"
                },
                "documents": {
                    "upload": "/documents",
                    "get": "/documents/{document_id}",
                    "by_shipment": "/documents/shipment/{shipment_id}",
                    "delete": "/documents/{document_id}"
                },
                "alerts": {
                    "create": "/alerts",
                    "list": "/alerts",
                    "get": "/alerts/{alert_id}",
                    "mark_read": "/alerts/{alert_id}/read",
                    "delete": "/alerts/{alert_id}"
                },
                "insurance": {
                    "create": "/insurance",
                    "get": "/insurance/{insurance_id}",
                    "by_shipment": "/insurance/shipment/{shipment_id}"
                },
                "reports": {
                    "dashboard": "/reports/dashboard",
                    "shipments": "/reports/shipments"
                },
                "docs": "/docs",
                "redoc": "/redoc"
            }
        }
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "timestamp": time.time()
        }







