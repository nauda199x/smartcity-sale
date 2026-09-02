#!/usr/bin/env python3
"""Attach the final site-wide visual theme to committed HTML deterministically."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_PARTS = {".git", "_site"}
THEME_HREF = "/assets/css/site-theme.css?v=20260902-1"
THEME_LINK = f'<link rel="stylesheet" href="{THEME_HREF}">'


def eligible(path: Path) -> bool:
    return not any(part in EXCLUDED_PARTS for part in path.relative_to(ROOT).parts)


updated = 0
for page in sorted(ROOT.rglob("*.html")):
    if not eligible(page):
        continue
    html = page.read_text(encoding="utf-8")
    if "</head>" not in html:
        continue
    themed = html.replace(THEME_LINK, "")
    themed = themed.replace("</head>", THEME_LINK + "</head>", 1)
    if themed != html:
        page.write_text(themed, encoding="utf-8")
        updated += 1

print(f"applied site theme to {updated} HTML files")
