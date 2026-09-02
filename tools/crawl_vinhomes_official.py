#!/usr/bin/env python3
"""Discover official Vinhomes Smart City pages and media.

This crawler is intentionally conservative: it inventories first-party pages,
images and downloadable documents so editorial pages can be built from verified
facts. It does not mirror whole page prose.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, asdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse, urldefrag
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "official" / "crawl-inventory.json"
START_URLS = [
    "https://smartcity.vinhomes.vn/",
    "https://smartcity.vinhomes.vn/the-grand-sapphire/",
    "https://smartcity.vinhomes.vn/tai-lieu-ban-hang/",
]
ALLOWED_HOST = "smartcity.vinhomes.vn"
MAX_PAGES = 80
REQUEST_DELAY = 0.35
UA = "Mozilla/5.0 (compatible; SanSmartCityResearchBot/1.0; +https://timmuasmartcity.com/)"


@dataclass
class PageRecord:
    url: str
    title: str
    description: str
    headings: list[str]
    links: list[str]
    images: list[str]
    documents: list[str]


class Extractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self.in_title = False
        self.in_heading = False
        self.heading_parts: list[str] = []
        self.headings: list[str] = []
        self.description = ""
        self.links: set[str] = set()
        self.images: set[str] = set()

    def handle_starttag(self, tag: str, attrs) -> None:
        data = dict(attrs)
        if tag == "title":
            self.in_title = True
        if tag in {"h1", "h2", "h3"}:
            self.in_heading = True
            self.heading_parts = []
        if tag == "meta" and data.get("name", "").lower() == "description":
            self.description = data.get("content", "").strip()
        if tag == "a" and data.get("href"):
            self.links.add(data["href"].strip())
        if tag == "img":
            for key in ("src", "data-src", "data-lazy-src"):
                if data.get(key):
                    self.images.add(data[key].strip())
            srcset = data.get("srcset", "")
            for item in srcset.split(","):
                candidate = item.strip().split(" ")[0]
                if candidate:
                    self.images.add(candidate)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
        if tag in {"h1", "h2", "h3"} and self.in_heading:
            text = " ".join("".join(self.heading_parts).split())
            if text:
                self.headings.append(text)
            self.in_heading = False
            self.heading_parts = []

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)
        if self.in_heading:
            self.heading_parts.append(data)

    @property
    def title(self) -> str:
        return " ".join("".join(self.title_parts).split())


def normalize(base: str, candidate: str) -> str:
    if not candidate or candidate.startswith(("mailto:", "tel:", "javascript:", "#")):
        return ""
    absolute = urldefrag(urljoin(base, candidate))[0]
    parsed = urlparse(absolute)
    if parsed.scheme not in {"http", "https"}:
        return ""
    return absolute


def is_page(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.netloc == ALLOWED_HOST and not parsed.path.lower().endswith(
        (".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg", ".pdf", ".zip", ".doc", ".docx", ".xls", ".xlsx")
    )


def fetch(url: str) -> str:
    req = Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml"})
    with urlopen(req, timeout=25) as response:
        content_type = response.headers.get("Content-Type", "")
        if "text/html" not in content_type:
            return ""
        return response.read().decode("utf-8", errors="replace")


def crawl() -> list[PageRecord]:
    queue = list(START_URLS)
    seen: set[str] = set()
    records: list[PageRecord] = []

    while queue and len(seen) < MAX_PAGES:
        url = queue.pop(0)
        if url in seen or not is_page(url):
            continue
        seen.add(url)
        try:
            html = fetch(url)
        except Exception as exc:  # network failures should not kill the inventory run
            print(f"WARN {url}: {exc}")
            continue
        if not html:
            continue

        parser = Extractor()
        parser.feed(html)

        links = sorted(filter(None, (normalize(url, x) for x in parser.links)))
        images = sorted(filter(None, (normalize(url, x) for x in parser.images)))
        documents = sorted(
            x for x in links
            if urlparse(x).path.lower().endswith((".pdf", ".zip", ".doc", ".docx", ".xls", ".xlsx"))
        )

        records.append(PageRecord(
            url=url,
            title=parser.title,
            description=parser.description,
            headings=parser.headings,
            links=links,
            images=images,
            documents=documents,
        ))

        for link in links:
            if is_page(link) and link not in seen and link not in queue:
                queue.append(link)

        time.sleep(REQUEST_DELAY)

    return records


def main() -> None:
    records = crawl()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source": "https://smartcity.vinhomes.vn/",
        "page_count": len(records),
        "pages": [asdict(r) for r in records],
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT} with {len(records)} pages")


if __name__ == "__main__":
    main()
