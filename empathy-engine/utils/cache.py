"""
utils/cache.py — In-memory response cache for Empathy Engine

Caches (text, voice_id) → response so identical requests
reuse existing audio files without re-running the model or TTS.

Uses a simple dict with LRU-like eviction (max 200 entries).
"""

import hashlib
import logging
from collections import OrderedDict
from pathlib import Path

logger = logging.getLogger(__name__)

_MAX_ENTRIES = 200

# OrderedDict preserves insertion order for LRU eviction
_cache: OrderedDict[str, dict] = OrderedDict()


def _make_key(text: str, voice_id: str | None) -> str:
    """Create a stable cache key from input parameters."""
    raw = f"{text.strip().lower()}|{voice_id or 'default'}"
    return hashlib.sha256(raw.encode()).hexdigest()


def get_cached(text: str, voice_id: str | None = None) -> dict | None:
    """
    Retrieve a cached response if it exists AND the audio file still exists.

    Args:
        text:     Input text.
        voice_id: Optional voice ID.

    Returns:
        Cached response dict, or None if not found / file missing.
    """
    key = _make_key(text, voice_id)
    entry = _cache.get(key)

    if entry is None:
        return None

    # Verify audio file still exists on disk
    audio_path = entry.get("_audio_path")
    if audio_path and not Path(audio_path).exists():
        logger.debug(f"Cache hit but file missing — evicting key {key[:8]}…")
        del _cache[key]
        return None

    # Move to end (LRU: most recently used)
    _cache.move_to_end(key)
    logger.info(f"Cache HIT for key {key[:8]}…")
    return entry


def set_cached(text: str, voice_id: str | None, response: dict, audio_path: str) -> None:
    """
    Store a response in the cache.

    Args:
        text:       Input text.
        voice_id:   Optional voice ID.
        response:   API response dict to cache.
        audio_path: Absolute path to the audio file (for existence check).
    """
    key = _make_key(text, voice_id)

    # Store response + internal path reference
    entry = {**response, "_audio_path": audio_path}
    _cache[key] = entry
    _cache.move_to_end(key)

    # Evict oldest entries if over limit
    while len(_cache) > _MAX_ENTRIES:
        evicted_key, _ = _cache.popitem(last=False)
        logger.debug(f"Cache evicted key {evicted_key[:8]}… (limit={_MAX_ENTRIES})")

    logger.debug(f"Cache SET for key {key[:8]}… (total entries={len(_cache)})")


def clear_cache() -> int:
    """Clear all cache entries. Returns number of entries cleared."""
    count = len(_cache)
    _cache.clear()
    logger.info(f"Cache cleared ({count} entries removed).")
    return count


def cache_stats() -> dict:
    """Return basic cache statistics."""
    return {
        "entries":    len(_cache),
        "max_entries": _MAX_ENTRIES,
    }
