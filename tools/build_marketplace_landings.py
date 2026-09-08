#!/usr/bin/env python3
"""Generate crawlable marketplace demand pages before the main SEO sitemap pass."""
from build_seo_portal import SITE_ROOT, fetch_approved_listings
from marketplace_landing_pages import generate_marketplace_landing_pages


def main() -> None:
    if not SITE_ROOT.is_dir():
        raise SystemExit("_site does not exist; run prepare_portal_v2.py first")
    rows = fetch_approved_listings()
    generated = generate_marketplace_landing_pages(SITE_ROOT, rows)
    print(f"SEO demand pages ready: {len(generated)}")


if __name__ == "__main__":
    main()
