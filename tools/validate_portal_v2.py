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
 "tong-quan-smart-city/index.html",
 "vi-tri-smart-city/index.html",
 "mat-bang-smart-city/index.html",
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
 "assets/js/marketplace-api.js"
]
errors=[]
for rel in required:
    if not (ROOT/rel).exists():
        errors.append(f"missing required file: {rel}")

htmls=[p for p in ROOT.rglob("*.html") if "_source" not in p.parts and "_site" not in p.parts]
for p in htmls:
    text=p.read_text("utf-8",errors="replace")
    rel=p.relative_to(ROOT)
    if "<title>" not in text:
        errors.append(f"{rel}: missing title")
    if "lumi-hanoi.com" in text or "salsyqatlzapnzbcnnsr" in text:
        errors.append(f"{rel}: Lumi project contamination")
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

cfg=ROOT/"assets/js/marketplace-config.js"
if cfg.exists():
    c=cfg.read_text("utf-8",errors="replace")
    if "owwqrgwezuwonwdzphie.supabase.co" not in c:
        errors.append("marketplace-config.js: wrong Supabase project")
    if "sb_publishable_" not in c:
        errors.append("marketplace-config.js: publishable key missing")

if errors:
    print(f"PORTAL VALIDATION FAILED ({len(errors)} errors)")
    for e in errors[:80]:
        print("-",e)
    sys.exit(1)
print(f"PORTAL VALIDATION PASSED: {len(htmls)} HTML pages")
