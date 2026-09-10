"""One-off I6 wording pass over the twenty speaker notes and the plan's note blocks (fix wave step 8).

Each note's full text occurs once in projects/Speaker-cab-system/plan-1-knowledge-engine.md;
the script rewrites the note and swaps old text for new text in the plan so they stay identical.
"""
import re
from pathlib import Path

VAULT = Path(__file__).resolve().parents[3]
SPEAKERS = VAULT / "knowledge/speakers"
PLAN = VAULT / "projects/Speaker-cab-system/plan-1-knowledge-engine.md"
REF = " Families and genres per [[speaker-cab-voicing]]."

BEST_WITH = {
    "celestion-g12h-30-anniversary": ("Marshall, Tweed Fender, Vox", "Classic rock; Blues; Indie and alternative", ""),
    "celestion-cream": ("Boutique clean, Blackface Fender, Vox at any power", "Worship and pop; Jazz; Indie and alternative", ""),
    "celestion-blue": ("Vox, Boutique clean up to 15 W, or two Blues under a 30 W amp (the accepted early-breakup case)",
                       "Indie and alternative; Blues; Worship and pop at low volume", ""),
    "celestion-g12-65-heritage": ("Marshall, Modern high gain at moderate gain", "Classic rock; Blues", ""),
    "celestion-heritage-g12h55": ("Marshall, Tweed Fender", "Classic rock; Blues", ""),
    "eminence-swamp-thang": ("Modern high gain, Modeling and solid state, Marshall", "Metal and modern high gain; Classic rock",
                             " Suits baritone and drop tunings."),
    "jensen-c12n": ("Blackface Fender, Tweed Fender", "Roots, country, alt-country; Jazz; Blues",
                    " Qts above 1: prefers open or semi-open; closed boxes under about 59 L net come out peaky (Qtc 1.26 at 44 L; 1.18, big, at the 68 L clamp)."),
    "celestion-g12h-75-creamback": ("Modern high gain, Blackface Fender, Modeling and solid state",
                                    "Metal and modern high gain; Classic rock; Funk and R&B", ""),
    "eminence-texas-heat": ("Tweed Fender, Marshall, Blackface Fender", "Blues; Classic rock; Roots, country, alt-country", ""),
    "celestion-g12m-25-greenback": ("Marshall, Vox, Tweed Fender", "Classic rock; Blues; Indie and alternative",
                                    " Two per cabinet under amps over 20 W."),
    "eminence-tonker": ("Modeling and solid state, Boutique clean, Blackface Fender at high volume",
                        "Jazz; Worship and pop; Funk and R&B", ""),
    "celestion-vintage-30": ("Marshall, Modern high gain, Boutique clean", "Classic rock; Metal and modern high gain; Worship and pop", ""),
    "celestion-gold": ("Vox, Boutique clean, Blackface Fender", "Indie and alternative; Blues; Worship and pop", ""),
    "celestion-g12m-65-creamback": ("Marshall, Boutique clean, Modern high gain at moderate gain",
                                    "Classic rock; Blues; Worship and pop", ""),
    "wgs-green-beret": ("Marshall, Vox, Tweed Fender", "Classic rock; Blues",
                        " Qts 1.18 as printed: prefers open or semi-open backs; two per cabinet for amps over 20 W."),
    "wgs-veteran-30": ("Modern high gain, Marshall, Boutique clean", "Classic rock; Metal and modern high gain; Worship and pop", ""),
    "wgs-et65": ("Marshall, Blackface Fender, Boutique clean", "Classic rock; Blues; Indie and alternative",
                 " Qts above 0.9: prefers open or semi-open backs."),
    "eminence-cannabis-rex": ("Blackface Fender, Boutique clean, Tweed Fender",
                              "Roots, country, alt-country; Jazz; Indie and alternative; Blues", ""),
    "jensen-p12n": ("Tweed Fender, Blackface Fender", "Blues; Roots, country, alt-country; Jazz",
                    " Historically an open-back combo speaker; prefers open or semi-open."),
    "eminence-red-white-and-blues": ("Blackface Fender, Modeling and solid state, Boutique clean",
                                     "Funk and R&B; Worship and pop; Roots, country, alt-country", ""),
}

SIXTEEN_OHM = ("- The frontmatter holds the 8 ohm set; a 16 ohm choice is voiced with it until a per-impedance "
               "schema lands (see the model limits in [[speaker-cab-voicing]]).")
SOURCED = " Cutout, power, sensitivity, and impedance are from the cited product page (or sheet) as well."

EXTRA = {
    "celestion-g12h-30-anniversary": [
        ("The current 30 W G12H with the\n75 Hz cone", "The current 30 W G12H with the\n85 Hz cone"),
        ("Qts = 0.61 x 14.7 / (0.61 + 14.7) = 0.58.", "Qts = 0.61 x 14.7 / (0.61 + 14.7) = 0.58 (the rounded factors shown give 0.59; the unrounded chain gives 0.58, the frontmatter value)."),
    ],
    "wgs-green-beret": [
        ("its printed Cms of 0.06 mm/N agrees)", "its printed Cms of 0.06 mm/N agrees within 7 percent)"),
        ("are assumptions stated above, not WGS data;", "are assumptions stated above, not WGS data; depth 128.6 mm and weight 3.4 kg are assumed as the ET65's, since WGS prints only \"mounting as the ET65\";"),
    ],
    "celestion-heritage-g12h55": [
        ("- Thiele-Small values are Voice Coil Test Bench sample 1 (16 ohm):", "- Thiele-Small values are Voice Coil Test Bench sample 1 (16 ohm), LTD model column:"),
    ],
}


def rewrite(slug: str, text: str) -> str:
    fams, genres, tail = BEST_WITH[slug]
    lines = text.split("\n")
    idx = [i for i, l in enumerate(lines) if l.startswith("- Amp families:")]
    assert len(idx) == 1, slug
    lines[idx[0]] = f"- Amp families: {fams}. Genres: {genres}.{tail}{REF}"
    if slug.startswith("celestion-") or slug.startswith("eminence-"):
        head = "- Celestion publishes" if slug.startswith("celestion-") else "- 8 ohm T/S from"
        idx = [i for i, l in enumerate(lines) if l.startswith(head)]
        assert len(idx) == 1, slug
        lines[idx[0]] += SOURCED
        if slug in ("eminence-texas-heat", "eminence-swamp-thang"):
            lines.insert(idx[0] + 1, SIXTEEN_OHM)
    text = "\n".join(lines)
    for old, new in EXTRA.get(slug, []):
        assert text.count(old) == 1, (slug, old)
        text = text.replace(old, new)
    return text


def main() -> int:
    et65 = (SPEAKERS / "wgs-et65.md").read_text()
    assert "depth_mm: 128.6\n" in et65 and "weight_kg: 3.4\n" in et65, "ET65 depth or weight moved"
    plan = PLAN.read_text()
    for path in sorted(SPEAKERS.glob("*.md")):
        old = path.read_text()
        new = rewrite(path.stem, old)
        assert plan.count(old) == 1, path.name
        assert "—" not in new and "–" not in new
        plan = plan.replace(old, new)
        path.write_text(new)
    PLAN.write_text(plan)
    print("rewrote 20 notes and their plan blocks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
