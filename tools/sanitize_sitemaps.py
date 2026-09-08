#!/usr/bin/env python3
"""Remove noindex HTML URLs from generated URL-set sitemaps.

The SEO builder serializes HTML through BeautifulSoup before sitemap discovery.
That can reorder meta attributes (for example content before name), so a regex
that assumes attribute order can miss a valid noindex directive. This final
sanitizer is deliberately parser-based and makes the sitemap invariant explicit:
no HTML page carrying robots=noindex may be submitted to search engines.
"""
from __future__ import annotations

from pathlib import Path
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SITE_ROOT = ROOT / "_site"
SITE_HOST = "timmuasmartcity.com"
NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
IMAGE_NS = "http://www.google.com/schemas/sitemap-image/1.1"


def local_html(url: str) -> Path | None:
    parts = urlsplit(url)
    if parts.netloc and parts.netloc != SITE_HOST:
        return None
    path = parts.path or "/"
    if path == "/":
        return SITE_ROOT / "index.html"
    if path.endswith("/"):
        return SITE_ROOT / path.lstrip("/") / "index.html"
    target = SITE_ROOT / path.lstrip("/")
    if target.suffix.lower() == ".html":
        return target
    return None


def has_noindex(path: Path | None) -> bool:
    if path is None or not path.is_file():
        return False
    soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="replace"), "html.parser")
    for meta in soup.find_all("meta"):
        if str(meta.get("name") or "").strip().lower() != "robots":
            continue
        tokens = {token.strip().lower() for token in str(meta.get("content") or "").split(",")}
        if "noindex" in tokens or any(token.startswith("noindex") for token in tokens):
            return True
    return False


def sanitize_urlset(path: Path) -> int:
    if not path.is_file():
        return 0
    tree = ET.parse(path)
    root = tree.getroot()
    removed = 0
    for node in list(root.findall(f"{{{NS}}}url")):
        loc = node.find(f"{{{NS}}}loc")
        url = (loc.text or "").strip() if loc is not None else ""
        if url and has_noindex(local_html(url)):
            root.remove(node)
            removed += 1
    if removed:
        ET.register_namespace("", NS)
        ET.register_namespace("image", IMAGE_NS)
        ET.indent(root, space="  ")
        path.write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            + ET.tostring(root, encoding="unicode")
            + "\n",
            encoding="utf-8",
        )
    return removed


def main() -> None:
    if not SITE_ROOT.is_dir():
        raise SystemExit("_site does not exist; run the portal build first")
    removed = 0
    for name in (
        "sitemap-pages.xml",
        "sitemap-floorplans.xml",
        "sitemap-listings.xml",
        "sitemap-images.xml",
    ):
        removed += sanitize_urlset(SITE_ROOT / name)
    print(f"SEO: removed {removed} noindex URL(s) from generated sitemaps")


if __name__ == "__main__":
    main()
