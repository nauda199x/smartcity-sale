-- Smart City marketplace parity. Applied with the Supabase migration API.
-- Extends existing tables and preserves all listings, approval policies and contacts.
alter table public.listings drop constraint if exists listings_description_check;
alter table public.listings add constraint listings_description_check
  check (char_length(btrim(description)) between 1 and 3000);

alter table public.listings add column if not exists view_count bigint not null default 0
  check (view_count >= 0);

create table if not exists private.listing_view_visitors (
  listing_id uuid not null references public.listings(id) on delete cascade,
  visitor_hash text not null check (char_length(visitor_hash) = 64),
  last_viewed_at timestamptz not null default now(),
  primary key (listing_id, visitor_hash)
);
alter table private.listing_view_visitors enable row level security;
revoke all on private.listing_view_visitors from public, anon, authenticated;

-- Counting a view must not refresh the posting date or invalidate an admin edit.
create or replace function private.set_updated_at()
returns trigger language plpgsql set search_path = '' as $$
begin
  if (to_jsonb(new) - 'updated_at' - 'view_count') is distinct from
     (to_jsonb(old) - 'updated_at' - 'view_count') then
    new.updated_at = clock_timestamp();
  else
    new.updated_at = old.updated_at;
  end if;
  return new;
end;
$$;

create or replace function private.protect_listing_view_count()
returns trigger language plpgsql set search_path = '' as $$
begin
  if current_user in ('anon', 'authenticated') then
    if tg_op = 'INSERT' then
      new.view_count := 0;
    elsif new.view_count is distinct from old.view_count then
      raise exception 'View counts can only be updated by the counter';
    end if;
  end if;
  return new;
end;
$$;
create trigger listings_protect_view_count before insert or update on public.listings
  for each row execute function private.protect_listing_view_count();

-- A narrowly scoped anonymous counter, not a general-purpose write endpoint.
-- Only the invoker wrapper below is exposed through PostgREST.
create or replace function private.record_listing_view(target_listing_id uuid)
returns bigint language plpgsql security definer set search_path = '' as $$
declare
  headers jsonb := '{}'::jsonb;
  agent text;
  client_ip text;
  fingerprint text;
  counter bigint;
  incremented boolean := false;
begin
  if (select auth.uid()) is not null then return null; end if;
  select l.view_count into counter from public.listings l
    where l.id = target_listing_id and l.status = 'approved' and l.contact_public
      and (l.expires_at is null or l.expires_at > now());
  if not found then return null; end if;
  begin
    headers := coalesce(nullif(current_setting('request.headers', true), '')::jsonb, '{}'::jsonb);
  exception when others then headers := '{}'::jsonb;
  end;
  agent := lower(coalesce(headers->>'user-agent', ''));
  client_ip := coalesce(nullif(btrim(split_part(coalesce(headers->>'x-forwarded-for', ''), ',', 1)), ''),
    nullif(headers->>'cf-connecting-ip', ''), nullif(headers->>'x-real-ip', ''), '');
  if agent = '' or client_ip = '' or
    agent ~ '(bot|crawler|spider|slurp|preview|headless|lighthouse|pagespeed|curl|wget)' then
    return counter;
  end if;
  fingerprint := encode(extensions.digest(target_listing_id::text || '|' || client_ip || '|' || agent, 'sha256'), 'hex');
  insert into private.listing_view_visitors as v (listing_id, visitor_hash, last_viewed_at)
    values (target_listing_id, fingerprint, now())
    on conflict (listing_id, visitor_hash) do update set last_viewed_at = excluded.last_viewed_at
      where v.last_viewed_at <= now() - interval '1 hour'
    returning true into incremented;
  if coalesce(incremented, false) then
    update public.listings l set view_count = l.view_count + 1
      where l.id = target_listing_id and l.status = 'approved' and l.contact_public
        and (l.expires_at is null or l.expires_at > now())
      returning l.view_count into counter;
  end if;
  return counter;
end;
$$;
revoke all on function private.record_listing_view(uuid) from public, anon, authenticated;
grant usage on schema private to anon;
grant execute on function private.record_listing_view(uuid) to anon;

create or replace function public.record_listing_view(target_listing_id uuid)
returns bigint language sql security invoker set search_path = '' as $$
  select private.record_listing_view(target_listing_id);
$$;
revoke all on function public.record_listing_view(uuid) from public, anon, authenticated;
grant execute on function public.record_listing_view(uuid) to anon;

create index if not exists listings_admin_created_idx on public.listings (created_at desc, id desc);
create index if not exists listings_public_type_date_idx on public.listings
  (listing_type, approved_at desc, id desc) where status = 'approved' and contact_public;
create index if not exists listing_reports_open_listing_idx on public.listing_reports (listing_id)
  where resolved_at is null;
notify pgrst, 'reload schema';

-- Public readers receive the listing fields used on the marketplace, not
-- private email, exact unit code, legal notes or notification metadata.
revoke select on public.listings from anon;
grant select (
  id,listing_code,slug,listing_type,status,title,description,phase,tower,unit_type,bedroom_count,
  area_sqm,floor_label,price_vnd,furnishing,available_from,poster_name,contact_phone,is_featured,sort_priority,
  approved_at,expires_at,created_at,updated_at,view_count
) on public.listings to anon;
notify pgrst, 'reload schema';
