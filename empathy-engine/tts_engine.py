"""
tts_engine.py — Text-to-Speech Engine with Multi-Emotion Support

Splits input text into emotional segments, generates audio per segment, 
and merges them using pydub into a single output.
"""

import logging
import uuid
import asyncio
import re
from datetime import datetime
from pathlib import Path

import edge_tts
from pydub import AudioSegment
from emotion import detect_emotion

logger = logging.getLogger(__name__)

# Output directory (project root / outputs)
OUTPUTS_DIR = Path(__file__).parent / "outputs"
TEMP_DIR    = OUTPUTS_DIR / "temp"
OUTPUTS_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

DEFAULT_VOICE = "en-IN-NeerjaNeural"

# Define emotion to voice parameter mapping (no SSML)
# edge-tts requires rate/pitch to have + or - signs. "0" and "0%" are invalid.
# Define emotion to voice parameter mapping (no SSML)
# edge-tts requires rate/pitch to have + or - signs. "0" and "0%" are invalid.
emotion_map = {
    "happy":   {"rate": "+15%", "pitch": "+5Hz"},
    "sad":     {"rate": "-10%", "pitch": "-5Hz"},
    "angry":   {"rate": "+10%", "pitch": "+8Hz"},
    "neutral": {"rate": "+0%",  "pitch": "+0Hz"}
}


def validate_prosody(rate: str, pitch: str) -> tuple[str, str]:
    """
    Ensures rate/pitch values are strictly formatted for edge-tts.
    Values MUST include + or - sign. '0' and '0%' are invalid.
    """
    # Fix rate
    if rate in ["0", "0%"]:
        rate = "+0%"
    if not rate.startswith(("+", "-")):
        rate = "+" + rate

    # Fix pitch
    if pitch in ["0", "0Hz"]:
        pitch = "+0Hz"
    if not pitch.startswith(("+", "-")):
        pitch = "+" + pitch

    return rate, pitch


def _get_output_path(prefix: str = "output", ext: str = "mp3") -> Path:
    """Generate a unique output file path using timestamp + UUID fragment."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    uid       = uuid.uuid4().hex[:8]
    filename  = f"{prefix}_{timestamp}_{uid}.{ext}"
    return OUTPUTS_DIR / filename


def list_voices() -> list[dict]:
    """Return available voices."""
    return [
        {
            "id": DEFAULT_VOICE,
            "name": "Neerja Neural (Indian English Female)",
            "lang": "en-IN",
        }
    ]


def clean_text(text: str) -> str:
    """Minimal text cleaning to ensure natural flow without word skipping."""
    if not text:
        return ""
    text = text.strip()
    text = text.replace("\n", " ")
    return " ".join(text.split())


def split_text_into_segments(text: str) -> list[str]:
    """
    Split text into segments while PRESERVING all connectors like 'but'/'however'.
    Includes smart merging to ensure connectors aren't at the start of a segment.
    """
    cleaned = clean_text(text)
    # Use capturing group ( ) to keep delimiters in the split parts list
    pattern = r'(,|\.|\bbut\b|\bhowever\b)'
    parts = re.split(pattern, cleaned, flags=re.IGNORECASE)
    
    raw_segments = []
    current = ""
    
    for part in parts:
        if part is None:
            continue
        
        trimmed = part.strip()
        
        # Punctuation stick to the PREVIOUS segment
        if trimmed in [",", "."]:
            current += trimmed
            if current.strip():
                raw_segments.append(current.strip())
            current = ""
        # Connectors stick to the FOLLOWING segment (initially)
        elif trimmed.lower() in ["but", "however"]:
            if current.strip():
                raw_segments.append(current.strip())
            current = trimmed + " "
        else:
            current += part

    if current.strip():
        raw_segments.append(current.strip())
    
    # --- SMART MERGING: Prevent connectors from being at the start of a segment ---
    # TTS engines often ignore connectors at the start of a chunk.
    final_segments = []
    if raw_segments:
        final_segments.append(raw_segments[0])
        for i in range(1, len(raw_segments)):
            seg = raw_segments[i]
            if seg.lower().startswith(("but ", "and ", "however ")):
                # Merge with previous segment
                final_segments[-1] += " " + seg
            else:
                final_segments.append(seg)

    result = [s for s in final_segments if s.strip()]
    print(f"FINAL SEGMENTS: {result}")
    return result


async def generate_segment_audio(text: str, emotion: str, voice: str) -> Path:
    """Generate audio for a single segment with specific emotion parameters."""
    out_path = TEMP_DIR / f"seg_{uuid.uuid4().hex[:8]}.mp3"
    params   = emotion_map.get(emotion.lower(), emotion_map["neutral"]).copy()
    
    # Minimal text cleaning (No injection of commas)
    cleaned_text = clean_text(text)
    
    # Add slight emphasis spacing to force TTS to pronounce weak connectors (and, but)
    # This prevents the initial-connector-skip bug in edge-tts
    processed_text = cleaned_text.replace(" but ", " ... but ").replace(" and ", " ... and ")
    
    print(f"SEGMENT (processed): {processed_text}")
    
    # Apply strict validation before TTS call
    rate, pitch = validate_prosody(params["rate"], params["pitch"])

    try:
        communicate = edge_tts.Communicate(
            text=processed_text, 
            voice=voice, 
            rate=rate, 
            pitch=pitch
        )
        await communicate.save(str(out_path))
        return out_path
    except Exception as e:
        logger.error(f"Segment TTS failed: {e}")
        # Fallback to safe neutral on any failure
        try:
            safe_rate, safe_pitch = "+0%", "+0Hz"
            communicate = edge_tts.Communicate(
                text=processed_text, 
                voice=voice, 
                rate=safe_rate, 
                pitch=safe_pitch
            )
            await communicate.save(str(out_path))
            return out_path
        except Exception as fe:
            logger.critical(f"Total fallback TTS failure: {fe}")
            raise


def merge_audio_segments(segment_paths: list[Path]) -> Path:
    """Merge multiple mp3 files into one with transitions using pydub."""
    if not segment_paths:
        raise RuntimeError("No segments to merge.")
    
    final_output = _get_output_path("final_output", "mp3")
    combined = AudioSegment.empty()
    
    # 200ms silence for smooth transitions (Avoid too long/short pauses)
    pause = AudioSegment.silent(duration=80)
    
    try:
        for i, path in enumerate(segment_paths):
            seg = AudioSegment.from_file(str(path), format="mp3")
            combined += seg
            if i < len(segment_paths) - 1:
                combined += pause
        
        combined.export(str(final_output), format="mp3")
        
        # Cleanup temp segments
        for path in segment_paths:
            try: path.unlink()
            except: pass
            
        logger.info(f"Merged {len(segment_paths)} segments into {final_output.name}")
        return final_output
    except Exception as e:
        logger.error(f"Audio merging failed: {e}")
        # If merge fails, return the first segment as fallback
        return segment_paths[0]


async def synthesise_multi_emotion(text: str, voice_id: str | None = None) -> Path:
    """
    The main multi-emotion pipeline:
    1. Segment text
    2. Detect emotion per segment
    3. Generate audio per segment
    4. Merge audio
    """
    voice = voice_id or DEFAULT_VOICE
    segments = split_text_into_segments(text)
    
    if len(segments) <= 1:
        # Fallback to single emotion detection if no segments found or only one
        em_data = detect_emotion(text)
        return await generate_segment_audio(text, em_data["emotion"], voice)

    segment_paths = []
    
    for seg_text in segments:
        em_data = detect_emotion(seg_text)
        path = await generate_segment_audio(seg_text, em_data["emotion"], voice)
        segment_paths.append(path)

    loop = asyncio.get_event_loop()
    # Pydub merging is CPU-bound; run in executor
    final_path = await loop.run_in_executor(None, merge_audio_segments, segment_paths)
    return final_path


# ─── Backward Compatibility Wrappers ──────────────────────────────────────────

async def synthesise_async(text: str, emotion: str = "neutral", intensity: str = "medium", voice_id: str | None = None) -> Path:
    """
    Used by main.py. 
    Can either use the new multi-emotion pipeline OR the old single style.
    Let's switch to multi-emotion by default if the text contains connectors.
    """
    # If text is complex, use multi-emotion pipeline
    if any(p in text for p in [".", "!", "?", ",", " but ", " and "]):
        return await synthesise_multi_emotion(text, voice_id)
    
    # Otherwise, fallback to single prompt (original behaviour)
    # Reusing multi-emotion pipeline with a single segment is effectively the same.
    return await synthesise_multi_emotion(text, voice_id)


def synthesise_sync(text: str, emotion: str = "neutral", intensity: str = "medium", voice_id: str | None = None) -> Path:
    """Synchronous version for CLI usage."""
    return asyncio.run(synthesise_multi_emotion(text, voice_id))

