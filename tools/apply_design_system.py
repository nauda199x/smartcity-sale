"""Attach Design System V2 assets to public HTML, deterministically."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {"_source", "_site", ".git"}

for page in sorted(ROOT.rglob("*.html")):
    if any(part in EXCLUDED for part in page.relative_to(ROOT).parts):
        continue
    text = page.read_text(encoding="utf-8")
    if "/assets/design-system.css" not in text:
        text = text.replace("</head>", '<link rel="stylesheet" href="/assets/design-system.css"></head>', 1)
    if "/assets/app-shell.js" not in text:
        text = text.replace("</body>", '<script src="/assets/app-shell.js" defer></script></body>', 1)
    # V2 provides these formerly repeated article/project rules centrally.
    if page.name != "404.html":
        text = re.sub(r"<style>(?:(?!</style>).)*</style>", "", text, flags=re.S)
    text = text.replace(' style="background:#f7f9f8"', ' class="section-surface"')
    text = text.replace('class="btn" style="background:#0b1220;color:#fff"', 'class="btn button-primary"')
    page.write_text(text, encoding="utf-8")

print("applied Design System V2")
