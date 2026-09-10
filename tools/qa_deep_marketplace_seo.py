#!/usr/bin/env python3
"""Regression checks for the deep marketplace SEO post-build pass."""
from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/deepen_marketplace_seo.py"
WORKFLOW = ROOT / ".github/workflows/site-pipeline.yml"

errors = []
text = SCRIPT.read_text(encoding="utf-8")
workflow = WORKFLOW.read_text(encoding="utf-8")

try:
    ast.parse(text)
except SyntaxError as exc:
    errors.append(f"deep SEO script syntax error: {exc}")

required_source = {
    '"updated_at.desc,id.desc"': "freshness API must sort by real updated_at",
    '"RealEstateListing"': "listing JSON-LD must use RealEstateListing",
    '"OfferForLease"': "rent listing schema must expose lease semantics",
    '"OfferForPurchase"': "sale listing schema must expose purchase semantics",
    '"dateModified"': "listing schema must expose dateModified",
    '"datePosted"': "listing schema must expose datePosted",
    '"priceCurrency": "VND"': "offers must state VND currency",
    '"twitter:title"': "listing pages need twitter:title",
    '"twitter:description"': "listing pages need twitter:description",
    'remove_urls_from_pages_sitemap': "duplicate phase pages must leave sitemap",
    'data-seo-demand-link': "marketplace hubs must link to rich demand landings",
    'data-seo-demand-crosslinks': "demand landing cluster needs sibling crawl links",
    'marketplace-snapshot.json': "scheduled publishing fingerprint must include freshness",
}
for needle, message in required_source.items():
    if needle not in text:
        errors.append(message)

if "python3 tools/deepen_marketplace_seo.py" not in workflow:
    errors.append("site pipeline must run deep marketplace SEO pass")
if workflow.find("python3 tools/deepen_marketplace_seo.py") > workflow.find("python3 tools/sanitize_sitemaps.py"):
    errors.append("deep SEO pass must run before sitemap sanitization")
if workflow.find("python3 tools/deepen_marketplace_seo.py") < workflow.find("python3 tools/build_seo_portal.py"):
    errors.append("deep SEO pass must run after the normal SEO build")

if errors:
    raise SystemExit("Deep marketplace SEO QA failed:\n- " + "\n- ".join(errors))
print("Deep marketplace SEO QA passed")
