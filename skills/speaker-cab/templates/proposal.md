---
type: proposal
customer: {{customer}}
order: {{order}}
generated: {{generated}}
---
<!--
MaximoCabs voice, from the site on 2026-09-11. Write the four slots in this register:
  "Custom cabinets, built to your sound"
  "We treat every order as an acoustic brief. Two 1x12 cabinets, one in tolex, one in hardwood, each tuned to the amp you actually play and the rooms you actually play in."
  "Tailored, not configured."
  "Tell us your amplifier, the style you play, and the rooms you work in. We design the internal volume, port, and baffle around it. Defaults exist; specs do not."
  "Void-free Baltic birch ply in the Tolex, solid resawn hardwood in the Hardwood. Hand-cut joinery. Felt-isolated floating baffles. Nothing decorative."
  "Every cabinet is built start-to-finish by one builder. Lead times reflect that."
Rule: nothing in this proposal is a measured claim. Say what the cabinet is designed for; never quote a frequency, a decibel, or a test result.
Edit only between the slot markers. Every line outside them is a fact from cab.json and voicing.json that `cabreport.py --verify` checks.
-->

# Your MaximoCabs {{line_label}}

Prepared for {{customer}}.

## 1. Your rig and goals

<!-- slot: rig_and_goals -->
<!-- /slot -->

## 2. The recommended cabinet

- Cabinet: {{line_label}}, {{back_type}}
- Configuration: {{configuration}}
- Speaker: {{speaker_label}}
- Impedance and wiring: {{wiring}}
- External size, width x height x depth: {{external_in}} ({{external_mm}})
- Estimated weight, loaded: {{mass_lb}} lb ({{mass_kg}} kg)

<!-- slot: why_this_cabinet -->
<!-- /slot -->

## 3. What it is designed to do

<!-- slot: designed_to_do -->
<!-- /slot -->

## 4. Alternatives considered

<!-- slot: alternatives -->
<!-- /slot -->

## 5. Finishes

- Finish: {{finish}}
- Grill cloth: {{grill_cloth}}
- Hardware: {{hardware}}

<!-- Swatches: copy the files named below from ~/ClaudeProjects/MaximoCabs/public/materials/ (tolex/, grill-cloth/, wood/) into this order's images/ folder. A name prefixed with its folder is the file <folder>/<rest of the name> copied under the prefixed name: images/tolex-fender-black.jpg is tolex/fender-black.jpg. -->
{{swatch_finish}}
{{swatch_cloth}}

## 6. Lead time and price

- Lead time: {{lead_time}}
- Price:

{{status_line}}
