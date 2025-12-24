"""
Find My Journal - FastAPI Application Entry Point
"""
import os
import sys
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.services.db_service import db_service
from app.api.v1.auth import router as auth_router
from app.api.v1.search import router as search_router
from app.api.v1.explain import router as explain_router
from app.api.v1.share import router as share_router
from app.api.v1.saved_searches import router as saved_searches_router
from app.api.v1.feedback import router as feedback_router

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered academic journal finder for researchers",
)

# CORS middleware for frontend access
# Read allowed origins from environment variable, fallback to localhost for dev
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    Verifies database connectivity.
    """
    db_connected = db_service.check_connection()

    return {
        "status": "ok" if db_connected else "degraded",
        "db": "connected" if db_connected else "disconnected",
    }


# Include API routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(search_router, prefix="/api/v1")
app.include_router(explain_router, prefix="/api/v1")
app.include_router(share_router, prefix="/api/v1")
app.include_router(saved_searches_router, prefix="/api/v1")
app.include_router(feedback_router, prefix="/api/v1")
