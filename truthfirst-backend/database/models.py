"""
SQLAlchemy Database Models for TruthFirst
"""
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, Enum as SQLEnum, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone
import enum

Base = declarative_base()


class CaseStatus(str, enum.Enum):
    """Case processing status"""
    PENDING = "PENDING"           # Submitted, not yet analyzed
    PROCESSING = "PROCESSING"     # Currently being analyzed
    COMPLETED = "COMPLETED"       # Analysis complete
    FAILED = "FAILED"            # Analysis failed


# class CaseType(str, enum.Enum):
#     """Type of content being analyzed"""
#     IMAGE = "IMAGE"
#     EMAIL = "EMAIL"
#     URL = "URL"

class CaseType(str, enum.Enum):
    IMAGE = "IMAGE"
    EMAIL = "EMAIL"
    URL = "URL"
    VIDEO = "VIDEO"

class Case(Base):
    """Main case model for storing investigation requests"""
    __tablename__ = "cases"
    
    # Primary Key
    id = Column(String(36), primary_key=True, index=True)  # UUID
    
    # Personal Information
    user_name = Column(String(255), nullable=False)
    user_email = Column(String(255), nullable=False, index=True)
    user_phone = Column(String(20), nullable=True)
    user_location = Column(String(255), nullable=True)
    
    # Case Information
    case_type = Column(SQLEnum(CaseType), nullable=False, index=True)
    case_source = Column(String(255), nullable=True)  # Where did they encounter this?
    case_description = Column(Text, nullable=True)
    
    # File/Content Information
    file_path = Column(String(500), nullable=True)  # Path to uploaded file
    file_name = Column(String(255), nullable=True)  # Original filename
    file_size = Column(Integer, nullable=True)      # Size in bytes
    content_text = Column(Text, nullable=True)      # For email/URL text content
    
    # Status & Processing
    status = Column(SQLEnum(CaseStatus), default=CaseStatus.PENDING, index=True)
    
    # Analysis Results (stored as JSON)
    analysis_result = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    analyzed_at = Column(DateTime, nullable=True)
    
    # Soft Delete (for 30-day retention)
    is_deleted = Column(Boolean, default=False, index=True)
    deleted_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Case {self.id} - {self.case_type} - {self.status}>"

class OTP(Base):
    __tablename__ = "otps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, index=True)
    otp_code = Column(String(6), nullable=False)
    attempts = Column(Integer, default=0)
    is_verified = Column(Boolean, default=False)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    expires_at = Column(
        DateTime(timezone=True),
        nullable=False
    )

    verified_at = Column(
        DateTime(timezone=True),
        nullable=True
    )
