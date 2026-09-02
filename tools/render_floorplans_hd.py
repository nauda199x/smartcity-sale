#!/usr/bin/env python3
"""Build a crisp local HD render for every tower floor plan on the Smart City hub.

Goals:
- 49/49 tower pages receive a local WebP floor-plan render.
- Every published render has a long edge of at least 3840 px (unless a source is
  already larger, in which case native dimensions are retained).
- Re-render from an official brochure PDF where the repository already records a
  stable page mapping; otherwise use the verified local source already in the repo.
- Never hotlink the public HTML to external images.
- Keep an auditable manifest describing whether an asset came from an official
  PDF render or a deterministic high-quality resample of the verified local source.

This script is designed to run in GitHub Actions where the full repository and
network are available.
"""

from __future__ import annotations

import hashlib
import io
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import fitz  # PyMuPDF
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parents[1]
HUB = ROOT / "mat-bang-smart-city" / "index.html"
OUT_DIR = ROOT / "images" / "official" / "floorplans-hd"
MANIFEST = ROOT / "data" / "official" / "floorplans-hd-20260902.json"
TARGET_LONG_EDGE = 3840
WEBP_QUALITY = 94
TIMEOUT = 60

# Stable brochure mappings already documented by the project's provenance files.
# Page indexes are zero-based.
PDF_OVERRIDES: dict[str, dict[str, Any]] = {
    "/images/official/sola-park/sola-park-mat-bang-g1-g2.webp": {
        "url": "https://imperiasmartcity.com/upload/setting/file_brochure/1/file-brochure-1719020881.pdf",
        "page_index": 19,
        "label": "The Sola Park official brochure, page 20",
    },
    "/images/official/sola-park/sola-park-mat-bang-g3.webp": {
        "url": "https://imperiasmartcity.com/upload/setting/file_brochure/1/file-brochure-1719020881.pdf",
        "page_index": 22,
        "label": "The Sola Park official brochure, page 23",
    },
}

SESSION = requests.Session()
SESSION.headers.update(
    {
        "User-Agent": "Mozilla/5.0 (compatible; SmartCityFloorplanRenderer/1.0; +https://timmuasmartcity.com/)"
    }
)


def tower_slug(href: str) -> str:
    parts = [p for p in href.strip("/").split("/") if p]
    if parts and parts[0] == "mat-bang-smart-city":
        parts = parts[1:]
    slug = "-".join(parts)
    slug = re.sub(r"[^a-z0-9-]+", "-", slug.lower()).strip("-")
    if not slug:
        raise ValueError(f"Cannot create slug from href: {href}")
    return slug


def open_local_image(src: str) -> Image.Image:
    path = ROOT / src.lstrip("/")
    if not path.is_file():
        raise FileNotFoundError(f"Missing local floor-plan source: {src}")
    im = Image.open(path)
    im = ImageOps.exif_transpose(im)
    return im.convert("RGB")


_pdf_cache: dict[str, bytes] = {}


def fetch_pdf(url: str) -> bytes:
    if url not in _pdf_cache:
        response = SESSION.get(url, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.content
        if not data.startswith(b"%PDF"):
            raise ValueError(f"Expected PDF from {url}, got {response.headers.get('content-type')}")
        _pdf_cache[url] = data
    return _pdf_cache[url]


def render_pdf_page(url: str, page_index: int) -> Image.Image:
    data = fetch_pdf(url)
    doc = fitz.open(stream=data, filetype="pdf")
    if page_index < 0 or page_index >= doc.page_count:
        raise IndexError(f"PDF page {page_index} outside 0..{doc.page_count - 1}: {url}")
    page = doc.load_page(page_index)
    rect = page.rect
    long_edge_pt = max(rect.width, rect.height)
    scale = TARGET_LONG_EDGE / long_edge_pt
    # Render a little above target then downsample to improve fine text/line edges.
    matrix = fitz.Matrix(scale * 1.18, scale * 1.18)
    pix = page.get_pixmap(matrix=matrix, alpha=False)
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    doc.close()
    return im


def to_hd(im: Image.Image) -> tuple[Image.Image, dict[str, int]]:
    original_w, original_h = im.size
    current_long = max(original_w, original_h)
    target_long = max(TARGET_LONG_EDGE, current_long)
    if current_long != target_long:
        scale = target_long / current_long
        new_size = (max(1, round(original_w * scale)), max(1, round(original_h * scale)))
        im = im.resize(new_size, Image.Resampling.LANCZOS, reducing_gap=3.0)

    # Floor-plan drawings are line/text heavy. A restrained unsharp pass after
    # resampling keeps room labels readable without inventing geometry.
    im = im.filter(ImageFilter.UnsharpMask(radius=0.75, percent=115, threshold=2))
    return im, {
        "source_width": original_w,
        "source_height": original_h,
        "output_width": im.width,
        "output_height": im.height,
    }


def save_webp(im: Image.Image, path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, "WEBP", quality=WEBP_QUALITY, method=6)
    return hashlib.sha1(path.read_bytes()).hexdigest()


def replace_img_src_and_dimensions(html: str, old_src: str, new_src: str, width: int, height: int) -> tuple[str, int]:
    pattern = re.compile(
        r"<img\b(?P<attrs>[^>]*?\bsrc=[\"']" + re.escape(old_src) + r"[\"'][^>]*)>",
        flags=re.I,
    )
    count = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal count
        count += 1
        attrs = match.group("attrs")
        attrs = re.sub(
            r"(\bsrc=)[\"']" + re.escape(old_src) + r"[\"']",
            lambda m: m.group(1) + f'"{new_src}"',
            attrs,
            count=1,
            flags=re.I,
        )
        if re.search(r"\bwidth=[\"']?\d+", attrs, flags=re.I):
            attrs = re.sub(r"\bwidth=[\"']?\d+[\"']?", f'width="{width}"', attrs, count=1, flags=re.I)
        else:
            attrs += f' width="{width}"'
        if re.search(r"\bheight=[\"']?\d+", attrs, flags=re.I):
            attrs = re.sub(r"\bheight=[\"']?\d+[\"']?", f'height="{height}"', attrs, count=1, flags=re.I)
        else:
            attrs += f' height="{height}"'
        return "<img" + attrs + ">"

    return pattern.sub(repl, html), count


def replace_text_refs(path: Path, replacements: dict[str, str]) -> int:
    text = path.read_text(encoding="utf-8")
    before = text
    for old, new in replacements.items():
        text = text.replace(old, new)
    if text != before:
        path.write_text(text, encoding="utf-8")
        return 1
    return 0


def main() -> None:
    if not HUB.is_file():
        raise SystemExit(f"Missing hub: {HUB}")

    # Idempotency comes first: after the UX redesign the master page is a
    # 10-project directory instead of a 49-card technical hub. The rendered
    # manifest is now the source of truth for an already-complete HD set.
    if MANIFEST.is_file():
        existing = json.loads(MANIFEST.read_text(encoding="utf-8"))
        assets = existing.get("assets", [])
        if existing.get("tower_count") == 49 and len(assets) == 49 and len({x.get("hd_src") for x in assets}) == 49:
            for asset in assets:
                src = str(asset.get("hd_src") or "")
                if max(int(asset.get("output_width", 0)), int(asset.get("output_height", 0))) < TARGET_LONG_EDGE:
                    raise SystemExit(f"Existing HD asset below target: {src}")
                if not (ROOT / src.lstrip("/")).is_file():
                    raise SystemExit(f"Existing HD asset missing: {src}")
            print("HD FLOORPLANS ALREADY READY: validated existing 49/49 4K tower renders; no re-encode needed.")
            return

    # Legacy generation fallback: only used when the HD manifest does not yet
    # exist. Older revisions exposed all 49 source drawings on this hub.
    soup = BeautifulSoup(HUB.read_text(encoding="utf-8"), "html.parser")
    cards = soup.select(".floor-hub-card")
    if len(cards) != 49:
        raise SystemExit(
            "HD manifest is missing and the legacy 49-card source hub is no longer available; "
            f"found {len(cards)} source cards"
        )

    entries: list[dict[str, Any]] = []
    by_old_src: dict[str, list[dict[str, Any]]] = defaultdict(list)

    # Render every tower to its own SEO-readable 4K asset.
    for card in cards:
        link = card.select_one("a.card-link[href]")
        img_tag = card.select_one(".floor-hub-card__media img[src]")
        if not link or not img_tag:
            raise SystemExit("Floor-plan card missing tower link or image")

        href = str(link["href"])
        old_src = str(img_tag["src"])
        if old_src.startswith(("http://", "https://", "//")):
            raise SystemExit(f"External floor-plan source found in hub: {old_src}")

        slug = tower_slug(href)
        out_rel = f"/images/official/floorplans-hd/{slug}.webp"
        out_path = ROOT / out_rel.lstrip("/")

        mode = "verified_local_hd_resample"
        provenance: dict[str, Any] = {"local_source": old_src}
        source_im: Image.Image

        pdf = PDF_OVERRIDES.get(old_src)
        if pdf:
            try:
                source_im = render_pdf_page(pdf["url"], int(pdf["page_index"]))
                mode = "official_pdf_render"
                provenance.update(
                    {
                        "pdf_url": pdf["url"],
                        "pdf_page": int(pdf["page_index"]) + 1,
                        "pdf_label": pdf["label"],
                    }
                )
            except Exception as exc:
                print(f"PDF render fallback for {href}: {exc}")
                source_im = open_local_image(old_src)
                provenance["pdf_fallback_error"] = str(exc)
        else:
            source_im = open_local_image(old_src)

        hd, dims = to_hd(source_im)
        sha1 = save_webp(hd, out_path)

        entry = {
            "href": href,
            "tower_slug": slug,
            "old_src": old_src,
            "hd_src": out_rel,
            "mode": mode,
            **provenance,
            **dims,
            "bytes": out_path.stat().st_size,
            "sha1": sha1,
        }
        if max(dims["output_width"], dims["output_height"]) < TARGET_LONG_EDGE:
            raise SystemExit(f"HD output below target: {entry}")
        entries.append(entry)
        by_old_src[old_src].append(entry)

    # First replace generic references throughout public HTML/XML with one HD
    # derivative for each original source. Shared plans are pixel-identical
    # because the render mode is source-level, so this is safe.
    canonical_replacements = {
        old: items[0]["hd_src"] for old, items in by_old_src.items()
    }
    text_files = [
        p
        for p in ROOT.rglob("*")
        if p.is_file()
        and p.suffix.lower() in {".html", ".xml"}
        and "_site" not in p.parts
        and ".git" not in p.parts
    ]
    changed_text_files = sum(replace_text_refs(p, canonical_replacements) for p in text_files)

    # Then make the master hub and every tower page point to the tower-specific
    # filename. Every tower also gets a dedicated non-hero drawing section so
    # the shared pinch/zoom viewer works even on pages that previously used a
    # lifestyle hero or had no floor-plan drawing in the body.
    hub_html = HUB.read_text(encoding="utf-8")
    hub_soup = BeautifulSoup(hub_html, "html.parser")
    hub_by_href: dict[str, Any] = {}
    for card in hub_soup.select(".floor-hub-card"):
        link = card.select_one("a.card-link[href]")
        if link:
            hub_by_href[str(link["href"])] = card

    inserted_sections = 0
    for entry in entries:
        href = entry["href"]
        canonical = canonical_replacements[entry["old_src"]]
        card = hub_by_href.get(href)
        if card is None:
            raise SystemExit(f"Tower disappeared from hub: {href}")
        img = card.select_one(".floor-hub-card__media img[src]")
        if img is None:
            raise SystemExit(f"Hub image missing: {href}")
        plan_alt = str(img.get("alt") or f"Mặt bằng {entry['tower_slug']}")
        img["src"] = entry["hd_src"]
        img["width"] = str(entry["output_width"])
        img["height"] = str(entry["output_height"])

        tower_page = ROOT / href.lstrip("/") / "index.html"
        if not tower_page.is_file():
            raise SystemExit(f"Tower page missing: {href}")

        tower_html = tower_page.read_text(encoding="utf-8")
        # Promote all tower-specific metadata and any pre-existing image
        # reference from the generic/shared output to this tower's SEO path.
        tower_html = tower_html.replace(canonical, entry["hd_src"])
        tower_html = tower_html.replace(entry["old_src"], entry["hd_src"])
        tower_soup = BeautifulSoup(tower_html, "html.parser")

        matching_imgs = [
            node
            for node in tower_soup.select("main img[src]")
            if str(node.get("src")) == entry["hd_src"]
        ]
        for node in matching_imgs:
            node["width"] = str(entry["output_width"])
            node["height"] = str(entry["output_height"])

        zoomable_match = next(
            (
                node
                for node in matching_imgs
                if "article-hero-media" not in (node.get("class") or [])
            ),
            None,
        )

        if zoomable_match is None:
            section_html = f"""
<section class="section section-alt floorplan-hd-section">
  <div class="container">
    <div class="section-head">
      <div>
        <p class="eyebrow section-kicker">Bản vẽ HD</p>
        <h2>Mặt bằng tòa · ảnh 4K để phóng to</h2>
      </div>
      <p>Bấm vào bản vẽ để mở chế độ xem lớn; trên điện thoại có thể chụm hai ngón để zoom và kéo ảnh.</p>
    </div>
    <div class="plan-frame">
      <img src="{entry['hd_src']}" width="{entry['output_width']}" height="{entry['output_height']}" alt="{plan_alt}" loading="lazy" decoding="async">
    </div>
  </div>
</section>
"""
            section = BeautifulSoup(section_html, "html.parser").section
            main = tower_soup.find("main")
            if main is None or section is None:
                raise SystemExit(f"Cannot insert HD floor-plan section: {href}")
            cta = tower_soup.select_one(".smart-owner-cta")
            cta_section = cta.find_parent("section") if cta else None
            if cta_section is not None:
                cta_section.insert_before(section)
            else:
                main.append(section)
            inserted_sections += 1

        tower_page.write_text(str(tower_soup), encoding="utf-8")

    HUB.write_text(str(hub_soup), encoding="utf-8")
    print(f"Tower detail pages refreshed; inserted {inserted_sections} dedicated zoomable plan sections.")

    # Update sitemap-image references to HD variants after tower-specific hub
    # wiring. Shared plans use the canonical HD path there.
    sitemap_images = ROOT / "sitemap-images.xml"
    if sitemap_images.is_file():
        replace_text_refs(sitemap_images, canonical_replacements)

    manifest = {
        "generated_at": "2026-09-02",
        "target_long_edge_px": TARGET_LONG_EDGE,
        "webp_quality": WEBP_QUALITY,
        "tower_count": len(entries),
        "unique_original_sources": len(by_old_src),
        "rendering_policy": {
            "official_pdf": "Rendered directly from a documented official brochure page when a stable mapping exists.",
            "verified_local": "Deterministic Lanczos resample + restrained line-art sharpening from the repository's verified local floor-plan source. No generative detail is added.",
            "public_delivery": "All public pages point to local WebP assets; no external floor-plan hotlinks.",
        },
        "assets": entries,
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Final integrity check against the rewritten hub.
    final = BeautifulSoup(HUB.read_text(encoding="utf-8"), "html.parser")
    final_cards = final.select(".floor-hub-card")
    hd_imgs = []
    for card in final_cards:
        link = card.select_one("a.card-link[href]")
        img = card.select_one(".floor-hub-card__media img[src]")
        if not link or not img:
            raise SystemExit("Final hub card missing link/image")
        src = str(img["src"])
        w = int(img.get("width", 0))
        h = int(img.get("height", 0))
        if not src.startswith("/images/official/floorplans-hd/"):
            raise SystemExit(f"Non-HD floorplan remains on hub: {src}")
        if max(w, h) < TARGET_LONG_EDGE:
            raise SystemExit(f"Floorplan below 4K long edge: {src} {w}x{h}")
        if not (ROOT / src.lstrip("/")).is_file():
            raise SystemExit(f"Generated image missing: {src}")
        hd_imgs.append(src)

    if len(final_cards) != 49 or len(set(hd_imgs)) != 49:
        raise SystemExit(
            f"Expected 49 tower-specific HD outputs, got cards={len(final_cards)} unique_hd={len(set(hd_imgs))}"
        )

    print(
        f"HD FLOORPLANS READY: 49/49 tower renders, "
        f"{len(by_old_src)} verified source drawings, min long edge {TARGET_LONG_EDGE}px, "
        f"{changed_text_files} generic HTML/XML files refreshed."
    )


if __name__ == "__main__":
    main()
