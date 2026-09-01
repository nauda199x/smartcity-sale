#!/usr/bin/env python3
"""Validate first-party image provenance, files, and recorded dimensions."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlsplit

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "official" / "asset-manifest.json"
ALLOWED_HOSTS = {"smartcity.vinhomes.vn", "vinhomes.vn", "www.vinhomes.vn"}


def main() -> None:
    errors: list[str] = []
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assets = data.get("assets", [])
    if data.get("count") != len(assets):
        errors.append(f"manifest count {data.get('count')} != {len(assets)} assets")
    paths: set[str] = set()
    sources: set[str] = set()
    for index, asset in enumerate(assets, 1):
        label = f"asset {index}"
        local = asset.get("local_path", "")
        source = asset.get("source_url", "")
        source_page = asset.get("source_page", "")
        if not local.startswith("/images/official/"):
            errors.append(f"{label}: invalid local path {local!r}")
            continue
        if local in paths:
            errors.append(f"{label}: duplicate local path {local}")
        paths.add(local)
        if source in sources:
            errors.append(f"{label}: duplicate source URL {source}")
        sources.add(source)
        for key, url in (("source_url", source), ("source_page", source_page)):
            parsed = urlsplit(url)
            # Some legacy first-party pages still emit HTTP asset URLs. The files
            # are downloaded at build time and then served locally over HTTPS.
            if parsed.scheme not in {"http", "https"} or parsed.hostname not in ALLOWED_HOSTS:
                errors.append(f"{label}: unapproved {key} {url!r}")
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

    if errors:
        print(f"OFFICIAL ASSET VALIDATION FAILED ({len(errors)} errors)")
        for error in errors:
            print("-", error)
        raise SystemExit(1)
    print(f"OFFICIAL ASSET VALIDATION PASSED: {len(assets)} traced WebP files")


if __name__ == "__main__":
    main()
