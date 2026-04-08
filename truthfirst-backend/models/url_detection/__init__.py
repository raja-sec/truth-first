# ============================================================================
# File 1: models/url_detection/__init__.py
# ============================================================================
"""
Standalone URL Phishing Detection Module

This module provides multi-source threat intelligence scanning for URLs.

Components:
- vt_pool: VirusTotal API key pool with token bucket rate limiting
- scanner: Main orchestration with caching and deduplication
- logic: Rule-based decision engine for verdict calculation
- fetchers: API clients for GSB, VirusTotal, URLScan
- cache: In-memory cache with TTL and in-flight tracking
- batch_runner: Offline batch processing for datasets
- main: Entry point for standalone usage

Architecture:
- Thread-safe concurrent scanning (max 5 parallel)
- RAM cache (24h phishing, 1h clean)
- In-flight deduplication (prevents duplicate API calls)
- Graceful degradation (partial results if APIs fail)
- Production-ready for hackathon scale (100+ concurrent users)
"""

__version__ = "1.0.0"
__author__ = "TruthFirst Team"
