#!/usr/bin/env python3
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"_site"
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir()

files=[
    "index.html","404.html","gateway-tower.html","robots.txt","sitemap.xml","sitemap-images.xml","CNAME",
    "favicon.ico","favicon-32.png","favicon-192.png","favicon-512.png","apple-touch-icon.png","site.webmanifest",
    "data.json",
    # Editorial / SEO assets with unique intent. Project-profile duplicates stay on
    # their canonical /phan-khu-smart-city/ routes instead of being staged twice.
    "cam-nang.html",
    "chi-phi-mua-can-ho-chuyen-nhuong-vinhomes-smart-city.html",
    "chon-tang-huong-view-can-ho-vinhomes-smart-city.html",
    "gia-ban-vinhomes-smart-city.html",
    "kiem-tra-phap-ly-can-ho-vinhomes-smart-city-truoc-dat-coc.html",
    "kinh-nghiem-mua-can-ho-vinhomes-smart-city.html",
    "mua-can-ho-2pn-vinhomes-smart-city.html",
    "mua-can-ho-vinhomes-smart-city-de-o-hay-dau-tu.html",
    "quy-trinh-chuyen-nhuong-can-ho-vinhomes-smart-city.html",
    "so-sanh-phan-khu-vinhomes-smart-city.html",
    "ban-can-ho-2pn-vinhomes-smart-city.html",
    "ban-can-ho-duoi-4-ty-vinhomes-smart-city.html",
    "ban-can-ho-sapphire-smart-city.html",
    "ban-studio-vinhomes-smart-city.html",
    "chinh-sach-bao-mat.html","dieu-khoan-su-dung.html"
]
dirs=[
    "assets","images","blog",
    "tong-quan-smart-city","vi-tri-smart-city","mat-bang-smart-city","tien-ich-smart-city",
    "phan-khu-smart-city","gia-smart-city",
    "giao-dich-smart-city","mua-ban-smart-city","cho-thue-smart-city",
    "dang-tin-smart-city","tin-dang-smart-city","admin"
]
for name in files:
    src=ROOT/name
    if src.exists():
        shutil.copy2(src,OUT/name)
for name in dirs:
    src=ROOT/name
    if src.exists():
        shutil.copytree(src,OUT/name)

# Keep legacy URLs that Google may still know alive long enough to migrate users
# to the current canonical hub. GitHub Pages cannot emit per-path HTTP 301s, so
# these tiny zero-second meta-refresh pages act as legacy redirects. They are
# noindex so the SEO builder keeps them out of sitemaps while the canonical URL
# remains the only indexable phân-khu hub.
legacy_redirects={
    "phan-khu.html":"/phan-khu-smart-city/",
    "phan-khu/index.html":"/phan-khu-smart-city/",
}
for rel_path,destination in legacy_redirects.items():
    target=OUT/rel_path
    target.parent.mkdir(parents=True,exist_ok=True)
    canonical_url=f"https://timmuasmartcity.com{destination}"
    target.write_text(
        "<!doctype html><html lang=\"vi\"><head>"
        "<meta charset=\"utf-8\">"
        f"<meta http-equiv=\"refresh\" content=\"0;url={destination}\">"
        f"<link rel=\"canonical\" href=\"{canonical_url}\">"
        "<meta name=\"robots\" content=\"noindex,follow\">"
        "<title>Phân khu Vinhomes Smart City</title>"
        "</head><body>"
        f"<p>Trang đã chuyển sang <a href=\"{destination}\">Phân khu Smart City</a>.</p>"
        "</body></html>",
        encoding="utf-8",
    )

# Apply the site-wide visual identity at staging time so every current and future
# public HTML page receives the same theme without duplicating markup in source files.
theme_link='<link rel="stylesheet" href="/assets/css/modern-ui.css?v=20260901-homeoverview2">'
site_theme_link='<link rel="stylesheet" href="/assets/css/site-theme.css?v=20260902-1">'
theme_meta='<meta name="theme-color" content="#0e211c">'
shell_script='<script src="/assets/app-shell.js?v=20260901-shellfix1" defer></script>'
themed=0
for html in OUT.rglob("*.html"):
    text=html.read_text(encoding="utf-8")
    if "modern-ui.css" not in text and "</head>" in text:
        text=text.replace("</head>", theme_link + theme_meta + "</head>", 1)
        html.write_text(text, encoding="utf-8")
        themed+=1
    if "</head>" in text:
        # The posting-page language must remain the final cascade layer.
        text=text.replace(site_theme_link,"")
        text=text.replace("</head>",site_theme_link+"</head>",1)
        html.write_text(text,encoding="utf-8")
    if "app-shell.js" not in text and "</body>" in text:
        text=text.replace("</body>", shell_script + "</body>", 1)
        html.write_text(text, encoding="utf-8")

print(f"staged clean Smart City portal {OUT} · applied modern UI to {themed} HTML files")
