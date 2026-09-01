#!/usr/bin/env python3
"""Validate the private Imperia image manifest and public dossier usage."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

from bs4 import BeautifulSoup
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "official" / "imperia-assets.json"
PAGE = ROOT / "phan-khu-smart-city" / "imperia" / "index.html"
TOWER_HUB = ROOT / "mat-bang-smart-city" / "imperia" / "index.html"
TOWER_PAGES = {
    code: ROOT / "mat-bang-smart-city" / "imperia" / code / "index.html"
    for code in ("i1", "i2", "i3", "i4", "i5")
}
LOCAL_PREFIX = "/images/official/imperia/"
SOURCE_HOSTS = {
    "mikgroup.vn",
    "www.mikgroup.vn",
    "vinhomesmartcity.com.vn",
    "www.vinhomesmartcity.com.vn",
}
MEDIA_TYPES = {"actual", "diagram"}
EXPECTED_MIX = {"actual": 9, "diagram": 5}


def sha1(path: Path) -> str:
    digest = hashlib.sha1()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    errors: list[str] = []
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assets = data.get("assets", [])
    if data.get("count") != len(assets):
        errors.append(f"manifest count {data.get('count')} != {len(assets)} assets")
    if len(assets) < 14:
        errors.append(f"image pack is too thin: {len(assets)} assets")

    local_paths: set[str] = set()
    source_urls: set[str] = set()
    media_mix: Counter[str] = Counter()
    manifest_dimensions: dict[str, tuple[int, int]] = {}
    for index, asset in enumerate(assets, 1):
        label = f"asset {index}"
        local = asset.get("local_path", "")
        source = asset.get("source_url", "")
        source_page = asset.get("source_page", "")
        media_type = asset.get("media_type")

        if not local.startswith(LOCAL_PREFIX):
            errors.append(f"{label}: invalid local path {local!r}")
        if local in local_paths:
            errors.append(f"{label}: duplicate local path {local}")
        local_paths.add(local)
        if source in source_urls:
            errors.append(f"{label}: duplicate source URL {source}")
        source_urls.add(source)

        source_parts = urlsplit(source)
        page_parts = urlsplit(source_page)
        if source_parts.scheme != "https" or source_parts.hostname not in SOURCE_HOSTS:
            errors.append(f"{label}: unapproved source URL {source!r}")
        if page_parts.scheme != "https" or page_parts.hostname not in SOURCE_HOSTS:
            errors.append(f"{label}: unapproved source page {source_page!r}")
        if media_type not in MEDIA_TYPES:
            errors.append(f"{label}: invalid media type {media_type!r}")
        else:
            media_mix[media_type] += 1
        if media_type == "actual" and "2024" not in asset.get("published_context", ""):
            errors.append(f"{label}: actual image has no publication year")

        path = ROOT / local.lstrip("/")
        if not path.is_file() or path.stat().st_size <= 0:
            errors.append(f"{label}: missing or empty file {local}")
            continue
        try:
            with Image.open(path) as image:
                image.load()
                if image.format != "WEBP":
                    errors.append(f"{label}: expected WEBP, got {image.format}")
                if list(image.size) != [asset.get("width"), asset.get("height")]:
                    errors.append(
                        f"{label}: dimensions {image.size} != "
                        f"({asset.get('width')}, {asset.get('height')})"
                    )
                manifest_dimensions[local] = image.size
        except OSError as exc:
            errors.append(f"{label}: unreadable image: {exc}")
        if asset.get("bytes") != path.stat().st_size:
            errors.append(f"{label}: byte count is stale for {local}")
        if asset.get("sha1") != sha1(path):
            errors.append(f"{label}: SHA-1 is stale for {local}")

    if media_mix != Counter(EXPECTED_MIX):
        errors.append(f"unexpected media mix {dict(media_mix)} != {EXPECTED_MIX}")

    html = PAGE.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    if soup.select_one("#nguon") or soup.select_one(".imperia-sources"):
        errors.append("public page exposes a source panel")
    if re.search(r">\s*(Nguồn|Mở nguồn|Source)\b", html, flags=re.IGNORECASE):
        errors.append("public page exposes source-labelled UI")
    external_links = sorted(
        tag["href"]
        for tag in soup.find_all("a", href=True)
        if urlsplit(tag["href"]).scheme or urlsplit(tag["href"]).netloc
    )
    if external_links:
        errors.append("public page links externally: " + ", ".join(external_links))

    image_tags = soup.find_all("img", src=True)
    page_images = {tag["src"] for tag in image_tags}
    external_images = sorted(
        src for src in page_images if urlsplit(src).scheme or urlsplit(src).netloc
    )
    if external_images:
        errors.append("page hotlinks images: " + ", ".join(external_images))
    unused = sorted(local_paths - page_images)
    if unused:
        errors.append("manifest assets not used on page: " + ", ".join(unused))
    undeclared = sorted(
        src for src in page_images if src.startswith(LOCAL_PREFIX) and src not in local_paths
    )
    if undeclared:
        errors.append("page uses undeclared Imperia assets: " + ", ".join(undeclared))
    duplicate_uses = [
        src
        for src, count in Counter(tag["src"] for tag in image_tags).items()
        if count > 1
    ]
    if duplicate_uses:
        errors.append("page repeats image assets: " + ", ".join(sorted(duplicate_uses)))

    for tag in image_tags:
        src = tag["src"]
        if not tag.get("alt", "").strip():
            errors.append(f"image has empty alt text: {src}")
        if src in manifest_dimensions:
            expected_width, expected_height = manifest_dimensions[src]
            try:
                width = int(tag.get("width", ""))
                height = int(tag.get("height", ""))
            except ValueError:
                errors.append(f"image has invalid HTML dimensions: {src}")
                continue
            if (width, height) != (expected_width, expected_height):
                errors.append(
                    f"HTML dimensions for {src} are {(width, height)}, "
                    f"expected {(expected_width, expected_height)}"
                )

    public_text = soup.get_text(" ", strip=True)
    word_count = len(re.findall(r"\b\w+\b", public_text, flags=re.UNICODE))
    if word_count < 2600:
        errors.append(f"public page is too thin: {word_count} words")
    for required in (
        "2,33 ha",
        "3.922",
        "07/2022",
        "I1–I5",
        "28,1",
        "76,2",
        "25 tiện ích",
    ):
        if required not in public_text:
            errors.append(f"public page is missing required fact {required!r}")
    if "FAQPage" not in html or len(soup.select(".mwh-faq details")) < 8:
        errors.append("page is missing the full FAQ experience")

    cluster_pages = {"hub": TOWER_HUB, **TOWER_PAGES}
    for label, cluster_path in cluster_pages.items():
        cluster_html = cluster_path.read_text(encoding="utf-8")
        cluster_soup = BeautifulSoup(cluster_html, "html.parser")
        cluster_hotlinks = sorted(
            tag["src"]
            for tag in cluster_soup.find_all("img", src=True)
            if urlsplit(tag["src"]).scheme or urlsplit(tag["src"]).netloc
        )
        if cluster_hotlinks:
            errors.append(
                f"{label} tower page hotlinks images: " + ", ".join(cluster_hotlinks)
            )
    if "1.170" in TOWER_HUB.read_text(encoding="utf-8") or "1.170" in TOWER_PAGES[
        "i1"
    ].read_text(encoding="utf-8"):
        errors.append("I1 pages still expose the contradictory 1,170-unit estimate")
    for code, cluster_path in TOWER_PAGES.items():
        expected_plan = f"{LOCAL_PREFIX}imperia-mat-bang-{code}.webp"
        if expected_plan not in cluster_path.read_text(encoding="utf-8"):
            errors.append(f"{code} page is missing local plan {expected_plan}")

    if errors:
        print(f"IMPERIA ASSET VALIDATION FAILED ({len(errors)} errors)")
        for error in errors:
            print("-", error)
        raise SystemExit(1)
    print(
        f"IMPERIA ASSET VALIDATION PASSED: {len(assets)} traced WebP files "
        f"({dict(media_mix)}), {word_count} public words, no public source panel, "
        "external links, repeated images, or project/tower image hotlinks"
    )


if __name__ == "__main__":
    main()
