# ============================================================================
# File 3: models/url_detection/cache.py
# ============================================================================
import time
import hashlib
import threading

# Global in-memory cache (RAM-based for speed)
CACHE = {}
INFLIGHT = {}  # Tracks ongoing scans to prevent duplicates
LOCK = threading.Lock()

def _hash(url):
    """
    Generate SHA-256 hash of URL for cache key.
    
    Args:
        url: URL string
        
    Returns:
        str: Hexadecimal hash
        
    Why hash?
        - Fixed key size (64 chars)
        - Faster lookup
        - Avoid storing raw URLs
    """
    return hashlib.sha256(url.encode()).hexdigest()

def get_cache(url):
    """
    Retrieve cached scan result if valid.
    
    Args:
        url: URL to lookup
        
    Returns:
        dict: Cached result if valid, None if expired/missing
    """
    h = _hash(url)
    item = CACHE.get(h)
    if not item:
        return None
    if item["expires"] < time.time():
        CACHE.pop(h, None)
        return None
    return item["data"]

def set_cache(url, data, ttl):
    """
    Store scan result in cache with TTL.
    
    Args:
        url: URL being cached
        data: Scan result (dict)
        ttl: Time-to-live in seconds
    """
    CACHE[_hash(url)] = {
        "data": data,
        "expires": time.time() + ttl
    }

def get_inflight(url):
    """
    Check if URL scan is currently in progress.
    
    Args:
        url: URL to check
        
    Returns:
        threading.Event: Event to wait on, or None if not in progress
    """
    return INFLIGHT.get(_hash(url))

def set_inflight(url, event):
    """
    Mark URL scan as in-progress.
    
    Args:
        url: URL being scanned
        event: threading.Event for waiters to block on
    """
    INFLIGHT[_hash(url)] = event

def clear_inflight(url):
    """
    Mark URL scan as complete.
    
    Args:
        url: URL that finished scanning
    """
    INFLIGHT.pop(_hash(url), None)