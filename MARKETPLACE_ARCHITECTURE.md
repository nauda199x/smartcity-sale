# Smart City Marketplace V1

## Goal

Turn timmuasmartcity.com from a buyer portal into a moderated marketplace while preserving the existing project guides, price pages and legacy inventory URLs.

## Public flow

```
Home / project content
        |
        v
/giao-dich-smart-city/
    |               |
    v               v
/mua-ban.../    /cho-thue.../
    |               |
    +------> approved listings
                 |
                 v
         /tin-dang-smart-city/?slug=...
                 |
                 +--> phone / Zalo / report
```

## Submission flow

```
/dang-tin-smart-city/
   -> pending listing
   -> image upload
   -> /admin/ moderation
   -> approved
   -> public feed/detail
```

## Data model

- `listings`: transaction, status, location, unit, price, public contact.
- `listing_images`: ordered image objects.
- `listing_reports`: public reports for stale/wrong listings.
- `admin_users`: explicit allow-list for moderation access.

## Smart City taxonomy

Phases/towers are based on the project's existing inventory: Sapphire, Sakura, Miami, Tonkin, Masteri, Lumiere, Imperia, Canopy, Sola Park and Victoria. Supported unit types are Studio, 1PN, 1PN+, 2PN, 2PN+, 3PN, 4PN, Duplex, Penthouse and Shop chân đế.

## SEO migration rule

Do not delete or redirect the existing `/can-ho-dang-ban.html` inventory until the database-backed marketplace has been populated and indexed. New marketplace collection URLs are added to the sitemap, while admin and the generic JS detail shell remain noindex/non-sitemap.
