"""Production FastAPI service for AI Music Compositor."""

import os
import uuid
import time
import json
import asyncio
import threading
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, status
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from music import compose_music, sanitize_user_input, MusicState
from component import composer_agent, midi_converter
from audio_synth import render_midi_to_wav

# Storage directory for generated assets
STORAGE_DIR = Path("storage/compositions")
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="AI Music Compositor API",
    description="LangGraph-powered AI music generator with MIDI and audio synthesis.",
    version="1.0.0"
)

# Enable CORS for frontend web integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Request & Response Models ---
class ComposeRequest(BaseModel):
    prompt: str = Field(
        ...,
        min_length=3,
        max_length=250,
        example="Create a melancholic 15-second string ensemble in C minor"
    )
    style: str = Field(
        default="Romantic era",
        max_length=50,
        example="Romantic era"
    )

class NoteSummary(BaseModel):
    pitch: str
    duration: float

class ChordSummary(BaseModel):
    pitches: List[str]
    duration: float

class CompositionDetails(BaseModel):
    tempo_bpm: int
    time_signature: str
    melody_instrument: str
    harmony_instrument: str
    melody: List[NoteSummary]
    harmony: List[ChordSummary]

class ComposeResponse(BaseModel):
    session_id: str
    target_seconds: float
    composition: CompositionDetails
    midi_download_url: str
    audio_stream_url: Optional[str] = None


# --- Fixed Background Cleanup Utility ---
def cleanup_old_files(file_paths: List[str], delay_seconds: int = 3600):
    """Deletes temporary files after the delay in the background thread."""
    time.sleep(delay_seconds)
    for path in file_paths:
        try:
            if os.path.exists(path):
                os.remove(path)
        except OSError:
            pass


# --- SSE Event Generator ---
async def stream_composition_events(prompt: str, style: str):
    """
    Yields real-time Server-Sent Events (SSE) through each pipeline stage:
    1. extracting_key: input sanitization & harmonic context
    2. generating_notes: LLM musical structure and note generation
    3. compiling_midi: music21 score assembly & velocity dynamics
    4. rendering_wav: audio rendering via FluidSynth / pretty_midi DSP
    5. completed: final payload with metadata and download URLs
    """
    session_id = str(uuid.uuid4())

    def format_sse(event: str, payload: dict) -> str:
        return f"event: {event}\ndata: {json.dumps(payload)}\n\n"

    try:
        # Stage 1: Key selection & sanitization
        safe_input = sanitize_user_input(prompt)
        safe_style = sanitize_user_input(style, max_chars=60)
        yield format_sse("extracting_key", {
            "stage": "extracting_key",
            "message": "Sanitizing input and preparing harmonic key palette...",
            "session_id": session_id
        })

        # Stage 2: LLM generation
        yield format_sse("generating_notes", {
            "stage": "generating_notes",
            "message": "AI composer writing melody, chords, tempo, and rhythm...",
            "session_id": session_id
        })

        initial_state: MusicState = {
            "musician_input": safe_input,
            "style": safe_style
        }
        composer_output = await asyncio.to_thread(composer_agent, initial_state)
        current_state = {**initial_state, **composer_output}

        # Stage 3: Compiling MIDI
        yield format_sse("compiling_midi", {
            "stage": "compiling_midi",
            "message": "Assembling music21 score and applying humanized velocity dynamics...",
            "session_id": session_id
        })

        midi_output = await asyncio.to_thread(midi_converter, current_state)
        temp_midi = midi_output.get("midi_file")
        if not temp_midi or not os.path.exists(temp_midi):
            raise RuntimeError("MIDI converter failed to output a valid .mid file.")

        final_midi_path = STORAGE_DIR / f"{session_id}.mid"
        final_wav_path = STORAGE_DIR / f"{session_id}.wav"
        os.replace(temp_midi, final_midi_path)

        # Stage 4: Rendering WAV
        yield format_sse("rendering_wav", {
            "stage": "rendering_wav",
            "message": "Synthesizing 44.1kHz audio via FluidSynth / DSP engine...",
            "session_id": session_id
        })

        has_audio = await asyncio.to_thread(
            render_midi_to_wav,
            str(final_midi_path),
            str(final_wav_path)
        )

        # Schedule cleanup in background thread
        cleanup_files = [str(final_midi_path)]
        if has_audio:
            cleanup_files.append(str(final_wav_path))
        threading.Thread(target=cleanup_old_files, args=(cleanup_files, 3600), daemon=True).start()

        # Stage 5: Final Completed Payload
        comp_data = composer_output.get("composition_data", {})
        target_sec = composer_output.get("target_seconds", 10.0)

        yield format_sse("completed", {
            "stage": "completed",
            "message": "Composition generated successfully!",
            "session_id": session_id,
            "target_seconds": target_sec,
            "composition": {
                "tempo_bpm": comp_data.get("tempo_bpm", 120),
                "time_signature": comp_data.get("time_signature", "4/4"),
                "melody_instrument": comp_data.get("melody_instrument", "Piano"),
                "harmony_instrument": comp_data.get("harmony_instrument", "None"),
                "melody": comp_data.get("melody", []),
                "harmony": comp_data.get("harmony", []),
            },
            "midi_download_url": f"/api/v1/download/{session_id}/midi",
            "audio_stream_url": f"/api/v1/download/{session_id}/audio" if has_audio else None
        })

    except Exception as e:
        yield format_sse("error", {
            "stage": "error",
            "message": f"Composition pipeline failed: {str(e)}",
            "session_id": session_id
        })


# --- API Endpoints ---
@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy", "service": "music-compositor"}


@app.post(
    "/api/v1/compose",
    response_model=ComposeResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Composition"]
)
async def create_composition(request: ComposeRequest, background_tasks: BackgroundTasks):
    session_id = str(uuid.uuid4())
    
    # 1. Run the LangGraph agent in a non-blocking worker thread
    try:
        result = await asyncio.to_thread(
            compose_music,
            musician_input=request.prompt,
            style=request.style
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Music composition failed: {str(e)}"
        )

    temp_midi_path = result.get("midi_file")
    if not temp_midi_path or not os.path.exists(temp_midi_path):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate valid MIDI file."
        )

    # 2. Move file to permanent storage
    final_midi_path = STORAGE_DIR / f"{session_id}.mid"
    final_wav_path = STORAGE_DIR / f"{session_id}.wav"
    os.replace(temp_midi_path, final_midi_path)

    # 3. Render MIDI to WAV audio in worker thread
    has_audio = await asyncio.to_thread(
        render_midi_to_wav,
        str(final_midi_path),
        str(final_wav_path)
    )

    # Schedule thread-safe file cleanup after 1 hour
    cleanup_files = [str(final_midi_path)]
    if has_audio:
        cleanup_files.append(str(final_wav_path))
    background_tasks.add_task(cleanup_old_files, cleanup_files, 3600)

    # 4. Construct API Response
    comp_data = result.get("composition_data", {})
    target_sec = result.get("target_seconds", 10.0)

    return ComposeResponse(
        session_id=session_id,
        target_seconds=target_sec,
        composition=CompositionDetails(
            tempo_bpm=comp_data.get("tempo_bpm", 120),
            time_signature=comp_data.get("time_signature", "4/4"),
            melody_instrument=comp_data.get("melody_instrument", "Piano"),
            harmony_instrument=comp_data.get("harmony_instrument", "StringInstrument"),
            melody=comp_data.get("melody", []),
            harmony=comp_data.get("harmony", []),
        ),
        midi_download_url=f"/api/v1/download/{session_id}/midi",
        audio_stream_url=f"/api/v1/download/{session_id}/audio" if has_audio else None
    )


# --- SSE Streaming Endpoints (POST and GET for frontend flexibility) ---
SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Content-Type": "text/event-stream",
    "X-Accel-Buffering": "no"
}

@app.post("/api/v1/compose/stream", tags=["Streaming Composition"])
async def stream_composition_post(request: ComposeRequest):
    """SSE streaming endpoint for fetch-based clients sending a JSON body."""
    return StreamingResponse(
        stream_composition_events(prompt=request.prompt, style=request.style),
        media_type="text/event-stream",
        headers=SSE_HEADERS
    )


@app.get("/api/v1/compose/stream", tags=["Streaming Composition"])
async def stream_composition_get(
    prompt: str = Query(..., min_length=3, max_length=250, description="Music description"),
    style: str = Query(default="Romantic era", max_length=50, description="Musical genre or style")
):
    """SSE streaming endpoint for native browser EventSource connections."""
    return StreamingResponse(
        stream_composition_events(prompt=prompt, style=style),
        media_type="text/event-stream",
        headers=SSE_HEADERS
    )


@app.get("/api/v1/download/{session_id}/midi", tags=["Download"])
async def download_midi(session_id: str):
    file_path = STORAGE_DIR / f"{session_id}.mid"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="MIDI file not found or expired.")
    
    return FileResponse(
        path=str(file_path),
        filename=f"composition_{session_id[:8]}.mid",
        media_type="audio/midi"
    )


@app.get("/api/v1/download/{session_id}/audio", tags=["Download"])
async def stream_audio(session_id: str):
    file_path = STORAGE_DIR / f"{session_id}.wav"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found or expired.")

    return FileResponse(
        path=str(file_path),
        filename=f"composition_{session_id[:8]}.wav",
        media_type="audio/wav"
    )
