 
"""
        TruthFirst Email Phishing Detector Adapter

        This adapter wraps the standalone email phishing detection module
        and integrates it with TruthFirst's unified analysis pipeline.

        Architecture:
        - BERT NLP analysis for semantic understanding
        - Multi-source URL threat intelligence (reuses URL module)
        - Email header forensics (SPF, DKIM, spoofing checks)
        - Keyword and behavioral heuristics
        - Dynamic risk fusion engine

        Verdict logic: GENUINE or PHISHING (threshold: 60% risk)
        """

import logging
import json
from models.email_detection.email_security_module import PhishingDetector

logger = logging.getLogger(__name__)


class EmailDetector:
            """
            Email Phishing Detection using BERT + Threat Intelligence + Forensics.
            
            Integrates standalone email detection module into TruthFirst backend.
            Maintains compatibility with TruthFirst's response schema.
            """
            
            def __init__(self, model_path: str):
                """
                Initialize email detector with BERT model.
                
                Args:
                    model_path: Path to fine-tuned BERT model directory
                    
                Note:
                    - Model is loaded once at initialization (singleton pattern)
                    - URL detection module is reused from existing infrastructure
                    - Supports both .eml file parsing and raw text analysis
                """
                try:
                    self.detector = PhishingDetector(model_path)
                    logger.info(f"✅ Email Detector initialized with model: {model_path}")
                except Exception as e:
                    logger.error(f"❌ Failed to initialize Email Detector: {e}")
                    raise RuntimeError(f"Email detector initialization failed: {e}")
            
            def analyze(self, content: str, content_type: str = "text") -> dict:
                """
                Analyze email content for phishing indicators.
                
                Args:
                    content: Email content (raw text or file path)
                    content_type: "text" for pasted content, "file" for .eml path
                    
                Returns:
                    dict with keys:
                        - verdict: "GENUINE" or "PHISHING"
                        - confidence: float (0.0-1.0)
                        - risk_score: int (0-100)
                        - factors: dict with analysis breakdown
                        - flags: list of detected issues
                        - explanation: plain English summary
                        
                Processing Pipeline:
                    1. Parse email (headers + body)
                    2. Extract and scan URLs (VirusTotal, GSB, URLScan)
                    3. BERT semantic analysis
                    4. Header forensics (SPF, DKIM, spoofing)
                    5. Keyword heuristics
                    6. Dynamic risk fusion
                """
                try:
                    # Call standalone email security module
                    result_json = self.detector.analyze(content, input_type=content_type)
                    result = json.loads(result_json)
                    
                    # Validate response structure
                    required_keys = ["verdict", "confidence", "risk_score", "factors", "flags", "explanation"]
                    missing_keys = [k for k in required_keys if k not in result]
                    
                    if missing_keys:
                        logger.error(f"Invalid email analysis response. Missing keys: {missing_keys}")
                        return self._error_response("Invalid analysis response format")
                    
                    # Log result for monitoring
                    verdict = result.get("verdict", "UNKNOWN")
                    risk = result.get("risk_score", 0)
                    logger.info(f"Email analysis complete: {verdict} (risk: {risk})")
                    
                    return result
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse email analysis JSON: {e}")
                    return self._error_response("JSON parsing failed")
                
                except Exception as e:
                    logger.error(f"Email analysis failed: {e}", exc_info=True)
                    return self._error_response(str(e))
            
            def _error_response(self, error_msg: str) -> dict:
                """
                Generate safe fallback response on error.
                
                Args:
                    error_msg: Error description
                    
                Returns:
                    dict with GENUINE verdict (conservative fallback) and error flag
                """
                return {
                    "modality": "email",
                    "verdict": "GENUINE",
                    "confidence": 0.5,
                    "risk_score": 0,
                    "factors": {
                        "body_text_analysis": 0,
                        "header_anomalies": 0,
                        "link_risk": 0,
                        "keyword_risk": 0
                    },
                    "flags": [f"Analysis error: {error_msg}"],
                    "extracted_data": {
                        "sender": "Unknown",
                        "subject": "Unknown",
                        "urls_found": 0
                    },
                    "explanation": "Unable to complete email analysis. Treat with caution."
                }
            
            def batch_analyze(self, emails: list, content_type: str = "text") -> list:
                """
                Analyze multiple emails (useful for batch processing).
                
                Args:
                    emails: List of email contents (text or file paths)
                    content_type: "text" or "file"
                    
                Returns:
                    List of analysis results (same format as analyze())
                """
                results = []
                for email in emails:
                    result = self.analyze(email, content_type)
                    results.append(result)
                return results
            
        # Global singleton instance (lazy-loaded)
_email_detector = None


def get_email_detector():
            """
            Get or create EmailDetector instance.
            Ensures BERT model is loaded only once.
            """
            global _email_detector

            if _email_detector is None:
                from config import settings

                logger.info("🔄 Initializing EmailDetector (lazy load)...")
                _email_detector = EmailDetector(
                    model_path=settings.EMAIL_MODEL_PATH
                )

            return _email_detector