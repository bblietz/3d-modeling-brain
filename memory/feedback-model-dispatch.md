---
name: feedback-model-dispatch
description: Name the model that fits each task and say so out loud, especially when Fable 5.1 is the better choice than whatever is active
metadata:
  type: feedback
---

Brian wants to be told which model fits a task, not just told when a switch happens. Two cases to speak up about: when Fable 5.1 is preferred over the active model, and when a task he asks for would be better served by a different model than the one running.

**Why:** he sets the session default himself (he set Opus 5 as default on 2026-09-09 mid-session), so the active model is often his choice rather than a per-task decision. He wants the per-task recommendation surfaced so he can decide, rather than silently running the wrong model. His global instructions already say correctness beats speed and cost is irrelevant, so the recommendation should never be shaded by cost.

**How to apply:** at the start of a request, and again when the task character changes, judge the right model and say it in one line. Prefer Fable 5.1 for deep design reasoning, geometry and dimension verification, debugging non-obvious failures, and anything touching shared state or a real physical fit. Opus 5 or lighter is fine for routine execution: running a slice, launching an app, fixing a path, single-file edits, well-bounded lookups. Do not bury the recommendation, and do not switch silently. Related: [[feedback-agentic-os-conventions]], [[feedback-minimal-test-coupons]].
