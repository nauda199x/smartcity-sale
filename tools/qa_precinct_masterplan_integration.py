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
    assert 'id="tra-cuu-mat-bang-theo-toa"' in text, f"SEO intent panel missing in {slug}"
    assert 'class="precinct-index-table"' in text, f"crawlable tower table missing in {slug}"
    assert f'Mặt bằng {project["name"]}: tổng thể và từng tòa' in text, f"search-intent heading missing in {slug}"
    assert project["image"] in text, f"masterplan image missing in {slug}"
    assert "PRECINCT_MASTERPLAN_INTEGRATED_START" in text, f"integration marker missing in {slug}"
    assert "precinct-masterplan.css?v=20260910-3" in text, f"masterplan css version missing in {slug}"
    assert f'https://timmuasmartcity.com/mat-bang-smart-city/{slug}/' in text, f"main canonical missing in {slug}"
    for tower in project["towers"]:
        tower_url = f'/mat-bang-smart-city/{slug}/{tower}/'
        assert tower_url in text, f"tower link {tower} missing in {slug}"
        assert text.count(tower_url) >= 2, f"tower {tower} should be linked from quick nav and crawlable table in {slug}"

    legacy = redirect.read_text(encoding="utf-8")
    assert 'content="noindex,follow"' in legacy, f"legacy tong-the must be noindex: {slug}"
    assert f'<link rel="canonical" href="{SITE}/mat-bang-smart-city/{slug}/">' in legacy, f"legacy canonical wrong: {slug}"
    assert f'/mat-bang-smart-city/{slug}/#mat-bang-tong-the' in legacy, f"legacy redirect target wrong: {slug}"
    assert f'href="/mat-bang-smart-city/{slug}/#mat-bang-tong-the"' in hub, f"hub main-page link missing: {slug}"

print(f"precinct SEO intent integration passed: {len(PROJECTS)} combined pages + crawlable tower tables + legacy redirects")
