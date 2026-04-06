"""
segmenter.py
Splits a narrative paragraph into meaningful scenes.
Strategy:
  1. Try NLTK sentence tokenizer (most accurate)
  2. Fall back to regex-based splitting
  3. Merge very short fragments into the previous scene
"""

import re
from typing import List

# Optional NLTK — graceful degradation if not installed
try:
    import nltk
    nltk.download("punkt", quiet=True)
    nltk.download("punkt_tab", quiet=True)
    from nltk.tokenize import sent_tokenize
    _NLTK_AVAILABLE = True
except Exception:
    _NLTK_AVAILABLE = False


# ── Public API ─────────────────────────────────────────────────────────────────

def segment_narrative(text: str, min_words: int = 4) -> List[str]:
    """
    Split *text* into a list of scene strings.
    Each scene is a clean, non-empty string with at least *min_words* words.
    """
    raw_sentences = _split_sentences(text)
    scenes = _merge_fragments(raw_sentences, min_words)
    # Return at most 3 scenes to avoid overloading APIs (Step 2)
    return scenes[:3]



# ── Internals ──────────────────────────────────────────────────────────────────

def _split_sentences(text: str) -> List[str]:
    """Return a raw list of sentences using NLTK or regex fallback."""
    if _NLTK_AVAILABLE:
        return sent_tokenize(text)
    # Regex: split on '.', '!', '?' followed by whitespace or end-of-string
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    return [p.strip() for p in parts if p.strip()]


def _merge_fragments(sentences: List[str], min_words: int) -> List[str]:
    """
    Merge sentences shorter than *min_words* words into the previous scene.
    Ensures every scene is semantically substantial.
    """
    scenes: List[str] = []
    for sent in sentences:
        words = sent.split()
        if len(words) < min_words and scenes:
            # Append to previous scene
            scenes[-1] = scenes[-1].rstrip() + " " + sent
        else:
            scenes.append(sent)
    # Final clean-up
    return [s.strip() for s in scenes if s.strip()]
