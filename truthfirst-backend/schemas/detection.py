"""
Pydantic Schemas for Detection Results
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any


class ImageMetrics(BaseModel):
    """Metrics from Image Detector"""
    cnn_fake: float = Field(..., description="CNN fake probability")
    frequency_score: float = Field(..., description="Frequency domain analysis score")
    artifact_score: float = Field(..., description="Artifact/noise inconsistency score")


class ImageAnalysisResult(BaseModel):
    """Normalized Image Analysis Result for Frontend"""
    modality: str = Field(default="image", description="Type of content analyzed")
    verdict: str = Field(..., description="GENUINE or DEEPFAKE/PHISHING")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    risk_score: int = Field(..., ge=0, le=100, description="Risk score (0-100)")
    factors: ImageMetrics = Field(..., description="Detailed detection factors")
    flags: List[str] = Field(default_factory=list, description="List of detected issues")
    explanation: str = Field(..., description="Human-readable summary")
    grad_cam_base64: Optional[str] = Field(None, description="Base64-encoded Grad-CAM heatmap")
    face_found: bool = Field(..., description="Whether a face was detected")


class ErrorResponse(BaseModel):
    """Standard Error Response"""
    error: str = Field(..., description="Error type/code")
    message: str = Field(..., description="User-friendly error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details (dev only)")


class HealthResponse(BaseModel):
    """Health Check Response"""
    model_config = ConfigDict(protected_namespaces=())  # Allow model_ prefix
    
    status: str = Field(..., description="Service status")
    app_name: str = Field(..., description="Application name")
    version: str = Field(..., description="API version")
    model_loaded: bool = Field(..., description="Whether image model is loaded")
    device: str = Field(..., description="Device being used (cuda/cpu)")