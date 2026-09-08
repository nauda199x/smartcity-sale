-- Optional marketplace member accounts for timmuasmartcity.com.
-- Anonymous posting remains available; signed-in posters gain ownership and self-service actions.

alter table public.listings
  add column if not exists owner_user_id uuid references auth.users(id) on delete set null;

create index if not exists listings_owner_user_created_idx
  on public.listings(owner_user_id, created_at desc)
  where owner_user_id is not null;

comment on column public.listings.owner_user_id is
  'Optional Supabase Auth owner. Null means the listing was submitted without an account.';

-- A normal authenticated member may read only their own non-public records.
-- Approved public inventory continues to be read anonymously by the public UI.
drop policy if exists listings_member_read_own on public.listings;
create policy listings_member_read_own
on public.listings
for select
to authenticated
using (owner_user_id = auth.uid());

-- Keep member creation as strict as anonymous submission, while binding ownership
-- to the JWT subject. Admin users continue to be covered by listings_admin_manage.
drop policy if exists listings_member_submit_pending on public.listings;
create policy listings_member_submit_pending
on public.listings
for insert
to authenticated
with check (
  owner_user_id = auth.uid()
  and status = 'pending'
  and contact_public
  and not is_featured
  and sort_priority = 0
  and approved_at is null
  and expires_at is null
);

-- Members can read and attach images only for listings they own.
drop policy if exists listing_images_member_read_own on public.listing_images;
create policy listing_images_member_read_own
on public.listing_images
for select
to authenticated
using (
  exists (
    select 1
    from public.listings l
    where l.id = listing_images.listing_id
      and l.owner_user_id = auth.uid()
  )
);

drop policy if exists listing_images_member_insert_own on public.listing_images;
create policy listing_images_member_insert_own
on public.listing_images
for insert
to authenticated
with check (
  storage_path like ('pending/' || listing_id::text || '/%')
  and exists (
    select 1
    from public.listings l
    where l.id = listing_images.listing_id
      and l.owner_user_id = auth.uid()
      and l.status = 'pending'
  )
);

-- Storage uploads are additionally tied to the pending listing owner. The existing
-- helper still enforces the upload path/rate/size rules used by anonymous posters.
create or replace function private.can_upload_owned_pending_image(object_name text)
returns boolean
language plpgsql
stable
security definer
set search_path = public, storage, pg_temp
as $$
declare
  listing_uuid uuid;
begin
  if auth.uid() is null or split_part(object_name, '/', 1) <> 'pending' then
    return false;
  end if;

  begin
    listing_uuid := split_part(object_name, '/', 2)::uuid;
  exception when others then
    return false;
  end;

  return exists (
    select 1
    from public.listings l
    where l.id = listing_uuid
      and l.owner_user_id = auth.uid()
      and l.status = 'pending'
  );
end;
$$;

revoke all on function private.can_upload_owned_pending_image(text) from public;
grant execute on function private.can_upload_owned_pending_image(text) to authenticated;

drop policy if exists listing_images_storage_member_upload on storage.objects;
create policy listing_images_storage_member_upload
on storage.objects
for insert
to authenticated
with check (
  bucket_id = 'listing-images'
  and private.can_upload_pending_image(name)
  and private.can_upload_owned_pending_image(name)
  and lower(storage.extension(name)) = any (array['jpg','jpeg','png','webp']::text[])
);

-- Controlled owner actions. Members never receive generic UPDATE permission through
-- RLS, so moderation fields cannot be changed directly from the browser.
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
          is_featured = false,
          sort_priority = 0
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
    'updated_at', row_after.updated_at
  );
end;
$$;

revoke all on function public.owner_listing_action(uuid, text) from public;
grant execute on function public.owner_listing_action(uuid, text) to authenticated;
