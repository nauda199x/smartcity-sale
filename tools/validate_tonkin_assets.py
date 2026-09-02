#!/usr/bin/env python3
"""Validate The Tonkin dossier and local image pack."""

from __future__ import annotations
import hashlib, json, re
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit
from bs4 import BeautifulSoup
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"data"/"official"/"tonkin-assets.json"
PAGE=ROOT/"phan-khu-smart-city"/"tonkin"/"index.html"
HUB=ROOT/"mat-bang-smart-city"/"tonkin"/"index.html"
TOWERS={c:ROOT/"mat-bang-smart-city"/"tonkin"/c/"index.html" for c in ("tk1","tk2")}
PREFIX="/images/official/tonkin/"
EXPECTED={"actual":5,"diagram":3}
LEGACY_PLANS={"tk1":PREFIX+"tonkin-mat-bang-tk1.webp","tk2":PREFIX+"tonkin-mat-bang-tk2.webp"}
PLANS={"tk1":"/images/official/floorplans-hd/tonkin-tk1.webp","tk2":"/images/official/floorplans-hd/tonkin-tk2.webp"}
TOTAL=PREFIX+"tonkin-tong-mat-bang.webp"

def digest(path):
    h=hashlib.sha1()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def external(v):
    p=urlsplit(v)
    return bool(p.scheme or p.netloc)

def main():
    errors=[]
    data=json.loads(MANIFEST.read_text(encoding="utf-8"))
    assets=data.get("assets",[])
    if data.get("count")!=len(assets): errors.append("manifest count mismatch")
    if len(assets)!=8: errors.append(f"expected 8 assets, got {len(assets)}")
    mix=Counter(); locals=set(); dims={}
    for i,a in enumerate(assets,1):
        local=a.get("local_path",""); typ=a.get("media_type")
        if not local.startswith(PREFIX): errors.append(f"asset {i}: bad local path")
        if local in locals: errors.append(f"asset {i}: duplicate local path")
        locals.add(local)
        if typ not in EXPECTED: errors.append(f"asset {i}: bad media type {typ}")
        else: mix[typ]+=1
        path=ROOT/local.lstrip("/")
        if not path.is_file(): errors.append(f"asset {i}: missing {local}"); continue
        try:
            with Image.open(path) as im:
                im.load()
                if im.format!="WEBP": errors.append(f"asset {i}: not WEBP")
                if im.size!=(a.get("width"),a.get("height")): errors.append(f"asset {i}: dimension mismatch")
                dims[local]=im.size
        except OSError as exc: errors.append(f"asset {i}: unreadable {exc}")
        if a.get("bytes")!=path.stat().st_size: errors.append(f"asset {i}: byte mismatch")
        if a.get("sha1")!=digest(path): errors.append(f"asset {i}: sha mismatch")
    if mix!=Counter(EXPECTED): errors.append(f"media mix {dict(mix)} != {EXPECTED}")

    html=PAGE.read_text(encoding="utf-8"); soup=BeautifulSoup(html,"html.parser")
    if re.search(r">\s*(Nguồn|Mở nguồn|Source)\b",html,re.I): errors.append("public source UI present")
    if [a["href"] for a in soup.find_all("a",href=True) if external(a["href"])]: errors.append("external links present")
    tags=soup.find_all("img",src=True); images=[t["src"] for t in tags]
    if [x for x in images if external(x)]: errors.append("image hotlinks present")
    expected_images=(locals-set(LEGACY_PLANS.values()))|set(PLANS.values())
    if set(images)!=expected_images: errors.append(f"main image set differs: unused={sorted(expected_images-set(images))}, undeclared={sorted(set(images)-expected_images)}")
    repeated=[x for x,n in Counter(images).items() if n>1 and not x.startswith("/images/official/floorplans-hd/")]
    if repeated: errors.append("main repeats images: "+", ".join(repeated))
    for t in tags:
        src=t["src"]
        if not t.get("alt","").strip(): errors.append(f"missing alt {src}")
        if src in dims:
            try: wh=(int(t.get("width","")),int(t.get("height","")))
            except ValueError: wh=(-1,-1)
            if wh!=dims[src]: errors.append(f"HTML dimensions mismatch {src}: {wh} != {dims[src]}")
    text=soup.get_text(" ",strip=True)
    words=len(re.findall(r"\b\w+\b",text,re.UNICODE))
    if words<3500: errors.append(f"page too thin: {words} words")
    for req in ("TK1","TK2","1.172","586","38 tầng","16 căn","7 thang","1,8m","Maison Détox","The Goddess"):
        if req not in text: errors.append(f"missing fact {req}")
    if "1.200" in text: errors.append("rounded 1.200 total remains on public page")
    if re.search(r"\b6 căn/sàn\b",text): errors.append("stale 6-apartment typo remains")
    if "FAQPage" not in html or len(soup.select(".tonkin-faq details"))<8: errors.append("FAQ incomplete")

    for label,path in {"hub":HUB,**TOWERS}.items():
        h=path.read_text(encoding="utf-8"); s=BeautifulSoup(h,"html.parser")
        if any(external(t["src"]) for t in s.find_all("img",src=True)): errors.append(f"{label}: image hotlink")
        if re.search(r">\s*(Nguồn|Mở nguồn|Source)\b",h,re.I): errors.append(f"{label}: source UI")
    hub_html=HUB.read_text(encoding="utf-8")
    if TOTAL not in hub_html: errors.append("hub missing total plan")
    for code,plan in PLANS.items():
        if plan not in hub_html: errors.append(f"hub missing {code} plan")
        th=TOWERS[code].read_text(encoding="utf-8")
        if plan not in th: errors.append(f"{code}: missing matching plan")
        if "586 căn" not in th or "16 căn/sàn" not in th: errors.append(f"{code}: missing core tower facts")
        s=BeautifulSoup(th,"html.parser")
        hero=s.select_one(".article-hero-media")
        if not hero or not hero.get("src","").startswith(PREFIX) or hero.get("src")==plan: errors.append(f"{code}: missing local real-image hero")
    if "7 thang" not in TOWERS["tk1"].read_text(encoding="utf-8"): errors.append("TK1 missing lift count")
    if "7 thang" not in TOWERS["tk2"].read_text(encoding="utf-8"): errors.append("TK2 missing lift count")

    if errors:
        print(f"TONKIN VALIDATION FAILED ({len(errors)} errors)")
        for e in errors: print("-",e)
        raise SystemExit(1)
    print(f"TONKIN VALIDATION PASSED: 8 traced WebP files ({dict(mix)}), {words} public words, 9 FAQ items, no public source UI/hotlinks, TK1-TK2 plans local")

if __name__=="__main__": main()
