-- Marketplace Growth Phase 2: fresh inventory + bulk posting support.
-- Applied to production on 2026-09-08.

alter table public.listings
  add column if not exists last_confirmed_at timestamptz not null default now(),
  add column if not exists source_channel text not null default 'form';

do $$
begin
  if not exists (
    select 1 from pg_constraint
    where conrelid='public.listings'::regclass
      and conname='listings_source_channel_check'
  ) then
    alter table public.listings
      add constraint listings_source_channel_check
      check (source_channel in ('form','bulk','admin'));
  end if;
end $$;

create index if not exists listings_public_freshness_idx
  on public.listings(listing_type, last_confirmed_at desc, approved_at desc)
  where status='approved';

-- Logged-in posters may submit normal form or bulk rows, but cannot claim admin source.
drop policy if exists listings_member_submit_pending on public.listings;
create policy listings_member_submit_pending
on public.listings
for insert
to authenticated
with check (
  owner_user_id = (select auth.uid())
  and status = 'pending'
  and contact_public
  and not is_featured
  and sort_priority = 0
  and approved_at is null
  and expires_at is null
  and source_channel in ('form','bulk')
);

-- Extend the controlled owner lifecycle with a non-moderation freshness action.
create or replace function public.owner_listing_action(p_listing_id uuid, p_action text)
returns jsonb
language plpgsql
security definer
set search_path = public, pg_temp
as $$
declare
  row_before public.listings%rowtype;
  row_after public.listings%rowtype;
  action_name text := lower(btrim(coalesce(p_action, '')));
begin
  if auth.uid() is null then
    raise exception 'authentication required' using errcode = '42501';
  end if;

  select * into row_before
  from public.listings
  where id = p_listing_id
    and owner_user_id = auth.uid()
  for update;

  if not found then
    raise exception 'listing not found' using errcode = 'P0002';
  end if;

  if action_name = 'hide' then
    update public.listings
      set status = 'expired',
          expires_at = now(),
          is_featured = false,
          sort_priority = 0
      where id = p_listing_id
      returning * into row_after;

  elsif action_name = 'relist' then
    update public.listings
      set status = 'pending',
          approved_at = null,
          expires_at = null,
          last_confirmed_at = now(),
          is_featured = false,
          sort_priority = 0
      where id = p_listing_id
      returning * into row_after;

  elsif action_name = 'confirm' then
    if row_before.status not in ('approved','pending') then
      raise exception 'listing must be active or pending to confirm' using errcode = '22023';
    end if;
    update public.listings
      set last_confirmed_at = now()
      where id = p_listing_id
      returning * into row_after;

  elsif action_name = 'done' then
    update public.listings
      set status = case when listing_type = 'rent' then 'rented' else 'sold' end,
          expires_at = now(),
          is_featured = false,
          sort_priority = 0
      where id = p_listing_id
      returning * into row_after;

  else
    raise exception 'unsupported action' using errcode = '22023';
  end if;

  return jsonb_build_object(
    'id', row_after.id,
    'listing_code', row_after.listing_code,
    'status', row_after.status,
    'last_confirmed_at', row_after.last_confirmed_at,
    'updated_at', row_after.updated_at
  );
end;
$$;

revoke execute on function public.owner_listing_action(uuid,text) from anon;
revoke execute on function public.owner_listing_action(uuid,text) from public;
grant execute on function public.owner_listing_action(uuid,text) to authenticated;
