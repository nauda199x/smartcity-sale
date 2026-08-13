"""Reusable, dependency-light helpers for the untrusted media import pipeline."""
from __future__ import annotations

import hashlib
import io
import json
import re
import stat
import unicodedata
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont, ImageOps, UnidentifiedImageError

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FILENAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*\.webp$")
ROLES = {"hero", "exterior", "interior", "amenity", "pool", "landscape", "lobby", "layout", "map", "construction", "actual", "general"}
ROLE_WORDS = {
    "pool": ("pool", "be-boi", "beboi"), "lobby": ("lobby", "sanh"),
    "layout": ("layout", "floor-plan", "mat-bang", "matbang"),
    "map": ("map", "location-map", "ban-do", "bando"),
    "construction": ("construction", "tien-do", "tiendo"),
    "interior": ("interior", "noi-that", "noithat"),
    "exterior": ("exterior", "ngoai-that", "ngoaithat"),
    "landscape": ("landscape", "canh-quan", "canhquan"),
}

@dataclass(frozen=True)
class ZipMedia:
    original_name: str
    data: bytes


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", value)).strip("-")


def validate_slug(value: str) -> str:
    if not SLUG_RE.fullmatch(value):
        raise ValueError("slug must be lowercase ASCII words separated by single hyphens")
    return value


def safe_zip_members(path: Path, *, max_files: int = 2000, max_member_bytes: int = 150_000_000,
                     max_total_bytes: int = 1_000_000_000) -> tuple[list[ZipMedia], list[dict], int]:
    """Read approved image members without writing attacker-controlled paths to disk."""
    accepted: list[ZipMedia] = []
    skipped: list[dict] = []
    total = 0
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        if len(infos) > max_files:
            raise ValueError(f"ZIP contains too many entries ({len(infos)} > {max_files})")
        for info in infos:
            name = info.filename.replace("\\", "/")
            pure = PurePosixPath(name)
            reason = None
            mode = info.external_attr >> 16
            if info.is_dir():
                continue
            if (pure.is_absolute() or ".." in pure.parts or name.startswith("/")
                    or re.match(r"^[A-Za-z]:", name)):
                reason = "unsafe-path"
            elif stat.S_ISLNK(mode):
                reason = "symlink"
            elif info.flag_bits & 1:
                reason = "encrypted"
            elif any(part.startswith(".") for part in pure.parts) or "__MACOSX" in pure.parts:
                reason = "hidden-metadata"
            elif pure.name.lower() in {"thumbs.db", "desktop.ini", ".ds_store"}:
                reason = "metadata"
            elif pure.suffix.lower() not in SUPPORTED_EXTENSIONS:
                reason = "unsupported-format"
            elif mode & 0o111:
                reason = "executable"
            elif info.file_size > max_member_bytes:
                reason = "member-too-large"
            elif info.file_size > 10_000_000 and info.file_size > max(1, info.compress_size) * 200:
                reason = "suspicious-compression-ratio"
            total += info.file_size
            if total > max_total_bytes:
                raise ValueError("ZIP uncompressed data exceeds safety limit")
            if reason:
                skipped.append({"originalFilename": pure.name, "reason": reason})
                continue
            accepted.append(ZipMedia(pure.name, archive.read(info)))
    accepted.sort(key=lambda item: (slugify(Path(item.original_name).stem), item.original_name.casefold()))
    return accepted, skipped, total


def normalize_image(data: bytes) -> Image.Image:
    """Decode fully, apply EXIF orientation, flatten transparency, and discard metadata."""
    with Image.open(io.BytesIO(data)) as source:
        source.load()
        image = ImageOps.exif_transpose(source)
        if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
            rgba = image.convert("RGBA")
            background = Image.new("RGB", rgba.size, "white")
            background.paste(rgba, mask=rgba.getchannel("A"))
            return background
        return image.convert("RGB")


def normalized_sha256(image: Image.Image) -> str:
    digest = hashlib.sha256()
    digest.update(f"RGB:{image.width}x{image.height}:".encode())
    digest.update(image.tobytes())
    return digest.hexdigest()


def difference_hash(image: Image.Image, size: int = 8) -> str:
    sample = image.convert("L").resize((size + 1, size), Image.Resampling.LANCZOS)
    pixels = list(sample.getdata())
    bits = [pixels[row * (size + 1) + col] > pixels[row * (size + 1) + col + 1]
            for row in range(size) for col in range(size)]
    return f"{sum(int(bit) << index for index, bit in enumerate(bits)):0{size * size // 4}x}"


def color_signature(image: Image.Image) -> tuple[int, int, int]:
    """Average color prevents dHash collisions between unrelated flat images."""
    pixel = image.convert("RGB").resize((1, 1), Image.Resampling.BOX).getpixel((0, 0))
    return tuple(pixel)


def hamming(left: str, right: str) -> int:
    return (int(left, 16) ^ int(right, 16)).bit_count()


def infer_role(filename: str) -> str:
    semantic = slugify(Path(filename).stem)
    for role, words in ROLE_WORDS.items():
        if any(re.search(rf"(?:^|-){re.escape(word)}(?:-|$)", semantic) for word in words):
            return role
    return "general"


def resized(image: Image.Image, max_width: int) -> Image.Image:
    if image.width <= max_width:
        return image.copy()
    height = max(1, round(image.height * max_width / image.width))
    return image.resize((max_width, height), Image.Resampling.LANCZOS)


def save_webp(image: Image.Image, path: Path, quality: int = 84) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, "WEBP", quality=quality, method=6, exact=True)
    return path.stat().st_size


def write_json_atomic(path: Path, payload: dict) -> None:
    encoded = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    json.loads(encoded)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(encoded, encoding="utf-8")
    temporary.replace(path)


def create_contact_sheet(items: Iterable[tuple[str, Image.Image]], path: Path, columns: int = 4) -> None:
    entries = list(items)
    cell_w, thumb_h, label_h = 260, 170, 42
    rows = (len(entries) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * cell_w, max(1, rows) * (thumb_h + label_h)), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for index, (filename, image) in enumerate(entries):
        x, y = (index % columns) * cell_w, (index // columns) * (thumb_h + label_h)
        preview = ImageOps.contain(image, (cell_w - 12, thumb_h - 12), Image.Resampling.LANCZOS)
        sheet.paste(preview, (x + (cell_w - preview.width) // 2, y + (thumb_h - preview.height) // 2))
        draw.text((x + 6, y + thumb_h + 4), f"{index + 1:02d}  {filename}"[:38], fill="black", font=font)
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(path, "JPEG", quality=82, optimize=True)
