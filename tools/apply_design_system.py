"""Attach Design System V2 assets to public HTML, deterministically."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {"_source", "_site", ".git"}
THEME_LINK = '<link rel="stylesheet" href="/assets/css/site-theme.css?v=20260902-1">'


def add_class_for_style(match: re.Match) -> str:
    """Replace the migrated style declaration and preserve an existing class."""
    tag = match.group(0).replace(' style="background:#f7f9f8"', "")
    class_attr = re.search(r'\bclass="([^"]*)"', tag)
    if class_attr:
        merged = class_attr.group(1).split()
        if "section-surface" not in merged:
            merged.append("section-surface")
        return tag[:class_attr.start()] + f'class="{" ".join(merged)}"' + tag[class_attr.end():]
    return tag[:-1] + ' class="section-surface">'


def merge_adjacent_classes(match: re.Match) -> str:
    """Repair output produced by the original V2 migration before this fix."""
    classes = list(dict.fromkeys((match.group(1) + " " + match.group(2)).split()))
    return f'class="{" ".join(classes)}"'

for page in sorted(ROOT.rglob("*.html")):
    if any(part in EXCLUDED for part in page.relative_to(ROOT).parts):
        continue
    text = page.read_text(encoding="utf-8")
    text = re.sub(r'class="([^"]*)"\s+class="([^"]*)"', merge_adjacent_classes, text)
    if "/assets/design-system.css" not in text:
        text = text.replace("</head>", '<link rel="stylesheet" href="/assets/design-system.css"></head>', 1)
    # Keep the Smart City theme as the final stylesheet after any generated layer.
    text = text.replace(THEME_LINK, "")
    text = text.replace("</head>", THEME_LINK + "</head>", 1)
    if "/assets/app-shell.js" not in text:
        text = text.replace("</body>", '<script src="/assets/app-shell.js" defer></script></body>', 1)
    # V2 provides these formerly repeated article/project rules centrally.
    if page.name != "404.html":
        text = re.sub(r"<style>(?:(?!</style>).)*</style>", "", text, flags=re.S)
    text = re.sub(
        r'<section\b[^>]*\bstyle="background:#f7f9f8"[^>]*>',
        add_class_for_style,
        text,
    )
    text = text.replace('class="btn" style="background:#0b1220;color:#fff"', 'class="btn button-primary"')
    page.write_text(text, encoding="utf-8")

print("applied Design System V2")
