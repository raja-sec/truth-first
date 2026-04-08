"""
Case Router - Case Submission and Management
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from database.db import get_db
from database import crud
from database.models import CaseType, CaseStatus
from schemas.case import (
    CaseSubmitResponse, CaseStatusResponse, CaseDetailsResponse,
    PersonalInfo, CaseInfo
)
from services.file_handler import file_handler
from services.analysis_service import analysis_service
from utils.constants import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from config import settings
from services.otp_service import OTPService
import json
import logging

router = APIRouter(prefix="/api/case", tags=["Case Management"])
logger = logging.getLogger(__name__)


@router.post("/submit", response_model=CaseSubmitResponse)
async def submit_case(
    personal_info: str = Form(..., description="Personal info as JSON string"),
    case_info: str = Form(..., description="Case info as JSON string"),
    verification_token: str = Form(..., description="OTP verification token"),
    file: UploadFile = File(None, description="File to analyze (for IMAGE/VIDEO types)"),
    content_text: str = Form(None, description="Text content (for EMAIL/URL types)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit a new case for analysis.
    
    **Supported Types:**
    - IMAGE: Requires file upload (jpg, png, webp)
    - VIDEO: Requires file upload (mp4, avi, mov)
    - EMAIL: Requires content_text (email body) or .eml file upload
    - URL: Requires content_text (URL to check)
    """
    try:
        # Validate verification token
        verified_email = await OTPService.validate_verification_token(verification_token)
        if not verified_email:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired verification token"
            )
        
        # Parse JSON strings
        personal_data = json.loads(personal_info)
        case_data = json.loads(case_info)

        # Securely override email with verified email
        personal_data["email"] = verified_email

        # Validate with Pydantic schemas
        personal = PersonalInfo(**personal_data)
        case_inf = CaseInfo(**case_data)
        
        # Validate inputs based on case type
        if case_inf.type == CaseType.IMAGE:
            if not file:
                raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="File upload required for IMAGE type")
            if file.filename:
                file_ext = file.filename.split(".")[-1].lower()
                if file_ext not in settings.allowed_image_types_list:
                    raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=f"Invalid file type. Allowed: {', '.join(settings.allowed_image_types_list)}")

        elif case_inf.type == CaseType.VIDEO:
            if not file:
                raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="File upload required for VIDEO type")
            if file.filename:
                file_ext = file.filename.split(".")[-1].lower()
                allowed_video_exts = ["mp4", "avi", "mov"]
                if file_ext not in allowed_video_exts:
                    raise HTTPException(
                        status_code=HTTP_400_BAD_REQUEST, 
                        detail=f"Invalid video type. Allowed: {', '.join(allowed_video_exts)}"
                    )
                    
        elif case_inf.type == CaseType.URL:
            if not content_text:
                raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Text content required for URL type")

        elif case_inf.type == CaseType.EMAIL:
            has_text = bool(content_text and content_text.strip())
            has_file = file is not None
            if not has_text and not has_file:
                raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="EMAIL requires either pasted content or .eml file upload")
            if has_file and file.filename:
                ext = file.filename.lower()
                if not ext.endswith((".eml", ".png", ".jpg", ".jpeg", ".webp")):
                    raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="EMAIL supports .eml or image screenshots")

        # Create case in database
        case = await crud.create_case(
            db=db,
            user_name=personal.name,
            user_email=personal.email,
            user_phone=personal.phone,
            user_location=personal.location,
            case_type=case_inf.type,
            case_source=case_inf.source,
            case_description=case_inf.description,
            content_text=content_text,
        )
        
        # Save file if provided
        if file:
            file_info = await file_handler.save_file(file, case.id, prefix="case")
            case.file_path = file_info["file_path"]
            case.file_name = file_info["file_name"]
            case.file_size = file_info["file_size"]
            await db.commit()
            
        logger.info(f"Case submitted successfully: {case.id} by {personal.email}")
        
        return CaseSubmitResponse(
            case_id=case.id,
            status=case.status,
            message="Case submitted successfully. You can now analyze it.",
            created_at=case.created_at
        )
    
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in request: {e}")
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid JSON format in personal_info or case_info"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Case submission error: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit case: {str(e)}" if settings.DEBUG else "Internal server error"
        )


@router.post("/{case_id}/analyze")
async def analyze_case(case_id: str, db: AsyncSession = Depends(get_db)):
    """
    Analyze a submitted case.
    This endpoint triggers the actual detection analysis.
    """
    try:
        case = await crud.get_case_by_id(db, case_id)
        if not case:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Case not found: {case_id}")
        
        if case.status == CaseStatus.COMPLETED:
            return JSONResponse(
                content={
                    "message": "Case already analyzed",
                    "case_id": case_id,
                    "status": case.status.value
                }
            )
        
        await crud.update_case_status(db, case_id, CaseStatus.PROCESSING)
        logger.info(f"Starting analysis for case {case_id}")
        
        try:
            analysis_result = await analysis_service.analyze_case(case)
            
            await crud.update_case_status(
                db=db,
                case_id=case_id,
                status=CaseStatus.COMPLETED,
                analysis_result=analysis_result
            )
            
            logger.info(f"Analysis completed for case {case_id}")
            
            return {
                "message": "Analysis completed successfully",
                "case_id": case_id,
                "status": CaseStatus.COMPLETED.value,
                "verdict": analysis_result["overall_verdict"],
                "confidence": analysis_result["overall_confidence"],
                "risk_score": analysis_result["overall_risk_score"]
            }
        
        except Exception as analysis_error:
            await crud.update_case_status(db, case_id, CaseStatus.FAILED)
            raise analysis_error
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis error for case {case_id}: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}" if settings.DEBUG else "Analysis failed"
        )


@router.get("/{case_id}/status", response_model=CaseStatusResponse)
async def get_case_status(case_id: str, db: AsyncSession = Depends(get_db)):
    """Get current status of a case."""
    case = await crud.get_case_by_id(db, case_id)
    if not case:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Case not found: {case_id}")
    
    return CaseStatusResponse(
        case_id=case.id,
        status=case.status,
        case_type=case.case_type,
        created_at=case.created_at,
        analyzed_at=case.analyzed_at,
        has_results=case.analysis_result is not None
    )


@router.get("/{case_id}", response_model=CaseDetailsResponse)
async def get_case_details(case_id: str, db: AsyncSession = Depends(get_db)):
    """Get complete case details including analysis results."""
    case = await crud.get_case_by_id(db, case_id)
    if not case:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Case not found: {case_id}")
    
    return CaseDetailsResponse(
        case_id=case.id,
        status=case.status,
        case_type=case.case_type,
        user_name=case.user_name,
        user_email=case.user_email,
        user_phone=case.user_phone,
        user_location=case.user_location,
        case_source=case.case_source,
        case_description=case.case_description,
        file_name=case.file_name,
        file_size=case.file_size,
        created_at=case.created_at,
        analyzed_at=case.analyzed_at,
        analysis_result=case.analysis_result
    )


@router.get("/user/{email}")
async def get_user_cases(email: str, limit: int = 10, db: AsyncSession = Depends(get_db)):
    """Get all cases submitted by a specific email address."""
    cases = await crud.get_cases_by_email(db, email, limit)
    return {
        "email": email,
        "total": len(cases),
        "cases": [
            {
                "case_id": case.id,
                "case_type": case.case_type.value,
                "status": case.status.value,
                "created_at": case.created_at.isoformat(),
                "file_name": case.file_name,
            }
            for case in cases
        ]
    }