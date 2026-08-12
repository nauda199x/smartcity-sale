import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data.json"
INDEX = ROOT / "index.html"


def money_number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def normalize_data():
    rows = json.loads(DATA.read_text(encoding="utf-8"))
    changed = 0
    for row in rows:
        # The sale site historically stored the sale price in a column named
        # "Giá thuê". The front-end already documented this as a sale-data
        # compatibility field, so migrate the source data to the correct name.
        if "Giá thuê" in row:
            if "Giá bán" not in row or not row.get("Giá bán"):
                row["Giá bán"] = row.get("Giá thuê")
            del row["Giá thuê"]
            changed += 1

        price = money_number(row.get("Giá bán"))
        area = money_number(row.get("Diện tích"))
        m2 = money_number(row.get("Giá mỗi m2"))

        # Keep the public m² figure mathematically consistent with the sale price
        # when the source contains an obvious transcription error (>15%).
        if price and area and area > 0:
            expected_m2 = price / area / 1_000_000
            if not m2 or abs(m2 - expected_m2) / expected_m2 > 0.15:
                row["Giá mỗi m2"] = round(expected_m2, 1)
                changed += 1

        # "Giá bao phí" must be close to the sale price. Values wildly above the
        # sale price are not safely inferable, so blank them instead of inventing a
        # number that could mislead a buyer.
        bao_phi = money_number(row.get("Giá bao phí tỷ"))
        if price and bao_phi is not None:
            bao_phi_vnd = bao_phi * 1_000_000_000 if bao_phi < 1000 else bao_phi
            if bao_phi_vnd < price or bao_phi_vnd > price + 500_000_000:
                row["Giá bao phí tỷ"] = ""
                row["Ghi chú dữ liệu"] = "Giá bao phí cần xác nhận lại với chủ nhà"
                changed += 1

        # A missing area should not be displayed as a fabricated value.
        if area is None or area <= 0:
            row["Diện tích"] = ""

    DATA.write_text(json.dumps(rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return changed, len(rows)


def replace_once(text, old, new):
    if old not in text:
        return text, False
    return text.replace(old, new), True


def normalize_index():
    text = INDEX.read_text(encoding="utf-8")
    changed = 0

    replacements = [
        (
            'const price = parseMoney(row["Giá thuê"] || row["Giá bán"]);',
            'const price = parseMoney(row["Giá bán"] || row["Giá thuê"]);'
        ),
        (
            '/* LUU Y: khoa trong data.json van la "Gia thue" du day la mang BAN.\n         Giu nguyen ten do de dung chung ma JavaScript voi ben cho thue.\n         Gia tri la DONG (2265000000), formatPrice() se doi ra ty khi hien. */',
            '/* MANG BAN: gia duoc luu o truong "Gia ban" theo DONG. */'
        ),
        (
            '"text": "Giá bán dao động phổ biến từ khoảng 2,2 tỷ với căn Studio đến trên 9 tỷ với căn 2-3 phòng ngủ ở phân khu cao cấp. Tính theo mét vuông thì mặt bằng chung khoảng 66 đến 122 triệu mỗi m², tùy phân khu, tầng và hướng. Mỗi căn trên trang đều ghi sẵn giá mỗi m² để anh/chị so nhanh."',
            '"text": "Giá bán thay đổi theo loại căn, phân khu, diện tích, tầng, hướng, nội thất và thời điểm chủ nhà xác nhận. Mỗi căn trên trang đều ghi giá bán và giá mỗi m² để anh/chị tự so sánh; giá thực tế cần xác nhận lại trước khi giao dịch."'
        ),
        (
            '"text": "Vinhomes Smart City tọa lạc tại quận Nam Từ Liêm, Hà Nội, là một trong những khu đô thị thông minh quy mô lớn tại khu vực phía Tây thủ đô."',
            '"text": "Vinhomes Smart City nằm trên Đại lộ Thăng Long, khu vực phường Tây Mỗ và phường Đại Mỗ, thành phố Hà Nội. Từ ngày 01/07/2025, Hà Nội vận hành mô hình chính quyền địa phương hai cấp và kết thúc đơn vị hành chính cấp huyện."'
        ),
        (
            '"name": "Vinhomes Smart City, Nam Từ Liêm, Hà Nội"',
            '"name": "Vinhomes Smart City, phường Tây Mỗ và phường Đại Mỗ, thành phố Hà Nội"'
        ),
        (
            '"addressLocality": "Tây Mỗ",\n      "addressRegion": "Hà Nội",',
            '"addressLocality": "Tây Mỗ và Đại Mỗ",\n      "addressRegion": "Hà Nội",'
        ),
        (
            '"_ghiChu": "sameAs dang tro ve kenh mang xa hoi cua ben CHO THUE. Day la kenh that nen giu lai giup Google noi hai site cung mot chu. Khi lap kenh rieng cho mang ban thi doi lai.",\n  "sameAs": [\n      "https://www.facebook.com/people/T%C3%ACm-thu%C3%AA-Smart-City/61591756688919/",\n      "https://www.tiktok.com/@timthuesmartcity",\n      "https://www.instagram.com/timthuesmartcity_com/",\n      "https://www.youtube.com/@Timthuesmartcity"\n    ],\n',
            ''
        ),
        (
            'placeholder="Tìm phân khu, mã căn, loại căn… (VD: Sapphire, 2PN, 8 triệu)"',
            'placeholder="Tìm phân khu, mã căn, loại căn… (VD: Sapphire, 2PN+, 3,5 tỷ)"'
        ),
        (
            '6,5 - 7,5 triệu',
            '2,5 - 3,5 tỷ'
        ),
        (
            '7,5 - 10 triệu',
            '3,5 - 5 tỷ'
        ),
        (
            '10 - 12 triệu',
            '5 - 7 tỷ'
        ),
        (
            '12 - 15 triệu',
            'Trên 7 tỷ'
        ),
        (
            'Trên 15 triệu',
            'Liên hệ để xác nhận'
        ),
        (
            'Ngày cần vào ở',
            'Thời điểm dự kiến mua'
        ),
        (
            'VD: Sa2, gần hồ...',
            'VD: SA2, gần hồ...'
        ),
        (
            'Nhu cầu khác (số người ở, có thú cưng, view...)',
            'Nhu cầu khác (tài chính, view, nội thất...)'
        ),
    ]

    for old, new in replacements:
        text, did = replace_once(text, old, new)
        changed += int(did)

    INDEX.write_text(text, encoding="utf-8")
    return changed


if __name__ == "__main__":
    data_changes, count = normalize_data()
    index_changes = normalize_index()
    print(f"Normalized {count} listings; data changes={data_changes}; index changes={index_changes}")
