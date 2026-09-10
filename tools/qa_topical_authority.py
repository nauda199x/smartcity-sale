#!/usr/bin/env python3
"""Static QA for the topical-authority SEO generator."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "tools" / "build_topical_authority.py"

spec = importlib.util.spec_from_file_location("topical_authority", PATH)
if spec is None or spec.loader is None:
    raise SystemExit("Cannot load build_topical_authority.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

assert len(mod.GUIDES) >= 4, "Topical authority cluster must contain at least four guides"
slugs = [g["slug"] for g in mod.GUIDES]
assert len(slugs) == len(set(slugs)), "Guide slugs must be unique"

for guide in mod.GUIDES:
    assert len(guide["title"]) >= 45, f"Title too thin: {guide['slug']}"
    assert 120 <= len(guide["description"]) <= 220, f"Meta description length out of range: {guide['slug']}"
    assert len(guide["sections"]) >= 5, f"Guide needs >=5 substantive sections: {guide['slug']}"
    assert len(guide["links"]) >= 3, f"Guide needs >=3 contextual internal links: {guide['slug']}"

    html = mod.render_guide(guide)
    doc = BeautifulSoup(html, "html.parser")
    canonical = doc.find("link", rel="canonical")
    robots = doc.find("meta", attrs={"name": "robots"})
    description = doc.find("meta", attrs={"name": "description"})
    h1 = doc.find("h1")
    schema_script = doc.find("script", attrs={"type": "application/ld+json"})

    expected = f"{mod.SITE}/blog/{guide['slug']}/"
    assert canonical and canonical.get("href") == expected, f"Bad canonical: {guide['slug']}"
    assert robots and "index" in str(robots.get("content", "")), f"Guide must be indexable: {guide['slug']}"
    assert description and description.get("content") == guide["description"], f"Meta description mismatch: {guide['slug']}"
    assert h1 and h1.get_text(" ", strip=True) == guide["title"], f"H1 mismatch: {guide['slug']}"
    assert schema_script and schema_script.string, f"Missing JSON-LD: {guide['slug']}"

    schema = json.loads(schema_script.string)
    graph = schema.get("@graph", [])
    types = {node.get("@type") for node in graph if isinstance(node, dict)}
    assert "Article" in types and "BreadcrumbList" in types, f"Missing Article/Breadcrumb schema: {guide['slug']}"
    assert doc.find("meta", attrs={"property": "og:title"}), f"Missing OG title: {guide['slug']}"
    assert doc.find("meta", attrs={"name": "twitter:title"}), f"Missing Twitter title: {guide['slug']}"

print(f"QA: topical-authority cluster valid ({len(mod.GUIDES)} guides)")
