import torch
import torch.nn as nn
from torchvision import models, transforms
import cv2
import numpy as np
from PIL import Image
import mediapipe as mp
import logging

logger = logging.getLogger(__name__)


# ===============================
# Feature Extractor (ResNeXt-50)
# ===============================
class FeatureExtractor(nn.Module):
    """
    Spatial feature extractor ("Eye")
    ResNeXt-50 (32x4d) with final FC layer removed.
    Outputs 2048-dim feature vector per frame.
    """

    def __init__(self):
        super().__init__()
        weights = models.ResNeXt50_32X4D_Weights.DEFAULT
        base = models.resnext50_32x4d(weights=weights)
        self.features = nn.Sequential(*list(base.children())[:-1])

    def forward(self, x):
        # (B, 3, 224, 224) -> (B, 2048)
        return self.features(x).flatten(start_dim=1)


# ===============================
# Temporal Classifier (LSTM)
# ===============================
class DeepfakeLSTM(nn.Module):
    """
    Temporal classifier ("Brain")
    Matches training configuration (V2 / Nuclear-compatible).
    """

    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=2048,
            hidden_size=256,
            num_layers=2,
            batch_first=True,
            dropout=0.6
        )
        self.fc = nn.Sequential(
            nn.Linear(256, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 1)
        )

    def forward(self, x):
        # x: (B, 32, 2048)
        self.lstm.flatten_parameters()
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])  # last timestep


# ===============================
# Video Detector
# ===============================
class VideoDetector:
    """
    TruthFirst Video Deepfake Detector
    Architecture:
      - ResNeXt-50 (feature extractor)
      - LSTM (temporal classifier)

    Inference Requirements:
      - 32 uniformly sampled frames
      - MediaPipe face detection
      - 10% context padding
      - 224x224 resize
      - ImageNet normalization
    """

    SEQ_LEN = 32

    def __init__(self, weights_path: str, device: str = "cpu"):
        self.device = device
        logger.info(f"🎬 Initializing VideoDetector on {self.device}")

        # Load models
        self.extractor = FeatureExtractor().to(self.device)
        self.lstm = DeepfakeLSTM().to(self.device)

        # state = torch.load(weights_path, map_location=self.device)
        state = torch.load(weights_path, map_location=self.device, weights_only=True)
        self.lstm.load_state_dict(state)

        self.extractor.eval()
        self.lstm.eval()

        logger.info("👁️  ResNeXt-50 loaded")
        logger.info("🧠 LSTM loaded")

        # MediaPipe face detection
        self.mp_face = mp.solutions.face_detection
        self.face_detector = self.mp_face.FaceDetection(
            model_selection=1,
            min_detection_confidence=0.5
        )

        # ImageNet normalization
        self.preprocess = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

    # -------------------------------
    # Frame Sampling + Face Extraction
    # -------------------------------
    def _extract_faces(self, video_path: str):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return None

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames <= 0:
            cap.release()
            return None

        indices = np.linspace(
            0, total_frames - 1, self.SEQ_LEN, dtype=int
        )

        faces = []

        for idx in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if not ret:
                continue

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_detector.process(rgb)

            if not results.detections:
                continue

            det = results.detections[0]
            bbox = det.location_data.relative_bounding_box
            h, w, _ = rgb.shape

            # 10% padding
            pad_x = int(bbox.width * w * 0.1)
            pad_y = int(bbox.height * h * 0.1)

            x1 = max(0, int(bbox.xmin * w) - pad_x)
            y1 = max(0, int(bbox.ymin * h) - pad_y)
            x2 = min(w, int((bbox.xmin + bbox.width) * w) + pad_x)
            y2 = min(h, int((bbox.ymin + bbox.height) * h) + pad_y)

            face = rgb[y1:y2, x1:x2]
            if face.size == 0:
                continue

            pil = Image.fromarray(face)
            tensor = self.preprocess(pil)
            faces.append(tensor)

        cap.release()

        if len(faces) < self.SEQ_LEN:
            return None

        return torch.stack(faces[:self.SEQ_LEN]).to(self.device)

    # -------------------------------
    # Public API
    # -------------------------------
    def analyze(self, video_path: str) -> dict:
        """
        Returns:
          {
            status,
            verdict,
            confidence,
            fake_probability,
            frames_analyzed
          }
        """
        try:
            frames = self._extract_faces(video_path)
            if frames is None:
                return {
                    "status": "error",
                    "reason": "No sufficient faces detected in video"
                }

            with torch.no_grad():
                feats = self.extractor(frames)           # (32, 2048)
                feats = feats.unsqueeze(0)               # (1, 32, 2048)
                logits = self.lstm(feats)
                prob = torch.sigmoid(logits).item()

            fake_pct = prob * 100
            is_fake = fake_pct > 50

            verdict = "DEEPFAKE" if is_fake else "GENUINE"
            confidence = fake_pct if is_fake else (100 - fake_pct)

            logger.info(
                f"🎬 Video result: {verdict} ({confidence:.2f}%)"
            )

            return {
                "status": "success",
                "verdict": verdict,
                "confidence": round(confidence, 2),
                "fake_probability": round(fake_pct, 2),
                "frames_analyzed": self.SEQ_LEN
            }

        except Exception as e:
            logger.exception("❌ Video analysis failed")
            return {
                "status": "error",
                "reason": str(e)
            }
