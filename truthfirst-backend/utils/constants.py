"""
Constants and Enums for TruthFirst
"""

# =========================
# User-Facing Verdicts
# =========================

VERDICT_GENUINE = "GENUINE"

# Modality-specific verdicts
VERDICT_DEEPFAKE = "DEEPFAKE"        # Image / Video
VERDICT_PHISHING = "PHISHING"        # Email / URL
VERDICT_SUSPICIOUS = "SUSPICIOUS"    # URL only
VERDICT_UNKNOWN = "UNKNOWN"          # Safe fallback

# =========================
# Modality Types
# =========================

MODALITY_IMAGE = "image"
MODALITY_VIDEO = "video"
MODALITY_EMAIL = "email"
MODALITY_URL = "url"


def get_fake_verdict(modality: str) -> str:
    """
    Get the appropriate 'fake' verdict based on modality.
    
    NOTE:
    - This returns the *worst-case* verdict
    - URL detector may later downgrade to SUSPICIOUS
    """
    if modality in [MODALITY_IMAGE, MODALITY_VIDEO]:
        return VERDICT_DEEPFAKE

    if modality in [MODALITY_EMAIL, MODALITY_URL]:
        return VERDICT_PHISHING

    return VERDICT_UNKNOWN


# =========================
# Error Messages (User-Facing)
# =========================

ERROR_MESSAGES = {
    "NO_FACE": "No face detected in the image. Please upload an image with a clear, visible face.",
    "INVALID_IMAGE": "Invalid or corrupted image file. Please upload a valid image (JPG, PNG, WEBP).",
    "FILE_TOO_LARGE": "File size exceeds maximum limit of {max_size}MB.",
    "INVALID_FILE_TYPE": "Invalid file type. Allowed formats: {allowed_types}",
    "INTERNAL_ERROR": "An internal error occurred during analysis. Please try again or contact support.",
    "MODEL_LOAD_ERROR": "Failed to load detection model. Please contact support."
}

# =========================
# HTTP Status Codes
# =========================

HTTP_200_OK = 200
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_413_REQUEST_TOO_LARGE = 413
HTTP_422_UNPROCESSABLE_ENTITY = 422
HTTP_500_INTERNAL_SERVER_ERROR = 500
