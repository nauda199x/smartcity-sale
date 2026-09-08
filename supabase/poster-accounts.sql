-- Poster accounts for timmuasmartcity.com.
-- Applied to Supabase project smartcity-marketplace on 2026-09-08.
-- Anonymous posting remains supported; signed-in posts gain owner_user_id so the
-- poster can manage them without receiving administrator privileges.

alter table public.listings
  add column if not exists owner_user_id uuid references auth.users(id) on delete set null;

create index if not exists listings_owner_user_id_idx on public.listings(owner_user_id);
create index if not exists listings_owner_status_created_idx on public.listings(owner_user_id, status, created_at desc);

create table if not exists public.marketplace_profiles (
  user_id uuid primary key references auth.users(id) on delete cascade,
  display_name text not null,
  phone text not null,
  poster_type text not null default 'agent' check (poster_type in ('owner','agent')),
  company_name text,
  is_verified boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint marketplace_profiles_name_len check (char_length(btrim(display_name)) between 2 and 120),
  constraint marketplace_profiles_phone_len check (char_length(btrim(phone)) between 8 and 30),
  constraint marketplace_profiles_company_len check (company_name is null or char_length(company_name) <= 160)
);

alter table public.marketplace_profiles enable row level security;

drop policy if exists marketplace_profiles_owner_read on public.marketplace_profiles;
create policy marketplace_profiles_owner_read
on public.marketplace_profiles for select to authenticated
using (user_id = auth.uid());

drop policy if exists marketplace_profiles_admin_manage on public.marketplace_profiles;
create policy marketplace_profiles_admin_manage
on public.marketplace_profiles for all to authenticated
using ((select private.is_admin()))
with check ((select private.is_admin()));

grant select on public.marketplace_profiles to authenticated;
revoke insert, update, delete on public.marketplace_profiles from authenticated;

drop policy if exists listings_owner_read on public.listings;
create policy listings_owner_read
on public.listings for select to authenticated
using (owner_user_id = auth.uid());

drop policy if exists listings_owner_submit_pending on public.listings;
create policy listings_owner_submit_pending
on public.listings for insert to authenticated
with check (
  owner_user_id = auth.uid()
  and status = 'pending'
  and contact_public
  and not is_featured
  and sort_priority = 0
  and approved_at is null
  and expires_at is null
);

create or replace function public.marketplace_upsert_profile(
  p_display_name text,
  p_phone text,
  p_poster_type text default 'agent',
  p_company_name text default null
)
returns public.marketplace_profiles
language plpgsql
security definer
set search_path = public
as $$
declare
  v_uid uuid := auth.uid();
  v_row public.marketplace_profiles;
begin
  if v_uid is null then
    raise exception 'authentication_required' using errcode = '42501';
  end if;
  if char_length(btrim(coalesce(p_display_name,''))) not between 2 and 120 then
    raise exception 'invalid_display_name' using errcode = '22023';
  end if;
  if char_length(btrim(coalesce(p_phone,''))) not between 8 and 30 then
    raise exception 'invalid_phone' using errcode = '22023';
  end if;
  if p_poster_type not in ('owner','agent') then
    raise exception 'invalid_poster_type' using errcode = '22023';
  end if;
  if p_company_name is not null and char_length(p_company_name) > 160 then
    raise exception 'invalid_company_name' using errcode = '22023';
  end if;

  insert into public.marketplace_profiles(user_id,display_name,phone,poster_type,company_name)
  values (v_uid,btrim(p_display_name),btrim(p_phone),p_poster_type,nullif(btrim(coalesce(p_company_name,'')),''))
  on conflict (user_id) do update set
    display_name = excluded.display_name,
    phone = excluded.phone,
    poster_type = excluded.poster_type,
    company_name = excluded.company_name,
    updated_at = now()
  returning * into v_row;

  return v_row;
end;
$$;

create or replace function public.marketplace_my_listing_action(
  p_listing_id uuid,
  p_action text
)
returns table(id uuid, status text, expires_at timestamptz, updated_at timestamptz)
language plpgsql
security definer
set search_path = public
as $$
declare
  v_uid uuid := auth.uid();
  v_type text;
  v_status text;
begin
  if v_uid is null then
    raise exception 'authentication_required' using errcode = '42501';
  end if;

  select listing_type, listings.status into v_type, v_status
  from public.listings
  where listings.id = p_listing_id and owner_user_id = v_uid
  for update;

  if not found then
    raise exception 'listing_not_found' using errcode = 'P0002';
  end if;

  if p_action = 'hide' then
    update public.listings
      set status='expired', expires_at=now(), is_featured=false, sort_priority=0, updated_at=now()
      where listings.id=p_listing_id and owner_user_id=v_uid;
  elsif p_action = 'done' then
    update public.listings
      set status=case when v_type='rent' then 'rented' else 'sold' end,
          expires_at=coalesce(expires_at,now()), is_featured=false, sort_priority=0, updated_at=now()
      where listings.id=p_listing_id and owner_user_id=v_uid;
  elsif p_action = 'renew' then
    if v_status not in ('expired','rejected','sold','rented') then
      raise exception 'listing_not_renewable' using errcode = '22023';
    end if;
    update public.listings
      set status='pending', approved_at=null, expires_at=null, is_featured=false, sort_priority=0, updated_at=now()
      where listings.id=p_listing_id and owner_user_id=v_uid;
  else
    raise exception 'invalid_action' using errcode = '22023';
  end if;

  return query
    select listings.id, listings.status, listings.expires_at, listings.updated_at
    from public.listings
    where listings.id=p_listing_id and owner_user_id=v_uid;
end;
$$;

revoke all on function public.marketplace_upsert_profile(text,text,text,text) from public;
grant execute on function public.marketplace_upsert_profile(text,text,text,text) to authenticated;
revoke all on function public.marketplace_my_listing_action(uuid,text) from public;
grant execute on function public.marketplace_my_listing_action(uuid,text) to authenticated;
