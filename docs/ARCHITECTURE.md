# Tìm Mua Smart City — Portal Architecture

## Current repository

The site is currently a static GitHub Pages project. Important existing areas:

- `/index.html` — information-first homepage.
- `/assets/portal.css` — homepage/portal styling.
- `/assets/v3.css`, `/assets/app-shell.js`, `/assets/gallery.js` — legacy/listing UI shared code.
- `/can-ho-dang-ban/` — live resale inventory experience backed by `/data.json`.
- `/blog/` — buyer guides and SEO articles.
- `/images/hero/`, `/images/editorial/` — existing media.
- `/tools/` and `/.github/workflows/` — normalization and media automation.

## Technology decision

Keep the public site **static HTML/CSS/JS on GitHub Pages** for now. Do not introduce React/Next or a build framework yet because the current repository already deploys directly and the listing engine is working. Add a Python-based content ingestion layer and GitHub Actions for repeatable crawling, normalization and image optimization.

Benefits:

1. Very low hosting complexity and fast HTML delivery.
2. SEO-critical content remains server-visible/static HTML.
3. Existing `/can-ho-dang-ban/` and `data.json` remain intact.
4. Python can crawl and normalize official project information without coupling scraping code to UI code.

## Target information architecture

```text
/
├── index.html                         # Editorial homepage / Smart City portal
├── can-ho-dang-ban/                   # Unique live inventory/search product
├── tong-quan/                         # Project overview, masterplan, location
├── vi-tri-giao-thong/                 # Connections, roads, planned transport
├── tien-ich/
│   ├── index.html                     # Amenities hub
│   ├── central-park/
│   ├── sportia-park/
│   ├── vuon-nhat/
│   ├── vincom-mega-mall/
│   ├── vinschool/
│   └── vinmec/
├── song-thong-minh/                   # Security, traffic, operations, Intercom
├── phan-khu/
│   ├── index.html                     # Subdivision hub
│   ├── sapphire/
│   ├── grand-sapphire/
│   ├── the-sakura/
│   ├── the-tonkin/
│   ├── masteri-west-heights/
│   └── ...                            # Expand only when reliable source/data exists
├── loai-can/
│   ├── studio/
│   ├── 1pn/
│   ├── 2pn/
│   └── 3pn/
├── gia-thi-truong/                    # Asking-price intelligence from own inventory
├── tin-tuc/                           # Fresh project/area news; dated and sourced
├── blog/                              # Evergreen buyer guides
├── data/
│   ├── official/                      # Normalized facts extracted from official sources
│   └── inventory/                     # Future split from current data.json if needed
├── images/
│   ├── hero/
│   ├── official/                      # Locally stored project media, SEO filenames
│   │   ├── tong-quan/
│   │   ├── tien-ich/
│   │   ├── phan-khu/
│   │   └── mat-bang/
│   └── editorial/                     # Site-owned/edited supporting media
└── tools/
    ├── crawl_vinhomes_official.py     # Discovery/inventory crawler
    ├── normalize_official_content.py  # Facts/labels/URLs normalization
    └── optimize_images.py             # WebP/resizing/metadata pipeline
```

## Data model

Official information is stored as normalized facts, not copied page prose. Each fact should carry:

- `topic`
- `label`
- `value`
- `unit` when applicable
- `source_url`
- `source_title`
- `retrieved_at`
- `notes`

Media inventory should carry:

- original URL
- source page URL
- intended local SEO filename
- subject/category
- alt-text draft
- copyright/source attribution note
- download status
- output dimensions/format

## UX direction

The homepage is an **information portal**, not a clone of the rental site. The primary journey is:

`Learn Smart City → compare subdivisions/amenities → understand prices → open live apartments → contact`.

The live inventory remains a differentiated product but is intentionally separated under `/can-ho-dang-ban/`.

## SEO rules

- One search intent per landing page.
- Canonical on every indexable page.
- Unique title/description/H1.
- `Article`, `BreadcrumbList`, `WebSite` and relevant structured data where appropriate.
- Local images with descriptive filenames and alt text.
- No copied long-form prose from source pages; facts are rewritten into buyer-focused editorial content.
- Current pricing is generated from the site's own resale inventory rather than historical developer sales policies.
