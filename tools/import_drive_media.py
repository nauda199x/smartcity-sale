#!/usr/bin/env python3
"""Import a public Google Drive folder through Media Pipeline V1."""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import gdown
from PIL import Image, UnidentifiedImageError

from media_utils import SUPPORTED_EXTENSIONS, validate_slug

ROOT = Path(__file__).resolve().parents[1]
DRIVE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{10,100}$")
SAFE_SOURCE_NAME_RE = re.compile(r"^[^\x00-\x1f\x7f/\\]{1,180}$")
PIL_FORMATS = {".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG", ".webp": "WEBP"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder-id", required=True, help="Public Google Drive folder ID")
    parser.add_argument("--slug", required=True, help="Lowercase URL slug")
    parser.add_argument("--type", required=True,
                        choices=("project", "amenity", "editorial", "listing", "shared"))
    parser.add_argument("--max-files", type=int, default=200)
    parser.add_argument("--max-file-mb", type=int, default=50)
    parser.add_argument("--max-total-mb", type=int, default=500)
    parser.add_argument("--force", action="store_true", help="Replace an existing media pack")
    return parser.parse_args()


def approved_images(download: Path, max_files: int, max_file_bytes: int,
                    max_total_bytes: int) -> list[Path]:
    """Return fully decoded, ordinary image files within the configured bounds."""
    files = sorted((path for path in download.rglob("*") if path.is_file()),
                   key=lambda path: path.relative_to(download).as_posix().casefold())
    images: list[Path] = []
    total = 0
    for path in files:
        relative = path.relative_to(download)
        if path.is_symlink() or len(relative.parts) != 1:
            # gdown may recreate Drive subfolders. Names never become output paths, but
            # rejecting nested content keeps the remote import boundary unambiguous.
            raise ValueError(f"nested or linked file is not allowed: {relative}")
        if not SAFE_SOURCE_NAME_RE.fullmatch(path.name):
            raise ValueError(f"unsafe source filename: {path.name!r}")
        suffix = path.suffix.lower()
        if suffix not in SUPPORTED_EXTENSIONS:
            raise ValueError(f"unsupported file in Drive folder: {path.name}")
        size = path.stat().st_size
        if size <= 0 or size > max_file_bytes:
            raise ValueError(f"source file exceeds size limit: {path.name}")
        total += size
        if total > max_total_bytes:
            raise ValueError("Drive images exceed total download limit")
        try:
            with Image.open(path) as image:
                image.load()
                if image.format != PIL_FORMATS[suffix]:
                    raise ValueError(f"extension/content mismatch: {path.name}")
        except (UnidentifiedImageError, OSError) as error:
            raise ValueError(f"invalid image content: {path.name}") from error
        images.append(path)
        if len(images) > max_files:
            raise ValueError(f"Drive folder contains more than {max_files} images")
    if not images:
        raise ValueError("Drive folder contains no supported images")
    return images


def main() -> int:
    args = parse_args()
    try:
        validate_slug(args.slug)
        if not DRIVE_ID_RE.fullmatch(args.folder_id):
            raise ValueError("invalid Google Drive folder ID")
        if not (1 <= args.max_files <= 1000):
            raise ValueError("max-files must be between 1 and 1000")
        if not (1 <= args.max_file_mb <= 150) or not (1 <= args.max_total_mb <= 1000):
            raise ValueError("invalid byte limit")
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    # Everything received from Drive, including gdown's cookies/intermediates, lives
    # outside the repository and is removed by TemporaryDirectory on every exit path.
    try:
        with tempfile.TemporaryDirectory(prefix="drive-media-") as temporary:
            workspace = Path(temporary)
            download = workspace / "download"
            download.mkdir()
            url = f"https://drive.google.com/drive/folders/{args.folder_id}"
            result = gdown.download_folder(url=url, output=os.fspath(download), quiet=False,
                                           use_cookies=False, remaining_ok=True)
            if result is None:
                raise ValueError("Google Drive folder could not be listed or downloaded; confirm it is public")
            images = approved_images(download, args.max_files, args.max_file_mb * 1_000_000,
                                     args.max_total_mb * 1_000_000)
            archive = workspace / "media.zip"
            with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_STORED) as target:
                for index, path in enumerate(images, 1):
                    target.write(path, f"{index:04d}-{path.name}")
            command = [sys.executable, os.fspath(ROOT / "tools/process_media_pack.py"),
                       "--input", os.fspath(archive), "--slug", args.slug, "--type", args.type]
            if args.force:
                command.append("--force")
            subprocess.run(command, cwd=ROOT, check=True)
            print(f"Imported {len(images)} public Drive image(s); remote originals were removed.")
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
