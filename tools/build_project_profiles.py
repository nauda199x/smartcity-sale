#!/usr/bin/env python3
"""Build buyer-oriented project profiles and their hub from reviewed project data."""
from __future__ import annotations

from collections import Counter
from html import escape
import json
import statistics
import unicodedata
from pathlib import Path
from urllib.parse import quote

from public_images import public_inventory_image

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "https://timmuasmartcity.com"
PROJECTS = json.loads((ROOT / "data/projects/projects.json").read_text(encoding="utf-8"))["projects"]
ROWS = json.loads((ROOT / "data.json").read_text(encoding="utf-8"))
PUBLIC_FIELDS = {"Tòa", "Phân khu", "Loại", "Diện tích", "Tầng", "Nội thất", "Hướng ban công", "Giá bán tỷ", "Giá bán", "Giá mỗi m2", "Pháp lý", "Ảnh đại diện", "Hiển thị trên Web"}
EDITORIAL_ART = {
    "lumiere-evergreen": "/images/projects/editorial/lumiere-evergreen.svg",
    "sapphire": "/images/projects/editorial/sapphire.svg",
    "the-sakura": "/images/projects/editorial/the-sakura.svg",
    "masteri-west-heights": "/images/projects/editorial/masteri-west-heights.svg",
    "gateway-tower": "/images/projects/editorial/gateway-tower.svg",
}
DEFAULT_EDITORIAL_ART = "/images/projects/editorial/sapphire.svg"


def normalized(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or "")).encode("ascii", "ignore").decode().lower()
    return " ".join(text.split())


def inventory(project: dict) -> list[dict]:
    """Exact normalized-label matching only; deliberately no substring/fuzzy matching."""
    labels = {normalized(x) for x in project["inventoryLabels"]}
    found = []
    for source in ROWS:
        if source.get("Hiển thị trên Web") != "Có" or normalized(source.get("Phân khu")) not in labels:
            continue
        found.append({key: source.get(key) for key in PUBLIC_FIELDS})
    return found


def media(project: dict) -> tuple[dict, list[dict]]:
    manifest = ROOT / "data/media" / f'{project["slug"]}.json'
    if not manifest.exists():
        return {}, []
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    assets = payload.get("assets", [])
    return payload, sorted(assets, key=lambda x: (x.get("sortOrder", 999), x.get("filename", "")))


def variant_dimensions(payload: dict, item: dict, variant: str) -> tuple[int, int]:
    """Derive dimensions for the selected generated variant, not its hero."""
    width = min(item.get("width", 1600), payload.get("variantWidths", {}).get(variant, item.get("width", 1600)))
    ratio = number(item.get("aspectRatio")) or (item.get("width", 1600) / item.get("height", 900))
    return int(width), max(1, round(width / ratio))


def hero_asset(project: dict) -> dict | None:
    payload, assets = media(project)
    candidates = [item for item in assets if item.get("role") == "hero"]
    candidates = candidates or [item for item in assets if item.get("featured")]
    candidates = candidates or assets
    return {"payload": payload, "item": candidates[0]} if candidates else None


def image_for(project: dict, variant: str = "hero") -> tuple[str, str, int, int]:
    selected = hero_asset(project)
    if selected:
        payload, item = selected["payload"], selected["item"]
        src = item.get("variants", {}).get(variant) or item.get("src")
        width, height = variant_dimensions(payload, item, variant)
        return src, item.get("alt") or project["name"], width, height
    return EDITORIAL_ART.get(project["slug"], DEFAULT_EDITORIAL_ART), f'Ảnh biên tập dự phòng cho hồ sơ {project["name"]}', 1600, 1000


def hub_image_for(project: dict) -> tuple[str, str, int, int]:
    """Prefer reviewed project media; otherwise use a real current listing photo on hub cards."""
    if hero_asset(project):
        return image_for(project, "card")
    for row in inventory(project):
        src = public_inventory_image(row.get("Ảnh đại diện"))
        if src:
            tower = str(row.get("Tòa") or "").strip()
            kind = str(row.get("Loại") or "căn hộ").strip()
            detail = " · ".join(x for x in (tower, kind) if x)
            return src, f'Ảnh căn thực tế {detail} trong quỹ {project["name"]}', 1200, 800
    return image_for(project, "card")


def number(value: object) -> float | None:
    try:
        result = float(value)
        return result if result > 0 else None
    except (TypeError, ValueError):
        return None


def fmt(value: float, digits: int = 1) -> str:
    return f"{value:,.{digits}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def metrics(rows: list[dict]) -> dict:
    prices = [x for r in rows if (x := number(r.get("Giá bán tỷ")))]
    ppm = [x for r in rows if (x := number(r.get("Giá mỗi m2")))]
    areas = [x for r in rows if (x := number(r.get("Diện tích")))]
    types = Counter(str(r.get("Loại") or "").strip() for r in rows if str(r.get("Loại") or "").strip())
    towers = Counter(str(r.get("Tòa") or "").strip() for r in rows if str(r.get("Tòa") or "").strip())
    return {"count": len(rows), "prices": prices, "ppm": ppm, "areas": areas, "types": types, "towers": towers}


def header() -> str:
    return '<header class="top"><div class="shell nav"><a class="brand" href="/"><span class="brand-mark">⌂</span><span>Tìm Mua Smart City</span></a><nav class="navlinks"><a href="/phan-khu.html">Phân khu</a><a href="/gia-ban-vinhomes-smart-city.html">Giá bán</a><a href="/can-ho-dang-ban.html">Căn đang bán</a><a href="/cam-nang.html">Cẩm nang</a><a href="/ky-gui-ban-can.html">Ký gửi</a></nav></div></header>'


def head(project: dict, hero: str, schema: list[dict]) -> str:
    seo, route = project["seo"], project["route"]
    return f'''<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(seo["title"])}</title><meta name="description" content="{escape(seo["description"], quote=True)}"><link rel="canonical" href="{DOMAIN}/{route}"><meta name="robots" content="index,follow,max-image-preview:large">
<meta property="og:type" content="website"><meta property="og:title" content="{escape(seo["title"], quote=True)}"><meta property="og:description" content="{escape(seo["description"], quote=True)}"><meta property="og:image" content="{DOMAIN}{hero}"><meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="/assets/portal.css"><link rel="stylesheet" href="/assets/design-system.css"><link rel="stylesheet" href="/assets/project-profiles.css"><script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')}</script></head>'''


def listing_cards(rows: list[dict], name: str) -> str:
    ranked = sorted(rows, key=lambda r: (not bool(r.get("Ảnh đại diện")), not bool(number(r.get("Giá bán tỷ"))), not bool(number(r.get("Diện tích")))))[:6]
    if not ranked:
        return f'<div class="pp-empty"><b>Chưa có căn khớp dữ liệu hiện tại.</b><p>Snapshot công khai chưa ghi nhận căn mang đúng nhãn {escape(name)}. Điều này không có nghĩa dự án hết hàng. Hệ thống không lấy căn dự án khác để lấp chỗ trống.</p></div>'
    cards = []
    for row in ranked:
        image = public_inventory_image(row.get("Ảnh đại diện")) or EDITORIAL_ART.get(next((p["slug"] for p in PROJECTS if p["name"] == name), ""), DEFAULT_EDITORIAL_ART)
        title = " · ".join(filter(None, [str(row.get("Tòa") or ""), str(row.get("Loại") or "")]))
        details = " · ".join(filter(None, [f'{fmt(x)} m²' if (x := number(row.get("Diện tích"))) else "", str(row.get("Tầng") or ""), str(row.get("Hướng ban công") or "")]))
        price = f'{fmt(x, 2)} tỷ' if (x := number(row.get("Giá bán tỷ"))) else "Liên hệ xác nhận"
        ppm = f'{fmt(x)} tr/m²' if (x := number(row.get("Giá mỗi m2"))) else ""
        cards.append(f'<article class="pp-listing"><img src="{escape(image, quote=True)}" alt="Căn {escape(title)} tại {escape(name)}" loading="lazy" width="1200" height="800" referrerpolicy="no-referrer"><div><small>{escape(name)}</small><h3>{escape(title)}</h3><p>{escape(details)}</p><strong>{price}</strong><span>{ppm}</span></div></article>')
    return '<div class="pp-listings">' + ''.join(cards) + '</div>'


def tower_distribution(rows: list[dict]) -> str:
    towers = metrics(rows)["towers"]
    if not towers:
        return ""
    ranked = sorted(towers.items(), key=lambda item: (-item[1], normalized(item[0])))[:10]
    links = ''.join(
        f'<a href="/can-ho-dang-ban.html?q={quote(tower)}"><span>{escape(tower)}</span><b>{count} căn</b></a>'
        for tower, count in ranked
    )
    return f'<div class="pp-tower-breakdown"><small>Tòa đang có hàng trong snapshot</small><div class="pp-tower-chips">{links}</div></div>'


def market_section(rows: list[dict]) -> str:
    m = metrics(rows)
    blocks = [f'<div><span>Căn đang hiển thị</span><strong>{m["count"]}</strong></div>']
    if len(m["prices"]) >= 3:
        blocks += [f'<div><span>Giá chào trung vị</span><strong>{fmt(statistics.median(m["prices"]), 2)} tỷ</strong></div>', f'<div><span>Khoảng giá chào</span><strong>{fmt(min(m["prices"]), 2)}–{fmt(max(m["prices"]), 2)} tỷ</strong></div>']
    if len(m["ppm"]) >= 3:
        blocks.append(f'<div><span>Giá/m² trung vị</span><strong>{fmt(statistics.median(m["ppm"]))} triệu</strong></div>')
    distribution = ''.join(f'<li><span>{escape(kind)}</span><b>{count} căn</b></li>' for kind, count in sorted(m["types"].items()))
    note = "Mẫu dưới 3 căn nên không công bố trung vị." if 0 < m["count"] < 3 else "Giá chào tại thời điểm build; không phải giá giao dịch hay xu hướng lịch sử."
    return f'<div class="pp-market-grid">{"".join(blocks)}</div>{f"<ul class=pp-distribution>{distribution}</ul>" if distribution else ""}{tower_distribution(rows)}<p class="pp-source">{note}</p>'


def gallery(project: dict) -> str:
    payload, all_assets = media(project)
    hero = hero_asset(project)
    hero_id = hero["item"].get("id") if hero else None
    allowed = {"exterior", "interior", "amenity", "pool", "landscape", "lobby", "layout", "map", "construction", "actual", "general"}
    explicitly_curated = any("gallerySelected" in item for item in all_assets)
    if explicitly_curated:
        assets = [item for item in all_assets if item.get("id") != hero_id and item.get("gallerySelected") is True]
    else:
        assets = [item for item in all_assets if item.get("id") != hero_id and item.get("role") in allowed][:8]
    if not assets:
        return ""
    figures = []
    for item in assets:
        src = item.get("variants", {}).get("content") or item.get("src")
        width, height = variant_dimensions(payload, item, "content")
        caption = item.get("caption")
        figcaption = f'<figcaption>{escape(caption)}</figcaption>' if caption else ""
        figures.append(f'<figure><img src="{src}" alt="{escape(item.get("alt") or project["name"], quote=True)}" loading="lazy" width="{width}" height="{height}">{figcaption}</figure>')
    return f'<section class="pp-section pp-gallery-section"><div class="shell"><div class="pp-heading"><span>Hình ảnh</span><h2>Không gian dự án</h2></div><div class="pp-gallery">{"".join(figures)}</div></div></section>'


def inventory_gallery(rows: list[dict], project: dict) -> str:
    """Build a clearly-labelled gallery from reviewed live inventory, never from another project."""
    figures = []
    seen = set()
    ranked = sorted(rows, key=lambda r: (not bool(r.get("Ảnh đại diện")), str(r.get("Tòa") or ""), str(r.get("Loại") or "")))
    for row in ranked:
        src = public_inventory_image(row.get("Ảnh đại diện"))
        if not src or src in seen:
            continue
        seen.add(src)
        tower = str(row.get("Tòa") or "").strip()
        kind = str(row.get("Loại") or "Căn hộ").strip()
        area = f'{fmt(x)} m²' if (x := number(row.get("Diện tích"))) else ""
        caption = " · ".join(x for x in (tower, kind, area) if x)
        alt = f'Ảnh căn thực tế {caption} tại {project["name"]}'
        figures.append(f'<figure><img src="{escape(src, quote=True)}" alt="{escape(alt, quote=True)}" loading="lazy" width="1200" height="800" referrerpolicy="no-referrer"><figcaption>{escape(caption)}</figcaption></figure>')
        if len(figures) >= 8:
            break
    if len(figures) < 2:
        return ""
    return f'<section class="pp-section pp-inventory-gallery-section" id="anh-can-thuc-te"><div class="shell"><div class="pp-heading pp-heading-row"><div><span>Ảnh căn thực tế</span><h2>Nhìn sản phẩm đang có trong quỹ.</h2></div><p class="pp-inventory-gallery-note">Ảnh lấy từ các bản ghi đang bán khớp đúng dự án/phân khu; đây không phải phối cảnh quảng cáo đại diện cho toàn dự án.</p></div><div class="pp-inventory-gallery">{"".join(figures)}</div></div></section>'


def build_profile(project: dict) -> None:
    rows = inventory(project)
    hero, alt, width, height = image_for(project)
    canonical = f'{DOMAIN}/{project["route"]}'
    faq_schema = {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in project["faq"]]}
    schema = [{"@context":"https://schema.org","@type":"WebPage","name":project["seo"]["title"],"description":project["seo"]["description"],"url":canonical,"inLanguage":"vi"}, {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Trang chủ","item":DOMAIN+"/"},{"@type":"ListItem","position":2,"name":"Phân khu","item":DOMAIN+"/phan-khu.html"},{"@type":"ListItem","position":3,"name":project["name"],"item":canonical}]}, {"@context":"https://schema.org", **faq_schema}]
    facts = ''.join(f'<div><span>{escape(fact["label"])}</span><strong>{escape(fact["value"])}</strong></div>' for fact in project["facts"])
    overview = ''.join(f'<p>{escape(p)}</p>' for p in project["overview"])
    bullets = lambda values: ''.join(f'<li>{escape(x)}</li>' for x in values)
    type_stats = metrics(rows)["types"]
    types = ''.join(f'<div><strong>{escape(kind)}</strong><span>{count} căn trong quỹ hiện tại</span></div>' for kind, count in sorted(type_stats.items()))
    filter_url = "/can-ho-dang-ban.html?q=" + quote(project["inventoryLabels"][0])
    faq = ''.join(f'<details><summary>{escape(q)}</summary><p>{escape(a)}</p></details>' for q, a in project["faq"])
    related = ''.join(f'<a href="{url}"><span>Đọc tiếp</span><b>{escape(label)}</b> →</a>' for label, url in project["related"])
    sources = ''.join(f'<li><a href="{escape(source["url"], quote=True)}" rel="nofollow noopener">{escape(source["label"])}</a> · {escape(source["publisher"])} · truy cập {escape(source["accessed"])}</li>' for source in project["sources"])
    actual_gallery = inventory_gallery(rows, project)
    photo_jump = '<a href="#anh-can-thuc-te">Ảnh căn thực tế</a>' if actual_gallery else ""
    html = head(project, hero, schema) + f'''<body class="project-profile pp-{project["accent"]}">{header()}<main>
<nav class="shell pp-breadcrumb" aria-label="Breadcrumb"><a href="/">Trang chủ</a><span>›</span><a href="/phan-khu.html">Phân khu</a><span>›</span><span>{escape(project["name"])}</span></nav>
<section class="pp-hero"><img src="{hero}" alt="{escape(alt, quote=True)}" width="{width}" height="{height}" fetchpriority="high"><div class="shell pp-hero-copy"><span>{escape(project["eyebrow"])}</span><h1>{escape(project["name"])}</h1><p>{escape(project["summary"])}</p><div><a class="btn btn-primary" href="{filter_url}">Tìm căn đang bán</a><a class="btn btn-ghost" href="#thi-truong">Xem dữ liệu thị trường</a></div></div></section>
<section class="pp-facts"><div class="shell pp-facts-grid">{facts}</div></section>
<section class="pp-section"><div class="shell pp-two"><div><div class="pp-heading"><span>01 · Tổng quan</span><h2>Hiểu dự án trước khi chọn căn</h2></div>{overview}</div><aside><b>Đi nhanh tới</b><a href="#vi-tri">Vị trí</a>{photo_jump}<a href="#loai-can">Loại căn</a><a href="#thi-truong">Dữ liệu thị trường</a><a href="#inventory">Quỹ căn</a><a href="#faq">FAQ</a></aside></div></section>
<section class="pp-section pp-tint" id="vi-tri"><div class="shell pp-split"><div class="pp-heading"><span>02 · Vị trí</span><h2>Kết nối trong Smart City</h2></div><div><p>{escape(project["location"])}</p><div class="pp-links"><a href="/phan-khu.html">Tổng quan phân khu →</a><a href="/cam-nang.html">Cẩm nang người mua →</a></div></div></div></section>
{gallery(project)}
{actual_gallery}
<section class="pp-section"><div class="shell"><div class="pp-heading"><span>03 · Tòa & mặt bằng</span><h2>Đọc sản phẩm ở cấp từng căn</h2></div><div class="pp-three"><div><h3>Tòa / layout</h3><ul>{bullets(project["buildings"])}</ul></div><div><h3>Tiện ích & cảnh quan</h3><ul>{bullets(project["amenities"])}</ul></div><div id="loai-can"><h3>Loại căn đang có</h3>{f'<div class="pp-types">{types}</div>' if types else '<p>Chưa có mẫu inventory khớp để thống kê loại căn.</p>'}</div></div></div></section>
<section class="pp-section pp-dark"><div class="shell pp-advice"><div><div class="pp-heading"><span>04 · Phù hợp với ai?</span><h2>Shortlist theo nhu cầu thật</h2></div><ul>{bullets(project["fit"])}</ul></div><div><div class="pp-heading"><span>05 · Buyer notes</span><h2>Điểm nên cân nhắc trước khi mua</h2></div><ol>{bullets(project["considerations"])}</ol></div></div></section>
<section class="pp-section" id="thi-truong"><div class="shell pp-split"><div class="pp-heading"><span>06 · Snapshot</span><h2>Dữ liệu thị trường hiện tại</h2><p>Tính tự động từ các căn công khai khớp đúng nhãn dự án.</p></div><div>{market_section(rows)}</div></div></section>
<section class="pp-section pp-tint" id="inventory"><div class="shell"><div class="pp-heading pp-heading-row"><div><span>07 · Inventory</span><h2>Căn đang bán tại {escape(project["name"])}</h2></div><a href="{filter_url}">Xem toàn bộ căn →</a></div>{listing_cards(rows, project["name"])}<p class="pp-source">Dữ liệu có thể thay đổi. Vui lòng xác nhận lại giá, hiện trạng và hồ sơ trước khi đặt cọc.</p></div></section>
<section class="pp-section" id="faq"><div class="shell pp-faq"><div class="pp-heading"><span>08 · FAQ</span><h2>Câu hỏi người mua thường đặt</h2></div><div>{faq}</div></div></section>
<section class="pp-section pp-related"><div class="shell"><div class="pp-heading"><span>Liên quan</span><h2>Tiếp tục nghiên cứu</h2></div><div>{related}</div></div></section>
<section class="pp-sources"><div class="shell"><h2>Nguồn tham khảo</h2><ul>{sources}</ul><p>Thông tin dự án dùng để định hướng; hồ sơ và điều kiện của từng căn cần được xác minh tại thời điểm giao dịch.</p></div></section>
<section class="pp-cta"><div class="shell"><div><span>Bước tiếp theo</span><h2>Từ hồ sơ dự án tới căn phù hợp.</h2></div><div><a class="btn btn-primary" href="{filter_url}">Tìm quỹ căn</a><a class="btn btn-ghost" href="/ky-gui-ban-can.html">Ký gửi căn hộ</a></div></div></section></main>
<footer class="footer"><div class="shell"><p>Tìm Mua Smart City · Cổng thông tin độc lập dành cho người mua. <a href="/gia-ban-vinhomes-smart-city.html">Cách đọc dữ liệu giá</a>.</p></div></footer><script src="/assets/app-shell.js" defer></script></body></html>'''
    (ROOT / project["route"]).write_text(html, encoding="utf-8")
    print("built profile", project["route"], f"({len(rows)} inventory rows)")


def build_hub() -> None:
    grouped = {}
    for project in PROJECTS:
        hero, alt, width, height = hub_image_for(project)
        count = len(inventory(project))
        availability = f"{count} căn đang hiển thị" if count else "Chưa có căn khớp dữ liệu hiện tại"
        card = f'<article class="pp-hub-card"><a class="pp-hub-image" href="/{project["route"]}"><img src="{hero}" alt="{escape(alt, quote=True)}" width="{width}" height="{height}" loading="lazy" referrerpolicy="no-referrer"></a><div><span>{escape(project["developer"])} · {availability}</span><h3><a href="/{project["route"]}">{escape(project["name"])}</a></h3><p>{escape(project["summary"])}</p><a href="/{project["route"]}">Mở hồ sơ →</a></div></article>'
        grouped.setdefault(project["family"], []).append(card)
    groups = "".join(f'<section class="pp-hub-group"><div class="pp-heading"><span>Nhóm chủ thể</span><h2>{escape(family)}</h2></div><div class="pp-hub-grid">{"".join(cards)}</div></section>' for family, cards in grouped.items())
    schema = [{"@context":"https://schema.org","@type":"CollectionPage","name":"Hồ sơ dự án và phân khu Smart City","url":DOMAIN+"/phan-khu.html"}]
    pseudo = {"seo":{"title":"Dự án & phân khu Vinhomes Smart City | Knowledge Hub","description":"Knowledge hub dự án Smart City theo đúng chủ thể phát triển, vị trí, sản phẩm, lưu ý người mua và quỹ căn hiện tại."},"route":"phan-khu.html"}
    html = head(pseudo, "/images/hero/hero-smart-city-desktop.webp", schema) + f'''<body class="project-profile">{header()}<main><section class="pp-hub-hero"><img src="/images/hero/hero-smart-city-desktop.webp" alt="Toàn cảnh các tòa căn hộ Vinhomes Smart City vào buổi tối" width="1800" height="1013" fetchpriority="high"><div class="shell"><span>Project Knowledge Hub V2</span><h1>Hiểu đúng dự án,<br>rồi mới chọn căn.</h1><p>Hồ sơ được tách theo đúng phân khu, dự án và chủ thể phát triển. Mỗi trang kết nối nguồn sơ cấp, phân tích người mua và inventory hiện tại.</p></div></section><section class="pp-section"><div class="shell">{groups}</div></section><section class="pp-section pp-dark"><div class="shell pp-split"><div><div class="pp-heading"><span>Quy trình</span><h2>Đọc khu trước, lọc căn sau.</h2></div><p>Snapshot chỉ dùng giá chào công khai và không thay thế thẩm định căn. Sau khi chọn 1–2 dự án, hãy tạo nhóm căn cùng loại, diện tích và vị trí để so.</p></div><div class="pp-links"><a href="/so-sanh-phan-khu-vinhomes-smart-city.html">Mở bảng so sánh →</a><a href="/gia-ban-vinhomes-smart-city.html">Cách đọc giá/m² →</a><a href="/can-ho-dang-ban.html">Mở toàn bộ quỹ căn →</a><a href="/cam-nang.html">Cẩm nang người mua →</a></div></div></section></main><footer class="footer"><div class="shell"><p>Tìm Mua Smart City · Hồ sơ độc lập dành cho người mua.</p></div></footer><script src="/assets/app-shell.js" defer></script></body></html>'''
    (ROOT / "phan-khu.html").write_text(html, encoding="utf-8")
    print("built grouped project hub")


if __name__ == "__main__":
    for item in PROJECTS:
        build_profile(item)
    build_hub()