# 🎵 WaveSmith — AI Music Compositor

> Transform plain natural language prompts into expressive, multi-track MIDI compositions and synthesized 44.1kHz studio WAV audio in real-time.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14.2-black.svg?logo=next.js&logoColor=white)](https://nextjs.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![DSP Engine](https://img.shields.io/badge/DSP-TinySoundFont-purple.svg)](https://github.com/schellingb/tinysoundfont)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)

---

## ✨ Features

- **Natural Language to Music**: Describe musical visions in plain English (*e.g., "Create a melancholic, emotional violin melody in C minor with deep string chords"* or *"Fast energetic Krishna flute with acoustic guitar"*).
- **Resilient Dual-LLM Engine**:
  - **Primary**: Google Gemini (`gemini-3.1-flash-lite`) with structured schema enforcement.
  - **Secondary (Zero-Downtime Failover)**: Groq (`openai/gpt-oss-120b`) handles instantaneous failover if Gemini encounters 503 high-demand surges or quota limits.
- **Full 128 General MIDI Palette**:
  - Supports the entire General MIDI instrument specification (Programs 0–127).
  - Handles lead melodies, counterpoint, polyphonic chord voicings, and pitched percussion (Taiko Drum, Synth Drum, Melodic Tom).
- **Intent-Aware Track Orchestration**:
  - **Solo Mode**: Detects requests for *"only flute"*, *"solo piano"*, or *"just drums"*, generating pure single-voice audio without unwanted background instruments.
  - **Dual-Track Matching**: Supports explicit requests like *"use violin in both melody and harmony tracks"*.
  - **Smart Accompaniment**: Intelligently pairs melody leads with tonally cohesive harmonic voicings.
- **Embedded Studio Audio Synthesis**:
  - Direct in-memory synthesis via `tinysoundfont` and bundled `soundfonts/TimGM6mb.sf2` (5.9MB General MIDI SoundFont bank).
  - Soft peak normalization (`0.94`) and amplitude verification (`_is_audible`) guarantee loud, rich, non-distorted audio.
  - Multi-tier fallback to system FluidSynth CLI and procedural harmonic timbre DSP.
- **Silent-Play Proof Browser Engine**:
  - Preloads audio as an in-memory `blob:` URL on the frontend, completely eliminating cross-origin Range streaming dropouts and silent playback in Chrome/Edge/Safari.
  - One-click direct downloads for both `.wav` and `.mid` files without opening new browser tabs.
- **Real-Time Server-Sent Events (SSE)**:
  - Streams live pipeline status updates stage-by-stage to the browser, eliminating cold-wait latency.
- **Modern WaveSmith Studio UI**:
  - Next.js 14 App Router, Tailwind CSS, Lucide icons, responsive layout, interactive scrubber bar, frequency equalizer visualizer, and piano-roll breakdown cards.

---

## 🏗️ Architecture & Pipeline

```mermaid
flowchart LR
    A["👤 User Prompt"] --> B["1. Key & Intent Extraction"]
    B --> C["2. AI Music Generation\n(Gemini ⇄ Groq Failover)"]
    C --> D["3. MIDI Assembly\n(music21 + Velocity Dynamics)"]
    D --> E["4. SoundFont DSP Synthesis\n(TinySoundFont → 44.1kHz WAV)"]
    E --> F["5. SSE Event Stream &\nIn-Memory Blob Playback"]
```

### Event Streaming Stages

1. `extracting_key`: Sanitizes prompt input and selects harmonic tonality and scale.
2. `generating_notes`: AI agent drafts structured melody notes, chords, tempo (BPM), and meter.
3. `compiling_midi`: Builds `music21` multi-track score, applying humanized dynamic velocity and measure accents.
4. `rendering_wav`: Synthesizes 44.1kHz WAV audio via TinySoundFont engine with peak normalization.
5. `completed`: Delivers structured composition breakdown, direct download links, and audio stream.

---

## 📂 Project Structure

```text
WaveSmith-AI-Music-Composer/
├── app.py                     # Production FastAPI service with SSE & download endpoints
├── music.py                   # LangGraph state machine & LLM client failover setup
├── component.py               # 128 GM instrument resolver, composer agent & MIDI compiler
├── audio_synth.py             # Studio SoundFont audio synthesizer with audibility guards
├── main.py                    # Interactive terminal/CLI runner
├── requirements.txt           # Python backend dependencies
├── Dockerfile                 # Multi-stage production container for Render
├── render.yaml                # Render Infrastructure-as-Code blueprint
├── vercel.json                # Vercel deployment configuration
├── .dockerignore              # Docker build exclusions
├── .gitignore                 # Git ignore rules
├── soundfonts/
│   ├── TimGM6mb.sf2           # Bundled 5.9MB General MIDI SoundFont bank (tracked in git)
│   └── default.sf2            # Optional large local SoundFont bank (151MB, gitignored)
├── storage/
│   └── compositions/          # Cache for generated .mid and .wav files
└── frontend/                  # Next.js 14 web application
    ├── src/
    │   ├── app/
    │   │   ├── page.tsx       # WaveSmith studio dashboard & state orchestrator
    │   │   ├── layout.tsx     # Root layout and metadata
    │   │   └── globals.css    # Global Tailwind styles
    │   ├── components/
    │   │   ├── AudioPlayerCard.tsx        # Player with blob preloader, scrubber & direct download
    │   │   ├── CompositionDetailsCard.tsx # Visual melody notes & harmonic voicing viewer
    │   │   ├── LiveStreamPipeline.tsx     # Real-time 5-stage progress stepper
    │   │   ├── PromptCard.tsx             # Studio input controls & style picker
    │   │   ├── Header.tsx                 # Studio navigation header
    │   │   └── HeroWaveBackground.tsx     # Dynamic background aesthetic
    │   ├── services/
    │   │   └── streamService.ts           # EventSource and Fetch SSE stream client
    │   ├── types/
    │   │   └── music.ts                   # TypeScript interfaces and composition schemas
    │   └── lib/
    │       └── utils.ts                   # Formatting helpers and class mergers
    ├── package.json
    ├── tailwind.config.ts
    └── tsconfig.json
```

---

## 🚀 Getting Started

### Prerequisites

- **Python**: 3.10, 3.11, or 3.12
- **Node.js**: 18.x or 20.x
- **API Keys**:
  - [Google AI Studio Key](https://aistudio.google.com/) (`GOOGLE_API_KEY`)
  - [Groq Cloud Key](https://console.groq.com/) (`GROQ_API_KEY`)

---

### 1. Backend Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/shyamgadhiya/WaveSmith-AI-Music-Composer.git
   cd WaveSmith-AI-Music-Composer
   ```

2. **Create and activate a virtual environment**:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   Create a `.env` file in the project root:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key_here
   GROQ_API_KEY=your_groq_api_key_here
   ```

5. **Start the FastAPI backend server**:
   ```bash
   uvicorn app:app --reload --port 8000
   ```
   *The API will be accessible at `http://127.0.0.1:8000` (Interactive Swagger docs at `http://127.0.0.1:8000/docs`).*

---

### 2. Frontend Setup

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install frontend packages**:
   ```bash
   npm install
   ```

3. **Set local backend URL**:
   Create a `frontend/.env.local` file:
   ```env
   NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
   ```

4. **Start the Next.js development server**:
   ```bash
   npm run dev
   ```
   *Open [http://localhost:3000](http://localhost:3000) in your browser.*

---

## 📡 API Reference

### 1. SSE Real-Time Composition Stream
`GET /api/v1/compose/stream`

Yields Server-Sent Events as each pipeline step finishes.

**Query Parameters:**
| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `prompt` | string | Yes | — | Musical description (3–250 chars) |
| `style` | string | No | `"Romantic era"` | Musical aesthetic or genre |

**Example SSE Events:**
```text
event: extracting_key
data: {"stage": "extracting_key", "message": "Sanitizing input and preparing harmonic key palette..."}

event: generating_notes
data: {"stage": "generating_notes", "message": "AI composer writing melody, chords, tempo, and rhythm..."}

event: compiling_midi
data: {"stage": "compiling_midi", "message": "Assembling music21 score and applying humanized velocity dynamics..."}

event: rendering_wav
data: {"stage": "rendering_wav", "message": "Synthesizing 44.1kHz audio via FluidSynth / DSP engine..."}

event: completed
data: {
  "stage": "completed",
  "session_id": "c1f72d42-498c-4a39-9d7a-12903b418a09",
  "target_seconds": 12.0,
  "composition": {
    "tempo_bpm": 84,
    "time_signature": "4/4",
    "melody_instrument": "Violin",
    "harmony_instrument": "Violin",
    "melody": [{"pitch": "D5", "duration": 1.5}],
    "harmony": [{"pitches": ["D3", "F#3", "A3"], "duration": 4.0}]
  },
  "midi_download_url": "/api/v1/download/c1f72d42-498c-4a39-9d7a-12903b418a09/midi",
  "audio_stream_url": "/api/v1/download/c1f72d42-498c-4a39-9d7a-12903b418a09/audio"
}
```

### 2. Direct Downloads & Audio Streaming
- **Audio Stream**: `GET /api/v1/download/{session_id}/audio` (Streams inline with `Accept-Ranges` and exposed CORS headers)
- **Audio Download**: `GET /api/v1/download/{session_id}/audio?download=true` (Returns `Content-Disposition: attachment; filename="composition_...wav"`)
- **MIDI Download**: `GET /api/v1/download/{session_id}/midi` (Returns `Content-Disposition: attachment; filename="composition_...mid"`)

---

## 🎼 Prompt Examples to Try

| Style | Example Prompt | Orchestration Result |
|---|---|---|
| **Classical Violin** | `"Create a melancholic, emotional violin melody in C minor with deep string chords"` | Lead: Violin · Accomp: String Ensemble 1 |
| **Dual Violin** | `"Create a violin melody in D minor also use violin in both harmony and melody tracks"` | Lead: Violin · Accomp: Violin |
| **Solo Flute** | `"Give me music of flute only for 15 seconds"` | Lead: Flute · Accomp: None (Solo) |
| **Devotional** | `"Create an intricate Krishna style flute melody in D major"` | Lead: Flute · Accomp: Nylon String Guitar |
| **Rhythmic Beat** | `"Give me just beat of drum for 10 seconds"` | Lead: Synth Drum · Accomp: None (Solo) |
| **Baroque Invention** | `"Create a two-part counterpoint invention in D Dorian for harpsichord"` | Lead: Harpsichord · Accomp: Harpsichord |

---

## 🛠️ Tech Stack

- **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/) with asynchronous background tasks and streaming responses.
- **Agent Orchestration**: [LangGraph](https://langchain-ai.github.io/langgraph/) & [LangChain Core](https://python.langchain.com/).
- **LLM Models**: Google Gemini (`gemini-3.1-flash-lite`) + Groq (`openai/gpt-oss-120b`).
- **Music Representation**: [music21](https://web.mit.edu/music21/) & [pretty_midi](https://github.com/craffel/pretty-midi).
- **Audio Synthesis**: [tinysoundfont](https://github.com/schellingb/tinysoundfont), [soundfile](https://pysoundfile.readthedocs.io/), and [FluidSynth](https://www.fluidsynth.org/).
- **Frontend Framework**: [Next.js 14](https://nextjs.org/) (React 18, TypeScript, Tailwind CSS).
- **Icons & Styling**: [Lucide React](https://lucide.dev/), Tailwind CSS with custom glassmorphism design system.

---

## ☁️ Deployment Guide

### Deploying Backend to Render (Docker)
1. Fork or push this repository to GitHub.
2. In the [Render Dashboard](https://dashboard.render.com/), click **New +** → **Web Service**.
3. Select your repository `WaveSmith-AI-Music-Composer`.
4. Choose the **Docker** runtime (Render automatically detects `Dockerfile`).
5. Set the required **Environment Variables**:
   - `GOOGLE_API_KEY`: Your Gemini API key
   - `GROQ_API_KEY`: Your Groq API key
6. Click **Create Web Service**. Render builds the container with all audio build dependencies and launches Uvicorn on `$PORT`.
7. Copy your production URL (e.g., `https://wavesmith-backend.onrender.com`).

### Deploying Frontend to Vercel
1. In the [Vercel Dashboard](https://vercel.com/), click **Add New...** → **Project**.
2. Import the `WaveSmith-AI-Music-Composer` repository.
3. In **Build and Output Settings**, set **Root Directory** to `frontend`.
4. Under **Environment Variables**, add:
   - `NEXT_PUBLIC_BACKEND_URL`: `https://wavesmith-backend.onrender.com` (your Render service URL without trailing slash)
5. Click **Deploy**.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
