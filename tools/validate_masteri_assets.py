#!/usr/bin/env python3
"""Validate the Masteri West Heights editorial image pack and page usage."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

from bs4 import BeautifulSoup
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "official" / "masteri-west-heights-assets.json"
PAGE = ROOT / "phan-khu-smart-city" / "masteri-west-heights" / "index.html"
LOCAL_PREFIX = "/images/official/masteri-west-heights/"
SOURCE_HOSTS = {
    "masterisehomes.com",
    "www.masterisehomes.com",
    "cdnphoto.dantri.com.vn",
    "i1-vnexpress.vnecdn.net",
}
PAGE_HOSTS = {"masterisehomes.com", "www.masterisehomes.com"}
MEDIA_TYPES = {"actual", "rendering", "diagram"}


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

    local_paths: set[str] = set()
    source_urls: set[str] = set()
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
            errors.append(f"{label}: source page is not a Masterise page {source_page!r}")
        if media_type not in MEDIA_TYPES:
            errors.append(f"{label}: invalid media type {media_type!r}")
        if media_type == "actual" and not any(
            year in asset.get("published_context", "") for year in ("2023", "2024")
        ):
            errors.append(f"{label}: actual image has no publication year")

        path = ROOT / local.lstrip("/")
        if not path.is_file() or path.stat().st_size <= 0:
            errors.append(f"{label}: missing or empty file {local}")
            continue
        try:
            with Image.open(path) as image:
                if image.format != "WEBP":
                    errors.append(f"{label}: expected WEBP, got {image.format}")
                if list(image.size) != [asset.get("width"), asset.get("height")]:
                    errors.append(
                        f"{label}: dimensions {image.size} != "
                        f"({asset.get('width')}, {asset.get('height')})"
                    )
        except OSError as exc:
            errors.append(f"{label}: unreadable image: {exc}")
        if asset.get("bytes") != path.stat().st_size:
            errors.append(f"{label}: byte count is stale for {local}")
        if asset.get("sha1") != sha1(path):
            errors.append(f"{label}: SHA-1 is stale for {local}")

    soup = BeautifulSoup(PAGE.read_text(encoding="utf-8"), "html.parser")
    page_images = {tag["src"] for tag in soup.find_all("img", src=True)}
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
        errors.append("page uses undeclared Masteri assets: " + ", ".join(undeclared))

    if errors:
        print(f"MASTERI ASSET VALIDATION FAILED ({len(errors)} errors)")
        for error in errors:
            print("-", error)
        raise SystemExit(1)
    print(
        f"MASTERI ASSET VALIDATION PASSED: {len(assets)} traced WebP files, "
        "no image hotlinks"
    )


if __name__ == "__main__":
    main()
