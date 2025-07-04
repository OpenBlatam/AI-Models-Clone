#!/usr/bin/env python3
"""
Demo Script for Improved AI Video API
=====================================

Demonstrates the new API capabilities and performance improvements.
"""

import asyncio
import json
import time
from typing import List
import httpx


class APIDemo:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = None
        
    async def __aenter__(self):
        self.client = httpx.AsyncClient(base_url=self.base_url)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()

    async def create_video(self, prompt: str, user_id: str = "demo_user") -> dict:
        """Create a video generation request."""
        response = await self.client.post(
            "/api/v1/videos",
            json={
                "input_text": prompt,
                "user_id": user_id,
                "quality": "high",
                "duration": 30
            },
            headers={"Authorization": "Bearer demo-token"}
        )
        return response.json()

    async def run_demo(self):
        """Run the complete demonstration."""
        print("🎉 AI Video API Improved - Demo")
        print("=" * 50)
        
        try:
            # Test health endpoint
            health_response = await self.client.get("/api/v1/health")
            print(f"✅ Health check: {health_response.status_code}")
            
            # Create a video
            print("📝 Creating demo video...")
            create_response = await self.create_video("Demo video about AI")
            
            print(f"📋 Response: {json.dumps(create_response, indent=2)}")
            print("✨ Demo completed!")
            
        except Exception as e:
            print(f"❌ Demo failed: {e}")


async def main():
    """Main demo function."""
    async with APIDemo() as demo:
        await demo.run_demo()


if __name__ == "__main__":
    asyncio.run(main()) 