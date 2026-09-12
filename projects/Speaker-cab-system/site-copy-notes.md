---
name: site-copy-notes
description: Sentences on the MaximoCabs site that the speaker cab system has overtaken or that need a check (hardwood joinery, closed-back wording, loaded weights); a note for Brian, the site itself is out of scope in this vault
type: note
created: 2026-09-11
tags: [project, speaker-cab, maximocabs, site]
---

# MaximoCabs site copy: notes for Brian

The vault does not change the site (`~/ClaudeProjects/MaximoCabs`); this note records what the Plan 2 and Plan 3 work found, per [[2026-09-11-plan-3-skill-design]] section 11. Line numbers are as of 2026-09-11.

## Wrong: hardwood joinery

`src/content/cabinets/hardwood-1x12.md`, line 33:

    joinery: "Through-tenon corner posts, glued + pinned"

The hardwood line is built with finger joints by default and through dovetails as the option, with no corner posts, since [[2026-09-10-plan-2-generator-design]] (see [[speaker-cab-construction]], Shell per line). The tolex page already reads `joinery: "Hand-cut finger joints"` (`tolex-1x12.md`, line 33) and the homepage says "Hand-cut joinery." (`src/pages/index.astro`, line 28). A row that matches the build: `joinery: "Hand-cut finger joints (through dovetails on request)"`.

## A default, not the only option: closed-back wording

Both cabinet pages, line 30:

    configuration: "1x12 closed-back, ported"

and the tolex description (`tolex-1x12.md`, line 39): "Closed-back for focused low end."

The system voices closed-ported, closed, open, and semi-open boxes and 2x12 cabinets ([[speaker-cab-voicing]], Enclosure type rules), and the homepage already promises the volume, port, and baffle designed around the rig (`index.astro`, line 24). The wording can stay as the default if the pages say so, for example `configuration: "1x12 closed-back, ported (open-back and 2x12 on request)"`.

## Verify before changing: loaded weights

`tolex-1x12.md`, line 37: `weightApprox: "~32 lb loaded"`. `hardwood-1x12.md`, line 37: `weightApprox: "~38 lb loaded (varies by species)"`.

The site-default fixture (`projects/Speaker-cab-system/fixtures/site-default/`, the 20 x 18 x 11 in tolex box with a G12H Anniversary at 4.7 kg) computes 17.0 kg, 37.5 lb, loaded: 11.3 kg of birch parts, the 4.7 kg speaker, and a 1 kg hardware allowance. That is a starting-value calculation ([[speaker-cab-construction]], Weight and center of mass), not a measurement: weigh a built tolex cab before touching the page. If the model holds, the tolex figure reads about 6 lb light and the hardwood figure needs its own check against the species densities.
