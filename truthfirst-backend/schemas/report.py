"""
Report API Schemas
Pydantic models for report endpoints.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class WarningHeader(BaseModel):
    """Warning header for complaint guidance."""
    text: str
    emphasis: List[str]


class OurAnalysis(BaseModel):
    """Our analysis section."""
    label: str
    case_id: str
    finding: str
    file_hash: Optional[str] = None
    file_hash_label: str
    note: str


class WhenToReport(BaseModel):
    """When to report checklist."""
    title: str
    conditional_note: str
    checklist: List[str]


class WhenNotToReport(BaseModel):
    """When NOT to report checklist."""
    title: str
    checklist: List[str]


class LegalResponsibility(BaseModel):
    """Legal responsibility section."""
    title: str
    points: List[str]


class FilingStep(BaseModel):
    """Single step in filing process."""
    step: int
    action: str
    details: List[str]


class HowToFile(BaseModel):
    """How to file instructions."""
    title: str
    steps: List[FilingStep]


class ComplaintExample(BaseModel):
    """Example complaint."""
    label: str
    text: str
    why_good: Optional[str] = None
    why_bad: Optional[str] = None


class Examples(BaseModel):
    """Good vs bad examples."""
    good_complaint: ComplaintExample
    bad_complaint: ComplaintExample


class ResourceLink(BaseModel):
    """Resource link."""
    label: str
    url: str
    note: str


class Resources(BaseModel):
    """Helpful resources."""
    title: str
    links: List[ResourceLink]


class Disclaimer(BaseModel):
    """Legal disclaimer."""
    title: str
    points: List[str]


class GuidanceContent(BaseModel):
    """Main guidance content."""
    title: str
    warning_header: WarningHeader
    our_analysis: OurAnalysis
    when_to_report: WhenToReport
    when_not_to_report: WhenNotToReport
    legal_responsibility: LegalResponsibility
    how_to_file: HowToFile
    examples: Examples
    resources: Resources
    disclaimer: Disclaimer


class ComplaintGuidanceActions(BaseModel):
    """Actions for complaint guidance."""
    cybercrime_portal_url: str
    pdf_report_url: str
    file_hash: Optional[str] = None
    modal_action: str


class ComplaintGuidanceResponse(BaseModel):
    """Response for complaint guidance endpoint."""
    case_id: str
    case_type: str
    analysis_type: str
    verdict_category: str
    finding_summary: str
    guidance: GuidanceContent
    actions: ComplaintGuidanceActions
    
    class Config:
        json_schema_extra = {
            "example": {
                "case_id": "TF20251215-ABC123",
                "case_type": "IMAGE",
                "analysis_type": "deepfake",
                "verdict_category": "deepfake",
                "finding_summary": "Image shows signs of AI manipulation",
                "guidance": {
                    "title": "Report to Cyber Crime Portal",
                    "warning_header": {
                        "text": "This is a GUIDE...",
                        "emphasis": ["TruthFirst does not file complaints..."]
                    }
                },
                "actions": {
                    "cybercrime_portal_url": "https://cybercrime.gov.in/",
                    "pdf_report_url": "/api/report/TF20251215-ABC123/pdf",
                    "file_hash": "sha256:abc123...",
                    "modal_action": "close"
                }
            }
        }


class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    case_id: Optional[str] = None
    status: Optional[str] = None
    message: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Case not found",
                "case_id": "invalid-id"
            }
        }