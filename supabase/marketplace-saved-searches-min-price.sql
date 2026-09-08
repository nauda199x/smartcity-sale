-- Production follow-up applied after marketplace-saved-searches.sql.
alter table public.saved_searches add column if not exists min_price_vnd bigint;

do $$ begin
  if not exists (select 1 from pg_constraint where conname='saved_searches_min_price_positive') then
    alter table public.saved_searches
      add constraint saved_searches_min_price_positive check (min_price_vnd is null or min_price_vnd > 0);
  end if;
  if not exists (select 1 from pg_constraint where conname='saved_searches_price_range') then
    alter table public.saved_searches
      add constraint saved_searches_price_range check (min_price_vnd is null or max_price_vnd is null or min_price_vnd <= max_price_vnd);
  end if;
end $$;
