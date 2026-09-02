#!/usr/bin/env python3
"""Fail CI on SEO regressions in staged _site."""
from pathlib import Path
from urllib.parse import urlsplit
import re
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/"_site"
DOMAIN="https://timmuasmartcity.com"
NS={"sm":"http://www.sitemaps.org/schemas/sitemap/0.9"}


def html_for(url:str)->Path:
    path=urlsplit(url).path
    if path=="/":
        return SITE/"index.html"
    target=SITE/path.lstrip("/")
    if path.endswith("/"):
        return target/"index.html"
    return target


def canonical(text:str)->str:
    soup=BeautifulSoup(text,"html.parser")
    for link in soup.find_all("link"):
        rel=link.get("rel") or []
        if "canonical" in rel:
            return str(link.get("href") or "").strip()
    return ""


def noindex(text:str)->bool:
    soup=BeautifulSoup(text,"html.parser")
    for meta in soup.find_all("meta"):
        if str(meta.get("name") or "").lower()=="robots":
            return "noindex" in str(meta.get("content") or "").lower()
    return False


def main():
    errors=[]
    required=["sitemap.xml","sitemap-pages.xml","sitemap-floorplans.xml","sitemap-listings.xml","sitemap-images.xml","robots.txt"]
    for name in required:
        if not (SITE/name).is_file():
            errors.append(f"missing {name}")

    if errors:
        raise SystemExit("\n".join(errors))

    if not (SITE/"assets/css/site-theme.css").is_file():
        errors.append("missing staged site-wide theme stylesheet")

    theme_prefix="/assets/css/site-theme.css?v=20260902-"
    for page in SITE.rglob("*.html"):
        text=page.read_text(encoding="utf-8",errors="replace")
        soup=BeautifulSoup(text,"html.parser")
        styles=[
            link.get("href","")
            for link in soup.find_all("link")
            if "stylesheet" in (link.get("rel") or [])
        ]
        if not any(href.startswith(theme_prefix) for href in styles):
            errors.append(f"site-wide theme missing from {page.relative_to(SITE)}")
            continue
        if not styles or not styles[-1].startswith(theme_prefix):
            errors.append(f"site-wide theme is not final in {page.relative_to(SITE)}")

    index=ET.parse(SITE/"sitemap.xml").getroot()
    sitemap_locs=[node.text.strip() for node in index.findall("sm:sitemap/sm:loc",NS) if node.text]
    expected={DOMAIN+"/sitemap-pages.xml",DOMAIN+"/sitemap-floorplans.xml",DOMAIN+"/sitemap-listings.xml",DOMAIN+"/sitemap-images.xml"}
    if set(sitemap_locs)!=expected:
        errors.append(f"sitemap.xml index mismatch: {sitemap_locs}")

    seen_urls=set()
    seen_canonicals={}
    for name in ("sitemap-pages.xml","sitemap-floorplans.xml","sitemap-listings.xml"):
        root=ET.parse(SITE/name).getroot()
        for node in root.findall("sm:url/sm:loc",NS):
            url=(node.text or "").strip()
            if not url:
                continue
            if url in seen_urls:
                errors.append(f"duplicate sitemap URL: {url}")
            seen_urls.add(url)
            page=html_for(url)
            if not page.is_file():
                errors.append(f"sitemap URL has no staged page: {url} -> {page.relative_to(SITE)}")
                continue
            text=page.read_text(encoding="utf-8",errors="replace")
            if noindex(text):
                errors.append(f"noindex URL present in sitemap: {url}")
            can=canonical(text)
            if not can:
                errors.append(f"missing canonical: {url}")
            elif can!=url:
                errors.append(f"canonical mismatch: {url} -> {can}")
            if can:
                seen_canonicals.setdefault(can,[]).append(url)
            if not re.search(r"<title>[^<]{8,}</title>",text,re.I):
                errors.append(f"missing/short title: {url}")
            if not re.search(r"<h1(?:\s[^>]*)?>[\s\S]*?</h1>",text,re.I):
                errors.append(f"missing H1: {url}")

    for can,urls in seen_canonicals.items():
        if len(urls)>1:
            errors.append(f"duplicate canonical {can}: {urls}")

    robots=(SITE/"robots.txt").read_text(encoding="utf-8")
    if "Sitemap: https://timmuasmartcity.com/sitemap.xml" not in robots:
        errors.append("robots.txt missing sitemap index declaration")
    if "Disallow: /admin/" not in robots:
        errors.append("robots.txt must keep /admin/ blocked")

    # The generic JS detail shell is intentionally noindex; generated clean listing
    # URLs must be the indexable surfaces.
    shell=(SITE/"tin-dang-smart-city/index.html")
    if shell.is_file() and not noindex(shell.read_text(encoding="utf-8",errors="replace")):
        errors.append("/tin-dang-smart-city/ shell must remain noindex")

    if errors:
        raise SystemExit("SEO validation failed:\n- "+"\n- ".join(errors))
    print(f"SEO validation passed: {len(seen_urls)} indexable URLs across split sitemaps")


if __name__=="__main__":
    main()
