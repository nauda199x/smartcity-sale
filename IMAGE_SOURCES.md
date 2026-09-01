# Image source registry

This registry covers external project/editorial images added after the visual-content audit. Existing listing media remains governed by its reviewed inventory fields, and existing project packs remain governed by their media manifests and import history.

## 2026-08-13 visual enrichment

No new external image was downloaded or committed. The homepage and project hub reuse already-committed, optimized repository media:

- `images/projects/lumiere-evergreen/lumiere-evergreen-07-card.webp` — reviewed project image from the existing LUMIÈRE Evergreen media pack; used on `/`; role: project image, never listing media.
- `images/hero/hero-smart-city-desktop.webp` — existing Smart City overview image; used on `/phan-khu.html`; role: project/editorial context, never listing media.

The existing LUMIÈRE pack was imported before this registry was introduced. Its asset identity, variants, curation, and original filename are recorded in `data/media/lumiere-evergreen.json`; its Git history is the authoritative provenance trail. No source or license claim has been inferred or added in this change.

## 2026-09-01 official-source research pack

Forty-eight first-party images were downloaded from `smartcity.vinhomes.vn`, converted to WebP, and stored locally. Exact source URLs, source pages, hashes, dimensions, byte counts, categories, and local paths are recorded in `data/official/asset-manifest.json`.

| Category | Files | Source page | Current editorial use |
| --- | ---: | --- | --- |
| `overview` | 14 | `https://smartcity.vinhomes.vn/` | Smart City overview, parks, landscape, and smart-ecosystem context |
| `gateway-tower` | 14 | `https://smartcity.vinhomes.vn/gateway-tower/` | Gateway exterior renderings, interior reference imagery, and apartment layouts |
| `sapphire-parkville` | 14 | `https://smartcity.vinhomes.vn/sapphire-parkville/` | ParkVille renderings, internal landscape, and S4.02/S4.03 unit layouts |
| `gallery` | 6 | `https://smartcity.vinhomes.vn/thu-vien/` | Smart City-wide editorial imagery |

Publication rules for this pack:

- Captions distinguish renderings, historical launch material, and apartment reference imagery from verified current-condition photography.
- Every published image uses a descriptive Vietnamese `alt`, fixed dimensions, local HTTPS delivery, and lazy loading unless it is the page's LCP/hero image.
- Images are project/editorial context only. They must never be attached to a resale/rental listing unless the listing owner separately verifies that the image depicts the advertised property.
- Public availability and first-party provenance do not establish a reuse licence. No copyright or licence grant is inferred here; the site owner should retain any permission or press-kit terms separately and replace an asset promptly if requested by the rights holder.
- `tools/validate_official_assets.py` verifies provenance hosts, file integrity, WebP format, dimensions, and manifest consistency. `tools/sync_official_assets.py` is the reproducible acquisition/optimisation path.
