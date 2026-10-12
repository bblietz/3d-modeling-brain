---
name: feedback-model-dispatch
description: "Design work runs on Fable 5.1 only; if a lighter model is active, STOP before building and tell Brian, do not proceed with a note"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 436656c6-ca45-4497-873c-df44f48e28f5
  modified: 2026-10-12T05:47:49.981Z
---

Brian wants design work (CAD, geometry, dimensions, fits, anything that ends in a print or a cut) done on Fable 5.1. If the session is running a lighter model when design work starts, stop before building anything and say so, so he can run `/model fable` and have the work redone. Naming the mismatch and continuing anyway is not enough.

**Why:** on 2026-10-11 a Sonnet 5.5 session built the first two versions of the guitar pick before he noticed; he switched to Fable and asked for the work redone, then said "next time stop when the wrong model is being used for design work". Earlier (2026-09-09) he set Opus 5 as default mid-session, so the active model is often his session default rather than a per-task choice; he wants the mismatch surfaced as a hard stop at the start, not discovered after the geometry is built. His global instructions say correctness beats speed and cost is irrelevant, so the recommendation is never shaded by cost.

**How to apply:** at the start of a request, and again when the task character changes, judge the right model and say it in one line. For design work on a model lighter than Fable 5.1: stop, state the mismatch, and wait; do not run the skill, do not build a first pass. Opus 5 or lighter is fine for routine execution: running a slice, launching an app, fixing a path, single-file edits, well-bounded lookups. Never switch silently. Related: [[feedback-agentic-os-conventions]], [[feedback-minimal-test-coupons]].
