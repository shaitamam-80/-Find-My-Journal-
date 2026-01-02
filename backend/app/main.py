"""
Find My Journal - FastAPI Application Entry Point
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.logging import setup_logging, get_logger
from app.core.exceptions import AppException, DatabaseError, NotFoundError
from app.services.db_service import db_service

# Initialize logging before anything else
setup_logging()
logger = get_logger(__name__)
from app.api.v1.auth import router as auth_router
from app.api.v1.search import router as search_router
from app.api.v1.explain import router as explain_router
from app.api.v1.share import router as share_router
from app.api.v1.saved_searches import router as saved_searches_router
from app.api.v1.feedback import router as feedback_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.users import router as users_router
from app.api.v1.admin import router as admin_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown events."""
    # Startup
    logger.info("Starting up Find My Journal API...")
    await db_service.initialize()
    logger.info("Database connection established")

    yield  # Application runs here

    # Shutdown
    logger.info("Shutting down...")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered academic journal finder for researchers",
    lifespan=lifespan,
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


# Exception handlers
@app.exception_handler(DatabaseError)
async def database_error_handler(request: Request, exc: DatabaseError):
    logger.error(f"Database error: {exc.message}", extra={"details": exc.details})
    return JSONResponse(
        status_code=500,
        content={"error": "Database error", "message": exc.message}
    )


@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=404,
        content={"error": "Not found", "message": exc.message}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "message": "An unexpected error occurred"}
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
    db_connected = await db_service.check_connection()

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
app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
