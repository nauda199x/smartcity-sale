#!/usr/bin/env python3
"""Validate The Miami local assets and public dossier/plan cluster."""

from __future__ import annotations
import hashlib, json, re
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit
from bs4 import BeautifulSoup
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"data"/"official"/"miami-assets.json"
PAGE=ROOT/"phan-khu-smart-city"/"miami"/"index.html"
HUB=ROOT/"mat-bang-smart-city"/"miami"/"index.html"
TOWERS={c:ROOT/"mat-bang-smart-city"/"miami"/c/"index.html" for c in ("gs1","gs2","gs3","gs5","gs6")}
PREFIX="/images/official/miami/"
EXPECTED={"actual":5,"diagram":5}
LEGACY_PLANS={c:f"{PREFIX}miami-mat-bang-{c}.webp" for c in TOWERS}
PLANS={c:f"/images/official/floorplans-hd/miami-{c}.webp" for c in TOWERS}

def digest(path):
    h=hashlib.sha1()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def external(v):
    p=urlsplit(v); return bool(p.scheme or p.netloc)

def main():
    errors=[]
    data=json.loads(MANIFEST.read_text(encoding="utf-8"))
    assets=data.get("assets",[])
    if data.get("count")!=len(assets): errors.append("manifest count mismatch")
    if len(assets)!=10: errors.append(f"expected 10 assets, got {len(assets)}")
    mix=Counter(); locals=set(); dims={}
    for i,a in enumerate(assets,1):
        local=a.get("local_path",""); typ=a.get("media_type")
        if not local.startswith(PREFIX): errors.append(f"asset {i}: bad local path")
        if local in locals: errors.append(f"asset {i}: duplicate local path {local}")
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
    extlinks=[a["href"] for a in soup.find_all("a",href=True) if external(a["href"])]
    if extlinks: errors.append("external links present")
    tags=soup.find_all("img",src=True); images=[t["src"] for t in tags]
    hot=[x for x in images if external(x)]
    if hot: errors.append("image hotlinks present")
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
    for req in ("GS1","GS2","GS3","GS5","GS6","3,3ha","30 căn","19 căn","16 vị trí","1.000m²","Grand Sapphire"):
        if req not in text: errors.append(f"missing fact {req}")
    if "FAQPage" not in html or len(soup.select(".miami-faq details"))<8: errors.append("FAQ incomplete")

    cluster={"hub":HUB,**TOWERS}
    for label,path in cluster.items():
        h=path.read_text(encoding="utf-8"); s=BeautifulSoup(h,"html.parser")
        if any(external(t["src"]) for t in s.find_all("img",src=True)): errors.append(f"{label}: image hotlink")
        if re.search(r">\s*(Nguồn|Mở nguồn|Source)\b",h,re.I): errors.append(f"{label}: source UI")
    hub=HUB.read_text(encoding="utf-8")
    for code,plan in PLANS.items():
        if plan not in hub: errors.append(f"hub missing {code} plan")
        th=TOWERS[code].read_text(encoding="utf-8")
        if plan not in th: errors.append(f"{code} page missing plan")
    if "16 căn/sàn" not in TOWERS["gs5"].read_text(encoding="utf-8"): errors.append("GS5 missing 16 density")
    if "16 căn/sàn" not in TOWERS["gs6"].read_text(encoding="utf-8"): errors.append("GS6 missing 16 density")

    if errors:
        print(f"MIAMI VALIDATION FAILED ({len(errors)} errors)")
        for e in errors: print("-",e)
        raise SystemExit(1)
    print(f"MIAMI VALIDATION PASSED: 10 traced WebP files ({dict(mix)}), {words} public words, no public source UI/hotlinks, GS5/GS6 plans local and 16-apartment typical density")

if __name__=="__main__": main()
