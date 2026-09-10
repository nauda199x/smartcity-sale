#!/usr/bin/env python3
"""Validate the high-intent Vinhomes Smart City traffic content cluster."""
from __future__ import annotations

from pathlib import Path
from urllib.parse import urlsplit
import json
import re
import sys

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "seo" / "traffic-content"
SITE = ROOT / "_site"
DOMAIN = "https://timmuasmartcity.com"

REQUIRED = {
    "gia-thue-vinhomes-smart-city-2026.html": ["/cho-thue-smart-city/", "/gia-smart-city/"],
    "phi-dich-vu-vinhomes-smart-city.html": ["/mua-ban-smart-city/", "/cho-thue-smart-city/"],
    "co-nen-mua-vinhomes-smart-city-2026.html": ["/mua-ban-smart-city/", "/mat-bang-smart-city/"],
    "so-sanh-masteri-west-heights-lumiere-evergreen.html": [
        "/phan-khu-smart-city/masteri-west-heights/",
        "/phan-khu-smart-city/lumiere-evergreen/",
    ],
    "so-sanh-the-sola-park-the-victoria.html": [
        "/phan-khu-smart-city/sola-park/",
        "/phan-khu-smart-city/victoria/",
    ],
    "shop-chan-de-vinhomes-smart-city.html": ["/mua-ban-smart-city/", "/cho-thue-smart-city/"],
    "mua-can-ho-1pn-1-vinhomes-smart-city.html": [
        "/mat-bang-can-ho-1pn-1-vinhomes-smart-city.html",
        "/mua-ban-smart-city/",
    ],
    "mua-can-ho-3pn-vinhomes-smart-city.html": ["/mat-bang-smart-city/", "/mua-ban-smart-city/"],
}


def schema_types(doc: BeautifulSoup) -> set[str]:
    found: set[str] = set()
    for script in doc.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            data = json.loads(script.get_text())
        except (ValueError, TypeError):
            continue
        stack = [data]
        while stack:
            item = stack.pop()
            if isinstance(item, dict):
                typ = item.get("@type")
                if isinstance(typ, str):
                    found.add(typ)
                elif isinstance(typ, list):
                    found.update(str(value) for value in typ)
                stack.extend(item.values())
            elif isinstance(item, list):
                stack.extend(item)
    return found


def validate_article(path: Path, filename: str, errors: list[str]) -> None:
    if not path.is_file():
        errors.append(f"missing article: {path}")
        return
    text = path.read_text(encoding="utf-8", errors="replace")
    doc = BeautifulSoup(text, "html.parser")
    prefix = f"{filename}: "

    title = doc.title.get_text(" ", strip=True) if doc.title else ""
    h1 = doc.find("h1")
    desc = doc.find("meta", attrs={"name": "description"})
    robots = doc.find("meta", attrs={"name": "robots"})
    canonical = doc.find("link", rel=lambda value: value and "canonical" in value)
    expected = DOMAIN + "/" + filename

    if len(title) < 25:
        errors.append(prefix + "missing/weak title")
    if h1 is None or len(h1.get_text(" ", strip=True)) < 20:
        errors.append(prefix + "missing/weak H1")
    if not desc or len(str(desc.get("content") or "").strip()) < 80:
        errors.append(prefix + "missing/weak meta description")
    robots_text = str(robots.get("content") if robots else "").lower()
    if "index" not in robots_text or "follow" not in robots_text or "noindex" in robots_text:
        errors.append(prefix + "must explicitly be index,follow")
    if not canonical or str(canonical.get("href") or "").strip() != expected:
        errors.append(prefix + f"canonical must be {expected}")

    for prop in ("og:title", "og:description", "og:url", "og:image", "og:site_name", "og:type"):
        if not doc.find("meta", attrs={"property": prop}):
            errors.append(prefix + f"missing {prop}")
    if not doc.find("meta", attrs={"name": "twitter:card"}):
        errors.append(prefix + "missing twitter:card")

    types = schema_types(doc)
    if "Article" not in types or "BreadcrumbList" not in types:
        errors.append(prefix + f"schema must contain Article + BreadcrumbList, got {sorted(types)}")

    body_text = doc.get_text(" ", strip=True)
    word_count = len(re.findall(r"\b\w+[\w+.-]*\b", body_text, flags=re.UNICODE))
    if word_count < 850:
        errors.append(prefix + f"too thin ({word_count} words)")
    if len(doc.find_all(["h2", "h3"])) < 8:
        errors.append(prefix + "needs deeper heading structure")
    if not doc.select_one(".cta"):
        errors.append(prefix + "missing transaction CTA")
    if not doc.find("img", alt=True):
        errors.append(prefix + "missing descriptive image")

    hrefs = {str(a.get("href") or "") for a in doc.find_all("a", href=True)}
    for required in REQUIRED[filename]:
        if required not in hrefs:
            errors.append(prefix + f"missing required internal link {required}")

    # Keep editorial URLs clean; query-string filters are fine as CTA targets only,
    # but article canonicals and their own URLs must never be parameterized.
    if urlsplit(expected).query:
        errors.append(prefix + "article canonical contains query string")


def main() -> None:
    errors: list[str] = []
    for filename in REQUIRED:
        validate_article(SOURCE / filename, filename, errors)

    builder = (ROOT / "tools" / "build_traffic_seo_cluster.py")
    if not builder.is_file():
        errors.append("missing build_traffic_seo_cluster.py")
    workflow = (ROOT / ".github" / "workflows" / "site-pipeline.yml").read_text(encoding="utf-8")
    if "python3 tools/build_traffic_seo_cluster.py" not in workflow:
        errors.append("site pipeline must stage traffic SEO cluster")
    if "python3 tools/qa_traffic_seo_cluster.py" not in workflow:
        errors.append("site pipeline must validate traffic SEO cluster")

    # When _site exists (CI after staging), require every article to be present and
    # require the editorial hub to expose the cluster to crawlers/users.
    if SITE.is_dir():
        for filename in REQUIRED:
            validate_article(SITE / filename, filename, errors)
        hub = SITE / "cam-nang.html"
        if hub.is_file():
            text = hub.read_text(encoding="utf-8", errors="replace")
            if "data-traffic-seo-links" not in text:
                errors.append("staged cam-nang.html must expose traffic SEO links")
            for filename in REQUIRED:
                if f'href="/{filename}"' not in text:
                    errors.append(f"cam-nang missing link to {filename}")

    if errors:
        raise SystemExit("Traffic SEO validation failed:\n- " + "\n- ".join(errors))
    print(f"Traffic SEO validation passed: {len(REQUIRED)} deep high-intent articles")


if __name__ == "__main__":
    main()
