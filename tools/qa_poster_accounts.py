#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def require(path, *needles):
    text = (ROOT / path).read_text(encoding="utf-8")
    missing = [needle for needle in needles if needle not in text]
    assert not missing, f"{path}: missing {missing}"
    return text

page = require(
    "tai-khoan-smart-city/index.html",
    'data-account-root',
    'data-login-form',
    'data-register-form',
    'data-account-dashboard',
    'data-my-listings',
    'marketplace-account.js',
    'marketplace-account.css',
    'name="robots" content="noindex,follow"',
)
assert "service_role" not in page.lower()

account = require(
    "assets/js/marketplace-account.js",
    'smartcity_marketplace_user_session',
    'owner_user_id',
    'marketplace_upsert_profile',
    'marketplace_my_listing_action',
    'listMyListings',
    'ownedCreateListing',
    'api.createListing=async data=>',
)
assert "service_role" not in account.lower()
assert "supabasePublishableKey" in account
assert "localStorage" in account

migration = require(
    "supabase/poster-accounts.sql",
    "owner_user_id uuid references auth.users(id)",
    "marketplace_profiles",
    "listings_owner_submit_pending",
    "owner_user_id = auth.uid()",
    "marketplace_my_listing_action",
    "marketplace_upsert_profile",
)
assert "service_role" not in migration.lower()

prepare = require("tools/prepare_portal_v2.py", '"tai-khoan-smart-city"')
shell = require(
    "assets/app-shell.js",
    '/tai-khoan-smart-city/',
    'marketplace-account.js',
    'addPosterAccountLink',
)

print("poster-account checks passed")
