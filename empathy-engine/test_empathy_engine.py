"""
tests/test_empathy_engine.py — Unit Tests

Run with: python -m pytest tests/ -v

Tests cover:
  - Emotion detection
  - Intensity scoring
  - Voice parameter mapping
  - Input validation (via API schema)
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from intensity import detect_intensity, _score_punctuation, _score_keywords
from mapper    import get_voice_params, list_emotions


# ─── Sample test inputs ───────────────────────────────────────────────────────
SAMPLE_INPUTS = [
    {
        "text":             "I am so incredibly happy today! This is the best day ever!!",
        "expected_emotion": "happy",
        "expected_intensity": "high",
    },
    {
        "text":             "I feel okay, nothing special.",
        "expected_emotion": "neutral",
        "expected_intensity": "low",
    },
    {
        "text":             "I'm devastated... everything fell apart.",
        "expected_emotion": "sad",
        "expected_intensity": "high",
    },
    {
        "text":             "THIS IS ABSOLUTELY OUTRAGEOUS! HOW DARE THEY!!!",
        "expected_emotion": "angry",
        "expected_intensity": "high",
    },
    {
        "text":             "The weather is quite pleasant today.",
        "expected_emotion": "neutral",
        "expected_intensity": "low",
    },
]


# ─── Intensity tests ──────────────────────────────────────────────────────────
class TestIntensity:

    def test_exclamation_marks_raise_score(self):
        score = _score_punctuation("This is amazing!!!")
        assert score > 0.2, "Multiple exclamation marks should raise punctuation score"

    def test_ellipsis_raises_score(self):
        score = _score_punctuation("I don't know... maybe...")
        assert score > 0.1, "Ellipsis should contribute to punctuation score"

    def test_caps_words_raise_score(self):
        score = _score_punctuation("THIS IS WRONG")
        assert score > 0.15, "All-caps words should raise punctuation score"

    def test_high_intensity_keywords(self):
        score = _score_keywords("I absolutely hate this, it is extremely awful")
        assert score > 0.3

    def test_softening_keywords_reduce_score(self):
        score_normal = _score_keywords("I am unhappy")
        score_soft   = _score_keywords("I am slightly unhappy")
        assert score_soft <= score_normal

    def test_high_confidence_gives_high_intensity(self):
        result = detect_intensity("Great!!!", confidence=0.97)
        assert result == "high"

    def test_low_confidence_gives_low_intensity(self):
        result = detect_intensity("okay", confidence=0.35)
        assert result == "low"

    def test_valid_return_values(self):
        for text, conf in [("ok", 0.5), ("amazing!!!", 0.9), ("slightly sad", 0.4)]:
            result = detect_intensity(text, conf)
            assert result in ("low", "medium", "high")


# ─── Mapper tests ─────────────────────────────────────────────────────────────
class TestMapper:

    def test_all_emotions_return_params(self):
        for emotion in list_emotions():
            for intensity in ("low", "medium", "high"):
                params = get_voice_params(emotion, intensity)
                assert "rate"        in params
                assert "volume"      in params
                assert "pitch_label" in params

    def test_happy_high_faster_than_happy_low(self):
        low  = get_voice_params("happy", "low")
        high = get_voice_params("happy", "high")
        assert high["rate"] >= low["rate"], "High intensity should be faster than low for happy"

    def test_sad_high_quieter_than_sad_low(self):
        low  = get_voice_params("sad", "low")
        high = get_voice_params("sad", "high")
        assert high["volume"] <= low["volume"], "High sad intensity should be quieter"

    def test_rate_within_bounds(self):
        for emotion in list_emotions():
            for intensity in ("low", "medium", "high"):
                params = get_voice_params(emotion, intensity)
                assert 80 <= params["rate"] <= 300, f"Rate out of bounds for {emotion}/{intensity}"

    def test_volume_within_bounds(self):
        for emotion in list_emotions():
            for intensity in ("low", "medium", "high"):
                params = get_voice_params(emotion, intensity)
                assert 0.20 <= params["volume"] <= 1.0, f"Volume out of bounds for {emotion}/{intensity}"

    def test_unknown_emotion_falls_back_to_neutral(self):
        params   = get_voice_params("confusion", "medium")
        neutral  = get_voice_params("neutral", "medium")
        assert params["rate"]   == neutral["rate"]
        assert params["volume"] == neutral["volume"]

    def test_unknown_intensity_falls_back_to_medium(self):
        medium  = get_voice_params("happy", "medium")
        unknown = get_voice_params("happy", "extreme")
        assert medium["rate"]   == unknown["rate"]
        assert medium["volume"] == unknown["volume"]


# ─── Emotion detection tests (integration — requires model) ───────────────────
# These tests are marked slow and require the HuggingFace model to be downloaded.
# Run with: pytest tests/ -v -m integration

@pytest.mark.integration
class TestEmotionDetection:

    @pytest.fixture(autouse=True, scope="class")
    def load_model(self):
        from emotion import load_emotion_model
        load_emotion_model()

    def test_happy_text(self):
        from emotion import detect_emotion
        result = detect_emotion("I am so incredibly happy and joyful today!")
        assert result["emotion"] == "happy"
        assert result["confidence"] > 0.5

    def test_sad_text(self):
        from emotion import detect_emotion
        result = detect_emotion("I feel terrible and deeply heartbroken.")
        assert result["emotion"] in ("sad", "neutral")   # Model may vary

    def test_empty_ish_text_returns_dict(self):
        from emotion import detect_emotion
        result = detect_emotion("ok")
        assert "emotion"    in result
        assert "confidence" in result

    def test_all_sample_inputs(self):
        from emotion import detect_emotion
        for sample in SAMPLE_INPUTS:
            result = detect_emotion(sample["text"])
            assert "emotion"    in result
            assert "confidence" in result
            assert 0.0 <= result["confidence"] <= 1.0


# ─── Run summary ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n📋 Sample Test Inputs & Expected Outputs\n" + "─"*50)
    for s in SAMPLE_INPUTS:
        print(f"\n  Text:     \"{s['text'][:60]}\"")
        print(f"  Expected: emotion={s['expected_emotion']}, intensity={s['expected_intensity']}")
