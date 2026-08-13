#!/usr/bin/env python3
"""Convert an untrusted ZIP of property images into deterministic web assets."""
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

from PIL import UnidentifiedImageError

from media_utils import (color_signature, create_contact_sheet, difference_hash, hamming, infer_role,
                         normalize_image, normalized_sha256, resized, safe_zip_members,
                         save_webp, validate_slug, write_json_atomic)

ROOT = Path(__file__).resolve().parents[1]
TYPE_DIRS = {"project": "projects", "amenity": "amenities", "editorial": "editorial",
             "listing": "listings", "shared": "shared"}
VARIANTS = {"hero": 1920, "content": 1400, "card": 900, "thumb": 560}
QUALITY = 84


def contained(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Untrusted ZIP file")
    parser.add_argument("--slug", required=True, help="Lowercase URL slug")
    parser.add_argument("--type", required=True, choices=sorted(TYPE_DIRS))
    parser.add_argument("--output", type=Path, help="Asset directory (must remain below images/)")
    parser.add_argument("--force", action="store_true", help="Replace an existing media pack")
    parser.add_argument("--dry-run", action="store_true", help="Validate/process without writing output")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        validate_slug(args.slug)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    source = args.input.resolve()
    if not source.is_file():
        print("error: input ZIP does not exist", file=sys.stderr)
        return 2
    output = (args.output or ROOT / "images" / TYPE_DIRS[args.type] / args.slug).resolve()
    if not contained(output, ROOT / "images"):
        print("error: output must be inside the repository images/ directory", file=sys.stderr)
        return 2
    output_url = "/" + output.relative_to(ROOT).as_posix()
    manifest_path = ROOT / "data" / "media" / f"{args.slug}.json"
    preview_path = ROOT / "data" / "media" / "previews" / f"{args.slug}-contact-sheet.jpg"
    if not args.dry_run and (output.exists() or manifest_path.exists()) and not args.force:
        print("error: output exists; use --force to replace it", file=sys.stderr)
        return 2
    if source.stat().st_size > 100_000_000:
        print("warning: ZIP is larger than 100 MB", file=sys.stderr)

    try:
        members, rejected, total_source = safe_zip_members(source)
    except Exception as error:
        print(f"error: invalid or unsafe ZIP: {error}", file=sys.stderr)
        return 2
    if len(members) > 500:
        print("warning: ZIP contains more than 500 candidate images", file=sys.stderr)

    valid, corrupt, duplicates, seen_sha, seen_phash = [], [], [], {}, []
    for member in members:
        try:
            image = normalize_image(member.data)
            sha = normalized_sha256(image)
            phash = difference_hash(image)
            color = color_signature(image)
        except (UnidentifiedImageError, OSError, ValueError) as error:
            corrupt.append({"originalFilename": member.original_name, "reason": "corrupt-image"})
            print(f"skip corrupt image: {member.original_name}: {error}", file=sys.stderr)
            continue
        duplicate_of = seen_sha.get(sha)
        strategy = "sha256"
        if duplicate_of is None:
            for previous_hash, previous_color, previous_id in seen_phash:
                if hamming(phash, previous_hash) <= 2 and max(
                        abs(left - right) for left, right in zip(color, previous_color)) <= 12:
                    duplicate_of, strategy = previous_id, "dhash"
                    break
        if duplicate_of:
            duplicates.append({"originalFilename": member.original_name,
                               "duplicateOf": duplicate_of, "strategy": strategy})
            continue
        item_id = f"{args.slug}-{len(valid) + 1:02d}"
        seen_sha[sha] = item_id
        seen_phash.append((phash, color, item_id))
        if image.width < 640 or image.height < 360:
            print(f"warning: small image {member.original_name} ({image.width}x{image.height})", file=sys.stderr)
        if image.height > image.width * 2.5:
            print(f"warning: extremely narrow portrait {member.original_name}", file=sys.stderr)
        valid.append((member, image, sha, phash, item_id))
    if not valid:
        print("error: no valid unique images found", file=sys.stderr)
        return 1

    staging_parent = ROOT / ".media-tmp"
    staging_parent.mkdir(exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f"{args.slug}-", dir=staging_parent))
    assets, contact_items, optimized_size = [], [], 0
    try:
        for order, (member, image, sha, phash, item_id) in enumerate(valid, 1):
            base = f"{args.slug}-{order:02d}"
            variants = {}
            hero_bytes = 0
            hero_dimensions = image.size
            for variant, max_width in VARIANTS.items():
                result = resized(image, max_width)
                filename = f"{base}-{variant}.webp"
                byte_count = save_webp(result, stage / filename, QUALITY)
                optimized_size += byte_count
                variants[variant] = f"{output_url}/{filename}"
                if variant == "hero":
                    hero_bytes, hero_dimensions = byte_count, result.size
            role = infer_role(member.original_name)
            assets.append({"alt": "", "aspectRatio": round(image.width / image.height, 6),
                           "bytes": hero_bytes, "caption": "", "featured": False,
                           "filename": f"{base}-hero.webp", "height": hero_dimensions[1],
                           "id": item_id, "originalFilename": member.original_name,
                           "perceptualHash": phash, "role": role, "sha256": sha,
                           "sortOrder": order,
                           "src": variants["hero"], "variants": variants,
                           "width": hero_dimensions[0]})
            contact_items.append((f"{base} ({role})", resized(image, 240)))
        names = [path.name for path in stage.iterdir()]
        if len(names) != len(set(names)):
            raise RuntimeError("duplicate output filenames")
        payload = {"assets": assets, "duplicates": duplicates, "schemaVersion": 1,
                   "slug": args.slug, "type": args.type,
                   "variantWidths": VARIANTS, "webpQuality": QUALITY}
        if not args.dry_run:
            if args.force:
                shutil.rmtree(output, ignore_errors=True)
            output.parent.mkdir(parents=True, exist_ok=True)
            stage.replace(output)
            stage = None
            write_json_atomic(manifest_path, payload)
            create_contact_sheet(contact_items, preview_path)
    finally:
        if stage:
            shutil.rmtree(stage, ignore_errors=True)
        if staging_parent.exists() and not any(staging_parent.iterdir()):
            staging_parent.rmdir()

    savings = (1 - optimized_size / total_source) * 100 if total_source else 0
    print("\nMedia summary")
    print(f"Input files: {len(members) + len(rejected)}")
    print(f"Valid images: {len(valid) + len(duplicates)}")
    print(f"Corrupt skipped: {len(corrupt)}")
    print(f"Duplicates skipped: {len(duplicates)}")
    print(f"Production images: {len(assets)}")
    print(f"Total source size: {total_source:,} bytes")
    print(f"Total optimized size: {optimized_size:,} bytes")
    print(f"Savings: {savings:.1f}%")
    print(f"Manifest: {'(dry run) ' if args.dry_run else ''}{manifest_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
