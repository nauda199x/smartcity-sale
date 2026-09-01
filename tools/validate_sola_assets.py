#!/usr/bin/env python3
"""Validate the private Sola Park image manifest and public page usage."""

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
MANIFEST = ROOT / "data" / "official" / "sola-park-assets.json"
PAGE = ROOT / "phan-khu-smart-city" / "sola-park" / "index.html"
LOCAL_PREFIX = "/images/official/sola-park/"
SOURCE_HOSTS = {
    "imperiasmartcity.com",
    "www.coteccons.vn",
    "www.linkedin.com",
}
PAGE_HOSTS = SOURCE_HOSTS
MEDIA_TYPES = {"actual", "rendering", "diagram"}
EXPECTED_MIX = {"actual": 5, "rendering": 6, "diagram": 8}


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
    if len(assets) < 18:
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
        if page_parts.scheme != "https" or page_parts.hostname not in PAGE_HOSTS:
            errors.append(f"{label}: unapproved source page {source_page!r}")
        if media_type not in MEDIA_TYPES:
            errors.append(f"{label}: invalid media type {media_type!r}")
        else:
            media_mix[media_type] += 1
        if media_type == "actual" and not any(
            year in asset.get("published_context", "") for year in ("2025", "2026")
        ):
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
    if soup.select_one("#nguon") or soup.select_one(".sola-sources"):
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
        errors.append("page uses undeclared Sola assets: " + ", ".join(undeclared))
    duplicate_uses = [src for src, count in Counter(tag["src"] for tag in image_tags).items() if count > 1]
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
    if word_count < 2000:
        errors.append(f"public page is too thin: {word_count} words")
    for required in ("29/04/2025", "30/07/2026", "46.765", "4.527", "31,8", "75,9"):
        if required not in public_text:
            errors.append(f"public page is missing required fact {required!r}")

    if errors:
        print(f"SOLA ASSET VALIDATION FAILED ({len(errors)} errors)")
        for error in errors:
            print("-", error)
        raise SystemExit(1)
    print(
        f"SOLA ASSET VALIDATION PASSED: {len(assets)} traced WebP files "
        f"({dict(media_mix)}), {word_count} public words, no public source panel, "
        "external links, repeated images, or image hotlinks"
    )


if __name__ == "__main__":
    main()
