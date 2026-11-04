# =====================================================================
# Production Dockerfile for AI Music Compositor (FastAPI Backend)
# =====================================================================
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Install essential system audio & C build dependencies including General MIDI SoundFonts
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    portaudio19-dev \
    libsndfile1 \
    fluidsynth \
    fluid-soundfont-gm \
    timgm6mb-soundfont \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first for optimal Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Ensure storage directories exist and default.sf2 is available
RUN mkdir -p storage/compositions soundfonts && \
    if [ ! -f soundfonts/default.sf2 ]; then \
        if [ -f soundfonts/TimGM6mb.sf2 ]; then \
            ln -sf soundfonts/TimGM6mb.sf2 soundfonts/default.sf2; \
        elif [ -f /usr/share/sounds/sf2/TimGM6mb.sf2 ]; then \
            ln -sf /usr/share/sounds/sf2/TimGM6mb.sf2 soundfonts/default.sf2; \
        elif [ -f /usr/share/sounds/sf2/FluidR3_GM.sf2 ]; then \
            ln -sf /usr/share/sounds/sf2/FluidR3_GM.sf2 soundfonts/default.sf2; \
        fi; \
    fi

EXPOSE 8000

# Launch Uvicorn with dynamic Render PORT support
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}"]

