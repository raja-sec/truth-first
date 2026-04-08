# ============================================================================
# File 6: models/url_detection/scanner.py
# ============================================================================
import threading
from models.url_detection.cache import get_cache, set_cache, get_inflight, set_inflight, clear_inflight
from models.url_detection.fetchers import fetch_gsb, fetch_vt, fetch_urlscan
from models.url_detection.logic import calculate_url_verdict

CACHE_TTL_PHISH = 86400  # 24 hours for phishing URLs
CACHE_TTL_CLEAN = 3600   # 1 hour for clean URLs

SCAN_SEMAPHORE = threading.Semaphore(5)  # Max 5 parallel scans


def normalize_gsb(data):
    """Normalize Google Safe Browsing response."""
    if not data or "error" in data:
        return {"detected": False, "reason": None}
    matches = data.get("matches", [])
    if matches:
        return {"detected": True, "reason": matches[0].get("threatType")}
    return {"detected": False, "reason": None}

def normalize_vt(data):
    """Normalize VirusTotal response."""
    stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
    cnt = stats.get("malicious", 0)
    return {"detected": cnt > 0, "cnt": cnt}

def normalize_urlscan(data):
    """Normalize URLScan response."""
    verdicts = data.get("verdicts", {})
    score = verdicts.get("engines", {}).get("score", 0)
    detected = verdicts.get("overall", {}).get("malicious", False) or score > 0
    return {"detected": detected, "score": score}

def scan_url(url, vt_pool):
    """
    Main URL scanning orchestration.
    
    Args:
        url: URL to scan
        vt_pool: VTKeyPool for VirusTotal API calls
        
    Returns:
        dict: Scan result with verdict, confidence, risk score
        
    Flow:
        1. Check cache → return if hit
        2. Check in-flight → wait if duplicate
        3. Acquire semaphore (limit concurrency)
        4. Call APIs (GSB, VT, conditional URLScan)
        5. Normalize responses
        6. Calculate verdict
        7. Cache result
        8. Return
        
    Features:
        - In-flight deduplication (prevents duplicate scans)
        - Partial result handling (graceful API failures)
        - Conditional scanning (skip URLScan if VT confident)
    """
    with SCAN_SEMAPHORE:
        # 1. Check cache
        cached = get_cache(url)
        if cached:
            return cached

        # 2. Check in-flight (prevent duplicate scans)
        inflight = get_inflight(url)
        if inflight:
            inflight.wait()
            return get_cache(url)

        # 3. Mark as in-flight
        event = threading.Event()
        set_inflight(url, event)

        try:
            flags = []

            # 4. Fetch from APIs
            gsb_raw = fetch_gsb(url)
            if "error" in gsb_raw:
                flags.append("Partial scan – Google Safe Browsing unavailable")
            gsb = normalize_gsb(gsb_raw)

            vt_raw = fetch_vt(url, vt_pool)
            if "error" in vt_raw:
                flags.append("Partial scan – VirusTotal unavailable")
            vt = normalize_vt(vt_raw)

            # Conditional URLScan (only if VT not confident)
            if vt["cnt"] >= 1:
                us = {"detected": False, "score": 0}
            else:
                us_raw = fetch_urlscan(url)
                if "error" in us_raw:
                    flags.append("Partial scan – URLScan unavailable")
                us = normalize_urlscan(us_raw)

            # 5. Calculate verdict
            result = calculate_url_verdict(gsb, vt, us)

            # 6. Merge flags
            if flags:
                result["flags"].extend(flags)

            # 7. Cache result (longer TTL for phishing)
            ttl = CACHE_TTL_PHISH if result["verdict"] != "GENUINE" else CACHE_TTL_CLEAN
            set_cache(url, result, ttl)
            
            return result

        finally:
            # 8. Clear in-flight and notify waiters
            clear_inflight(url)
            event.set()