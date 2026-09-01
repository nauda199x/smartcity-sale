#!/usr/bin/env python3
"""Validate the master floor-plan hub."""

from __future__ import annotations
from pathlib import Path
from urllib.parse import urlsplit
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
PAGE=ROOT/"mat-bang-smart-city"/"index.html"
EXPECTED_IDS={"sapphire","sakura","miami","tonkin","imperia","canopy","sola","victoria","masteri","lumiere"}

def external(src: str) -> bool:
    p=urlsplit(src)
    return bool(p.scheme or p.netloc)

def main():
    errors=[]
    html=PAGE.read_text(encoding="utf-8")
    soup=BeautifulSoup(html,"html.parser")

    sections=soup.select(".floor-hub-section[id]")
    ids={s.get("id") for s in sections}
    if ids!=EXPECTED_IDS:
        errors.append(f"project sections mismatch: {sorted(ids)}")

    jump=soup.select(".floor-hub-jump a[href^='#']")
    if len(jump)!=10:
        errors.append(f"expected 10 project jump links, got {len(jump)}")

    plan_cards=soup.select(".floor-hub-card")
    missing_cards=soup.select(".floor-hub-missing")
    if len(plan_cards)!=32:
        errors.append(f"expected 32 plan cards, got {len(plan_cards)}")
    if len(missing_cards)!=17:
        errors.append(f"expected 17 transparent missing-plan cards, got {len(missing_cards)}")

    tower_links=[]
    for card in plan_cards:
        link=card.select_one("a.card-link[href]")
        if not link:
            errors.append("plan card missing tower link")
            continue
        tower_links.append(link["href"])
        img=card.select_one(".floor-hub-card__media img[src]")
        if not img:
            errors.append(f"plan card missing image: {link['href']}")
            continue
        src=img["src"]
        if external(src):
            errors.append(f"external image hotlink: {src}")
        if not src.startswith("/images/"):
            errors.append(f"non-local plan image: {src}")
        if any(x in src for x in ("/editorial/","hero-smart-city")):
            errors.append(f"placeholder used as plan image: {src}")
        fp=ROOT/src.lstrip("/")
        if not fp.is_file():
            errors.append(f"missing local image file: {src}")
        if not img.get("alt","").strip():
            errors.append(f"missing alt: {src}")
        if not img.get("width") or not img.get("height"):
            errors.append(f"missing dimensions: {src}")

    for card in missing_cards:
        href=card.get("href")
        if not href:
            errors.append("missing-plan card missing href")
        else:
            tower_links.append(href)

    if len(tower_links)!=49:
        errors.append(f"expected 49 tower links, got {len(tower_links)}")
    if len(set(tower_links))!=49:
        errors.append("tower links contain duplicates")

    for href in tower_links:
        if not href.startswith("/mat-bang-smart-city/") or not href.endswith("/"):
            errors.append(f"bad tower href: {href}")
            continue
        target=ROOT/href.lstrip("/")/"index.html"
        if not target.is_file():
            errors.append(f"tower page missing: {href}")

    all_main_imgs=soup.select("main img[src]")
    hot=[img["src"] for img in all_main_imgs if external(img["src"])]
    if hot:
        errors.append("main contains external image hotlinks: "+", ".join(hot))

    hero_stats=[x.get_text(" ",strip=True) for x in soup.select(".floor-hub-stats > div")]
    if not any("49" in x for x in hero_stats): errors.append("49-tower stat missing")
    if not any("32" in x for x in hero_stats): errors.append("32-plan stat missing")

    if errors:
        print(f"FLOOR HUB VALIDATION FAILED ({len(errors)} errors)")
        for e in errors: print("-",e)
        raise SystemExit(1)
    print("FLOOR HUB VALIDATION PASSED: 10 projects, 49 tower links, 32 direct plan previews, 17 explicitly marked missing, 0 image hotlinks")

if __name__=="__main__":
    main()
