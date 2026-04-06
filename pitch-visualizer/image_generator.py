"""
image_generator.py
High-Quality Image Generator for "Pitch Visualizer".
- Upgraded to Flux-v1 Engine (World-class quality)
- Built-in Visual Prompt Enhancer (Cinematic, Lighting, Atmosphere)
- Sequential processing with 3x retry and safe error handling.
"""

import os
import asyncio
import httpx
from pathlib import Path
from typing import Optional
import urllib.parse

# ── Style Presets ─────────────────────────────────────────────────────────────
STYLE_PRESETS = {
    "photorealistic": "ultra realistic, cinematic lighting",
    "cinematic": "movie still, dramatic lighting, film look",
    "cartoon": "animated, vibrant, stylized",
    "digital_art": "concept art, detailed painting"
}

# ── Cinematic Visual Prompt Enhancer ──────────────────────────────────────────

def enhance_prompt(prompt: str, style: str = "photorealistic") -> str:
    """
    Transforms a simple scene sentence into a highly detailed cinematic prompt.
    Fixes Step 1.
    """
    base = f"""
    {prompt},
    ultra realistic, cinematic composition,
    dramatic lighting, volumetric lighting,
    depth of field, 35mm lens,
    highly detailed, professional photography,
    sharp focus, 4k resolution,
    emotional storytelling scene
    """
    
    style_sfx = STYLE_PRESETS.get(style, STYLE_PRESETS["photorealistic"])
    
    if style == "cartoon":
        base += ", animated style, vibrant colors, 2D illustration"
    elif style == "digital_art":
        base += ", concept art, artstation style, digital painting"
    elif style == "cinematic":
        base += ", movie still, dramatic shadows, film grain"
    
    # Return a clean single-line prompt for the API
    return " ".join(base.split()).strip()

# ── Flux Image Generation with Retry ────────────────────────────────────────

async def generate_image(prompt: str, output_path: Path, style: str = "photorealistic") -> str:
    """
    Use the high-quality Flux model (via Pollinations) to generate presentation-ready images.
    Features Step 2: Encapsulated prompt enhancement.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Step 2: Force prompt enhancement
    enhanced_prompt = enhance_prompt(prompt, style)
    
    encoded_prompt = urllib.parse.quote(enhanced_prompt)
    seed = os.urandom(4).hex()
    
    pollinations_url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}?"
        f"width=1024&height=1024&nologo=true&model=flux&seed={seed}"
    )
    
    print(f"[Flux Engine] Generating: {prompt[:40]}...")
    print(f"  > Enhanced: {enhanced_prompt[:60]}...")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        for attempt in range(1, 4):
            try:
                response = await client.get(pollinations_url)
                if response.status_code == 200:
                    with open(output_path, "wb") as f:
                        f.write(response.content)
                    print(f"  > Success: Saved to {output_path}")
                    return str(output_path)
                else:
                    print(f"  > Attempt {attempt} failed: HTTP {response.status_code}")
                    if attempt < 3: await asyncio.sleep(2)
            except Exception as e:
                print(f"  > Attempt {attempt} error: {e}")
                if attempt < 3: await asyncio.sleep(2)

    return None





