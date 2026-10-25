"""Fill the slice figures from cable-bin-slice.json into options.html and brief.md.

Placeholders: {{P1_TIME}} {{P1_G}} {{P2_TIME}} {{P2_G}} {{TOTAL_TIME}} {{TOTAL_G}}
{{BIN_TIME}} {{BIN_G}}. Already-filled files are rewritten from the templates
kept beside them (*.tmpl), so the script is safe to rerun after a reslice.

Run from the vault root: .venv/bin/python projects/Cable-bin/pipeline/fill_numbers.py
"""
import json
import os
import shutil

PROJ = os.path.join("/home/brian/ClaudeProjects/3d-modeling-brain", "projects", "Cable-bin")


def hm(seconds):
    h, m = divmod(round(seconds / 60), 60)
    return f"{h} h {m:02d} min" if h else f"{m} min"


def main():
    d = json.load(open(os.path.join(PROJ, "cable-bin-slice.json")))
    p1 = next(p for p in d["plates"] if p["name"] == "Bin")
    p2 = next(p for p in d["plates"] if p["name"] != "Bin")
    four = 4 * p1["seconds"] + p2["seconds"]
    values = {
        "P1_TIME": hm(p1["seconds"]), "P1_G": f"{p1['grams']:.0f}",
        "P2_TIME": hm(p2["seconds"]), "P2_G": f"{p2['grams']:.0f}",
        "TOTAL_TIME": hm(four), "TOTAL_G": f"{4 * p1['grams'] + p2['grams']:.0f}",
        "BIN_TIME": hm(p1["seconds"]), "BIN_G": f"{p1['grams']:.0f}",
    }
    for fname in ("options.html", "brief.md"):
        path = os.path.join(PROJ, fname)
        tmpl = path + ".tmpl"
        if not os.path.exists(tmpl):
            shutil.copy(path, tmpl)
        s = open(tmpl).read()
        for k, v in values.items():
            s = s.replace("{{" + k + "}}", v)
        assert "{{" not in s, f"unfilled placeholder in {fname}"
        open(path, "w").write(s)
        print("filled", path)
    print(values)


if __name__ == "__main__":
    main()
