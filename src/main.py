"""Real FastAPI Application"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Real API",
    description="Real organized API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Real API - Organized!"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "organized": True}
