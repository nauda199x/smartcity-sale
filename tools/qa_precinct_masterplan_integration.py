#!/usr/bin/env python3
from pathlib import Path
import re

from build_precinct_masterplans import PROJECTS
from integrate_precinct_masterplans import tower_display

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://timmuasmartcity.com"

BANNED_VISIBLE_PHRASES = (
    "Danh mục crawlable",
    "URL riêng",
    "công cụ tìm kiếm",
    "quay lại Google",
    "SEO tốt",
    "website giữ mô tả trung lập",
    "luồng tra cứu",
    "Dữ liệu riêng của cụm",
    "Trang này không chỉ để mở ảnh kỹ thuật",
)

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
    for phrase in BANNED_VISIBLE_PHRASES:
        assert phrase not in text, f"technical/AI copy visible on precinct page {slug}: {phrase}"

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
        assert f'Mặt bằng {display} {project["name"]}: sơ đồ tầng HD và các loại căn hộ' in tower_text, f"human tower heading missing: {slug}/{tower}"
        assert f'href="/mat-bang-smart-city/{slug}/"' in tower_text, f"parent floorplan link missing: {slug}/{tower}"
        assert f'href="/phan-khu-smart-city/{slug}/"' in tower_text, f"project profile link missing: {slug}/{tower}"
        assert f'href="{tower_url}" aria-current="page"' in tower_text, f"current tower state missing: {slug}/{tower}"
        for sibling in project["towers"]:
            sibling_url = f'/mat-bang-smart-city/{slug}/{sibling}/'
            assert sibling_url in tower_text, f"sibling tower link {sibling} missing from {slug}/{tower}"

        assert "TOWER_EDITORIAL_START" in tower_text, f"rich editorial marker missing: {slug}/{tower}"
        assert "tower-editorial.css?v=20260910-2" in tower_text, f"editorial CSS missing: {slug}/{tower}"
        assert f'Mặt bằng {display} {project["name"]}: thông tin cần biết trước khi mua hoặc thuê' in tower_text, f"editorial H2 missing: {slug}/{tower}"
        assert f'FAQ về mặt bằng {display}' in tower_text, f"tower FAQ missing: {slug}/{tower}"
        assert tower_text.count("<details") >= 4, f"tower FAQ too thin: {slug}/{tower}"
        assert '/mua-ban-smart-city/' in tower_text and '/cho-thue-smart-city/' in tower_text, f"transaction links missing: {slug}/{tower}"
        for phrase in BANNED_VISIBLE_PHRASES:
            assert phrase not in tower_text, f"technical/AI copy visible on {slug}/{tower}: {phrase}"

        editorial = re.search(r'<!-- TOWER_EDITORIAL_START -->(.*?)<!-- TOWER_EDITORIAL_END -->', tower_text, flags=re.S)
        assert editorial, f"cannot isolate editorial block: {slug}/{tower}"
        plain = re.sub(r'<[^>]+>', ' ', editorial.group(1))
        word_count = len(re.findall(r'\b\w+\b', plain, flags=re.UNICODE))
        assert word_count >= 650, f"editorial content still thin ({word_count} words): {slug}/{tower}"
        assert plain.count(display) >= 5, f"tower-specific copy too generic: {slug}/{tower}"

    legacy = redirect.read_text(encoding="utf-8")
    assert 'content="noindex,follow"' in legacy, f"legacy tong-the must be noindex: {slug}"
    assert f'<link rel="canonical" href="{SITE}/mat-bang-smart-city/{slug}/">' in legacy, f"legacy canonical wrong: {slug}"
    assert f'/mat-bang-smart-city/{slug}/#mat-bang-tong-the' in legacy, f"legacy redirect target wrong: {slug}"
    assert f'href="/mat-bang-smart-city/{slug}/#mat-bang-tong-the"' in hub, f"hub main-page link missing: {slug}"

assert tower_count >= 49, f"unexpectedly low tower coverage: {tower_count}"
print(
    f"floorplan SEO integration passed: {len(PROJECTS)} precinct pages + {tower_count} tower pages + "
    "natural editorial content (>=650 words/page) + AI/technical copy lint + crawlable sibling links"
)
