AI Sales Toolkit

AI Sales Toolkit is a dual-system application that combines emotion-aware speech synthesis and AI-driven visual storytelling. It enables users to generate expressive voice outputs and convert ideas into structured visual presentations.

⸻

Overview

This repository contains two independent but complementary systems:
	•	Empathy Engine (Task 1)
An NLP-based system that detects emotions in text and maps them to voice parameters for expressive speech generation.
	•	Pitch Visualizer (Task 2)
A pipeline that converts textual input into storyboard visuals and exports them as PowerPoint presentations and video files.

⸻

Repository Structure

AI-Sales-Toolkit/
├── empathy-engine/
├── pitch-visualizer/
└── README.md


⸻

Task 1: Empathy Engine

Description

The Empathy Engine is designed to enhance text-to-speech systems by incorporating emotional context. It processes input text, identifies the underlying emotion, and adjusts speech characteristics accordingly.

Key Features
	•	Emotion classification using NLP models
	•	Dynamic voice parameter tuning (rate, volume)
	•	Support for multiple emotional tones
	•	Improved speech realism over standard TTS

⸻

Design Decisions

Emotion Detection
The system uses a pre-trained transformer-based model to classify text into emotion categories such as happy, sad, angry, and neutral. This allows accurate detection of user intent.

Emotion-to-Voice Mapping
Each emotion is mapped to specific speech parameters:

Emotion	Speech Rate	Volume	Purpose
Happy	High	High	Convey energy and positivity
Sad	Low	Low	Convey empathy and seriousness
Angry	High	High	Convey urgency and intensity
Neutral	Normal	Normal	Informational tone

Rationale
Human communication relies heavily on tone and pacing. These mappings replicate natural speech behavior, improving listener engagement and clarity.

⸻

Setup and Execution

cd empathy-engine
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py

Access the application at:
http://localhost:8000

⸻

Task 2: Pitch Visualizer

Description

Pitch Visualizer transforms textual narratives into visual storyboards. It generates images for each scene and supports exporting outputs as PowerPoint presentations and video files.

⸻

Pipeline

Text Input
   ↓
Scene Segmentation
   ↓
Prompt Enhancement
   ↓
Image Generation
   ↓
PPT Export / Video Export


⸻

Key Features
	•	Automatic scene segmentation
	•	AI-based image generation
	•	Prompt enhancement for improved visuals
	•	Export to PPT (slide per scene)
	•	Export to MP4 video
	•	Sequential processing for stability

⸻

Design Decisions

Prompt Engineering
Raw text is not directly passed to the image generator. Instead, prompts are enhanced using structured descriptors.

Prompt Enhancement Strategy
Each prompt includes:
	•	Composition details (camera angle, framing)
	•	Lighting conditions (cinematic, dramatic, soft)
	•	Quality attributes (high resolution, detailed textures)

Rationale
Enhanced prompts ensure consistent, high-quality outputs and reduce randomness in generated images.

⸻

Setup and Execution

cd pitch-visualizer
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

Create a .env file (do not commit):

GOOGLE_API_KEY=your_api_key

Install FFmpeg and ensure it is available in PATH.

Run the server:

uvicorn main:app --reload --port 8000

Access:
http://localhost:8000

⸻

System Architecture

The system follows a modular pipeline:
	•	Input Layer: Accepts user text
	•	Processing Layer:
	•	Emotion detection (Task 1)
	•	Scene segmentation (Task 2)
	•	Generation Layer:
	•	Voice synthesis
	•	Image generation
	•	Export Layer:
	•	PowerPoint generation
	•	Video rendering

⸻

Technology Stack
	•	Python
	•	FastAPI
	•	HTML, CSS, JavaScript
	•	Transformers (NLP models)
	•	External image generation APIs
	•	python-pptx
	•	FFmpeg

⸻

Installation (Combined)

git clone https://github.com/satish05112003/Ai-sales-toolkit.git
cd Ai-sales-toolkit

Set up each module independently (recommended).

⸻

Usage

Empathy Engine
	•	Provide text input
	•	System detects emotion
	•	Outputs expressive speech

Pitch Visualizer
	•	Provide narrative input
	•	System generates storyboard
	•	Download outputs as PPT or video

⸻

Troubleshooting
	•	Ensure dependencies are installed
	•	Verify FFmpeg installation for video export
	•	Check API keys in .env
	•	Increase delay if API rate limits occur
