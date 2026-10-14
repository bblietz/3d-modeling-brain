---
name: feedback-bounded-fanout
description: Never launch one heavy python or slicer process per variant; fan out through a bounded pool (4 workers, e.g. xargs -P 4) after measuring one run's peak RSS. A session in this vault fanned out about 30 filament-budget runs at once on 2026-10-12 and OOM-killed Brian's user manager and trading daemons for 4 hours.
metadata:
  node_type: memory
  type: feedback
  originSessionId: 436656c6-ca45-4497-873c-df44f48e28f5
  modified: 2026-10-14T10:30:00.000Z
---

Heavy jobs on this box (G-code parses, trimesh `contains`, Bambu CLI slices, OpenSCAD renders) are launched through a bounded pool, never one process per variant. The rule came out of Brian's Linux Admin project after the 2026-10-12 OOM storm.

**Why:** on 2026-10-12 at 10:05 PDT a 3d-modeling-brain session ran `projects/NACS-wall-holder/pipeline/filament_budget.py regions` for every filament variant at the same time, about 30 python processes of 1 to 2 GB each (the holder's run actually peaked at 9.7 GB because trimesh without embree expands `mesh.contains()` to about 100 KB per point). The kernel's OOM killer fired 189 times on the 64 GB box and, because Ubuntu's user manager and user services carried a higher oom_score_adj than the slicers, it killed `systemd --user` itself: Ollama, Open WebUI, the trading daemon and dashboard and the Kalshi bot were down from 10:06 to 14:00 PDT, most of a US market day, with live crypto money on the trading side. Brian fixed the box side on 2026-10-14 (user manager oom_score_adj -1000, trading units -900, MemoryLow chain, swap 16 GB) and had the slicer job chunked (`contains(mesh, pts, chunk=2000)` in filament_budget.py, peak 0.49 GB, identical totals). None of that makes an unbounded fan-out safe; it only keeps the damage to the session that caused it.

**How to apply:** before fanning anything out, run ONE instance under `/usr/bin/time -v` and read its Maximum resident set size; then size the pool so pool x peak stays under about half of `free -g`'s available column, and cap it at 4 regardless (`xargs -P 4`, `concurrent.futures` with `max_workers=4`, or a sequential loop when the per-run cost is unknown). Subagents count too: do not give several subagents each a heavy job at the same time. If a job's peak is unexpectedly large, fix the job (chunk the work, as in filament_budget.py) rather than raising the pool. The slicer-group memory cap via `systemd-run --user --scope -p MemoryMax=44G` is still Brian's open call in the Linux Admin project; do not apply it from here. Related: [[feedback-agentic-os-conventions]], [[project-nacs-wall-holder]], [[project-keep-tools-in-vault]].
