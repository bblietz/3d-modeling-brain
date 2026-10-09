---
name: feedback-keep-skirt
description: Every print 3MF keeps the 2-loop skirt (skirt_loops 2, distance 3, height 1); Brian confirmed it 2026-10-09 after asking what the border was
metadata:
  type: feedback
---

Keep the skirt on every print 3MF the pipelines build: `skirt_loops 2`, `skirt_distance 3`,
`skirt_height 1`. Bambu's X2D profiles default to no skirt (`skirt_loops 0`).

**Why:** Brian asked on 2026-10-09 why "you always add a border around the actual device"; told
it is the skirt from the vault's PETG rule (primes the flow after the purge line, shows first-layer
adhesion before the part starts, about a gram and a minute), he said "leave the skirt in".

**How to apply:** do not drop or shrink the skirt to save time or filament, and do not ask again;
if a project needs a brim instead, say so and keep the skirt setting documented in its pipeline.
Related: [[feedback-stl-to-bambu-3mf]], [[project-nacs-wall-holder]].
