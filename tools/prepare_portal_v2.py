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
    "favicon-32.png","favicon-192.png","favicon-512.png","apple-touch-icon.png","site.webmanifest"
]
dirs=[
    "assets","images",
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

# Apply the site-wide visual identity at staging time so every current and future
# public HTML page receives the same theme without duplicating markup in source files.
theme_link='<link rel="stylesheet" href="/assets/css/modern-ui.css?v=20260831-modern1">'
theme_meta='<meta name="theme-color" content="#12302a">'
themed=0
for html in OUT.rglob("*.html"):
    text=html.read_text(encoding="utf-8")
    if "modern-ui.css" not in text and "</head>" in text:
        text=text.replace("</head>", theme_link + theme_meta + "</head>", 1)
        html.write_text(text, encoding="utf-8")
        themed+=1

print(f"staged clean Smart City portal {OUT} · applied modern UI to {themed} HTML files")
