# =====================================================================
# Production Dockerfile for AI Music Compositor (FastAPI Backend)
# =====================================================================
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Install essential system audio & C build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libsndfile1 \
    fluidsynth \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first for optimal Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Ensure storage directories exist
RUN mkdir -p storage/compositions soundfonts

EXPOSE 8000

# Launch Uvicorn with dynamic Render PORT support
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}"]
