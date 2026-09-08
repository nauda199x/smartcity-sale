#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    target = ROOT / path
    assert target.exists(), f"missing {path}"
    return target.read_text(encoding="utf-8")


page = read("tai-khoan-smart-city/index.html")
account = read("assets/js/marketplace-account.js")
dashboard = read("assets/js/marketplace-account-page.js")
shell = read("assets/app-shell.js")
css = read("assets/css/marketplace-account.css")
sql = read("supabase/marketplace-member-accounts.sql")

checks = {
    "account page is intentionally noindex": 'name="robots" content="noindex,follow"' in page,
    "account page exposes sign in and sign up": 'data-member-form="signin"' in page and 'data-member-form="signup"' in page,
    "account page loads member client": "marketplace-account.js" in page and "marketplace-account-page.js" in page,
    "member client preserves anonymous posting": "originalCreateListing(data)" in account,
    "member client binds logged-in listing owner": "owner_user_id:session.user.id" in account,
    "member uploads use authenticated token": "originalUploadImage" in account and "token:session.access_token,body:file" in account,
    "member dashboard lists owned inventory": "owner_user_id:`eq.${session.user.id}`" in account and "listMine" in dashboard,
    "member dashboard exposes controlled lifecycle actions": all(action in dashboard for action in ['"hide"', '"relist"', '"done"']),
    "shell exposes Tin cua toi navigation": "/tai-khoan-smart-city/" in shell,
    "posting form gets optional member enhancement": "loadMemberPostingEnhancements" in shell,
    "member CSS contains responsive rules": "@media(max-width:760px)" in css,
    "database adds nullable auth ownership": "add column if not exists owner_user_id uuid references auth.users(id)" in sql,
    "database authenticated insert binds auth uid": "owner_user_id = auth.uid()" in sql and "listings_member_submit_pending" in sql,
    "database owner action is controlled RPC": "owner_listing_action" in sql and "security definer" in sql,
    "storage upload is owner restricted": "can_upload_owned_pending_image" in sql and "listing_images_storage_member_upload" in sql,
}

failed = [name for name, ok in checks.items() if not ok]
for name, ok in checks.items():
    print(("PASS" if ok else "FAIL"), name)

if failed:
    raise SystemExit(f"{len(failed)} marketplace account checks failed")

print(f"{len(checks)} marketplace account checks passed")
