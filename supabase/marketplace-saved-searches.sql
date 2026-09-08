-- Saved searches / in-account new-listing alerts for marketplace members.
-- Applied to production on 2026-09-08.

create table if not exists public.saved_searches (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  label text not null,
  listing_type text not null check (listing_type in ('sale','rent')),
  keyword text,
  phase text,
  tower text,
  unit_type text,
  max_price_vnd bigint,
  min_area_sqm numeric,
  max_area_sqm numeric,
  furnishing text,
  fingerprint text not null,
  last_seen_at timestamptz not null default now(),
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint saved_searches_label_len check (char_length(btrim(label)) between 2 and 120),
  constraint saved_searches_keyword_len check (keyword is null or char_length(keyword) <= 100),
  constraint saved_searches_phase_len check (phase is null or char_length(phase) <= 80),
  constraint saved_searches_tower_len check (tower is null or char_length(tower) <= 80),
  constraint saved_searches_unit_type_len check (unit_type is null or char_length(unit_type) <= 80),
  constraint saved_searches_furnishing_len check (furnishing is null or char_length(furnishing) <= 80),
  constraint saved_searches_fingerprint_len check (char_length(fingerprint) between 8 and 160),
  constraint saved_searches_max_price_positive check (max_price_vnd is null or max_price_vnd > 0),
  constraint saved_searches_area_range check (
    (min_area_sqm is null or min_area_sqm >= 0)
    and (max_area_sqm is null or max_area_sqm > 0)
    and (min_area_sqm is null or max_area_sqm is null or min_area_sqm <= max_area_sqm)
  ),
  unique (user_id, fingerprint)
);

create index if not exists saved_searches_user_updated_idx
  on public.saved_searches(user_id, updated_at desc);

alter table public.saved_searches enable row level security;

drop policy if exists saved_searches_owner_select on public.saved_searches;
create policy saved_searches_owner_select
on public.saved_searches for select to authenticated
using (user_id = (select auth.uid()));

drop policy if exists saved_searches_owner_insert on public.saved_searches;
create policy saved_searches_owner_insert
on public.saved_searches for insert to authenticated
with check (user_id = (select auth.uid()));

drop policy if exists saved_searches_owner_update on public.saved_searches;
create policy saved_searches_owner_update
on public.saved_searches for update to authenticated
using (user_id = (select auth.uid()))
with check (user_id = (select auth.uid()));

drop policy if exists saved_searches_owner_delete on public.saved_searches;
create policy saved_searches_owner_delete
on public.saved_searches for delete to authenticated
using (user_id = (select auth.uid()));

revoke all on public.saved_searches from anon;
grant select, insert, update, delete on public.saved_searches to authenticated;
