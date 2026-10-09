---
name: feedback-nanobanana-report-cost
description: "Every nanobanana (Gemini image) API call must be reported to Brian with its cost; Brian's rule 2026-10-09"
metadata:
  node_type: memory
  type: feedback
  originSessionId: d3e73073-5ff1-4cf2-8b88-f1fd6660abc7
  modified: 2026-10-09T16:57:55.688Z
---

Whenever the nanobanana skill (Google Gemini image generation, `gemini-3-pro-image-preview`) is used, report the cost of the call to Brian in the reply, every time, even when it is small. If the price is uncertain, say what it is based on.

**Why:** the Gemini image API is metered per image on Brian's own API key, unlike the rest of the vault tooling. Brian said on 2026-10-09: "whenever you use nanobanana API, if there is a cost associated always report it to me."

**How to apply:** scripts that call the API print the response's usage metadata (prompt and candidate token counts) and a dollar estimate from Google's current price list; quote that in the reply, and give the count of images generated. Check the price list again if it is more than a few months old. Related: [[project-built-in-bench]] (first use: `projects/Built-in-bench/render_in_room.py`).
