---
tags: [reference, git-history]
---

# FreeCAD repo git history

Full log of the local-only git repo at `~/ClaudeProjects/FreeCAD` (the setup project), preserved before that directory was deleted (migration 2026-07-30). Newest first.

```
commit e3069667b472dde931a2cae80117cf90091a09de
Author: brian <bblietz@gmail.com>
Date:   2026-07-30 17:56:15 -0700

    Add lego-rocket-mk3: round-body redesign of the 22-piece rocket kit
    
    Round Ø34 (R4) and Ø15.8 (R2) modules replace the Mk2 square bodies and
    octagonal approximations. 10 unique parts, 22 pieces, 3 colors, 125.6 mm
    assembled. Includes parametric build scripts, parts + assembly FCStd,
    per-part STLs, and a verified Bambu X2D kit project 3MF (22 arranged bed
    objects, 0.18 mm / 0.6 nozzle, red/white/gray filament mapping).
    
    Two documented geometry fixes over DESIGN.md: the Taper's clutch cavity
    keeps full Ø30.2 only over the stud zone then chamfers inward (a straight
    Ø30.2 x 8.4 cut would sever the cone skirt), and R2 modules/skirts gain
    four stud-relief notches at (+-4,+-4) so round parts can seat over 2x2
    stud groups (stud crescents reach r8.06, beyond the Ø13 cavity wall).
    
    Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

 models/lego-rocket-mk3/BUILD-INSTRUCTIONS.md       |  75 +++++++++++++++++++++
 models/lego-rocket-mk3/DESIGN.md                   |  47 +++++++++++++
 models/lego-rocket-mk3/bell.stl                    | Bin 0 -> 34184 bytes
 models/lego-rocket-mk3/body.stl                    | Bin 0 -> 195884 bytes
 models/lego-rocket-mk3/boosterbody.stl             | Bin 0 -> 71284 bytes
 models/lego-rocket-mk3/boostercone.stl             | Bin 0 -> 78184 bytes
 models/lego-rocket-mk3/lego-rocket-mk3.3mf         | Bin 0 -> 500774 bytes
 models/lego-rocket-mk3/lego_rocket_mk3.FCStd       | Bin 0 -> 166872 bytes
 .../lego-rocket-mk3/lego_rocket_mk3_assembly.FCStd | Bin 0 -> 231745 bytes
 models/lego-rocket-mk3/nose.stl                    | Bin 0 -> 87884 bytes
 models/lego-rocket-mk3/pad.stl                     | Bin 0 -> 405684 bytes
 models/lego-rocket-mk3/porthole.stl                | Bin 0 -> 215884 bytes
 models/lego-rocket-mk3/scripts/01_pad.py           |  43 ++++++++++++
 models/lego-rocket-mk3/scripts/02_bell.py          |  28 ++++++++
 models/lego-rocket-mk3/scripts/03_tail.py          |  54 +++++++++++++++
 models/lego-rocket-mk3/scripts/04_body.py          |  38 +++++++++++
 models/lego-rocket-mk3/scripts/05_porthole.py      |  42 ++++++++++++
 models/lego-rocket-mk3/scripts/06_taper.py         |  48 +++++++++++++
 models/lego-rocket-mk3/scripts/07_stage.py         |  47 +++++++++++++
 models/lego-rocket-mk3/scripts/08_nose.py          |  48 +++++++++++++
 models/lego-rocket-mk3/scripts/09_boosterbody.py   |  38 +++++++++++
 models/lego-rocket-mk3/scripts/10_boostercone.py   |  39 +++++++++++
 models/lego-rocket-mk3/scripts/11_assembly.py      |  64 ++++++++++++++++++
 models/lego-rocket-mk3/scripts/12_save_export.py   |  31 +++++++++
 models/lego-rocket-mk3/stage.stl                   | Bin 0 -> 71284 bytes
 models/lego-rocket-mk3/tail.stl                    | Bin 0 -> 198284 bytes
 models/lego-rocket-mk3/taper.stl                   | Bin 0 -> 208684 bytes
 27 files changed, 642 insertions(+)

commit 1be0c855272de0505a4ea4e13dd14832e150b31b
Author: brian <bblietz@gmail.com>
Date:   2026-07-30 13:11:58 -0700

    Add lego-rocket-mk2: 22-piece multi-stage rocket with launch pad and boosters
    
    Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

 models/lego-rocket-mk2/BUILD-INSTRUCTIONS.md       |  61 +++++++++++++++++++++
 models/lego-rocket-mk2/body-4x4.stl                | Bin 0 -> 190484 bytes
 models/lego-rocket-mk2/booster-body.stl            | Bin 0 -> 40084 bytes
 models/lego-rocket-mk2/booster-cone.stl            | Bin 0 -> 66784 bytes
 models/lego-rocket-mk2/engine-bell.stl             | Bin 0 -> 34184 bytes
 models/lego-rocket-mk2/instructions/assembled.png  | Bin 0 -> 37838 bytes
 .../lego-rocket-mk2/instructions/kit-contents.png  | Bin 0 -> 17550 bytes
 models/lego-rocket-mk2/instructions/step-1.png     | Bin 0 -> 29872 bytes
 models/lego-rocket-mk2/instructions/step-2.png     | Bin 0 -> 30857 bytes
 models/lego-rocket-mk2/instructions/step-3.png     | Bin 0 -> 24106 bytes
 models/lego-rocket-mk2/instructions/step-4.png     | Bin 0 -> 27619 bytes
 models/lego-rocket-mk2/instructions/step-5.png     | Bin 0 -> 24699 bytes
 models/lego-rocket-mk2/instructions/step-6.png     | Bin 0 -> 25543 bytes
 models/lego-rocket-mk2/instructions/step-7.png     | Bin 0 -> 28808 bytes
 models/lego-rocket-mk2/instructions/step-8.png     | Bin 0 -> 37838 bytes
 models/lego-rocket-mk2/launch-pad.stl              | Bin 0 -> 434484 bytes
 models/lego-rocket-mk2/lego-rocket-mk2.3mf         | Bin 0 -> 414663 bytes
 models/lego-rocket-mk2/lego-rocket-mk2.FCStd       | Bin 0 -> 65876 bytes
 models/lego-rocket-mk2/nose-cone.stl               | Bin 0 -> 76484 bytes
 models/lego-rocket-mk2/oct-body.stl                | Bin 0 -> 40084 bytes
 models/lego-rocket-mk2/porthole-brick.stl          | Bin 0 -> 207684 bytes
 models/lego-rocket-mk2/result.json                 |  10 ++++
 models/lego-rocket-mk2/tail-section.stl            | Bin 0 -> 194484 bytes
 models/lego-rocket-mk2/taper-adapter.stl           | Bin 0 -> 159284 bytes
 24 files changed, 71 insertions(+)

commit fb204e7c4abe2eb99a735cb93293ffd845b48caa
Author: brian <bblietz@gmail.com>
Date:   2026-07-30 12:55:28 -0700

    Add lego-rocket kit: 5-piece Lego-compatible rocket with build instructions
    
    Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

 models/lego-rocket/BUILD-INSTRUCTIONS.md         |  48 +++++++++++++++++++++++
 models/lego-rocket/body-brick.stl                | Bin 0 -> 38484 bytes
 models/lego-rocket/fin-base.stl                  | Bin 0 -> 40884 bytes
 models/lego-rocket/instructions/assembled.png    | Bin 0 -> 5022 bytes
 models/lego-rocket/instructions/kit-contents.png | Bin 0 -> 15522 bytes
 models/lego-rocket/instructions/step-1.png       | Bin 0 -> 5041 bytes
 models/lego-rocket/instructions/step-2.png       | Bin 0 -> 13101 bytes
 models/lego-rocket/instructions/step-3.png       | Bin 0 -> 12633 bytes
 models/lego-rocket/instructions/step-4.png       | Bin 0 -> 12839 bytes
 models/lego-rocket/instructions/step-5.png       | Bin 0 -> 19674 bytes
 models/lego-rocket/lego-rocket.3mf               | Bin 0 -> 53481 bytes
 models/lego-rocket/lego-rocket.FCStd             | Bin 0 -> 20113 bytes
 models/lego-rocket/nose-cone.stl                 | Bin 0 -> 55684 bytes
 models/lego-rocket/result.json                   |  10 +++++
 14 files changed, 58 insertions(+)

commit b3e7ab0407939301fd2772b0020f4673a8b38247
Author: brian <bblietz@gmail.com>
Date:   2026-07-28 22:38:11 -0700

    Rework kelkom button legs: corner-mounted arc-section snap legs
    
    Legs moved to diagonally opposite corners per measurement of the
    original part: 6mm chord, 1.3mm wall, R6 outer / R4.7 inner arc,
    barbs revolved along the outer face.
    
    Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

 .../kelkom-intercom-button.3mf                      | Bin 5454 -> 7826 bytes
 .../kelkom-intercom-button.FCStd                    | Bin 14932 -> 21516 bytes
 .../kelkom-intercom-button.stl                      | Bin 13684 -> 26084 bytes
 3 files changed, 0 insertions(+), 0 deletions(-)

commit 403cada40e0d4342f760738345d120bfc0cc50c9
Author: brian <bblietz@gmail.com>
Date:   2026-07-28 22:32:00 -0700

    Add kelkom-intercom-button snap-fit button model
    
    Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

 .../kelkom-intercom-button/kelkom-intercom-button.3mf  | Bin 0 -> 5454 bytes
 .../kelkom-intercom-button.FCStd                       | Bin 0 -> 14932 bytes
 .../kelkom-intercom-button/kelkom-intercom-button.stl  | Bin 0 -> 13684 bytes
 models/kelkom-intercom-button/reference/bottom.jpg     | Bin 0 -> 147671 bytes
 models/kelkom-intercom-button/reference/side.jpg       | Bin 0 -> 93686 bytes
 models/kelkom-intercom-button/reference/side2.jpg      | Bin 0 -> 103055 bytes
 models/kelkom-intercom-button/reference/top.jpg        | Bin 0 -> 80371 bytes
 7 files changed, 0 insertions(+), 0 deletions(-)

commit 9a164fc665e238284a30147aaaa567db40897c50
Author: brian <bblietz@gmail.com>
Date:   2026-07-27 20:55:22 -0700

    feat: resize Clawd to 2 3/4 x 1 15/16 x 1 inch
    
    Rebuild the parametric model at 69.85 x 49.2125 x 25.4mm. The requested
    aspect differs from the sprite's 8:5 grid, so cells become 8.73mm wide x
    9.84mm tall (per-axis scale) instead of square. Features preserved:
    1/32" roundovers on exposed edges, 3-degree limb tapers, 3mm eye
    sockets with eyes 1mm proud (body 24.4mm + eyes = 25.4mm total), leg and
    eye widths scaled with cell width. Re-exported fine-mesh STLs and the
    Bambu project 3MF (X2D 0.6 nozzle, 0.18mm Balanced Quality, orange/black
    filaments), round-trip verified.
    
    Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

 models/anthropic-mascot/anthropic-mascot-body.stl | Bin 452684 -> 452684 bytes
 models/anthropic-mascot/anthropic-mascot-eyes.stl | Bin 11684 -> 11684 bytes
 models/anthropic-mascot/anthropic-mascot.3mf      | Bin 103888 -> 108008 bytes
 models/anthropic-mascot/anthropic-mascot.FCStd    | Bin 76282 -> 79124 bytes
 models/anthropic-mascot/anthropic-mascot.stl      | Bin 464284 -> 464284 bytes
 5 files changed, 0 insertions(+), 0 deletions(-)

commit 6d59ff88397cb0a576b3677fcba99921c46b5e25
Author: brian <bblietz@gmail.com>
Date:   2026-07-27 20:44:37 -0700

    feat: 0.6mm high-flow nozzle project 3MF at 0.18mm Balanced Quality
    
    Regenerate anthropic-mascot.3mf for the installed 0.6mm high-flow nozzle:
    X2D 0.6 machine preset, 0.18mm Balanced Quality process (finest for 0.6),
    PLA Basic X2D filaments. The CLI can't resolve preset 'inherits' chains
    for X2D profiles (bundled profiles predate the printer) and silently
    falls back to base values, so presets are flattened to self-contained
    JSONs first; documented in the skill. CLAUDE.md and the printability
    table now reflect the 0.6mm nozzle (min wall ~1.24mm).
    
    Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

 CLAUDE.md                                    |   3 ++-
 models/anthropic-mascot/anthropic-mascot.3mf | Bin 101555 -> 103888 bytes
 skills/3d-model/SKILL.md                     |  28 +++++++++++++++++++--------
 3 files changed, 22 insertions(+), 9 deletions(-)

commit 05bc60267cb6c4249d727dc1c90830b7306845d7
Author: brian <bblietz@gmail.com>
Date:   2026-07-26 21:50:33 -0700

    fix: ship Bambu Studio project 3MF — generic basematerials open all-green
    
    Bambu Studio ignores object-level basematerials in standard 3MFs (its
    color import only parses vertex/face colors). Rebuild anthropic-mascot.3mf
    as a project 3MF via the bambu-studio CLI (--assemble, per-part filament
    ids), patch filament_colour to #CC785C/#141414, and verify by round-trip.
    Update the /3d-model skill to make this the multi-color procedure.
    
    Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

 models/anthropic-mascot/anthropic-mascot.3mf   | Bin 93205 -> 101555 bytes
 models/anthropic-mascot/anthropic-mascot.FCStd | Bin 76282 -> 76282 bytes
 skills/3d-model/SKILL.md                       |  51 ++++++++++++++++---------
 3 files changed, 32 insertions(+), 19 deletions(-)

commit 7533f2cd071ac2246f8f2cbd8d4b05210370d6f8
Author: brian <bblietz@gmail.com>
Date:   2026-07-26 14:46:44 -0700

    docs: AMS 2 Pro color capacity in CLAUDE.md printer constraints
    
    Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

 CLAUDE.md | 5 ++++-
 1 file changed, 4 insertions(+), 1 deletion(-)

commit 5a2260cca195d9af7bd29ce17a6f3bd8e5931832
Author: brian <bblietz@gmail.com>
Date:   2026-07-26 14:45:46 -0700

    docs: AMS 2 Pro color capacity in /3d-model skill
    
    Main nozzle + AMS 2 Pro = max 4 colors; 2nd nozzle is for support
    material, usable as a lower-accuracy 5th color only when precision
    doesn't matter.
    
    Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

 skills/3d-model/SKILL.md | 6 ++++++
 1 file changed, 6 insertions(+)

commit 6ca814bf1c6fffef7ab9b5e62568441c390160b8
Author: brian <bblietz@gmail.com>
Date:   2026-07-26 14:43:14 -0700

    docs: mandatory 3MF color-injection step in /3d-model skill
    
    FreeCAD's Mesh 3MF writer drops all material data; document the
    basematerials post-processing step so multi-color exports never ship
    colorless again.
    
    Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

 skills/3d-model/SKILL.md | 21 +++++++++++++++++++++
 1 file changed, 21 insertions(+)

commit f780ae224fe36c657875e1b2f32dd0c2a0734345
Author: brian <bblietz@gmail.com>
Date:   2026-07-26 14:42:14 -0700

    fix: embed orange/black materials in the 3MF export
    
    FreeCAD's Mesh 3MF writer emits no material data, so slicers painted
    all three objects in their default filament color. Inject standard 3MF
    basematerials (#CC785C body, #141414 eyes) with per-object pid/pindex.
    
    Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

 models/anthropic-mascot/anthropic-mascot.3mf | Bin 93080 -> 93205 bytes
 1 file changed, 0 insertions(+), 0 deletions(-)

commit 58405b2a749eca59842f6492b9bda2abf8528b9d
Author: brian <bblietz@gmail.com>
Date:   2026-07-26 14:37:19 -0700

    feat: eyes raised 1mm proud of the face
    
    Eye solids extended from 3mm to 4mm tall: 3mm socket engagement
    unchanged (z19-22), top 1mm protrudes above the face (z22-23). Exposed
    top rims get the 1/32in roundover; vertical sides stay square for the
    exact socket fit. Body untouched.
    
    Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

 models/anthropic-mascot/anthropic-mascot-eyes.stl | Bin 1284 -> 11684 bytes
 models/anthropic-mascot/anthropic-mascot.3mf      | Bin 90543 -> 93080 bytes
 models/anthropic-mascot/anthropic-mascot.FCStd    | Bin 65466 -> 76282 bytes
 models/anthropic-mascot/anthropic-mascot.stl      | Bin 453884 -> 464284 bytes
 4 files changed, 0 insertions(+), 0 deletions(-)

commit ec14ba49b5de229725511d4321d899158f4b4bc6
Author: brian <bblietz@gmail.com>
Date:   2026-07-26 14:33:49 -0700

    feat: 3-degree taper on arm tops/bottoms and leg sides
    
    Arms narrow toward the tips and legs narrow toward the feet (~0.59mm
    per face over the 11.25mm limb length), built as trapezoidal prisms
    replacing the square boxes. Feature tree rebuilt, 1/32in roundover
    re-applied with eye sockets kept square, meshes re-exported.
    
    Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

 models/anthropic-mascot/anthropic-mascot-body.stl | Bin 452684 -> 452684 bytes
 models/anthropic-mascot/anthropic-mascot.3mf      | Bin 90184 -> 90543 bytes
 models/anthropic-mascot/anthropic-mascot.FCStd    | Bin 67092 -> 65466 bytes
 models/anthropic-mascot/anthropic-mascot.stl      | Bin 453884 -> 453884 bytes
 4 files changed, 0 insertions(+), 0 deletions(-)

commit d5cf1336fc11b51f5ae6f3a5ef78309f60e018bc
Author: brian <bblietz@gmail.com>
Date:   2026-07-26 14:30:33 -0700

    feat: 1/32in roundover on all exposed edges of anthropic-mascot
    
    Part::Fillet at 0.79375mm on 84 of 108 body edges; the eye-socket
    edges and eye solids stay square so the flush two-color inlay fit is
    preserved. Meshes re-exported at 0.05mm deflection so the small rounds
    stay smooth.
    
    Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

 models/anthropic-mascot/anthropic-mascot-body.stl | Bin 7084 -> 452684 bytes
 models/anthropic-mascot/anthropic-mascot.3mf      | Bin 5247 -> 90184 bytes
 models/anthropic-mascot/anthropic-mascot.FCStd    | Bin 33389 -> 67092 bytes
 models/anthropic-mascot/anthropic-mascot.stl      | Bin 8284 -> 453884 bytes
 4 files changed, 0 insertions(+), 0 deletions(-)

commit 79e4b73178253a4df92739e6d5df6995e56afb81
Author: brian <bblietz@gmail.com>
Date:   2026-07-26 14:28:36 -0700

    fix: rebuild anthropic-mascot as Clawd pixel crab from reference sprite
    
    Replaces the rejected logo-starburst geometry. Voxel model derived from
    the official sprite (8x5 cell grid measured pixel-exact from Brian's
    reference image): 90x56.25x22mm, terracotta body with nub arms and four
    legs, 3mm-deep eye sockets with separate black eye solids for two-color
    X2D printing. Reference image in reference/clawd-sprite.jpg.
    
    Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

 models/anthropic-mascot/anthropic-mascot-body.stl  | Bin 1572384 -> 7084 bytes
 models/anthropic-mascot/anthropic-mascot-eyes.stl  | Bin 417484 -> 1284 bytes
 models/anthropic-mascot/anthropic-mascot.3mf       | Bin 454181 -> 5247 bytes
 models/anthropic-mascot/anthropic-mascot.FCStd     | Bin 432057 -> 33389 bytes
 models/anthropic-mascot/anthropic-mascot.stl       | Bin 1989784 -> 8284 bytes
 models/anthropic-mascot/reference/clawd-sprite.jpg | Bin 0 -> 6437 bytes
 6 files changed, 0 insertions(+), 0 deletions(-)

commit 877a673d735995da12558c7133e3153d4673c11f
Author: brian <bblietz@gmail.com>
Date:   2026-07-26 14:16:24 -0700

    feat: anthropic-mascot model — orange starburst plushie with black eyes
    
    90mm two-color desk figure for the Bambu Lab X2D: flat-back domed
    starburst (12 rays) with separate eye solids in matching sockets for
    dual-nozzle printing. Exports: FCStd, combined STL/3MF, plus split
    body/eyes STLs for filament assignment in Bambu Studio.
    
    Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

 models/anthropic-mascot/anthropic-mascot-body.stl | Bin 0 -> 1572384 bytes
 models/anthropic-mascot/anthropic-mascot-eyes.stl | Bin 0 -> 417484 bytes
 models/anthropic-mascot/anthropic-mascot.3mf      | Bin 0 -> 454181 bytes
 models/anthropic-mascot/anthropic-mascot.FCStd    | Bin 0 -> 432057 bytes
 models/anthropic-mascot/anthropic-mascot.stl      | Bin 0 -> 1989784 bytes
 5 files changed, 0 insertions(+), 0 deletions(-)

commit 49b435183180bfc2b8736d0b2b8e946e6ccfd47d
Author: brian <bblietz@gmail.com>
Date:   2026-07-26 14:08:04 -0700

    fix: harden launcher and smoke test against failure paths
    
    - start-freecad-mcp.sh: fail fast with a clear error if the AppImage is
      missing/non-executable, instead of burning ~2 minutes of nohup+poll
      before blaming auto_start_rpc.
    - smoke-test.py: pre-close any stale SmokeTest doc from a prior failed
      run, and wrap the test body in try/finally so a mid-run failure can't
      leak an open document into the next run.
    - CLAUDE.md: note the three version-pinned spots to update on a FreeCAD
      upgrade.
    
    Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

 CLAUDE.md                    |   4 ++
 scripts/smoke-test.py        | 103 ++++++++++++++++++++++++++-----------------
 scripts/start-freecad-mcp.sh |   5 +++
 3 files changed, 71 insertions(+), 41 deletions(-)

commit 00d6556ebfbfa316fa1d7607e131b89474be7fe8
Author: brian <bblietz@gmail.com>
Date:   2026-07-26 13:57:17 -0700

    docs: project CLAUDE.md quick reference
    
    Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

 CLAUDE.md | 25 +++++++++++++++++++++++++
 1 file changed, 25 insertions(+)

commit 28a0b980f5a1099c68091a810af092146eceaaa7
Author: brian <bblietz@gmail.com>
Date:   2026-07-26 13:53:45 -0700

    feat: /3d-model skill encoding the modeling workflow
    
    Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

 skills/3d-model/SKILL.md | 119 +++++++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 119 insertions(+)

commit f5d693abb79b5f2062850f380bcf7badba5ccaf6
Author: brian <bblietz@gmail.com>
Date:   2026-07-26 13:48:12 -0700

    feat: end-to-end smoke test for FreeCAD MCP system
    
    Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

 scripts/smoke-test.py | 88 +++++++++++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 88 insertions(+)

commit c497579c31bb8e9032254baec33e7255f6358618
Author: brian <bblietz@gmail.com>
Date:   2026-07-26 13:42:38 -0700

    feat: FreeCAD launcher with RPC readiness wait
    
    Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

 scripts/start-freecad-mcp.sh | 44 ++++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 44 insertions(+)

commit e991b5da894ba875846869aa612bf630939fcdbc
Author: brian <bblietz@gmail.com>
Date:   2026-07-26 13:34:53 -0700

    chore: project scaffolding for 3D model system
    
    Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

 .gitignore       | 15 +++++++++++++++
 models/.gitkeep  |  0
 scripts/.gitkeep |  0
 skills/.gitkeep  |  0
 4 files changed, 15 insertions(+)

commit 02935891bc2faf807bfa1db15d1ae590278d4a5e
Author: brian <bblietz@gmail.com>
Date:   2026-07-26 13:31:08 -0700

    docs: implementation plan for FreeCAD 3D model system
    
    Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

 .../plans/2026-07-26-freecad-3d-model-system.md    | 632 +++++++++++++++++++++
 1 file changed, 632 insertions(+)

commit a76c0fbd4b836efe3ddc78c4a116011f4dc8a0af
Author: brian <bblietz@gmail.com>
Date:   2026-07-26 13:25:40 -0700

    Confirm X2D build volume against official spec sheet; note nozzle range
    
    Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

 docs/superpowers/specs/2026-07-26-freecad-3d-model-system-design.md | 1 +
 1 file changed, 1 insertion(+)

commit 93431efee8c538465406da4d0711b091bc5e6ebc
Author: brian <bblietz@gmail.com>
Date:   2026-07-26 13:19:24 -0700

    Add design spec for FreeCAD 3D model generation system
    
    Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

 .../2026-07-26-freecad-3d-model-system-design.md   | 99 ++++++++++++++++++++++
 1 file changed, 99 insertions(+)
```
