#!/usr/bin/env python3
from pathlib import Path

from build_precinct_masterplans import PROJECTS
from integrate_precinct_masterplans import tower_display

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://timmuasmartcity.com"

hub = (ROOT / "mat-bang-smart-city" / "phan-khu" / "index.html").read_text(encoding="utf-8")
assert "/tong-the/" not in hub, "hub still points to separate tong-the pages"

tower_count = 0
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
    assert "precinct-masterplan.css?v=20260910-4" in text, f"masterplan css version missing in {slug}"
    assert f'https://timmuasmartcity.com/mat-bang-smart-city/{slug}/' in text, f"main canonical missing in {slug}"

    for tower in project["towers"]:
        tower_count += 1
        tower_url = f'/mat-bang-smart-city/{slug}/{tower}/'
        assert tower_url in text, f"tower link {tower} missing in {slug}"
        assert text.count(tower_url) >= 2, f"tower {tower} should be linked from quick nav and crawlable table in {slug}"

        tower_path = ROOT / "mat-bang-smart-city" / slug / tower / "index.html"
        assert tower_path.is_file(), f"missing tower floorplan page: {slug}/{tower}"
        tower_text = tower_path.read_text(encoding="utf-8")
        display = tower_display(project, tower)
        assert "TOWER_FLOORPLAN_INTENT_START" in tower_text, f"tower intent marker missing: {slug}/{tower}"
        assert 'id="tra-cuu-mat-bang-toa"' in tower_text, f"tower intent section missing: {slug}/{tower}"
        assert 'id="mat-bang-hd"' in tower_text, f"HD floorplan anchor missing: {slug}/{tower}"
        assert "tower-floorplan-intent.css?v=20260910-1" in tower_text, f"tower CSS missing: {slug}/{tower}"
        assert "precinct-masterplan.css?v=20260910-4" in tower_text, f"shared precinct CSS missing: {slug}/{tower}"
        assert f'Mặt bằng tòa {display} {project["name"]}: bản vẽ HD và tòa cùng phân khu' in tower_text, f"tower search-intent heading missing: {slug}/{tower}"
        assert f'href="/mat-bang-smart-city/{slug}/"' in tower_text, f"parent floorplan link missing: {slug}/{tower}"
        assert f'href="/phan-khu-smart-city/{slug}/"' in tower_text, f"project profile link missing: {slug}/{tower}"
        assert f'href="{tower_url}" aria-current="page"' in tower_text, f"current tower state missing: {slug}/{tower}"
        for sibling in project["towers"]:
            sibling_url = f'/mat-bang-smart-city/{slug}/{sibling}/'
            assert sibling_url in tower_text, f"sibling tower link {sibling} missing from {slug}/{tower}"

    legacy = redirect.read_text(encoding="utf-8")
    assert 'content="noindex,follow"' in legacy, f"legacy tong-the must be noindex: {slug}"
    assert f'<link rel="canonical" href="{SITE}/mat-bang-smart-city/{slug}/">' in legacy, f"legacy canonical wrong: {slug}"
    assert f'/mat-bang-smart-city/{slug}/#mat-bang-tong-the' in legacy, f"legacy redirect target wrong: {slug}"
    assert f'href="/mat-bang-smart-city/{slug}/#mat-bang-tong-the"' in hub, f"hub main-page link missing: {slug}"

assert tower_count >= 49, f"unexpectedly low tower coverage: {tower_count}"
print(
    f"floorplan SEO intent integration passed: {len(PROJECTS)} precinct pages + "
    f"{tower_count} tower pages + crawlable sibling links + legacy redirects"
)
