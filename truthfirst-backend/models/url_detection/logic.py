# ============================================================================
# File 5: models/url_detection/logic.py
# ============================================================================

def verdict(v, r, c, f, flags, exp):
    """
    Construct standardized verdict response.
    
    Args:
        v: verdict string (GENUINE/SUSPICIOUS/PHISHING)
        r: risk_score (0-100)
        c: confidence (0.0-1.0)
        f: factors dict
        flags: list of detection flags
        exp: explanation string
        
    Returns:
        dict: Normalized verdict structure
    """
    return {
        "verdict": v,
        "risk_score": r,
        "confidence": c,
        "factors": f,
        "flags": flags,
        "explanation": exp
    }

def calculate_url_verdict(gsb, vt, us):
    """
    Rule-based decision engine for URL verdict.
    
    Args:
        gsb: Normalized Google Safe Browsing result
        vt: Normalized VirusTotal result
        us: Normalized URLScan result
        
    Returns:
        dict: Final verdict with risk score, confidence, and flags
        
    Decision Rules:
        1. GSB detected OR VT ≥ 2 vendors → PHISHING (critical)
        2. VT = 1 vendor + URLScan detected → PHISHING (high confidence)
        3. VT = 1 vendor only → SUSPICIOUS
        4. URLScan detected only → SUSPICIOUS
        5. No detections → GENUINE
        
    Risk Scores:
        PHISHING: 85-100 (high risk)
        SUSPICIOUS: 50-65 (medium risk)
        GENUINE: 0 (no risk)
    """
    factors = {
        "gsb_threat": gsb["reason"],
        "vt_malicious": vt["cnt"],
        "urlscan_score": us["score"]
    }

    # Rule 1: Critical threat (GSB or multiple VT detections)
    if gsb["detected"] or vt["cnt"] >= 2:
        return verdict("PHISHING", 100, 0.99, factors,
                       ["Confirmed threat by trusted authority"],
                       "Critical threat detected.")

    # Rule 2: High confidence phishing (VT + URLScan)
    if us["detected"] and vt["cnt"] >= 1:
        return verdict("PHISHING", 85, 0.90, factors,
                       ["Behavioral anomalies confirmed"],
                       "High risk phishing behavior.")

    # Rule 3: Single vendor detection
    if vt["cnt"] == 1:
        return verdict("SUSPICIOUS", 65, 0.75, factors,
                       ["Flagged by 1 security vendor"],
                       "Suspicious URL.")

    # Rule 4: Behavioral detection only
    if us["detected"]:
        return verdict("SUSPICIOUS", 50, 0.60, factors,
                       ["Behavioral detection"],
                       "Suspicious page behavior.")

    # Rule 5: No threats detected
    return verdict("GENUINE", 0, 0.95, factors, [], "No threats detected.")
