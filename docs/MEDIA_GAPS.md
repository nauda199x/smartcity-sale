# Visual media audit and remaining gaps

Audit date: 2026-08-13

## Scope reviewed

- Static/generated architecture, build scripts, homepage, project hub, ten project profiles, sale routes, SEO/editorial routes, project and listing cards.
- `data/media/`, local hero/project assets, LUMIÈRE Evergreen variants and curation, responsive image markup, lazy/LCP behavior, media/site/profile validators, deploy staging, tests, and both GitHub Actions workflows.
- Listing data was not changed. Project/editorial images were not inserted into listing media.

## Improvements made

- The homepage LUMIÈRE Evergreen feature card now uses its reviewed project-specific card variant instead of an abstract monogram.
- The project knowledge hub now opens with the existing Smart City overview image, with fixed dimensions, eager LCP loading, readable overlays, and responsive cropping.
- Existing project-profile gallery behavior remains unchanged: the LUMIÈRE gallery uses curated lazy-loaded content variants while all inventory cards retain only reviewed listing imagery.

## MEDIA_GAPS

| Project/page | Missing media | Why it was not added | Recommended source |
| --- | --- | --- | --- |
| The Sapphire | Project-specific exterior and landscape gallery | Repository manifest is empty; no clearly licensed source was available locally | User-owned photos or a licensed developer press kit |
| The Miami | Project-specific exterior and amenity gallery | Repository manifest is empty | User-owned photos or a licensed developer press kit |
| The Sakura | Project-specific exterior and Japanese landscape gallery | Only editorial SVG fallback is available | User-owned photos or a licensed developer press kit |
| The Tonkin | Project-specific exterior and common-space gallery | Repository manifest is empty | User-owned photos or a licensed developer press kit |
| Masteri West Heights | Project-specific exterior, lobby, and landscape gallery | Only editorial SVG fallback is available | User-owned photos or a licensed Masterise press kit |
| Imperia Smart City / The Mirae Park | Project-specific overview and common-space gallery | Repository manifest is empty | User-owned photos or a licensed MIK press kit |
| The Sola Park | Project-specific exterior and amenity gallery | Repository manifest is empty | User-owned photos or a licensed MIK press kit |
| Imperia Smart City – The Victoria | Project-specific exterior and amenity gallery | Repository manifest is empty | User-owned photos or a licensed MIK press kit |
| The Canopy Residences | Project-specific exterior and amenity gallery | Repository manifest is empty | User-owned photos or a licensed developer press kit |
| Gateway Tower | Project-specific exterior/gallery manifest | An editorial SVG exists, but no project manifest or verified photo pack exists | User-owned photos or a licensed developer press kit |
| Homepage lifestyle section | Verified Smart City-wide park, lake, sports, and retail imagery | LUMIÈRE-specific photos would misrepresent the broader development; no reusable general pack exists | User-owned Smart City photography or clearly licensed destination media |

Unrelated or uncertain imagery was deliberately not used as a substitute. Future additions should use the existing media importer, exact manifest schema, optimized variants, and validators documented in `docs/MEDIA-PIPELINE.md`.
