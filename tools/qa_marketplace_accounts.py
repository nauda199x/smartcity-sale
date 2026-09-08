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
hardening = read("supabase/marketplace-member-accounts-hardening.sql")
growth2 = read("supabase/marketplace-bulk-freshness.sql")
template = read("assets/templates/mau-dang-nhieu-can-smart-city.csv")

checks = {
    "account page is intentionally noindex": 'name="robots" content="noindex,follow"' in page,
    "account page exposes sign in and sign up": 'data-member-form="signin"' in page and 'data-member-form="signup"' in page,
    "account page loads member client": "marketplace-account.js" in page and "marketplace-account-page.js" in page,
    "member client preserves anonymous posting": "originalCreateListing(data)" in account,
    "member client binds logged-in listing owner": "owner_user_id:session.user.id" in account,
    "member uploads use authenticated token": "originalUploadImage" in account and "token:session.access_token,body:file" in account,
    "member dashboard lists owned inventory": "owner_user_id:`eq.${session.user.id}`" in account and "listMine" in dashboard,
    "member dashboard exposes controlled lifecycle actions": all(action in dashboard for action in ['"hide"', '"relist"', '"done"', '"confirm"']),
    "shell exposes Tin cua toi navigation": "/tai-khoan-smart-city/" in shell,
    "posting form gets optional member enhancement": "loadMemberPostingEnhancements" in shell,
    "member CSS contains responsive rules": "@media(max-width:760px)" in css,
    "database adds nullable auth ownership": "add column if not exists owner_user_id uuid references auth.users(id)" in sql,
    "database authenticated insert binds auth uid": "owner_user_id = auth.uid()" in sql and "listings_member_submit_pending" in sql,
    "database owner action is controlled RPC": "owner_listing_action" in sql and "security definer" in sql,
    "storage upload is owner restricted": "can_upload_owned_pending_image" in sql and "listing_images_storage_member_upload" in sql,
    "owner RPC is explicitly denied to anon": "revoke execute on function public.owner_listing_action(uuid,text) from anon" in hardening,
    "bulk workspace exists": 'data-bulk-file' in page and 'data-bulk-import' in page and 'mau-dang-nhieu-can-smart-city.csv' in page,
    "bulk API caps batch size": "rows.length>50" in account and "bulkCreateListings" in account,
    "bulk API prevents account duplicates": "duplicateKey" in account and "existingKeys" in account and "batchKeys" in account,
    "bulk CSV parser validates smart city vocabulary": "parseCsv" in dashboard and "phaseFrom" in dashboard and "unitTypeFrom" in dashboard,
    "bulk template has required columns": all(column in template.splitlines()[0] for column in ["loai_giao_dich", "phan_khu", "toa", "loai_can", "dien_tich", "gia", "ten_nguoi_dang", "so_dien_thoai"]),
    "freshness metadata is persisted": "last_confirmed_at" in growth2 and "source_channel" in growth2,
    "freshness action does not grant moderation": "action_name = 'confirm'" in growth2 and "set last_confirmed_at = now()" in growth2,
    "member insert cannot claim admin source": "source_channel in ('form','bulk')" in growth2,
    "dashboard flags stale inventory": "days>21" in dashboard and "data-count-stale" in page and "member-freshness" in css,
    "growth2 assets use cache-busting version": "20260908-growth2" in page and "20260908-growth2" in shell,
}

failed = [name for name, ok in checks.items() if not ok]
for name, ok in checks.items():
    print(("PASS" if ok else "FAIL"), name)

if failed:
    raise SystemExit(f"{len(failed)} marketplace account checks failed")

print(f"{len(checks)} marketplace account checks passed")
