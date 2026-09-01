#!/usr/bin/env python3
"""Build production SEO artifacts inside _site.

- Generates crawlable static pages for approved marketplace listings.
- Adds ItemList JSON-LD to sale/rent collection pages.
- Splits XML sitemaps into pages, floorplans, listings and images.
- Makes /sitemap.xml a sitemap index so Search Console needs one submission.
- Never uses service-role credentials; only the public Supabase publishable key.
"""
from __future__ import annotations

from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE_ROOT = ROOT / "_site"
SITE = "https://timmuasmartcity.com"
CONFIG = ROOT / "assets/js/marketplace-config.js"
NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
IMAGE_NS = "http://www.google.com/schemas/sitemap-image/1.1"


def parse_marketplace_config() -> tuple[str, str, str]:
    text = CONFIG.read_text(encoding="utf-8")
    def grab(name: str) -> str:
        match = re.search(rf'{re.escape(name)}\s*:\s*"([^"]+)"', text)
        return match.group(1) if match else ""
    return grab("supabaseUrl").rstrip("/"), grab("supabasePublishableKey"), grab("storageBucket") or "listing-images"


def fetch_approved_listings() -> list[dict]:
    base, key, _ = parse_marketplace_config()
    if not base or not key:
        print("SEO: marketplace config missing; skip static listing generation")
        return []
    params = {
        "select": "id,slug,listing_code,listing_type,title,description,poster_name,contact_phone,phase,tower,unit_type,bedroom_count,area_sqm,price_vnd,furnishing,floor_label,available_from,legal_status,approved_at,created_at,listing_images(storage_path,sort_order,alt_text)",
        "status": "eq.approved",
        "order": "is_featured.desc,sort_priority.desc,approved_at.desc",
        "limit": "500",
    }
    req = Request(
        f"{base}/rest/v1/listings?{urlencode(params)}",
        headers={"apikey": key, "Authorization": f"Bearer {key}", "Accept": "application/json"},
    )
    try:
        with urlopen(req, timeout=20) as response:
            rows = json.loads(response.read().decode("utf-8"))
        return rows if isinstance(rows, list) else []
    except Exception as exc:
        print(f"SEO: approved listings fetch failed: {exc}")
        return []


def price_text(value, listing_type: str) -> str:
    try:
        amount = float(value or 0)
    except (TypeError, ValueError):
        amount = 0
    if not amount:
        return "Liên hệ"
    if listing_type == "rent":
        number = amount / 1_000_000
        return f"{number:g} triệu/tháng".replace(".", ",")
    number = amount / 1_000_000_000
    return f"{number:.2f}".rstrip("0").rstrip(".").replace(".", ",") + " tỷ"


def image_url(storage_path: str) -> str:
    base, _, bucket = parse_marketplace_config()
    path = "/".join(segment for segment in str(storage_path or "").split("/") if segment)
    if not base or not path:
        return ""
    from urllib.parse import quote
    encoded = "/".join(quote(segment, safe="") for segment in path.split("/"))
    return f"{base}/storage/v1/object/public/{quote(bucket, safe='')}/{encoded}"


def listing_path(row: dict) -> tuple[str, Path]:
    segment = "cho-thue-smart-city" if row.get("listing_type") == "rent" else "mua-ban-smart-city"
    slug = re.sub(r"[^a-z0-9-]", "", str(row.get("slug") or "").lower()).strip("-")
    if not slug:
        slug = re.sub(r"[^a-z0-9]+", "-", str(row.get("listing_code") or row.get("id") or "tin").lower()).strip("-")
    rel = f"/{segment}/{slug}/"
    return rel, SITE_ROOT / segment / slug / "index.html"


def listing_html(row: dict, rel: str) -> str:
    title = str(row.get("title") or "Căn hộ Vinhomes Smart City").strip()
    desc = str(row.get("description") or "").strip()
    short_desc = re.sub(r"\s+", " ", desc)[:155] or "Tin đăng căn hộ Vinhomes Smart City đã được duyệt hiển thị."
    listing_type = "Cho thuê" if row.get("listing_type") == "rent" else "Mua bán"
    price = price_text(row.get("price_vnd"), row.get("listing_type") or "sale")
    phase = str(row.get("phase") or "")
    tower = str(row.get("tower") or "")
    unit = str(row.get("unit_type") or "")
    area = row.get("area_sqm")
    area_text = f"{area:g} m²" if isinstance(area, (int, float)) else (f"{area} m²" if area else "—")
    floor = str(row.get("floor_label") or "—")
    furnishing = str(row.get("furnishing") or "—")
    poster = str(row.get("poster_name") or "Người đăng")
    phone = str(row.get("contact_phone") or "").strip()
    tel = re.sub(r"[^+0-9]", "", phone)
    zalo = re.sub(r"\D", "", phone)
    images = sorted(row.get("listing_images") or [], key=lambda item: int(item.get("sort_order") or 0))
    gallery = []
    for index, item in enumerate(images):
        src = image_url(item.get("storage_path"))
        if not src:
            continue
        alt = str(item.get("alt_text") or f"{title} — ảnh {index+1}")
        gallery.append(f'<figure><img src="{escape(src)}" alt="{escape(alt)}" loading="{"eager" if index == 0 else "lazy"}" decoding="async"></figure>')
    if not gallery:
        gallery.append('<figure><img src="/images/hero/hero-smart-city-desktop.webp" alt="Vinhomes Smart City" loading="eager"></figure>')
    og_image = image_url(images[0].get("storage_path")) if images else SITE + "/images/hero/hero-smart-city-desktop.webp"
    canonical = SITE + rel
    breadcrumb_parent = "/cho-thue-smart-city/" if row.get("listing_type") == "rent" else "/mua-ban-smart-city/"
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Trang chủ", "item": SITE + "/"},
                    {"@type": "ListItem", "position": 2, "name": listing_type, "item": SITE + breadcrumb_parent},
                    {"@type": "ListItem", "position": 3, "name": title, "item": canonical},
                ],
            },
            {
                "@type": "WebPage",
                "name": title,
                "description": short_desc,
                "url": canonical,
                "dateModified": str(row.get("approved_at") or row.get("created_at") or "")[:10] or str(date.today()),
                "inLanguage": "vi-VN",
                "mainEntity": {
                    "@type": "Apartment",
                    "name": title,
                    "floorSize": {"@type": "QuantitativeValue", "value": area or 0, "unitCode": "MTK"},
                    "address": {
                        "@type": "PostalAddress",
                        "addressLocality": "Hà Nội",
                        "addressCountry": "VN",
                        "streetAddress": "Vinhomes Smart City, Tây Mỗ",
                    },
                },
            },
        ],
    }
    facts = [
        ("Mức giá", price), ("Diện tích", area_text), ("Loại căn", unit or "—"),
        ("Tầng", floor), ("Phân khu", phase or "—"), ("Tòa", tower or "—"), ("Nội thất", furnishing),
    ]
    fact_html = "".join(f"<div><dt>{escape(k)}</dt><dd>{escape(str(v))}</dd></div>" for k, v in facts)
    call = f'<a class="btn btn-primary" href="tel:{escape(tel)}">Gọi {escape(phone)}</a>' if tel else ""
    zalo_link = f'<a class="btn" href="https://zalo.me/{escape(zalo)}" target="_blank" rel="noopener">Nhắn Zalo</a>' if zalo else ""
    return f'''<!doctype html>
<html lang="vi"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{escape(title)} | Tìm Mua Smart City</title>
<meta name="description" content="{escape(short_desc)}">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{escape(canonical)}">
<link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png">
<meta property="og:type" content="article"><meta property="og:site_name" content="Tìm Mua Smart City">
<meta property="og:title" content="{escape(title)}"><meta property="og:description" content="{escape(short_desc)}">
<meta property="og:url" content="{escape(canonical)}"><meta property="og:image" content="{escape(og_image)}">
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="/assets/css/site.css?v=20260901-seo2"><link rel="stylesheet" href="/assets/css/marketplace.css?v=20260901-seo2">
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, separators=(",", ":"))}</script>
</head>
<body class="listing-detail-page">
<a class="skip-link" href="#main">Bỏ qua điều hướng</a>
<header class="site-header"><div class="container nav"><a class="brand" href="/"><span class="brand-mark" aria-hidden="true">SC</span><span>TÌM MUA SMART CITY</span></a><nav class="nav-links" aria-label="Điều hướng chính"><a href="/tong-quan-smart-city/">Tổng quan</a><a href="/giao-dich-smart-city/">Giao dịch</a><a href="/mua-ban-smart-city/">Mua bán</a><a href="/cho-thue-smart-city/">Cho thuê</a><a href="/dang-tin-smart-city/">Đăng tin</a></nav></div></header>
<main id="main">
<div class="container breadcrumb"><a href="/">Trang chủ</a><span>/</span><a href="{breadcrumb_parent}">{listing_type}</a><span>/</span>{escape(title)}</div>
<div class="container detail-shell detail-shell--portal">
<article class="detail-main">
<div class="detail-gallery-wrap"><div class="detail-gallery"><div class="detail-gallery-track">{''.join(gallery)}</div><span class="detail-gallery-counter">1/{len(gallery)}</span></div></div>
<div class="detail-copy"><p class="eyebrow">{escape(str(row.get("listing_code") or ""))}</p><h1>{escape(title)}</h1><div class="detail-location"><strong>Vinhomes Smart City</strong><span>{escape(" · ".join(x for x in [phase, tower] if x))}</span></div><h2>Mô tả</h2><p class="detail-description">{escape(desc)}</p><h2>Đặc điểm bất động sản</h2><dl class="detail-feature-list">{fact_html}</dl><p class="notice"><strong>Lưu ý:</strong> Người xem cần tự kiểm tra danh tính, quyền giao dịch, hiện trạng căn và hồ sơ trước khi đặt cọc.</p></div>
</article>
<aside><div class="detail-panel"><p class="eyebrow">{listing_type}</p><strong class="detail-price">{escape(price)}</strong><dl class="detail-specs">{fact_html}</dl><div class="detail-poster"><span>Người đăng</span><strong>{escape(poster)}</strong></div><div class="detail-contact">{call}{zalo_link}</div><p class="detail-note">Giá và trạng thái căn cần được xác nhận lại tại thời điểm liên hệ.</p></div></aside>
</div></main>
<footer class="site-footer"><div class="container footer-grid"><div><a class="brand" href="/"><span class="brand-mark" aria-hidden="true">SC</span><span>TÌM MUA SMART CITY</span></a><p>Cổng thông tin & sàn giao dịch chuyên sâu Vinhomes Smart City.</p></div><div><nav class="footer-links"><a href="/giao-dich-smart-city/">Giao dịch</a><a href="/mua-ban-smart-city/">Mua bán</a><a href="/cho-thue-smart-city/">Cho thuê</a><a href="/cam-nang.html">Cẩm nang</a><a href="/dang-tin-smart-city/">Đăng tin</a></nav></div></div></footer>
<script src="/assets/js/site.js" defer></script><script src="/assets/app-shell.js" defer></script>
</body></html>'''


def generate_listing_pages(rows: list[dict]) -> list[tuple[str, str]]:
    output = []
    for row in rows:
        rel, target = listing_path(row)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(listing_html(row, rel), encoding="utf-8")
        lastmod = str(row.get("approved_at") or row.get("created_at") or "")[:10]
        output.append((SITE + rel, lastmod))
    print(f"SEO: generated {len(output)} static approved listing pages")
    return output


def inject_itemlist(rows: list[dict], listing_type: str, target: Path) -> None:
    if not target.is_file():
        return
    filtered = [row for row in rows if row.get("listing_type") == listing_type]
    items = []
    for pos, row in enumerate(filtered, 1):
        rel, _ = listing_path(row)
        items.append({"@type": "ListItem", "position": pos, "url": SITE + rel, "name": str(row.get("title") or "")})
    schema = {"@context": "https://schema.org", "@type": "ItemList", "name": "Căn hộ đang giao dịch tại Vinhomes Smart City", "numberOfItems": len(items), "itemListElement": items}
    text = target.read_text(encoding="utf-8")
    marker = '<script data-seo-itemlist type="application/ld+json">'
    block = marker + json.dumps(schema, ensure_ascii=False, separators=(",", ":")) + "</script>"
    if marker in text:
        text = re.sub(r'<script data-seo-itemlist type="application/ld\+json">.*?</script>', block, text, flags=re.S)
    else:
        text = text.replace("</head>", block + "</head>", 1)
    target.write_text(text, encoding="utf-8")


def add_camnang_internal_links() -> None:
    for path in SITE_ROOT.rglob("*.html"):
        if any(part.startswith(".") for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if 'class="footer-links"' not in text or 'href="/cam-nang.html"' in text:
            continue
        text = text.replace('class="footer-links"', 'class="footer-links"', 1)
        match = re.search(r'(<nav[^>]*class="footer-links"[^>]*>)(.*?)(</nav>)', text, re.S)
        if not match:
            continue
        body = match.group(2) + '<a href="/cam-nang.html">Cẩm nang</a>'
        text = text[:match.start()] + match.group(1) + body + match.group(3) + text[match.end():]
        path.write_text(text, encoding="utf-8")


def page_url(path: Path) -> str:
    rel = path.relative_to(SITE_ROOT).as_posix()
    if rel == "index.html":
        return SITE + "/"
    if rel.endswith("/index.html"):
        return SITE + "/" + rel[:-10]
    return SITE + "/" + rel


def is_indexable(path: Path, text: str) -> bool:
    rel = path.relative_to(SITE_ROOT).as_posix()
    if rel == "404.html" or rel.startswith("admin/") or rel.startswith("tin-dang-smart-city/"):
        return False
    robots = re.search(r'<meta[^>]+name=["\']robots["\'][^>]+content=["\']([^"\']+)', text, re.I)
    return not (robots and "noindex" in robots.group(1).lower())


def write_urlset(path: Path, rows: list[tuple[str, str]]) -> None:
    ET.register_namespace("", NS)
    root = ET.Element(f"{{{NS}}}urlset")
    for url, lastmod in rows:
        node = ET.SubElement(root, f"{{{NS}}}url")
        ET.SubElement(node, f"{{{NS}}}loc").text = url
        if lastmod and re.fullmatch(r"\d{4}-\d{2}-\d{2}", lastmod):
            ET.SubElement(node, f"{{{NS}}}lastmod").text = lastmod
    ET.indent(root, space="  ")
    path.write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode") + "\n", encoding="utf-8")


def build_image_sitemap(indexable: list[tuple[Path, str]]) -> int:
    ET.register_namespace("", NS)
    ET.register_namespace("image", IMAGE_NS)
    root = ET.Element(f"{{{NS}}}urlset")
    count = 0
    for path, url in indexable:
        text = path.read_text(encoding="utf-8", errors="replace")
        found = []
        seen = set()
        for match in re.finditer(r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>', text, re.I):
            src = match.group(1)
            parts = urlsplit(src)
            if parts.scheme and parts.netloc:
                if parts.netloc != "timmuasmartcity.com":
                    continue
                image = src
            elif src.startswith("/"):
                local = SITE_ROOT / src.lstrip("/")
                if not local.is_file():
                    continue
                image = SITE + src
            else:
                continue
            if image in seen:
                continue
            seen.add(image)
            alt_match = re.search(r'alt=["\']([^"\']*)', match.group(0), re.I)
            found.append((image, alt_match.group(1) if alt_match else ""))
        if not found:
            continue
        url_node = ET.SubElement(root, f"{{{NS}}}url")
        ET.SubElement(url_node, f"{{{NS}}}loc").text = url
        for image, alt in found:
            img_node = ET.SubElement(url_node, f"{{{IMAGE_NS}}}image")
            ET.SubElement(img_node, f"{{{IMAGE_NS}}}loc").text = image
            if alt:
                ET.SubElement(img_node, f"{{{IMAGE_NS}}}title").text = alt
            count += 1
    ET.indent(root, space="  ")
    (SITE_ROOT / "sitemap-images.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode") + "\n", encoding="utf-8")
    return count


def build_sitemaps(listing_urls: list[tuple[str, str]]) -> None:
    indexable = []
    listing_set = {url for url, _ in listing_urls}
    for path in SITE_ROOT.rglob("*.html"):
        text = path.read_text(encoding="utf-8", errors="replace")
        if is_indexable(path, text):
            indexable.append((path, page_url(path)))

    floorplans = []
    pages = []
    for path, url in sorted(indexable, key=lambda item: item[1]):
        if url in listing_set:
            continue
        if "/mat-bang-smart-city/" in url:
            floorplans.append((url, ""))
        else:
            pages.append((url, ""))

    write_urlset(SITE_ROOT / "sitemap-pages.xml", pages)
    write_urlset(SITE_ROOT / "sitemap-floorplans.xml", floorplans)
    write_urlset(SITE_ROOT / "sitemap-listings.xml", listing_urls)
    image_count = build_image_sitemap(indexable)

    ET.register_namespace("", NS)
    index = ET.Element(f"{{{NS}}}sitemapindex")
    for filename in ("sitemap-pages.xml", "sitemap-floorplans.xml", "sitemap-listings.xml", "sitemap-images.xml"):
        node = ET.SubElement(index, f"{{{NS}}}sitemap")
        ET.SubElement(node, f"{{{NS}}}loc").text = SITE + "/" + filename
    ET.indent(index, space="  ")
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(index, encoding="unicode") + "\n"
    (SITE_ROOT / "sitemap.xml").write_text(xml, encoding="utf-8")
    (SITE_ROOT / "sitemap-index.xml").write_text(xml, encoding="utf-8")
    (SITE_ROOT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\nDisallow: /admin/\n\nSitemap: https://timmuasmartcity.com/sitemap.xml\n",
        encoding="utf-8",
    )
    print(f"SEO: sitemaps pages={len(pages)} floorplans={len(floorplans)} listings={len(listing_urls)} images={image_count}")


def main() -> None:
    if not SITE_ROOT.is_dir():
        raise SystemExit("_site does not exist; run prepare_portal_v2.py first")
    rows = fetch_approved_listings()
    listing_urls = generate_listing_pages(rows)
    inject_itemlist(rows, "sale", SITE_ROOT / "mua-ban-smart-city/index.html")
    inject_itemlist(rows, "rent", SITE_ROOT / "cho-thue-smart-city/index.html")
    add_camnang_internal_links()
    build_sitemaps(listing_urls)


if __name__ == "__main__":
    main()
