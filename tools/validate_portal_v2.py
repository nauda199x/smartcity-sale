#!/usr/bin/env python3
from pathlib import Path
from urllib.parse import urlsplit
import argparse,re,sys

parser=argparse.ArgumentParser()
parser.add_argument("--root",default=".")
args=parser.parse_args()
ROOT=Path(args.root).resolve()

required=[
 "index.html",
 "gateway-tower.html",
 "sitemap-images.xml",
 "tong-quan-smart-city/index.html",
 "vi-tri-smart-city/index.html",
 "mat-bang-smart-city/index.html",
 "tien-ich-smart-city/index.html",
 "phan-khu-smart-city/index.html",
 "gia-smart-city/index.html",
 "giao-dich-smart-city/index.html",
 "mua-ban-smart-city/index.html",
 "cho-thue-smart-city/index.html",
 "dang-tin-smart-city/index.html",
 "tin-dang-smart-city/index.html",
 "admin/index.html",
 "assets/css/site.css",
 "assets/css/marketplace.css",
 "assets/js/site.js",
 "assets/js/marketplace-config.js",
 "assets/js/marketplace-api.js",
 "assets/js/marketplace-list.js",
 "assets/js/marketplace-form.js",
 "assets/js/marketplace-detail.js"
]
errors=[]
for rel in required:
    if not (ROOT/rel).exists():
        errors.append(f"missing required file: {rel}")

public_html=[ROOT/"index.html", ROOT/"404.html", ROOT/"gateway-tower.html"]
for dirname in [
    "tong-quan-smart-city","vi-tri-smart-city","mat-bang-smart-city","tien-ich-smart-city",
    "phan-khu-smart-city","gia-smart-city","giao-dich-smart-city",
    "mua-ban-smart-city","cho-thue-smart-city","dang-tin-smart-city",
    "tin-dang-smart-city","admin"
]:
    d=ROOT/dirname
    if d.exists():
        public_html.extend(d.rglob("*.html"))
htmls=[]
seen=set()
for p in public_html:
    if p.exists() and p not in seen:
        seen.add(p); htmls.append(p)

for p in htmls:
    text=p.read_text("utf-8",errors="replace")
    rel=p.relative_to(ROOT)
    if "<title>" not in text:
        errors.append(f"{rel}: missing title")
    if "lumi-hanoi.com" in text or "salsyqatlzapnzbcnnsr" in text:
        errors.append(f"{rel}: Lumi project contamination")
    lowered=text.lower()
    if "drive.google.com" in lowered or "docs.google.com" in lowered:
        errors.append(f"{rel}: public Google Drive/Docs link is not allowed")
    forbidden_public_copy=["mở file drive","mở tài liệu gốc","nguồn tài liệu","drive cũ"]
    if any(token in lowered for token in forbidden_public_copy):
        errors.append(f"{rel}: internal source/archive copy leaked into public page")
    if "YOUR_PROJECT.supabase.co" in text or "YOUR_PUBLISHABLE_KEY" in text:
        errors.append(f"{rel}: placeholder backend config")
    for href in re.findall(r'href=["\']([^"\']+)["\']',text):
        if href.startswith(("#","mailto:","tel:","javascript:","https://","http://")):
            continue
        path=urlsplit(href).path
        if not path.startswith("/"):
            continue
        target=ROOT/path.lstrip("/")
        if path.endswith("/"):
            target=target/"index.html"
        elif not target.suffix:
            target=target/"index.html"
        if not target.exists():
            errors.append(f"{rel}: broken local href {href}")
    for src in re.findall(r'<img\b[^>]*\bsrc=["\']([^"\']+)["\']', text, flags=re.I):
        if src.startswith(("data:", "https://", "http://")):
            continue
        path=urlsplit(src).path
        if not path.startswith("/"):
            continue
        target=ROOT/path.lstrip("/")
        if not target.is_file():
            errors.append(f"{rel}: broken local image {src}")

cfg=ROOT/"assets/js/marketplace-config.js"
if cfg.exists():
    c=cfg.read_text("utf-8",errors="replace")
    if "owwqrgwezuwonwdzphie.supabase.co" not in c:
        errors.append("marketplace-config.js: wrong Supabase project")
    if "sb_publishable_" not in c:
        errors.append("marketplace-config.js: publishable key missing")

if errors:
    print(f"PORTAL VALIDATION FAILED ({len(errors)} errors)")
    for e in errors[:100]:
        print("-",e)
    sys.exit(1)
print(f"PORTAL VALIDATION PASSED: {len(htmls)} HTML pages")
