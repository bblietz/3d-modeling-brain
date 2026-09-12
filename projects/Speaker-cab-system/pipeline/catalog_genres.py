"""Rewrite each speaker note's Best with section onto canonical genre keys (Plan 3, Task 3).

The Plan 1 notes carry one bullet, "Amp families: ... Genres: <table labels>; ...
Families and genres per [[speaker-cab-voicing]]." This script splits it into
three bullets: the Amp families line (unchanged text), a Genres line holding
only the canonical keys from the voicing note's genre table, and a line with
any qualifier sentences plus the wikilink. Idempotent: a note that already
has a Genres line is left alone.

Run from the vault root:
  .venv/bin/python projects/Speaker-cab-system/pipeline/catalog_genres.py            (dry run)
  .venv/bin/python projects/Speaker-cab-system/pipeline/catalog_genres.py --apply
"""
import argparse
import re
from pathlib import Path

VAULT = Path(__file__).resolve().parents[3]
DEFAULT_SPEAKERS_DIR = VAULT / "knowledge" / "speakers"
SEE = "Families and genres per [[speaker-cab-voicing]]."
GENRE_KEYS = ("roots-country", "blues", "classic-rock", "indie-alternative", "jazz",
              "metal-high-gain", "worship-pop", "funk-rnb")
# Genre table row label (knowledge/speaker-cab-voicing.md) to its key.
LABEL_TO_KEY = {
    "Roots, country, alt-country": "roots-country",
    "Blues": "blues",
    "Classic rock": "classic-rock",
    "Indie and alternative": "indie-alternative",
    "Jazz": "jazz",
    "Metal and modern high gain": "metal-high-gain",
    "Worship and pop": "worship-pop",
    "Funk and R&B": "funk-rnb",
}
FAMILIES_PREFIX = "- Amp families: "


def genre_items(text: str) -> tuple:
    """(keys, qualifier sentences) from 'Label; Label qualifier; Label'."""
    keys, qualifiers = [], []
    for item in (s.strip() for s in text.split(";")):
        label = max((l for l in LABEL_TO_KEY if item == l or item.startswith(l + " ")),
                    key=len, default=None)
        if label is None:
            raise ValueError(f"genre {item!r} matches no row of the genre table")
        key = LABEL_TO_KEY[label]
        if key not in keys:
            keys.append(key)
        rest = item[len(label):].strip()
        if rest:
            qualifiers.append(f"{key} {rest}.")
    return keys, qualifiers


def patch_section(section: str) -> str:
    lines = section.split("\n")
    if any(l.startswith("- Genres: ") for l in lines):
        return section
    idx = next(i for i, l in enumerate(lines) if l.startswith(FAMILIES_PREFIX))
    body = lines[idx][len(FAMILIES_PREFIX):]
    families, rest = body.split(" Genres: ", 1)
    m = re.match(r"(.*?)\.(?: |$)(.*)", rest, re.S)
    keys, qualifiers = genre_items(m.group(1))
    tail = m.group(2).replace(SEE, "").strip()
    third = " ".join(s for s in ([tail] + qualifiers + [SEE]) if s)
    lines[idx:idx + 1] = [FAMILIES_PREFIX + families, "- Genres: " + ", ".join(keys), "- " + third]
    return "\n".join(lines)


def patch_note(text: str) -> str:
    head, section, rest = _split(text)
    return head + patch_section(section) + rest


def _split(text: str) -> tuple:
    marker = "\n## Best with\n"
    i = text.index(marker) + len(marker)
    j = text.find("\n## ", i)
    j = len(text) if j == -1 else j
    return text[:i], text[i:j], text[j:]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--speakers-dir", default=str(DEFAULT_SPEAKERS_DIR))
    ap.add_argument("--apply", action="store_true", help="write the notes (default: dry run)")
    args = ap.parse_args(argv)
    changed = 0
    for path in sorted(Path(args.speakers_dir).glob("*.md")):
        old = path.read_text()
        new = patch_note(old)
        keys = next(l for l in new.split("\n") if l.startswith("- Genres: "))[len("- Genres: "):]
        print(f"{path.stem}: {'unchanged' if new == old else 'patched'}, genres {keys}")
        if new != old:
            changed += 1
            if args.apply:
                path.write_text(new)
    print(f"{changed} note(s) {'written' if args.apply else 'would change'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
