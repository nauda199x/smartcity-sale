#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "https://timmuasmartcity.com"

hub_path = ROOT / "mat-bang-smart-city/lumiere-evergreen/index.html"
assert hub_path.exists(), "missing Lumiere Evergreen floorplan hub"
hub = hub_path.read_text(encoding="utf-8")
assert '<meta name="robots" content="index,follow,max-image-preview:large">' in hub
assert f'<link rel="canonical" href="{DOMAIN}/mat-bang-smart-city/lumiere-evergreen/">' in hub
assert '"@type":"CollectionPage"' in hub
assert '"@type":"BreadcrumbList"' in hub
assert '"@type":"FAQPage"' in hub
for tower in ("a1", "a2", "a3"):
    assert f'href="/mat-bang-smart-city/lumiere-evergreen/{tower}/"' in hub, f"hub missing {tower} link"
for child in (
    "mat-bang-can-ho-lumiere-evergreen-theo-loai.html",
    "cach-chon-toa-lumiere-evergreen-a1-a2-a3.html",
):
    assert f'href="/{child}"' in hub, f"hub missing child link: {child}"
for needle in ("The Aqua", "The Atmos", "The Aura", "Studio", "1PN+", "2PN+", "4PN", "26 căn", "12–19", "21–39"):
    assert needle in hub, f"hub missing {needle!r}"

PAGES = {
    "mat-bang-can-ho-lumiere-evergreen-theo-loai.html": [
        "36,1",
        "32,2",
        "51,9",
        "46,7",
        "66,1",
        "61,1",
        "115,0",
        "106,3",
        "4PN",
        "/mat-bang-smart-city/lumiere-evergreen/",
    ],
    "cach-chon-toa-lumiere-evergreen-a1-a2-a3.html": [
        "A1",
        "A2",
        "A3",
        "The Aqua",
        "The Atmos",
        "The Aura",
        "18 căn/sàn",
        "26 căn",
        "/mat-bang-smart-city/lumiere-evergreen/",
    ],
}

for filename, needles in PAGES.items():
    path = ROOT / filename
    assert path.exists(), f"missing Lumiere SEO page: {filename}"
    text = path.read_text(encoding="utf-8")
    assert 'name="robots" content="index,follow,max-image-preview:large"' in text, f"robots missing: {filename}"
    assert f'<link rel="canonical" href="{DOMAIN}/{filename}">' in text, f"self canonical missing: {filename}"
    assert '"@type":"Article"' in text, f"Article schema missing: {filename}"
    assert '"@type":"BreadcrumbList"' in text, f"Breadcrumb schema missing: {filename}"
    assert '"@type":"FAQPage"' in text, f"FAQ schema missing: {filename}"
    for needle in needles:
        assert needle in text, f"{needle!r} missing: {filename}"

for tower in ("a1", "a2", "a3"):
    path = ROOT / f"mat-bang-smart-city/lumiere-evergreen/{tower}/index.html"
    assert path.exists(), f"missing Lumiere tower page: {tower}"
    text = path.read_text(encoding="utf-8")
    assert "index,follow,max-image-preview:large" in text
    assert f"/mat-bang-smart-city/lumiere-evergreen/{tower}/" in text
    assert "lumière evergreen" in text.lower()

prepare = (ROOT / "tools/prepare_portal_v2.py").read_text(encoding="utf-8")
for filename in PAGES:
    assert f'"{filename}"' in prepare, f"staging missing Lumiere SEO page: {filename}"

print("Lumiere SEO cluster checks passed: deep hub + 2 intent pages + 3 tower pages")
