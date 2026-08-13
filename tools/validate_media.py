#!/usr/bin/env python3
"""Validate committed production media manifests and their referenced images."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
URL_RE = re.compile(r"^/images/[a-z0-9/-]+\.webp$")
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*\.webp$")
ROLES = {"hero", "exterior", "interior", "amenity", "pool", "landscape", "lobby",
         "layout", "map", "construction", "actual", "general"}


def validate(path: Path) -> list[str]:
    errors = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [f"{path}: invalid JSON: {error}"]
    required = {"schemaVersion", "slug", "type", "assets", "duplicates"}
    if not required <= data.keys() or not isinstance(data.get("assets"), list):
        return [f"{path}: malformed manifest root"]
    seen_ids, seen_paths = set(), set()
    for index, asset in enumerate(data["assets"]):
        label = f"{path}: asset {index + 1}"
        for field in ("id", "filename", "src", "variants", "width", "height", "sha256",
                      "role", "alt", "caption", "originalFilename"):
            if field not in asset:
                errors.append(f"{label}: missing {field}")
        if asset.get("id") in seen_ids:
            errors.append(f"{label}: duplicate id")
        seen_ids.add(asset.get("id"))
        if not isinstance(asset.get("filename"), str) or not NAME_RE.fullmatch(asset["filename"]):
            errors.append(f"{label}: filename is not URL-friendly")
        if asset.get("role") not in ROLES:
            errors.append(f"{label}: unsupported role")
        if not re.fullmatch(r"[0-9a-f]{64}", str(asset.get("sha256", ""))):
            errors.append(f"{label}: invalid sha256")
        for variant, url in asset.get("variants", {}).items():
            if not isinstance(url, str) or not URL_RE.fullmatch(url) or ".." in url:
                errors.append(f"{label}: invalid {variant} path")
                continue
            if url in seen_paths:
                errors.append(f"{label}: duplicate output path {url}")
            seen_paths.add(url)
            disk = ROOT / url.lstrip("/")
            try:
                disk.resolve().relative_to((ROOT / "images").resolve())
            except ValueError:
                errors.append(f"{label}: path escapes images/")
                continue
            if not disk.is_file():
                errors.append(f"{label}: missing file {url}")
            elif variant == "hero":
                try:
                    from PIL import Image
                    with Image.open(disk) as image:
                        if image.size != (asset.get("width"), asset.get("height")):
                            errors.append(f"{label}: dimensions do not match hero")
                except OSError as error:
                    errors.append(f"{label}: unreadable image: {error}")
        if asset.get("src") != asset.get("variants", {}).get("hero"):
            errors.append(f"{label}: src must identify hero variant")
        serialized = json.dumps(asset)
        if re.search(r"(?:[A-Za-z]:\\\\|/home/|/Users/|/workspace/)", serialized):
            errors.append(f"{label}: contains an absolute developer path")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug")
    args = parser.parse_args()
    directory = ROOT / "data" / "media"
    paths = [directory / f"{args.slug}.json"] if args.slug else sorted(directory.glob("*.json"))
    if args.slug and not paths[0].is_file():
        print(f"ERROR: manifest not found: {paths[0].relative_to(ROOT)}")
        return 1
    errors = [error for path in paths for error in validate(path)]
    for error in errors:
        print(f"ERROR: {error}")
    print(f"validated {len(paths)} media manifest(s), {len(errors)} error(s)")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
