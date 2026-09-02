#!/usr/bin/env python3
"""Validate the visual floor-plan directory and project-integrated HD cards."""
from __future__ import annotations
from pathlib import Path
import json
from urllib.parse import urlsplit
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
PAGE=ROOT/"mat-bang-smart-city"/"index.html"
MANIFEST=ROOT/"data"/"official"/"floorplans-hd-20260902.json"
PHASES=("sapphire","sakura","miami","tonkin","imperia","canopy","sola-park","victoria","masteri-west-heights","lumiere-evergreen")

def external(src:str)->bool:
    p=urlsplit(src); return bool(p.scheme or p.netloc)

def main():
    errors=[]
    data=json.loads(MANIFEST.read_text(encoding="utf-8")); assets=data.get("assets",[])
    if data.get("tower_count")!=49 or len(assets)!=49:
        errors.append(f"HD manifest incomplete: tower_count={data.get('tower_count')} assets={len(assets)}")
    hd={}
    for a in assets:
        href=a.get("href",""); src=a.get("hd_src","")
        if not href or not src: errors.append(f"manifest asset missing href/src: {a}"); continue
        hd[href]=src
        if max(int(a.get("output_width",0)),int(a.get("output_height",0)))<3840: errors.append(f"HD image below 3840px: {href}")
        if not (ROOT/src.lstrip("/")).is_file(): errors.append(f"HD image missing: {src}")
    if len(hd)!=49: errors.append(f"expected 49 unique manifest hrefs, got {len(hd)}")

    soup=BeautifulSoup(PAGE.read_text(encoding="utf-8"),"html.parser")
    dirs=soup.select(".floor-directory-card[href]")
    if len(dirs)!=10: errors.append(f"expected 10 directory cards, got {len(dirs)}")
    expected={f"/phan-khu-smart-city/{s}/#mat-bang-tung-toa" for s in PHASES}
    if {x.get("href") for x in dirs}!=expected: errors.append("directory links do not match phase dossiers")
    stats=" ".join(x.get_text(" ",strip=True) for x in soup.select(".floor-directory-stats > div"))
    for req in ("10","49","49/49"):
        if req not in stats: errors.append(f"directory stat missing {req}")

    cards={}
    for slug in PHASES:
        p=ROOT/"phan-khu-smart-city"/slug/"index.html"
        ps=BeautifulSoup(p.read_text(encoding="utf-8"),"html.parser")
        sec=ps.select_one("#mat-bang-tung-toa.phase-floorplans")
        if not sec: errors.append(f"{slug}: missing integrated floor-plan section"); continue
        for card in sec.select(".phase-floorplan-card[href]"):
            href=card.get("href",""); img=card.select_one("img[src]")
            if not img: errors.append(f"{slug}: card missing image {href}"); continue
            src=img.get("src","")
            if external(src) or not src.startswith("/images/official/floorplans-hd/"): errors.append(f"{slug}: bad HD src {src}")
            if not img.get("width") or not img.get("height") or not img.get("alt","").strip(): errors.append(f"{slug}: image metadata incomplete {href}")
            cards[href]=src
    if len(cards)!=49: errors.append(f"expected 49 integrated tower cards, got {len(cards)}")
    if set(cards)!=set(hd): errors.append("integrated tower links do not match HD manifest")
    for href,src in hd.items():
        if cards.get(href)!=src: errors.append(f"phase card HD mismatch: {href}")
        tp=ROOT/href.lstrip("/")/"index.html"
        if not tp.is_file(): errors.append(f"tower page missing: {href}")
        elif src not in tp.read_text(encoding="utf-8"): errors.append(f"tower page missing HD src: {href}")
    if errors:
        print(f"FLOOR DIRECTORY VALIDATION FAILED ({len(errors)} errors)")
        for e in errors: print("-",e)
        raise SystemExit(1)
    print("FLOOR DIRECTORY VALIDATION PASSED: 10 phase dossiers, 49 integrated HD cards, 49 tower pages")
if __name__=="__main__": main()
