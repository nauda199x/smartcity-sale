from __future__ import annotations

from collections import defaultdict
from datetime import date
from html import escape
from pathlib import Path
import json
import re
import statistics
import unicodedata

SITE = "https://timmuasmartcity.com"

PHASE_SLUGS = {
    "Sapphire": "sapphire",
    "Sakura": "sakura",
    "Miami": "miami",
    "Tonkin": "tonkin",
    "Masteri": "masteri",
    "Lumiere": "lumiere-evergreen",
    "Imperia": "imperia",
    "Canopy": "canopy",
    "Sola Park": "sola-park",
    "Victoria": "victoria",
}
PHASE_INFO = {
    "Sapphire": "/phan-khu-smart-city/sapphire/",
    "Sakura": "/phan-khu-smart-city/sakura/",
    "Miami": "/phan-khu-smart-city/miami/",
    "Tonkin": "/phan-khu-smart-city/tonkin/",
    "Masteri": "/phan-khu-smart-city/masteri-west-heights/",
    "Lumiere": "/phan-khu-smart-city/lumiere-evergreen/",
    "Imperia": "/phan-khu-smart-city/imperia/",
    "Canopy": "/phan-khu-smart-city/canopy/",
    "Sola Park": "/phan-khu-smart-city/sola-park/",
    "Victoria": "/phan-khu-smart-city/victoria/",
}


def safe_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def slugify(value: str) -> str:
    text = unicodedata.normalize("NFD", str(value or "").replace("đ", "d").replace("Đ", "D"))
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn").lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")[:70]


def listing_path(row: dict) -> str:
    segment = "cho-thue-smart-city" if row.get("listing_type") == "rent" else "mua-ban-smart-city"
    slug = re.sub(r"[^a-z0-9-]", "", str(row.get("slug") or "").lower()).strip("-")
    if not slug:
        slug = slugify(str(row.get("listing_code") or row.get("id") or "tin-dang"))
    return f"/{segment}/{slug}/"


def money(value, listing_type: str) -> str:
    try:
        amount = float(value or 0)
    except (TypeError, ValueError):
        amount = 0
    if not amount:
        return "Liên hệ"
    if listing_type == "rent":
        return f"{amount / 1_000_000:g} triệu/tháng".replace(".", ",")
    return f"{amount / 1_000_000_000:.2f}".rstrip("0").rstrip(".").replace(".", ",") + " tỷ"


def price_summary(rows: list[dict], listing_type: str) -> str:
    prices = []
    for row in rows:
        try:
            value = float(row.get("price_vnd") or 0)
        except (TypeError, ValueError):
            value = 0
        if value > 0:
            prices.append(value)
    prices.sort()
    if not prices:
        return "Giá liên hệ theo từng căn."
    low, high = money(prices[0], listing_type), money(prices[-1], listing_type)
    median = money(statistics.median(prices), listing_type)
    return f"Quỹ đang hiển thị có mức giá từ {low} đến {high}; trung vị khoảng {median}."


def card(row: dict) -> str:
    href = listing_path(row)
    facts = " · ".join(
        str(value)
        for value in [
            row.get("tower"),
            row.get("unit_type"),
            f"{row.get('area_sqm')} m²" if row.get("area_sqm") else "",
        ]
        if value
    )
    return (
        '<article class="seo-market-card"><div>'
        f'<p>{escape(str(row.get("listing_code") or "Tin đăng"))}</p>'
        f'<h3><a href="{escape(href)}">{escape(str(row.get("title") or "Căn hộ Vinhomes Smart City"))}</a></h3>'
        f'<span>{escape(facts)}</span></div>'
        f'<strong>{escape(money(row.get("price_vnd"), row.get("listing_type") or "sale"))}</strong>'
        "</article>"
    )


def page_html(
    rows: list[dict],
    *,
    listing_type: str,
    phase: str,
    unit_type: str | None = None,
    tower: str | None = None,
) -> tuple[str, str]:
    is_rent = listing_type == "rent"
    action = "Cho thuê" if is_rent else "Mua bán"
    segment = "cho-thue-smart-city" if is_rent else "mua-ban-smart-city"
    phase_slug = PHASE_SLUGS.get(phase, slugify(phase))

    suffix = ""
    label_bits = [phase]
    if tower:
        suffix = f"/{slugify(tower)}"
        label_bits.append(tower)
    elif unit_type:
        suffix = f"/{slugify(unit_type)}"
        label_bits.append(unit_type)

    rel = f"/{segment}/{phase_slug}{suffix}/"
    canonical = SITE + rel
    label = " · ".join(label_bits)
    h1 = f"{action} căn hộ {label} Vinhomes Smart City"
    title = f"{h1} – Giá & tin mới cập nhật"
    description = (
        f"Cập nhật {len(rows)} tin {action.lower()} {label} tại Vinhomes Smart City. "
        "Xem mức giá, diện tích, tòa và liên hệ trực tiếp người đăng."
    )
    modified = max(
        (str(row.get("approved_at") or row.get("created_at") or "")[:10] for row in rows),
        default=str(date.today()),
    )
    listing_items = "".join(card(row) for row in rows[:30])

    item_list = [
        {
            "@type": "ListItem",
            "position": index,
            "url": SITE + listing_path(row),
            "name": str(row.get("title") or "Căn hộ Vinhomes Smart City"),
        }
        for index, row in enumerate(rows[:30], 1)
    ]
    breadcrumb_items = [
        {"@type": "ListItem", "position": 1, "name": "Trang chủ", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": action, "item": SITE + f"/{segment}/"},
        {
            "@type": "ListItem",
            "position": 3,
            "name": phase,
            "item": SITE + f"/{segment}/{phase_slug}/",
        },
    ]
    if suffix:
        breadcrumb_items.append(
            {
                "@type": "ListItem",
                "position": 4,
                "name": tower or unit_type or label,
                "item": canonical,
            }
        )
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "CollectionPage",
                "name": h1,
                "description": description,
                "url": canonical,
                "dateModified": modified,
                "inLanguage": "vi-VN",
                "isPartOf": {"@type": "WebSite", "name": "Sàn Smart City", "url": SITE + "/"},
            },
            {
                "@type": "ItemList",
                "name": h1,
                "numberOfItems": len(rows),
                "itemListElement": item_list,
            },
            {"@type": "BreadcrumbList", "itemListElement": breadcrumb_items},
        ],
    }

    breadcrumbs = [
        ("Trang chủ", "/"),
        (action, f"/{segment}/"),
        (phase, f"/{segment}/{phase_slug}/"),
    ]
    if suffix:
        breadcrumbs.append((tower or unit_type or label, rel))
    crumbs = '<span>/</span>'.join(
        f'<a href="{escape(href)}">{escape(name)}</a>' for name, href in breadcrumbs
    )

    phase_info = PHASE_INFO.get(phase, "/phan-khu-smart-city/")
    view_all_query = [f"phase={phase}"]
    if tower:
        view_all_query.append(f"tower={tower}")
    if unit_type:
        view_all_query.append(f"bedroom={unit_type}")
    from urllib.parse import urlencode
    filtered_href = f"/{segment}/?{urlencode(dict(item.split('=', 1) for item in view_all_query))}#quy-can"

    html = f'''<!doctype html><html lang="vi"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{escape(title)}</title><meta name="description" content="{escape(description)}"><meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{escape(canonical)}"><meta property="og:title" content="{escape(title)}"><meta property="og:description" content="{escape(description)}"><meta property="og:url" content="{escape(canonical)}"><meta property="og:type" content="website"><meta property="og:site_name" content="Sàn Smart City"><meta property="og:image" content="{SITE}/images/hero/hero-smart-city-desktop.webp">
<link rel="stylesheet" href="/assets/css/site.css?v=20260901-seo2"><link rel="stylesheet" href="/assets/css/marketplace.css?v=20260901-seo2"><link rel="stylesheet" href="/assets/css/site-theme.css?v=20260902-1">
<style>.seo-market-hero{{padding:42px 0 22px;background:#f4f8f6}}.seo-market-hero h1{{max-width:850px;margin:8px 0 12px;font-size:clamp(32px,5vw,54px);line-height:1.05}}.seo-market-hero>div>p:last-of-type{{max-width:820px;line-height:1.7}}.seo-market-summary{{display:grid;grid-template-columns:2fr 1fr;gap:22px;padding:28px 0}}.seo-market-list{{display:grid;gap:10px}}.seo-market-card{{display:flex;justify-content:space-between;gap:18px;border:1px solid #dfe7e3;border-radius:14px;padding:15px;background:#fff}}.seo-market-card p,.seo-market-card span{{margin:0;color:#68746f;font-size:12px}}.seo-market-card h3{{margin:4px 0 5px;font-size:16px}}.seo-market-card strong{{white-space:nowrap;font-size:18px}}.seo-market-side{{border:1px solid #dfe7e3;border-radius:16px;padding:18px;height:max-content}}.seo-market-side .btn{{display:flex;justify-content:center;margin-top:10px}}@media(max-width:760px){{.seo-market-summary{{grid-template-columns:1fr}}.seo-market-card{{display:block}}.seo-market-card strong{{display:block;margin-top:10px}}}}</style>
<script type="application/ld+json">{safe_json(schema)}</script>
</head><body>
<header class="site-header"><div class="container nav"><a class="brand" href="/"><span class="brand-mark" aria-hidden="true">SC</span><span>SÀN SMART CITY</span></a><nav class="nav-links"><a href="/tong-quan-smart-city/">Tổng quan</a><a href="/mua-ban-smart-city/">Mua bán</a><a href="/cho-thue-smart-city/">Cho thuê</a><a href="/dang-tin-smart-city/">Đăng tin</a></nav></div></header>
<main><div class="seo-market-hero"><div class="container"><div class="breadcrumb">{crumbs}</div><p class="eyebrow">Quỹ căn đã duyệt · cập nhật theo dữ liệu marketplace</p><h1>{escape(h1)}</h1><p>{escape(description)} Trang này chỉ được tạo khi có đủ nguồn hàng đang hiển thị, giúp tránh các trang lọc rỗng hoặc nội dung mỏng.</p></div></div>
<div class="container seo-market-summary"><section><h2>{len(rows)} tin đang hiển thị</h2><div class="seo-market-list">{listing_items}</div></section><aside class="seo-market-side"><h2>Mặt bằng giá hiện tại</h2><p>{escape(price_summary(rows, listing_type))}</p><p>Dữ liệu là giá người đăng cung cấp và có thể thay đổi. Nên xác nhận lại trạng thái căn, giá và hồ sơ trước khi đặt cọc.</p><a class="btn" href="{escape(phase_info)}">Xem thông tin phân khu</a><a class="btn btn-primary" href="{escape(filtered_href)}">Mở bộ lọc quỹ {action.lower()}</a></aside></div></main>
<footer class="site-footer"><div class="container footer-grid"><div><a class="brand" href="/"><span class="brand-mark">SC</span><span>SÀN SMART CITY</span></a></div><div><nav class="footer-links"><a href="/giao-dich-smart-city/">Giao dịch</a><a href="/mua-ban-smart-city/">Mua bán</a><a href="/cho-thue-smart-city/">Cho thuê</a><a href="/cam-nang.html">Cẩm nang</a></nav></div></div></footer><script src="/assets/js/site.js" defer></script><script src="/assets/app-shell.js" defer></script></body></html>'''
    return rel, html


def generate_marketplace_landing_pages(site_root: Path, rows: list[dict]) -> list[str]:
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        phase = str(row.get("phase") or "").strip()
        if not phase:
            continue
        listing_type = "rent" if row.get("listing_type") == "rent" else "sale"
        groups[(listing_type, phase, None, None)].append(row)
        if row.get("unit_type"):
            groups[(listing_type, phase, str(row.get("unit_type")), None)].append(row)
        if row.get("tower"):
            groups[(listing_type, phase, None, str(row.get("tower")))].append(row)

    generated = []
    for (listing_type, phase, unit_type, tower), items in groups.items():
        # Phase and phase+unit pages need at least two live listings; tower pages
        # need three. This keeps the index focused on useful demand pages rather
        # than manufacturing thousands of thin filter URLs.
        minimum = 3 if tower else 2
        if len(items) < minimum:
            continue
        items = sorted(
            items,
            key=lambda row: str(row.get("approved_at") or row.get("created_at") or ""),
            reverse=True,
        )
        rel, html = page_html(
            items,
            listing_type=listing_type,
            phase=phase,
            unit_type=unit_type,
            tower=tower,
        )
        target = site_root / rel.strip("/") / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html, encoding="utf-8")
        generated.append(rel)
    print(f"SEO: generated {len(generated)} inventory landing pages")
    return generated
