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
CSS = '<link rel="stylesheet" href="/assets/css/precinct-masterplan.css?v=20260910-2">'


def label_tower(slug: str) -> str:
    if slug.startswith("s") and "-" in slug:
        a, b = slug.split("-", 1)
        return f"{a.upper()}.{b}"
    return slug.replace("-", " ").upper()


def masterplan_block(project: dict) -> str:
    slug = project["slug"]
    name = project["name"]
    tower_links = "".join(
        f'<a class="precinct-tower" href="/mat-bang-smart-city/{slug}/{tower}/">{escape(label_tower(tower))}</a>'
        for tower in project["towers"]
    )
    return f'''{START}
<section class="section precinct-masterplan-inline" id="mat-bang-tong-the">
  <div class="container">
    <div class="section-head">
      <div><p class="eyebrow section-kicker">Mặt bằng tổng thể + mặt bằng tòa</p><h2>Mặt bằng tổng thể {escape(name)}</h2></div>
      <p>Xem vị trí các tòa trên cùng trang với mặt bằng chi tiết bên dưới để đối chiếu nhanh, không phải chuyển qua một trang tổng thể riêng.</p>
    </div>
    <figure class="precinct-plan">
      <a class="precinct-plan__media" href="{project['image']}" target="_blank" rel="noopener" aria-label="Mở ảnh lớn mặt bằng tổng thể {escape(name)}">
        <img src="{project['image']}" alt="Mặt bằng tổng thể và bối cảnh {escape(name)}" loading="eager" decoding="async">
      </a>
      <figcaption>{escape(project['image_label'])}</figcaption>
    </figure>
    <div class="precinct-towers" aria-label="Chọn mặt bằng từng tòa">{tower_links}</div>
    <div class="notice"><strong>Cách xem nhanh:</strong> dùng ảnh tổng thể để xác định vị trí tòa, sau đó kéo xuống ngay bên dưới để xem mặt bằng chi tiết từng tòa; cần soi kỹ thì bấm mã tòa để mở hồ sơ HD riêng.</div>
  </div>
</section>
{END}'''


def ensure_css(text: str) -> str:
    if "precinct-masterplan.css" in text:
        return text
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
    print(f"integrated precinct masterplans into {len(PROJECTS)} main floorplan pages")


if __name__ == "__main__":
    main()
