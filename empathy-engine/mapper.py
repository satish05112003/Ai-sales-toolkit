"""
mapper.py — Emotion → Voice Parameter Mapper

Reads config/voice_map.json and translates (emotion, intensity)
into concrete TTS parameters: rate, volume.
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Path to config file (relative to project root)
_CONFIG_PATH = Path(__file__).parent / "config" / "voice_map.json"

# Cached config (loaded once)
_config: dict | None = None


def _load_config() -> dict:
    """Load and cache the voice map configuration."""
    global _config
    if _config is None:
        try:
            with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
                _config = json.load(f)
            logger.info("Voice map config loaded.")
        except FileNotFoundError:
            logger.error(f"voice_map.json not found at {_CONFIG_PATH}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in voice_map.json: {e}")
            raise
    return _config


def get_voice_params(emotion: str, intensity: str) -> dict:
    """
    Convert emotion + intensity into concrete TTS voice parameters.

    Args:
        emotion:   One of: happy, sad, angry, neutral, excited, calm
        intensity: One of: low, medium, high

    Returns:
        {
            "rate":        <int>   — words per minute (WPM)
            "volume":      <float> — 0.0 to 1.0
            "pitch_label": <str>   — "low" | "medium" | "high"
            "description": <str>   — human-readable style description
        }
    """
    config = _load_config()
    emotions = config["emotions"]

    # Fallback to neutral if unknown emotion
    if emotion not in emotions:
        logger.warning(f"Unknown emotion '{emotion}', falling back to 'neutral'.")
        emotion = "neutral"

    # Fallback to medium if unknown intensity
    if intensity not in ("low", "medium", "high"):
        logger.warning(f"Unknown intensity '{intensity}', falling back to 'medium'.")
        intensity = "medium"

    entry   = emotions[emotion]
    base    = entry["base"]
    delta   = entry["intensity_delta"][intensity]

    raw_rate   = base["rate"]   + delta["rate"]
    raw_volume = base["volume"] + delta["volume"]

    # Clamp within safe bounds
    rate_min, rate_max     = config["rate_bounds"]["min"],   config["rate_bounds"]["max"]
    vol_min,  vol_max      = config["volume_bounds"]["min"], config["volume_bounds"]["max"]

    final_rate   = max(rate_min,  min(rate_max,  int(raw_rate)))
    final_volume = max(vol_min,   min(vol_max,   round(raw_volume, 2)))

    params = {
        "rate":        final_rate,
        "volume":      final_volume,
        "pitch_label": base["pitch_label"],
        "description": entry["description"],
    }

    logger.debug(f"Voice params for ({emotion}, {intensity}): {params}")
    return params


def list_emotions() -> list[str]:
    """Return all supported emotion labels."""
    config = _load_config()
    return list(config["emotions"].keys())
