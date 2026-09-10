#!/usr/bin/env python3
"""Stage high-intent editorial SEO pages and strengthen their crawl graph.

This runs after prepare_portal_v2.py. Source articles live under
seo/traffic-content/ so editorial content is reviewable without duplicating the
production HTML tree. The normal SEO builder later discovers these pages and
adds them to sitemap-pages.xml.
"""
from __future__ import annotations

from pathlib import Path
import shutil

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
SOURCE = ROOT / "seo" / "traffic-content"

ARTICLES = {
    "gia-thue-vinhomes-smart-city-2026.html": "Giá thuê Vinhomes Smart City 2026",
    "phi-dich-vu-vinhomes-smart-city.html": "Phí dịch vụ Vinhomes Smart City",
    "co-nen-mua-vinhomes-smart-city-2026.html": "Có nên mua Vinhomes Smart City 2026?",
    "so-sanh-masteri-west-heights-lumiere-evergreen.html": "Masteri West Heights vs LUMIÈRE Evergreen",
    "so-sanh-the-sola-park-the-victoria.html": "The Sola Park vs The Victoria",
    "shop-chan-de-vinhomes-smart-city.html": "Shop chân đế Vinhomes Smart City",
    "mua-can-ho-1pn-1-vinhomes-smart-city.html": "Mua căn 1PN+1 Vinhomes Smart City",
    "mua-can-ho-3pn-vinhomes-smart-city.html": "Mua căn 3PN Vinhomes Smart City",
}


def append_related_block(path: Path, links: list[tuple[str, str]], heading: str) -> None:
    if not path.is_file():
        return
    doc = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    main = doc.find("main")
    if main is None or doc.select_one("[data-traffic-seo-links]"):
        return
    section = doc.new_tag("section", attrs={"data-traffic-seo-links": "", "class": "section seo-related-links"})
    container = doc.new_tag("div", attrs={"class": "container"})
    title = doc.new_tag("h2")
    title.string = heading
    container.append(title)
    intro = doc.new_tag("p")
    intro.string = "Các bài dưới đây đi tiếp từ nhu cầu tìm hiểu sang so sánh giá, chi phí và quỹ căn đang giao dịch."
    container.append(intro)
    nav = doc.new_tag("nav", attrs={"aria-label": heading})
    for href, label in links:
        anchor = doc.new_tag("a", href=href)
        anchor.string = label + " →"
        nav.append(anchor)
    container.append(nav)
    section.append(container)
    main.append(section)
    path.write_text(str(doc), encoding="utf-8")


def main() -> None:
    if not SITE.is_dir():
        raise SystemExit("_site missing; run prepare_portal_v2.py first")
    missing = [name for name in ARTICLES if not (SOURCE / name).is_file()]
    if missing:
        raise SystemExit("Missing traffic SEO source articles: " + ", ".join(missing))

    for filename in ARTICLES:
        shutil.copy2(SOURCE / filename, SITE / filename)

    append_related_block(
        SITE / "cam-nang.html",
        [
            ("/gia-thue-vinhomes-smart-city-2026.html", "Giá thuê Smart City 2026"),
            ("/phi-dich-vu-vinhomes-smart-city.html", "Phí dịch vụ & chi phí ở"),
            ("/co-nen-mua-vinhomes-smart-city-2026.html", "Có nên mua Smart City?"),
            ("/mua-can-ho-1pn-1-vinhomes-smart-city.html", "Cách chọn căn 1PN+1"),
            ("/mua-can-ho-3pn-vinhomes-smart-city.html", "Cách chọn căn 3PN"),
            ("/shop-chan-de-vinhomes-smart-city.html", "Shop chân đế Smart City"),
            ("/so-sanh-masteri-west-heights-lumiere-evergreen.html", "Masteri vs LUMIÈRE"),
            ("/so-sanh-the-sola-park-the-victoria.html", "Sola Park vs Victoria"),
        ],
        "Cụm tìm kiếm có ý định giao dịch cao",
    )
    append_related_block(
        SITE / "gia-smart-city" / "index.html",
        [
            ("/gia-thue-vinhomes-smart-city-2026.html", "Phân tích giá thuê theo loại căn"),
            ("/phi-dich-vu-vinhomes-smart-city.html", "Các khoản phí cần tính cùng giá"),
            ("/co-nen-mua-vinhomes-smart-city-2026.html", "Khung quyết định trước khi mua"),
        ],
        "Đọc giá theo mục tiêu sử dụng",
    )
    append_related_block(
        SITE / "phan-khu-smart-city" / "masteri-west-heights" / "index.html",
        [("/so-sanh-masteri-west-heights-lumiere-evergreen.html", "So sánh Masteri West Heights với LUMIÈRE Evergreen")],
        "Đặt Masteri cạnh lựa chọn gần nhất",
    )
    append_related_block(
        SITE / "phan-khu-smart-city" / "lumiere-evergreen" / "index.html",
        [("/so-sanh-masteri-west-heights-lumiere-evergreen.html", "So sánh LUMIÈRE Evergreen với Masteri West Heights")],
        "So sánh trước khi chốt phân khúc",
    )
    append_related_block(
        SITE / "phan-khu-smart-city" / "sola-park" / "index.html",
        [("/so-sanh-the-sola-park-the-victoria.html", "So sánh The Sola Park với The Victoria")],
        "Hai lựa chọn cần đặt cạnh nhau",
    )
    append_related_block(
        SITE / "phan-khu-smart-city" / "victoria" / "index.html",
        [("/so-sanh-the-sola-park-the-victoria.html", "So sánh The Victoria với The Sola Park")],
        "So sánh trước khi chọn dự án",
    )
    append_related_block(
        SITE / "mat-bang-can-ho-1pn-1-vinhomes-smart-city.html",
        [("/mua-can-ho-1pn-1-vinhomes-smart-city.html", "Từ mặt bằng 1PN+1 sang quyết định mua")],
        "Đã hiểu mặt bằng? Đi tiếp tới quyết định mua",
    )
    append_related_block(
        SITE / "mat-bang-can-ho-vinhomes-smart-city.html",
        [("/mua-can-ho-3pn-vinhomes-smart-city.html", "Cách chọn căn 3PN cho gia đình")],
        "Từ layout sang lựa chọn căn thực tế",
    )
    print(f"Traffic SEO: staged {len(ARTICLES)} articles and strengthened contextual internal links")


if __name__ == "__main__":
    main()
