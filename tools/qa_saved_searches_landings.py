#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def read(path):
    target=ROOT/path
    assert target.exists(), f"missing {path}"
    return target.read_text(encoding="utf-8")

sql=read("supabase/marketplace-saved-searches.sql")
landing=read("tools/marketplace_landing_pages.py")
assert "saved_searches_owner_select" in sql
assert "user_id = (select auth.uid())" in sql
assert "revoke all on public.saved_searches from anon" in sql
assert "generate_marketplace_landing_pages" in landing
assert "minimum = 3 if tower else 2" in landing
assert 'meta name="robots" content="index,follow,max-image-preview:large"' in landing
assert '"@type":"ItemList"' in landing
print("saved search + landing page baseline checks passed")
