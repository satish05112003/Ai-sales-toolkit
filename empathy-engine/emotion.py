"""
emotion.py — Emotion Detection using HuggingFace Transformers

Uses the model: j-hartmann/emotion-english-distilroberta-base
Classifies text into: joy, sadness, anger, fear, disgust, surprise, neutral
Then maps to our simplified set: happy, sad, angry, neutral, excited, calm
"""

import logging
from transformers import pipeline

logger = logging.getLogger(__name__)

# ─── Emotion label normalization ─────────────────────────────────────────────
# Maps HuggingFace model labels → our simplified emotion labels
EMOTION_MAP = {
    "joy":      "happy",
    "sadness":  "sad",
    "anger":    "angry",
    "fear":     "sad",       # Fear → sad-like vocal delivery
    "disgust":  "angry",     # Disgust → angry-like vocal delivery
    "surprise": "excited",
    "neutral":  "neutral",
}

# Global pipeline (loaded once, reused across requests)
_classifier = None


def load_emotion_model():
    """
    Load the HuggingFace emotion classification pipeline.
    Called once at startup to avoid repeated loading overhead.
    """
    global _classifier
    if _classifier is None:
        logger.info("Loading emotion detection model — this may take a moment...")
        try:
            _classifier = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                top_k=None,          # Return scores for ALL labels
                truncation=True,
                max_length=512,
            )
            logger.info("Emotion model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load emotion model: {e}")
            raise RuntimeError(f"Emotion model could not be loaded: {e}")
    return _classifier


def detect_emotion(text: str) -> dict:
    """
    Detect the primary emotion in the given text.

    Args:
        text: Input string to classify.

    Returns:
        {
            "raw_emotion": "joy",           # original HuggingFace label
            "emotion": "happy",             # normalized label
            "confidence": 0.92,             # top score (0–1)
            "all_scores": { "joy": 0.92, ...}  # full score breakdown
        }
    """
    classifier = load_emotion_model()

    try:
        results = classifier(text)
        # results is a list of lists when top_k=None:  [[{label, score}, ...]]
        scores = results[0]

        # Sort by score descending
        scores_sorted = sorted(scores, key=lambda x: x["score"], reverse=True)
        top = scores_sorted[0]

        raw_emotion = top["label"].lower()
        normalized  = EMOTION_MAP.get(raw_emotion, "neutral")
        confidence  = round(top["score"], 4)

        all_scores = {item["label"].lower(): round(item["score"], 4) for item in scores_sorted}

        logger.debug(f"Emotion detected: {raw_emotion} → {normalized} (confidence={confidence})")

        return {
            "raw_emotion": raw_emotion,
            "emotion":     normalized,
            "confidence":  confidence,
            "all_scores":  all_scores,
        }

    except Exception as e:
        logger.error(f"Emotion detection failed: {e}")
        # Graceful fallback to neutral
        return {
            "raw_emotion": "neutral",
            "emotion":     "neutral",
            "confidence":  0.0,
            "all_scores":  {},
        }
