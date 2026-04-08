"""
TruthFirst Backend - Main Application Entry Point
FastAPI application for multi-modal deception detection.
"""
import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import configuration
from config import settings, validate_model_file

# Import routers
from routers import health, analysis, case, report, otp, files

# Import model loader and database
from services.model_loader import model_loader
from database.db import init_db, close_db

# Configure professional logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("truthfirst.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    logger.info(f"Starting {settings.APP_NAME} in {settings.APP_ENV} mode")
    logger.info(f"Compute Device: {settings.model_device}")
    
    try:
        # Validate core model files exist
        validate_model_file()
        
        # Initialize database
        await init_db()
        logger.info("Database initialized successfully.")
        
        # Pre-load core models
        logger.info("Initializing model loader...")
        model_loader.load_image_detector()
        # The other modalities (video, email, url) will load based on your model_loader logic
        logger.info("Core models loaded.")
        
    except Exception as e:
        logger.critical(f"Application startup failed: {str(e)}", exc_info=True)
        raise
    
    logger.info("Application startup complete. Ready to accept traffic.")
    
    yield
    
    # Shutdown sequence
    logger.info("Initiating application shutdown...")
    model_loader.unload()
    await close_db()
    logger.info("Cleanup complete. Application terminated.")


# Initialize FastAPI app with updated metadata
app = FastAPI(
    title=settings.APP_NAME,
    description="Multi-Modal Deception Detection API (Image, Video, URL, Email)",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None, # Disable swagger in production
    redoc_url="/redoc" if settings.DEBUG else None
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(f"CORS configured for origins: {settings.cors_origins_list}")


# Include routers
app.include_router(health.router)
app.include_router(analysis.router)
app.include_router(case.router)
app.include_router(report.router)
app.include_router(otp.router)
app.include_router(files.router)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API health and version info"""
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "status": "operational",
        "environment": settings.APP_ENV,
        "modalities_active": ["image", "video", "url", "email"]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )