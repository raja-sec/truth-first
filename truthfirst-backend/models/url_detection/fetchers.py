# ============================================================================
# File 4: models/url_detection/fetchers.py
# ============================================================================
import os
import time
import base64
import requests
from dotenv import load_dotenv

load_dotenv()
TIMEOUT = 5

# API keys loaded from environment
GSB_API_KEY = os.getenv("GSB_API_KEY")
URLSCAN_API_KEY = os.getenv("URLSCAN_API_KEY")

def fetch_gsb(url):
    """
    Check URL against Google Safe Browsing.
    
    Args:
        url: URL to check
        
    Returns:
        dict: GSB API response or {"error": True}
        
    Detects:
        - MALWARE
        - SOCIAL_ENGINEERING (phishing)
    """
    if not GSB_API_KEY:
        return {"error": True}

    try:
        res = requests.post(
            "https://safebrowsing.googleapis.com/v4/threatMatches:find",
            params={"key": GSB_API_KEY},
            json={
                "client": {"clientId": "standalone", "clientVersion": "1.0"},
                "threatInfo": {
                    "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING"],
                    "platformTypes": ["ANY_PLATFORM"],
                    "threatEntryTypes": ["URL"],
                    "threatEntries": [{"url": url}]
                }
            },
            timeout=TIMEOUT
        )
        return res.json()
    except Exception:
        return {"error": True}


def vt_url_id(url):
    """
    Generate VirusTotal URL ID (base64-encoded URL).
    
    Args:
        url: URL string
        
    Returns:
        str: Base64-encoded URL without padding
    """
    return base64.urlsafe_b64encode(url.encode()).decode().strip("=")


def fetch_vt(url, vt_pool):
    """
    Submit URL to VirusTotal and retrieve analysis.
    
    Args:
        url: URL to scan
        vt_pool: VTKeyPool instance for key rotation
        
    Returns:
        dict: VT analysis result or {"error": True}
        
    Process:
        1. Wait for available API key (respects rate limits)
        2. Submit URL for scanning
        3. Poll for results (max 3 retries)
        
    Rate Limit:
        4 requests per minute per key (enforced by vt_pool)
    """
    key = None
    while not key:
        key = vt_pool.get_key()
        if not key:
            print("[VT] All keys exhausted, waiting...")
            time.sleep(2)

    headers = {"x-apikey": key}

    try:
        # Submit URL for scanning
        requests.post(
            "https://www.virustotal.com/api/v3/urls",
            headers=headers,
            data={"url": url},
            timeout=TIMEOUT
        )

        # Poll for results
        url_id = vt_url_id(url)
        for _ in range(3):
            res = requests.get(
                f"https://www.virustotal.com/api/v3/urls/{url_id}",
                headers=headers,
                timeout=TIMEOUT
            )
            if res.status_code == 200:
                return res.json()
            time.sleep(2)
    except Exception:
        pass

    return {"error": True}


def fetch_urlscan(url):
    """
    Submit URL to URLScan.io for behavioral analysis.
    
    Args:
        url: URL to scan
        
    Returns:
        dict: URLScan result or {"error": True}
        
    Detects:
        - Phishing behavior (page content, redirects)
        - Malicious JavaScript
        - Clone pages
    """
    if not URLSCAN_API_KEY:
        return {"error": True}

    try:
        headers = {
            "API-Key": URLSCAN_API_KEY,
            "Content-Type": "application/json"
        }
        res = requests.post(
            "https://urlscan.io/api/v1/scan/",
            headers=headers,
            json={"url": url, "visibility": "public"},
            timeout=TIMEOUT
        )
        return res.json()
    except Exception:
        return {"error": True}