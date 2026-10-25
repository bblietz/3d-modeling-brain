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
  guided   images/alcove-overlay.png (photo_match.py: the CAD bench and shelves projected into the alcove photo
           through a camera matched to it, at true scale) -> images/bench-in-nook-guided.png; Gemini only makes the
           flat CAD surfaces photoreal and may not move an edge. Verify with photo_match.py check <output>.
  styled   images/bench-in-nook-guided.png (the verified picture) + images/concept-ai-bench-web.jpg (the client's
           reference) -> images/bench-in-nook-styled.png; the dog, pillows, throw, shelf objects, dog bowls and rug
           from the reference added, nothing else changed. Verify with photo_match.py check <output> again.
  dogs     images/bench-in-nook-styled.png + images/maizy.jpg + images/franco.jpg (the client's dogs)
           -> images/bench-in-nook-dogs.png; the golden retriever replaced by Maizy and Franco, nothing else changed.
           Verify with photo_match.py check <output> again.
  soffit   images/bench-in-nook-dogs-soffit-overlay.png (photo_match.py soffit: the dropped soffit and its two
           downlights z-buffered onto the dogs picture at true scale) -> images/bench-in-nook-soffit.png; Gemini only
           makes the flat soffit photoreal and lights the lamps. Verify with photo_match.py check <output> again.
  soffit-paint  images/bench-in-nook-soffit.png -> images/bench-in-nook-soffit-paint.png; Gemini kept the overlay's
           grey underside as a blue-grey ceiling three times, so this pass repaints the soffit as drywall (underside
           ceiling white, face wall cream) and changes nothing else. Verify with photo_match.py check <output> again.
  walnut-shelves  images/bench-in-nook-soffit-paint.png -> images/bench-in-nook-walnut-shelves.png; the three shelves
           changed from maple to walnut matching the drawer panels (Brian 2026-10-24), nothing else changed. The earlier
           stages were run with maple shelves; the overlay (photo_match.py) and the guided/styled/soffit prompts now say
           walnut, so a rerun from guided gets walnut shelves without this pass. Verify with photo_match.py check <output>.

Usage: ~/.claude/skills/nanobanana/.venv/bin/python projects/Built-in-bench/render_in_room.py [bench|shelves|white|white-maple|white-all|white-inset|guided|styled|dogs|soffit|soffit-paint|walnut-shelves] [variant]
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

GUIDED_PROMPT = """Image 1 is a photograph of an empty alcove (a former wet bar) into which a built-in bench and three floating shelves
have been placed by CAD, flat-shaded, at their exact built size and position. The perspective, the size, the height and
every edge of the bench and the shelves in image 1 are correct and final.

Turn the flat CAD surfaces into a photorealistic photograph of the finished, installed piece and change NOTHING about
the geometry: every edge of the bench, the drawer fronts, the brass pulls, the cushion and the shelves stays exactly
where it is in image 1, at the same position and size. Do not make the bench taller, shorter, deeper or narrower. Do
not move or resize the shelves. Keep the camera, the walls, the door, the floor, the pilasters and their baseboards
exactly as in the photo.

Materials and finish:
- The drawer frames (the pale border around each drawer front), the plinth strip at the floor and the narrow strips at
  the walls are painted smooth satin white enamel, the same white as the door and the baseboards, no wood grain.
- Inside each white frame is a flat walnut veneer panel, dark chocolate brown with visible straight grain, recessed
  1/4 inch behind the white frame, so a thin shadow runs along the top inside edge of the frame. One 8 inch brushed
  brass bar pull centered on each panel, exactly where the brass bar is in image 1.
- A thin 1/8 inch shadow gap between the two drawer fronts and around them.
- The top is solid hard maple, pale blond with fine grain, clear satin finish, gently eased front edge; only its 3/4
  inch front edge shows under the cushion.
- The cushion is one long boxed cushion in oatmeal linen with piped edges, slightly soft, covering the whole top.
- The three shelves are solid walnut like the drawer panels, dark chocolate brown with visible straight grain, clear
  satin finish, 1-1/2 inch thick slabs floating on the back wall with no visible brackets. Lightly styled: a few books, a small plant, a basket, a small framed picture, all standing on the
  shelves without hiding their front edges. No words, no signs, no lights, no dog.
- Soft contact shadows under the top's overhang, under the cushion and under the shelves; a faint reflection of the
  white plinth in the glossy floor. Same lighting, white balance, grain and lens as the photo. Photorealistic, no CAD
  look."""

STYLED_PROMPT = """Image 1 is a photograph of a finished built-in bench in an alcove: white painted drawer frames around dark walnut
panels with brass bar pulls, a maple top, one long oatmeal linen cushion, and three walnut floating shelves above. Its
geometry has been verified against the design and is final. Image 2 is the client's reference picture of a similar
alcove bench with a golden retriever and accessories.

Edit image 1 to add the dog and the accessories from image 2, and change nothing else. Do not move, resize, redraw or
restyle the bench, the drawer fronts, the brass pulls, the cushion, the maple top, the shelves, the walls, the door, the
floor, the pilasters or the camera: every edge that is in image 1 stays exactly where it is, at the same size.

Add, placed naturally and at real-world scale (the bench is 66 inches wide, the cushion top is 17 inches above the floor):
- The golden retriever from image 2, an older dog, lying on the cushion a little right of center, facing the camera,
  relaxed with its head up, like in image 2. The dog rests entirely on the cushion and does not hang over its front edge.
- Three throw pillows standing against the back wall like in image 2: a dark olive green velvet pillow and a cream and
  grey striped linen pillow at the left end, a rust brown pillow at the right end, the dog between them.
- A cream and grey woven throw blanket with fringe, folded on the cushion at the left end with one corner hanging just
  over the cushion's front edge, not below the maple top's edge, so both drawer fronts stay fully visible.
- The shelves styled like image 2, replacing the few objects on them now: a trailing pothos in a white pot at the left
  end of the top shelf with vines hanging down, a lidded woven seagrass basket, a few hardcover books lying and standing,
  a small framed landscape picture, two cream ceramic jars, a small wooden bowl, a second small potted plant, a woven
  basket holding tennis balls on the bottom shelf, and a small white framed sign reading GOOD DOGS LIVE HERE leaning on
  the bottom shelf. Everything stands on the shelves and does not hide the shelf front edges.
- Two stainless steel dog bowls in a small wooden tray on the floor just outside the alcove, to the right of the right
  pilaster, in the passage.
- A natural jute rug on the floor in the foreground at the bottom of the frame, ending well in front of the bench so the
  white plinth and the floor line under the bench stay fully visible.

Keep the lighting exactly as it is in image 1; the new items cast soft natural shadows consistent with it. No recessed
lights, no other new objects, no other changes. Photorealistic, matching image 1's grain, lens and white balance."""

DOGS_PROMPT = """Image 1 is a photograph of a finished built-in bench in an alcove with a golden retriever lying on its cushion, pillows,
a throw, styled shelves above, dog bowls on the floor and a rug. Its geometry has been verified and is final. Images 2
and 3 are photos of the client's two dogs, who live in this house.

Edit image 1 so the golden retriever is REPLACED by these two dogs, and change nothing else. Remove the golden retriever
completely. Do not move, resize, redraw or restyle the bench, the drawer fronts, the brass pulls, the cushion, the maple
top, the shelves and their objects, the pillows, the throw, the dog bowls, the rug, the walls, the door, the floor, the
pilasters or the camera: every edge that is in image 1 stays exactly where it is, at the same size.

The two dogs, each a faithful likeness of the dog in its photo (same breed look, coat colors, markings, head shape,
ears, collar), ignoring the people, the beach and the ball in the photos:
- Maizy (image 2): a small senior terrier mix, chocolate brown and white with a white blaze down her face, brown ears,
  a grey muzzle, a white chest and legs and a mostly white tail, short coat. She lies curled up on the cushion at the
  left of center, next to the striped pillow, relaxed, head resting on her paws or turned toward the camera.
- Franco (image 3): a large black Labrador mix with a short glossy black coat, a broad head, a leather collar with a
  tag. He lies on the cushion right of center where the retriever was, chest down, head up, facing the camera, relaxed.
- True relative size: Franco is a big dog, Maizy a small one, about half his length. Both rest entirely on the cushion
  and do not hang over its front edge; both fit between the pillows on the 66 inch bench.

Keep the lighting exactly as it is in image 1; the dogs cast soft natural shadows on the cushion consistent with it.
No other new objects, no other changes. Photorealistic, matching image 1's grain, lens and white balance."""

SOFFIT_PROMPT = """Image 1 is a photograph of a finished built-in bench in an alcove with two dogs on its cushion, pillows, a throw, three
walnut floating shelves with objects, dog bowls on the floor and a rug. Across the top of the picture a DROPPED SOFFIT has
been placed by CAD, flat-shaded, at its exact built size and position: a bulkhead hung from the ceiling whose front face
is flush with the faces of the two pilasters, in the same plane as them. It is one continuous band from the outer edge
of the left pilaster across the alcove, across the top of the right pilaster and on to the right over the hallway
opening, out past the edge of the picture; both pilasters now stop at its underside, like posts under a lintel. Its
underside runs back to the alcove's back wall; over the hallway opening it is the same depth, and beyond its back edge
the room ceiling stays at its full height. To the left of the left pilaster, the recess with the door keeps its
full-height ceiling. In its underside over the alcove are two round recessed LED downlights, where the two pale discs
are. Every edge of the soffit and the position of each light are correct and final.

Turn the flat CAD surfaces into a photorealistic part of the photograph and change NOTHING else. The CAD surfaces' flat
colors are unpainted PLACEHOLDERS, not colors to keep: in the finished photograph the soffit is drywall, its front face
painted the same cream as the walls and pilasters and continuous with the pilaster faces below it (one flat plane, at
most a faint paint line where a pilaster meets it), and its underside painted the same matte white as the room ceiling
(not grey, not blue), ordinary painted ceiling drywall with a crisp corner where its top meets the room ceiling, a soft
shadow line along the underside's front edge, and the soft shadow it casts onto the alcove's back wall and side walls
and onto the wall beyond the hallway opening. The two downlights are flush recessed fixtures with slim white trim rings,
switched on: warm white light pooling down the back wall over the shelves and the bench, soft highlights on the objects
on the top shelf and on the dogs, consistent with the photo's daylight and not overpowering it. Do not move, resize or
redraw the soffit, the lights, the bench, the dogs, the pillows, the throw, the shelves and their objects, the sign, the
bowls, the rug, the walls, the door, the floor, the pilasters or the camera: every edge that is in image 1 stays exactly
where it is, at the same size. Photorealistic, no CAD look, matching image 1's grain, lens and white balance."""

SOFFIT_PAINT_PROMPT = """Image 1 is a photograph of a finished built-in bench in an alcove with two dogs on its cushion, shelves above, and a
dropped soffit across the top of the picture, flush with the pilaster faces and running on over the hallway opening,
with two recessed downlights in its underside over the alcove. Two surfaces of that soffit are wrongly colored and must
be repainted; everything else is final.

- The soffit's UNDERSIDE (the lowered ceiling plane inside the alcove, with the two downlights, and its continuation
  over the hallway opening) is tinted pale blue-grey. Repaint it the same warm matte white as the room ceiling: plain
  painted ceiling drywall, slightly shadowed toward its back edge, with a warm glow around each downlight. No blue, no
  grey tint.
- The soffit's FRONT FACE (the flat beige band across the top of the picture, above the alcove, the pilasters and the
  hallway opening) looks like a flat painted-on rectangle. Make it read as real drywall painted the same cream as the
  walls and pilasters, in one plane with the pilaster faces below it, with the same subtle light falloff and surface
  texture and a crisp corner where it meets the room ceiling.

Keep both surfaces exactly where they are, at the same size, with the same edges. Keep the two downlights exactly where
they are, switched on. Do not change the bench, the dogs, the pillows, the throw, the shelves and their objects, the
sign, the bowls, the rug, the walls, the door, the floor, the pilasters, the lighting or the camera. Photorealistic,
matching image 1's grain, lens and white balance."""

WALNUT_SHELVES_PROMPT = """Image 1 is a photograph of a finished built-in bench in an alcove: white painted drawer frames around dark walnut
panels with brass bar pulls, a maple top, a cushion with two dogs on it, pillows, a throw, three pale maple floating
shelves above with objects on them, a dropped soffit with two downlights, dog bowls on the floor and a rug. Everything
in it is final except the wood of the three shelves.

Change the three floating shelves from pale maple to solid WALNUT, the same wood as the drawer panels below them: the
same dark chocolate brown, the same straight grain, the same clear satin finish, not reddish like the floor. Every
visible face of each shelf changes: the top face, the front edge and the underside. Each shelf stays exactly where it
is, at the same size and thickness, with the same edges and the same shadows under it; the warm light from the
downlights still falls on the top shelf.

Change nothing else. Every object on the shelves (the trailing pothos, the books, the baskets, the framed picture, the
jars, the wooden bowl, the plant, the sign reading GOOD DOGS LIVE HERE) stays exactly where it is, unchanged. The bench
top stays pale maple. Do not change the bench, the drawer fronts, the brass pulls, the cushion, the dogs, the pillows,
the throw, the soffit, the lights, the bowls, the rug, the walls, the door, the floor, the pilasters, the lighting or
the camera. Photorealistic, matching image 1's grain, lens and white balance."""

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
    "guided": ((f"{PROJ}/images/alcove-overlay.png", "image/png"), None, GUIDED_PROMPT, "bench-in-nook-guided"),
    "styled": ((f"{PROJ}/images/bench-in-nook-guided.png", "image/png"),
               (f"{PROJ}/images/concept-ai-bench-web.jpg", "image/jpeg"), STYLED_PROMPT, "bench-in-nook-styled"),
    "dogs": ((f"{PROJ}/images/bench-in-nook-styled.png", "image/png"), (f"{PROJ}/images/maizy.jpg", "image/jpeg"),
             (f"{PROJ}/images/franco.jpg", "image/jpeg"), DOGS_PROMPT, "bench-in-nook-dogs"),
    "soffit": ((f"{PROJ}/images/bench-in-nook-dogs-soffit-overlay.png", "image/png"), SOFFIT_PROMPT,
               "bench-in-nook-soffit"),
    "soffit-paint": ((f"{PROJ}/images/bench-in-nook-soffit.png", "image/png"), SOFFIT_PAINT_PROMPT,
                     "bench-in-nook-soffit-paint"),
    "walnut-shelves": ((f"{PROJ}/images/bench-in-nook-soffit-paint.png", "image/png"), WALNUT_SHELVES_PROMPT,
                       "bench-in-nook-walnut-shelves"),
}
job = sys.argv[1] if len(sys.argv) > 1 else "bench"
if job not in JOBS:
    sys.exit(f"unknown job {job!r}; use one of {list(JOBS)}")
variant = sys.argv[2] if len(sys.argv) > 2 else ""
*imgs, PROMPT, stem = JOBS[job]       # any number of (path, mime) inputs, None entries skipped
OUT = f"{PROJ}/images/{stem}{('-' + variant) if variant else ''}.png"

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
parts = []
for path, mime in [i for i in imgs if i]:
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
