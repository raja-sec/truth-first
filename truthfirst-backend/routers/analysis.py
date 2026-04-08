"""
Analysis Router - Image Detection Endpoint
Handles image upload and deepfake detection
"""
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
from schemas.detection import ImageAnalysisResult, ImageMetrics, ErrorResponse
from services.model_loader import get_image_detector
from models.image_detector import ImageDetector
from utils.constants import (
    VERDICT_GENUINE, VERDICT_DEEPFAKE, MODALITY_IMAGE,
    ERROR_MESSAGES,
    HTTP_400_BAD_REQUEST, HTTP_413_REQUEST_TOO_LARGE,
    HTTP_422_UNPROCESSABLE_ENTITY, HTTP_500_INTERNAL_SERVER_ERROR
)
from config import settings
import base64
import logging
import traceback
import os
import uuid
import shutil
import cv2
from services.model_loader import model_loader


router = APIRouter(prefix="/api/analyze", tags=["Analysis"])
logger = logging.getLogger(__name__)


def validate_image_file(file: UploadFile) -> tuple[bool, str]:
    """
    Validate uploaded image file
    
    Returns:
        tuple: (is_valid, error_message)
    """
    # Check file extension
    if not file.filename:
        return False, ERROR_MESSAGES["INVALID_IMAGE"]
    
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in settings.allowed_image_types_list:
        return False, ERROR_MESSAGES["INVALID_FILE_TYPE"].format(
            allowed_types=", ".join(settings.allowed_image_types_list)
        )
    
    return True, ""


def normalize_image_result(raw_result: dict) -> ImageAnalysisResult:
    """
    Normalize ImageDetector output to frontend schema
    
    Args:
        raw_result: Output from ImageDetector.analyze()
        
    Returns:
        ImageAnalysisResult with normalized fields
    """
    # Map internal verdict to user-facing verdict
    internal_verdict = raw_result["verdict"]
    
    if internal_verdict == "REAL":
        user_verdict = VERDICT_GENUINE
    else:  # FAKE
        user_verdict = VERDICT_DEEPFAKE  # For images, use DEEPFAKE
    
    # Convert confidence from 0-100 to 0-1
    confidence_normalized = raw_result["confidence"] / 100.0
    
    # Risk score is same as confidence percentage
    risk_score = int(raw_result["confidence"])
    
    # Build explanation
    if user_verdict == VERDICT_GENUINE:
        explanation = f"Image appears authentic with {raw_result['confidence']:.1f}% confidence. No significant manipulation detected."
    else:
        explanation = f"Image shows signs of deepfake manipulation with {raw_result['confidence']:.1f}% confidence. Multiple forensic indicators detected."
    
    # Base64 encode Grad-CAM heatmap
    grad_cam_base64 = base64.b64encode(raw_result["heatmap_bytes"]).decode("utf-8")
    
    # Create metrics object
    metrics = ImageMetrics(
        cnn_fake=raw_result["metrics"]["cnn_fake"],
        frequency_score=raw_result["metrics"]["freq"],
        artifact_score=raw_result["metrics"]["art"]
    )
    
    return ImageAnalysisResult(
        modality=MODALITY_IMAGE,
        verdict=user_verdict,
        confidence=confidence_normalized,
        risk_score=risk_score,
        factors=metrics,
        flags=raw_result["flags"],
        explanation=explanation,
        grad_cam_base64=grad_cam_base64,
        face_found=raw_result["face_found"]
    )


@router.post("/image", response_model=ImageAnalysisResult)
async def analyze_image(
    file: UploadFile = File(..., description="Image file (JPG/PNG/WEBP, max 10MB)"),
    detector: ImageDetector = Depends(get_image_detector)
):
    """
    Analyze an image for deepfake detection
    
    **Process:**
    1. Validates file type and size
    2. Extracts face region (with padding)
    3. Runs CNN + Frequency + Artifact analysis
    4. Applies fusion logic for final verdict
    5. Generates Grad-CAM heatmap
    
    **Returns:**
    - Verdict: GENUINE or DEEPFAKE/PHISHING
    - Confidence score (0-1)
    - Risk score (0-100)
    - Detailed forensic factors
    - Flags indicating specific issues
    - Grad-CAM visualization (base64)
    """
    
    try:
        # Step 1: Validate file type
        is_valid, error_msg = validate_image_file(file)
        if not is_valid:
            logger.warning(f"Invalid file upload: {error_msg}")
            raise HTTPException(
                status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                detail=error_msg
            )
        
        # Step 2: Read file and check size
        image_bytes = await file.read()
        file_size_mb = len(image_bytes) / (1024 * 1024)
        
        if file_size_mb > settings.MAX_FILE_SIZE_MB:
            logger.warning(f"File too large: {file_size_mb:.2f}MB")
            raise HTTPException(
                status_code=HTTP_413_REQUEST_TOO_LARGE,
                detail=ERROR_MESSAGES["FILE_TOO_LARGE"].format(
                    max_size=settings.MAX_FILE_SIZE_MB
                )
            )
        
        logger.info(f"Processing image: {file.filename} ({file_size_mb:.2f}MB)")
        
        # Step 3: Run analysis
        raw_result = detector.analyze(image_bytes)
        
        # Step 4: Check for errors from detector
        if "error" in raw_result:
            error_type = raw_result["error"]
            if error_type == "Invalid Image":
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail=ERROR_MESSAGES["INVALID_IMAGE"]
                )
            else:
                raise HTTPException(
                    status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=ERROR_MESSAGES["INTERNAL_ERROR"]
                )
        
        # Step 5: Check if face was found
        if not raw_result.get("face_found", False):
            logger.warning("No face detected in uploaded image")
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES["NO_FACE"]
            )
        
        # Step 6: Normalize and return result
        normalized_result = normalize_image_result(raw_result)
        
        logger.info(
            f"Analysis complete: {normalized_result.verdict} "
            f"(confidence: {normalized_result.confidence:.2f})"
        )
        
        return normalized_result
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
        
    except Exception as e:
        # Catch any unexpected errors
        logger.error(f"Unexpected error during image analysis: {str(e)}")
        
        # In development mode, include stack trace
        error_detail = {
            "error": "INTERNAL_ERROR",
            "message": ERROR_MESSAGES["INTERNAL_ERROR"]
        }
        
        if settings.DEBUG:
            error_detail["details"] = {
                "exception": str(e),
                "traceback": traceback.format_exc()
            }
        
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )
        
        
@router.post("/video")
async def analyze_video(file: UploadFile = File(...)):
    """
    Analyze a video for deepfake manipulation.

    **Process:**
    1. Validates file type (MP4, AVI, MOV) and limits duration to 60 seconds.
    2. Uniformly samples 32 frames across the video timeline.
    3. Detects and extracts facial regions with 10% context padding via MediaPipe.
    4. Runs spatial-temporal analysis using a ResNeXt-50 + LSTM architecture.

    **Returns:**
    - Verdict: GENUINE or DEEPFAKE
    - Confidence score (0-100%)
    - Total frames analyzed
    """

    # 1️⃣ Check video model availability (soft fail)
    if not model_loader.is_video_available():
        raise HTTPException(
            status_code=503,
            detail={
                "error": "VIDEO_MODEL_UNAVAILABLE",
                "message": "Video analysis is not enabled on this server."
            }
        )

    # 2️⃣ Validate MIME type
    if file.content_type not in settings.ALLOWED_VIDEO_TYPES:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail={
                "error": "INVALID_VIDEO_TYPE",
                "message": f"Allowed types: {settings.ALLOWED_VIDEO_TYPES}"
            }
        )

    # 3️⃣ Save to temp file
    temp_filename = f"video_{uuid.uuid4()}.mp4"
    temp_path = os.path.join(settings.TEMP_DIR, temp_filename)

    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 4️⃣ Validate duration
        cap = cv2.VideoCapture(temp_path)
        if not cap.isOpened():
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid or corrupted video file"
            )

        fps = cap.get(cv2.CAP_PROP_FPS)
        frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frames / fps if fps > 0 else 0
        cap.release()

        if duration > settings.MAX_VIDEO_DURATION:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=f"Maximum video duration is {settings.MAX_VIDEO_DURATION}s"
            )

        # 5️⃣ Load detector lazily
        detector = model_loader.load_video_detector()
        result = detector.analyze(temp_path)

        # 6️⃣ Handle model errors
        if result.get("status") != "success":
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=result.get("reason", "Video analysis failed")
            )

        # 7️⃣ Return normalized response
        return {
            "modality": "video",
            "verdict": result["verdict"],
            "confidence": result["confidence"],
            "fake_probability": result["fake_probability"],
            "frames_analyzed": result["frames_analyzed"],
            "video_duration": round(duration, 2),
            "total_frames": frames
        }

    finally:
        # 8️⃣ Guaranteed cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)
