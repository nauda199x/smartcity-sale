#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from build_precinct_masterplans import PROJECTS
from integrate_precinct_masterplans import tower_display

ROOT = Path(__file__).resolve().parents[1]

GENERIC_REPLACEMENTS = {
    "Tra cứu mặt bằng · tổng thể · từng tòa": "Mặt bằng tổng thể · mặt bằng từng tòa",
    "Danh mục crawlable": "Danh sách mặt bằng từng tòa",
    "Mỗi tòa có URL riêng để Google và người dùng đi thẳng tới đúng hồ sơ kỹ thuật, thay vì gom toàn bộ bản vẽ vào một ảnh hoặc một trang chung.": "Mỗi tòa có một mặt bằng riêng để xem rõ lõi thang, hành lang, vị trí căn góc và từng trục căn trước khi lựa chọn.",
    "Đi từ sơ đồ phân khu tới đúng tòa, rồi mở mặt bằng HD để đọc lõi thang, trục căn và mã căn. Cấu trúc này giúp người xem tìm đúng dữ liệu mà không phải đoán từ một ảnh tổng.": "Xem mặt bằng tổng thể để xác định vị trí tòa, sau đó mở bản HD của từng tòa để đọc lõi thang, hành lang và từng trục căn.",
    "<strong>Lưu ý dữ liệu:</strong> website chỉ ghi các thông số đã có trong hồ sơ đang lưu. Khi chưa có bản tổng thể hoặc dữ kiện đủ tin cậy, trang giữ mô tả trung lập và dẫn sang đúng mặt bằng tòa thay vì suy đoán.": "<strong>Lưu ý:</strong> hướng, tầm nhìn và diện tích của một căn cụ thể nên được đối chiếu thêm trên hồ sơ căn hộ và kiểm tra thực tế trước khi giao dịch.",
    "Mặt bằng tòa · hồ sơ HD · liên kết phân khu": "Mặt bằng tòa · ảnh HD · căn hộ điển hình",
    "<p class=\"eyebrow section-kicker\">Cách đọc đúng</p>": "<p class=\"eyebrow section-kicker\">Xem nhanh mặt bằng</p>",
    "<strong>Đúng tòa:</strong>": "<strong>Mã tòa:</strong>",
    "<strong>Đúng bản vẽ:</strong>": "<strong>Ảnh HD:</strong>",
    "<strong>Đúng dữ kiện:</strong>": "<strong>Hướng &amp; view:</strong>",
    "Chuyển ngang giữa các tòa để so đúng mặt bằng thay vì quay lại Google hoặc dùng nhầm sơ đồ của tòa khác.": "Mở nhanh các tòa cùng phân khu để so layout, mật độ căn và vị trí trục trước khi chọn căn.",
    "<strong>Nguyên tắc dữ liệu:</strong> chỉ dùng thông số có trong hồ sơ hiện có; không tự suy hướng, view, mật độ hoặc diện tích khi chưa đủ căn cứ.": "<strong>Lưu ý khi xem căn:</strong> hướng và tầm nhìn nên được kiểm tra trên sơ đồ tổng thể và đối chiếu thực tế tại đúng tầng đang quan tâm.",
    "luồng tra cứu": "cách xem mặt bằng",
}

BANNED_VISIBLE_PHRASES = (
    "Danh mục crawlable",
    "URL riêng",
    "công cụ tìm kiếm",
    "quay lại Google",
    "SEO tốt",
    "website giữ mô tả trung lập",
    "luồng tra cứu",
    "Dữ liệu riêng của cụm",
    "Trang này không chỉ để mở ảnh kỹ thuật",
)


def humanize_project_page(project: dict) -> None:
    path = ROOT / "mat-bang-smart-city" / project["slug"] / "index.html"
    text = path.read_text(encoding="utf-8")
    for old, new in GENERIC_REPLACEMENTS.items():
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")


def humanize_tower_page(project: dict, tower: str) -> None:
    path = ROOT / "mat-bang-smart-city" / project["slug"] / tower / "index.html"
    text = path.read_text(encoding="utf-8")
    display = tower_display(project, tower)
    name = project["name"]

    for old, new in GENERIC_REPLACEMENTS.items():
        text = text.replace(old, new)

    text = text.replace(
        f"Mặt bằng tòa {display} {name}: bản vẽ HD và tòa cùng phân khu",
        f"Mặt bằng {display} {name}: sơ đồ tầng HD và các loại căn hộ",
    )
    text = text.replace(
        f"Trang này là hồ sơ riêng của {display}. Dùng đúng mặt bằng của tòa trước khi kết luận mã căn, vị trí lõi thang, trục góc, hướng/view hoặc so giá với căn khác.",
        f"Mặt bằng {display} giúp xác định từng trục căn, vị trí lõi thang và hành lang trước khi so giá hoặc đi xem nhà thực tế.",
    )
    text = text.replace(
        f"Thuộc <strong>{name}</strong>. URL riêng của hồ sơ này giúp người dùng và công cụ tìm kiếm không phải suy tòa từ một trang mặt bằng tổng.",
        f"Thuộc <strong>{name}</strong>. Mở ảnh HD để xem rõ mã căn, vị trí căn góc và khoảng cách tới lõi thang.",
    )

    for phrase in BANNED_VISIBLE_PHRASES:
        if phrase in text:
            raise AssertionError(f"technical/AI copy still visible in {project['slug']}/{tower}: {phrase}")

    path.write_text(text, encoding="utf-8")


def main() -> None:
    towers = 0
    for project in PROJECTS:
        humanize_project_page(project)
        for tower in project["towers"]:
            humanize_tower_page(project, tower)
            towers += 1
    print(f"humanized visible floorplan copy: {len(PROJECTS)} precinct pages + {towers} tower pages")


if __name__ == "__main__":
    main()
