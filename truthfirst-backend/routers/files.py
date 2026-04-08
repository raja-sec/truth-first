from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import mimetypes
import logging

from config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/uploads", tags=["Files"])

@router.get("/{date}/{case_id}/{filename}")
async def serve_uploaded_file(date: str, case_id: str, filename: str):
    """
    Serve uploaded files for display in the frontend.
    Path format: /uploads/YYYY-MM-DD/case_id/filename.ext
    """
    file_path = Path(settings.UPLOAD_DIR) / date / case_id / filename
    
    if not file_path.exists() or not file_path.is_file():
        logger.warning(f"File requested but not found: {file_path}")
        raise HTTPException(status_code=404, detail="File not found")
    
    # Security: Ensure file is strictly within the uploads directory (prevents path traversal)
    try:
        file_path.resolve().relative_to(Path(settings.UPLOAD_DIR).resolve())
    except ValueError:
        logger.error(f"Path traversal attempt blocked: {file_path}")
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Dynamically determine the correct media type (e.g., video/mp4, image/png)
    content_type, _ = mimetypes.guess_type(str(file_path))
    if not content_type:
        content_type = "application/octet-stream"  # Safe fallback
        
    return FileResponse(
        path=str(file_path),
        media_type=content_type,
        filename=filename
    )