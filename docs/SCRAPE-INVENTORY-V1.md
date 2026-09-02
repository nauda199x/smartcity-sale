# Official Vinhomes Smart City — Scrape Inventory V1

Source domain: `https://smartcity.vinhomes.vn/`

## P0 — project-level content
From the official homepage:
- project scale: 280 ha;
- construction density: 14.7%;
- location on Đại lộ Thăng Long;
- smart-city pillars: smart security, smart apartment, smart operations, smart community;
- supporting smart systems: multi-layer camera, elevator access control / Face ID, smart fire warning, environmental alerts, real-time traffic information, Intercom;
- outdoor amenities: landscape lake, Kayak, wellness park, picnic park, Aerobic, skating, dance, BBQ, outdoor gym;
- ecosystem: VinBus, office, Vincom Mega Mall, Vinschool, Vinmec;
- Japanese garden / Zen Park overview;
- official product lines: Sapphire, Ruby, Diamond;
- official apartment-interest labels visible in forms: Studio, 1PN+1, 2PN, 2PN+1, 3PN, 3PN+1.

## P0 — visual assets
Collect and classify high-resolution first-party media suitable for editorial use:
- homepage hero / project panorama;
- masterplan / location map;
- Central Park imagery;
- Zen Park / Japanese garden imagery;
- Sportia Park imagery;
- smart-city technology illustrations / photos;
- Vincom / Vinschool / Vinmec / VinBus ecosystem imagery;
- official aerials and real-life project photography;
- gallery hub albums.

Store locally under `images/official/` with SEO-friendly names and a source manifest. Prefer original/high-resolution URLs over thumbnail derivatives when available.

## P1 — Gateway Tower
Official page exposes structured product data including:
- 29 floors;
- 18 apartments/floor;
- apartment-type ranges: Studio 31.5–33.9 m²; 1PN+1 46.3–51.7 m²; 2PN 58.9–59.1 m²; 2PN+1 69.1–69.4 m²; 3PN 81.8 m²;
- immediate handover status stated on the source page;
- connectivity references (Đại lộ Thăng Long, Lê Trọng Tấn / Vành đai 3.5, metro lines as presented by source);
- internal amenities;
- typical-floor plan and unit-level plan images;
- downloadable documents if publicly linked.

Historical promotional price/support claims on this page must NOT be reused as current 2026 sale policy unless independently re-verified as current. They are retained only as historical source metadata.

## P1 — Sapphire ParkVille
Collect:
- overview / positioning;
- tower count and layout details where stated;
- amenity descriptions;
- masterplan / tower plans;
- apartment-type plans and area ranges;
- official gallery media;
- public brochures/documents.

## P1 — The Grand Sapphire
Collect:
- overview / location;
- building configuration;
- amenity system and park/lake relationships;
- product / apartment-type data;
- plans / maps;
- official gallery media;
- public brochures/documents.

## P1 — The Metrolines and related subdivisions
Discover and collect first-party pages for:
- The Sakura;
- The Tonkin;
- The Miami;
- any remaining Metrolines pages still publicly accessible;
- historical pages where useful for entity facts, while clearly tagging time-sensitive information.

## P1 — library and newsroom
From official gallery/news hubs:
- discover album pages;
- collect media metadata and original file URLs;
- discover official news about construction, handover, parks, infrastructure and subdivisions;
- capture publish date, title, canonical URL and image URLs;
- do not copy article body verbatim into Sàn Smart City.

## Asset processing rules
1. Download locally, never hotlink in production.
2. Keep `original_url` and `source_page` in `data/official/asset-manifest.json`.
3. Deduplicate by SHA-256.
4. Normalize image orientation and strip unnecessary metadata.
5. Generate WebP variants (target widths: 480, 768, 1200, 1600 where useful).
6. Preserve original file only when needed for zoomable plans / documents.
7. Use descriptive Vietnamese/ASCII-friendly filenames, e.g. `vinhomes-smart-city-central-park-ho-canh-quan.webp`.
8. Add descriptive alt text based on what is visibly depicted, not keyword stuffing.
9. Mark maps/layouts as such so they can use contain/zoom UX instead of destructive `object-fit: cover`.

## Editorial rules
- Facts and measurements stay faithful to first-party sources.
- Published text is rewritten for buyer intent and comparison intent.
- Time-sensitive sale policy / promotion claims are excluded unless verified as current.
- Every page includes a source note or source registry entry.
- Proprietary live resale inventory is never mixed into 'official source' JSON; it remains a separate dataset.
