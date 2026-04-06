"""
Pitch Visualizer: From Words to Storyboard
Main FastAPI application
"""

import os
import uuid
import asyncio
from pathlib import Path
from typing import List

from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env

from fastapi import FastAPI, Request, HTTPException

from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from segmenter import segment_narrative
from image_generator import generate_image, enhance_prompt, STYLE_PRESETS
from ppt_generator import create_ppt
from video_generator import create_video

# ── App setup ──────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "storyboard_outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Pitch Visualizer", version="1.0.0")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.mount("/storyboard_outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


# ── Request / Response models ──────────────────────────────────────────────────
class StoryboardRequest(BaseModel):
    text: str
    style: str = "photorealistic"   # photorealistic | cartoon | digital_art


class StoryboardResponse(BaseModel):
    session_id: str
    images: List[str]
    captions: List[str]
    prompts: List[str]
    style: str


# ── Routes ─────────────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # Debug: Check if STYLE_PRESETS is correctly imported
    print(f"DEBUG: STYLE_PRESETS type is {type(STYLE_PRESETS)}")

    # Pre-compute styles safely as a fallback
    styles = list(STYLE_PRESETS.keys()) if isinstance(STYLE_PRESETS, dict) else []

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"styles": styles}
    )


@app.post("/generate-storyboard", response_model=StoryboardResponse)
async def generate_storyboard(payload: StoryboardRequest):
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    style = payload.style if payload.style in STYLE_PRESETS else "photorealistic"

    # 1. Segment narrative into scenes (already limited to 3 in segmenter.py)
    scenes = segment_narrative(text)
    
    # 2. Setup session
    session_id = uuid.uuid4().hex[:8]
    session_dir = OUTPUT_DIR / session_id
    session_dir.mkdir(exist_ok=True)

    image_paths: List[str] = []
    used_prompts: List[str] = []
    
    # 3. Generate images (Strictly sequential)
    for i, scene in enumerate(scenes):
        try:
            # We call enhance_prompt here just to capture it for the UI (Step 5)
            # image_generator.generate_image will ALSO call it internally (Step 2)
            enhanced = enhance_prompt(scene, style)
            used_prompts.append(enhanced)

            print(f"[Main] Processing Scene {i+1}/{len(scenes)}...")
            result = await generate_image(scene, session_dir / f"scene_{i+1:02d}.png", style)
            
            if result:
                web_path = f"/storyboard_outputs/{session_id}/{Path(result).name}"
                image_paths.append(web_path)
            
            # Step 6: Cooldown to prevent rate-limits
            if i < len(scenes) - 1:
                await asyncio.sleep(2)
        except Exception as e:
            print(f"Error on scene {i+1}: {e}")

    # 4. Export to PPT and Video (Part 3 integration)
    # Filter out None results from image_paths (only use successful ones)
    full_image_paths = [Path(BASE_DIR) / p.lstrip('/') for p in image_paths]
    
    # Session-specific output paths to avoid collisions
    ppt_path_local   = session_dir / "storyboard.pptx"
    video_path_local = session_dir / "storyboard.mp4"
    
    create_ppt(full_image_paths, scenes, used_prompts, output_path=str(ppt_path_local))
    create_video(full_image_paths, output_path=str(video_path_local))

    # Also save to fixed root path as fallback (per user request Part 4)
    import shutil
    shutil.copy(ppt_path_local, "storyboard.pptx")
    shutil.copy(video_path_local, "storyboard.mp4")

    print(f"[Main] Storyboard complete! Session: {session_id}")

    # Step 5: Returning prompts and scene count for UI display
    return {
        "session_id": session_id,
        "images": image_paths,
        "captions": scenes,
        "prompts": used_prompts,
        "style": style,
        "total_scenes": len(scenes)
    }




@app.get("/storyboard/{session_id}", response_class=HTMLResponse)
async def view_storyboard(request: Request, session_id: str):
    """Render a full-page storyboard for sharing."""
    session_dir = OUTPUT_DIR / session_id
    if not session_dir.exists():
        raise HTTPException(status_code=404, detail="Storyboard not found.")

    images = sorted(session_dir.glob("scene_*.png"))
    panels = [
        {"image": f"/storyboard_outputs/{session_id}/{p.name}",
         "caption": f"Scene {i+1}"}
        for i, p in enumerate(images)
    ]
    return templates.TemplateResponse(
        request=request,
        name="storyboard.html",
        context={"panels": panels, "session_id": session_id},
    )



@app.get("/download-ppt")
async def download_ppt():
    """Download the latest generated PPT pitch deck."""
    ppt_path = Path("storyboard.pptx")
    if not ppt_path.exists():
        raise HTTPException(status_code=404, detail="Pitch deck not found. Generate it first.")
    return FileResponse(str(ppt_path), filename="storyboard.pptx")


@app.get("/download-video")
async def download_video():
    """Download the latest generated video demo."""
    video_path = Path("storyboard.mp4")
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video not found. Generate it first.")
    return FileResponse(str(video_path), filename="storyboard.mp4")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
