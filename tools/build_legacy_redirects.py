"""Build compatibility pages for historical directory URLs.

GitHub Pages has no redirect rules. These noindex pages preserve old inbound URLs and
send visitors to the one canonical, flat `.html` route without a slash rewrite loop.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "https://timmuasmartcity.com"
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

for old, new in sorted(URL_MAP.items()):
    output = ROOT / old.lstrip("/") / "index.html"
    target = DOMAIN + new
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        f'''<!doctype html><html lang="vi"><head><meta charset="utf-8">
<meta name="robots" content="noindex,follow"><meta http-equiv="refresh" content="0; url={new}">
<link rel="canonical" href="{target}"><title>Đang chuyển trang…</title></head>
<body><p>Trang đã chuyển tới <a href="{new}">{target}</a>.</p></body></html>\n''',
        encoding="utf-8",
    )
    print("redirect", old, "->", new)
