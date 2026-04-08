import torch
import torch.nn as nn
from torchvision import models, transforms
import cv2
import numpy as np
from PIL import Image
import mediapipe as mp
import io

class ImageDetector:
    def __init__(self, model_path, device=None):
        """
        Production Image Forensic Module (Validated Dec 14, 2025)
        Accuracy: ~92.8% (Real: 90.6%, Fake: 94.9%)
        """
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        self.model_path = model_path
        
        # --- TUNED THRESHOLDS (From Colab Validation) ---
        self.FREQ_THRESHOLD = 118.15
        self.ART_THRESHOLD = 167.05
        
        # Logic Gate Configs
        self.SHIELD_THRESHOLD = 25.0    # Trust CNN if Fake% < 25%
        self.RESCUE_WEAK_ART = 200.0    # Rescue if CNN < 75% Conf & Art > 200
        self.RESCUE_SUPER_ART = 500.0   # Rescue if Art > 500 (Always)
        self.VETO_ART_CRITICAL = 20.0   # Veto Real -> Fake if Art < 20
        
        # 1. Dual-Mode Face Detection
        self.mp_face_detection = mp.solutions.face_detection
        self.detector_full = self.mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.4)
        self.detector_short = self.mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.4)
        
        # 2. Load CNN
        print(f"🏗️ Loading Image Forensics Model from {model_path}...")
        try:
            self.model = models.efficientnet_b0(weights=None)
            self.model.classifier[1] = nn.Linear(self.model.classifier[1].in_features, 2)
            state_dict = torch.load(model_path, map_location=self.device)
            self.model.load_state_dict(state_dict)
            self.model.to(self.device)
            self.model.eval()
            
            # Grad-CAM Hooks
            self.target_layer = self.model.features[-1]
            self.gradients = None
            self.activations = None
            self.target_layer.register_forward_hook(self._save_activation)
            self.target_layer.register_full_backward_hook(self._save_gradient)
            
            print("✅ Image Model Loaded.")
        except Exception as e:
            print(f"❌ CRITICAL: Model load failed. {e}")
            raise e

        # 3. Preprocessing
        self.stats = ([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        self.preprocess = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(*self.stats)
        ])

    def _save_activation(self, module, input, output): self.activations = output
    def _save_gradient(self, module, grad_input, grad_output): self.gradients = grad_output[0]

    def _get_frequency_score(self, img):
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            f = np.fft.fft2(gray)
            fshift = np.fft.fftshift(f)
            mag = 20 * np.log(np.abs(fshift) + 1e-8)
            h, w = gray.shape
            mask = np.ones((h, w), np.uint8)
            cv2.circle(mask, (w//2, h//2), 30, 0, -1)
            return np.mean(mag * mask)
        except: return 0.0

    def _get_artifact_score(self, img):
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            var = cv2.Laplacian(gray, cv2.CV_64F).var()
            h, w = gray.shape
            center = gray[h//4 : 3*h//4, w//4 : 3*w//4]
            c_var = cv2.Laplacian(center, cv2.CV_64F).var()
            return abs(var - c_var)
        except: return 0.0

    def _generate_heatmap(self, tensor, original_crop):
        pooled_gradients = torch.mean(self.gradients, dim=[0, 2, 3])
        activation = self.activations[0]
        for i in range(activation.shape[0]):
            activation[i, :, :] *= pooled_gradients[i]
        heatmap = torch.mean(activation, dim=0).cpu().detach().numpy()
        heatmap = np.maximum(heatmap, 0)
        if np.max(heatmap) != 0: heatmap /= np.max(heatmap)
        heatmap_resized = cv2.resize(heatmap, (224, 224))
        heatmap_colored = cv2.applyColorMap(np.uint8(255 * heatmap_resized), cv2.COLORMAP_JET)
        bg_img = cv2.resize(original_crop, (224, 224))
        return cv2.addWeighted(cv2.cvtColor(bg_img, cv2.COLOR_RGB2BGR), 0.6, heatmap_colored, 0.4, 0), heatmap_colored

    def analyze(self, image_bytes):
        # A. Decode
        nparr = np.frombuffer(image_bytes, np.uint8)
        original_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if original_img is None: return {"error": "Invalid Image"}
        original_img_rgb = cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB)
        
        # B. Face Detection
        results = self.detector_full.process(original_img_rgb)
        if not results.detections: results = self.detector_short.process(original_img_rgb)
        
        final_face = original_img_rgb
        face_found = False
        
        if results.detections:
            face_found = True
            detection = results.detections[0]
            bbox = detection.location_data.relative_bounding_box
            h, w, _ = original_img_rgb.shape
            x, y = int(bbox.xmin * w), int(bbox.ymin * h)
            w_box, h_box = int(bbox.width * w), int(bbox.height * h)
            
            # PADDING: 40% (Critical for CNN Context)
            padding = int(h_box * 0.40)
            x = max(0, x - padding)
            y = max(0, y - padding)
            w_box = min(w, w_box + 2*padding)
            h_box = min(h, h_box + 2*padding)
            final_face = original_img_rgb[y:y+h_box, x:x+w_box]

        # C. Inference
        pil_face = Image.fromarray(final_face)
        tensor = self.preprocess(pil_face).unsqueeze(0).to(self.device)
        self.model.zero_grad()
        outputs = self.model(tensor)
        probs = torch.nn.functional.softmax(outputs, dim=1)
        fake_prob = probs[0][0].item() * 100
        real_prob = probs[0][1].item() * 100
        score, idx = torch.max(outputs, 1)
        score.backward()
        
        # D. Math (Full Image)
        math_img = cv2.resize(original_img_rgb, (224, 224))
        freq_score = self._get_frequency_score(math_img)
        art_score = self._get_artifact_score(math_img)

        # E. FUSION LOGIC (PRODUCTION GRADE)
        verdict = "REAL" if real_prob > 50 else "FAKE"
        confidence = max(real_prob, fake_prob)
        flags = []

        freq_fail = freq_score < (self.FREQ_THRESHOLD - 10)
        art_fail_critical = art_score < self.VETO_ART_CRITICAL
        art_fail_suspicious = art_score < (self.ART_THRESHOLD - 20)

        if verdict == "FAKE":
            # GATE 1: SUPER RESCUE
            if art_score > self.RESCUE_SUPER_ART:
                verdict = "REAL"; confidence = 90.0
            # GATE 2: CONDITIONAL RESCUE
            elif confidence < 75.0 and art_score > self.RESCUE_WEAK_ART:
                 verdict = "REAL"; confidence = 75.0
            else:
                flags.append(f"Visual artifacts detected by AI ({fake_prob:.1f}%)")
                if freq_fail: flags.append("Auxiliary: Abnormal smoothness detected")
                if art_fail_suspicious: flags.append("Auxiliary: Inconsistent noise detected")

        else: # Verdict is REAL
            # GATE 3: SHIELD
            if fake_prob < self.SHIELD_THRESHOLD:
                pass 
            else:
                if freq_fail and art_fail_suspicious:
                    verdict = "FAKE"; confidence = 88.0 
                    flags.append("CRITICAL: Multiple Forensic Engines Failed")
                elif art_fail_critical:
                    verdict = "FAKE"; confidence = 80.0
                    flags.append("Critical Noise Inconsistency (Impossible Image)")
                elif freq_fail:
                    if confidence < 90:
                        verdict = "FAKE"; confidence = 65.0
                        flags.append("Abnormal High-Frequency loss")

        # F. Heatmap
        heatmap_overlay, _ = self._generate_heatmap(tensor, final_face)
        _, buffer = cv2.imencode('.jpg', heatmap_overlay)
        heatmap_bytes = buffer.tobytes()

        return {
            "verdict": verdict,
            "confidence": round(confidence, 2),
            "face_found": face_found,
            "flags": flags,
            "metrics": {"cnn_fake": round(fake_prob, 2), "freq": round(freq_score, 2), "art": round(art_score, 2)},
            "heatmap_bytes": heatmap_bytes
        }