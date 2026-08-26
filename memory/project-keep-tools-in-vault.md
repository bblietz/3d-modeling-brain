---
name: project-keep-tools-in-vault
description: "Session scratchpads get wiped on Claude Code restarts; reusable pipeline tools and monitors must live in the vault (projects/<Name>/pipeline or scripts/), never only in the scratchpad"
metadata: 
  node_type: memory
  type: project
  originSessionId: 744ff3b5-47ea-4284-a4c0-57fb6e3fdbcb
  modified: 2026-08-25T04:52:52.870Z
---

On 2026-08-24 a Claude Code process restart erased the session scratchpad, taking with it the fill-core coupon builder, modifier injector, graft-slice and toolpath-void-metric scripts (all rewritten from the report afterward), the chamber-temperature monitor script and its CSV log, and converted photos.

**Why:** The scratchpad is session-specific and not durable; anything a later session or a rebuild needs must be in the vault, which is the Obsidian-indexed, persistent store.

**How to apply:** Subagent deliverables that are tools go in `projects/<Name>/pipeline/` (project-specific) or `scripts/` (general); monitors that must survive go in `scripts/` with their logs under the project directory. Use the scratchpad only for intermediate slices, G-code, and renders that are cheap to regenerate. Related: [[feedback-agentic-os-conventions]].
