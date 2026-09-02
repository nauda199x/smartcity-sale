#!/usr/bin/env python3
"""Crawl selected public pages from smartcity.vinhomes.vn.

Purpose:
- discover first-party pages, image/document URLs and headings;
- preserve source traceability for editorial rewriting;
- NEVER overwrite hand-written portal copy directly.

Outputs are raw discovery manifests. A separate build/editorial step decides what is
published on timmuasmartcity.com.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "official"
SOURCE_FILE = OUT_DIR / "source-pages.json"
ASSET_FILE = OUT_DIR / "asset-manifest.json"
USER_AGENT = "Mozilla/5.0 (compatible; SanSmartCityResearchBot/1.0; +https://timmuasmartcity.com/)"
ALLOWED_HOST = "smartcity.vinhomes.vn"

IMG_RE = re.compile(r'''(?:src|data-src|data-lazy-src|href)=["']([^"']+\.(?:jpg|jpeg|png|webp|avif|svg)(?:\?[^"']*)?)["']''', re.I)
DOC_RE = re.compile(r'''href=["']([^"']+\.(?:pdf|doc|docx|xls|xlsx)(?:\?[^"']*)?)["']''', re.I)
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)
H_RE = re.compile(r"<(h[1-3])[^>]*>(.*?)</\1>", re.I | re.S)
TAG_RE = re.compile(r"<[^>]+>")
SPACE_RE = re.compile(r"\s+")


@dataclass
class Asset:
    source_page: str
    original_url: str
    asset_type: str
    suggested_filename: str
    discovered_at: str


def fetch(url: str) -> str:
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,*/*"})
    with urlopen(req, timeout=25) as r:
        charset = r.headers.get_content_charset() or "utf-8"
        return r.read().decode(charset, errors="replace")


def clean_html_text(value: str) -> str:
    value = TAG_RE.sub(" ", value)
    value = value.replace("&nbsp;", " ").replace("&amp;", "&")
    return SPACE_RE.sub(" ", value).strip()


def normalize_asset(page_url: str, raw: str) -> str | None:
    url = urljoin(page_url, raw)
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return None
    return url


def filename_for(url: str, kind: str) -> str:
    parsed = urlparse(url)
    name = Path(parsed.path).name.lower() or kind
    name = re.sub(r"[^a-z0-9._-]+", "-", name).strip("-")
    digest = hashlib.sha1(url.encode()).hexdigest()[:8]
    stem = Path(name).stem[:80] or kind
    suffix = Path(name).suffix.lower() or (".pdf" if kind == "document" else ".img")
    return f"{stem}-{digest}{suffix}"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    config = json.loads(SOURCE_FILE.read_text(encoding="utf-8"))
    pages_out = []
    assets: list[Asset] = []
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    for item in config.get("pages", []):
        url = item["url"]
        if urlparse(url).hostname != ALLOWED_HOST:
            continue
        print("crawl", url)
        html = fetch(url)
        title_match = TITLE_RE.search(html)
        title = clean_html_text(title_match.group(1)) if title_match else ""
        headings = [clean_html_text(m.group(2)) for m in H_RE.finditer(html)]
        headings = [h for h in headings if h]

        found = set()
        for raw in IMG_RE.findall(html):
            asset_url = normalize_asset(url, raw)
            if not asset_url or asset_url in found:
                continue
            found.add(asset_url)
            assets.append(Asset(url, asset_url, "image", filename_for(asset_url, "image"), now))

        for raw in DOC_RE.findall(html):
            asset_url = normalize_asset(url, raw)
            if not asset_url or asset_url in found:
                continue
            found.add(asset_url)
            assets.append(Asset(url, asset_url, "document", filename_for(asset_url, "document"), now))

        pages_out.append({
            **item,
            "page_title": title,
            "headings": headings[:120],
            "asset_count": len(found),
            "crawled_at": now,
        })
        time.sleep(0.7)

    output = {
        "source_domain": config["source_domain"],
        "generated_at": now,
        "pages": pages_out,
        "assets": [asdict(a) for a in assets],
    }
    ASSET_FILE.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", ASSET_FILE, "assets=", len(assets))


if __name__ == "__main__":
    main()
