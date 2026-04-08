"""
Pydantic Schemas for Case Submission and Management
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Any
from datetime import datetime
from database.models import CaseStatus, CaseType


# ==================== REQUEST SCHEMAS ====================

class PersonalInfo(BaseModel):
    """Personal information of the user submitting the case"""
    name: str = Field(..., min_length=2, max_length=255, description="Full name")
    email: EmailStr = Field(..., description="Email address for notifications")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number (optional)")
    location: Optional[str] = Field(None, max_length=255, description="City/State (optional)")


class CaseInfo(BaseModel):
    """Information about the case being submitted"""
    type: CaseType = Field(..., description="Type of content (IMAGE, EMAIL, URL)")
    source: Optional[str] = Field(None, max_length=255, description="Where was this encountered?")
    description: Optional[str] = Field(None, max_length=2000, description="Additional context")


class CaseSubmitRequest(BaseModel):
    """Complete case submission request"""
    personal_info: PersonalInfo
    case_info: CaseInfo
    # File will be uploaded via multipart/form-data separately


# ==================== RESPONSE SCHEMAS ====================

class CaseSubmitResponse(BaseModel):
    """Response after case submission"""
    case_id: str = Field(..., description="Unique case identifier")
    status: CaseStatus = Field(..., description="Current case status")
    message: str = Field(..., description="Success message")
    created_at: datetime = Field(..., description="Timestamp of creation")


class CaseStatusResponse(BaseModel):
    """Response for case status check"""
    case_id: str
    status: CaseStatus
    case_type: CaseType
    created_at: datetime
    analyzed_at: Optional[datetime] = None
    has_results: bool = Field(..., description="Whether analysis results are available")


class CaseDetailsResponse(BaseModel):
    """Detailed case information"""
    case_id: str
    status: CaseStatus
    case_type: CaseType
    
    # Personal info
    user_name: str
    user_email: str
    user_phone: Optional[str]
    user_location: Optional[str]
    
    # Case info
    case_source: Optional[str]
    case_description: Optional[str]
    
    # File info
    file_name: Optional[str]
    file_size: Optional[int]
    
    # Timestamps
    created_at: datetime
    analyzed_at: Optional[datetime]
    
    # Results (if available)
    analysis_result: Optional[Any] = None


class CaseListItem(BaseModel):
    """Minimal case information for list views"""
    case_id: str
    case_type: CaseType
    status: CaseStatus
    created_at: datetime
    file_name: Optional[str]


class CaseListResponse(BaseModel):
    """Response for listing cases"""
    cases: list[CaseListItem]
    total: int