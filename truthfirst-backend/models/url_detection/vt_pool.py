# ============================================================================
# File 2: models/url_detection/vt_pool.py
# ============================================================================
import time
import threading
from collections import deque

class TokenBucket:
    """
    Token bucket rate limiter for API requests.
    
    Implements smooth rate limiting without bursts.
    Each key gets its own bucket to enforce per-key limits.
    """
    def __init__(self, rate, per):
        """
        Initialize token bucket.
        
        Args:
            rate: Number of requests allowed
            per: Time period in seconds
        
        Example:
            TokenBucket(rate=4, per=60) = 4 requests per minute
        """
        self.rate = rate
        self.per = per
        self.tokens = rate
        self.updated = time.time()
        self.lock = threading.Lock()

    def allow(self):
        """
        Check if a request is allowed and consume a token.
        
        Returns:
            bool: True if request allowed, False if rate limit exceeded
        """
        with self.lock:
            now = time.time()
            elapsed = now - self.updated
            refill = int(elapsed * (self.rate / self.per))
            if refill > 0:
                self.tokens = min(self.rate, self.tokens + refill)
                self.updated = now

            if self.tokens > 0:
                self.tokens -= 1
                return True
            return False


class VTKeyPool:
    """
    VirusTotal API key pool with automatic rotation and rate limiting.
    
    Manages multiple VT keys to:
    - Increase throughput (N keys = N × rate limit)
    - Prevent API bans (enforces 4 req/min per key)
    - Rotate fairly (round-robin across keys)
    """
    def __init__(self, keys):
        """
        Initialize key pool.
        
        Args:
            keys: List of VirusTotal API keys
        """
        self.pool = deque()
        for k in keys:
            # Each key gets its own rate limiter (4 req/min)
            self.pool.append((k, TokenBucket(rate=4, per=60)))

    def get_key(self):
        """
        Get an available API key (respects rate limits).
        
        Returns:
            str: API key if available, None if all keys exhausted
            
        Note:
            Rotates through keys in round-robin fashion.
            If all keys are rate-limited, returns None (caller should wait).
        """
        for _ in range(len(self.pool)):
            key, limiter = self.pool[0]
            self.pool.rotate(-1)  # Move to back (round-robin)
            if limiter.allow():
                return key
        return None
