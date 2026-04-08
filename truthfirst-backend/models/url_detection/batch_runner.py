# ============================================================================
# File 7: models/url_detection/batch_runner.py
# ============================================================================
import csv
import time

def load(file, label):
    """Load URLs from file with label."""
    with open(file) as f:
        return [(l.strip(), label) for l in f if l.strip()]

def run_batch(genuine, phishing, scan_fn):
    """
    Batch process URLs from files and generate CSV report.
    
    Args:
        genuine: Path to genuine URLs file
        phishing: Path to phishing URLs file
        scan_fn: Scan function (e.g., scan_url)
        
    Output:
        results.csv with columns:
        - url, true_label, verdict, risk_score, confidence,
          vt_malicious, gsb_threat
    """
    rows = load(genuine, "GENUINE") + load(phishing, "PHISHING")

    with open("results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["url","true_label","verdict","risk_score","confidence","vt_malicious","gsb_threat"])

        for url, label in rows:
            print("Scanning:", url)
            r = scan_fn(url)
            writer.writerow([
                url, label,
                r["verdict"],
                r["risk_score"],
                r["confidence"],
                r["factors"]["vt_malicious"],
                r["factors"]["gsb_threat"]
            ])
            time.sleep(1)  # Respectful rate limiting