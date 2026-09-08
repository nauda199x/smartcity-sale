# Growth Phase 3 implementation

## Demand retention

Marketplace buyers/renters can save the exact filters they are using. The saved search is private to their authenticated account. If a visitor is not signed in, the intended search is kept locally and is saved after login.

The member dashboard counts approved listings whose `approved_at` is newer than the saved search's `last_seen_at`. Opening a saved search updates `last_seen_at`, so the badge represents newly approved matches since the previous visit. Phase 3 intentionally ships this as an in-account alert; outbound email/push delivery can be layered on later without changing the search model.

## SEO demand pages

The deployment build creates crawlable inventory-backed collection pages for sale/rent demand clusters:

- transaction + phase: minimum 2 approved listings;
- transaction + phase + unit type: minimum 2 approved listings;
- transaction + phase + tower: minimum 3 approved listings.

Pages disappear from the next build when the live approved inventory no longer meets the threshold. Each generated page has a self canonical, index/follow robots, CollectionPage + ItemList + Breadcrumb structured data, a live price range/median summary, direct links to listing detail pages, and links back to the relevant project and canonical marketplace filter.

This avoids indexing arbitrary query-string filters and avoids creating empty/thin landing pages purely for keyword coverage.
