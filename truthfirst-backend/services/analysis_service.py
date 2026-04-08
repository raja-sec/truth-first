"""
Analysis Service - Orchestrates Multi-Modal Detection
Routes content to appropriate detectors and aggregates results
"""
from database.models import Case, CaseType
from services.model_loader import get_image_detector
# from models.email_detector import get_email_detector
from models.url_detector import get_url_detector
from services.file_handler import file_handler
from utils.constants import VERDICT_GENUINE, get_fake_verdict, MODALITY_IMAGE
import logging
import base64
from services.model_loader import model_loader
from utils.constants import MODALITY_VIDEO


logger = logging.getLogger(__name__)


class AnalysisService:
    """Orchestrate multi-modal analysis"""
    
    def __init__(self):
        self.image_detector = None
        self.email_detector = None
        self.url_detector = None
    
    def _ensure_detectors_loaded(self):
        if self.image_detector is None:
            self.image_detector = get_image_detector()
            logger.info("✅ Image detector loaded")

        # if self.email_detector is None:
        #     self.email_detector = get_email_detector()
        #     logger.info("✅ Email detector loaded (stub)")

        if self.url_detector is None:
            self.url_detector = get_url_detector()
            logger.info("✅ URL detector loaded")


        # ✅ ADD THIS
        if not hasattr(self, "video_detector"):
            if model_loader.is_video_available():
                self.video_detector = model_loader.load_video_detector()
                logger.info("✅ Video detector loaded")
            else:
                self.video_detector = None
                logger.warning("⚠️ Video detector unavailable (model missing)")

    
    async def analyze_case(self, case: Case) -> dict:
        """
        Analyze a case based on its type.
        
        Args:
            case: Case object from database
        
        Returns:
            dict with analysis results
        """
        self._ensure_detectors_loaded()
        
        logger.info(f"🔍 Analyzing case {case.id} (type: {case.case_type})")
        
        try:
            if case.case_type == CaseType.IMAGE:
                return await self._analyze_image(case)
            elif case.case_type == CaseType.EMAIL:
                return await self._analyze_email(case)
            elif case.case_type == CaseType.URL:
                return await self._analyze_url(case)
            elif case.case_type == CaseType.VIDEO:   # ✅ ADD
                return await self._analyze_video(case)
            else:
                raise ValueError(f"Unknown case type: {case.case_type}")

        
        except Exception as e:
            logger.error(f"❌ Analysis failed for case {case.id}: {e}")
            raise
    
    async def _analyze_image(self, case: Case) -> dict:
        """Analyze image case"""
        logger.info(f"🖼️  Analyzing image: {case.file_path}")
        
        # Read image file
        image_bytes = await file_handler.read_file(case.file_path)
        
        # Run image detector
        raw_result = self.image_detector.analyze(image_bytes)
        
        # Check for errors
        if "error" in raw_result:
            raise ValueError(f"Image analysis error: {raw_result['error']}")
        
        # Normalize result
        normalized = self._normalize_image_result(raw_result)
        
        # Aggregate (single modality, so just return it)
        aggregated = {
            "overall_verdict": normalized["verdict"],
            "overall_confidence": normalized["confidence"],
            "overall_risk_score": normalized["risk_score"],
            "image_result": normalized,
            "email_result": None,
            "url_result": None,
            "flags": normalized["flags"],
            "recommendations": self._generate_recommendations(normalized),
        }
        
        return aggregated
    
    
    async def _analyze_video(self, case: Case) -> dict:
        """Analyze video case"""
        logger.info(f"🎬 Analyzing video: {case.file_path}")

        if not self.video_detector:
            raise RuntimeError("Video analysis unavailable")

        # Run video detector
        result = self.video_detector.analyze(case.file_path)

        if result.get("status") == "error":
            raise ValueError(result.get("reason", "Video analysis failed"))

        # Normalize
        verdict = result["verdict"]
        confidence_norm = result["confidence"] / 100.0
        risk_score = int(result["confidence"])

        normalized = {
            "modality": MODALITY_VIDEO,
            "verdict": verdict,
            "confidence": confidence_norm,
            "risk_score": risk_score,
            "frames_analyzed": result["frames_analyzed"],
            "fake_probability": result["fake_probability"],
        }

        aggregated = {
            "overall_verdict": verdict,
            "overall_confidence": confidence_norm,
            "overall_risk_score": risk_score,
            "image_result": None,
            "email_result": None,
            "url_result": None,
            "video_result": normalized,
            "flags": self._generate_video_flags(result),
            "recommendations": self._generate_recommendations(normalized),
        }

        return aggregated

    async def _analyze_email(self, case: Case) -> dict:
        """
        Analyze email case using EmailDetector (BERT + URL + Headers).
        Supports:
        - .eml file uploads
        - pasted email text
        """
        logger.info("📧 Analyzing email content")

        # Load email detector via ModelLoader
        detector = model_loader.load_email_detector()
        
        if case.file_path:
            ext = case.file_path.lower()

            if ext.endswith((".png", ".jpg", ".jpeg", ".webp")):
                content = case.file_path
                content_type = "image"
            else:
                content = case.file_path
                content_type = "file"
        else:
            content = case.content_text
            content_type = "text"


        if not content:
            return {
                "overall_verdict": "UNKNOWN",
                "overall_confidence": 0.0,
                "overall_risk_score": 0,
                "image_result": None,
                "email_result": None,
                "url_result": None,
                "flags": ["No email content provided"],
                "recommendations": ["Provide email content for analysis"],
            }

        # Run detection
        result = detector.analyze(content, content_type)

        verdict = result.get("verdict", "GENUINE")
        confidence = result.get("confidence", 0.5)
        risk_score = result.get("risk_score", 0)

        aggregated = {
            "overall_verdict": verdict,
            "overall_confidence": confidence,
            "overall_risk_score": risk_score,
            "image_result": None,
            "email_result": result,
            "url_result": None,
            "flags": self._generate_email_flags(result),
            "recommendations": self._generate_recommendations(result),
        }

        return aggregated
    
    async def _analyze_url(self, case: Case) -> dict:
        """Analyze URL case"""
        logger.info(f"🔗 Analyzing URL: {case.content_text}")
        
        # Get URL (from content_text field)
        url = case.content_text or ""
        
        # Run URL detector (stub)
        result = self.url_detector.analyze(url)
        
    
        
        aggregated = {
            "overall_verdict": result["verdict"],
            "overall_confidence": result["confidence"],
            "overall_risk_score": result["risk_score"],
            "image_result": None,
            "email_result": None,
            "url_result": result,
            "flags": result.get("flags", []),
            "recommendations": self._generate_recommendations(result),
        }

        
        return aggregated
    
    def _normalize_image_result(self, raw_result: dict) -> dict:
        """Normalize ImageDetector output to unified schema"""
        from schemas.detection import ImageMetrics
        
        # Map internal verdict to user-facing
        internal_verdict = raw_result["verdict"]
        
        if internal_verdict == "REAL":
            user_verdict = VERDICT_GENUINE
        else:  # FAKE
            user_verdict = get_fake_verdict(MODALITY_IMAGE)  # Returns "DEEPFAKE"
        
        # Convert confidence
        confidence_normalized = raw_result["confidence"] / 100.0
        risk_score = int(raw_result["confidence"])
        
        # Build explanation
        if user_verdict == VERDICT_GENUINE:
            explanation = f"Image appears authentic with {raw_result['confidence']:.1f}% confidence. No significant manipulation detected."
        else:
            explanation = f"Image shows signs of deepfake manipulation with {raw_result['confidence']:.1f}% confidence. Multiple forensic indicators detected."
        
        # Base64 encode Grad-CAM
        grad_cam_base64 = base64.b64encode(raw_result["heatmap_bytes"]).decode("utf-8")
        
        return {
            "modality": MODALITY_IMAGE,
            "verdict": user_verdict,
            "confidence": confidence_normalized,
            "risk_score": risk_score,
            "factors": {
                "cnn_fake": raw_result["metrics"]["cnn_fake"],
                "frequency_score": raw_result["metrics"]["freq"],
                "artifact_score": raw_result["metrics"]["art"],
            },
            "flags": raw_result["flags"],
            "explanation": explanation,
            "grad_cam_base64": grad_cam_base64,
            "face_found": raw_result["face_found"],
        }
    
    # def _generate_recommendations(self, result: dict) -> list[str]:
    #     """Generate action recommendations based on verdict"""
    #     recommendations = []
        
    #     if result["verdict"] == "DEEPFAKE/PHISHING":
    #         recommendations.extend([
    #             "Do not trust this content",
    #             "Report to appropriate authorities",
    #             "Verify through alternative sources",
    #         ])
    #     else:
    #         recommendations.append("Content appears legitimate, but always exercise caution")
        
    #     return recommendations
    
    def _generate_video_flags(self, result: dict) -> list[str]:
        flags = []

        if result["verdict"] == "DEEPFAKE":
            if result["confidence"] >= 85:
                flags.append("High confidence deepfake detected")
            else:
                flags.append("Temporal inconsistencies detected")

            if result["frames_analyzed"] < 30:
                flags.append("Limited face visibility")

        return flags
    
    
    def _generate_email_flags(self, result: dict) -> list[str]:
        flags = result.get("flags", []).copy()
        factors = result.get("factors", {})

        if result.get("verdict") == "PHISHING":
            if factors.get("body_text_analysis", 0) >= 80:
                flags.append("High-risk language detected by AI analysis")

            if factors.get("header_anomalies", 0) >= 50:
                flags.append("Email authentication anomalies detected")

            if factors.get("link_risk", 0) >= 85:
                flags.append("Confirmed malicious links found")

        extracted = result.get("extracted_data", {})
        if extracted.get("urls_found", 0) > 5:
            flags.append("Unusually high number of links in email")

        return flags



    def _generate_recommendations(self, result: dict) -> list[str]:
        # """Generate action recommendations based on verdict"""
        verdict = result.get("verdict", "")

        if verdict in ["DEEPFAKE", "PHISHING"]:
            return [
                "Do not trust or share this content",
                "Avoid engaging with the source",
                "Preserve evidence if harm occurred",
                "Report the content to the relevant platform or authorities",
            ]

        if verdict == VERDICT_GENUINE:
            return [
                "Content appears legitimate",
                "Still verify the original source when possible",
                "Exercise normal caution before sharing",
            ]

        return []


# Global service instance
analysis_service = AnalysisService()