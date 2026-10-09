#!/usr/bin/env python
"""Photoreal composites of the designed bench in Brian's alcove, made with Gemini 3 Pro Image
(the nanobanana skill's model and venv). Every run prints its token usage and a dollar estimate
(Brian's rule: report the cost of each metered call).

Jobs:
  bench    images/space-photo-web.jpg (the room) + images/hero.png (CAD render) -> images/bench-in-nook.png
  shelves  images/bench-in-nook-v2.png (the composite) + images/concept-ai-bench-web.jpg (the concept)
           -> images/bench-in-nook-shelves.png, three maple floating shelves added above the bench
  white    images/bench-in-nook-shelves-10in.png -> images/bench-in-nook-white.png, the bench's maple painted
           white with the walnut panels, maple top and maple shelves kept bare
  white-maple  images/bench-in-nook-white.png -> images/bench-in-nook-white-maple.png, the white bench with
           pale maple panels in the drawer fronts instead of walnut
  white-inset  images/bench-in-nook-white.png + images/hero.png -> images/bench-in-nook-white-inset.png, the white
           bench with the 1/2 walnut panels visibly recessed 1/4 in below the white frames
  white-all  images/bench-in-nook-white.png -> images/bench-in-nook-white-all.png, the white bench with the
           drawer panels painted white too (all-white fronts, brass pulls, maple top and shelves bare)

Usage: ~/.claude/skills/nanobanana/.venv/bin/python projects/Built-in-bench/render_in_room.py [bench|shelves|white|white-maple|white-all|white-inset] [variant]
A variant name is appended to the output file so reruns do not overwrite earlier images.
"""
import os
import sys

from google import genai
from google.genai import types

VAULT = "/home/brian/ClaudeProjects/3d-modeling-brain"
PROJ = f"{VAULT}/projects/Built-in-bench"
MODEL = "gemini-3-pro-image-preview"

BENCH_PROMPT = """Image 1 is a photo of an empty alcove in a house (a former wet bar): cream walls, a white baseboard,
dark hand-scraped plank floor, a six-panel door at the left, a passage past the right pilaster. The alcove is
66 inches wide between the two pilasters and 28 inches deep from the back wall to the pilaster faces.
Image 2 is a CAD rendering of a built-in bench designed for exactly this alcove.

Edit image 1 so the bench from image 2 is built into the alcove, as a realistic photograph taken with the
same camera, from the same spot, with the same lens, lighting, white balance, shadows and grain as image 1.
Keep the walls, door, floor, trim outside the alcove and everything else exactly as they are.

DEPTH IS THE CRITICAL PART. The bench is 25 inches deep and fills almost the whole 28 inch depth of the alcove.
Its top's front edge is only 3 inches behind the faces of the pilasters, so the bench front is nearly flush
with the pilaster faces. Of each pilaster's inner side wall, only a 3 inch wide strip remains visible in front
of the bench; the rest of the side walls is hidden behind the bench. The front of the bench must NOT be
recessed deep into the alcove. Seen from this camera, the drawer fronts sit just behind the plane of the
pilaster faces, and the top and cushion come almost out to that plane.

The bench, built the way image 2 shows it:
- It spans the alcove wall to wall (66 inches) with no gaps. The seat is low: the wood top is 16 inches above
  the floor, the cushion top 19 inches.
- Two drawers side by side, full width. Each drawer front is a flat panel: a pale clear-finished hard maple
  frame only 1-1/2 inches wide around a dark chocolate walnut veneer panel, flush, with a thin 1/8 inch
  shadow gap around each front. One 8 inch brushed brass bar pull centered on each drawer.
- A solid hard maple top, 3/4 inch thick, with a gently eased front edge overhanging the drawer fronts by 3/4
  inch. On it sits one long boxed cushion, 3 inches thick, oatmeal linen, covering the whole 25 inch depth.
- A flush maple plinth 4 inches tall at the floor, in the same plane as the drawer fronts, in place of the
  baseboard, which has been removed inside the alcove. Narrow maple strips at each wall.
- Clear satin finish: the maple reads pale blond, the walnut dark brown with visible grain. No shelves above,
  no dog, no accessories. Photorealistic, no CAD look, correct perspective into the alcove."""

SHELVES_PROMPT = """Image 1 is a photograph of a built-in bench in an alcove: two walnut-and-maple drawers, a solid maple top, an
oatmeal cushion, cream walls above. Image 2 is a concept picture of a similar alcove with three floating shelves
above the bench.

Edit image 1 to add three floating shelves above the bench, laid out like the shelves in image 2, and change
nothing else: same camera, lighting, walls, floor, door, and the bench exactly as it is.

The shelves:
- Solid hard maple, clear satin finish, the same pale blond maple as the bench's top and frames (not white oak,
  not darker). Each shelf is one thick slab 1-1/2 inches thick and a full 10 INCHES DEEP: it projects 10 inches
  out from the back wall, so its front edge stops 18 inches short of the pilaster faces (the alcove is 28
  inches deep). From this camera the top face of each shelf is clearly visible as a deep slab, not a thin
  ledge. Each spans the alcove wall to wall (66 inches) with no visible brackets, like the shelves in image 2.
- Three shelves, evenly spaced: the lowest about 20 inches above the cushion, the others about 14 inches apart,
  all well below the ceiling. Their front edges are set back a few inches from the pilaster faces.
- Lightly styled the way image 2 is: a few books, a small plant, a basket, a framed picture. No dog, no dog
  bowls, no signs with words, no lights added. Photorealistic, matching image 1's grain and white balance."""

WHITE_PROMPT = """Image 1 is a photograph of a built-in bench in an alcove with three maple floating shelves above it. The bench
has two drawers, each a pale maple frame around a dark walnut panel with a brass bar pull, a pale maple plinth at
the floor, narrow maple strips at the walls, a solid maple top and an oatmeal cushion.

Edit image 1 so the bench's woodwork is PAINTED WHITE, and change nothing else. Repaint in a smooth satin white
enamel, the same white as the door and the baseboards in the photo: the drawer frames (stiles and rails), the
plinth at the floor, the narrow strips at the walls, and the thin edge of the case that shows between them.
Keep exactly as they are: the dark walnut panels inside the frames (bare wood, visible grain), the brass bar
pulls, the solid maple top with its bare blond wood and 3/4 inch overhang, the oatmeal cushion, the three maple
shelves with their objects, the walls, floor, door, lighting and camera. Painted surfaces show no wood grain,
with soft sprayed-enamel reflections. Photorealistic, matching image 1's grain and white balance."""

WHITE_MAPLE_PROMPT = """Image 1 is a photograph of a built-in bench in an alcove with three maple floating shelves above it. The bench
is painted satin white: white drawer frames, a white plinth at the floor, white strips at the walls. Inside each
white drawer frame is a dark walnut panel with a brass bar pull. The top is bare solid maple with an oatmeal
cushion on it.

Edit image 1 so the two DARK WALNUT PANELS inside the white drawer frames become PALE MAPLE PANELS, and change
nothing else. Each panel is maple veneer plywood with a clear satin finish: the same pale blond maple as the
bench top and the three shelves, creamy light wood, not white, not yellow, not orange, with fine subtle straight
grain running horizontally along the long dimension of the panel. The panels stay flush inside the white frames
with the same thin shadow lines, and the brass bar pulls stay exactly where they are. Keep exactly as they are:
the white painted frames, plinth and wall strips, the maple top, the cushion, the three maple shelves with their
objects, the walls, floor, door, lighting and camera. Photorealistic, matching image 1's grain and white balance."""

WHITE_ALL_PROMPT = """Image 1 is a photograph of a built-in bench in an alcove with three maple floating shelves above it. The bench
is painted satin white: white drawer frames, a white plinth at the floor, white strips at the walls. Inside each
white drawer frame is a dark walnut panel with a brass bar pull. The top is bare solid maple with an oatmeal
cushion on it.

Edit image 1 so the two DARK WALNUT PANELS inside the white drawer frames are PAINTED WHITE as well, and change
nothing else. Each drawer front becomes all white: the panel is the same smooth satin white enamel as the frame
around it, with no wood grain, so the frame and panel are only told apart by the thin shadow line of the
tongue-and-groove joint where the panel sits in the frame. The brass bar pulls stay exactly where they are. Keep
exactly as they are: the white painted frames, plinth and wall strips, the bare maple top, the cushion, the three
maple shelves with their objects, the walls, floor, door, lighting and camera. Photorealistic, soft sprayed-enamel
reflections on the painted surfaces, matching image 1's grain and white balance."""

WHITE_INSET_PROMPT = """Image 1 is a photograph of a built-in bench in an alcove with three maple floating shelves above it. The bench
is painted satin white, with a dark walnut panel inside each white drawer frame, brass bar pulls, a bare maple top
and an oatmeal cushion. Image 2 is a CAD rendering of the same bench, only to show how the walnut panels are built.

Edit image 1 so each dark walnut panel is visibly INSET: the panel face sits recessed about 1/4 inch BELOW the
front face of the white frame on all four sides, like a shaker door with a shallow recess. The white frame's inner
edges therefore show as a thin, crisp white step around the panel, and the top edge of the opening casts a soft
shadow onto the upper part of the walnut panel. Keep the panel itself flat, bare walnut with visible grain and no
raised profile or bevel. Do not change anything else: the white frames, plinth and wall strips, the brass pulls in
the same places, the bare maple top, the cushion, the three maple shelves with their objects, the walls, floor,
door, lighting and camera. Photorealistic, matching image 1's grain and white balance."""

JOBS = {
    "bench": ((f"{PROJ}/images/space-photo-web.jpg", "image/jpeg"), (f"{PROJ}/images/hero.png", "image/png"),
              BENCH_PROMPT, "bench-in-nook"),
    "shelves": ((f"{PROJ}/images/bench-in-nook-v2.png", "image/png"),
                (f"{PROJ}/images/concept-ai-bench-web.jpg", "image/jpeg"), SHELVES_PROMPT, "bench-in-nook-shelves"),
    "white": ((f"{PROJ}/images/bench-in-nook-shelves-10in.png", "image/png"), None, WHITE_PROMPT, "bench-in-nook-white"),
    "white-maple": ((f"{PROJ}/images/bench-in-nook-white.png", "image/png"), None, WHITE_MAPLE_PROMPT,
                    "bench-in-nook-white-maple"),
    "white-all": ((f"{PROJ}/images/bench-in-nook-white.png", "image/png"), None, WHITE_ALL_PROMPT,
                  "bench-in-nook-white-all"),
    "white-inset": ((f"{PROJ}/images/bench-in-nook-white.png", "image/png"), (f"{PROJ}/images/hero.png", "image/png"),
                    WHITE_INSET_PROMPT, "bench-in-nook-white-inset"),
}
job = sys.argv[1] if len(sys.argv) > 1 else "bench"
if job not in JOBS:
    sys.exit(f"unknown job {job!r}; use one of {list(JOBS)}")
variant = sys.argv[2] if len(sys.argv) > 2 else ""
img1, img2, PROMPT, stem = JOBS[job]
OUT = f"{PROJ}/images/{stem}{('-' + variant) if variant else ''}.png"

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
parts = []
for path, mime in [i for i in (img1, img2) if i]:
    with open(path, "rb") as f:
        parts.append(types.Part.from_bytes(data=f.read(), mime_type=mime))
parts.append(PROMPT)
cfg = types.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"],
                                  image_config=types.ImageConfig(aspect_ratio="3:4", image_size="2K"))
resp = client.models.generate_content(model=MODEL, contents=parts, config=cfg)
img = text = None
for part in resp.candidates[0].content.parts:
    if part.inline_data and part.inline_data.mime_type.startswith("image/"):
        img = part.inline_data.data
    elif part.text:
        text = part.text
if not img:
    sys.exit(f"no image: {text}")
with open(OUT, "wb") as f:
    f.write(img)
print("wrote", os.path.relpath(OUT, VAULT), os.path.getsize(OUT) // 1024, "KB")
if text:
    print("model said:", text[:300])
# cost: Google list price 2026-10: image output $120 per 1M tokens (1120 tokens for a 1K/2K image = $0.134,
# 2000 for 4K = $0.24); input $2 per 1M tokens (text and images).
u = resp.usage_metadata
in_tok = getattr(u, "prompt_token_count", 0) or 0
out_tok = getattr(u, "candidates_token_count", 0) or 0
print(f"usage: {in_tok} input tokens, {out_tok} output tokens; estimated cost ${in_tok * 2e-6 + out_tok * 120e-6:.3f} "
      "(image output $120/1M tokens, input $2/1M)")
