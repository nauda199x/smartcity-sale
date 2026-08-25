#!/usr/bin/env python3
"""Normalize already-reviewed Drive thumbnail URLs after project profile rendering.

public_inventory_image() intentionally returns HTML-safe '&amp;'. Some project
profile call sites also HTML-escape the safe URL, producing '&amp;amp;sz=' in
source. Browsers then request an 'amp;sz' query parameter instead of 'sz',
which can fall back to a small thumbnail. Keep this post-render step narrow and
deterministic until the image helper contract is migrated site-wide.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = json.loads((ROOT / "data/projects/projects.json").read_text(encoding="utf-8"))["projects"]

changed = 0
for project in PROJECTS:
    path = ROOT / project["route"]
    if not path.is_file():
        continue
    text = path.read_text(encoding="utf-8")
    normalized = text.replace("&amp;amp;sz=w1200", "&amp;sz=w1200")
    if normalized != text:
        path.write_text(normalized, encoding="utf-8")
        changed += 1

print(f"normalized Drive thumbnail URLs in {changed} project profile(s)")
