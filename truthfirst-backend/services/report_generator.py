"""
Report Generator Service
Generates PDF reports for case analysis results.
"""

import os
import io
import hashlib
import base64
from datetime import datetime, timezone
from zoneinfo import ZoneInfo   # Python 3.9+
from typing import Optional, Dict, Any
from pathlib import Path
from jinja2 import Template
from weasyprint import HTML
from database.models import Case
from services.chart_generator import ChartGenerator
import logging
from weasyprint.text.fonts import FontConfiguration

logging.getLogger("fontTools").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

class ReportGenerator:
    """Service for generating PDF reports."""
    
    TEMPLATE_DIR = Path(__file__).parent / "pdf_templates"
    
    # GLOBAL font config (reused across all PDFs)
    FONT_CONFIG = FontConfiguration()
    
    @staticmethod
    def generate_pdf(case: Case) -> bytes:
        """
        Generate PDF report for a case.
        """
        # Prepare template data
        template_data = ReportGenerator._prepare_template_data(case)
        
        # Load and render template
        template_path = ReportGenerator.TEMPLATE_DIR / "report_base.html"
        with open(template_path, 'r', encoding='utf-8') as f:
            template = Template(f.read())
        
        html_content = template.render(**template_data)
        
        try:
            # Set base_url so WeasyPrint knows where to look for local assets
            base_url = str(Path(__file__).resolve().parent.parent)
            
            pdf_bytes = HTML(string=html_content, base_url=base_url).write_pdf(
                font_config=ReportGenerator.FONT_CONFIG
            )
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"❌ WeasyPrint failed to generate PDF: {str(e)}")
            
            # Fallback to reportlab if WeasyPrint crashes in Docker
            try:
                from reportlab.pdfgen import canvas
                
                logger.warning("⚠️ Attempting to generate fallback PDF...")
                packet = io.BytesIO()
                c = canvas.Canvas(packet)
                
                # Draw basic fallback report
                c.setFont("Helvetica-Bold", 16)
                c.drawString(50, 800, "TruthFirst Analysis Report (Fallback Mode)")
                
                c.setFont("Helvetica", 12)
                c.drawString(50, 770, f"Case ID: {case.id}")
                
                verdict = case.analysis_result.get('overall_verdict', 'UNKNOWN') if case.analysis_result else 'UNKNOWN'
                confidence = case.analysis_result.get('overall_confidence', 0.0) if case.analysis_result else 0.0
                
                c.drawString(50, 740, f"Verdict: {verdict}")
                c.drawString(50, 720, f"Confidence: {int(confidence * 100)}%")
                c.drawString(50, 700, f"Case Type: {case.case_type}")
                
                c.setFont("Helvetica-Oblique", 10)
                c.drawString(50, 650, "Note: Full graphical PDF generation failed due to container limitations.")
                c.drawString(50, 635, "Basic analysis data has been recovered above.")
                
                c.save()
                packet.seek(0)
                return packet.read()
                
            except Exception as backup_error:
                logger.error(f"❌ Fallback PDF also failed: {backup_error}")
                raise RuntimeError(f"PDF Generation Failed completely: {str(e)}")

    @staticmethod
    def _prepare_template_data(case: Case) -> Dict[str, Any]:
        """Prepare data for PDF template."""
        analysis = case.analysis_result or {}
        
        # Extract core data from NESTED structure (Phase 2 format)
        verdict = analysis.get('overall_verdict', 'UNKNOWN')
        confidence = analysis.get('overall_confidence', 0.0)
        risk_score = analysis.get('overall_risk_score', 0)
        
        # Extract from image_result if present
        image_result = analysis.get('image_result', {})
        flags = image_result.get('flags', []) if image_result else []
        explanation = image_result.get('explanation', 'No explanation available') if image_result else 'No explanation available'
        recommendations = analysis.get('recommendations', [])
        
        # Get file hash - calculate if not in analysis
        if 'file_hash' in analysis:
            file_hash = analysis['file_hash']
        else:
            file_hash = ReportGenerator._calculate_file_hash(case.file_path) if case.file_path else 'N/A'
        
        # Generate confidence chart
        chart_base64 = ChartGenerator.generate_confidence_gauge(
            confidence, verdict
        )
        
        # Get Grad-CAM (if available) - from image_result
        grad_cam_base64 = None
        if image_result:
            grad_cam_base64 = image_result.get('grad_cam_base64')
            
        # Get original image as base64 (for IMAGE cases)
        original_image_base64 = None
        if case.case_type == "IMAGE" and case.file_path:
            try:
                original_image_base64 = ReportGenerator._image_to_base64(case.file_path)
            except Exception:
                original_image_base64 = None

        # Format timestamps (UTC → IST)
        ist = ZoneInfo("Asia/Kolkata")

        def utc_to_ist(dt):
            if not dt:
                return 'N/A'

            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)

            return dt.astimezone(ist).strftime('%Y-%m-%d %H:%M:%S IST')


        analyzed_at = utc_to_ist(case.analyzed_at)
        created_at = utc_to_ist(case.created_at)

        
        # Get colors for verdict
        verdict_color = ReportGenerator._get_verdict_color(verdict)
        verdict_bg_color = ReportGenerator._get_verdict_bg_color(verdict)
        
        # Legend items (must match chart colors exactly)
        if verdict in ["DEEPFAKE", "PHISHING"]:
            legend_items = [
                {"label": "Deepfake", "color": "#ef4444"},
                {"label": "Genuine", "color": "#b8edc8"},
            ]
        else:
            legend_items = [
                {"label": "Genuine", "color": "#10b981"},
                {"label": "Risk", "color": "#edbaba"},
            ]

        
        # Build template data
        data = {
            'legend_items': legend_items,
            
            # Original image
            'original_image_base64': original_image_base64,
            
            # Header
            'case_id': case.id,
            'analyzed_at': analyzed_at,
            'created_at': created_at,
            'generated_at': datetime.now(tz=ist).strftime('%Y-%m-%d %H:%M:%S IST'),
            
            # Verdict
            'verdict': verdict,
            'confidence': confidence,
            'confidence_percent': int(confidence * 100),
            'risk_score': risk_score,
            'chart_base64': chart_base64,
            
            # Case details
            'case_type': case.case_type,
            'case_source': case.case_source or 'N/A',
            'case_description': case.case_description or 'N/A',
            'user_name': case.user_name,
            'user_email': case.user_email,
            
            # Analysis details
            'flags': flags,
            'explanation': explanation,
            'recommendations': recommendations,
            
            # Technical metadata
            'file_name': case.file_name or 'N/A',
            'file_size': ReportGenerator._format_file_size(case.file_size) if case.file_size else 'N/A',
            'file_hash': file_hash,
            'model_version': 'EfficientNet-B0 Hybrid Ensemble v1.0',
            
            # Grad-CAM
            'grad_cam_base64': grad_cam_base64,
            'has_grad_cam': grad_cam_base64 is not None,
            
            # Colors for styling (PRE-RENDERED, not Jinja in CSS)
            'verdict_color': verdict_color,
            'verdict_bg_color': verdict_bg_color,
            
            # Plain English explanation
            'plain_explanation': ReportGenerator._get_plain_explanation(
                verdict, confidence, case.case_type
            ),
            'action_recommendation': ReportGenerator._get_action_recommendation(
                verdict, case.case_type
            )
        }
        
        return data
    
    @staticmethod
    def _calculate_file_hash(file_path: str) -> str:
        """Calculate SHA-256 hash of file."""
        if not file_path or not os.path.exists(file_path):
            return 'N/A'
        
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return f"sha256:{sha256_hash.hexdigest()}"
        except Exception as e:
            return f'Error: {str(e)}'
    
    @staticmethod
    def _format_file_size(size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    @staticmethod
    def _get_verdict_color(verdict: str) -> str:
        """Get color for verdict."""
        if verdict in ['DEEPFAKE', 'PHISHING']:
            return '#ef4444'  # Red
        elif verdict == 'GENUINE':
            return '#10b981'  # Green
        else:
            return '#6b7280'  # Gray
    
    @staticmethod
    def _get_verdict_bg_color(verdict: str) -> str:
        """Get background color for verdict."""
        if verdict in ['DEEPFAKE', 'PHISHING']:
            return '#fef2f2'  # Light red
        elif verdict == 'GENUINE':
            return '#f0fdf4'  # Light green
        else:
            return '#f9fafb'  # Light gray
    
    @staticmethod
    def _get_plain_explanation(verdict: str, confidence: float, case_type: str) -> str:
        """Generate plain English explanation."""
        confidence_level = "high" if confidence > 0.8 else "moderate" if confidence > 0.5 else "low"
        
        if case_type == "IMAGE":
            if verdict == "DEEPFAKE":
                return f"This image shows clear signs of artificial creation with {confidence_level} confidence ({int(confidence * 100)}%). The AI detected multiple indicators of AI generation including unnatural patterns and manipulation artifacts. This is likely created using deepfake technology."
            else:
                return f"No signs of artificial manipulation detected with {confidence_level} confidence ({int(confidence * 100)}%). The image appears authentic. However, no AI system is 100% accurate. Always verify with source when possible."
        
        elif case_type == "EMAIL":
            if verdict == "PHISHING":
                return f"This email shows signs of a phishing attempt with {confidence_level} confidence ({int(confidence * 100)}%). Multiple suspicious indicators were detected. Do not click links or provide personal information."
            else:
                return f"This email appears legitimate with {confidence_level} confidence ({int(confidence * 100)}%). However, always verify sender identity and be cautious with sensitive information."
        
        elif case_type == "URL":
            if verdict == "PHISHING":
                return f"This URL shows signs of malicious intent with {confidence_level} confidence ({int(confidence * 100)}%). Do not visit this link or provide any information on the site."
            else:
                return f"This URL appears safe with {confidence_level} confidence ({int(confidence * 100)}%). However, always exercise caution when visiting unfamiliar websites."
        
        return "Analysis completed. Review the technical details for more information."
    
    @staticmethod
    def _get_action_recommendation(verdict: str, case_type: str) -> str:
        """Get recommended actions."""
        if verdict in ['DEEPFAKE', 'PHISHING']:
            actions = [
                "Do not share or trust this content",
                "Report to relevant platforms if found on social media",
                "Preserve evidence for authorities if harm occurred",
                "Consider filing complaint on cybercrime.gov.in if content is widely circulated or caused harm",
                "Alert others who may have been exposed to this content"
            ]
        else:
            actions = [
                "Content appears genuine, but verify with original source when possible",
                "Exercise normal caution when sharing or using this content",
                "If you have doubts, seek additional verification",
                "Report if you later discover this was misrepresented"
            ]
        
        return "\n".join(f"• {action}" for action in actions)
    
    @staticmethod
    def _image_to_base64(image_path: str) -> str:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")