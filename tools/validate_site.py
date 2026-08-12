#!/usr/bin/env python3
"""Validate the built static site using only the Python standard library."""
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "timmuasmartcity.com"
SOURCE_DIRS = {"_source", "_site", ".git"}
errors = []
canonicals = defaultdict(list)

class Document(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self.images=[]; self.canonical=[]; self.og_images=[]; self.noindex=False
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag in {"a","link","script"}:
            value=a.get("href") if tag != "script" else a.get("src")
            if value: self.links.append(value)
        if tag in {"img","source","video"}:
            for key in ("src","poster"):
                if a.get(key): self.images.append(a[key])
            if a.get("srcset"):
                self.images.extend(x.strip().split()[0] for x in a["srcset"].split(",") if x.strip())
        rel=a.get("rel","").lower().split()
        if tag=="link" and "canonical" in rel and a.get("href"): self.canonical.append(a["href"])
        if tag=="meta" and a.get("property","").lower()=="og:image" and a.get("content"): self.og_images.append(a["content"])
        if tag=="meta" and a.get("name","").lower()=="robots" and "noindex" in a.get("content","").lower(): self.noindex=True

def public_html():
    for p in ROOT.rglob("*.html"):
        if not any(part in SOURCE_DIRS for part in p.relative_to(ROOT).parts): yield p

def local_path(value, page):
    parsed=urlparse(value)
    if parsed.scheme in {"mailto","tel","data","javascript"} or value.startswith("#"): return None
    if parsed.netloc and parsed.netloc.lower()!=DOMAIN: return None
    raw=unquote(parsed.path)
    if not raw: return None
    candidate = ROOT / raw.lstrip("/") if raw.startswith("/") else page.parent / raw
    if raw.endswith("/"): candidate /= "index.html"
    if candidate.is_dir(): candidate /= "index.html"
    return candidate.resolve()

for page in public_html():
    doc=Document()
    try: doc.feed(page.read_text(encoding="utf-8"))
    except Exception as exc: errors.append(f"{page.relative_to(ROOT)}: invalid HTML input: {exc}"); continue
    rel=page.relative_to(ROOT)
    if page.name != "404.html":
        if len(doc.canonical)!=1: errors.append(f"{rel}: expected one canonical, found {len(doc.canonical)}")
        else:
            c=urlparse(doc.canonical[0])
            if c.scheme!="https" or c.netloc.lower()!=DOMAIN: errors.append(f"{rel}: canonical has wrong domain: {doc.canonical[0]}")
            if not doc.noindex: canonicals[doc.canonical[0]].append(str(rel))
    for value in doc.links + doc.images + doc.og_images:
        target=local_path(value,page)
        if target and not target.exists(): errors.append(f"{rel}: missing local target {value}")

for canonical,pages in canonicals.items():
    if len(pages)>1: errors.append(f"duplicate canonical {canonical}: {', '.join(pages)}")

sitemap=ROOT/"sitemap.xml"
try:
    tree=ET.parse(sitemap)
    locs=[n.text.strip() for n in tree.findall(".//{*}loc") if n.text]
    if len(locs)!=len(set(locs)): errors.append("sitemap.xml: duplicate URLs")
    for url in locs:
        parsed=urlparse(url)
        if parsed.scheme!="https" or parsed.netloc.lower()!=DOMAIN: errors.append(f"sitemap.xml: wrong domain {url}"); continue
        target=local_path(url,sitemap)
        if not target or not target.exists(): errors.append(f"sitemap.xml: URL has no file {url}")
        elif target.suffix==".html":
            d=Document(); d.feed(target.read_text(encoding="utf-8"))
            if not d.canonical or d.canonical[0]!=url: errors.append(f"sitemap.xml: canonical mismatch for {url}")
except Exception as exc: errors.append(f"sitemap.xml: cannot parse: {exc}")

robots=(ROOT/"robots.txt").read_text(encoding="utf-8")
if "Sitemap: https://timmuasmartcity.com/sitemap.xml" not in robots: errors.append("robots.txt: canonical sitemap declaration missing")
if (ROOT/"CNAME").read_text().strip()!=DOMAIN: errors.append("CNAME: production domain changed or malformed")

if errors:
    print(f"VALIDATION FAILED ({len(errors)} errors)")
    print("\n".join(f"- {e}" for e in errors)); sys.exit(1)
print(f"VALIDATION PASSED: {len(list(public_html()))} HTML pages, {len(locs)} sitemap URLs")
