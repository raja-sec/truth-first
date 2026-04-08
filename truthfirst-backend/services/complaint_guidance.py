"""
Complaint Guidance Service
Provides legally safe guidance for filing cyber crime complaints.

CRITICAL: This service provides GUIDANCE ONLY, never pre-filled complaints.
User is always responsible for their own complaint content.
"""

from typing import Dict, Any, Optional
from database.models import Case, CaseType, CaseStatus


class ComplaintGuidanceService:
    """Service for generating legally safe complaint guidance."""
    
    @staticmethod
    def get_guidance(case: Case) -> Dict[str, Any]:
        """
        Generate complaint guidance for a case.
        
        Args:
            case: Case object with analysis results
            
        Returns:
            Dictionary with structured guidance
        """
        # Extract case details
        case_type = case.case_type
        analysis = case.analysis_result or {}
        
        # Extract verdict from nested structure
        verdict = analysis.get('overall_verdict', 'UNKNOWN')
        file_hash = analysis.get('file_hash', 'N/A')
        
        # Determine verdict category
        verdict_category = ComplaintGuidanceService._get_verdict_category(
            case_type, verdict
        )
        
        # Get finding summary
        finding_summary = ComplaintGuidanceService._get_finding_summary(
            case_type, verdict
        )
        
        # Build guidance structure
        guidance = {
            "case_id": case.id,
            "case_type": case_type,
            "analysis_type": ComplaintGuidanceService._get_analysis_type(case_type),
            "verdict_category": verdict_category,
            "finding_summary": finding_summary,
            
            "guidance": {
                "title": "Report to Cyber Crime Portal",
                "warning_header": ComplaintGuidanceService._get_warning_header(),
                "our_analysis": ComplaintGuidanceService._get_our_analysis(
                    case.id, finding_summary, file_hash
                ),
                "when_to_report": ComplaintGuidanceService._get_when_to_report(
                    verdict_category
                ),
                "when_not_to_report": ComplaintGuidanceService._get_when_not_to_report(),
                "legal_responsibility": ComplaintGuidanceService._get_legal_responsibility(),
                "how_to_file": ComplaintGuidanceService._get_how_to_file(),
                "examples": ComplaintGuidanceService._get_examples(verdict_category),
                "resources": ComplaintGuidanceService._get_resources(),
                "disclaimer": ComplaintGuidanceService._get_disclaimer()
            },
            
            "actions": {
                "cybercrime_portal_url": "https://cybercrime.gov.in/",
                "pdf_report_url": f"/api/report/{case.id}/pdf",
                "file_hash": file_hash,
                "modal_action": "close"
            }
        }
        
        return guidance
    
    @staticmethod
    def _get_verdict_category(case_type: str, verdict: str) -> str:
        """Map verdict to user-friendly category."""
        if case_type == "IMAGE":
            return "deepfake" if verdict == "DEEPFAKE" else "genuine"
        elif case_type in ["EMAIL", "URL"]:
            return "phishing" if verdict == "PHISHING" else "genuine"
        return "unknown"
    
    @staticmethod
    def _get_analysis_type(case_type: str) -> str:
        """Get analysis type label."""
        if case_type == "IMAGE":
            return "deepfake"
        elif case_type == "EMAIL":
            return "phishing"
        elif case_type == "URL":
            return "malicious_url"
        return "unknown"
    
    @staticmethod
    def _get_finding_summary(case_type: str, verdict: str) -> str:
        """Generate finding summary based on case type and verdict."""
        if case_type == "IMAGE":
            if verdict == "DEEPFAKE":
                return "Image shows signs of AI manipulation"
            else:
                return "Image appears authentic"
        elif case_type == "EMAIL":
            if verdict == "PHISHING":
                return "Email shows signs of phishing attempt"
            else:
                return "Email appears legitimate"
        elif case_type == "URL":
            if verdict == "PHISHING":
                return "URL shows signs of malicious intent"
            else:
                return "URL appears safe"
        return "Analysis completed"
    
    @staticmethod
    def _get_warning_header() -> Dict[str, Any]:
        """Get warning header content."""
        return {
            "text": "This is a GUIDE to help you file a complaint with cybercrime.gov.in if you choose to do so.",
            "emphasis": [
                "TruthFirst does not file complaints on your behalf",
                "You are solely responsible for the accuracy of your complaint",
                "False reports are prosecutable under Indian Penal Code"
            ]
        }
    
    @staticmethod
    def _get_our_analysis(case_id: str, finding: str, file_hash: str) -> Dict[str, Any]:
        """Get our analysis section."""
        return {
            "label": "TruthFirst Analysis (For Your Reference Only)",
            "case_id": case_id,
            "finding": finding,
            "file_hash": file_hash if file_hash != 'N/A' else None,
            "file_hash_label": "File Fingerprint (for evidence integrity)",
            "note": "This is NOT legal proof or evidence. Use only as supporting information."
        }
    
    @staticmethod
    def _get_when_to_report(verdict_category: str) -> Dict[str, Any]:
        """Get when to report checklist."""
        conditional_note = ""
        if verdict_category in ["deepfake", "phishing"]:
            conditional_note = f"Since we found signs of {verdict_category}, report only if:"
        else:
            conditional_note = "Reporting content we found GENUINE may result in dismissal. Only report if you have strong evidence of misrepresentation."
        
        return {
            "title": "Only Report If:",
            "conditional_note": conditional_note,
            "checklist": [
                "You found this content yourself (not uploaded just to test our tool)",
                "You know HOW and WHERE you found it",
                "It caused actual harm or is being widely shared",
                "You can describe the ACTUAL INCIDENT in detail",
                "You have evidence beyond our analysis (screenshots, URLs, dates, etc.)"
            ]
        }
    
    @staticmethod
    def _get_when_not_to_report() -> Dict[str, Any]:
        """Get when NOT to report checklist."""
        return {
            "title": "Do NOT Report If:",
            "checklist": [
                "You're just testing our AI detection service",
                "It's a private or personal copy with no circulation",
                "No actual harm occurred to anyone",
                "You cannot provide accurate information about where/how you found it"
            ]
        }
    
    @staticmethod
    def _get_legal_responsibility() -> Dict[str, Any]:
        """Get legal responsibility section."""
        return {
            "title": "Your Legal Responsibility",
            "points": [
                "YOU are responsible for complaint accuracy and content",
                "YOU may face legal action for false or misleading reports",
                "WE are NOT responsible for your complaint or its outcome",
                "WE do not endorse any complaint you file",
                "OUR analysis is a tool output, not legal proof or evidence"
            ]
        }
    
    @staticmethod
    def _get_how_to_file() -> Dict[str, Any]:
        """Get step-by-step filing instructions."""
        return {
            "title": "How to File a Complaint",
            "steps": [
                {
                    "step": 1,
                    "action": "Gather YOUR evidence",
                    "details": [
                        "Original image/video/email you found",
                        "Screenshot of where you found it",
                        "Date and time you found it",
                        "Platform details (URL, username, post ID)",
                        "Any related communications (messages, emails)",
                        "Documentation of harm caused (if applicable)"
                    ]
                },
                {
                    "step": 2,
                    "action": "Visit cybercrime.gov.in",
                    "details": [
                        "Register with your phone number (OTP verification)",
                        "Select 'Report Other Cybercrimes'",
                        "Fill in YOUR personal details accurately"
                    ]
                },
                {
                    "step": 3,
                    "action": "Write YOUR complaint description",
                    "details": [
                        "Describe the incident in YOUR OWN WORDS",
                        "Include where, when, and how you found the content",
                        "Explain the impact or harm (if any)",
                        "You may mention: 'Technical analysis suggested potential manipulation'",
                        "Do NOT copy our verdict or confidence as fact"
                    ]
                },
                {
                    "step": 4,
                    "action": "Upload YOUR evidence and submit",
                    "details": [
                        "Upload the original content YOU found",
                        "Upload screenshots of where it appeared",
                        "Optionally: Our PDF report as reference (not as evidence)",
                        "Include file hash from our analysis if relevant",
                        "Submit your complaint"
                    ]
                }
            ]
        }
    
    @staticmethod
    def _get_examples(verdict_category: str) -> Dict[str, Any]:
        """Get good vs bad complaint examples."""
        content_type = "image" if verdict_category == "deepfake" else "content"
        issue_type = "artificial creation" if verdict_category == "deepfake" else "malicious intent"
        
        return {
            "good_complaint": {
                "label": "Example of GOOD Complaint Description",
                "text": f"I found a suspicious {content_type} on [PLATFORM NAME] on [DATE]. The {content_type} appears to show [DESCRIPTION]. When analyzed with AI detection tools, it showed signs of {issue_type}. This content has been [shared widely / affected me in this way]. I am reporting this for investigation.",
                "why_good": "You describe YOUR discovery and YOUR evidence, mentioning AI analysis only as supporting information"
            },
            "bad_complaint": {
                "label": "Example of BAD Complaint Description",
                "text": f"TruthFirst AI detected this as {verdict_category} with 92.3% confidence. Their analysis shows CNN model detected artifacts and technical indicators of manipulation.",
                "why_bad": "You're citing US as the authority instead of describing YOUR evidence and YOUR discovery"
            }
        }
    
    @staticmethod
    def _get_resources() -> Dict[str, Any]:
        """Get helpful resources links."""
        return {
            "title": "Helpful Resources",
            "links": [
                {
                    "label": "Official Cybercrime Portal",
                    "url": "https://cybercrime.gov.in/",
                    "note": "Go here to file your complaint"
                },
                {
                    "label": "FAQ & Guidelines",
                    "url": "https://cybercrime.gov.in/FAQ",
                    "note": "Read before filing"
                },
                {
                    "label": "Evidence Requirements",
                    "url": "https://cybercrime.gov.in/FAQ",
                    "note": "What evidence to attach"
                }
            ]
        }
    
    @staticmethod
    def _get_disclaimer() -> Dict[str, Any]:
        """Get legal disclaimer."""
        return {
            "title": "Important Legal Disclaimer",
            "points": [
                "TruthFirst provides AI-powered analysis tools only",
                "Our analysis has 92.8% accuracy on test data but is not infallible",
                "This is NOT a legal determination or court-admissible evidence",
                "We make no guarantees about detection accuracy in your specific case",
                "Consult legal counsel for serious matters",
                "Respect privacy and legal rights of all individuals",
                "Use our tools responsibly and ethically"
            ]
        }