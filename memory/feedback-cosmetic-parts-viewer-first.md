---
name: feedback-cosmetic-parts-viewer-first
description: On parts Brian will look at (cases, bezels, guards): push to the 3D viewer early, fit features to what the eye reads, offer guideline tradeoffs in one line before building the compliant-but-ugly version, and ask follow-ups in plain text
metadata:
  type: feedback
---

On cosmetic or hand-held parts, get the model into the OCP viewer as early as possible and size visible features to the feature the eye reads, not to a drawing's outer keepout boundary. When a vendor guideline (for example Apple's camera keepout cones) would force a visibly odd shape, say the tradeoff in one line and let Brian choose BEFORE building the compliant version. When he reports something wrong in the viewer, screenshot and look first, then ask in plain text, not with a multiple-choice dialog.

**Why:** On the [[project-iphone-case]] (2026-09-20) the camera guard took three versions, each corrected within minutes of Brian seeing the viewer: "the guard around it is too big. It should be snug around the camera" (I had sized it to Apple's plateau outer boundary, the base of the glass ramp, 4 mm off the visible island); then "the ring is too thick and there are cutouts in the top right and bottom right. Not good" (I had widened it to 5.1 mm for glue land and carved Apple's flash and LiDAR cones out of it); then "the guard should also be a bevel on the inside". He dismissed my multiple-choice dialog about what was wrong and typed the answer instead.

**How to apply:** Build the phone or mating-part proxy, push `SHOW=reset` as soon as the first visible feature exists, and iterate with `SHOW=1`. Keep engineering checks (keepout cones, clearances) as asserts or reports, but let looks lead on cosmetic features unless Brian says otherwise. Related: [[feedback-html-visual-companion]], [[feedback-verify-retention-features-closeup]].
