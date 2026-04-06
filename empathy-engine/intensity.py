"""
intensity.py — Emotion Intensity Detector

Determines how strongly an emotion is expressed using:
  1. Confidence score from the emotion classifier
  2. Punctuation patterns (!!!, ...)
  3. Keyword presence (very, extremely, so, etc.)
  4. All-caps detection

Returns: "low" | "medium" | "high"
"""

import re
import logging

logger = logging.getLogger(__name__)

# ─── Intensity keywords ───────────────────────────────────────────────────────
HIGH_INTENSITY_KEYWORDS = [
    "extremely", "absolutely", "incredibly", "furious", "devastated",
    "ecstatic", "thrilled", "terrified", "outraged", "overjoyed",
    "hate", "love", "amazing", "horrible", "fantastic", "terrible",
    "disgusting", "wonderful", "awful", "perfect", "worst", "best",
]

MEDIUM_INTENSITY_KEYWORDS = [
    "very", "really", "quite", "rather", "pretty", "fairly",
    "somewhat", "kind of", "sort of", "a bit", "a little",
    "happy", "sad", "angry", "upset", "glad", "worried",
]

LOW_INTENSITY_KEYWORDS = [
    "slightly", "mildly", "a tad", "barely", "hardly", "just",
    "okay", "fine", "alright", "decent", "acceptable",
]


def _score_punctuation(text: str) -> float:
    """
    Analyse punctuation for intensity signals.
    Returns a score between 0.0 and 1.0.
    """
    score = 0.0

    # Multiple exclamation marks → high energy
    exclamation_count = len(re.findall(r"!", text))
    score += min(exclamation_count * 0.15, 0.45)

    # Multiple question marks → confusion / frustration
    question_count = len(re.findall(r"\?", text))
    score += min(question_count * 0.08, 0.24)

    # Ellipsis → hesitation / sadness / trailing off
    ellipsis_count = len(re.findall(r"\.{2,}", text))
    score += min(ellipsis_count * 0.10, 0.20)

    # ALL CAPS words → shouting / strong emotion
    caps_words = re.findall(r"\b[A-Z]{2,}\b", text)
    score += min(len(caps_words) * 0.12, 0.36)

    return min(score, 1.0)


def _score_keywords(text: str) -> float:
    """
    Score based on presence of intensity-related keywords.
    Returns a score between 0.0 and 1.0.
    """
    text_lower = text.lower()
    score = 0.0

    for kw in HIGH_INTENSITY_KEYWORDS:
        if kw in text_lower:
            score += 0.20

    for kw in MEDIUM_INTENSITY_KEYWORDS:
        if kw in text_lower:
            score += 0.10

    for kw in LOW_INTENSITY_KEYWORDS:
        if kw in text_lower:
            score -= 0.05   # Softens intensity

    return max(0.0, min(score, 1.0))


def detect_intensity(text: str, confidence: float) -> str:
    """
    Determine emotion intensity level from text and classifier confidence.

    Args:
        text:       Raw input text.
        confidence: Emotion classification confidence score (0–1).

    Returns:
        "low" | "medium" | "high"
    """
    # Weighted composite score
    punct_score   = _score_punctuation(text)
    keyword_score = _score_keywords(text)

    # Confidence contributes directly — high confidence → stronger emotion
    composite = (
        confidence    * 0.45 +   # Model certainty
        punct_score   * 0.30 +   # Punctuation signals
        keyword_score * 0.25     # Keyword signals
    )

    logger.debug(
        f"Intensity scores — confidence={confidence:.2f}, "
        f"punct={punct_score:.2f}, keywords={keyword_score:.2f}, "
        f"composite={composite:.2f}"
    )

    if composite >= 0.65:
        return "high"
    elif composite >= 0.40:
        return "medium"
    else:
        return "low"
