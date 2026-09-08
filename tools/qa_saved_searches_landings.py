#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def read(path):
    target=ROOT/path
    assert target.exists(), f"missing {path}"
    return target.read_text(encoding="utf-8")

sql=read("supabase/marketplace-saved-searches.sql")
saved=read("assets/js/marketplace-saved-searches.js")
public_ui=read("assets/js/marketplace-saved-searches-ui.js")
account_ui=read("assets/js/marketplace-saved-searches-account.js")
account_page=read("tai-khoan-smart-city/index.html")
shell=read("assets/app-shell.js")
landing=read("tools/marketplace_landing_pages.py")
builder=read("tools/build_marketplace_landings.py")
workflow=read(".github/workflows/site-pipeline.yml")

checks={
    "saved searches are private RLS data":"saved_searches_owner_select" in sql and "user_id = (select auth.uid())" in sql,
    "anonymous saved-search access revoked":"revoke all on public.saved_searches from anon" in sql,
    "saved search tracks full price range":"min_price_vnd" in sql and "max_price_vnd" in sql and "saved_searches_price_range" in sql,
    "client counts approved matches since last view":"countMatches" in saved and 'params.set("approved_at",`gt.${search.last_seen_at}`)' in saved,
    "saved search upsert deduplicates criteria":"on_conflict" in saved and "user_id,fingerprint" in saved,
    "anonymous save intent survives login":"smartcity_marketplace_pending_saved_search_v1" in saved and "savePending" in public_ui,
    "public inventory exposes save-search control":"marketplace-save-search" in public_ui and "/tai-khoan-smart-city/?save_search=1" in public_ui,
    "account dashboard renders new match alerts":"data-count-new-matches" in account_page and "data-saved-search-list" in account_page and "countMatches" in account_ui,
    "opening saved search marks it seen":"saved.touch" in account_ui and "saved.urlFor" in account_ui,
    "shell lazily loads growth assets":"loadSavedSearchAssets" in shell and "marketplace-saved-searches-ui.js" in shell,
    "landing generator is inventory thresholded":"generate_marketplace_landing_pages" in landing and "minimum = 3 if tower else 2" in landing,
    "landing pages are indexable structured collections":'meta name="robots" content="index,follow,max-image-preview:large"' in landing and '"@type": "ItemList"' in landing and '"@type": "BreadcrumbList"' in landing,
    "landing build uses approved marketplace inventory":"fetch_approved_listings" in builder and "generate_marketplace_landing_pages" in builder,
    "CI validates and builds phase 3":"qa_saved_searches_landings.py" in workflow and "build_marketplace_landings.py" in workflow,
}

failed=[name for name,ok in checks.items() if not ok]
for name,ok in checks.items():print(("PASS" if ok else "FAIL"),name)
if failed:raise SystemExit(f"{len(failed)} saved-search/landing checks failed")
print(f"{len(checks)} saved-search + landing checks passed")
