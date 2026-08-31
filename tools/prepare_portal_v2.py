#!/usr/bin/env python3
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"_site"
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir()

files=[
    "index.html","404.html","robots.txt","sitemap.xml","CNAME",
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
print("staged clean Smart City portal", OUT)
