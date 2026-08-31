# Smart City Marketplace — Supabase activation

This marketplace is intentionally configured for a **dedicated Supabase project**. Do not reuse the Lumi Hanoi database.

## Activation order

1. Create the new Supabase project.
2. Run `supabase/marketplace-schema.sql` against that project.
3. Create the admin account in Supabase Authentication.
4. Add that Auth user to `public.admin_users`.
5. Read the project URL and **publishable key**.
6. Replace the placeholders in `assets/js/marketplace-config.js`.
7. Test all public and admin flows before merging/deploying.
8. Run Supabase Security Advisor and fix every relevant finding.

## Required functional tests

- Anonymous visitor can submit a sale listing with 1–12 supported images.
- Anonymous visitor can submit a rental listing.
- A newly submitted listing has status `pending` and cannot be read from the public feed.
- Admin can sign in, edit, approve, reject, mark sold/rented/expired, and delete.
- Only `approved`, public-contact, unexpired listings appear publicly.
- Approved listing opens on the detail page and exposes only the intended public contact fields.
- Image gallery, phone and Zalo actions work on desktop and mobile.
- A report can be submitted for a public listing.
- Deleting a listing also removes its uploaded image objects.
- No secret/service-role key appears in browser code or Git history.

## Admin grant

After creating the admin user in Authentication, run:

```sql
insert into public.admin_users(user_id)
select id
from auth.users
where email = 'ADMIN_EMAIL_HERE'
on conflict (user_id) do nothing;
```

## Public configuration

`assets/js/marketplace-config.js` may contain a Supabase publishable key. Never place a secret key, service-role key, database password, or private credential in this file.

## Marketplace routes

- `/giao-dich-smart-city/`
- `/mua-ban-smart-city/`
- `/cho-thue-smart-city/`
- `/dang-tin-smart-city/`
- `/tin-dang-smart-city/?slug=...`
- `/admin/` (noindex)

The legacy `/can-ho-dang-ban.html` remains available during migration so the current SEO inventory is not removed abruptly.
