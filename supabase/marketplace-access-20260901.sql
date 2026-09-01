-- Marketplace access patch — applied to Supabase project smartcity-marketplace on 2026-09-01.
-- Safe to re-run: grants are idempotent; the unit_type constraint is replaced each run.

begin;

alter table public.listings drop constraint if exists listings_unit_type_check;
alter table public.listings
  add constraint listings_unit_type_check
  check (unit_type = any (array[
    'Studio'::text,
    '1PN'::text,
    '1PN+'::text,
    '1PN+1'::text,
    '2PN'::text,
    '2PN+'::text,
    '2PN+1'::text,
    '2PN+1 (1WC)'::text,
    '2PN+1 (2WC)'::text,
    '3PN'::text,
    '3PN+1'::text,
    '4PN'::text,
    'Duplex'::text,
    'Penthouse'::text,
    'Shop chân đế'::text
  ]));

-- RLS policies already restrict what each role can actually read/write.
-- These grants expose only the operations required by the Data API.
grant usage on schema private to anon, authenticated;

grant select, insert on public.listings to anon;
grant select, insert on public.listing_images to anon;
grant insert on public.listing_reports to anon;

grant select on public.admin_users to authenticated;
grant select, insert, update, delete on public.listings to authenticated;
grant select, insert, update, delete on public.listing_images to authenticated;
grant select, insert, update, delete on public.listing_reports to authenticated;

grant usage, select on sequence public.listing_images_id_seq to anon, authenticated;
grant usage, select on sequence public.listing_reports_id_seq to anon, authenticated;

commit;

-- First admin provisioning (run once after creating the Auth user in Supabase Dashboard):
--
-- insert into public.admin_users (user_id)
-- select id from auth.users
-- where email = 'ADMIN_EMAIL'
-- on conflict (user_id) do nothing;
