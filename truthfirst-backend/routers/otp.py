"""
OTP API Router
Endpoints for OTP generation and verification with precise error handling.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database.db import get_db
from services.otp_service import OTPService
from services.email_service import EmailService
from schemas.otp import (
    OTPSendRequest,
    OTPSendResponse,
    OTPVerifyRequest,
    OTPVerifyResponse
)
# Make sure to create this file first
from utils.error_codes import OTPErrorCode

router = APIRouter(prefix="/api/otp", tags=["otp"])
logger = logging.getLogger(__name__)

# Map internal error codes to appropriate HTTP status codes
ERROR_STATUS_MAP = {
    OTPErrorCode.INVALID_OTP: 400,   # Bad Request
    OTPErrorCode.OTP_EXPIRED: 410,   # Gone (Resource no longer available)
    OTPErrorCode.MAX_ATTEMPTS: 429,  # Too Many Requests
    OTPErrorCode.OTP_USED: 409,      # Conflict (State conflict)
    OTPErrorCode.UNKNOWN_ERROR: 500  # Internal Server Error
}


@router.post("/send", response_model=OTPSendResponse)
async def send_otp(
    request: OTPSendRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Send OTP verification code to an email address.
    
    **Process:**
    1. Validates email format.
    2. Checks rate limiting (1 OTP per minute).
    3. Generates a secure 6-digit OTP.
    4. Stores in database with a 5-minute expiration.
    5. Dispatches email via secure SMTP.
    
    **Returns:**
        Confirmation that OTP was sent (does NOT include the actual OTP)
        
    **Raises:**
        429: Rate limit exceeded
        500: Email sending failed
    """
    email = request.email
    
    # Create OTP
    otp_code, error = await OTPService.create_otp(db, email)
    
    if error:
        # Rate limiting or other error from creation
        # Assuming create_otp returns a string error message for now, 
        # but ideally it should also follow the structured error pattern.
        # For simple rate limiting, 429 is standard.
        raise HTTPException(status_code=429, detail=str(error))
    
    # Send email
    email_sent = await EmailService.send_otp_email(email, otp_code)
    
    if not email_sent:
        raise HTTPException(
            status_code=500,
            detail="Failed to send OTP email. Please try again later."
        )
    
    logger.info(f"📧 OTP sent to {email}")
    
    return OTPSendResponse(
        success=True,
        message="OTP sent successfully. Check your email.",
        email=email,
        expires_in_minutes=5
    )


@router.post("/verify", response_model=OTPVerifyResponse)
async def verify_otp(
    request: OTPVerifyRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify OTP code and issue a JWT verification token.
    
    **Process:**
    1. Validates the provided 6-digit OTP code against the database.
    2. Enforces expiration (5 minutes) and maximum attempt limits (3 tries).
    3. Marks OTP as used to prevent replay attacks.
    4. Generates a secure JWT verification token.
    
    **Returns:**
        Verification token (valid for 10 minutes) to be used during case submission.
        
    **Raises:**
        400: Invalid OTP
        410: Expired OTP
        409: OTP Already Used
        429: Max Attempts Exceeded
    """
    email = request.email
    otp_code = request.otp_code

    try:
        # verify_otp now returns (token, error_dict)
        token, error = await OTPService.verify_otp(db, email, otp_code)

        if error:
            # Determine the correct HTTP status code based on the error code
            status_code = ERROR_STATUS_MAP.get(
                error.get("code", OTPErrorCode.UNKNOWN_ERROR),
                400 # Default fallback
            )

            # Return structured error details for the frontend
            raise HTTPException(
                status_code=status_code,
                detail={
                    "message": error.get("message", "Verification failed"),
                    "code": error.get("code", OTPErrorCode.UNKNOWN_ERROR)
                }
            )

        logger.info(f"✅ OTP verified for {email}")

        return OTPVerifyResponse(
            success=True,
            message="Email verified successfully",
            verification_token=token,
            token_expires_in_minutes=10
        )

    except HTTPException:
        # Re-raise HTTPExceptions explicitly to preserve status codes
        raise

    except Exception as e:
        logger.error(f"OTP verification unexpected error for {email}: {e}")
        # Fallback for truly unexpected system errors
        raise HTTPException(
            status_code=500,
            detail={
                "message": "An unexpected error occurred during verification",
                "code": OTPErrorCode.UNKNOWN_ERROR
            }
        )