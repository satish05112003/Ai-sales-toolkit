# AI Sales Toolkit

[![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green?logo=fastapi)](https://fastapi.tiangolo.com/)

AI Sales Toolkit is a dual-system AI application designed to improve communication and storytelling. It combines emotion-aware speech generation with AI-powered visual storytelling.

---

## Overview

This repository contains two main systems:

### Task 1: Empathy Engine
An AI system that detects emotions in text and adjusts voice output accordingly.

### Task 2: Pitch Visualizer
A system that converts text into storyboard visuals and exports them as PowerPoint presentations and videos.

---

## Repository Structure

```
AI-Sales-Toolkit/
├── empathy-engine/
├── pitch-visualizer/
└── README.md
```

---

# Task 1: Empathy Engine

## Description

Empathy Engine enhances traditional text-to-speech systems by adding emotional intelligence. It analyzes text input and modifies voice parameters to match the detected emotion.

---

## Features

- Emotion detection using NLP models  
- Dynamic voice parameter adjustment (speed and volume)  
- Multiple emotion handling  
- Improved natural speech output  

---

## Design Choices (Important)

### Emotion Detection

A transformer-based NLP model is used to classify text into emotions such as:
- happy
- sad
- angry
- neutral

### Emotion to Voice Mapping

| Emotion | Speech Rate | Volume | Purpose |
|--------|------------|--------|--------|
| Happy  | High       | High   | Energy and confidence |
| Sad    | Low        | Low    | Empathy and seriousness |
| Angry  | High       | High   | Urgency and intensity |
| Neutral| Normal     | Normal | Informational tone |

### Reasoning

These mappings are based on common human speech patterns:
- Faster and louder speech expresses excitement  
- Slower and softer speech expresses seriousness  

This improves listener engagement and realism.

---

## Setup and Run

```bash
cd empathy-engine
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Open in browser:
http://localhost:8000

---

# Task 2: Pitch Visualizer

## Description

Pitch Visualizer converts text into visual storyboards. It generates images for each scene and allows exporting results as PowerPoint and video files.

---

## Capabilities

- Convert text into scenes  
- Generate AI images  
- Enhance prompts for better quality  
- Export as PPT  
- Export as video  

---

## Workflow

```
Text Input → Scene Segmentation → Prompt Enhancement → Image Generation → PPT → Video
```

---

## Design Choices (Important)

### Prompt Engineering Strategy

Instead of sending raw text, the system enhances prompts before image generation.

### Prompt Enhancement

Each prompt includes:

- Cinematic composition  
- Lighting details  
- Camera effects  
- High-quality rendering instructions  

### Reasoning

This ensures:
- Better image quality  
- Consistent results  
- Professional output  

---

## Setup and Run

```bash
cd pitch-visualizer
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file:

```
GOOGLE_API_KEY=your_api_key
```

Do not commit `.env` to GitHub.

---

### Install FFmpeg

Required for video export.

Check installation:

```bash
ffmpeg -version
```

---

### Run Server

```bash
uvicorn main:app --reload --port 8000
```

Open:
http://localhost:8000

---

## System Architecture

```
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
```

---

## Tech Stack

- Python  
- FastAPI  
- HTML, CSS, JavaScript  
- Transformers (NLP)  
- Image generation APIs  
- python-pptx  
- FFmpeg  

---

## Installation (Combined)

```bash
git clone https://github.com/satish05112003/Ai-sales-toolkit.git
cd Ai-sales-toolkit
```

Set up each module separately.

---

## Usage

### Empathy Engine

- Input text  
- Detect emotion  
- Generate expressive speech  

### Pitch Visualizer

- Input story  
- Generate storyboard  
- Download PPT or video  

---

## Troubleshooting

- Ensure dependencies are installed  
- Check FFmpeg installation  
- Verify `.env` configuration  
- Increase delay if API rate limits occur  

---
