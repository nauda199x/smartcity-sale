#!/usr/bin/env python3
from __future__ import annotations

from html import escape
from pathlib import Path
import re

from build_precinct_masterplans import PROJECTS

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://timmuasmartcity.com"
START = "<!-- PRECINCT_MASTERPLAN_INTEGRATED_START -->"
END = "<!-- PRECINCT_MASTERPLAN_INTEGRATED_END -->"
TOWER_START = "<!-- TOWER_FLOORPLAN_INTENT_START -->"
TOWER_END = "<!-- TOWER_FLOORPLAN_INTENT_END -->"
CSS = '<link rel="stylesheet" href="/assets/css/precinct-masterplan.css?v=20260910-4">'
TOWER_CSS = '<link rel="stylesheet" href="/assets/css/tower-floorplan-intent.css?v=20260910-1">'

TOWER_NAMES = {
    "lumiere-evergreen": {
        "a1": "A1 · The Aqua",
        "a2": "A2 · The Atmos",
        "a3": "A3 · The Aura",
    },
    "masteri-west-heights": {
        "west-a": "West A",
        "west-b": "West B",
        "west-c": "West C",
        "west-d": "West D",
    },
    "canopy": {
        "tc1": "TC1 · The Canopy Vista",
        "tc2": "TC2 · The Canopy Summit",
        "tc3": "TC3 · The Canopy Harmony",
    },
}


def label_tower(slug: str) -> str:
    if slug.startswith("s") and "-" in slug:
        a, b = slug.split("-", 1)
        return f"{a.upper()}.{b}"
    return slug.replace("-", " ").upper()


def tower_display(project: dict, tower: str) -> str:
    return TOWER_NAMES.get(project["slug"], {}).get(tower, label_tower(tower))


def tower_index_rows(project: dict) -> str:
    slug = project["slug"]
    name = project["name"]
    rows = []
    for tower in project["towers"]:
        display = tower_display(project, tower)
        url = f"/mat-bang-smart-city/{slug}/{tower}/"
        rows.append(
            "<tr>"
            f"<td><strong>{escape(display)}</strong></td>"
            f"<td>Mặt bằng {escape(display)} {escape(name)}</td>"
            "<td>Sơ đồ tầng, lõi thang, trục căn và ảnh HD theo đúng tòa</td>"
            f'<td><a href="{url}" aria-label="Xem mặt bằng {escape(display)} {escape(name)}">Xem mặt bằng →</a></td>'
            "</tr>"
        )
    return "".join(rows)


def fact_chips(project: dict) -> str:
    return "".join(f"<span>{escape(fact)}</span>" for fact in project.get("facts", []))


def masterplan_block(project: dict) -> str:
    slug = project["slug"]
    name = project["name"]
    tower_links = "".join(
        f'<a class="precinct-tower" href="/mat-bang-smart-city/{slug}/{tower}/">{escape(tower_display(project, tower))}</a>'
        for tower in project["towers"]
    )
    rows = tower_index_rows(project)
    chips = fact_chips(project)
    return f'''{START}
<section class="section precinct-masterplan-inline" id="mat-bang-tong-the" aria-labelledby="mat-bang-tong-the-title">
  <div class="container">
    <div class="section-head precinct-masterplan-head">
      <div><p class="eyebrow section-kicker">Tra cứu mặt bằng · tổng thể · từng tòa</p><h2 id="mat-bang-tong-the-title">Mặt bằng {escape(name)}: tổng thể và từng tòa</h2></div>
      <p>Đi từ sơ đồ phân khu tới đúng tòa, rồi mở mặt bằng HD để đọc lõi thang, trục căn và mã căn. Cấu trúc này giúp người xem tìm đúng dữ liệu mà không phải đoán từ một ảnh tổng.</p>
    </div>

    <div class="precinct-intent-grid">
      <figure class="precinct-plan">
        <a class="precinct-plan__media" href="{project['image']}" target="_blank" rel="noopener" aria-label="Mở ảnh lớn mặt bằng tổng thể {escape(name)}">
          <img src="{project['image']}" alt="Mặt bằng tổng thể và bối cảnh {escape(name)}" loading="eager" decoding="async">
        </a>
        <figcaption>{escape(project['image_label'])}</figcaption>
      </figure>

      <aside class="precinct-intent-panel" id="tra-cuu-mat-bang-theo-toa">
        <p class="eyebrow section-kicker">Tra cứu nhanh</p>
        <h3>Chọn đúng tòa trước khi đọc mã căn</h3>
        <p>{escape(project['lead'])}</p>
        <div class="precinct-fact-chips" aria-label="Thông tin nhanh {escape(name)}">{chips}</div>
        <div class="precinct-towers" aria-label="Chọn mặt bằng từng tòa">{tower_links}</div>
      </aside>
    </div>

    <div class="precinct-index" aria-labelledby="danh-muc-mat-bang-title">
      <div class="precinct-index__head">
        <div><p class="eyebrow section-kicker">Danh mục crawlable</p><h3 id="danh-muc-mat-bang-title">Mặt bằng {escape(name)} theo từng tòa</h3></div>
        <p>Mỗi tòa có URL riêng để Google và người dùng đi thẳng tới đúng hồ sơ kỹ thuật, thay vì gom toàn bộ bản vẽ vào một ảnh hoặc một trang chung.</p>
      </div>
      <div class="precinct-index__scroll">
        <table class="precinct-index-table" aria-label="Danh sách mặt bằng từng tòa {escape(name)}">
          <thead><tr><th>Tòa</th><th>Nội dung</th><th>Dùng để kiểm tra</th><th>Hồ sơ</th></tr></thead>
          <tbody>{rows}</tbody>
        </table>
      </div>
    </div>

    <div class="precinct-search-guide">
      <div><strong>1 · Chọn phân khu/tòa</strong><span>Dùng ảnh tổng thể để xác định đúng cụm và đúng mã tòa.</span></div>
      <div><strong>2 · Mở mặt bằng HD</strong><span>Zoom sơ đồ đúng tòa để đọc lõi thang, hành lang, trục góc và nhóm căn.</span></div>
      <div><strong>3 · Đối chiếu căn thực tế</strong><span>Sau khi chốt trục mới so diện tích, hướng/view, khoảng chắn và tin đang giao dịch.</span></div>
    </div>
    <div class="notice precinct-seo-note"><strong>Lưu ý dữ liệu:</strong> website chỉ ghi các thông số đã có trong hồ sơ đang lưu. Khi chưa có bản tổng thể hoặc dữ kiện đủ tin cậy, trang giữ mô tả trung lập và dẫn sang đúng mặt bằng tòa thay vì suy đoán.</div>
  </div>
</section>
{END}'''


def sibling_tower_links(project: dict, current: str) -> str:
    slug = project["slug"]
    links = []
    for tower in project["towers"]:
        display = tower_display(project, tower)
        url = f"/mat-bang-smart-city/{slug}/{tower}/"
        current_attr = ' aria-current="page"' if tower == current else ""
        current_class = " is-current" if tower == current else ""
        links.append(
            f'<a class="tower-sibling{current_class}" href="{url}"{current_attr}>{escape(display)}</a>'
        )
    return "".join(links)


def tower_intent_block(project: dict, tower: str) -> str:
    slug = project["slug"]
    name = project["name"]
    display = tower_display(project, tower)
    siblings = sibling_tower_links(project, tower)
    parent_url = f"/mat-bang-smart-city/{slug}/"
    project_url = f"/phan-khu-smart-city/{slug}/"
    return f'''{TOWER_START}
<section class="section tower-intent-inline" id="tra-cuu-mat-bang-toa" aria-labelledby="tower-intent-title">
  <div class="container">
    <div class="section-head tower-intent-head">
      <div>
        <p class="eyebrow section-kicker">Mặt bằng tòa · hồ sơ HD · liên kết phân khu</p>
        <h2 id="tower-intent-title">Mặt bằng tòa {escape(display)} {escape(name)}: bản vẽ HD và tòa cùng phân khu</h2>
      </div>
      <p>Trang này là hồ sơ riêng của {escape(display)}. Dùng đúng mặt bằng của tòa trước khi kết luận mã căn, vị trí lõi thang, trục góc, hướng/view hoặc so giá với căn khác.</p>
    </div>

    <div class="tower-intent-grid">
      <article class="tower-intent-current">
        <p class="eyebrow section-kicker">Bạn đang xem</p>
        <h3>{escape(display)}</h3>
        <p>Thuộc <strong>{escape(name)}</strong>. URL riêng của hồ sơ này giúp người dùng và công cụ tìm kiếm không phải suy tòa từ một trang mặt bằng tổng.</p>
        <div class="tower-intent-actions">
          <a class="btn btn-primary" href="{parent_url}#mat-bang-tong-the">Xem mặt bằng tổng {escape(name)}</a>
          <a class="btn" href="{project_url}">Xem hồ sơ phân khu</a>
        </div>
      </article>
      <aside class="tower-intent-rules">
        <p class="eyebrow section-kicker">Cách đọc đúng</p>
        <ol>
          <li><strong>Đúng tòa:</strong> xác nhận {escape(display)} trước khi đọc mã căn.</li>
          <li><strong>Đúng bản vẽ:</strong> phóng to ảnh HD để đọc lõi thang, hành lang và trục căn.</li>
          <li><strong>Đúng dữ kiện:</strong> chỉ kết luận hướng/view khi sơ đồ hoặc hồ sơ có đủ thông tin để đối chiếu.</li>
        </ol>
      </aside>
    </div>

    <div class="tower-sibling-panel">
      <div class="tower-sibling-panel__head">
        <div><p class="eyebrow section-kicker">Mặt bằng cùng phân khu</p><h3>Các tòa khác trong {escape(name)}</h3></div>
        <p>Chuyển ngang giữa các tòa để so đúng mặt bằng thay vì quay lại Google hoặc dùng nhầm sơ đồ của tòa khác.</p>
      </div>
      <nav class="tower-sibling-nav" aria-label="Mặt bằng các tòa thuộc {escape(name)}">{siblings}</nav>
    </div>

    <div class="tower-search-guide">
      <a href="{parent_url}"><strong>1 · Về phân khu</strong><span>Xem tổng thể và vị trí tương quan các tòa.</span></a>
      <a href="#mat-bang-hd"><strong>2 · Soi bản vẽ HD</strong><span>Zoom để đọc đúng lõi thang và trục căn.</span></a>
      <a href="/giao-dich-smart-city/"><strong>3 · Xem căn giao dịch</strong><span>Sau khi chốt tòa/trục mới so căn đang bán hoặc cho thuê.</span></a>
    </div>
    <p class="tower-data-note"><strong>Nguyên tắc dữ liệu:</strong> chỉ dùng thông số có trong hồ sơ hiện có; không tự suy hướng, view, mật độ hoặc diện tích khi chưa đủ căn cứ.</p>
  </div>
</section>
{TOWER_END}'''


def replace_or_add_stylesheet(text: str, filename: str, tag: str) -> str:
    pattern = rf'<link[^>]+href=["\']/assets/css/{re.escape(filename)}\?v=[^"\']+["\'][^>]*>'
    if filename in text:
        return re.sub(pattern, tag, text, count=1)
    theme = re.search(r'<link[^>]+href=["\']/assets/css/site-theme\.css[^>]*>', text)
    if theme:
        return text[:theme.start()] + tag + text[theme.start():]
    return text.replace("</head>", tag + "</head>", 1)


def ensure_css(text: str) -> str:
    return replace_or_add_stylesheet(text, "precinct-masterplan.css", CSS)


def ensure_tower_css(text: str) -> str:
    return replace_or_add_stylesheet(text, "tower-floorplan-intent.css", TOWER_CSS)


def ensure_hd_anchor(text: str) -> str:
    if 'id="mat-bang-hd"' in text or "id='mat-bang-hd'" in text:
        return text
    match = re.search(
        r'<section\b[^>]*class=["\'][^"\']*\bfloorplan-hd-section\b[^"\']*["\'][^>]*>',
        text,
        flags=re.I,
    )
    if not match:
        return text
    tag = match.group(0)
    if re.search(r'\bid\s*=', tag, flags=re.I):
        return text
    anchored = tag[:-1] + ' id="mat-bang-hd">'
    return text[:match.start()] + anchored + text[match.end():]


def insert_after_preferred_section(text: str, block: str) -> str:
    for class_name in ("facts-panel", "floorplan-direct-note"):
        match = re.search(
            rf'(<section\b[^>]*class=["\'][^"\']*\b{class_name}\b[^"\']*["\'][^>]*>.*?</section>)',
            text,
            flags=re.S | re.I,
        )
        if match:
            return text[:match.end()] + block + text[match.end():]
    first_section = re.search(r'<section\b[^>]*class=["\'][^"\']*\bsection\b', text, flags=re.I)
    if first_section:
        return text[:first_section.start()] + block + text[first_section.start():]
    return text.replace("</main>", block + "</main>", 1)


def inject_main_page(project: dict) -> None:
    path = ROOT / "mat-bang-smart-city" / project["slug"] / "index.html"
    if not path.is_file():
        raise FileNotFoundError(path)
    text = path.read_text(encoding="utf-8")
    text = re.sub(re.escape(START) + r".*?" + re.escape(END), "", text, flags=re.S)
    text = ensure_css(text)
    text = insert_after_preferred_section(text, masterplan_block(project))
    path.write_text(text, encoding="utf-8")


def inject_tower_page(project: dict, tower: str) -> None:
    path = ROOT / "mat-bang-smart-city" / project["slug"] / tower / "index.html"
    if not path.is_file():
        raise FileNotFoundError(path)
    text = path.read_text(encoding="utf-8")
    text = re.sub(re.escape(TOWER_START) + r".*?" + re.escape(TOWER_END), "", text, flags=re.S)
    text = ensure_css(text)
    text = ensure_tower_css(text)
    text = ensure_hd_anchor(text)
    text = insert_after_preferred_section(text, tower_intent_block(project, tower))
    path.write_text(text, encoding="utf-8")


def redirect_page(project: dict) -> str:
    slug = project["slug"]
    name = project["name"]
    destination = f"/mat-bang-smart-city/{slug}/#mat-bang-tong-the"
    canonical = f"{SITE}/mat-bang-smart-city/{slug}/"
    return f'''<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="refresh" content="0;url={destination}"><meta name="robots" content="noindex,follow"><link rel="canonical" href="{canonical}"><title>Mặt bằng {escape(name)}</title></head><body><p>Mặt bằng tổng thể đã được gộp vào <a href="{destination}">trang mặt bằng {escape(name)}</a> để xem cùng mặt bằng từng tòa.</p></body></html>'''


def rewrite_legacy_precinct_pages(project: dict) -> None:
    target = ROOT / "mat-bang-smart-city" / project["slug"] / "tong-the" / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(redirect_page(project), encoding="utf-8")


def update_hub() -> None:
    hub = ROOT / "mat-bang-smart-city" / "phan-khu" / "index.html"
    if not hub.is_file():
        raise FileNotFoundError(hub)
    text = hub.read_text(encoding="utf-8")
    for project in PROJECTS:
        slug = project["slug"]
        text = text.replace(
            f'href="/mat-bang-smart-city/{slug}/tong-the/"',
            f'href="/mat-bang-smart-city/{slug}/#mat-bang-tong-the"',
        )
    text = text.replace("Xem mặt bằng phân khu →", "Xem tổng thể + từng tòa →")
    text = text.replace(
        "Mỗi hồ sơ có sơ đồ/ảnh tổng thể phù hợp nhất đang có, bảng tòa, đặc điểm layout và liên kết thẳng tới mặt bằng HD từng tòa.",
        "Mỗi phân khu mở thẳng trang mặt bằng chính: ảnh tổng thể nằm ngay phía trên thư viện mặt bằng từng tòa để khách đối chiếu trên một màn hình.",
    )
    hub.write_text(text, encoding="utf-8")


def main() -> None:
    tower_count = 0
    for project in PROJECTS:
        inject_main_page(project)
        rewrite_legacy_precinct_pages(project)
        for tower in project["towers"]:
            inject_tower_page(project, tower)
            tower_count += 1
    update_hub()
    print(
        f"integrated SEO-first floorplan intent into {len(PROJECTS)} precinct pages "
        f"and {tower_count} tower pages"
    )


if __name__ == "__main__":
    main()
