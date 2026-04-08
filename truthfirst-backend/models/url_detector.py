"""
TruthFirst URL Detector Adapter

This adapter wraps the standalone URL phishing detection module
and integrates it with TruthFirst's unified analysis pipeline.

Architecture:
- Uses multi-API threat intelligence (Google Safe Browsing, VirusTotal, URLScan)
- Implements key pooling and rate limiting for VirusTotal
- In-memory caching with TTL (24h phishing, 1h clean)
- In-flight deduplication to prevent duplicate scans
- Returns verdicts: GENUINE, SUSPICIOUS, PHISHING
"""

import logging
from models.url_detection.vt_pool import VTKeyPool
from models.url_detection.scanner import scan_url

logger = logging.getLogger(__name__)


class URLDetector:
    """
    URL Phishing Detection using multi-source threat intelligence.
    
    Integrates standalone URL detection module into TruthFirst backend.
    Maintains compatibility with TruthFirst's response schema.
    """
    
    def __init__(self, vt_keys: list, gsb_key: str = None, urlscan_key: str = None):
        """
        Initialize URL detector with API keys.
        
        Args:
            vt_keys: List of VirusTotal API keys (supports key rotation)
            gsb_key: Google Safe Browsing API key (optional)
            urlscan_key: URLScan.io API key (optional)
            
        Note:
            - VirusTotal keys are pooled with rate limiting (4 req/min/key)
            - GSB and URLScan keys are loaded from environment if not provided
            - Module gracefully handles missing keys (partial scans)
        """
        # Initialize VirusTotal key pool
        valid_keys = [k for k in vt_keys if k]
        if not valid_keys:
            logger.warning("⚠️  No VirusTotal keys provided. URL detection will have limited accuracy.")
        
        self.vt_pool = VTKeyPool(valid_keys) if valid_keys else None
        
        # API keys are also loaded from environment in fetchers.py
        # This initialization is primarily for the VT pool
        logger.info(f"✅ URL Detector initialized with {len(valid_keys)} VirusTotal keys")
        
        if not gsb_key:
            logger.warning("⚠️  Google Safe Browsing key not configured")
        if not urlscan_key:
            logger.warning("⚠️  URLScan.io key not configured")
    
    def analyze(self, url: str) -> dict:
        """
        Analyze URL for phishing/malicious content.
        
        Args:
            url: URL to scan (e.g., "https://suspicious-site.com")
            
        Returns:
            dict with keys:
                - verdict: "GENUINE", "SUSPICIOUS", or "PHISHING"
                - confidence: float (0.0-1.0)
                - risk_score: int (0-100)
                - factors: dict with detection sources
                - flags: list of warnings/detections
                - explanation: plain English summary
                
        Architecture Notes:
            - Results are cached in RAM (24h for phishing, 1h for clean)
            - Duplicate concurrent requests are deduplicated
            - Max 5 parallel scans enforced via semaphore
            - Partial results returned if some APIs fail
        """
        try:
            # Call standalone scanner (handles caching, deduplication, rate limiting)
            result = scan_url(url, self.vt_pool)
            
            # Validate response structure
            if not result or "verdict" not in result:
                logger.error(f"Invalid scanner response for URL: {url}")
                return self._error_response("Scanner returned invalid response")
            
            # Log result for monitoring
            verdict = result.get("verdict", "UNKNOWN")
            risk = result.get("risk_score", 0)
            logger.info(f"URL scan complete: {url[:50]}... → {verdict} (risk: {risk})")
            
            return result
            
        except Exception as e:
            logger.error(f"URL analysis failed: {e}", exc_info=True)
            return self._error_response(str(e))
    
    def _error_response(self, error_msg: str) -> dict:
        """
        Generate safe fallback response on error.
        
        Args:
            error_msg: Error description
            
        Returns:
            dict with GENUINE verdict and error flag
        """
        return {
            "verdict": "GENUINE",
            "confidence": 0.5,
            "risk_score": 0,
            "factors": {
                "gsb_threat": None,
                "vt_malicious": 0,
                "urlscan_score": 0
            },
            "flags": [f"Analysis error: {error_msg}"],
            "explanation": "Unable to complete threat analysis. Treat with caution."
        }
    
    def batch_analyze(self, urls: list) -> list:
        """
        Analyze multiple URLs (useful for batch processing).
        
        Args:
            urls: List of URLs to scan
            
        Returns:
            List of analysis results (same format as analyze())
            
        Note:
            - Respects rate limits via key pooling
            - Uses caching to avoid duplicate scans
            - Processes sequentially to avoid overload
        """
        results = []
        for url in urls:
            result = self.analyze(url)
            results.append(result)
        return results
    
    # --- TruthFirst compatibility wrapper ---

_url_detector = None


def get_url_detector():
    """
    Lazy loader for URLDetector to maintain compatibility
    with existing AnalysisService architecture.
    """
    global _url_detector

    if _url_detector is None:
        from config import settings

        vt_keys = [
            settings.VT_KEY_1,
            settings.VT_KEY_2,
            settings.VT_KEY_3,
        ]

        _url_detector = URLDetector(
            vt_keys=vt_keys,
            gsb_key=settings.GSB_API_KEY,
            urlscan_key=settings.URLSCAN_API_KEY,
        )

    return _url_detector
