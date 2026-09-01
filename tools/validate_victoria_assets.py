#!/usr/bin/env python3
"""Validate The Victoria internal assets and the public dossier/plan cluster."""

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
MANIFEST = ROOT / "data" / "official" / "victoria-assets.json"
PAGE = ROOT / "phan-khu-smart-city" / "victoria" / "index.html"
TOWER_HUB = ROOT / "mat-bang-smart-city" / "victoria" / "index.html"
TOWER_PAGES = {
    code: ROOT / "mat-bang-smart-city" / "victoria" / code / "index.html"
    for code in ("v1", "v2", "v3")
}
LOCAL_PREFIX = "/images/official/victoria/"
SOURCE_HOSTS = {
    "i.ex-cdn.com",
    "nongnghiepmoitruong.vn",
    "www.nongnghiepmoitruong.vn",
    "phuchung.com.vn",
    "www.phuchung.com.vn",
    "static1.cafeland.vn",
    "cafeland.vn",
    "www.cafeland.vn",
    "thevictoriasmartcity.vn",
    "www.thevictoriasmartcity.vn",
    "vinhomesland.vn",
    "www.vinhomesland.vn",
}
MEDIA_TYPES = {"actual", "diagram"}
EXPECTED_MIX = {"actual": 7, "diagram": 3}
EXPECTED_PLANS = {
    "v1": f"{LOCAL_PREFIX}victoria-mat-bang-v1.webp",
    "v2": f"{LOCAL_PREFIX}victoria-mat-bang-v2.webp",
    "v3": f"{LOCAL_PREFIX}victoria-mat-bang-v3.webp",
}


def sha1(path: Path) -> str:
    digest = hashlib.sha1()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_external(value: str) -> bool:
    parts = urlsplit(value)
    return bool(parts.scheme or parts.netloc)


def main() -> None:
    errors: list[str] = []
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assets = data.get("assets", [])

    if data.get("count") != len(assets):
        errors.append(f"manifest count {data.get('count')} != {len(assets)} assets")
    if len(assets) != 10:
        errors.append(f"expected 10 Victoria assets, got {len(assets)}")

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
        context = asset.get("published_context", "")

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

        if media_type == "actual" and not re.search(r"\b20(?:25|26)\b", context):
            errors.append(f"{label}: actual image lacks a 2025/2026 publication context")

        path = ROOT / local.lstrip("/")
        if not path.is_file() or path.stat().st_size <= 0:
            errors.append(f"{label}: missing or empty file {local}")
            continue

        try:
            with Image.open(path) as image:
                image.load()
                if image.format != "WEBP":
                    errors.append(f"{label}: expected WEBP, got {image.format}")
                expected_size = (asset.get("width"), asset.get("height"))
                if image.size != expected_size:
                    errors.append(f"{label}: dimensions {image.size} != {expected_size}")
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

    if soup.select_one("#nguon") or soup.select_one(".sources") or soup.select_one(".victoria-sources"):
        errors.append("public page exposes a source panel")
    if re.search(r">\s*(Nguồn|Mở nguồn|Source)\b", html, flags=re.IGNORECASE):
        errors.append("public page exposes source-labelled UI")

    external_links = sorted(
        tag["href"] for tag in soup.find_all("a", href=True) if is_external(tag["href"])
    )
    if external_links:
        errors.append("public page links externally: " + ", ".join(external_links))

    image_tags = soup.find_all("img", src=True)
    page_images = [tag["src"] for tag in image_tags]
    external_images = sorted(src for src in page_images if is_external(src))
    if external_images:
        errors.append("public page hotlinks images: " + ", ".join(external_images))

    image_counts = Counter(page_images)
    unused = sorted(local_paths - set(page_images))
    if unused:
        errors.append("manifest assets not used on main page: " + ", ".join(unused))
    undeclared = sorted(
        src for src in set(page_images)
        if src.startswith(LOCAL_PREFIX) and src not in local_paths
    )
    if undeclared:
        errors.append("main page uses undeclared Victoria assets: " + ", ".join(undeclared))
    repeated = sorted(src for src, count in image_counts.items() if count > 1)
    if repeated:
        errors.append("main page repeats image assets: " + ", ".join(repeated))

    for tag in image_tags:
        src = tag["src"]
        if not tag.get("alt", "").strip():
            errors.append(f"image has empty alt text: {src}")
        if src in manifest_dimensions:
            expected_width, expected_height = manifest_dimensions[src]
            try:
                actual_width = int(tag.get("width", ""))
                actual_height = int(tag.get("height", ""))
            except ValueError:
                errors.append(f"image has invalid HTML dimensions: {src}")
                continue
            if (actual_width, actual_height) != (expected_width, expected_height):
                errors.append(
                    f"HTML dimensions for {src} are {(actual_width, actual_height)}, "
                    f"expected {(expected_width, expected_height)}"
                )

    public_text = soup.get_text(" ", strip=True)
    word_count = len(re.findall(r"\b\w+\b", public_text, flags=re.UNICODE))
    if word_count < 3500:
        errors.append(f"public page is too thin: {word_count} words")

    for required in (
        "1.836",
        "38 tầng",
        "2 tầng hầm",
        "06/02/2026",
        "29–95,8",
        "V1 Spring",
        "V2 Sky",
        "V3 Shine",
        "163/SXD-QLN",
        "năm 2028",
    ):
        if required not in public_text:
            errors.append(f"public page is missing required fact {required!r}")

    if "FAQPage" not in html or len(soup.select(".vic-faq details")) < 8:
        errors.append("public page is missing the full FAQ experience")

    cluster_pages = {"hub": TOWER_HUB, **TOWER_PAGES}
    for label, cluster_path in cluster_pages.items():
        cluster_html = cluster_path.read_text(encoding="utf-8")
        cluster_soup = BeautifulSoup(cluster_html, "html.parser")
        hotlinks = sorted(
            tag["src"] for tag in cluster_soup.find_all("img", src=True)
            if is_external(tag["src"])
        )
        if hotlinks:
            errors.append(f"{label} page hotlinks images: " + ", ".join(hotlinks))
        if re.search(r">\s*(Nguồn|Mở nguồn|Source)\b", cluster_html, flags=re.IGNORECASE):
            errors.append(f"{label} page exposes source-labelled UI")

    hub_html = TOWER_HUB.read_text(encoding="utf-8")
    for code, plan in EXPECTED_PLANS.items():
        if plan not in hub_html:
            errors.append(f"hub is missing local {code.upper()} plan {plan}")

    for code, tower_path in TOWER_PAGES.items():
        tower_html = tower_path.read_text(encoding="utf-8")
        expected_plan = EXPECTED_PLANS[code]
        if expected_plan not in tower_html:
            errors.append(f"{code} page is missing local plan {expected_plan}")
        if "17 căn/sàn" not in tower_html:
            errors.append(f"{code} page is missing typical-floor density label")
        if "victoria-cat-noc-toan-canh-2026.webp" not in tower_html:
            errors.append(f"{code} page is missing local actual hero")

    if errors:
        print(f"VICTORIA ASSET VALIDATION FAILED ({len(errors)} errors)")
        for error in errors:
            print("-", error)
        raise SystemExit(1)

    print(
        f"VICTORIA ASSET VALIDATION PASSED: {len(assets)} traced WebP files "
        f"({dict(media_mix)}), {word_count} public words, 9 FAQ items, "
        "no public source UI, external links, image hotlinks or repeated dossier images"
    )


if __name__ == "__main__":
    main()
