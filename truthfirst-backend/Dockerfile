# truthfirst-backend/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for OpenCV (Video) and WeasyPrint (PDFs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    libcairo2 \
    libpango-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    fonts-dejavu-core \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for Docker layer caching
COPY requirements.txt .

# 🚨 NEW: Strip torch from requirements.txt so it doesn't download 3GB of NVIDIA drivers
RUN sed -i '/torch==/d' requirements.txt && \
    sed -i '/torchvision==/d' requirements.txt

# CRITICAL: Force CPU-only PyTorch installation to keep image size small
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install remaining dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Ensure uploads and temp directories exist
RUN mkdir -p uploads temp

# Expose port
EXPOSE 8000

# Download models on startup, then launch FastAPI
CMD python download_models.py && uvicorn main:app --host 0.0.0.0 --port 8000