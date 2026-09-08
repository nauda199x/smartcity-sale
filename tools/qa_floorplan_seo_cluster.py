#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = {
    "mat-bang-can-ho-vinhomes-smart-city.html": [
        "Mặt bằng căn hộ Vinhomes Smart City",
        "mat-bang-can-ho-2pn-vinhomes-smart-city.html",
        "mat-bang-can-ho-1pn-1-vinhomes-smart-city.html",
        "cach-doc-mat-bang-tang-ma-can-vinhomes-smart-city.html",
    ],
    "mat-bang-can-ho-2pn-vinhomes-smart-city.html": [
        "2PN 1WC",
        "2PN 2WC",
        "2PN+1",
        "/mat-bang-smart-city/",
    ],
    "mat-bang-can-ho-1pn-1-vinhomes-smart-city.html": [
        "1PN+1",
        "không gian +1",
        "/mat-bang-smart-city/",
    ],
    "cach-doc-mat-bang-tang-ma-can-vinhomes-smart-city.html": [
        "CH01",
        "CH02",
        "đúng tòa",
        "đúng nhóm tầng",
    ],
    "mat-bang-the-sapphire-vinhomes-smart-city.html": [
        "Sapphire 1",
        "Sapphire 2",
        "Sapphire 3",
        "Sapphire 4",
        "15 tòa",
    ],
}

for filename, needles in PAGES.items():
    path = ROOT / filename
    assert path.exists(), f"missing SEO floorplan page: {filename}"
    text = path.read_text(encoding="utf-8")
    assert 'name="robots" content="index,follow,max-image-preview:large"' in text, f"robots missing: {filename}"
    assert f'https://timmuasmartcity.com/{filename}' in text, f"self canonical missing: {filename}"
    assert '"@type":"Article"' in text, f"Article schema missing: {filename}"
    assert '"@type":"BreadcrumbList"' in text, f"Breadcrumb schema missing: {filename}"
    assert '"@type":"FAQPage"' in text, f"FAQ schema missing: {filename}"
    assert "/mat-bang-smart-city/" in text, f"floorplan hub link missing: {filename}"
    for needle in needles:
        assert needle in text, f"{needle!r} missing: {filename}"

hub = (ROOT / "cam-nang.html").read_text(encoding="utf-8")
for filename in PAGES:
    assert f'href="/{filename}"' in hub, f"guide hub does not link to {filename}"

sapphire = (ROOT / "mat-bang-the-sapphire-vinhomes-smart-city.html").read_text(encoding="utf-8")
assert "S4.01" in sapphire and "30 căn/sàn" in sapphire
assert "S4.02" in sapphire and "S4.03" in sapphire and "22 căn/sàn" in sapphire
# Avoid encoding the disputed L-vs-Z label for S4.02/S4.03 as a factual claim.
assert "S4.02 chữ L" not in sapphire and "S4.02 chữ Z" not in sapphire

print(f"floorplan SEO cluster checks passed: {len(PAGES)} deep pages + hub links")
