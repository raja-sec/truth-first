"""
OTP API Schemas
Pydantic models for OTP endpoints.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class OTPSendRequest(BaseModel):
    """Request to send OTP."""
    email: EmailStr = Field(..., description="Email address to send OTP to")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com"
            }
        }


class OTPSendResponse(BaseModel):
    """Response after sending OTP."""
    success: bool
    message: str
    email: str
    expires_in_minutes: int = 5
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "OTP sent successfully. Check your email.",
                "email": "user@example.com",
                "expires_in_minutes": 5
            }
        }


class OTPVerifyRequest(BaseModel):
    """Request to verify OTP."""
    email: EmailStr = Field(..., description="Email address")
    otp_code: str = Field(..., min_length=6, max_length=6, description="6-digit OTP code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "otp_code": "123456"
            }
        }


class OTPVerifyResponse(BaseModel):
    """Response after OTP verification."""
    success: bool
    message: str
    verification_token: Optional[str] = None
    token_expires_in_minutes: int = 10
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Email verified successfully",
                "verification_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_expires_in_minutes": 10
            }
        }


class OTPErrorResponse(BaseModel):
    """Error response for OTP operations."""
    success: bool = False
    message: str
    error: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "message": "OTP expired",
                "error": "The OTP code has expired. Please request a new one."
            }
        }