from __future__ import annotations

import hashlib
import json
import re
import time
from io import BytesIO
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SEEDS = ROOT / "data" / "official" / "asset-seeds.json"
OUT = ROOT / "images" / "official"
MANIFEST = ROOT / "data" / "official" / "asset-manifest.json"

UA = "Mozilla/5.0 (compatible; TimMuaSmartCityBot/1.0; +https://timmuasmartcity.com/)"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": UA, "Accept": "text/html,image/avif,image/webp,image/apng,image/*,*/*;q=0.8"})

IMG_EXT = {".jpg", ".jpeg", ".png", ".webp"}
SKIP_WORDS = {"logo", "icon", "favicon", "sprite", "arrow", "prev", "next", "decor", "loading", "pixel", "facebook"}


def safe_slug(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "asset"


def candidate_urls(html: str, base: str) -> set[str]:
    soup = BeautifulSoup(html, "html.parser")
    urls: set[str] = set()
    attrs = ("src", "data-src", "data-lazy-src", "data-original")
    for tag in soup.find_all(["img", "source"]):
        for attr in attrs:
            value = tag.get(attr)
            if value:
                urls.add(urljoin(base, value.strip()))
        srcset = tag.get("srcset") or tag.get("data-srcset")
        if srcset:
            for part in srcset.split(","):
                urls.add(urljoin(base, part.strip().split()[0]))
    for match in re.findall(r"url\((?:['\"])?([^)'\"]+)", html, flags=re.I):
        urls.add(urljoin(base, match.strip()))
    for a in soup.find_all("a", href=True):
        href = urljoin(base, a["href"].strip())
        if Path(urlparse(href).path.lower()).suffix in IMG_EXT:
            urls.add(href)
    return urls


def score(url: str, keywords: list[str]) -> int:
    lower = url.lower()
    if any(word in lower for word in SKIP_WORDS):
        return -100
    points = 0
    for keyword in keywords:
        if keyword.lower() in lower:
            points += 5
    suffix = Path(urlparse(url).path.lower()).suffix
    if suffix in IMG_EXT:
        points += 2
    if "uploads" in lower or "assets/images" in lower:
        points += 2
    return points


def download_image(url: str) -> tuple[bytes, str] | None:
    try:
        r = SESSION.get(url, timeout=25)
        r.raise_for_status()
        ctype = r.headers.get("content-type", "")
        if not ctype.startswith("image/"):
            return None
        return r.content, ctype
    except Exception as exc:
        print("download failed", url, exc)
        return None


def save_webp(content: bytes, category: str, slug: str, source_url: str) -> dict | None:
    try:
        im = Image.open(BytesIO(content)).convert("RGB")
        width, height = im.size
        if width < 640 or height < 360:
            return None
        category_dir = OUT / safe_slug(category)
        category_dir.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha1(source_url.encode("utf-8")).hexdigest()[:8]
        filename = f"{safe_slug(slug)}-{digest}.webp"
        path = category_dir / filename
        max_width = 1920
        if width > max_width:
            new_height = round(height * max_width / width)
            im = im.resize((max_width, new_height), Image.Resampling.LANCZOS)
        im.save(path, "WEBP", quality=82, method=6)
        return {
            "source_url": source_url,
            "local_path": "/" + str(path.relative_to(ROOT)).replace("\\", "/"),
            "width": width,
            "height": height,
            "sha1": hashlib.sha1(content).hexdigest(),
        }
    except Exception as exc:
        print("image decode failed", source_url, exc)
        return None


def crawl_source(page: str, category: str, keywords: list[str], limit: int = 14) -> list[dict]:
    print("crawl", page)
    try:
        r = SESSION.get(page, timeout=30)
        r.raise_for_status()
    except Exception as exc:
        print("page failed", page, exc)
        return []
    candidates = sorted(candidate_urls(r.text, page), key=lambda u: score(u, keywords), reverse=True)
    output: list[dict] = []
    used: set[str] = set()
    for i, url in enumerate(candidates):
        if len(output) >= limit:
            break
        if score(url, keywords) < 0:
            continue
        parsed = urlparse(url)
        if not parsed.netloc.endswith("vinhomes.vn"):
            continue
        stem = Path(parsed.path).stem or f"{category}-{i+1}"
        key = url.split("?")[0]
        if key in used:
            continue
        used.add(key)
        data = download_image(url)
        if not data:
            continue
        saved = save_webp(data[0], category, stem, url)
        if saved:
            saved.update({"source_page": page, "category": category, "discovered": True})
            output.append(saved)
        time.sleep(0.15)
    return output


def main() -> None:
    cfg = json.loads(SEEDS.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    assets: list[dict] = []

    for item in cfg.get("curated", []):
        data = download_image(item["url"])
        if not data:
            continue
        saved = save_webp(data[0], item["category"], item["slug"], item["url"])
        if saved:
            saved.update({"source_page": item["url"], "category": item["category"], "discovered": False})
            assets.append(saved)

    for source in cfg.get("sources", []):
        assets.extend(crawl_source(source["page"], source["category"], source.get("priority_keywords", [])))

    dedup: dict[str, dict] = {}
    for asset in assets:
        dedup.setdefault(asset["sha1"], asset)
    final = list(dedup.values())
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps({"generated_by": "tools/sync_official_assets.py", "count": len(final), "assets": final}, ensure_ascii=False, indent=2), encoding="utf-8")
    print("saved", len(final), "assets")


if __name__ == "__main__":
    main()
