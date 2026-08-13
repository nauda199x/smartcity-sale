# Project Profile System V1

## Architecture and canonical routes

`data/projects/projects.json` is the reviewed editorial source for the five profiles. `tools/build_project_profiles.py` combines it with public inventory in `data.json` and optional Media Pipeline manifests, then deterministically writes the existing canonical routes:

- `lumiere-evergreen-smart-city.html`
- `phan-khu-sapphire.html`
- `phan-khu-the-sakura.html`
- `masteri-west-heights-smart-city.html`
- `gateway-tower.html`
- the collection hub `phan-khu.html`

The generator runs after legacy flat-route generation, so the old sources can continue to exist for historical articles without overwriting profiles. It does not introduce route aliases or duplicate canonicals. Shared presentation lives in `assets/project-profiles.css` and continues to use Design System V2 tokens.

## Project data schema

The project file has a versioned root and a `projects` array. Each project declares:

- identity: `slug`, existing `route`, display `name`, eyebrow and optional accent;
- SEO: unique `title` and `description`;
- inventory: an explicit list of accepted `inventoryLabels`;
- reviewed facts and copy: `facts`, `overview`, `location`, `buildings`, `amenities`;
- decision support: `fit` and `considerations`;
- navigation: `related` links;
- visible FAQ pairs used for both page content and `FAQPage` structured data.

Optional sections are omitted when their underlying data is absent. In particular, a gallery is not emitted merely to repeat the fallback hero.

## Inventory matching and public fields

Matching is deliberately narrow. Both the configured label and `Phân khu` are Unicode-normalized, lower-cased and whitespace-normalized, then compared for **exact equality**. There is no substring or fuzzy matching. Current mappings are:

| Profile | Accepted `Phân khu` values |
| --- | --- |
| LUMIÈRE Evergreen | `Lumiere` |
| The Sapphire | `Sapphire` |
| The Sakura | `Sakura` |
| Masteri West Heights | `Masteri` |
| Gateway Tower | `Gateway`, `Gateway Tower` |

Only rows with `Hiển thị trên Web = Có` participate. Before rendering, each row is copied through an explicit public whitelist: tower, project, apartment type, area, floor band, furnishing, balcony direction, public asking price, price/m², legal status and representative image. Net-to-owner prices, commission, transfer fee, internal notes and internal IDs are neither copied nor rendered.

Listings are ranked by presence of image, price and area. Up to six are shown. A project with no exact match receives an honest empty state and inventory-filter CTA; the builder never borrows inventory from another project.

## Build-time market snapshot

Each profile reports the visible exact-match count and apartment-type distribution. Median asking price, asking-price range and median price/m² appear only with at least three valid numeric observations. Values are calculated from the current snapshot, not historical transactions, and the page labels them as asking prices rather than trends or achieved prices.

## Media Pipeline integration

For `data/media/<slug>.json`, the generator sorts assets by `featured`, `sortOrder` and filename. It selects the requested `hero`, `card` or `content` variant when available and uses manifest `alt`, `caption`, width and height. Up to six non-hero assets form the responsive editorial gallery.

If a manifest is absent, the generator uses the existing local Smart City editorial image and a deliberately generic alt description. It does not invent a subject, fabricate a gallery, hotlink a map or download external project imagery. To add a reviewed pack:

```bash
python3 tools/process_media_pack.py --input path/to/pack.zip --slug <slug> --type project
python3 tools/validate_media.py --slug <slug>
```

Review the contact sheet, then fill `role`, precise `alt`, useful `caption`, `featured` and `sortOrder` in the manifest before committing it.

## SEO rules

Every generated profile has one canonical on the pre-existing route, a unique title and description, a local OG image, `WebPage`, `BreadcrumbList`, and visible-FAQ-backed `FAQPage` JSON-LD. Profile copy links naturally to the homepage, project hub, pricing guide, inventory, buyer guides, comparison content and consignment route. Do not add FAQ schema for hidden questions or unverified answers.

## Build flow

The supported entry point remains:

```bash
python3 tools/build_site.py
```

For focused development, run `python3 tools/build_project_profiles.py`. Production validation includes media validation, site validation and staged deploy validation. Generated HTML is committed, so a second complete build must produce no diff.

## Adding a project

1. Confirm the canonical public route; do not create a second URL for existing content.
2. Audit exact `Phân khu` labels in `data.json` and add only reviewed labels to `inventoryLabels`.
3. Add independent, buyer-oriented copy and only sourced quick facts to `projects.json`.
4. Process and review a local media pack if one is available; otherwise leave media absent.
5. Add four to eight useful visible FAQ items and natural related links.
6. Build, inspect responsive layouts and verify that inventory belongs only to the intended project.
7. Run the complete deterministic and staged validation sequence documented above.
