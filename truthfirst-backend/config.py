# from pydantic_settings import BaseSettings
# from typing import List
# from pathlib import Path
# import os
# from pydantic import Field
# from pathlib import Path
# BASE_DIR = Path(__file__).resolve().parent

# BASE_DIR = Path(__file__).resolve().parent
# UPLOAD_DIR = BASE_DIR / "uploads"

# class Settings(BaseSettings):
#     # App
#     APP_NAME: str = "TruthFirst"
#     APP_ENV: str = "development"
#     DEBUG: bool = True
#     HOST: str = "0.0.0.0"
#     PORT: int = 8000
    
#     # ---------------------------------------------------------
#     # AI MODEL PATHS (Forced Absolute Paths)
#     # ---------------------------------------------------------
#     IMAGE_MODEL_PATH: str = str(BASE_DIR / "models" / "weights" / "efficientnet_b0.pth")
#     VIDEO_MODEL_PATH: str = str(BASE_DIR / "models" / "weights" / "truthfirst_video_best.pth")
#     BERT_MODEL_DIR: str = str(BASE_DIR / "models" / "email_detection" / "phishing_bert_final_v1")

#     # CORS
#     CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

#     @property
#     def cors_origins_list(self) -> List[str]:
#         return [o.strip() for o in self.CORS_ORIGINS.split(",")]

#     # Model
#     MODEL_PATH: str
#     DEVICE: str = "cuda"

#     @property
#     def model_device(self) -> str:
#         if self.DEVICE == "cuda":
#             try:
#                 import torch
#                 return "cuda" if torch.cuda.is_available() else "cpu"
#             except ImportError:
#                 return "cpu"
#         return self.DEVICE
    
#     # Video (Phase 9A)
#     # VIDEO_MODEL_PATH: str = "models/weights/truthfirst_video_best.pth"
#     MAX_VIDEO_SIZE_MB: int = 50
#     MAX_VIDEO_DURATION: int = 60  # seconds
#     ALLOWED_VIDEO_TYPES: str = "video/mp4,video/x-msvideo,video/quicktime"
#     TEMP_DIR: str = "temp"
    
#     EMAIL_MODEL_PATH: str = Field(
#         default="models/email_detection/phishing_bert_final_v1",
#         description="Path to email phishing BERT model"
#     )

#     # API Keys (Optional - Soft fails if missing)
#     GSB_API_KEY: str | None = None
#     VT_KEY_1: str | None = None
#     VT_KEY_2: str | None = None
#     VT_KEY_3: str | None = None
#     URLSCAN_API_KEY: str | None = None

#     @property
#     def vt_keys(self) -> List[str]:
#         return [k for k in [self.VT_KEY_1, self.VT_KEY_2, self.VT_KEY_3] if k]

#     @property
#     def max_video_size_bytes(self) -> int:
#         return self.MAX_VIDEO_SIZE_MB * 1024 * 1024

#     @property
#     def allowed_video_types_list(self) -> List[str]:
#         return [t.strip().lower() for t in self.ALLOWED_VIDEO_TYPES.split(",")]

#     # File Upload
#     MAX_FILE_SIZE_MB: int = 10
#     ALLOWED_IMAGE_TYPES: str = "jpg,jpeg,png,webp"
#     UPLOAD_DIR: str = "uploads"
#     FILE_RETENTION_DAYS: int = 30

#     @property
#     def max_file_size_bytes(self) -> int:
#         return self.MAX_FILE_SIZE_MB * 1024 * 1024

#     @property
#     def allowed_image_types_list(self) -> List[str]:
#         return [t.strip().lower() for t in self.ALLOWED_IMAGE_TYPES.split(",")]

#     # Database
#     DATABASE_URL: str

#     # Security (Phase 5)
#     SECRET_KEY: str

#     # SMTP Email Settings (Phase 5 - Gmail)
#     SMTP_HOST: str = "smtp.gmail.com"
#     SMTP_PORT: int = 587
#     SMTP_USERNAME: str
#     SMTP_PASSWORD: str
#     SMTP_FROM_EMAIL: str
#     SMTP_FROM_NAME: str = "TruthFirst Verification"

#     class Config:
#         env_file = ".env"
#         case_sensitive = True

# settings = Settings()

# # Ensure dirs exist
# Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
# Path("templates").mkdir(parents=True, exist_ok=True)
# Path(settings.TEMP_DIR).mkdir(parents=True, exist_ok=True)

# def validate_model_file():
#     """Validate required model files."""
#     # Image model (required)
#     if not os.path.exists(settings.MODEL_PATH):
#         raise FileNotFoundError(
#             f"❌ Image model not found at: {settings.MODEL_PATH}\n"
#             f"Please ensure the image model exists before starting the server."
#         )
#     print(f"✅ Image model found: {settings.MODEL_PATH}")

#     # Video model (optional)
#     if not os.path.exists(settings.VIDEO_MODEL_PATH):
#         print(
#             f"⚠️  Video model not found at: {settings.VIDEO_MODEL_PATH}\n"
#             f"   Video analysis will be unavailable until the model is placed."
#         )
#     else:
#         print(f"✅ Video model found: {settings.VIDEO_MODEL_PATH}")

from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path
import os
from pydantic import Field

BASE_DIR = Path(__file__).resolve().parent

class Settings(BaseSettings):
    # App
    APP_NAME: str = "TruthFirst"
    APP_ENV: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # ---------------------------------------------------------
    # AI MODEL PATHS (Forced Absolute Paths)
    # ---------------------------------------------------------
    IMAGE_MODEL_PATH: str = str(BASE_DIR / "models" / "weights" / "efficientnet_b0.pth")
    VIDEO_MODEL_PATH: str = str(BASE_DIR / "models" / "weights" / "truthfirst_video_best.pth")
    BERT_MODEL_DIR: str = str(BASE_DIR / "models" / "email_detection" / "phishing_bert_final_v1")

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]

    # Device
    DEVICE: str = "cuda"

    @property
    def model_device(self) -> str:
        if self.DEVICE == "cuda":
            try:
                import torch
                return "cuda" if torch.cuda.is_available() else "cpu"
            except ImportError:
                return "cpu"
        return self.DEVICE
    
    # Video 
    MAX_VIDEO_SIZE_MB: int = 50
    MAX_VIDEO_DURATION: int = 60  # seconds
    ALLOWED_VIDEO_TYPES: str = "video/mp4,video/x-msvideo,video/quicktime"
    TEMP_DIR: str = str(BASE_DIR / "temp")

    # API Keys (Optional - Soft fails if missing)
    GSB_API_KEY: str | None = None
    VT_KEY_1: str | None = None
    VT_KEY_2: str | None = None
    VT_KEY_3: str | None = None
    URLSCAN_API_KEY: str | None = None

    @property
    def vt_keys(self) -> List[str]:
        return [k for k in [self.VT_KEY_1, self.VT_KEY_2, self.VT_KEY_3] if k]

    @property
    def max_video_size_bytes(self) -> int:
        return self.MAX_VIDEO_SIZE_MB * 1024 * 1024

    @property
    def allowed_video_types_list(self) -> List[str]:
        return [t.strip().lower() for t in self.ALLOWED_VIDEO_TYPES.split(",")]

    # File Upload
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_IMAGE_TYPES: str = "jpg,jpeg,png,webp"
    UPLOAD_DIR: str = str(BASE_DIR / "uploads")
    FILE_RETENTION_DAYS: int = 30

    @property
    def max_file_size_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    @property
    def allowed_image_types_list(self) -> List[str]:
        return [t.strip().lower() for t in self.ALLOWED_IMAGE_TYPES.split(",")]

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str

    # SMTP Email Settings
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    SMTP_FROM_EMAIL: str
    SMTP_FROM_NAME: str = "TruthFirst Verification"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Ensure dirs exist (Using absolute paths)
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
Path(BASE_DIR / "templates").mkdir(parents=True, exist_ok=True)
Path(settings.TEMP_DIR).mkdir(parents=True, exist_ok=True)

def validate_model_file():
    """Validate required model files using absolute paths."""
    # Image model (required)
    if not os.path.exists(settings.IMAGE_MODEL_PATH):
        raise FileNotFoundError(
            f"❌ Image model not found at: {settings.IMAGE_MODEL_PATH}\n"
            f"Please ensure the image model exists before starting the server."
        )
    print(f"✅ Image model found: {settings.IMAGE_MODEL_PATH}")

    # Video model (optional)
    if not os.path.exists(settings.VIDEO_MODEL_PATH):
        print(
            f"⚠️  Video model not found at: {settings.VIDEO_MODEL_PATH}\n"
            f"   Video analysis will be unavailable until the model is placed."
        )
    else:
        print(f"✅ Video model found: {settings.VIDEO_MODEL_PATH}")
        
    # BERT model (optional)
    if not os.path.exists(settings.BERT_MODEL_DIR):
        print(
            f"⚠️  BERT model directory not found at: {settings.BERT_MODEL_DIR}\n"
            f"   Email analysis will be unavailable until the model is placed."
        )
    else:
        print(f"✅ BERT model found: {settings.BERT_MODEL_DIR}")