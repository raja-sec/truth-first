# """
# Model Loader Service - Singleton Pattern
# Ensures ImageDetector is loaded once and reused across requests
# """
# from typing import Optional
# from models.image_detector import ImageDetector

# # ADD THIS (new)
# from models.video_detector import VideoDetector

# from config import settings
# import logging
# import os
# from models.url_detector import URLDetector
# from models.email_detector import EmailDetector




# logger = logging.getLogger(__name__)


# class ModelLoader:
#     _instance: Optional['ModelLoader'] = None
#     _image_detector: Optional[ImageDetector] = None
#     _video_detector: Optional[VideoDetector] = None
#     _url_detector: Optional[URLDetector] = None  
#     _email_detector: Optional[EmailDetector] = None 

    
#     def __new__(cls):
#         if cls._instance is None:
#             cls._instance = super(ModelLoader, cls).__new__(cls)
#             cls._instance._video_model_available = os.path.exists(
#                 settings.VIDEO_MODEL_PATH
#             )
#             cls._instance._email_model_available = os.path.exists(
#                 settings.EMAIL_MODEL_PATH
#             )

#         return cls._instance

    
#     def load_video_detector(self) -> VideoDetector:
#         """
#         Load VideoDetector if available.
#         Lazy loads on first request.
#         Soft-fails if model is missing.
#         """
#         if not self._video_model_available:
#             raise RuntimeError(
#                 "Video analysis is unavailable. "
#                 "Video model file not found."
#             )

#         if self._video_detector is None:
#             logger.info("🔄 Initializing VideoDetector for the first time...")
#             try:
#                 self._video_detector = VideoDetector(
#                     weights_path=settings.VIDEO_MODEL_PATH,
#                     device=settings.model_device
#                 )
#                 logger.info("✅ VideoDetector loaded successfully")
#             except Exception as e:
#                 logger.error(f"❌ Failed to load VideoDetector: {e}")
#                 raise RuntimeError(f"Video model loading failed: {e}")

#         return self._video_detector
    
#     def load_image_detector(self) -> ImageDetector:
#         """
#         Load ImageDetector if not already loaded.
#         Returns cached instance on subsequent calls.
#         """
#         if self._image_detector is None:
#             logger.info("🔄 Initializing ImageDetector for the first time...")
#             try:
#                 self._image_detector = ImageDetector(
#                     model_path=settings.IMAGE_MODEL_PATH,
#                     device=settings.model_device
#                 )
#                 logger.info(f"✅ ImageDetector loaded successfully on device: {settings.model_device}")
#             except Exception as e:
#                 logger.error(f"❌ Failed to load ImageDetector: {e}")
#                 raise RuntimeError(f"Image model loading failed: {str(e)}")

#         return self._image_detector

#     def is_video_available(self) -> bool:
#         """Check if video model exists on disk"""
#         return self._video_model_available

        
#     def is_loaded(self) -> bool:
#         """Check if ImageDetector is loaded"""
#         return self._image_detector is not None
    
#     def unload(self):
#         """Unload all models (useful for testing or cleanup)"""
#         if self._image_detector is not None:
#             logger.info("🗑️ Unloading ImageDetector...")
#             self._image_detector = None

#         if self._video_detector is not None:
#             logger.info("🗑️ Unloading VideoDetector...")
#             self._video_detector = None
            
#     def load_url_detector(self) -> URLDetector:
#         """
#         Load URLDetector if not already loaded.
#         Uses multi-API threat intelligence (VT + GSB + URLScan).
#         Soft-fails if API keys are missing.
#         """
#         if self._url_detector is None:
#             logger.info("🔄 Initializing URLDetector...")
#             try:
#                 vt_keys = [
#                     settings.VT_KEY_1,
#                     settings.VT_KEY_2,
#                     settings.VT_KEY_3,
#                 ]

#                 self._url_detector = URLDetector(
#                     vt_keys=vt_keys,
#                     gsb_key=settings.GSB_API_KEY,
#                     urlscan_key=settings.URLSCAN_API_KEY,
#                 )
#                 logger.info("✅ URLDetector loaded successfully")
#             except Exception as e:
#                 logger.error(f"❌ Failed to load URLDetector: {e}")
#                 raise RuntimeError(f"URL detector loading failed: {e}")

#         return self._url_detector
    
#     def load_email_detector(self) -> EmailDetector:
#         """
#         Load EmailDetector if not already loaded.
#         Uses BERT-based phishing detection + URL intelligence.
#         """
#         if not self._email_model_available:
#             raise RuntimeError(
#                 f"Email analysis unavailable. "
#                 f"BERT model not found at {settings.EMAIL_MODEL_PATH}"
#             )

#         if self._email_detector is None:
#             logger.info("🔄 Initializing EmailDetector for the first time...")
#             try:
#                 self._email_detector = EmailDetector(
#                     model_path=settings.EMAIL_MODEL_PATH
#                 )
#                 logger.info("✅ EmailDetector loaded successfully")
#             except Exception as e:
#                 logger.error(f"❌ Failed to load EmailDetector: {e}")
#                 raise RuntimeError(f"Email detector loading failed: {e}")

#         return self._email_detector
    
    
#     def is_url_available(self) -> bool:
#         return any([
#             settings.VT_KEY_1,
#             settings.VT_KEY_2,
#             settings.VT_KEY_3,
#             settings.GSB_API_KEY,
#             settings.URLSCAN_API_KEY,
#         ])
        
    
    

#     def is_email_available(self) -> bool:
#         """Check if email BERT model exists on disk"""
#         return self._email_model_available



# # Global instance
# model_loader = ModelLoader()


# def get_image_detector() -> ImageDetector:
#     """
#     Dependency injection helper for FastAPI routes.
#     Returns the loaded ImageDetector instance.
#     """
#     return model_loader.load_image_detector()

# def get_video_detector() -> VideoDetector:
#     return model_loader.load_video_detector()


"""
Model Loader Service - Singleton Pattern
Ensures detectors are loaded once and reused across requests
"""
from typing import Optional
import logging
import os

from config import settings
from models.image_detector import ImageDetector
from models.video_detector import VideoDetector
from models.url_detector import URLDetector
from models.email_detector import EmailDetector

logger = logging.getLogger(__name__)

class ModelLoader:
    _instance: Optional['ModelLoader'] = None
    _image_detector: Optional[ImageDetector] = None
    _video_detector: Optional[VideoDetector] = None
    _url_detector: Optional[URLDetector] = None  
    _email_detector: Optional[EmailDetector] = None 

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
            cls._instance._video_model_available = os.path.exists(
                settings.VIDEO_MODEL_PATH
            )
            # FIXED: Uses the new BERT_MODEL_DIR from config.py
            cls._instance._email_model_available = os.path.exists(
                settings.BERT_MODEL_DIR
            )
        return cls._instance

    def load_video_detector(self) -> VideoDetector:
        """
        Load VideoDetector if available.
        Lazy loads on first request.
        """
        if not self._video_model_available:
            raise RuntimeError(
                "Video analysis is unavailable. Video model file not found."
            )

        if self._video_detector is None:
            logger.info("Initializing VideoDetector...")
            try:
                self._video_detector = VideoDetector(
                    weights_path=settings.VIDEO_MODEL_PATH,
                    device=settings.model_device
                )
                logger.info("VideoDetector loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load VideoDetector: {e}")
                raise RuntimeError(f"Video model loading failed: {e}")

        return self._video_detector
    
    def load_image_detector(self) -> ImageDetector:
        """
        Load ImageDetector if not already loaded.
        Returns cached instance on subsequent calls.
        """
        if self._image_detector is None:
            logger.info("Initializing ImageDetector...")
            try:
                self._image_detector = ImageDetector(
                    model_path=settings.IMAGE_MODEL_PATH,
                    device=settings.model_device
                )
                logger.info(f"ImageDetector loaded successfully on device: {settings.model_device}")
            except Exception as e:
                logger.error(f"Failed to load ImageDetector: {e}")
                raise RuntimeError(f"Image model loading failed: {str(e)}")

        return self._image_detector

    def is_video_available(self) -> bool:
        """Check if video model exists on disk"""
        return self._video_model_available
        
    def is_loaded(self) -> bool:
        """Check if ImageDetector is loaded"""
        return self._image_detector is not None
    
    def unload(self):
        """Unload all models (useful for testing or cleanup)"""
        if self._image_detector is not None:
            logger.info("Unloading ImageDetector...")
            self._image_detector = None

        if self._video_detector is not None:
            logger.info("Unloading VideoDetector...")
            self._video_detector = None
            
    def load_url_detector(self) -> URLDetector:
        """
        Load URLDetector if not already loaded.
        Uses multi-API threat intelligence.
        """
        if self._url_detector is None:
            logger.info("Initializing URLDetector...")
            try:
                vt_keys = [
                    settings.VT_KEY_1,
                    settings.VT_KEY_2,
                    settings.VT_KEY_3,
                ]

                self._url_detector = URLDetector(
                    vt_keys=vt_keys,
                    gsb_key=settings.GSB_API_KEY,
                    urlscan_key=settings.URLSCAN_API_KEY,
                )
                logger.info("URLDetector loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load URLDetector: {e}")
                raise RuntimeError(f"URL detector loading failed: {e}")

        return self._url_detector
    
    def load_email_detector(self) -> EmailDetector:
        """
        Load EmailDetector if not already loaded.
        Uses BERT-based phishing detection + URL intelligence.
        """
        if not self._email_model_available:
            raise RuntimeError(
                f"Email analysis unavailable. "
                f"BERT model not found at {settings.BERT_MODEL_DIR}"
            )

        if self._email_detector is None:
            logger.info("Initializing EmailDetector...")
            try:
                # FIXED: Uses the new BERT_MODEL_DIR
                self._email_detector = EmailDetector(
                    model_path=settings.BERT_MODEL_DIR
                )
                logger.info("EmailDetector loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load EmailDetector: {e}")
                raise RuntimeError(f"Email detector loading failed: {e}")

        return self._email_detector
    
    def is_url_available(self) -> bool:
        return any([
            settings.VT_KEY_1,
            settings.VT_KEY_2,
            settings.VT_KEY_3,
            settings.GSB_API_KEY,
            settings.URLSCAN_API_KEY,
        ])
        
    def is_email_available(self) -> bool:
        """Check if email BERT model exists on disk"""
        return self._email_model_available


# Global instance
model_loader = ModelLoader()

def get_image_detector() -> ImageDetector:
    """Dependency injection helper for FastAPI routes."""
    return model_loader.load_image_detector()

def get_video_detector() -> VideoDetector:
    """Dependency injection helper for FastAPI routes."""
    return model_loader.load_video_detector()