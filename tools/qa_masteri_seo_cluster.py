#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "https://timmuasmartcity.com"

hub_path = ROOT / "mat-bang-smart-city/masteri-west-heights/index.html"
assert hub_path.exists(), "missing Masteri floorplan hub"
hub = hub_path.read_text(encoding="utf-8")
assert '<meta name="robots" content="index,follow,max-image-preview:large">' in hub
assert f'<link rel="canonical" href="{DOMAIN}/mat-bang-smart-city/masteri-west-heights/">' in hub
assert '"@type":"CollectionPage"' in hub
assert '"@type":"FAQPage"' in hub
for tower in ("west-a", "west-b", "west-c", "west-d"):
    assert f'href="/mat-bang-smart-city/masteri-west-heights/{tower}/"' in hub, f"hub missing {tower} link"
for child in (
    "mat-bang-can-ho-masteri-west-heights-theo-loai.html",
    "cach-chon-toa-masteri-west-heights-west-a-b-c-d.html",
):
    assert f'href="/{child}"' in hub, f"hub missing child link: {child}"
assert "L3–19" in hub and "L21–34" in hub and "L35–37" in hub
assert "Studio" in hub and "1PN+" in hub and "2PN+" in hub and "3PN" in hub
assert "West B" in hub and "West C" in hub and "West D" in hub

PAGES = {
    "mat-bang-can-ho-masteri-west-heights-theo-loai.html": [
        "28,6–35,2",
        "41,8–47,6",
        "54,0–61,8",
        "73,8–80,1",
        "/mat-bang-smart-city/masteri-west-heights/",
    ],
    "cach-chon-toa-masteri-west-heights-west-a-b-c-d.html": [
        "West A",
        "West B",
        "West C",
        "West D",
        "Chữ U",
        "Chữ Z",
        "/mat-bang-smart-city/masteri-west-heights/",
    ],
}

for filename, needles in PAGES.items():
    path = ROOT / filename
    assert path.exists(), f"missing Masteri SEO page: {filename}"
    text = path.read_text(encoding="utf-8")
    assert 'name="robots" content="index,follow,max-image-preview:large"' in text, f"robots missing: {filename}"
    assert f'<link rel="canonical" href="{DOMAIN}/{filename}">' in text, f"self canonical missing: {filename}"
    assert '"@type":"Article"' in text, f"Article schema missing: {filename}"
    assert '"@type":"BreadcrumbList"' in text, f"Breadcrumb schema missing: {filename}"
    assert '"@type":"FAQPage"' in text, f"FAQ schema missing: {filename}"
    for needle in needles:
        assert needle in text, f"{needle!r} missing: {filename}"

for tower in ("west-a", "west-b", "west-c", "west-d"):
    path = ROOT / f"mat-bang-smart-city/masteri-west-heights/{tower}/index.html"
    assert path.exists(), f"missing Masteri tower page: {tower}"
    text = path.read_text(encoding="utf-8")
    assert "index,follow,max-image-preview:large" in text
    assert f"/mat-bang-smart-city/masteri-west-heights/{tower}/" in text
    assert "masteri-west-heights" in text.lower()

print("Masteri SEO cluster checks passed: deep hub + 2 intent pages + 4 tower pages")
