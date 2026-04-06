# AI Sales Toolkit

AI Sales Toolkit is a dual-system application that combines emotion-aware speech synthesis and AI-driven visual storytelling. It enables users to generate expressive voice outputs and convert ideas into structured visual presentations.

---

## Overview

This repository contains two independent but complementary systems:

- **Empathy Engine (Task 1)**  
  An NLP-based system that detects emotions in text and maps them to voice parameters for expressive speech generation.

- **Pitch Visualizer (Task 2)**  
  A system that converts textual input into storyboard visuals and exports them as PowerPoint presentations and video files.

---

## Repository Structure

AI-Sales-Toolkit/
├── empathy-engine/
├── pitch-visualizer/
└── README.md

---

# Task 1: Empathy Engine

## Description

The Empathy Engine enhances traditional text-to-speech systems by incorporating emotional context. It processes input text, identifies the underlying emotion, and adjusts speech characteristics accordingly.

---

## Key Features

- Emotion classification using NLP models  
- Dynamic voice parameter tuning (rate, volume)  
- Support for multiple emotional tones  
- Improved speech realism  

---

## Design Decisions

### Emotion Detection

A transformer-based NLP model is used to classify text into emotions such as happy, sad, angry, and neutral.

### Emotion-to-Voice Mapping

| Emotion  | Speech Rate | Volume | Purpose |
|----------|------------|--------|--------|
| Happy    | High       | High   | Energy and excitement |
| Sad      | Low        | Low    | Empathy and seriousness |
| Angry    | High       | High   | Urgency and intensity |
| Neutral  | Normal     | Normal | Informational tone |

### Rationale

These mappings replicate natural human speech behavior, improving engagement and clarity.

---

## Setup and Run

```bash
cd empathy-engine
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py

Open:
http://localhost:8000

⸻

Task 2: Pitch Visualizer

Description

Pitch Visualizer converts textual narratives into storyboard visuals. It generates images for each scene and allows exporting results as PowerPoint and video files.

⸻

Workflow

Text → Scenes → Prompt Enhancement → Image Generation → PPT → Video


⸻

Key Features
	•	Automatic scene segmentation
	•	AI-based image generation
	•	Prompt enhancement for better visuals
	•	PPT export (slide per scene)
	•	Video export (slideshow)
	•	Sequential processing for stability

⸻

Design Decisions

Prompt Engineering Strategy

Raw text is enhanced before being sent to the image generator.

Prompt Enhancement

Each prompt includes:
	•	Cinematic composition
	•	Lighting details
	•	Camera effects
	•	High-quality rendering instructions

Rationale

This ensures consistent, high-quality, and professional outputs.

⸻

Setup and Run

cd pitch-visualizer
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

Environment Variables

Create a .env file:

GOOGLE_API_KEY=your_api_key

Install FFmpeg

Verify installation:

ffmpeg -version

Run Server

uvicorn main:app --reload --port 8000

Open:
http://localhost:8000

⸻

System Architecture

User Input
   ↓
Processing Layer
   ├── Emotion Detection (Task 1)
   └── Scene Segmentation (Task 2)
   ↓
Generation Layer
   ├── Voice Output
   └── Image Generation
   ↓
Export Layer
   ├── PPT Export
   └── Video Export


⸻

Tech Stack
	•	Python
	•	FastAPI
	•	HTML, CSS, JavaScript
	•	Transformers (NLP)
	•	Image generation APIs
	•	python-pptx
	•	FFmpeg

⸻

Installation (Combined)

git clone https://github.com/satish05112003/Ai-sales-toolkit.git
cd Ai-sales-toolkit

Set up each project separately.

⸻

Usage

Task 1
	•	Input text
	•	Detect emotion
	•	Generate expressive speech

Task 2
	•	Input story
	•	Generate storyboard
	•	Download PPT or video

⸻

Troubleshooting
	•	Install required dependencies
	•	Ensure FFmpeg is installed
	•	Check .env file for API keys
	•	Increase delay if rate limits occur

⸻


👉 demo GIF  

Just say 👍
