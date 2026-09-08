-- Follow-up hardening for marketplace-member-accounts.sql.
-- Applied to the Smart City Supabase project on 2026-09-08.

-- The owner action is intentionally callable by authenticated members only.
-- Revoke anon explicitly because earlier project grants may survive a CREATE OR REPLACE.
revoke execute on function public.owner_listing_action(uuid,text) from anon;
revoke execute on function public.owner_listing_action(uuid,text) from public;
grant execute on function public.owner_listing_action(uuid,text) to authenticated;

-- Cache auth.uid() as an init plan rather than re-evaluating it for every row.
drop policy if exists listings_member_read_own on public.listings;
create policy listings_member_read_own
on public.listings
for select
to authenticated
using (owner_user_id = (select auth.uid()));

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
);

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
      and l.owner_user_id = (select auth.uid())
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
      and l.owner_user_id = (select auth.uid())
      and l.status = 'pending'
  )
);
