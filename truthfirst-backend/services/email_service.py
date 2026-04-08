"""
Email Service
Handles email sending via SMTP (Gmail).
"""

import logging
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from jinja2 import Template
from config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails."""
    
    TEMPLATE_DIR = Path(__file__).parent.parent / "templates"
    
    @staticmethod
    async def send_otp_email(email: str, otp_code: str) -> bool:
        """
        Send OTP verification email.
        
        Args:
            email: Recipient email
            otp_code: 6-digit OTP code
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Load email template
            template_path = EmailService.TEMPLATE_DIR / "email_otp.html"
            with open(template_path, 'r', encoding='utf-8') as f:
                template = Template(f.read())
            
            # Render template
            html_content = template.render(
                otp_code=otp_code,
                validity_minutes=5
            )
            
            # Create email message
            message = MIMEMultipart("alternative")
            message["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
            message["To"] = email
            message["Subject"] = "TruthFirst - Email Verification Code"
            
            # Add plain text fallback
            text_content = f"""
TruthFirst Email Verification

Your verification code is: {otp_code}

This code will expire in 5 minutes.

If you didn't request this code, please ignore this email.

---
TruthFirst - Multi-modal Investigation Platform
            """.strip()
            
            message.attach(MIMEText(text_content, "plain"))
            message.attach(MIMEText(html_content, "html"))
            
            # Send email
            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USERNAME,
                password=settings.SMTP_PASSWORD,
                start_tls=True
            )
            
            logger.info(f"✅ OTP email sent to {email}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to send OTP email to {email}: {str(e)}")
            return False
    
    @staticmethod
    async def send_case_confirmation_email(
        email: str,
        case_id: str,
        case_type: str
    ) -> bool:
        """
        Send case submission confirmation email (future enhancement).
        
        Args:
            email: Recipient email
            case_id: Case ID
            case_type: Case type (IMAGE/EMAIL/URL)
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Simple confirmation email
            message = MIMEText(f"""
TruthFirst - Case Submitted Successfully

Your case has been submitted successfully!

Case ID: {case_id}
Case Type: {case_type}

You can track your case status at:
http://localhost:8000/api/case/{case_id}/status

We will analyze your submission and provide results shortly.

---
TruthFirst - Multi-modal Investigation Platform
            """.strip())
            
            message["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
            message["To"] = email
            message["Subject"] = f"TruthFirst - Case {case_id} Submitted"
            
            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USERNAME,
                password=settings.SMTP_PASSWORD,
                start_tls=True
            )
            
            logger.info(f"✅ Confirmation email sent to {email} for case {case_id}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to send confirmation email: {str(e)}")
            return False