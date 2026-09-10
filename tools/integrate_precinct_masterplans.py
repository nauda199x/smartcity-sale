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
CSS = '<link rel="stylesheet" href="/assets/css/precinct-masterplan.css?v=20260910-3">'

TOWER_NAMES = {
    "lumiere-evergreen": {
        "a1": "A1 · The Aqua",
        "a2": "A2 · The Atmos",
        "a3": "A3 · The Aura",
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


def ensure_css(text: str) -> str:
    if "precinct-masterplan.css" in text:
        return re.sub(
            r'<link rel="stylesheet" href="/assets/css/precinct-masterplan\.css\?v=[^"]+">',
            CSS,
            text,
            count=1,
        )
    theme = re.search(r'<link[^>]+href=["\']/assets/css/site-theme\.css[^>]*>', text)
    if theme:
        return text[:theme.start()] + CSS + text[theme.start():]
    return text.replace("</head>", CSS + "</head>", 1)


def inject_main_page(project: dict) -> None:
    path = ROOT / "mat-bang-smart-city" / project["slug"] / "index.html"
    if not path.is_file():
        raise FileNotFoundError(path)
    text = path.read_text(encoding="utf-8")
    text = re.sub(re.escape(START) + r".*?" + re.escape(END), "", text, flags=re.S)
    text = ensure_css(text)
    block = masterplan_block(project)

    facts = re.search(r'(<section\b[^>]*class=["\'][^"\']*\bfacts-panel\b[^"\']*["\'][^>]*>.*?</section>)', text, flags=re.S | re.I)
    if facts:
        text = text[:facts.end()] + block + text[facts.end():]
    else:
        first_section = re.search(r'<section\b[^>]*class=["\'][^"\']*\bsection\b', text, flags=re.I)
        if first_section:
            text = text[:first_section.start()] + block + text[first_section.start():]
        else:
            text = text.replace("</main>", block + "</main>", 1)
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
    for project in PROJECTS:
        inject_main_page(project)
        rewrite_legacy_precinct_pages(project)
    update_hub()
    print(f"integrated SEO-first precinct masterplans into {len(PROJECTS)} main floorplan pages")


if __name__ == "__main__":
    main()
