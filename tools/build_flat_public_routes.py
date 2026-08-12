from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "https://timmuasmartcity.com"

ROUTES = {
    "_source/blog/index.html": "cam-nang.html",
    "_source/blog/gia-ban-vinhomes-smart-city/index.html": "gia-ban-vinhomes-smart-city.html",
    "_source/blog/chi-phi-mua-can-ho-chuyen-nhuong-vinhomes-smart-city/index.html": "chi-phi-mua-can-ho-chuyen-nhuong-vinhomes-smart-city.html",
    "_source/blog/kinh-nghiem-mua-can-ho-vinhomes-smart-city/index.html": "kinh-nghiem-mua-can-ho-vinhomes-smart-city.html",
    "_source/blog/mua-can-ho-2pn-vinhomes-smart-city/index.html": "mua-can-ho-2pn-vinhomes-smart-city.html",
    "_source/blog/so-sanh-phan-khu-vinhomes-smart-city/index.html": "so-sanh-phan-khu-vinhomes-smart-city.html",
    "_source/blog/masteri-west-heights-smart-city/index.html": "masteri-west-heights-smart-city.html",
    "_source/blog/sapphire-vinhomes-smart-city/index.html": "sapphire-vinhomes-smart-city.html",
    "_source/blog/the-sakura-vinhomes-smart-city/index.html": "the-sakura-vinhomes-smart-city.html",
    "_source/can-ho-dang-ban/index.html": "can-ho-dang-ban.html",
    "_source/phan-khu/index.html": "phan-khu.html",
    "_source/phan-khu/sapphire/index.html": "phan-khu-sapphire.html",
    "_source/phan-khu/the-sakura/index.html": "phan-khu-the-sakura.html",
    "_source/phan-khu/gateway-tower/index.html": "gateway-tower.html",
}

URL_MAP = {
    "/blog/": "/cam-nang.html",
    "/blog/gia-ban-vinhomes-smart-city/": "/gia-ban-vinhomes-smart-city.html",
    "/blog/chi-phi-mua-can-ho-chuyen-nhuong-vinhomes-smart-city/": "/chi-phi-mua-can-ho-chuyen-nhuong-vinhomes-smart-city.html",
    "/blog/kinh-nghiem-mua-can-ho-vinhomes-smart-city/": "/kinh-nghiem-mua-can-ho-vinhomes-smart-city.html",
    "/blog/mua-can-ho-2pn-vinhomes-smart-city/": "/mua-can-ho-2pn-vinhomes-smart-city.html",
    "/blog/so-sanh-phan-khu-vinhomes-smart-city/": "/so-sanh-phan-khu-vinhomes-smart-city.html",
    "/blog/masteri-west-heights-smart-city/": "/masteri-west-heights-smart-city.html",
    "/blog/sapphire-vinhomes-smart-city/": "/sapphire-vinhomes-smart-city.html",
    "/blog/the-sakura-vinhomes-smart-city/": "/the-sakura-vinhomes-smart-city.html",
    "/can-ho-dang-ban/": "/can-ho-dang-ban.html",
    "/phan-khu/": "/phan-khu.html",
    "/phan-khu/sapphire/": "/phan-khu-sapphire.html",
    "/phan-khu/the-sakura/": "/phan-khu-the-sakura.html",
    "/phan-khu/gateway-tower/": "/gateway-tower.html",
}

# Compute public inventory stats at build time so homepage never depends on JS for its key count.
rows = json.loads((ROOT / "data.json").read_text(encoding="utf-8"))
visible = [r for r in rows if isinstance(r, dict) and r.get("Hiển thị trên Web") == "Có"]
missing_image = [r for r in visible if not str(r.get("Ảnh đại diện") or "").strip()]
one_image = []
for r in visible:
    imgs = [x.strip() for x in str(r.get("Danh sách ảnh") or "").splitlines() if x.strip()]
    if len(imgs) == 1:
        one_image.append(r)
stats = {"visible": len(visible), "missing_image": len(missing_image), "one_image": len(one_image), "total_rows": len(rows)}
(ROOT / "data" / "public-stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")


def remove_shared_ga(html: str) -> str:
    # G-VF9KHC5TWD is also used by timthuesmartcity.com. Remove it from the sale portal
    # until a dedicated GA4 stream/property ID is configured, preventing mixed analytics.
    html = re.sub(r'<script async src="https://www\.googletagmanager\.com/gtag/js\?id=G-VF9KHC5TWD"></script>', '', html)
    html = re.sub(r'<script>window\.dataLayer=window\.dataLayer\|\|\[\];function gtag\(\)\{dataLayer\.push\(arguments\)\}gtag\(\'js\',new Date\(\)\);gtag\(\'config\',\'G-VF9KHC5TWD\'\);</script>', '', html)
    return html


def rewrite(html: str, public_path: str) -> str:
    for old, new in sorted(URL_MAP.items(), key=lambda x: -len(x[0])):
        html = html.replace(old, new)
        html = html.replace(DOMAIN + old, DOMAIN + new)
    canonical = DOMAIN + "/" + public_path
    if 'rel="canonical"' in html:
        html = re.sub(r'<link rel="canonical" href="[^"]+">', f'<link rel="canonical" href="{canonical}">', html, count=1)
    else:
        html = html.replace("</head>", f'<link rel="canonical" href="{canonical}"></head>', 1)
    return remove_shared_ga(html)

for src, dst in ROUTES.items():
    source = ROOT / src
    if not source.exists():
        print("skip missing", src)
        continue
    html = rewrite(source.read_text(encoding="utf-8"), dst)
    if dst == "can-ho-dang-ban.html" and 'property="og:title"' not in html:
        og = (
            '<meta property="og:type" content="website">'
            '<meta property="og:url" content="https://timmuasmartcity.com/can-ho-dang-ban.html">'
            '<meta property="og:title" content="Căn hộ đang bán tại Vinhomes Smart City">'
            '<meta property="og:description" content="Quỹ căn chuyển nhượng Vinhomes Smart City: lọc theo phân khu, loại căn, giá, diện tích và nội thất.">'
            '<meta property="og:image" content="https://timmuasmartcity.com/images/hero/hero-smart-city-desktop.webp">'
            '<meta name="twitter:card" content="summary_large_image">'
        )
        html = html.replace("</head>", og + "</head>", 1)
    (ROOT / dst).write_text(html, encoding="utf-8")
    print("built", dst)

# Rewrite homepage and generated flat pages to stable .html URLs.
for path in [ROOT / "index.html"] + [ROOT / p for p in ROUTES.values()]:
    if not path.exists():
        continue
    text = remove_shared_ga(path.read_text(encoding="utf-8"))
    for old, new in sorted(URL_MAP.items(), key=lambda x: -len(x[0])):
        text = text.replace(old, new)
        text = text.replace(DOMAIN + old, DOMAIN + new)
    text = re.sub(r'id="liveCount">[^<]*</strong>', f'id="liveCount">{stats["visible"]}</strong>', text)
    text = text.replace('href="https://zalo.me/0977923284" target="_blank" rel="noopener">Ký gửi', 'href="/ky-gui-ban-can.html">Ký gửi')
    path.write_text(text, encoding="utf-8")

# Sitemap: only stable URLs that do not rely on directory trailing-slash behavior.
sitemap = ROOT / "sitemap.xml"
if sitemap.exists():
    text = sitemap.read_text(encoding="utf-8")
    for old, new in sorted(URL_MAP.items(), key=lambda x: -len(x[0])):
        text = text.replace(DOMAIN + old, DOMAIN + new)
    for extra, priority in [
        ("/can-ho-dang-ban.html", "0.95"),
        ("/ky-gui-ban-can.html", "0.8"),
        ("/chinh-sach-bao-mat.html", "0.4"),
        ("/dieu-khoan-su-dung.html", "0.4"),
    ]:
        url = DOMAIN + extra
        if url not in text:
            text = text.replace("</urlset>", f'  <url><loc>{url}</loc><lastmod>2026-08-12</lastmod><changefreq>monthly</changefreq><priority>{priority}</priority></url>\n</urlset>')
    sitemap.write_text(text, encoding="utf-8")

print("public stats", stats)
