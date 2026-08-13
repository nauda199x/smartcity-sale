#!/usr/bin/env python3
"""Build Homepage Portal V3 from reviewed public inventory fields only."""
from collections import Counter
from datetime import date
from html import escape
from pathlib import Path
from statistics import median
import json
import re

from public_images import public_inventory_image

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "_source" / "homepage.html"
SAFE_FIELDS = {"Tòa", "Phân khu", "Loại", "Diện tích", "Tầng", "Nội thất", "Giá bán", "Giá mỗi m2"}
PUBLIC_IMAGE_FIELD = "Ảnh đại diện"
LOCAL_IMAGE_FALLBACK = "/images/hero/hero-smart-city-mobile.webp"


def public_image_url(row):
    """Return one reviewed public thumbnail; never read the source gallery field."""
    return public_inventory_image(row.get(PUBLIC_IMAGE_FIELD))


def is_positive_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0


def format_decimal(value):
    return f"{value:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".").rstrip("0").rstrip(",")


def listing_score(row):
    complete = sum(bool(row.get(key)) for key in SAFE_FIELDS)
    return (-complete, str(row.get("Phân khu") or ""), str(row.get("Tòa") or ""), str(row.get("Loại") or ""))


rows = json.loads((ROOT / "data.json").read_text(encoding="utf-8"))
visible = [row for row in rows if isinstance(row, dict) and row.get("Hiển thị trên Web") == "Có"]
valid_market = [row for row in visible if is_positive_number(row.get("Giá bán")) and is_positive_number(row.get("Diện tích"))]
unit_prices = [row["Giá mỗi m2"] for row in valid_market if is_positive_number(row.get("Giá mỗi m2"))]
types = Counter(str(row.get("Loại")) for row in visible if row.get("Loại"))
zones = Counter(str(row.get("Phân khu")) for row in visible if row.get("Phân khu"))

type_cards = []
for apartment_type in ("Studio", "1PN", "1PN+", "2PN", "2PN+", "3PN"):
    if types[apartment_type]:
        type_cards.append(
            f'<a href="/can-ho-dang-ban.html?q={escape(apartment_type)}"><span>{types[apartment_type]} căn</span>'
            f'<strong>{escape(apartment_type)}</strong><i aria-hidden="true">→</i></a>'
        )

candidates = [row for row in valid_market if public_image_url(row)]
featured, used_zones = [], set()
for row in sorted(candidates, key=listing_score):
    zone = str(row.get("Phân khu") or "")
    if zone in used_zones:
        continue
    featured.append(row)
    used_zones.add(zone)
    if len(featured) == 6:
        break
if len(featured) < 6:
    for row in sorted(candidates, key=listing_score):
        if row in featured:
            continue
        featured.append(row)
        if len(featured) == 6:
            break

featured_cards = []
for index, source in enumerate(featured, 1):
    # Whitelist prevents private pricing, notes, identifiers, fees and commissions entering HTML.
    row = {key: source.get(key) for key in SAFE_FIELDS}
    image = public_image_url(source)
    title = f'{row.get("Loại") or "Căn hộ"} · {row.get("Tòa") or row.get("Phân khu") or "Smart City"}'
    area = format_decimal(row["Diện tích"])
    price = format_decimal(row["Giá bán"] / 1_000_000_000)
    psm = format_decimal(row["Giá mỗi m2"]) if is_positive_number(row.get("Giá mỗi m2")) else ""
    meta = " · ".join(filter(None, (f"{area} m²", str(row.get("Tầng") or ""), str(row.get("Nội thất") or ""))))
    psm_html = f'<span>{psm} triệu/m²</span>' if psm else ""
    featured_cards.append(
        f'<article class="hp-listing"><div class="hp-listing__visual"><img src="{image}" alt="Ảnh căn {escape(title)}" '
        f'loading="lazy" width="1200" height="800" referrerpolicy="no-referrer" '
        f'onerror="this.onerror=null;this.src=\'{LOCAL_IMAGE_FALLBACK}\'"><span>{index:02d}</span>'
        f'<small>{escape(str(row.get("Phân khu") or "Smart City"))}</small></div><div class="hp-listing__body">'
        f'<p>{escape(str(row.get("Phân khu") or ""))}</p><h3>{escape(title)}</h3><div class="hp-listing__meta">{escape(meta)}</div>'
        f'<div class="hp-listing__price"><strong>{price} tỷ</strong>{psm_html}</div>'
        f'<a href="/can-ho-dang-ban.html?q={escape(str(row.get("Tòa") or row.get("Phân khu") or ""))}">Xem căn <span aria-hidden="true">→</span></a></div></article>'
    )

latest_date = max((str(row.get("Ngày xác nhận chủ") or "") for row in visible), default="")
try:
    parsed = date.fromisoformat(latest_date)
    updated = f"{parsed.day:02d}.{parsed.month:02d}.{parsed.year}"
except ValueError:
    updated = "đang cập nhật"
top_zone, top_count = zones.most_common(1)[0] if zones else ("Đang cập nhật", 0)
replacements = {
    "LIVE_COUNT": f"{len(visible):,}".replace(",", "."),
    "UPDATED_DATE": updated,
    "TYPE_CARDS": "".join(type_cards),
    "MEDIAN_PRICE": format_decimal(median(row["Giá bán"] for row in valid_market) / 1_000_000_000),
    "MEDIAN_PSM": format_decimal(median(unit_prices)),
    "TOP_ZONE": escape(top_zone), "TOP_ZONE_COUNT": str(top_count),
    "FEATURED_CARDS": "".join(featured_cards),
}
html = TEMPLATE.read_text(encoding="utf-8")
for key, value in replacements.items():
    html = html.replace("{{" + key + "}}", value)
unresolved = re.findall(r"{{[A-Z_]+}}", html)
if unresolved:
    raise RuntimeError(f"Unresolved homepage tokens: {unresolved}")
(ROOT / "index.html").write_text(html, encoding="utf-8")
print(f"built homepage: {len(visible)} listings, {len(featured)} featured, {len(types)} types")
