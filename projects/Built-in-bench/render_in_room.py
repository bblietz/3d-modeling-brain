#!/usr/bin/env python
"""Photoreal composite: the empty-alcove photo with the designed bench in it,
made with Gemini 3 Pro Image (the nanobanana skill's model and venv).

Inputs: images/space-photo-web.jpg (the room, image 1) and images/hero.png
(the CAD render, image 2, design reference). Output: images/bench-in-nook.png.

Usage: ~/.claude/skills/nanobanana/.venv/bin/python projects/Built-in-bench/render_in_room.py [variant]
"""
import os
import sys

from google import genai
from google.genai import types

VAULT = "/home/brian/ClaudeProjects/3d-modeling-brain"
PROJ = f"{VAULT}/projects/Built-in-bench"
MODEL = "gemini-3-pro-image-preview"
variant = sys.argv[1] if len(sys.argv) > 1 else ""
OUT = f"{PROJ}/images/bench-in-nook{('-' + variant) if variant else ''}.png"

PROMPT = """Image 1 is a photo of an empty alcove in a house (a former wet bar): cream walls, a white baseboard,
dark hand-scraped plank floor, a six-panel door at the left, a passage past the right pilaster.
Image 2 is a CAD rendering of a built-in bench designed for exactly this alcove.

Edit image 1 so the bench from image 2 is built into the alcove, as a realistic photograph taken with the
same camera, from the same spot, with the same lens, lighting, white balance, shadows and grain as image 1.
Keep the walls, door, floor, trim outside the alcove and everything else exactly as they are.

The bench, built the way image 2 shows it:
- It spans the alcove wall to wall (66 inches) with no gaps; its maple front sits 3 inches back from the
  faces of the two pilasters, and the seat is low: the wood top is 16 inches above the floor.
- Two drawers side by side, full width. Each drawer front is a flat panel: a pale clear-finished hard maple
  frame about 1-1/2 inches wide around a dark chocolate walnut veneer panel, flush, with a thin 1/8 inch
  shadow gap around each front. One 8 inch brushed brass bar pull centered on each drawer.
- A solid hard maple top, 3/4 inch thick, with a gently eased front edge overhanging the drawer fronts by 3/4
  inch. On it sits one long boxed cushion, 3 inches thick, oatmeal linen, covering the whole top.
- A flush maple plinth 4 inches tall at the floor, in the same plane as the drawer fronts, in place of the
  baseboard, which has been removed inside the alcove. Narrow maple strips at each wall.
- Clear satin finish: the maple reads pale blond, the walnut dark brown with visible grain. No shelves above,
  no dog, no accessories. Photorealistic, no CAD look, correct perspective into the alcove."""

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
parts = []
for path, mime in ((f"{PROJ}/images/space-photo-web.jpg", "image/jpeg"), (f"{PROJ}/images/hero.png", "image/png")):
    with open(path, "rb") as f:
        parts.append(types.Part.from_bytes(data=f.read(), mime_type=mime))
parts.append(PROMPT)
cfg = types.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"],
                                  image_config=types.ImageConfig(aspect_ratio="3:4", image_size="2K"))
resp = client.models.generate_content(model=MODEL, contents=parts, config=cfg)
img = text = None
for p in resp.candidates[0].content.parts:
    if p.inline_data and p.inline_data.mime_type.startswith("image/"):
        img = p.inline_data.data
    elif p.text:
        text = p.text
if not img:
    sys.exit(f"no image: {text}")
with open(OUT, "wb") as f:
    f.write(img)
print("wrote", os.path.relpath(OUT, VAULT), os.path.getsize(OUT) // 1024, "KB")
# cost: Brian's rule, report every metered call. Google list price 2026-10: image output $120 per 1M tokens
# (1120 tokens for a 1K/2K image = $0.134, 2000 for 4K = $0.24); input $2 per 1M tokens (text and images).
u = resp.usage_metadata
in_tok = getattr(u, "prompt_token_count", 0) or 0
out_tok = getattr(u, "candidates_token_count", 0) or 0
print(f"usage: {in_tok} input tokens, {out_tok} output tokens; estimated cost ${in_tok * 2e-6 + out_tok * 120e-6:.3f} "
      "(image output $120/1M tokens, input $2/1M)")
if text:
    print("model said:", text[:300])
