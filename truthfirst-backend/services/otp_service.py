"""
OTP Service
Handles OTP generation, validation, and rate limiting.
"""

import secrets
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from jose import JWTError, jwt

from database.models import OTP
from config import settings
from utils.error_codes import OTPErrorCode

logger = logging.getLogger(__name__)


class OTPService:
    """Service for OTP generation and validation."""
    
    # OTP Configuration
    OTP_LENGTH = 6
    OTP_EXPIRY_MINUTES = 5
    RATE_LIMIT_SECONDS = 60  # 1 OTP per minute
    MAX_ATTEMPTS = 3
    
    # JWT Configuration for verification tokens
    SECRET_KEY = settings.SECRET_KEY
    ALGORITHM = "HS256"
    TOKEN_EXPIRY_MINUTES = 10
    
    @staticmethod
    def generate_otp() -> str:
        """Generate a 6-digit OTP."""
        return str(secrets.randbelow(900000) + 100000)
    
    @staticmethod
    async def create_otp(
        db: AsyncSession,
        email: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Create and store OTP for email.
        
        Returns:
            Tuple of (otp_code, error_message)
        """
        # Check rate limiting
        rate_limit_error = await OTPService._check_rate_limit(db, email)
        if rate_limit_error:
            return None, rate_limit_error
        
        # Invalidate any existing OTPs for this email
        await OTPService._invalidate_existing_otps(db, email)
        
        # Generate new OTP
        otp_code = OTPService.generate_otp()
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=OTPService.OTP_EXPIRY_MINUTES
        )
        
        # Create OTP record
        otp = OTP(
            email=email,
            otp_code=otp_code,
            expires_at=expires_at,
            is_verified=False,
            attempts=0
        )
        
        db.add(otp)
        await db.commit()
        await db.refresh(otp)
        
        logger.info(f"✅ OTP created for {email}, expires at {expires_at}")
        return otp_code, None

    @classmethod
    async def verify_otp(cls, db: AsyncSession, email: str, otp_code: str):
        """
        Verify OTP code and return (token, error_dict).
        Error is ALWAYS None or a dictionary: {"message": str, "code": str}
        """
        
        # 1. Try to find the exact valid OTP entry
        result = await db.execute(
            select(OTP)
            .where(OTP.email == email, OTP.otp_code == otp_code)
            .order_by(OTP.created_at.desc())
        )
        otp_entry = result.scalar_one_or_none()

        # ---------------------------------------------------------
        # SCENARIO A: No exact match found (Code is wrong, or record missing)
        # ---------------------------------------------------------
        if not otp_entry:
            # Fetch the LATEST record for this email (ignoring code) to see status
            result = await db.execute(
                select(OTP)
                .where(OTP.email == email)
                .order_by(OTP.created_at.desc())
                .limit(1)
            )
            latest_otp = result.scalar_one_or_none()


            # If absolutely no record exists for this email
            if not latest_otp:
                return None, {
                    "message": "Invalid OTP",
                    "code": OTPErrorCode.INVALID_OTP
                }

            # Check if that latest record is actually expired
            if latest_otp.expires_at <= datetime.now(timezone.utc):
                return None, {
                    "message": "OTP expired",
                    "code": OTPErrorCode.OTP_EXPIRED
                }

            # Check if it was already used
            if latest_otp.is_verified:
                return None, {
                    "message": "OTP already used",
                    "code": OTPErrorCode.OTP_USED
                }

            # Check attempts limit
            if latest_otp.attempts >= cls.MAX_ATTEMPTS:
                return None, {
                    "message": "Maximum attempts exceeded. Request a new OTP.",
                    "code": OTPErrorCode.MAX_ATTEMPTS
                }

            # If we are here, the record exists and is valid, but the CODE was wrong.
            # We must increment the attempts counter.
            latest_otp.attempts += 1
            await db.commit()

            return None, {
                "message": "Invalid OTP",
                "code": OTPErrorCode.INVALID_OTP
            }

        # ---------------------------------------------------------
        # SCENARIO B: Exact match found (Email + Code are correct)
        # Now we check the state of this specific matching record
        # ---------------------------------------------------------
        
        # 1. Check Expiry
        if otp_entry.expires_at <= datetime.now(timezone.utc):
            return None, {
                "message": "OTP expired",
                "code": OTPErrorCode.OTP_EXPIRED
            }

        # 2. Check Already Verified
        if otp_entry.is_verified:
            return None, {
                "message": "OTP already used",
                "code": OTPErrorCode.OTP_USED
            }

        # 3. Check Max Attempts
        if otp_entry.attempts >= cls.MAX_ATTEMPTS:
            return None, {
                "message": "Maximum attempts exceeded. Request a new OTP.",
                "code": OTPErrorCode.MAX_ATTEMPTS
            }

        # ---------------------------------------------------------
        # SCENARIO C: Success
        # ---------------------------------------------------------
        otp_entry.is_verified = True
        otp_entry.verified_at = datetime.now(timezone.utc)
        await db.commit()

        # Generate the JWT/Token for the next step
        token = cls._generate_verification_token(email)
        return token, None

    @staticmethod
    async def validate_verification_token(token: str) -> Optional[str]:
        """Validate verification token and extract email."""
        try:
            payload = jwt.decode(
                token,
                OTPService.SECRET_KEY,
                algorithms=[OTPService.ALGORITHM],
                options={"verify_exp": True}
            )
            return payload.get("email")
        except JWTError:
            return None

    @staticmethod
    def _generate_verification_token(email: str) -> str:
        """Generate JWT verification token."""
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=OTPService.TOKEN_EXPIRY_MINUTES)

        payload = {
            "email": email,
            "iat": int(now.timestamp()),
            "exp": int(expires_at.timestamp())
        }

        return jwt.encode(
            payload,
            OTPService.SECRET_KEY,
            algorithm=OTPService.ALGORITHM
        )
    
    @staticmethod
    async def _check_rate_limit(
        db: AsyncSession,
        email: str
    ) -> Optional[str]:
        """Check if email is rate limited."""
        rate_limit_time = datetime.now(timezone.utc) - timedelta(
            seconds=OTPService.RATE_LIMIT_SECONDS
        )
        
        result = await db.execute(
            select(OTP).where(
                and_(
                    OTP.email == email,
                    OTP.created_at > rate_limit_time
                )
            )
        )
        recent_otp = result.scalar_one_or_none()
        
        if recent_otp:
            seconds_remaining = int(
                (recent_otp.created_at + timedelta(seconds=OTPService.RATE_LIMIT_SECONDS)
                - datetime.now(timezone.utc)).total_seconds()
            )
            return f"Please wait {seconds_remaining} seconds before requesting another OTP"
        
        return None
    
    @staticmethod
    async def _invalidate_existing_otps(
        db: AsyncSession,
        email: str
    ):
        """Invalidate any existing unverified OTPs for email."""
        result = await db.execute(
            select(OTP).where(
                and_(
                    OTP.email == email,
                    OTP.is_verified == False
                )
            )
        )
        existing_otps = result.scalars().all()
        
        for otp in existing_otps:
            otp.is_verified = True  # Mark as used to prevent reuse
        
        if existing_otps:
            await db.commit()
            logger.info(f"🗑️ Invalidated {len(existing_otps)} existing OTPs for {email}")