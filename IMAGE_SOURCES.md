# Image source registry

This registry covers external project/editorial images added after the visual-content audit. Existing listing media remains governed by its reviewed inventory fields, and existing project packs remain governed by their media manifests and import history.

## 2026-08-25 Masteri West Heights buyer profile

No third-party marketing image was downloaded or committed.

- Hero on `/masteri-west-heights-smart-city.html`: reuses `images/hero/hero-smart-city-desktop.webp`, an existing Smart City overview image already committed to this repository. The page labels it as Smart City context rather than a project-specific exterior image.
- Gallery on `/masteri-west-heights-smart-city.html`: uses four Google Drive thumbnail URLs already present in the reviewed Masteri inventory records. They are explicitly labelled as listing/apartment media, not official project photography.
- Project facts and floorplan structure are linked to the official Masterise Homes project pages in the page content; those official images are not copied into this repository in this change.

## 2026-08-13 visual enrichment

No new external image was downloaded or committed. The homepage and project hub reuse already-committed, optimized repository media:

- `images/projects/lumiere-evergreen/lumiere-evergreen-07-card.webp` — reviewed project image from the existing LUMIÈRE Evergreen media pack; used on `/`; role: project image, never listing media.
- `images/hero/hero-smart-city-desktop.webp` — existing Smart City overview image; used on `/phan-khu.html`; role: project/editorial context, never listing media.

The existing LUMIÈRE pack was imported before this registry was introduced. Its asset identity, variants, curation, and original filename are recorded in `data/media/lumiere-evergreen.json`; its Git history is the authoritative provenance trail. No source or license claim has been inferred or added in this change.
