#!/usr/bin/env python
"""Print the shop page to PDF with headless Chrome (Letter, 1/2 in margins, no
browser header or footer). The page's own @media print rules do the layout:
tick boxes and zoom captions hidden, each row and drawing kept on one page,
each big section on a new page.

Usage: .venv/bin/python projects/Built-in-bench/make_pdf.py
Run make_cutlist_page.py first.
"""
import os
import subprocess
import sys

VAULT = "/home/brian/ClaudeProjects/3d-modeling-brain"
PROJ = f"{VAULT}/projects/Built-in-bench"
HTML = f"{PROJ}/cutlist.html"
PDF = f"{PROJ}/cutlist.pdf"
PROFILE = os.environ.get("CHROME_PROFILE", "/tmp/claude-chrome-print-profile")

assert os.path.exists(HTML), "run make_cutlist_page.py first"
cmd = ["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox",
       f"--user-data-dir={PROFILE}", "--no-pdf-header-footer",
       "--run-all-compositor-stages-before-draw", "--virtual-time-budget=8000",
       f"--print-to-pdf={PDF}", f"file://{HTML}"]
r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
if not os.path.exists(PDF):
    print(r.stderr[-2000:])
    sys.exit("no PDF written")
print("wrote", os.path.relpath(PDF, VAULT), os.path.getsize(PDF) // 1024, "KB")
