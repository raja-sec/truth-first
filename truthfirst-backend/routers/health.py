"""
Health Check Router
Provides system status and model readiness information
"""
from fastapi import APIRouter
from schemas.detection import HealthResponse
from services.model_loader import model_loader
from config import settings

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify service status
    
    Returns:
        - Service status
        - Model loading status
        - Device information
    """
    return HealthResponse(
        status="healthy",
        app_name=settings.APP_NAME,
        version="1.0.0-phase1",
        model_loaded=model_loader.is_loaded(),
        device=settings.model_device
    )