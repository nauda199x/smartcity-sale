#!/usr/bin/env python3
from __future__ import annotations

from html import escape, unescape
from pathlib import Path
import re

from build_precinct_masterplans import PROJECTS
from integrate_precinct_masterplans import tower_display

ROOT = Path(__file__).resolve().parents[1]
START = "<!-- TOWER_EDITORIAL_START -->"
END = "<!-- TOWER_EDITORIAL_END -->"
CSS = '<link rel="stylesheet" href="/assets/css/tower-editorial.css?v=20260910-1">'


def strip_html(value: str) -> str:
    value = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", value, flags=re.S | re.I)
    value = re.sub(r"<[^>]+>", " ", value)
    value = unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def tower_summary(text: str, display: str, project_name: str) -> str:
    match = re.search(r'<p\b[^>]*class=["\'][^"\']*\blead\b[^"\']*["\'][^>]*>(.*?)</p>', text, flags=re.S | re.I)
    if match:
        summary = strip_html(match.group(1))
        if len(summary) >= 24:
            return summary
    meta = re.search(r'<meta\b[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)', text, flags=re.I)
    if meta:
        summary = strip_html(meta.group(1))
        if len(summary) >= 24:
            return summary
    return f"{display} có hồ sơ mặt bằng riêng trong cụm {project_name}; nên đọc đúng bản vẽ của tòa trước khi so một căn cụ thể."


def tower_tokens(tower: str, display: str) -> set[str]:
    tokens = {tower.upper(), display.upper(), tower.replace("-", ".").upper(), tower.replace("-", " ").upper()}
    return {token for token in tokens if token}


def matched_cards(project: dict, tower: str, display: str) -> list[tuple[str, str]]:
    tokens = tower_tokens(tower, display)
    matches = []
    for title, body in project.get("cards", []):
        haystack = f"{title} {body}".upper()
        if any(token in haystack for token in tokens):
            matches.append((title, body))
    if matches:
        return matches[:2]
    cards = list(project.get("cards", []))
    if not cards:
        return []
    idx = project["towers"].index(tower)
    return [cards[idx % len(cards)], cards[(idx + 1) % len(cards)]] if len(cards) > 1 else cards


def sibling_context(project: dict, tower: str) -> tuple[str | None, str | None]:
    towers = project["towers"]
    idx = towers.index(tower)
    previous_tower = towers[idx - 1] if idx > 0 else None
    next_tower = towers[idx + 1] if idx < len(towers) - 1 else None
    prev_name = tower_display(project, previous_tower) if previous_tower else None
    next_name = tower_display(project, next_tower) if next_tower else None
    return prev_name, next_name


def card_articles(project: dict, tower: str, display: str) -> str:
    rows = []
    for title, body in matched_cards(project, tower, display):
        rows.append(
            '<article class="tower-editorial-card">'
            f'<h3>{escape(title)}</h3><p>{escape(body)}</p>'
            f'<p>Khi xem <strong>{escape(display)}</strong>, phần này nên được đối chiếu lại trên đúng ảnh HD của tòa. '
            'Điểm quan trọng là phân biệt dữ kiện có trên bản vẽ với những yếu tố chỉ có thể xác nhận ngoài thực địa.</p>'
            '</article>'
        )
    return "".join(rows)


def analysis_articles(project: dict, display: str) -> str:
    rows = []
    for title, body in project.get("analysis", []):
        rows.append(
            '<article class="tower-editorial-card tower-editorial-card--analysis">'
            f'<h3>{escape(title)}</h3><p>{escape(body)}</p>'
            f'<p>Với {escape(display)}, nguyên tắc này giúp giảm nhầm giữa vị trí tòa, vị trí trục căn và cảm nhận view thực tế. '
            'Nếu bản vẽ không thể hiện đủ ký hiệu, website giữ mô tả trung lập thay vì suy đoán.</p>'
            '</article>'
        )
    return "".join(rows)


def facts_markup(project: dict) -> str:
    return "".join(f"<span>{escape(fact)}</span>" for fact in project.get("facts", []))


def compare_neighbors(project: dict, tower: str) -> str:
    slug = project["slug"]
    prev_name, next_name = sibling_context(project, tower)
    items = []
    if prev_name:
        idx = project["towers"].index(tower)
        prev_slug = project["towers"][idx - 1]
        items.append(f'<a href="/mat-bang-smart-city/{slug}/{prev_slug}/"><strong>So với {escape(prev_name)}</strong><span>Mở tòa liền trước để đối chiếu hình khối, lõi thang và trục căn.</span></a>')
    if next_name:
        idx = project["towers"].index(tower)
        next_slug = project["towers"][idx + 1]
        items.append(f'<a href="/mat-bang-smart-city/{slug}/{next_slug}/"><strong>So với {escape(next_name)}</strong><span>Mở tòa liền sau để nhận ra khác biệt trước khi chốt một trục căn.</span></a>')
    items.append(f'<a href="/mat-bang-smart-city/{slug}/"><strong>So toàn {escape(project["name"])}</strong><span>Quay về mặt bằng phân khu để đặt tòa trong đúng bối cảnh tổng thể.</span></a>')
    return "".join(items)


def editorial_block(project: dict, tower: str, summary: str) -> str:
    slug = project["slug"]
    name = project["name"]
    display = tower_display(project, tower)
    cards = card_articles(project, tower, display)
    analysis = analysis_articles(project, display)
    facts = facts_markup(project)
    comparisons = compare_neighbors(project, tower)
    return f'''{START}
<section class="section tower-editorial" id="tim-hieu-toa-{escape(tower)}" aria-labelledby="tower-editorial-title">
  <div class="container tower-editorial__container">
    <header class="tower-editorial__hero">
      <div>
        <p class="eyebrow section-kicker">Hồ sơ tòa · đọc để chọn căn</p>
        <h2 id="tower-editorial-title">Tìm hiểu mặt bằng {escape(display)} {escape(name)} trước khi mua hoặc thuê</h2>
      </div>
      <p class="tower-editorial__lead">{escape(summary)} Trang này không chỉ để mở ảnh kỹ thuật: phần nội dung dưới đây giúp đặt bản vẽ của {escape(display)} vào đúng bối cảnh {escape(name)}, biết nên nhìn điểm nào và tránh nhầm dữ kiện khi so căn.</p>
    </header>

    <div class="tower-editorial__facts" aria-label="Dữ kiện cấp phân khu">{facts}</div>

    <div class="tower-editorial__intro">
      <article>
        <h3>Mặt bằng {escape(display)} cho biết điều gì?</h3>
        <p>Giá trị lớn nhất của mặt bằng tòa là cho thấy cấu trúc tổ chức một tầng: vị trí lõi thang, hành lang, các trục góc và quan hệ giữa những căn nằm trên cùng một sàn. Khi người mua hoặc người thuê đã biết chính xác tòa {escape(display)}, việc đọc đúng sơ đồ của tòa sẽ hữu ích hơn rất nhiều so với xem một ảnh tổng của toàn dự án.</p>
        <p>Với một căn cụ thể, nên dùng bản vẽ để xác định <strong>trục căn và tương quan trên mặt sàn</strong> trước; sau đó mới đối chiếu diện tích, tầng, hướng cửa, hướng ban công, khoảng chắn và view thực tế. Những thông tin cuối cùng chỉ nên kết luận khi tài liệu hoặc hiện trạng cho phép xác nhận.</p>
      </article>
      <article>
        <h3>{escape(display)} nằm trong bối cảnh {escape(name)}</h3>
        <p>{escape(project['lead'])} Vì vậy một mặt bằng tòa không nên bị đọc tách khỏi phân khu. Hai căn có diện tích gần nhau vẫn có thể cho trải nghiệm khác nếu nằm ở tòa khác, trục khác hoặc tiếp cận cảnh quan và tiện ích theo cách khác.</p>
        <p>Trước khi chốt một mã căn, người xem nên quay lại <a href="/mat-bang-smart-city/{slug}/#mat-bang-tong-the">mặt bằng tổng {escape(name)}</a> để xác định đúng vị trí tòa, rồi trở lại bản vẽ HD của {escape(display)} để đọc chi tiết. Đây là luồng tra cứu mà website dùng xuyên suốt cho toàn bộ Smart City.</p>
      </article>
    </div>

    <div class="tower-editorial__section-head">
      <div><p class="eyebrow section-kicker">Dữ liệu riêng của cụm</p><h2>Điểm cần đọc kỹ trên {escape(display)}</h2></div>
      <p>Các ghi chú dưới đây lấy từ hồ sơ phân khu đang có trong website, sau đó đặt lại vào ngữ cảnh của đúng tòa để người xem dùng được khi so căn.</p>
    </div>
    <div class="tower-editorial__cards">{cards}</div>

    <div class="tower-editorial__section-head">
      <div><p class="eyebrow section-kicker">Phân tích khi chọn căn</p><h2>Từ bản vẽ đến quyết định mua hoặc thuê</h2></div>
      <p>SEO tốt không phải lặp từ khóa “mặt bằng” nhiều lần. Nội dung cần trả lời được các câu hỏi mà người dùng thực sự gặp khi chuyển từ xem sơ đồ sang chọn một căn hộ.</p>
    </div>
    <div class="tower-editorial__cards tower-editorial__cards--analysis">{analysis}</div>

    <div class="tower-editorial__checklist">
      <div class="tower-editorial__checklist-copy">
        <p class="eyebrow section-kicker">Checklist thực tế</p>
        <h2>Cách kiểm tra một căn tại {escape(display)}</h2>
        <p>Để tránh chọn căn chỉ vì giá hoặc ảnh nội thất đẹp, có thể đi theo bốn lớp kiểm tra. Cách này đặc biệt hữu ích khi cùng một tòa có nhiều trục và nhiều tầng đang được đăng bán/cho thuê.</p>
      </div>
      <ol>
        <li><strong>Chốt đúng tòa và đúng trục.</strong><span>Đối chiếu mã căn trên bản vẽ {escape(display)}; không lấy vị trí trục từ tòa khác áp sang.</span></li>
        <li><strong>Đọc lõi thang và hành lang.</strong><span>Xem căn nằm ở góc, giữa hành lang hay gần lõi giao thông để hiểu bố cục trên tầng.</span></li>
        <li><strong>Đối chiếu hướng và khoảng nhìn.</strong><span>Chỉ kết luận khi có la bàn, sơ đồ tổng hoặc dữ liệu thực địa đủ rõ; không suy hướng từ tên mã căn.</span></li>
        <li><strong>Sau cùng mới so giá.</strong><span>Khi đã chốt được tòa, trục, tầng và trạng thái căn, việc so tin bán/thuê mới có ý nghĩa và ít sai lệch hơn.</span></li>
      </ol>
    </div>

    <div class="tower-editorial__section-head">
      <div><p class="eyebrow section-kicker">So sánh nhanh</p><h2>Đặt {escape(display)} cạnh các tòa cùng phân khu</h2></div>
      <p>Một trang tòa mạnh cần dẫn người xem tới lựa chọn kế tiếp, không biến họ thành người phải quay lại Google mỗi lần muốn so một mặt bằng khác.</p>
    </div>
    <div class="tower-editorial__compare">{comparisons}</div>

    <div class="tower-editorial__faq" id="faq-mat-bang-{escape(tower)}">
      <div class="tower-editorial__section-head">
        <div><p class="eyebrow section-kicker">Câu hỏi thường gặp</p><h2>FAQ về mặt bằng {escape(display)}</h2></div>
        <p>Câu trả lời ưu tiên cách tra cứu an toàn và những dữ kiện website đang có, thay vì cố điền các thông số chưa được xác minh.</p>
      </div>
      <details open><summary>Mặt bằng {escape(display)} dùng để xem những gì?</summary><p>Dùng để đọc cấu trúc mặt sàn của đúng tòa: lõi thang, hành lang, các trục căn và quan hệ giữa các căn trên tầng. Khi cần xác định một căn cụ thể, hãy mở ảnh HD rồi phóng to mã căn trước khi đối chiếu các thông tin giao dịch.</p></details>
      <details><summary>Có thể suy hướng căn chỉ từ mặt bằng {escape(display)} không?</summary><p>Không nên. Nếu bản vẽ không thể hiện ký hiệu phương hướng hoặc chưa được đặt trong sơ đồ tổng có định hướng rõ, việc tự gán Đông/Tây/Nam/Bắc có thể gây sai. Website chỉ kết luận hướng khi có đủ căn cứ để đối chiếu.</p></details>
      <details><summary>Nên so {escape(display)} với tòa khác như thế nào?</summary><p>Hãy so theo cùng một trình tự: vị trí tòa trong {escape(name)}, hình khối và lõi giao thông, trục căn, tầng, khoảng nhìn thực tế rồi mới đến giá. Cách này giúp tránh việc hai căn “cùng số phòng ngủ” bị coi là tương đương khi bối cảnh mặt bằng khác nhau.</p></details>
      <details><summary>Sau khi xem mặt bằng, tìm căn đang bán hoặc cho thuê ở đâu?</summary><p>Anh/chị có thể đi tiếp tới <a href="/mua-ban-smart-city/">danh sách căn đang bán</a>, <a href="/cho-thue-smart-city/">danh sách căn cho thuê</a> hoặc <a href="/giao-dich-smart-city/">cổng giao dịch Smart City</a>. Nên ghi lại tòa và trục cần tìm trước khi lọc tin.</p></details>
    </div>

    <div class="tower-editorial__cta">
      <div><p class="eyebrow section-kicker">Bước tiếp theo</p><h2>Đã hiểu mặt bằng {escape(display)}? Chuyển sang xem căn thực tế.</h2><p>Dùng mặt bằng để thu hẹp tòa và trục, sau đó mới so căn đang giao dịch để tránh mất thời gian với những lựa chọn không phù hợp.</p></div>
      <div class="tower-editorial__cta-actions"><a class="btn btn-primary" href="/mua-ban-smart-city/">Xem căn đang bán</a><a class="btn" href="/cho-thue-smart-city/">Xem căn cho thuê</a></div>
    </div>
  </div>
</section>
{END}'''


def ensure_css(text: str) -> str:
    pattern = r'<link[^>]+href=["\']/assets/css/tower-editorial\.css\?v=[^"\']+["\'][^>]*>'
    if "tower-editorial.css" in text:
        return re.sub(pattern, CSS, text, count=1)
    theme = re.search(r'<link[^>]+href=["\']/assets/css/site-theme\.css[^>]*>', text)
    if theme:
        return text[:theme.start()] + CSS + text[theme.start():]
    return text.replace("</head>", CSS + "</head>", 1)


def inject(project: dict, tower: str) -> None:
    path = ROOT / "mat-bang-smart-city" / project["slug"] / tower / "index.html"
    if not path.is_file():
        raise FileNotFoundError(path)
    text = path.read_text(encoding="utf-8")
    text = re.sub(re.escape(START) + r".*?" + re.escape(END), "", text, flags=re.S)
    display = tower_display(project, tower)
    summary = tower_summary(text, display, project["name"])
    text = ensure_css(text)
    block = editorial_block(project, tower, summary)
    marker = "<!-- TOWER_FLOORPLAN_INTENT_END -->"
    if marker in text:
        text = text.replace(marker, marker + block, 1)
    else:
        text = text.replace("</main>", block + "</main>", 1)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    count = 0
    for project in PROJECTS:
        for tower in project["towers"]:
            inject(project, tower)
            count += 1
    print(f"rich editorial tower content generated: {count} tower pages")


if __name__ == "__main__":
    main()
