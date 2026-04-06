"""
main.py — Empathy Engine Entry Point

Runs as:
  - FastAPI server:  uvicorn main:app --reload
  - CLI mode:        python main.py

Provides:
  POST /generate-voice  → emotion detection + TTS generation
  GET  /voices          → list available system voices
  GET  /outputs/{file}  → serve generated audio files
  GET  /health          → health check
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, field_validator

from emotion    import detect_emotion, load_emotion_model
from intensity  import detect_intensity
from mapper     import get_voice_params
from tts_engine import synthesise_async, synthesise_sync, list_voices, OUTPUTS_DIR
from utils      import (
    setup_logging, log_generation_event,
    get_cached, set_cached, cache_stats,
)

# ─── Environment & Logging ────────────────────────────────────────────────────
load_dotenv()
setup_logging()
logger = logging.getLogger(__name__)

# ─── FastAPI App ──────────────────────────────────────────────────────────────
app = FastAPI(
    title       = "Empathy Engine",
    description = "Convert text into emotionally expressive speech.",
    version     = "1.0.0",
)

# Allow all origins for local dev (tighten in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

# Serve generated audio files
app.mount("/outputs", StaticFiles(directory=str(OUTPUTS_DIR)), name="outputs")

# Serve static assets (CSS, JS)
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# HTML templates
templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


# ─── Request / Response Models ────────────────────────────────────────────────
class VoiceRequest(BaseModel):
    text:     str
    voice_id: str | None = None   # Optional: pyttsx3 voice ID

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Text must not be empty.")
        if len(v) > 2000:
            raise ValueError("Text must not exceed 2000 characters.")
        return v


class VoiceResponse(BaseModel):
    emotion:      str
    intensity:    str
    voice_params: dict
    audio_url:    str
    cached:       bool = False
    segments:     bool = False


# ─── Startup: pre-load model ──────────────────────────────────────────────────
@app.on_event("startup")
async def on_startup():
    """Pre-load the emotion model so first request isn't slow."""
    logger.info("Starting Empathy Engine…")
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, load_emotion_model)
        logger.info("Empathy Engine ready.")
    except Exception as e:
        logger.error(f"Model pre-load failed: {e}")


# ─── Routes ───────────────────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
async def index(request: Request):
    """Serve the web frontend."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health():
    """Health check endpoint for deployment platforms."""
    return {"status": "ok", "cache": cache_stats()}


@app.get("/voices")
async def get_voices():
    """Return list of available TTS voices on the current system."""
    voices = list_voices()
    return {"voices": voices, "count": len(voices)}


@app.post("/generate-voice", response_model=VoiceResponse)
async def generate_voice(req: VoiceRequest):
    """
    Main endpoint: detect emotion from text and generate expressive speech.

    Flow:
      1. Check cache
      2. Detect emotion (HuggingFace model)
      3. Detect intensity
      4. Map to voice parameters
      5. Synthesise audio (pyttsx3)
      6. Cache result
      7. Return response
    """

    # ── 1. Cache check ────────────────────────────────────────────────────
    cached = get_cached(req.text, req.voice_id)
    if cached:
        response = {k: v for k, v in cached.items() if not k.startswith("_")}
        response["cached"] = True
        return response

    # ── 2. Emotion detection ──────────────────────────────────────────────
    try:
        emotion_data = detect_emotion(req.text)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=f"Emotion model error: {e}")

    emotion    = emotion_data["emotion"]
    confidence = emotion_data["confidence"]

    # ── 3. Intensity detection ────────────────────────────────────────────
    intensity = detect_intensity(req.text, confidence)

    # ── 4. Voice parameter mapping ────────────────────────────────────────
    params = get_voice_params(emotion, intensity)
    voice_params = {
        "rate":   params["rate"],
        "volume": params["volume"],
    }

    # ── 5. TTS synthesis (Multi-Emotion / Multi-Segment) ──────────────────
    try:
        # The new synthesise_async in tts_engine.py handles segmentation and 
        # per-segment emotion detection internally.
        audio_path = await synthesise_async(
            text      = req.text,
            voice_id  = req.voice_id,
        )
    except Exception as e:
        logger.error(f"TTS synthesis error: {e}")
        raise HTTPException(status_code=500, detail=f"TTS synthesis failed: {e}")

    # ── 6. Build response ─────────────────────────────────────────────────
    audio_url = f"/outputs/{audio_path.name}"

    response = {
        "emotion":     emotion,  # Keep overall emotion for metadata
        "intensity":   intensity,
        "voice_params": voice_params,
        "audio_url":   audio_url,
        "cached":      False,
        "segments":    True,     # Flag to indicate multi-segment processing
    }

    # ── 7. Cache + log ────────────────────────────────────────────────────
    set_cached(req.text, req.voice_id, response, str(audio_path))
    log_generation_event(logger, req.text, emotion, intensity, audio_path.name)

    return response


@app.exception_handler(422)
async def validation_error_handler(request: Request, exc):
    """Convert Pydantic validation errors into clean 400 responses."""
    errors = exc.errors()
    messages = [e["msg"] for e in errors]
    return JSONResponse(
        status_code=400,
        content={"detail": messages},
    )


# ─── CLI Mode ─────────────────────────────────────────────────────────────────
def run_cli():
    """Interactive CLI for local testing without starting the server."""
    print("\n🎙️  Empathy Engine — CLI Mode")
    print("=" * 40)

    # Pre-load model
    print("Loading emotion model (first run may download ~250 MB)…")
    load_emotion_model()
    print("Model ready.\n")

    while True:
        try:
            text = input("Enter text (or 'quit' to exit): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if text.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        if not text:
            print("Please enter some text.\n")
            continue

        if len(text) > 2000:
            print("Text too long (max 2000 chars). Please shorten it.\n")
            continue

        print("\nAnalysing…")

        # Detect emotion
        emotion_data = detect_emotion(text)
        emotion      = emotion_data["emotion"]
        confidence   = emotion_data["confidence"]

        # Detect intensity
        intensity = detect_intensity(text, confidence)

        # Map to voice params
        params = get_voice_params(emotion, intensity)

        print(f"\n  Emotion:   {emotion.upper()} (confidence: {confidence:.0%})")
        print(f"  Intensity: {intensity.upper()}")
        print(f"  Voice:     rate={params['rate']} WPM, volume={params['volume']}")
        print(f"  Style:     {params['description']}")
        print("\nGenerating audio…")

        # Synthesise
        try:
            audio_path = synthesise_sync(text)
            print(f"\n✅ Audio saved: {audio_path}")
            log_generation_event(logger, text, emotion, intensity, audio_path.name)
        except Exception as e:
            print(f"\n❌ TTS failed: {e}")

        print()


# ─── Entry Point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--server":
        # Explicit server mode: python main.py --server
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", 8000))
        uvicorn.run("main:app", host=host, port=port, reload=False)
    else:
        # Default: CLI mode
        run_cli()
