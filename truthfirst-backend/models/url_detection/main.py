# ============================================================================
# File 8: models/url_detection/main.py
# ============================================================================
import os
from models.url_detection.vt_pool import VTKeyPool
from models.url_detection.scanner import scan_url
from models.url_detection.batch_runner import run_batch
from dotenv import load_dotenv

load_dotenv()

# Initialize VT key pool from environment
VT_KEYS = [os.getenv("VT_KEY_1"), os.getenv("VT_KEY_2"), os.getenv("VT_KEY_3")]
vt_pool = VTKeyPool([k for k in VT_KEYS if k])

def scan(url):
    """Wrapper for standalone usage."""
    return scan_url(url, vt_pool)

if __name__ == "__main__":
    # Batch processing mode
    run_batch("genuine.txt", "phishing.txt", scan)