# TruthFirst : Multi-Modal Deception Detection 

**Defending against AI-generated media, deepfakes, and social engineering.**

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white) ![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB) ![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=PyTorch&logoColor=white) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)

---

## Overview

As generative AI blurs the line between reality and fabrication, the threat of deepfakes and sophisticated phishing campaigns is scaling exponentially. **TruthFirst** is a comprehensive cybersecurity platform engineered to investigate suspicious media and digital communications. 

By utilizing a multi-modal architecture, TruthFirst analyzes **Images, Videos, URLs, and Emails** to detect manipulation. Beyond simple detection, it provides explainable AI visualizer outputs (Grad-CAM), generates professional forensic PDF reports, and provides legally compliant guidance for reporting verified threats to official cybercrime authorities.

[**View Live Demo**](#) *(Placeholder for deployment link)*

---

## Core Detection Modalities

TruthFirst does not rely on a single algorithm; it uses context-aware pipelines tailored to the specific modality being analyzed.

### 1. Image Deepfake Detection
* **Hybrid AI Ensemble:** Combines a custom-trained EfficientNet-B0 Convolutional Neural Network with mathematical Frequency (FFT) and Artifact Engines.
* **Explainable AI:** Generates side-by-side **Grad-CAM heatmaps**, highlighting the exact pixel regions where the model detected synthetic blending or manipulation.
* **Veto Logic Engine:** Implements "Shield and Rescue" thresholds to heavily minimize false positives.

### 🎬 2. Video Temporal Analysis
* **Spatial-Temporal Architecture:** Utilizes a **ResNeXt-50** feature extractor to process 32 uniformly sampled frames, paired with a 2-layer **LSTM** (Long Short-Term Memory) network for deep time-series analysis.
* **Targeted Face Extraction:** Employs MediaPipe for precise facial tracking and bounding box extraction (with 10% context padding) across supported video formats (MP4, AVI, MOV) up to 60 seconds in duration.
* **Temporal Inconsistency Detection:** Specifically targets inter-frame flickering, unnatural expression shifts, and temporal blending artifacts common in deepfake generation.
* **Resilient Deployment:** Features soft-fail initialization and native CPU fallback, ensuring the core platform remains stable even if video model weights are missing or GPU compute is unavailable.

### 3. URL Threat Intelligence
* **Multi-API Fusion:** Queries a weighted ensemble of trusted security APIs, including VirusTotal, Google Safe Browsing, and URLScan.io.
* **Optimized Scaling:** Features an in-memory TTL caching system, in-flight request deduplication, and token-bucket rate limiting with automated API key rotation.

### 4. Email Forensics
* **NLP Semantic Analysis:** Leverages a fine-tuned HuggingFace BERT model to detect urgency, threat language, and social engineering tactics in the email body.
* **Header & Link Extraction:** Fuses NLP results with deep header forensics (SPF, DKIM, spoofing detection) and routes extracted links through the URL Threat Intelligence pipeline.

---

## Key Platform Features

* **Actionable Forensic Reports:** Generates standardized, downloadable PDF reports via WeasyPrint, featuring embedded visualizations, confidence charts, and SHA-256 file hashes.
* **Cybercrime Reporting Guide:** Features a legally safe, user-driven guidance modal for filing official complaints (designed strictly as a guide to prevent liability and false reports).
* **Token-Gated Authentication:** Secures the case submission pipeline utilizing JWTs and stateless OTP (One-Time Password) email verification.

---

## Architecture & Tech Stack

TruthFirst is built with a decoupled frontend and backend, enabling heavy machine learning workloads to run asynchronously without blocking the user interface.

### Backend (Python / Machine Learning)
* **Framework:** FastAPI (Async API layer)
* **ML Stack:** PyTorch, HuggingFace Transformers, OpenCV, MediaPipe
* **Database:** PostgreSQL 16 with SQLAlchemy 2.0 (Async) + Alembic
* **Reporting:** WeasyPrint, Jinja2, Matplotlib

### Frontend (User Interface)
* **Framework:** React 18 (TypeScript) via Vite
* **Styling:** Tailwind CSS (with Dark/Light mode support)
* **State & Localization:** Custom hooks, i18next (prepared for multi-language support)

---

## Local Development (Quick Start)

*Note: TruthFirst relies on heavy `.pth` and `.bin` machine learning weights which are not tracked in this repository. Ensure you have the model weights placed in their respective `models/` subdirectories before starting.*

### 1. Clone & Install
```bash
git clone https://github.com/raja-sec/truth-first.git
cd truth-first/truthfirst-backend

# Setup Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment


```bash
cp .env.example .env
```

*Populate the `.env` file with your PostgreSQL database URL, SMTP credentials, and Threat Intel API keys.*

### 3. Start the Platform

**Start the FastAPI Backend:**


```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Start the React Frontend:**


```bash
cd ../truthfirst-frontend
npm install
npm run dev
```

---

## Legal Disclaimer

TruthFirst is an investigative tool designed strictly for awareness and guidance. AI detection systems are not 100% accurate and can produce false positives or false negatives. Output from this platform **does not constitute legal proof or court-admissible evidence**. Users are solely responsible for verifying threats and ensuring the accuracy of any official complaints filed with law enforcement or cybercrime portals.

---

*Designed and engineered for the defense against digital deception.*