#!/usr/bin/env python3
"""Validate the unified real-estate design system and critical shell fixes."""

from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
errors=[]

modern=(ROOT/"assets/css/modern-ui.css").read_text(encoding="utf-8")
shell=(ROOT/"assets/app-shell.js").read_text(encoding="utf-8")
home=(ROOT/"index.html").read_text(encoding="utf-8")
overview=(ROOT/"tong-quan-smart-city"/"index.html").read_text(encoding="utf-8")
hub=(ROOT/"phan-khu-smart-city/index.html").read_text(encoding="utf-8")
market=(ROOT/"assets/js/marketplace-list.js").read_text(encoding="utf-8")
stage=(ROOT/"tools/prepare_portal_v2.py").read_text(encoding="utf-8")

for token in (
    "REAL ESTATE PORTAL UI 2026",
    ".listing-card--marketplace",
    ".detail-shell--portal",
    ".marketplace-toolbar",
    ".mobile-property-nav",
    ".home-v2-hero",
    ".home-v2-finder",
    ".overview-v2-hero",
    ".overview-v2-steps",
    ".floor-hub-card",
    ".form-section--premium",
):
    if token not in modern:
        errors.append(f"modern UI missing {token}")

legacy_routes=("/phan-khu.html","/gia-ban-vinhomes-smart-city.html","/can-ho-dang-ban.html","/ky-gui-ban-can.html")
for route in legacy_routes:
    if route in shell:
        errors.append(f"legacy app-shell route remains: {route}")
if "outerHTML" in shell:
    errors.append("app-shell still replaces canonical header/footer")
if "mobile-property-nav" not in shell or "nav-direct-cta" not in shell:
    errors.append("shell enhancer missing property navigation")

if "home-v2-hero" not in home or "home-v2-finder" not in home:
    errors.append("premium homepage structure missing")
if "overview-v2-hero" not in overview or "overview-v2-steps" not in overview:
    errors.append("premium overview structure missing")
if re.search(r'<img[^>]+src="https?://',home):
    errors.append("homepage still contains image hotlinks")
if re.search(r'<img[^>]+src="https?://',overview):
    errors.append("overview still contains image hotlinks")
if re.search(r'<a[^>]+href="https?://',overview):
    errors.append("overview still exposes outbound source links")
if re.search(r'>\s*(Nguồn|Mở nguồn|Source)\b',overview,re.I):
    errors.append("overview still exposes source-labelled UI")
if re.search(r'<img[^>]+src="https?://',hub):
    errors.append("project hub still contains image hotlinks")
if "/images/official/sapphire/sapphire-tong-the-thuc-te.webp" not in home:
    errors.append("homepage Sapphire card is not using real local Sapphire imagery")
if "/images/official/sapphire/sapphire-tong-the-thuc-te.webp" not in hub:
    errors.append("project hub Sapphire card is not using real local Sapphire imagery")
if "/images/projects/sapphire/archive/s4-03.jpg" in hub:
    errors.append("project hub regressed to Sapphire floor-plan image")

if "marketplace-sort" not in market or "price-asc" not in market or "area-desc" not in market:
    errors.append("marketplace sort control missing")
if "20260901-homeoverview2" not in stage:
    errors.append("staging does not inject latest homepage/overview stylesheet")
if "app-shell.js" not in stage:
    errors.append("staging does not ensure shell enhancer")

if modern.count("@media(max-width:760px)") < 1:
    errors.append("mobile breakpoint missing")
if "--re-brand:#0c7a62" not in modern:
    errors.append("brand token missing")

if errors:
    print(f"REAL ESTATE UI VALIDATION FAILED ({len(errors)} errors)")
    for e in errors:
        print("-",e)
    raise SystemExit(1)

print("REAL ESTATE UI VALIDATION PASSED: premium homepage + overview, unified shell, local media, marketplace sorting, desktop/mobile portal styling")
