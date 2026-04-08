"""
Report API Router
Endpoints for PDF report generation and complaint guidance.
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from database.db import get_db
from database import crud
from database.models import CaseStatus
from services.report_generator import ReportGenerator
from services.complaint_guidance import ComplaintGuidanceService
from schemas.report import ComplaintGuidanceResponse, ErrorResponse

router = APIRouter(prefix="/api/report", tags=["reports"])


@router.get("/{case_id}/pdf")
async def get_pdf_report(
    case_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate and download a comprehensive PDF forensic report for a case.
    
    Args:
        case_id: Unique Case Identifier
        
    Returns:
        A formatted PDF file as a downloadable attachment.
        
    Raises:
        404: Case not found
        400: Analysis not completed or results missing
    """
    # Get case - use correct function name from Phase 2
    case = await crud.get_case_by_id(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Check if analysis is completed
    if case.status != "COMPLETED":
        raise HTTPException(
            status_code=400,
            detail=f"Analysis not complete. Current status: {case.status}"
        )
    
    # Check if analysis result exists
    if not case.analysis_result:
        raise HTTPException(
            status_code=400,
            detail="No analysis results available"
        )
    
    try:
        # Generate PDF
        pdf_bytes = ReportGenerator.generate_pdf(case)
        
        # Return as downloadable file
        filename = f"TruthFirst_Report_{case_id}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate PDF: {str(e)}"
        )


@router.get("/{case_id}/complaint-guidance", response_model=ComplaintGuidanceResponse)
async def get_complaint_guidance(
    case_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve legally safe complaint filing guidance for a specific case.
    
    **IMPORTANT:** This endpoint provides GUIDANCE ONLY.
    It does NOT pre-fill official complaints or submit anything to authorities.
    The user is solely responsible for their complaint content and evidence.
    
    Args:
        case_id: Unique Case Identifier
        
    Returns:
        Structured JSON guidance including legal disclaimers, proper filing steps, and good vs. bad complaint examples.
        
    Raises:
        404: Case not found
        400: Analysis not completed, in progress, or failed
    """
    # Get case - use correct function name from Phase 2
    case = await crud.get_case_by_id(db, case_id)
    if not case:
        raise HTTPException(
            status_code=404,
            detail="Case not found"
        )
    
    # Check if analysis is completed
    if case.status == "PENDING":
        raise HTTPException(
            status_code=400,
            detail="Analysis not complete. Please complete the analysis first."
        )
    
    if case.status == "PROCESSING":
        raise HTTPException(
            status_code=400,
            detail="Analysis in progress. Please wait for completion."
        )
    
    if case.status == "FAILED":
        raise HTTPException(
            status_code=400,
            detail="Analysis failed. Cannot provide guidance for failed analysis."
        )
    
    # Check if analysis result exists
    if not case.analysis_result:
        raise HTTPException(
            status_code=400,
            detail="No analysis results available"
        )
    
    try:
        # Generate guidance
        guidance = ComplaintGuidanceService.get_guidance(case)
        return guidance
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate guidance: {str(e)}"
        )