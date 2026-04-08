"""
File Upload and Management Service
Handles saving, validation, and cleanup of uploaded files
"""
import os
import aiofiles
from pathlib import Path
from datetime import datetime
from fastapi import UploadFile
import logging
import uuid

logger = logging.getLogger(__name__)


class FileHandler:
    """Handle file uploads and storage"""
    
    def __init__(self, upload_dir: str = "uploads"):
        """
        Initialize file handler with upload directory.
        
        Args:
            upload_dir: Base directory for file uploads
        """
        self.upload_dir = Path(upload_dir)
        self._ensure_upload_dir()
    
    def _ensure_upload_dir(self):
        """Create upload directory if it doesn't exist"""
        if not self.upload_dir.exists():
            self.upload_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 Created upload directory: {self.upload_dir}")
    
    def _get_case_dir(self, case_id: str) -> Path:
        """
        Get directory for a specific case.
        Creates subdirectory structure: uploads/YYYY-MM-DD/case_id/
        """
        date_dir = datetime.utcnow().strftime("%Y-%m-%d")
        case_dir = self.upload_dir / date_dir / case_id
        
        if not case_dir.exists():
            case_dir.mkdir(parents=True, exist_ok=True)
        
        return case_dir
    
    async def save_file(
        self,
        file: UploadFile,
        case_id: str,
        prefix: str = "file"
    ) -> dict:
        """
        Save uploaded file to disk.
        
        Args:
            file: FastAPI UploadFile object
            case_id: Case ID for organizing files
            prefix: Filename prefix (e.g., 'image', 'email')
        
        Returns:
            dict with file_path, file_name, file_size
        """
        try:
            # Get case directory
            case_dir = self._get_case_dir(case_id)
            
            # Generate safe filename
            file_ext = Path(file.filename).suffix if file.filename else ""
            safe_filename = f"{prefix}_{uuid.uuid4().hex[:8]}{file_ext}"
            file_path = case_dir / safe_filename
            
            # Save file
            content = await file.read()
            file_size = len(content)
            
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)
            
            logger.info(f"💾 Saved file: {file_path} ({file_size} bytes)")
            
            return {
                "file_path": str(file_path),
                "file_name": file.filename,
                "file_size": file_size,
            }
        
        except Exception as e:
            logger.error(f"❌ Failed to save file: {e}")
            raise
        finally:
            # Reset file pointer
            await file.seek(0)
    
    async def read_file(self, file_path: str) -> bytes:
        """
        Read file contents from disk.
        
        Args:
            file_path: Path to file
        
        Returns:
            File contents as bytes
        """
        try:
            async with aiofiles.open(file_path, 'rb') as f:
                content = await f.read()
            
            return content
        
        except Exception as e:
            logger.error(f"❌ Failed to read file {file_path}: {e}")
            raise
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from disk.
        
        Args:
            file_path: Path to file
        
        Returns:
            True if deleted, False if not found
        """
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                logger.info(f"🗑️  Deleted file: {file_path}")
                return True
            else:
                logger.warning(f"⚠️  File not found: {file_path}")
                return False
        
        except Exception as e:
            logger.error(f"❌ Failed to delete file {file_path}: {e}")
            return False
    
    def delete_case_files(self, case_id: str) -> int:
        """
        Delete all files for a specific case.
        
        Args:
            case_id: Case ID
        
        Returns:
            Number of files deleted
        """
        deleted_count = 0
        
        try:
            # Search in all date directories
            for date_dir in self.upload_dir.iterdir():
                if not date_dir.is_dir():
                    continue
                
                case_dir = date_dir / case_id
                if case_dir.exists():
                    for file_path in case_dir.iterdir():
                        if file_path.is_file():
                            file_path.unlink()
                            deleted_count += 1
                    
                    # Remove empty directory
                    case_dir.rmdir()
                    logger.info(f"🗑️  Deleted case directory: {case_dir}")
            
            return deleted_count
        
        except Exception as e:
            logger.error(f"❌ Failed to delete case files: {e}")
            return deleted_count


# Global file handler instance
file_handler = FileHandler()