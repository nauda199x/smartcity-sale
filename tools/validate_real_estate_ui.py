#!/usr/bin/env python3
"""Validate the unified real-estate design system and critical shell fixes."""

from pathlib import Path
import json
import re
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
errors=[]

modern=(ROOT/"assets/css/modern-ui.css").read_text(encoding="utf-8")
shell=(ROOT/"assets/app-shell.js").read_text(encoding="utf-8")
home=(ROOT/"index.html").read_text(encoding="utf-8")
overview=(ROOT/"tong-quan-smart-city"/"index.html").read_text(encoding="utf-8")
hub=(ROOT/"phan-khu-smart-city/index.html").read_text(encoding="utf-8")
market=(ROOT/"assets/js/marketplace-list.js").read_text(encoding="utf-8")
stage=(ROOT/"tools/prepare_portal_v2.py").read_text(encoding="utf-8")
theme=(ROOT/"assets/css/site-theme.css").read_text(encoding="utf-8")
manifest=json.loads((ROOT/"site.webmanifest").read_text(encoding="utf-8"))
brand_logo=(ROOT/"assets/brand/timmua-smartcity-logo.svg").read_text(encoding="utf-8")

if "<span>SÀN SMART CITY</span>" not in home:
    errors.append("homepage header is missing the Sàn Smart City identity")
home_title_match=re.search(r"<title>(.*?)</title>",home,re.I|re.S)
home_title=(home_title_match.group(1) if home_title_match else "").replace("&amp;","&")
if not ("Vinhomes Smart City" in home_title and "mua bán" in home_title.lower() and "cho thuê" in home_title.lower()):
    errors.append("homepage SEO title must cover Vinhomes Smart City + mua bán + cho thuê intent")
if '"name":"Sàn Smart City"' not in home or '"alternateName":"timmuasmartcity.com"' not in home:
    errors.append("homepage WebSite schema is missing the new name or domain alias")
if manifest.get("name") != "Sàn Smart City" or manifest.get("short_name") != "Sàn SC":
    errors.append("web manifest still exposes an outdated site name")
if "SÀN SMART CITY" not in brand_logo or "MUA BÁN • CHO THUÊ • ĐĂNG CĂN" not in brand_logo:
    errors.append("full brand logo is missing the new name or transaction line")

legacy_brand = "Tìm" + " Mua Smart City"
for page in ROOT.rglob("*.html"):
    relative=page.relative_to(ROOT)
    if any(part in {".git","_site"} for part in relative.parts):
        continue
    if legacy_brand in page.read_text(encoding="utf-8",errors="replace"):
        errors.append(f"legacy brand name remains in {relative}")

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
if "/assets/css/home-overview.css?v=20260901-pro1" not in home:
    errors.append("homepage is not directly linked to robust home-overview CSS")
if "/assets/css/home-overview.css?v=20260901-pro1" not in overview:
    errors.append("overview is not directly linked to robust home-overview CSS")
if "<h1>Vinhomes Smart City</h1>" not in home:
    errors.append("homepage hero title regressed")
if "<h1>Tổng quan Vinhomes Smart City</h1>" not in overview:
    errors.append("overview hero title regressed")
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
if "site-theme.css?v=20260902-1" not in stage:
    errors.append("staging does not inject the site-wide posting theme")

for token in (
    "SÀN SMART CITY — SITE THEME 2026-09-02",
    "--sc-green:#0b6b57",
    "--sc-blue:#1588df",
    "--sc-dark:#0e211c",
    "--sc-gradient:linear-gradient(100deg,#16a777 0%,#1588df 100%)",
    "font-family:var(--sc-font)!important",
    ".brand-mark,.site-brand__mark",
    ".listing-card--marketplace",
    ".form-section--premium",
    ".site-footer",
    "@media(max-width:760px)",
):
    if token not in theme:
        errors.append(f"site-wide posting theme missing {token}")

theme_prefix="/assets/css/site-theme.css?v=20260902-"
for page in ROOT.rglob("*.html"):
    relative=page.relative_to(ROOT)
    if any(part in {".git","_site"} for part in relative.parts):
        continue
    text=page.read_text(encoding="utf-8",errors="replace")
    soup=BeautifulSoup(text,"html.parser")
    styles=[
        link.get("href","")
        for link in soup.find_all("link")
        if "stylesheet" in (link.get("rel") or [])
    ]
    if not any(href.startswith(theme_prefix) for href in styles):
        errors.append(f"site-wide posting theme not linked from {relative}")
        continue
    if not styles or not styles[-1].startswith(theme_prefix):
        errors.append(f"site-wide posting theme is not the final stylesheet in {relative}")

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
