# 🎙️ Empathy Engine

> Transform plain text into emotionally expressive speech using AI-powered emotion detection and dynamic voice synthesis.

---

## Overview

Empathy Engine is a full-stack Python project that:

1. **Detects emotion** in any input text using a HuggingFace transformer model
2. **Measures intensity** (low / medium / high) via punctuation, keywords, and model confidence
3. **Maps emotion → voice parameters** (rate, volume, pitch label) using a configurable JSON file
4. **Synthesises speech** offline using `pyttsx3` with dynamic voice adjustment
5. **Serves a web UI** via FastAPI where you can type, listen, and download audio

---

## Project Structure

```
empathy-engine/
│
├── main.py              ← FastAPI app + CLI entry point
├── emotion.py           ← HuggingFace emotion classifier
├── intensity.py         ← Intensity scorer (punctuation + keywords + confidence)
├── mapper.py            ← Emotion → voice parameter mapping
├── tts_engine.py        ← pyttsx3 TTS synthesis (async-safe)
│
├── utils/
│   ├── __init__.py
│   ├── logger.py        ← Structured logging setup
│   └── cache.py         ← In-memory LRU response cache
│
├── config/
│   └── voice_map.json   ← Voice parameter config per emotion + intensity
│
├── templates/
│   └── index.html       ← Web frontend (HTML + JS)
│
├── static/              ← Static assets (CSS/JS if separated)
├── outputs/             ← Generated .wav files (auto-created)
├── logs/
│   └── emotion.log      ← Structured generation log
│
├── tests/
│   └── test_empathy_engine.py
│
├── requirements.txt
├── .env.example
└── README.md
```

---

## Setup

### 1. Clone / Extract the project

```bash
cd empathy-engine
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv

# macOS / Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** `torch` (~2 GB) and the HuggingFace model (~250 MB) are downloaded automatically on first run.

### 4. Set up environment variables

```bash
cp .env.example .env
# Edit .env if needed (optional — defaults work out of the box)
```

### 5. System-level TTS dependency (Linux only)

```bash
sudo apt-get install espeak espeak-ng libespeak-ng-dev
```

macOS and Windows include a speech engine by default (no extra install needed).

---

## Running the Project

### Option A — Web Server (recommended)

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Then open: **http://localhost:8000**

Or use the built-in launcher:

```bash
python main.py --server
```

### Option B — CLI Mode

```bash
python main.py
```

You'll be prompted to enter text. The engine will:
- Print detected emotion and intensity
- Generate and save a `.wav` file to `/outputs`

---

## API Usage

### `POST /generate-voice`

**Request:**
```json
{
  "text": "I am so thrilled about today!! Everything is amazing!",
  "voice_id": null
}
```

**Response:**
```json
{
  "emotion": "happy",
  "intensity": "high",
  "voice_params": {
    "rate": 215,
    "volume": 0.95
  },
  "audio_url": "/outputs/output_20260406_123456_a1b2c3d4.wav",
  "cached": false
}
```

**Error responses:**
- `400` — Empty text, text too long, or validation error
- `500` — Model loading failure or TTS synthesis error

### `GET /voices`

Returns all available TTS voices on the current system.

```json
{
  "voices": [
    { "id": "HKEY_LOCAL_MACHINE\\...", "name": "Microsoft David", "lang": "en-US" }
  ],
  "count": 3
}
```

### `GET /health`

```json
{ "status": "ok", "cache": { "entries": 4, "max_entries": 200 } }
```

---

## Emotion → Voice Design

The mapping is defined in `config/voice_map.json` and works as follows:

| Emotion  | Rate (WPM) | Volume | Pitch Label | Style |
|----------|-----------|--------|-------------|-------|
| Happy    | 185       | 0.85   | High        | Upbeat, fast-paced |
| Sad      | 130       | 0.60   | Low         | Slow, quiet, heavy |
| Angry    | 195       | 0.95   | High        | Forceful, loud |
| Neutral  | 160       | 0.75   | Medium      | Balanced, even |
| Excited  | 210       | 0.90   | High        | Very fast, enthusiastic |
| Calm     | 145       | 0.70   | Low         | Slow, soothing |

**Intensity scaling** applies a delta on top of the base values:
- `low`    → no change (pure baseline)
- `medium` → small delta (+/- rate, +/- volume)
- `high`   → larger delta

All values are clamped to safe bounds (rate: 80–300 WPM, volume: 0.20–1.00).

---

## Intensity Detection

Intensity is computed from three signals, weighted as:

| Signal              | Weight |
|---------------------|--------|
| Model confidence    | 45%    |
| Punctuation score   | 30%    |
| Keyword score       | 25%    |

**Punctuation signals:** `!` marks, `?` marks, `...` ellipses, ALL CAPS words

**Keyword signals:**
- High: *extremely, furious, ecstatic, outraged, devastated*
- Medium: *very, really, quite, happy, sad, angry*
- Softeners: *slightly, barely, a tad* (reduce score)

---

## Caching

Identical `(text, voice_id)` pairs are cached in memory for the server's lifetime. If the same text is sent again, the existing audio file is reused — no model inference or TTS re-synthesis needed. Cache capacity: 200 entries (LRU eviction).

---

## Logging

All generation events are written to `logs/emotion.log`:

```
2026-04-06 12:34:56 [INFO    ] __main__ — GENERATION | emotion=happy | intensity=high | file=output_20260406_123456_a1b2c3d4.wav | text_preview="I am so thrilled..."
```

---

## Testing

Run unit tests (no model download required):

```bash
pytest tests/ -v
```

Run integration tests (requires model download):

```bash
pytest tests/ -v -m integration
```

---

## Deployment

### Render / Railway

Set environment variables in your dashboard:
```
HOST=0.0.0.0
PORT=8000
```

Start command:
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

> **Important:** Cloud TTS with `pyttsx3` requires `espeak` installed in the build environment. Add a `render.yaml` or `nixpacks.toml` build step:
> ```
> apt-get install -y espeak espeak-ng
> ```

---

## Quick Command Reference

```bash
# Install
pip install -r requirements.txt

# Start web server
uvicorn main:app --reload

# CLI mode
python main.py

# Run tests
pytest tests/ -v

# Test the API
curl -X POST http://localhost:8000/generate-voice \
     -H "Content-Type: application/json" \
     -d '{"text": "I am absolutely overjoyed today!!"}'
```
