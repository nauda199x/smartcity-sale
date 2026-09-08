-- Follow-up to poster-accounts.sql. Signed-in posters need to read the image
-- rows attached to their own pending/expired listings in the account dashboard.

drop policy if exists listing_images_owner_read on public.listing_images;
create policy listing_images_owner_read
on public.listing_images for select to authenticated
using (
  exists (
    select 1 from public.listings
    where listings.id = listing_images.listing_id
      and listings.owner_user_id = auth.uid()
  )
);
