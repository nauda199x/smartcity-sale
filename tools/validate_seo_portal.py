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

            soup=BeautifulSoup(text,"html.parser")
            required_social=[
                ("property","og:title"),
                ("property","og:description"),
                ("property","og:url"),
                ("property","og:site_name"),
                ("property","og:type"),
                ("property","og:image"),
                ("name","twitter:card"),
            ]
            for key,value in required_social:
                if not soup.find("meta",attrs={key:value}):
                    errors.append(f"missing {value}: {url}")
            og_url=soup.find("meta",attrs={"property":"og:url"})
            if og_url and str(og_url.get("content") or "").strip()!=url:
                errors.append(f"og:url mismatch: {url} -> {og_url.get('content')}")
            if not soup.find("script",attrs={"type":"application/ld+json"}):
                errors.append(f"missing JSON-LD: {url}")
            breadcrumb=soup.select_one(".breadcrumb, .crumbs, .pp-breadcrumb")
            if breadcrumb is None:
                for nav in soup.find_all("nav"):
                    aria=str(nav.get("aria-label") or "").lower()
                    if "breadcrumb" in aria or "đường dẫn" in aria:
                        breadcrumb=nav
                        break
            if breadcrumb is not None:
                jsonld=" ".join(
                    script.get_text()
                    for script in soup.find_all("script",attrs={"type":"application/ld+json"})
                )
                if "BreadcrumbList" not in jsonld:
                    errors.append(f"visible breadcrumb missing BreadcrumbList schema: {url}")

    for can,urls in seen_canonicals.items():
        if len(urls)>1:
            errors.append(f"duplicate canonical {can}: {urls}")


    home_text=(SITE/"index.html").read_text(encoding="utf-8",errors="replace")
    home_soup=BeautifulSoup(home_text,"html.parser")
    home_jsonld=" ".join(
        script.get_text()
        for script in home_soup.find_all("script",attrs={"type":"application/ld+json"})
    )
    if "Organization" not in home_jsonld:
        errors.append("homepage must expose Organization JSON-LD")
    primary_nav=home_soup.select_one("nav.nav-links")
    if primary_nav is not None and not primary_nav.find("a",href="/cam-nang.html"):
        errors.append("homepage primary navigation must link to /cam-nang.html")

    robots=(SITE/"robots.txt").read_text(encoding="utf-8")
    if "Sitemap: https://timmuasmartcity.com/sitemap.xml" not in robots:
        errors.append("robots.txt missing sitemap index declaration")
    if "Disallow: /admin/" not in robots:
        errors.append("robots.txt must keep /admin/ blocked")

    # Public marketplace/card/admin links must never override clean listing URLs
    # with the legacy noindex ?slug= detail shell.
    for script_name in ("marketplace-list.js", "marketplace-admin.js"):
        script_path=SITE/"assets/js"/script_name
        if not script_path.is_file():
            errors.append(f"missing staged {script_name}")
            continue
        script_text=script_path.read_text(encoding="utf-8",errors="replace")
        if "/tin-dang-smart-city/" in script_text or "?slug=" in script_text:
            errors.append(f"legacy noindex listing route leaked into {script_name}")
        if "api.listingUrl(" not in script_text:
            errors.append(f"{script_name} must use api.listingUrl() for approved listing links")

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
