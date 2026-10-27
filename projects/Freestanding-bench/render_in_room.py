#!/usr/bin/env python
"""Photoreal composites of the freestanding bench in the client's alcove, made with Gemini 3 Pro Image (the
nanobanana skill's model and venv). Every run prints its token usage and a dollar estimate (Brian's rule: report
the cost of each metered call). Same method as projects/Built-in-bench/render_in_room.py: Gemini only
photorealizes a true-scale CAD overlay (photo_match.py) and may not move an edge; verify every output with
`photo_match.py check <output>`.

Jobs (BASE=legs|blades|gables picks the overlay for `guided`, default legs; outputs carry no base suffix, so pass a
variant name as the second argument when making pictures of the other bases):
  guided        images/alcove-overlay-<base>.png -> images/bench-in-nook-guided.png: the flat CAD bench, shelves and
                soffit made photoreal, nothing moved
  styled        images/bench-in-nook-guided.png + images/concept-ai-bench-web.jpg (the client's reference) +
                images/maizy.jpg + images/franco.jpg -> images/bench-in-nook-styled.png: the pillows, throw, shelf
                objects, sign and rug from the reference, and the client's two dogs on the cushion (no bowls, no collar)
  dogs          images/bench-in-nook-styled.png + the two dog photos -> images/bench-in-nook-dogs.png: fallback if the
                styled pass drew the wrong dogs; replaces whatever dog it drew with Maizy and Franco
  soffit-paint  images/bench-in-nook-styled.png -> images/bench-in-nook-soffit-paint.png: fallback if the soffit's
                underside came out blue-grey (it did in every pass of the built-in chain)

Usage: ~/.claude/skills/nanobanana/.venv/bin/python projects/Freestanding-bench/render_in_room.py [guided|styled|dogs|soffit-paint] [variant]
A variant name is appended to the output file so reruns do not overwrite earlier images.
"""
import os
import sys

from google import genai
from google.genai import types

VAULT = "/home/brian/ClaudeProjects/3d-modeling-brain"
PROJ = f"{VAULT}/projects/Freestanding-bench"
MODEL = "gemini-3-pro-image-preview"
BASE = os.environ.get("BASE", "legs")

GUIDED_PROMPT = """Image 1 is a photograph of an empty alcove (a former wet bar) into which a freestanding bench, three floating shelves
and a dropped soffit have been placed by CAD, flat-shaded, at their exact built size and position. The perspective, the
size, the height and every edge of the bench, the shelves and the soffit in image 1 are correct and final.

Turn the flat CAD surfaces into a photorealistic photograph of the finished pieces in place and change NOTHING about the
geometry: every edge of the bench, its legs, the drawer fronts, the brass pulls, the cushion, the shelves and the soffit
stays exactly where it is in image 1, at the same position and size. Do not make the bench taller, shorter, deeper or
narrower; do not move its legs; do not move or resize the shelves or the soffit. Keep the camera, the walls, the door, the
floor, the pilasters and their baseboards exactly as in the photo.

The bench is a freestanding piece of furniture, not built in: it stands on short square legs with open floor under it, so
the plank floor runs on under the bench between the legs, in soft shadow, and the white baseboard of the back wall
continues behind it. It stands clear of both side walls, with a narrow strip of wall showing at each end. Only the two
front legs show from this camera; the back legs are hidden behind the case.

Materials and finish:
- Each drawer front is a frame painted smooth satin white enamel (the same white as the door and the baseboards, no wood
  grain) around a flat panel painted the same satin white, recessed a little behind the frame, so a thin shadow runs
  along the top inside edge of the frame and fainter ones down the sides; the front reads as a white frame around a
  recessed white panel. One brushed brass bar pull centered on each panel, exactly where the brass bar is in image 1. A
  thin shadow gap between the two fronts, and a thin dark line under them where the case's underside begins.
- The case's end panels (the narrow painted face at each end of the bench, beside the fronts) are the same satin white.
- The top is solid hard maple, pale blond with fine grain, clear satin finish, gently eased edges; it overhangs the fronts
  and the ends a little, so its front edge and its two end edges show under the cushion as a thin pale wood band.
- The legs are solid hard maple like the top, square, straight, pale blond, clear satin finish, standing on the floor with
  a soft contact shadow; under the case, between the legs, the floor is in shadow, and a maple rail runs front to back
  at each end, mostly hidden behind the front leg.
- The cushion is one long boxed cushion in oatmeal linen with piped edges, slightly soft, covering the whole top.
- The three shelves are solid hard maple like the top, thick slabs floating on the back wall with no visible brackets.
  Lightly styled: a few books, a small plant, a basket, a small framed picture, all standing on the shelves without
  hiding their front edges. No words, no signs, no dog.
- The soffit across the top of the picture is painted drywall: its front face the same cream as the walls and pilasters,
  in one plane with the pilaster faces below it, with a crisp corner where it meets the room ceiling; its underside the
  same matte white as the room ceiling (not grey, not blue), with the two round recessed downlights switched on, slim
  white trim rings, warm light pooling down the back wall over the shelves and the bench, consistent with the daylight.
- Soft contact shadows under the top's overhang, under the cushion, under the shelves and under the bench on the floor.
  Same lighting, white balance, grain and lens as the photo. Photorealistic, no CAD look."""

STYLED_PROMPT = """Image 1 is a photograph of a finished freestanding bench in an alcove: all-white frame-and-panel drawer fronts with brass
bar pulls, a maple top on short maple legs with open floor under it, one long oatmeal linen cushion, three maple floating
shelves above and a dropped soffit with two downlights. Its geometry has been verified against the design and is final.
Image 2 is the client's reference picture of a similar alcove bench with a golden retriever and accessories. Images 3 and
4 are photos of the client's two dogs, who live in this house.

Edit image 1 to add the accessories from image 2 and the two dogs from images 3 and 4, and change nothing else. Do not
move, resize, redraw or restyle the bench, its legs, the drawer fronts, the brass pulls, the cushion, the maple top, the
shelves, the soffit, the lights, the walls, the door, the floor, the pilasters or the camera: every edge that is in image
1 stays exactly where it is, at the same size.

Add, placed naturally and at real-world scale:
- The two dogs on the cushion, each a faithful likeness of the dog in its photo (same breed look, coat colors, markings,
  head shape, ears), ignoring the people, the beach, the ball and any collars in the photos; neither dog wears a collar:
  Maizy (image 3), a small senior terrier mix, chocolate brown and white with a white blaze down her face, brown ears, a
  grey muzzle, a white chest and legs and a mostly white tail, short coat, lies curled up on the cushion left of center
  next to the striped pillow, relaxed, head turned toward the camera. Franco (image 4), a large black Labrador mix with a
  short glossy black coat and a broad head, no collar, lies on the cushion right of center, chest down, head up, facing
  the camera, relaxed. True relative size: Franco is a big dog, Maizy a small one, about half his length. Both rest
  entirely on the cushion and do not hang over its front edge. No golden retriever.
- Three throw pillows standing against the back wall like in image 2: a dark olive green velvet pillow and a cream and
  grey striped linen pillow at the left end, a rust brown pillow at the right end, the dogs between them.
- A cream and grey woven throw blanket with fringe, folded on the cushion at the left end with one corner hanging just
  over the cushion's front edge, not below the maple top's edge, so both drawer fronts stay fully visible.
- The shelves styled like image 2, replacing the few objects on them now: a trailing pothos in a white pot at the left
  end of the top shelf with vines hanging down, a lidded woven seagrass basket, a few hardcover books lying and standing,
  a small framed landscape picture, two cream ceramic jars, a small wooden bowl, a second small potted plant, a woven
  basket holding tennis balls on the bottom shelf, and a small white framed sign reading GOOD DOGS LIVE HERE leaning on
  the bottom shelf. Everything stands on the shelves and does not hide the shelf front edges.
- A natural jute rug on the floor in the foreground at the bottom of the frame, ending well in front of the bench so the
  legs and the open floor under the bench stay fully visible.
- No dog bowls, no tray, no other new objects.

Keep the lighting exactly as it is in image 1; the new items cast soft natural shadows consistent with it. No other
changes. Photorealistic, matching image 1's grain, lens and white balance."""

DOGS_PROMPT = """Image 1 is a photograph of a finished freestanding bench in an alcove with a dog lying on its cushion, pillows, a throw,
styled shelves above and a rug. Its geometry has been verified and is final. Images 2 and 3 are photos of the client's
two dogs, who live in this house.

Edit image 1 so the dog on the cushion is REPLACED by these two dogs, and change nothing else. Remove the dog that is there
completely. Do not move, resize, redraw or restyle the bench, its legs, the drawer fronts, the brass pulls, the cushion,
the maple top, the shelves and their objects, the pillows, the throw, the rug, the soffit, the walls, the door, the
floor, the pilasters or the camera: every edge that is in image 1 stays exactly where it is, at the same size.

The two dogs, each a faithful likeness of the dog in its photo (same breed look, coat colors, markings, head shape,
ears), ignoring the people, the beach, the ball and any collars in the photos; neither dog wears a collar here:
- Maizy (image 2): a small senior terrier mix, chocolate brown and white with a white blaze down her face, brown ears,
  a grey muzzle, a white chest and legs and a mostly white tail, short coat. She lies curled up on the cushion at the
  left of center, next to the striped pillow, relaxed, head resting on her paws or turned toward the camera.
- Franco (image 3): a large black Labrador mix with a short glossy black coat, a broad head, no collar. He lies on the
  cushion right of center, chest down, head up, facing the camera, relaxed.
- True relative size: Franco is a big dog, Maizy a small one, about half his length. Both rest entirely on the cushion
  and do not hang over its front edge; both fit between the pillows.

Keep the lighting exactly as it is in image 1; the dogs cast soft natural shadows on the cushion consistent with it.
No other new objects, no other changes. Photorealistic, matching image 1's grain, lens and white balance."""

SOFFIT_PAINT_PROMPT = """Image 1 is a photograph of a finished freestanding bench in an alcove with two dogs on its cushion, shelves above, and a
dropped soffit across the top of the picture, flush with the pilaster faces and running on over the hallway opening,
with two recessed downlights in its underside over the alcove. Two surfaces of that soffit are wrongly colored and must
be repainted; everything else is final.

- The soffit's UNDERSIDE (the lowered ceiling plane inside the alcove, with the two downlights, and its continuation
  over the hallway opening) is tinted pale blue-grey. Repaint it the same warm matte white as the room ceiling: plain
  painted ceiling drywall, slightly shadowed toward its back edge, with a warm glow around each downlight. No blue, no
  grey tint.
- The soffit's FRONT FACE (the flat band across the top of the picture, above the alcove, the pilasters and the hallway
  opening) looks like a flat painted-on rectangle. Make it read as real drywall painted the same cream as the walls and
  pilasters, in one plane with the pilaster faces below it, with the same subtle light falloff and surface texture and a
  crisp corner where it meets the room ceiling.

Keep both surfaces exactly where they are, at the same size, with the same edges. Keep the two downlights exactly where
they are, switched on. Do not change the bench, its legs, the dogs, the pillows, the throw, the shelves and their objects,
the sign, the rug, the walls, the door, the floor, the pilasters, the lighting or the camera. Photorealistic, matching
image 1's grain, lens and white balance."""

JOBS = {
    "guided": ((f"{PROJ}/images/alcove-overlay-{BASE}.png", "image/png"), GUIDED_PROMPT, "bench-in-nook-guided"),
    "styled": ((f"{PROJ}/images/bench-in-nook-guided.png", "image/png"),
               (f"{PROJ}/images/concept-ai-bench-web.jpg", "image/jpeg"), (f"{PROJ}/images/maizy.jpg", "image/jpeg"),
               (f"{PROJ}/images/franco.jpg", "image/jpeg"), STYLED_PROMPT, "bench-in-nook-styled"),
    "dogs": ((f"{PROJ}/images/bench-in-nook-styled.png", "image/png"), (f"{PROJ}/images/maizy.jpg", "image/jpeg"),
             (f"{PROJ}/images/franco.jpg", "image/jpeg"), DOGS_PROMPT, "bench-in-nook-dogs"),
    "soffit-paint": ((f"{PROJ}/images/bench-in-nook-styled.png", "image/png"), SOFFIT_PAINT_PROMPT,
                     "bench-in-nook-soffit-paint"),
}
job = sys.argv[1] if len(sys.argv) > 1 else "guided"
if job not in JOBS:
    sys.exit(f"unknown job {job!r}; use one of {list(JOBS)}")
variant = sys.argv[2] if len(sys.argv) > 2 else ""
*imgs, PROMPT, stem = JOBS[job]       # any number of (path, mime) inputs
OUT = f"{PROJ}/images/{stem}{('-' + variant) if variant else ''}.png"

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
parts = []
for path, mime in imgs:
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
