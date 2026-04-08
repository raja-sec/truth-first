import os
import requests
from pathlib import Path

# ==========================================
# TRUTHFIRST MODEL DOWNLOADER
# Maps flat Hugging Face URLs to strict local directories
# ==========================================

REPO_ID = "raja-sec/truthfirst-models"  

MODELS_TO_DOWNLOAD = {
    "models/weights/efficientnet_b0.pth": f"https://huggingface.co/{REPO_ID}/resolve/main/efficientnet_b0.pth?download=true",
    
    "models/weights/truthfirst_video_best.pth": f"https://huggingface.co/{REPO_ID}/resolve/main/truthfirst_video_best.pth?download=true",
    
    "models/email_detection/phishing_bert_final_v1/config.json": f"https://huggingface.co/{REPO_ID}/resolve/main/phishing_bert_final_v1/config.json?download=true",
    "models/email_detection/phishing_bert_final_v1/model.safetensors": f"https://huggingface.co/{REPO_ID}/resolve/main/phishing_bert_final_v1/model.safetensors?download=true",
    "models/email_detection/phishing_bert_final_v1/tokenizer_config.json": f"https://huggingface.co/{REPO_ID}/resolve/main/phishing_bert_final_v1/tokenizer_config.json?download=true",
    "models/email_detection/phishing_bert_final_v1/vocab.txt": f"https://huggingface.co/{REPO_ID}/resolve/main/phishing_bert_final_v1/vocab.txt?download=true",
}

def download_file(url: str, dest_path: str):
    """Downloads a file with a progress indicator."""
    path = Path(dest_path)
    
    # Skip if file already exists and has a size > 0
    if path.exists() and path.stat().st_size > 0:
        print(f"Already exists: {dest_path}")
        return

    # Create parent directories if they don't exist
    path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Downloading {dest_path}...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(dest_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"✅ Successfully downloaded: {dest_path}")
    except Exception as e:
        print(f"❌ Failed to download {dest_path}: {e}")

if __name__ == "__main__":
    print("Starting model weight downloads...")
    for local_path, download_url in MODELS_TO_DOWNLOAD.items():
        download_file(download_url, local_path)
    print("All models are ready!")