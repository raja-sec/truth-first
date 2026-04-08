"""
Email Security Module - Multi-Layer Phishing Detection

This is the core email phishing detection engine that combines:
1. BERT NLP analysis (semantic understanding)
2. URL threat intelligence (VirusTotal, Google Safe Browsing, URLScan)
3. Email header forensics (SPF, DKIM, spoofing detection)
4. Behavioral heuristics (urgency keywords, social engineering)
5. Dynamic risk fusion logic

Architecture:
- Defense-in-depth: Multiple independent layers
- Explainable AI: Each component contributes to risk score
- Production-ready: Thread-safe, rate-limited, cached
"""

import torch
import json
import re
import os
import email
from email import policy
from email.parser import BytesParser
from dotenv import load_dotenv
from PIL import Image
import sys
import pytesseract

# Strictly separate Windows vs Linux paths
if sys.platform == "win32":
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
else:
    # Explicitly force the Linux path for the Docker container
    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'


# Import URL detection modules (reused from url_detection/)
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'url_detection'))

from vt_pool import VTKeyPool
from scanner import scan_url
from transformers import BertTokenizer, BertForSequenceClassification
import torch.nn.functional as F

# Load environment variables
load_dotenv()
# # --- TESSERACT CONFIG (Windows) ---
# pytesseract.pytesseract.tesseract_cmd = (
#     r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# )


class PhishingDetector:
    """
    Multi-layer email phishing detection system.
    
    Components:
    - BERT: Fine-tuned language model for phishing text classification
    - URL Scanner: Multi-API threat intelligence (GSB, VT, URLScan)
    - Header Forensics: SPF/DKIM validation, spoofing detection
    - Heuristics: Keyword matching, urgency detection
    - Fusion Engine: Dynamic risk aggregation with context-aware weighting
    """
    
    def __init__(self, model_path):
        """
        Initialize email security core.
        
        Args:
            model_path: Path to fine-tuned BERT model directory
        """
        print("--- INITIALIZING EMAIL SECURITY CORE ---")
        
        # 1. Load BERT Model (NLP Engine)
        print(f"[1/3] Loading BERT Model from {model_path}...")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = BertTokenizer.from_pretrained(model_path)
        self.model = BertForSequenceClassification.from_pretrained(model_path).to(self.device)
        self.model.eval()
        
        # 2. Initialize VirusTotal Key Pool (Threat Engine)
        print("[2/3] Initializing VirusTotal Key Pool...")
        vt_keys = [
            os.getenv("VT_KEY_1"), 
            os.getenv("VT_KEY_2"), 
            os.getenv("VT_KEY_3")
        ]
        # Filter out None values
        self.vt_pool = VTKeyPool([k for k in vt_keys if k])
        
        print("[3/3] Email Security System Ready.")

    def _parse_eml(self, file_path):
        """
        Parse raw .eml file to extract headers and body.
        
        Args:
            file_path: Path to .eml file
            
        Returns:
            tuple: (body_text, headers_dict)
            
        Extracts:
            - Email body (plain text preferred, HTML fallback)
            - Critical headers: From, To, Subject, Return-Path,
              Authentication-Results, Received
        """
        with open(file_path, 'rb') as f:
            msg = BytesParser(policy=policy.default).parse(f)
        
        # Extract Body (prefer plain text, fallback to HTML)
        body = msg.get_body(preferencelist=('plain', 'html'))
        body_text = body.get_content() if body else ""
        
        # Extract Headers
        headers = {
            "From": msg.get("From", ""),
            "To": msg.get("To", ""),
            "Subject": msg.get("Subject", ""),
            "Return-Path": msg.get("Return-Path", ""),
            "Authentication-Results": msg.get("Authentication-Results", ""),
            "Received": str(msg.get_all("Received", []))
        }
        return body_text, headers
    
    def _parse_image(self, image_path: str) -> str:
        """
        Extract text from email screenshots using OCR.
        """
        try:
            image = Image.open(image_path)
            raw_text = pytesseract.image_to_string(image)

            # Clean OCR noise
            clean_text = " ".join(raw_text.split())
            return clean_text

        except Exception as e:
            print(f"OCR failed: {e}")
            return ""


    def _extract_urls(self, text):
        """
        Extract all URLs from text using regex.
        
        Args:
            text: Email body or any text content
            
        Returns:
            list: Extracted URLs
            
        Pattern:
            Matches http:// and https:// URLs
        """
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.findall(url_pattern, str(text))
    
    def _is_valid_url(self, url: str) -> bool:
        return (
            isinstance(url, str)
            and url.startswith(("http://", "https://"))
            and "." in url
            and len(url) > 10
        )


    def _analyze_headers(self, headers):
        """
        Email header forensics (SPF, DKIM, spoofing detection).
        
        Args:
            headers: Dictionary of email headers
            
        Returns:
            tuple: (anomaly_score, flags_list)
            
        Checks:
        1. SPF Failure: Sender IP not authorized (+25 risk)
        2. DKIM Failure: Digital signature invalid (+25 risk)
        3. From vs Return-Path Mismatch: Spoofing attempt (+30 risk)
        
        Why This Matters:
            Legitimate organizations almost never fail SPF+DKIM.
            Mismatched domains are a common phishing tactic.
        """
        flags = []
        score = 0
        
        if not headers:
            return 0, []

        # 1. SPF/DKIM Check (via Authentication-Results header)
        # This header is added by receiving servers (Gmail, Outlook)
        auth_results = headers.get("Authentication-Results", "").lower()
        
        if "dkim=fail" in auth_results:
            score += 25
            flags.append("Security Protocol Failed: DKIM signature is invalid")
        
        if "spf=fail" in auth_results:
            score += 25
            flags.append("Security Protocol Failed: SPF check failed (Sender IP not authorized)")

        # 2. Spoofing Check (From vs Return-Path)
        # Return-Path is where bounces go. If it's totally different from 'From', suspicious.
        from_header = headers.get("From", "")
        return_path = headers.get("Return-Path", "")
        
        # Extract emails from format "Name <email@domain.com>"
        from_email = re.search(r'<(.+?)>', from_header)
        return_email = re.search(r'<(.+?)>', return_path)
        
        if from_email and return_email:
            from_domain = from_email.group(1).split('@')[-1]
            return_domain = return_email.group(1).split('@')[-1]
            
            # Logic: If domain is completely different
            if from_domain not in return_domain and return_domain not in from_domain:
                score += 30
                flags.append(f"Spoofing Attempt: 'From' is {from_domain} but 'Return-Path' is {return_domain}")

        return score, flags

    def analyze(self, input_data, input_type="text"):
        """
        Main email analysis controller.
        
        Args:
            input_data: Raw text string OR file path to .eml
            input_type: "text" or "file"
            
        Returns:
            JSON string with analysis result
            
        Processing Pipeline:
        1. Parse email (text or .eml)
        2. Extract and scan URLs (threat intelligence)
        3. BERT NLP analysis
        4. Header forensics
        5. Keyword heuristics
        6. Dynamic risk fusion
        7. Generate verdict + explanation
        """
        # --- PHASE 1: PARSING ---
        # if input_type == "file":
        #     body_text, headers = self._parse_eml(input_data)
        # else:
        #     body_text = input_data
        #     headers = {} 
        if input_type == "file":
            body_text, headers = self._parse_eml(input_data)

        elif input_type == "image":
            body_text = self._parse_image(input_data)
            headers = {}

        else:
            body_text = input_data
            headers = {}
            
        if not body_text.strip():
            return json.dumps({
                "modality": "email",
                "verdict": "UNCERTAIN",
                "confidence": 0.0,
                "risk_score": 0,
                "factors": {},
                "flags": ["OCR failed or no readable text found"],
                "explanation": "Unable to extract readable text from the image."
            }, indent=2)


        # --- PHASE 2: URL THREAT INTELLIGENCE ---
        # urls = self._extract_urls(body_text)
        urls = self._extract_urls(body_text)

        MAX_URLS_PER_EMAIL = 4  # VT-safe
        urls = urls[:MAX_URLS_PER_EMAIL]

        url_reports = []
        max_url_risk = 0
        url_flags = []

        # MAX_URLS_PER_EMAIL = 4  # VT + URLScan safe limit

        if urls:
            for url in urls[:MAX_URLS_PER_EMAIL]:

                # ✅ Skip malformed / junk URLs
                if not isinstance(url, str) or not url.startswith(("http://", "https://")) or "." not in url:
                    continue

                try:
                    scan_result = scan_url(url, self.vt_pool)
                except Exception as e:
                    # Soft-fail URL scanning errors (rate limit, 400s, timeouts)
                    continue

                current_risk = scan_result.get("risk_score", 0)

                if current_risk > max_url_risk:
                    max_url_risk = current_risk

                if scan_result.get("verdict") == "PHISHING":
                    url_flags.append(f"Malicious Link: {url}")

                url_reports.append({
                    "url": url,
                    "verdict": scan_result.get("verdict", "UNKNOWN"),
                    "risk_score": scan_result.get("risk_score", 0),
                    "sources": scan_result.get("factors", [])
                })

        
        # --- PHASE 3: BERT MODEL ANALYSIS ---
        # Combine Subject + Body for better context
        subject_text = headers.get("Subject", "")
        if subject_text:
            combined_text = f"Subject: {subject_text} Body: {body_text}"
        else:
            combined_text = str(body_text)

        clean_text = " ".join(combined_text.lower().split())
        inputs = self.tokenizer(
            clean_text, 
            return_tensors="pt", 
            truncation=True, 
            padding=True, 
            max_length=256
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = F.softmax(outputs.logits, dim=1)
            bert_confidence = probs[0][1].item()  # Phishing class probability

        bert_score = bert_confidence * 100

        # --- PHASE 4: HEADER HEURISTICS ---
        header_score, header_flags = self._analyze_headers(headers)
        
        # --- PHASE 5: KEYWORD HEURISTICS ---
        keyword_score = 0
        urgent_words = [
            'urgent', 'suspend', 'immediately', 'verify account', 
            'unauthorized', 'expire', 'offer', 'winner', 'claim',
            'confirm identity', 'update payment'
        ]
        found_keywords = [w for w in urgent_words if w in clean_text]
        if found_keywords:
            keyword_score = 15
            header_flags.append(f"Urgency/Threat language: {', '.join(found_keywords[:3])}")

        # --- PHASE 6: DYNAMIC RISK FUSION ---
        
        # Scenario A: URL is definitely malicious -> Immediate override
        if max_url_risk >= 85:
            final_risk_score = 99
            verdict = "PHISHING"
            explanation = "Email contains confirmed malicious links."
            
        # Scenario B: No URLs and No Headers (Raw Text Input)
        elif not urls and not headers:
            # Trust the AI Model + Keywords
            final_risk_score = (bert_score * 0.9) + (keyword_score * 0.1)
            explanation = f"AI Text Analysis indicates {int(bert_score)}% risk based on content patterns."
            
        # Scenario C: Mixed Signals (Standard Email)
        else:
            # If no URLs found, distribute URL weight to BERT
            if not urls:
                final_risk_score = (bert_score * 0.7) + ((header_score + keyword_score) * 0.3)
                explanation = f"AI Analysis indicates {int(bert_score)}% risk. Heuristics added {int(header_score + keyword_score)} risk points."
            else:
                # Full Weighted Formula: BERT(40%) + URL(40%) + Headers(20%)
                final_risk_score = (
                    (bert_score * 0.4) + 
                    (max_url_risk * 0.4) + 
                    ((header_score + keyword_score) * 0.2)
                )
                explanation = f"Combined Risk: AI ({int(bert_score)}%), Links ({max_url_risk}%), Heuristics ({int(header_score + keyword_score)}%)."

        # Cap Score at 100
        final_risk_score = min(final_risk_score, 100)
        
        # Verdict threshold: 60%
        verdict = "PHISHING" if final_risk_score > 60 else "GENUINE"

        # --- PHASE 7: GENERATE JSON RESPONSE ---
        all_flags = header_flags + url_flags

        response = {
            "modality": "email",
            "verdict": verdict,
            "confidence": round(final_risk_score / 100, 2),
            "risk_score": int(final_risk_score),
            "factors": {
                "body_text_analysis": int(bert_score),
                "header_anomalies": header_score,
                "link_risk": max_url_risk,
                "keyword_risk": keyword_score
            },
            "flags": list(set(all_flags)),  # Remove duplicates
            "extracted_data": {
                "sender": headers.get("From", "Unknown/Screenshot"),
                "subject": headers.get("Subject", "Unknown/Screenshot"),
                "urls_found": len(urls),

                # ✅ OCR transparency (THIS answers your question)
                "ocr_used": input_type == "image",
                "ocr_text_length": len(body_text),
                "ocr_snippet": (
                    body_text[:120] + "..."
                    if input_type == "image" and body_text
                    else None
                )
            },

            "explanation": explanation
        }
        
        return json.dumps(response, indent=2)