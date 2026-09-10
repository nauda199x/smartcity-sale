#!/usr/bin/env python3
from pathlib import Path

from build_precinct_masterplans import PROJECTS

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://timmuasmartcity.com"

hub = (ROOT / "mat-bang-smart-city" / "phan-khu" / "index.html").read_text(encoding="utf-8")
assert "/tong-the/" not in hub, "hub still points to separate tong-the pages"

for project in PROJECTS:
    slug = project["slug"]
    main = ROOT / "mat-bang-smart-city" / slug / "index.html"
    redirect = ROOT / "mat-bang-smart-city" / slug / "tong-the" / "index.html"
    assert main.is_file(), f"missing main floorplan page: {slug}"
    assert redirect.is_file(), f"missing legacy redirect: {slug}"

    text = main.read_text(encoding="utf-8")
    assert 'id="mat-bang-tong-the"' in text, f"masterplan not integrated into {slug}"
    assert project["image"] in text, f"masterplan image missing in {slug}"
    assert "PRECINCT_MASTERPLAN_INTEGRATED_START" in text, f"integration marker missing in {slug}"
    assert "precinct-masterplan.css" in text, f"masterplan css missing in {slug}"
    assert f'https://timmuasmartcity.com/mat-bang-smart-city/{slug}/' in text, f"main canonical missing in {slug}"
    for tower in project["towers"]:
        assert f'/mat-bang-smart-city/{slug}/{tower}/' in text, f"tower link {tower} missing in {slug}"

    legacy = redirect.read_text(encoding="utf-8")
    assert 'content="noindex,follow"' in legacy, f"legacy tong-the must be noindex: {slug}"
    assert f'<link rel="canonical" href="{SITE}/mat-bang-smart-city/{slug}/">' in legacy, f"legacy canonical wrong: {slug}"
    assert f'/mat-bang-smart-city/{slug}/#mat-bang-tong-the' in legacy, f"legacy redirect target wrong: {slug}"
    assert f'href="/mat-bang-smart-city/{slug}/#mat-bang-tong-the"' in hub, f"hub main-page link missing: {slug}"

print(f"precinct masterplan integration passed: {len(PROJECTS)} combined pages + legacy redirects")
