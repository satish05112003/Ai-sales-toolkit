# AI Sales Toolkit 🚀

A comprehensive suite of AI-powered tools designed to supercharge sales narratives and presentations. This repository combines two powerful engines into a unified toolkit.

## 📁 Repository Structure

```text
AI-Sales-Toolkit/
├── empathy-engine/      # Emotion detection + Expressive TTS
├── pitch-visualizer/    # AI Storyboarding + Presentation Generator
└── README.md            # Root documentation
```

---

## 🎙️ 1. Empathy Engine
The **Empathy Engine** converts plain text into emotionally expressive speech. It uses a fine-tuned DistilRoBERTa model to detect sentiment and intensity, then maps those to vocal parameters (pitch, rate, volume) using `pyttsx3`.

### Key Features:
- **Real-time Emotion Detection**: Identifies joy, sadness, anger, and more.
- **Dynamic TTS**: Adjusts voice delivery based on detected emotion.
- **Multi-Segment Support**: Different parts of a sentence can have different emotional tones.

### How to Run:
1. `cd empathy-engine`
2. `python -m venv venv`
3. `venv\Scripts\activate`
4. `pip install -r requirements.txt`
5. `python main.py --server` (starts FastAPI on port 8000)

---

## 🖼️ 2. Pitch Visualizer
The **Pitch Visualizer** transforms a sales pitch narrative into a multi-panel cinematic storyboard, complete with an automated PowerPoint deck and a video preview.

### Key Features:
- **Narrative Segmentation**: Automatically splits your pitch into key scenes.
- **Cinematic Image Generation**: Uses the Flux-v1 engine for high-quality visuals.
- **Export to PPT/Video**: One-click generation of professional pitch assets.

### How to Run:
1. `cd pitch-visualizer`
2. `python -m venv venv`
3. `venv\Scripts\activate`
4. `pip install -r requirements.txt`
5. `python main.py` (starts FastAPI on port 8000)

---

## 🛠️ General Setup

### Environment Variables
Both projects require a `.env` file for configuration. Use the provided `.env.example` (or create a new one) with the following:
- `GOOGLE_API_KEY`: Required for Gemini-based prompt enhancement in Pitch Visualizer.
- `ELEVENLABS_API_KEY`: (Optional) For high-quality cloud-based TTS in Empathy Engine.

### Requirements
- Python 3.9+
- ffmpeg (for video generation)

---

## 👨‍💻 Author
**Satish**
[GitHub](https://github.com/satish05112003) | [Project Repository](https://github.com/satish05112003/Ai-sales-toolkit)
