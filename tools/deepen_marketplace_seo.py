#!/usr/bin/env python3
"""Deep SEO post-processing for Smart City marketplace output.

Runs after build_seo_portal.py and before sitemap sanitization.

Goals:
- keep listing sitemap lastmod tied to real listing updates;
- enrich listing JSON-LD with RealEstateListing + sale/lease offer semantics;
- strengthen Twitter metadata on listing detail pages;
- consolidate duplicate phase category surfaces around richer demand landings;
- improve internal crawl paths between marketplace hubs and generated demand pages.
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from urllib.parse import urlencode
import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup

from build_seo_portal import SITE_ROOT, SITE, NS, parse_marketplace_config, safe_json
from marketplace_landing_pages import PHASE_SLUGS, slugify


def fetch_freshness_rows() -> list[dict]:
    base, key, _ = parse_marketplace_config()
    if not base or not key:
        raise RuntimeError("Marketplace configuration is required for deep SEO generation")
    params = {
        "select": (
            "id,slug,listing_type,title,phase,tower,unit_type,bedroom_count,"
            "price_vnd,poster_name,approved_at,created_at,updated_at,expires_at"
        ),
        "status": "eq.approved",
        "order": "updated_at.desc,id.desc",
        "limit": "500",
    }
    rows: list[dict] = []
    offset = 0
    while True:
        params["offset"] = str(offset)
        result = subprocess.run(
            [
                "curl", "--fail", "--silent", "--show-error", "--location",
                "--max-time", "30", "--retry", "2",
                "-H", f"apikey: {key}",
                "-H", "Accept: application/json",
                f"{base}/rest/v1/listings?{urlencode(params)}",
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode:
            raise RuntimeError(
                "Public freshness fetch failed; stop deployment rather than publish stale SEO dates"
            )
        batch = json.loads(result.stdout)
        if not isinstance(batch, list):
            raise RuntimeError("Invalid freshness response")
        rows.extend(batch)
        if len(batch) < 500:
            break
        offset += len(batch)
    return rows


def clean_date(value: object) -> str:
    text = str(value or "")
    match = re.match(r"(\d{4}-\d{2}-\d{2})", text)
    return match.group(1) if match else ""


def freshness_date(row: dict) -> str:
    candidates = [
        clean_date(row.get("updated_at")),
        clean_date(row.get("approved_at")),
        clean_date(row.get("created_at")),
    ]
    return max((value for value in candidates if value), default="")


def published_date(row: dict) -> str:
    return clean_date(row.get("approved_at")) or clean_date(row.get("created_at"))


def listing_rel(row: dict) -> str:
    segment = "cho-thue-smart-city" if row.get("listing_type") == "rent" else "mua-ban-smart-city"
    slug = re.sub(r"[^a-z0-9-]", "", str(row.get("slug") or "").lower()).strip("-")
    return f"/{segment}/{slug}/"


def ensure_meta(doc: BeautifulSoup, *, name: str, content: str) -> None:
    if not content:
        return
    node = doc.find("meta", attrs={"name": name})
    if node:
        node["content"] = content
        return
    node = doc.new_tag("meta")
    node["name"] = name
    node["content"] = content
    doc.head.append(node)


def jsonld_objects(doc: BeautifulSoup) -> list[tuple[object, dict]]:
    parsed = []
    for script in doc.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            data = json.loads(script.string or script.get_text() or "{}")
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            parsed.append((script, data))
    return parsed


def enrich_listing_page(path: Path, row: dict) -> bool:
    if not path.is_file():
        return False
    doc = BeautifulSoup(path.read_text(encoding="utf-8", errors="replace"), "html.parser")
    title = doc.title.get_text(" ", strip=True) if doc.title else str(row.get("title") or "")
    description_node = doc.find("meta", attrs={"name": "description"})
    description = str(description_node.get("content") or "") if description_node else ""
    ensure_meta(doc, name="twitter:title", content=title)
    ensure_meta(doc, name="twitter:description", content=description)

    canonical_node = doc.find("link", rel=lambda value: value and "canonical" in value)
    canonical = str(canonical_node.get("href") or "") if canonical_node else SITE + listing_rel(row)
    apartment_id = canonical + "#apartment"

    changed_schema = False
    for script_node, data in jsonld_objects(doc):
        graph = data.get("@graph")
        if not isinstance(graph, list):
            continue
        listing_node = next(
            (
                node for node in graph
                if isinstance(node, dict)
                and node.get("@type") in ("WebPage", "RealEstateListing")
            ),
            None,
        )
        if not listing_node:
            continue

        listing_node["@type"] = "RealEstateListing"
        listing_node["@id"] = canonical + "#listing"
        listing_node["url"] = canonical
        listing_node["datePosted"] = published_date(row)
        listing_node["datePublished"] = published_date(row)
        listing_node["dateModified"] = freshness_date(row)

        apartment = listing_node.get("mainEntity")
        if not isinstance(apartment, dict):
            apartment = {"@type": "Apartment", "name": str(row.get("title") or title)}
            listing_node["mainEntity"] = apartment
        apartment["@id"] = apartment_id
        apartment["url"] = canonical
        try:
            bedrooms = int(row.get("bedroom_count") or 0)
        except (TypeError, ValueError):
            bedrooms = 0
        if bedrooms > 0:
            apartment["numberOfBedrooms"] = bedrooms

        price = row.get("price_vnd")
        try:
            price_number = int(float(price or 0))
        except (TypeError, ValueError):
            price_number = 0
        if price_number > 0:
            if row.get("listing_type") == "rent":
                offer = {
                    "@type": "OfferForLease",
                    "url": canonical,
                    "availability": "https://schema.org/InStock",
                    "itemOffered": {"@id": apartment_id},
                    "priceSpecification": {
                        "@type": "UnitPriceSpecification",
                        "price": price_number,
                        "priceCurrency": "VND",
                        "unitText": "MONTH",
                    },
                }
            else:
                offer = {
                    "@type": "OfferForPurchase",
                    "url": canonical,
                    "availability": "https://schema.org/InStock",
                    "itemOffered": {"@id": apartment_id},
                    "price": price_number,
                    "priceCurrency": "VND",
                }
            poster = str(row.get("poster_name") or "").strip()
            if poster:
                offer["offeredBy"] = {"@type": "Person", "name": poster}
            listing_node["offers"] = offer

        script_node.string = safe_json(data)
        changed_schema = True
        break

    if changed_schema:
        path.write_text(str(doc), encoding="utf-8")
    return changed_schema


def rewrite_listing_sitemap(rows: list[dict]) -> int:
    target = SITE_ROOT / "sitemap-listings.xml"
    if not target.is_file():
        raise RuntimeError("sitemap-listings.xml is missing")
    ET.register_namespace("", NS)
    tree = ET.parse(target)
    root = tree.getroot()
    by_url = {SITE + listing_rel(row): freshness_date(row) for row in rows}
    changed = 0
    for url_node in root.findall(f"{{{NS}}}url"):
        loc = url_node.find(f"{{{NS}}}loc")
        if loc is None or not loc.text:
            continue
        lastmod = by_url.get(loc.text)
        if not lastmod:
            continue
        node = url_node.find(f"{{{NS}}}lastmod")
        if node is None:
            node = ET.SubElement(url_node, f"{{{NS}}}lastmod")
        if node.text != lastmod:
            node.text = lastmod
            changed += 1
    ET.indent(root, space="  ")
    target.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        + ET.tostring(root, encoding="unicode")
        + "\n",
        encoding="utf-8",
    )
    return changed


def demand_phase_url(listing_type: str, phase: str) -> str:
    segment = "cho-thue-smart-city" if listing_type == "rent" else "mua-ban-smart-city"
    phase_slug = PHASE_SLUGS.get(phase, slugify(phase))
    return f"/{segment}/{phase_slug}/"


def remove_urls_from_pages_sitemap(urls: set[str]) -> int:
    target = SITE_ROOT / "sitemap-pages.xml"
    if not target.is_file() or not urls:
        return 0
    ET.register_namespace("", NS)
    tree = ET.parse(target)
    root = tree.getroot()
    removed = 0
    for url_node in list(root.findall(f"{{{NS}}}url")):
        loc = url_node.find(f"{{{NS}}}loc")
        if loc is not None and loc.text in urls:
            root.remove(url_node)
            removed += 1
    ET.indent(root, space="  ")
    target.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        + ET.tostring(root, encoding="unicode")
        + "\n",
        encoding="utf-8",
    )
    return removed


def consolidate_phase_categories(rows: list[dict]) -> tuple[int, int]:
    """Prefer rich demand pages over generic phase category pages when both exist."""
    counts: dict[tuple[str, str], int] = defaultdict(int)
    for row in rows:
        phase = str(row.get("phase") or "").strip()
        if phase:
            listing_type = "rent" if row.get("listing_type") == "rent" else "sale"
            counts[(listing_type, phase)] += 1

    hubs_changed = 0
    generic_consolidated = 0
    for listing_type, segment in (("sale", "mua-ban-smart-city"), ("rent", "cho-thue-smart-city")):
        hub_path = SITE_ROOT / segment / "index.html"
        if hub_path.is_file():
            hub_doc = BeautifulSoup(
                hub_path.read_text(encoding="utf-8", errors="replace"), "html.parser"
            )
            changed = False
            for (typ, phase), count in counts.items():
                if typ != listing_type or count < 2:
                    continue
                rich = demand_phase_url(typ, phase)
                rich_path = SITE_ROOT / rich.strip("/") / "index.html"
                if not rich_path.is_file():
                    continue
                generic = f"/{segment}/phan-khu/{slugify(phase)}/"
                for anchor in hub_doc.find_all("a", href=generic):
                    anchor["href"] = rich
                    anchor["data-seo-demand-link"] = "phase"
                    changed = True
            if changed:
                hub_path.write_text(str(hub_doc), encoding="utf-8")
                hubs_changed += 1

        phase_root = SITE_ROOT / segment / "phan-khu"
        if not phase_root.is_dir():
            continue
        for page in phase_root.glob("*/index.html"):
            phase_slug = page.parent.name
            rich_candidates = [
                demand_phase_url(typ, phase)
                for (typ, phase), count in counts.items()
                if typ == listing_type
                and count >= 2
                and PHASE_SLUGS.get(phase, slugify(phase)) == phase_slug
            ]
            rich = rich_candidates[0] if rich_candidates else ""
            if not rich or not (SITE_ROOT / rich.strip("/") / "index.html").is_file():
                continue
            doc = BeautifulSoup(page.read_text(encoding="utf-8", errors="replace"), "html.parser")
            robots = doc.find("meta", attrs={"name": re.compile(r"^robots$", re.I)})
            if robots is None:
                robots = doc.new_tag("meta")
                robots["name"] = "robots"
                doc.head.append(robots)
            robots["content"] = "index,follow,max-image-preview:large"
            canonical = doc.find("link", rel=lambda value: value and "canonical" in value)
            if canonical is None:
                canonical = doc.new_tag("link", rel="canonical")
                doc.head.append(canonical)
            canonical["href"] = SITE + rich
            og_url = doc.find("meta", attrs={"property": "og:url"})
            if og_url is not None:
                og_url["content"] = SITE + rich
            marker = doc.select_one("[data-seo-consolidation]")
            if marker is None:
                main = doc.find("main")
                if main:
                    marker = doc.new_tag("p")
                    marker["data-seo-consolidation"] = ""
                    marker["class"] = ["visually-hidden"]
                    link = doc.new_tag("a", href=rich)
                    link.string = "Xem trang quỹ căn theo phân khu"
                    marker.append(link)
                    main.insert(0, marker)
            page.write_text(str(doc), encoding="utf-8")
            generic_consolidated += 1

    duplicate_urls = set()
    for listing_type, segment in (("sale", "mua-ban-smart-city"), ("rent", "cho-thue-smart-city")):
        for (typ, phase), count in counts.items():
            if typ != listing_type or count < 2:
                continue
            rich = demand_phase_url(typ, phase)
            if (SITE_ROOT / rich.strip("/") / "index.html").is_file():
                duplicate_urls.add(SITE + f"/{segment}/phan-khu/{slugify(phase)}/")
    removed = remove_urls_from_pages_sitemap(duplicate_urls)
    return hubs_changed, removed


def inject_demand_crosslinks() -> int:
    changed = 0
    for segment in ("mua-ban-smart-city", "cho-thue-smart-city"):
        root = SITE_ROOT / segment
        if not root.is_dir():
            continue
        for phase_slug in set(PHASE_SLUGS.values()):
            phase_page = root / phase_slug / "index.html"
            if not phase_page.is_file():
                continue
            children = sorted(
                child.parent.name
                for child in (root / phase_slug).glob("*/index.html")
                if child.parent.name != "page"
            )
            children = children[:16]
            targets = [(f"/{segment}/{phase_slug}/", "Tất cả quỹ căn phân khu")]
            targets.extend(
                (f"/{segment}/{phase_slug}/{child}/", child.replace("-", " ").upper())
                for child in children
            )
            for page in [phase_page] + [
                root / phase_slug / child / "index.html" for child in children
            ]:
                if not page.is_file():
                    continue
                doc = BeautifulSoup(page.read_text(encoding="utf-8", errors="replace"), "html.parser")
                if doc.select_one("[data-seo-demand-crosslinks]"):
                    continue
                main = doc.find("main")
                if main is None:
                    continue
                nav = doc.new_tag("nav")
                nav["class"] = ["container", "inventory-category-links", "seo-demand-crosslinks"]
                nav["aria-label"] = "Khám phá quỹ căn liên quan"
                nav["data-seo-demand-crosslinks"] = ""
                heading = doc.new_tag("strong")
                heading.string = "Quỹ căn liên quan: "
                nav.append(heading)
                current_rel = "/" + page.relative_to(SITE_ROOT).as_posix().removesuffix("index.html")
                for href, label in targets:
                    if href == current_rel:
                        continue
                    link = doc.new_tag("a", href=href)
                    link.string = label
                    nav.append(link)
                main.append(nav)
                page.write_text(str(doc), encoding="utf-8")
                changed += 1
    return changed


def update_snapshot_fingerprint(rows: list[dict]) -> bool:
    """Make scheduled publishing notice real listing edits/confirmations, not view counters."""
    target = SITE_ROOT / "assets/data/marketplace-snapshot.json"
    if not target.is_file():
        return False
    snapshot = json.loads(target.read_text(encoding="utf-8"))
    freshness = [
        (str(row.get("id") or ""), str(row.get("updated_at") or ""))
        for row in sorted(rows, key=lambda item: str(item.get("id") or ""))
    ]
    payload = {
        "inventory": str(snapshot.get("fingerprint") or ""),
        "freshness": freshness,
    }
    snapshot["fingerprint"] = hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    target.write_text(json.dumps(snapshot, ensure_ascii=False), encoding="utf-8")
    return True


def main() -> None:
    if not SITE_ROOT.is_dir():
        raise SystemExit("_site does not exist; run the normal portal build first")
    rows = fetch_freshness_rows()
    by_id = {str(row.get("id")): row for row in rows}

    enriched = 0
    for segment in ("mua-ban-smart-city", "cho-thue-smart-city"):
        root = SITE_ROOT / segment
        if not root.is_dir():
            continue
        for page in root.glob("*/index.html"):
            doc = BeautifulSoup(page.read_text(encoding="utf-8", errors="replace"), "html.parser")
            main_node = doc.select_one("main[data-listing-id]")
            if not main_node:
                continue
            row = by_id.get(str(main_node.get("data-listing-id") or ""))
            if row and enrich_listing_page(page, row):
                enriched += 1

    lastmods = rewrite_listing_sitemap(rows)
    hubs, duplicate_sitemap_removed = consolidate_phase_categories(rows)
    crosslinks = inject_demand_crosslinks()
    snapshot = update_snapshot_fingerprint(rows)
    print(
        "Deep SEO: "
        f"listing_schema={enriched} lastmods={lastmods} hubs={hubs} "
        f"phase_duplicates_removed_from_sitemap={duplicate_sitemap_removed} "
        f"demand_crosslinks={crosslinks} freshness_snapshot={snapshot}"
    )


if __name__ == "__main__":
    main()
