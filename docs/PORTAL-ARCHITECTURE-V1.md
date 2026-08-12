# Tìm Mua Smart City — Portal Architecture V1

Updated: 2026-08-12

## Product direction
`timmuasmartcity.com` is not a clone of the rental site and not a brochure clone of the developer website. It is a buyer-first information portal for Vinhomes Smart City, with one proprietary layer the official site does not have: a live searchable resale inventory.

Core journey:
1. Learn the urban area.
2. Compare subdivisions, amenities, transport and apartment types.
3. Understand price and buying process.
4. Open live resale inventory.
5. Contact / request consultation.

## Current stack
The repository is currently a static GitHub Pages site built with HTML, CSS and vanilla JavaScript. Existing strengths that should be preserved during the first restructuring phase:
- no framework runtime cost;
- very fast static delivery;
- existing `data.json` resale inventory;
- working gallery / listing UI;
- existing GitHub Actions automation;
- existing blog URLs already indexed or indexable.

For V1 we will NOT migrate to Next.js/React. A framework migration would introduce unnecessary deployment risk before the information architecture is stable. We will first build a clean static content/data layer and reusable CSS/JS components. A future framework migration can be considered only if the portal grows beyond what static generation can comfortably manage.

## Proposed repository tree
```text
/
├── index.html                         # editorial / portal homepage
├── can-ho-dang-ban/
│   └── index.html                     # proprietary live resale search
├── phan-khu/
│   ├── index.html                     # subdivision hub
│   ├── sapphire/
│   ├── the-sakura/
│   ├── the-tonkin/
│   ├── the-miami/
│   ├── sola-park/
│   ├── masteri-west-heights/
│   ├── canopy-residences/
│   ├── lumiere-evergreen/
│   └── imperia-smart-city/
├── tien-ich/
│   ├── index.html
│   ├── central-park/
│   ├── zen-park/
│   ├── sportia-park/
│   ├── vincom-mega-mall/
│   ├── vinschool/
│   ├── vinmec/
│   └── vinbus/
├── tong-quan/
│   ├── index.html
│   ├── vi-tri-giao-thong/
│   ├── quy-hoach/
│   └── smart-city/
├── can-ho/
│   ├── studio/
│   ├── 1pn/
│   ├── 2pn/
│   ├── 2pn-plus/
│   └── 3pn/
├── gia-thi-truong/
│   ├── index.html
│   └── bang-gia-vinhomes-smart-city/
├── tin-tuc/
│   └── index.html
├── blog/                              # existing buyer guides retained
├── assets/
│   ├── portal.css
│   ├── portal.js
│   └── components.css
├── images/
│   ├── official/                      # downloaded official-source media
│   │   ├── overview/
│   │   ├── amenities/
│   │   ├── subdivisions/
│   │   ├── layouts/
│   │   └── maps/
│   ├── editorial/                     # owned / edited editorial media
│   └── listings/                      # optional future local listing media
├── data/
│   ├── official/
│   │   ├── project.json
│   │   ├── amenities.json
│   │   ├── subdivisions.json
│   │   ├── apartment-types.json
│   │   ├── source-pages.json
│   │   └── asset-manifest.json
│   └── data.json                      # existing live listing data stays at root until migration
├── tools/
│   ├── crawl_vinhomes_sources.py
│   ├── download_official_assets.py
│   ├── optimize_images.py
│   └── build_portal_pages.py
└── .github/workflows/
    ├── crawl-official-sources.yml
    └── build-portal.yml
```

## Content model
Every official fact must store:
- `value`
- `unit` where applicable
- `source_url`
- `source_title`
- `retrieved_at`
- optional `source_note`

Every downloaded media asset must store:
- local path
- original URL
- source page
- image role (`hero`, `amenity`, `map`, `layout`, `subdivision`, `gallery`)
- alt text
- caption
- width / height
- mime type
- checksum

This lets content be rewritten without losing source traceability.

## SEO architecture
Primary commercial keywords stay mapped to distinct intents:
- `/` — Vinhomes Smart City overview + buyer portal
- `/can-ho-dang-ban/` — mua bán Vinhomes Smart City / căn đang bán
- `/gia-thi-truong/bang-gia-vinhomes-smart-city/` — bảng giá Vinhomes Smart City
- `/phan-khu/.../` — subdivision entity intent
- `/can-ho/2pn/` etc. — apartment-type intent
- `/tien-ich/.../` — amenity / lifestyle intent
- `/tong-quan/vi-tri-giao-thong/` — location / connectivity intent

Existing blog articles become support content and should internally link into these entity / commercial hubs instead of competing with them.

## UX principles
- Homepage is editorial first, inventory second.
- One strong search / CTA to live inventory, not a full listing grid above the fold.
- Large visual storytelling blocks using project media.
- Sticky desktop header; compact mobile bottom navigation.
- Clear distinction between official-source facts and Tìm Mua Smart City analysis.
- Tables are reserved for comparisons; cards for discovery; maps / plans for spatial content.
- Mobile-first image ratios and typography.

## Performance targets
- Hero WebP/AVIF responsive variants.
- Above-fold JS kept minimal.
- Lazy-load below-fold media.
- Width/height or aspect ratio declared to avoid CLS.
- Prefer local assets over third-party hotlinks.
- No image above ~250 KB unless it is a deliberately high-resolution zoomable plan.
- Target LCP under 2.0 seconds on a warm CDN/static-cache path and keep total homepage transfer lean.

## Phase plan
### Phase 1 — source/data foundation
- crawl official pages and build source manifest;
- download and normalize selected official media;
- seed project / amenity / subdivision structured data;
- create portal URL skeleton.

### Phase 2 — portal homepage
- replace listing-style homepage with editorial portal homepage;
- retain live inventory as a prominent differentiated CTA;
- add project overview, subdivisions, amenities, transport and latest guides.

### Phase 3 — entity pages
- build subdivision, amenity, apartment-type and location pages from structured data;
- add local optimized image galleries and layouts.

### Phase 4 — news / market layer
- market-price hub using live inventory where valid;
- news hub with dated content and source attribution;
- Search Console-driven expansion.
