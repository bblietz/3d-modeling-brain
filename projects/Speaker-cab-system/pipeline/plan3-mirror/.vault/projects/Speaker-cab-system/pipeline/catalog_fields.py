"""Add frame and magnet diameters to the speaker catalog notes (Plan 2, Task 1).

Inserts frame_diameter_mm, magnet_diameter_mm, and magnet_diameter_estimated
into each note's YAML frontmatter directly after depth_mm, and appends one
flagged bullet to the note's Data notes list. Values and their basis come from
knowledge/research/speaker-envelopes-and-port-stock.md; estimated magnet
diameters use the conservative top of the research band. Idempotent: a second
run changes nothing.

Run from the vault root:
  .venv/bin/python projects/Speaker-cab-system/pipeline/catalog_fields.py            (dry run)
  .venv/bin/python projects/Speaker-cab-system/pipeline/catalog_fields.py --apply
"""
import argparse
from pathlib import Path

VAULT = Path(__file__).resolve().parents[3]
DEFAULT_SPEAKERS_DIR = VAULT / "knowledge" / "speakers"
SEE = "See [[speaker-envelopes-and-port-stock]]."
VOICE_COIL = ("- The 141.pdf source is Voice Coil magazine (February 2015), "
              "not a Celestion spec sheet.")

# slug: (frame_diameter_mm, magnet_diameter_mm, estimated, basis or None)
EMINENCE_38 = "top of the 135 to 150 mm band from the published magnet weight and ferrite density"
EMINENCE_59 = "top of the 163 to 181 mm band from the published magnet weight and ferrite density"
WGS_G12M = "by analogy to the Celestion G12M it clones, 145 to 150 mm band"
WGS_V30 = "by analogy to the Celestion Vintage 30 it clones"
FIELDS = {
    "celestion-blue": (309, 128, False, None),
    "celestion-cream": (309, 128, False, None),
    "celestion-gold": (309, 128, False, None),
    "celestion-g12-65-heritage": (309, 145, False, None),
    "celestion-g12m-25-greenback": (309, 150, False, None),
    "celestion-g12m-65-creamback": (309, 150, False, None),
    "celestion-vintage-30": (309, 156, False, None),
    "celestion-g12h-30-anniversary": (309, 156, False, None),
    "celestion-g12h-75-creamback": (309, 168, False, None),
    "celestion-heritage-g12h55": (309, 168, False, None),
    "jensen-c12n": (307.0, 134.0, False, None),
    "jensen-p12n": (307.0, 160.0, False, None),
    "eminence-cannabis-rex": (305.6, 150, True, EMINENCE_38),
    "eminence-red-white-and-blues": (305.6, 150, True, EMINENCE_38),
    "eminence-texas-heat": (305.6, 150, True, EMINENCE_38),
    "eminence-swamp-thang": (305.6, 181, True, EMINENCE_59),
    "eminence-tonker": (305.6, 181, True, EMINENCE_59),
    "wgs-et65": (309.6, 150, True, WGS_G12M),
    "wgs-green-beret": (309.6, 150, True, WGS_G12M),
    "wgs-veteran-30": (309.6, 156, True, WGS_V30),
}


def _bullet(frame, magnet, estimated, basis) -> str:
    if estimated:
        return (f"- Magnet diameter {magnet:g} mm is estimated ({basis}); "
                f"frame diameter {frame:g} mm is published. {SEE}")
    return (f"- Frame diameter {frame:g} mm and magnet diameter {magnet:g} mm "
            f"from the maker's drawing. {SEE}")


def patch_note(text: str, slug: str) -> str:
    frame, magnet, estimated, basis = FIELDS[slug]
    head, body = text.split("\n---\n", 1)
    lines = head.split("\n")
    if not any(line.startswith("frame_diameter_mm:") for line in lines):
        idx = next(i for i, line in enumerate(lines) if line.startswith("depth_mm:"))
        lines[idx + 1:idx + 1] = [f"frame_diameter_mm: {frame:g}",
                                  f"magnet_diameter_mm: {magnet:g}",
                                  f"magnet_diameter_estimated: {'true' if estimated else 'false'}"]
    head = "\n".join(lines)
    section, rest = body.split("\n## Field notes", 1)
    if SEE not in section:
        section = section.rstrip("\n") + "\n" + _bullet(frame, magnet, estimated, basis) + "\n"
    if "2019/10/141.pdf" in head and VOICE_COIL not in section:
        section = section.rstrip("\n") + "\n" + VOICE_COIL + "\n"
    return head + "\n---\n" + section + "\n## Field notes" + rest


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--speakers-dir", default=str(DEFAULT_SPEAKERS_DIR))
    ap.add_argument("--apply", action="store_true", help="write the notes (default: dry run)")
    args = ap.parse_args(argv)
    speakers = Path(args.speakers_dir)
    changed = 0
    for slug in sorted(FIELDS):
        path = speakers / f"{slug}.md"
        if not path.exists():
            print(f"{slug}: MISSING note")
            continue
        old = path.read_text()
        new = patch_note(old, slug)
        state = "unchanged" if new == old else "patched"
        frame, magnet, estimated, _ = FIELDS[slug]
        print(f"{slug}: {state}, frame {frame:g}, magnet {magnet:g}"
              f"{' (estimated)' if estimated else ''}")
        if new != old:
            changed += 1
            if args.apply:
                path.write_text(new)
    print(f"{changed} note(s) {'written' if args.apply else 'would change'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
