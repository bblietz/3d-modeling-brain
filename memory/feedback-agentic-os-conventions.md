---
name: feedback-agentic-os-conventions
description: Run 3d-modeling-brain as an agentic OS, subagent-first, with memory indexed by Obsidian
metadata:
  type: feedback
---

Brian wants the 3d-modeling-brain project operated as an agentic OS and second brain.

**Why:** parallelize work, protect the main context from bloat, and keep all durable knowledge browsable and linkable in Obsidian.

**How to apply:** dispatch subagents whenever a task can be delegated (exploration, reference-image inspection, transcript mining, parallel independent builds), batching independent ones in parallel. Write durable notes as Obsidian markdown with frontmatter and [[wikilinks]]. The canonical memory location is `<project>/memory/`; the `~/.claude/projects/-home-brian-ClaudeProjects-3d-modeling-brain/memory` path is a symlink to it and must not be broken. See also [[user-printer-hardware]].
