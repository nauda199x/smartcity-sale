#!/usr/bin/env python3
"""Validate the master floor-plan hub."""

from __future__ import annotations
from pathlib import Path
import json
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
    if len(plan_cards)!=49:
        errors.append(f"expected 49 plan cards, got {len(plan_cards)}")
    if len(missing_cards)!=0:
        errors.append(f"expected 0 missing-plan cards, got {len(missing_cards)}")

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


    manifest_path=ROOT/"data"/"official"/"missing-floorplans-20260901.json"
    if not manifest_path.is_file():
        errors.append("missing 49/49 acquisition manifest")
    else:
        manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("acquired")!=16 or manifest.get("failed"):
            errors.append(f"floorplan acquisition manifest is incomplete: acquired={manifest.get('acquired')}, failed={manifest.get('failed')}")

    required_new_plans={
        "/mat-bang-smart-city/sapphire/s1-01/": "/images/official/floorplans/sapphire-s1-01.webp",
        "/mat-bang-smart-city/sapphire/s1-03/": "/images/official/floorplans/sapphire-s1-03.webp",
        "/mat-bang-smart-city/sapphire/s1-05/": "/images/official/floorplans/sapphire-s1-05.webp",
        "/mat-bang-smart-city/sapphire/s2-01/": "/images/official/floorplans/sapphire-s2-01.webp",
        "/mat-bang-smart-city/sapphire/s2-05/": "/images/official/floorplans/sapphire-s2-05.webp",
        "/mat-bang-smart-city/sapphire/s3-01/": "/images/official/floorplans/sapphire-s3-01.webp",
        "/mat-bang-smart-city/sapphire/s3-02/": "/images/official/floorplans/sapphire-s3-02.webp",
        "/mat-bang-smart-city/sapphire/s4-02/": "/images/official/floorplans/sapphire-s4-02.webp",
        "/mat-bang-smart-city/masteri-west-heights/west-a/": "/images/official/floorplans/masteri-west-a-b.webp",
        "/mat-bang-smart-city/masteri-west-heights/west-b/": "/images/official/floorplans/masteri-west-a-b.webp",
        "/mat-bang-smart-city/masteri-west-heights/west-c/": "/images/official/floorplans/masteri-west-c.webp",
        "/mat-bang-smart-city/masteri-west-heights/west-d/": "/images/official/floorplans/masteri-west-d.webp",
        "/mat-bang-smart-city/lumiere-evergreen/a1/": "/images/official/floorplans/lumiere-a1-the-aqua.webp",
        "/mat-bang-smart-city/lumiere-evergreen/a2/": "/images/official/floorplans/lumiere-a2-the-atmos.webp",
        "/mat-bang-smart-city/lumiere-evergreen/a3/": "/images/official/floorplans/lumiere-a3-the-aura.webp",
        "/mat-bang-smart-city/sola-park/g5/": "/images/official/floorplans/sola-g5-the-avenue.webp",
        "/mat-bang-smart-city/sola-park/g6/": "/images/official/floorplans/sola-g6-the-sky.webp"
    }

    # Once the 4K render manifest exists, the HD paths supersede the older
    # acquisition paths above. Before generation (for example the first PR
    # validation pass), the original paths remain valid.
    hd_manifest_path=ROOT/"data"/"official"/"floorplans-hd-20260902.json"
    hd_by_href={}
    if hd_manifest_path.is_file():
        try:
            hd_manifest=json.loads(hd_manifest_path.read_text(encoding="utf-8"))
            assets=hd_manifest.get("assets",[])
            if hd_manifest.get("tower_count")!=49 or len(assets)!=49:
                errors.append(
                    f"HD floorplan manifest incomplete: tower_count={hd_manifest.get('tower_count')} assets={len(assets)}"
                )
            for asset in assets:
                href=asset.get("href")
                src=asset.get("hd_src")
                if href and src:
                    hd_by_href[href]=src
                if max(int(asset.get("output_width",0)),int(asset.get("output_height",0)))<3840:
                    errors.append(f"HD floorplan below 3840px long edge: {href} -> {asset.get('output_width')}x{asset.get('output_height')}")
                if src and not (ROOT/src.lstrip("/")).is_file():
                    errors.append(f"HD manifest asset missing on disk: {src}")
            if len(hd_by_href)!=49:
                errors.append(f"HD manifest expected 49 unique tower hrefs, got {len(hd_by_href)}")
        except Exception as exc:
            errors.append(f"cannot parse HD floorplan manifest: {exc}")

    card_by_href={}
    for card in plan_cards:
        link=card.select_one("a.card-link[href]")
        img=card.select_one(".floor-hub-card__media img[src]")
        if link and img:
            card_by_href[link["href"]]=img["src"]

    for href,legacy_src in required_new_plans.items():
        expected_src=hd_by_href.get(href,legacy_src)
        if card_by_href.get(href)!=expected_src:
            errors.append(f"new plan not wired on hub: {href} -> {card_by_href.get(href)!r}")
        tower=ROOT/href.lstrip("/")/"index.html"
        if tower.is_file():
            tower_html=tower.read_text(encoding="utf-8")
            if expected_src not in tower_html:
                errors.append(f"new plan not wired on tower page: {href}")
        else:
            errors.append(f"new tower page missing: {href}")

    if hd_by_href:
        # All 49 tower cards must use the tower-specific HD path, not just the
        # 17 drawings added by the earlier completion pass.
        for href,expected_src in hd_by_href.items():
            if card_by_href.get(href)!=expected_src:
                errors.append(f"HD tower card mismatch: {href} -> {card_by_href.get(href)!r}")
            tower=ROOT/href.lstrip("/")/"index.html"
            if tower.is_file() and expected_src not in tower.read_text(encoding="utf-8"):
                errors.append(f"HD floorplan missing from tower page: {href}")

    all_main_imgs=soup.select("main img[src]")
    hot=[img["src"] for img in all_main_imgs if external(img["src"])]
    if hot:
        errors.append("main contains external image hotlinks: "+", ".join(hot))

    hero_stats=[x.get_text(" ",strip=True) for x in soup.select(".floor-hub-stats > div")]
    if not any("49" in x for x in hero_stats): errors.append("49-tower stat missing")
    if not any("49/49" in x for x in hero_stats): errors.append("49/49 plan stat missing")

    if errors:
        print(f"FLOOR HUB VALIDATION FAILED ({len(errors)} errors)")
        for e in errors: print("-",e)
        raise SystemExit(1)
    print("FLOOR HUB VALIDATION PASSED: 10 projects, 49 tower links, 49 direct plan previews, 0 missing, 0 image hotlinks")

if __name__=="__main__":
    main()
