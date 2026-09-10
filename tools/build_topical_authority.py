#!/usr/bin/env python3
"""Build evergreen topical-authority guides and contextual internal links.

Runs against the staged `_site` output. The pages target informational intent that
supports, rather than duplicates, marketplace inventory pages. Each guide has a
self-canonical, Article + Breadcrumb schema, contextual links into the transaction
hubs, and is appended to sitemap-pages.xml.
"""
from __future__ import annotations

from pathlib import Path
from html import escape
import json
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SITE_ROOT = ROOT / "_site"
SITE = "https://timmuasmartcity.com"
NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
PUBLISHED = "2026-09-10"

GUIDES = [
    {
        "slug": "thue-can-ho-vinhomes-smart-city-kinh-nghiem",
        "title": "Kinh nghiệm thuê căn hộ Vinhomes Smart City: lọc đúng tòa, đúng giá, đúng hợp đồng",
        "description": "Hướng dẫn thuê căn hộ Vinhomes Smart City theo ngân sách, phân khu, tòa, loại căn, nội thất, chi phí phát sinh và các điểm cần kiểm tra trước khi đặt cọc.",
        "eyebrow": "Cẩm nang người thuê",
        "intro": "Smart City có nguồn cung thuê lớn nhưng mức giá, nội thất và điều kiện hợp đồng thay đổi mạnh giữa từng tòa. Cách tìm hiệu quả nhất là thu hẹp nhu cầu trước khi gọi từng tin, rồi kiểm tra lại căn thực tế và điều khoản cọc.",
        "sections": [
            ("1. Chốt 4 biến số trước khi tìm căn", "Hãy xác định ngân sách tối đa, ngày vào ở, số người ở và loại căn cần thiết. Sau đó mới chọn 2–3 phân khu hoặc tòa ưu tiên. Làm theo thứ tự này giúp tránh mất thời gian xem những căn đẹp nhưng không phù hợp hành trình sống hoặc vượt ngân sách."),
            ("2. Đừng so giá thuê chỉ bằng số phòng ngủ", "Hai căn cùng là 2PN có thể khác diện tích, số WC, vị trí trên mặt sàn, mức độ hoàn thiện và chất lượng nội thất. Giá thuê vì vậy phải đọc cùng tòa, diện tích, nội thất, tầng và thời điểm có thể bàn giao. Nên mở mặt bằng tòa để hiểu đúng layout trước khi đi xem."),
            ("3. Tổng chi phí tháng quan trọng hơn giá niêm yết", "Ngoài tiền thuê, cần hỏi rõ phí quản lý, gửi xe, internet, điện nước, phí tiện ích nếu có và trách nhiệm sửa chữa thiết bị. Một căn có giá thuê thấp hơn đôi khi lại có tổng chi phí sử dụng cao hơn nếu thiếu nội thất hoặc phát sinh nhiều khoản bên ngoài."),
            ("4. Checklist trước khi đặt cọc", "Xác nhận đúng căn và người có quyền cho thuê; kiểm tra nội thất bàn giao; ghi rõ tiền cọc, thời hạn hợp đồng, thời điểm vào ở, điều kiện hoàn cọc và thời gian báo trước khi chấm dứt. Nếu giao dịch từ xa, cần có đủ hình ảnh hoặc video cập nhật và thông tin nhận diện căn trước khi chuyển tiền."),
            ("5. Cách dùng quỹ căn trên marketplace", "Bắt đầu ở trang cho thuê, lọc theo phân khu, tòa, loại căn và giá. Khi mở tin chi tiết, đối chiếu ảnh, mô tả, ngày đăng và thông tin liên hệ. Tin rao phản ánh mức chào tại thời điểm đăng; trạng thái căn vẫn cần được người thuê xác nhận lại trực tiếp."),
        ],
        "links": [("Xem quỹ căn cho thuê", "/cho-thue-smart-city/"), ("Xem mặt bằng từng tòa", "/mat-bang-smart-city/"), ("So sánh giá Smart City", "/gia-smart-city/")],
    },
    {
        "slug": "cho-thue-can-ho-vinhomes-smart-city-chu-nha",
        "title": "Chủ nhà cho thuê căn hộ Vinhomes Smart City: cách đăng tin dễ có khách và hạn chế tin trôi",
        "description": "Cẩm nang dành cho chủ nhà Vinhomes Smart City: chuẩn bị ảnh, giá, mô tả, thông tin căn và cách đăng tin để khách lọc được đúng nhu cầu.",
        "eyebrow": "Cẩm nang chủ nhà",
        "intro": "Một tin cho thuê tốt không cần viết dài, nhưng phải đủ dữ liệu để khách quyết định có nên liên hệ hay không. Với marketplace, cấu trúc thông tin quan trọng hơn các câu quảng cáo chung chung.",
        "sections": [
            ("1. Ảnh đúng căn là tín hiệu mạnh nhất", "Nên có ảnh phòng khách, bếp, phòng ngủ, WC, ban công hoặc view và các thiết bị chính. Ảnh sáng, thẳng khung và đúng hiện trạng giúp khách tự sàng lọc trước khi nhắn. Không nên dùng ảnh căn khác chỉ để minh họa vì làm giảm độ tin cậy của tin."),
            ("2. Giá phải đi cùng điều kiện thuê", "Ngoài giá thuê tháng, nên nói rõ mức cọc, thời hạn hợp đồng mong muốn, thời điểm nhận nhà và nội thất để lại. Nếu có điều kiện đặc biệt như không nuôi thú cưng hoặc chỉ cho thuê dài hạn, nên ghi ngay trong mô tả để giảm trao đổi không phù hợp."),
            ("3. Tiêu đề nên chứa dữ liệu khách đang tìm", "Một tiêu đề tốt có thể gồm loại căn, tòa hoặc phân khu và điểm khác biệt quan trọng. Ví dụ cấu trúc: 1PN+1 · tòa · full nội thất · vào ở ngay. Không cần nhồi nhiều tính từ; khách thường lọc theo dữ liệu cụ thể hơn là khẩu hiệu."),
            ("4. Cập nhật trạng thái để giữ chất lượng marketplace", "Khi căn đã cho thuê, nên gỡ hoặc cập nhật trạng thái càng sớm càng tốt. Một sàn có nhiều tin hết hàng làm khách mất niềm tin và cũng khiến dữ liệu thị trường kém hữu ích. Tin còn hàng và ngày cập nhật rõ ràng có giá trị hơn số lượng tin lớn nhưng cũ."),
            ("5. Đăng tin để tạo URL riêng cho căn", "Tin được duyệt có trang chi tiết riêng với tiêu đề, mô tả, ảnh và thông tin liên hệ. Điều này giúp khách có thể chia sẻ đúng căn, đồng thời tạo cấu trúc nội dung rõ ràng hơn so với một bài đăng ngắn trôi nhanh trên mạng xã hội."),
        ],
        "links": [("Đăng tin miễn phí", "/dang-tin-smart-city/"), ("Xem quỹ căn cho thuê", "/cho-thue-smart-city/"), ("Mở cổng giao dịch", "/giao-dich-smart-city/")],
    },
    {
        "slug": "cach-doc-mat-bang-vinhomes-smart-city",
        "title": "Cách đọc mặt bằng Vinhomes Smart City: mã căn, lõi thang, vị trí và công năng",
        "description": "Hướng dẫn đọc mặt bằng Vinhomes Smart City để hiểu vị trí căn trên tầng, lõi thang, hành lang, loại căn, hướng tiếp cận và các yếu tố cần kiểm tra trước khi mua hoặc thuê.",
        "eyebrow": "Cẩm nang mặt bằng",
        "intro": "Mặt bằng không chỉ để xem căn có mấy phòng. Nó giúp giải thích nhiều khác biệt về công năng, độ riêng tư, khoảng cách tới thang máy và trải nghiệm sử dụng thực tế giữa các căn cùng diện tích.",
        "sections": [
            ("1. Bắt đầu từ đúng tòa và đúng nhóm tầng", "Một tòa có thể có nhiều mặt bằng tầng điển hình hoặc thay đổi ở một số tầng đặc biệt. Trước khi suy luận mã căn, cần chắc chắn bản vẽ đang xem đúng tòa và đúng nhóm tầng. Đây là bước quan trọng nhất để tránh nhầm vị trí căn."),
            ("2. Xác định lõi thang và hành lang trước", "Hãy tìm thang máy, thang bộ, phòng kỹ thuật và hướng hành lang. Sau đó mới xác định vị trí căn. Căn gần thang có lợi về di chuyển nhưng có thể khác về mức độ riêng tư; căn cuối hành lang thường yên hơn nhưng quãng đi bộ dài hơn."),
            ("3. Đọc layout thay vì chỉ đọc nhãn 1PN hoặc 2PN", "Cùng nhãn loại căn nhưng cách bố trí phòng khách, logia, bếp, số WC và không gian +1 có thể khác. Hãy nhìn lối vào, chiều dài hành lang trong căn, vị trí cửa phòng ngủ và khả năng đặt đồ nội thất thực tế."),
            ("4. Hướng và view cần đối chiếu với bản đồ tổng thể", "Mặt bằng tầng cho biết căn nằm ở cạnh nào của tòa, nhưng để kết luận view nội khu, đường lớn hay công trình lân cận cần đối chiếu thêm vị trí tòa trên tổng mặt bằng. Không nên suy đoán hướng chỉ từ số căn nếu chưa xác minh bản vẽ."),
            ("5. Dùng mặt bằng để so hai căn cùng giá", "Khi hai căn có tổng giá gần nhau, mặt bằng giúp so thêm vị trí trên tầng, số mặt thoáng, khoảng cách tới thang, hình dạng phòng và mức độ tối ưu diện tích. Đây là lớp thông tin thường giải thích vì sao hai căn nhìn giống nhau trên tin rao nhưng trải nghiệm thực tế khác nhau."),
        ],
        "links": [("Mở kho mặt bằng", "/mat-bang-smart-city/"), ("Xem các phân khu", "/phan-khu-smart-city/"), ("Xem căn đang bán", "/mua-ban-smart-city/")],
    },
    {
        "slug": "kiem-tra-phap-ly-can-ho-vinhomes-smart-city-truoc-dat-coc",
        "title": "Kiểm tra pháp lý căn hộ Vinhomes Smart City trước khi đặt cọc: checklist cho người mua",
        "description": "Checklist kiểm tra chủ thể giao dịch, giấy tờ căn hộ, thế chấp, công nợ, điều khoản cọc và bàn giao khi mua căn hộ Vinhomes Smart City chuyển nhượng.",
        "eyebrow": "Cẩm nang giao dịch",
        "intro": "Tin rao và giá chào chỉ là bước đầu. Trước khi đặt cọc, người mua cần tách việc đánh giá căn hộ khỏi việc kiểm tra người bán, hồ sơ và các nghĩa vụ gắn với căn. Những nội dung dưới đây là checklist thực hành, không thay thế tư vấn pháp lý cho trường hợp cụ thể.",
        "sections": [
            ("1. Xác định đúng người có quyền giao dịch", "Đối chiếu người ký với hồ sơ hiện có của căn. Nếu giao dịch thông qua người được ủy quyền, cần kiểm tra phạm vi và thời hạn ủy quyền có phù hợp với việc nhận cọc, ký hồ sơ và nhận tiền hay không."),
            ("2. Kiểm tra loại giấy tờ hiện có của căn", "Mỗi căn có thể ở trạng thái hồ sơ khác nhau theo thời điểm. Người mua nên biết mình đang giao dịch dựa trên giấy tờ nào, các bước tiếp theo cần thực hiện và điều kiện để chuyển nhượng. Không nên dùng một checklist giấy tờ duy nhất cho mọi căn."),
            ("3. Làm rõ thế chấp, công nợ và nghĩa vụ tài chính", "Nếu căn có liên quan tới khoản vay hoặc nghĩa vụ chưa hoàn tất, cần ghi rõ cách xử lý, mốc thanh toán và trách nhiệm của từng bên. Các khoản phí quản lý, điện nước hoặc nghĩa vụ khác cũng nên được xác nhận trước ngày bàn giao."),
            ("4. Điều khoản cọc phải gắn với điều kiện kiểm tra", "Biên bản cọc nên nêu rõ căn hộ, giá, số tiền cọc, lịch thanh toán, thời hạn ký hồ sơ, điều kiện bàn giao và cách xử lý nếu một bên không đáp ứng cam kết. Những điều kiện quan trọng như cung cấp hồ sơ hoặc giải chấp cần được viết thành điều khoản cụ thể thay vì chỉ thỏa thuận miệng."),
            ("5. Đối chiếu hiện trạng căn khi bàn giao", "Ngoài hồ sơ, cần ghi nhận nội thất để lại, thiết bị, thẻ cư dân, chìa khóa và tình trạng căn. Hình ảnh hoặc biên bản bàn giao giúp giảm tranh chấp về những hạng mục đã có trước thời điểm nhận nhà."),
        ],
        "links": [("Xem quỹ căn mua bán", "/mua-ban-smart-city/"), ("Cách so giá căn hộ", "/gia-smart-city/"), ("Mở cổng giao dịch", "/giao-dich-smart-city/")],
    },
]


def safe_json(data: object) -> str:
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def render_guide(g: dict) -> str:
    rel = f"/blog/{g['slug']}/"
    canonical = SITE + rel
    article_schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Article",
                "@id": canonical + "#article",
                "headline": g["title"],
                "description": g["description"],
                "datePublished": PUBLISHED,
                "dateModified": PUBLISHED,
                "inLanguage": "vi-VN",
                "mainEntityOfPage": canonical,
                "author": {"@type": "Organization", "name": "Sàn Smart City", "url": SITE + "/"},
                "publisher": {"@type": "Organization", "name": "Sàn Smart City", "url": SITE + "/"},
                "image": SITE + "/images/hero/hero-smart-city-desktop.webp",
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Trang chủ", "item": SITE + "/"},
                    {"@type": "ListItem", "position": 2, "name": "Cẩm nang", "item": SITE + "/cam-nang.html"},
                    {"@type": "ListItem", "position": 3, "name": g["title"], "item": canonical},
                ],
            },
        ],
    }
    sections = "".join(f"<section><h2>{escape(h)}</h2><p>{escape(p)}</p></section>" for h, p in g["sections"])
    links = "".join(f'<a href="{escape(href)}">{escape(label)} →</a>' for label, href in g["links"])
    return f'''<!doctype html><html lang="vi"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{escape(g['title'])} | Sàn Smart City</title>
<meta name="description" content="{escape(g['description'])}"><meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{canonical}"><meta property="og:type" content="article"><meta property="og:site_name" content="Sàn Smart City"><meta property="og:title" content="{escape(g['title'])}"><meta property="og:description" content="{escape(g['description'])}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{SITE}/images/hero/hero-smart-city-desktop.webp"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{escape(g['title'])}"><meta name="twitter:description" content="{escape(g['description'])}">
<link rel="stylesheet" href="/assets/css/site.css?v=20260901-seo2"><link rel="stylesheet" href="/assets/css/site-theme.css?v=20260902-1">
<style>.seo-guide{{max-width:900px;margin:0 auto;padding:36px 20px 70px}}.seo-guide .crumbs{{font-size:13px;color:#68746f;margin-bottom:24px}}.seo-guide h1{{font-size:clamp(34px,6vw,58px);line-height:1.06;letter-spacing:-.035em;margin:10px 0 18px}}.seo-guide .lead{{font-size:19px;line-height:1.75;color:#3f4b47}}.seo-guide section{{padding:22px 0;border-top:1px solid #e2e8e5}}.seo-guide h2{{font-size:26px;margin:0 0 10px}}.seo-guide p{{line-height:1.8}}.seo-guide-links{{display:grid;gap:10px;margin-top:28px;padding:20px;border:1px solid #dfe7e3;border-radius:16px;background:#f8faf9}}.seo-guide-links a{{font-weight:700;text-decoration:none}}.seo-guide-note{{padding:14px 16px;background:#f4f8f6;border-radius:12px;margin:24px 0}}</style>
<script type="application/ld+json">{safe_json(article_schema)}</script></head><body>
<header class="site-header"><div class="container nav"><a class="brand" href="/"><span class="brand-mark">SC</span><span>SÀN SMART CITY</span></a><nav class="nav-links"><a href="/tong-quan-smart-city/">Tổng quan</a><a href="/mat-bang-smart-city/">Mặt bằng</a><a href="/mua-ban-smart-city/">Mua bán</a><a href="/cho-thue-smart-city/">Cho thuê</a><a href="/dang-tin-smart-city/">Đăng tin</a></nav></div></header>
<main class="seo-guide"><div class="crumbs"><a href="/">Trang chủ</a> / <a href="/cam-nang.html">Cẩm nang</a></div><p class="eyebrow">{escape(g['eyebrow'])}</p><h1>{escape(g['title'])}</h1><p class="lead">{escape(g['intro'])}</p><div class="seo-guide-note">Nội dung được biên soạn theo mục tiêu hỗ trợ người dùng ra quyết định và cần được đối chiếu lại với dữ liệu, hồ sơ hoặc tình trạng căn tại thời điểm giao dịch.</div>{sections}<div class="seo-guide-links"><strong>Đi tiếp theo nhu cầu</strong>{links}</div></main>
<footer class="site-footer"><div class="container footer-grid"><a class="brand" href="/"><span class="brand-mark">SC</span><span>SÀN SMART CITY</span></a><nav class="footer-links"><a href="/cam-nang.html">Cẩm nang</a><a href="/mua-ban-smart-city/">Mua bán</a><a href="/cho-thue-smart-city/">Cho thuê</a></nav></div></footer><script src="/assets/js/site.js" defer></script><script src="/assets/app-shell.js" defer></script></body></html>'''


def add_to_sitemap(urls: list[str]) -> None:
    path = SITE_ROOT / "sitemap-pages.xml"
    if not path.is_file():
        raise RuntimeError("sitemap-pages.xml missing before topical-authority pass")
    ET.register_namespace("", NS)
    tree = ET.parse(path)
    root = tree.getroot()
    existing = {n.text for n in root.findall(f"{{{NS}}}url/{{{NS}}}loc") if n.text}
    for url in urls:
        if url in existing:
            continue
        node = ET.SubElement(root, f"{{{NS}}}url")
        ET.SubElement(node, f"{{{NS}}}loc").text = url
        ET.SubElement(node, f"{{{NS}}}lastmod").text = PUBLISHED
    ET.indent(root, space="  ")
    path.write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode") + "\n", encoding="utf-8")


def inject_cluster_links() -> None:
    targets = {
        "cho-thue-smart-city/index.html": [GUIDES[0], GUIDES[1]],
        "mua-ban-smart-city/index.html": [GUIDES[3], GUIDES[2]],
        "mat-bang-smart-city/index.html": [GUIDES[2]],
        "gia-smart-city/index.html": [GUIDES[3], GUIDES[0]],
        "cam-nang.html": GUIDES,
    }
    for rel, guides in targets.items():
        path = SITE_ROOT / rel
        if not path.is_file():
            continue
        doc = BeautifulSoup(path.read_text(encoding="utf-8", errors="replace"), "html.parser")
        main = doc.find("main") or doc.body
        if main is None or doc.find(attrs={"data-topical-authority": "20260910"}):
            continue
        section = doc.new_tag("section")
        section["data-topical-authority"] = "20260910"
        section["class"] = ["section", "seo-authority-cluster"]
        wrap = doc.new_tag("div")
        wrap["class"] = ["container"]
        heading = doc.new_tag("h2")
        heading.string = "Cẩm nang chuyên sâu Smart City"
        wrap.append(heading)
        intro = doc.new_tag("p")
        intro.string = "Đọc thêm theo đúng bước ra quyết định để kết nối dữ liệu dự án, mặt bằng và giao dịch."
        wrap.append(intro)
        links = doc.new_tag("div")
        links["class"] = ["seo-authority-links"]
        for guide in guides:
            a = doc.new_tag("a", href=f"/blog/{guide['slug']}/")
            a.string = guide["title"]
            links.append(a)
        wrap.append(links)
        section.append(wrap)
        main.append(section)
        style = doc.new_tag("style")
        style.string = ".seo-authority-cluster{padding:34px 0}.seo-authority-links{display:grid;gap:10px;margin-top:14px}.seo-authority-links a{display:block;padding:14px 16px;border:1px solid #dfe7e3;border-radius:12px;text-decoration:none;font-weight:700}"
        doc.head.append(style)
        path.write_text(str(doc), encoding="utf-8")


def main() -> None:
    urls = []
    for guide in GUIDES:
        rel = f"/blog/{guide['slug']}/"
        target = SITE_ROOT / rel.strip("/") / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_guide(guide), encoding="utf-8")
        urls.append(SITE + rel)
    inject_cluster_links()
    add_to_sitemap(urls)
    print(f"SEO: generated {len(urls)} topical-authority guides and contextual cluster links")


if __name__ == "__main__":
    main()
