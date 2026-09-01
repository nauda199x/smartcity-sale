#!/usr/bin/env python3
"""Build an image sitemap from local images used by URLs in sitemap.xml."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
SITE = "https://timmuasmartcity.com"
SITEMAP = ROOT / "sitemap.xml"
OUTPUT = ROOT / "sitemap-images.xml"
NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
IMAGE_NS = "http://www.google.com/schemas/sitemap-image/1.1"


def html_path(url: str) -> Path:
    path = urlsplit(url).path
    if path == "/":
        return ROOT / "index.html"
    target = ROOT / path.lstrip("/")
    if path.endswith("/"):
        return target / "index.html"
    if target.suffix:
        return target
    return target / "index.html"


def local_image(src: str) -> tuple[Path, str] | None:
    parts = urlsplit(src)
    if parts.scheme or parts.netloc or not parts.path.startswith("/"):
        return None
    target = ROOT / parts.path.lstrip("/")
    if not target.is_file():
        return None
    return target, SITE + parts.path


def main() -> None:
    ET.register_namespace("", NS)
    ET.register_namespace("image", IMAGE_NS)
    source = ET.parse(SITEMAP).getroot()
    output = ET.Element(f"{{{NS}}}urlset")
    page_count = 0
    image_count = 0

    for item in source.findall(f"{{{NS}}}url"):
        loc_node = item.find(f"{{{NS}}}loc")
        if loc_node is None or not loc_node.text:
            continue
        page_url = loc_node.text.strip()
        page = html_path(page_url)
        if not page.is_file():
            continue
        soup = BeautifulSoup(page.read_text(encoding="utf-8", errors="replace"), "html.parser")
        images: list[tuple[str, str]] = []
        seen: set[str] = set()
        for tag in soup.find_all("img", src=True):
            resolved = local_image(tag["src"].strip())
            if not resolved or resolved[1] in seen:
                continue
            seen.add(resolved[1])
            images.append((resolved[1], tag.get("alt", "").strip()))
        if not images:
            continue
        url_node = ET.SubElement(output, f"{{{NS}}}url")
        ET.SubElement(url_node, f"{{{NS}}}loc").text = page_url
        for image_url, alt in images:
            image_node = ET.SubElement(url_node, f"{{{IMAGE_NS}}}image")
            ET.SubElement(image_node, f"{{{IMAGE_NS}}}loc").text = image_url
            if alt:
                ET.SubElement(image_node, f"{{{IMAGE_NS}}}title").text = alt
            image_count += 1
        page_count += 1

    ET.indent(output, space="  ")
    OUTPUT.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        + ET.tostring(output, encoding="unicode")
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUTPUT}: {image_count} images across {page_count} pages")


if __name__ == "__main__":
    main()
