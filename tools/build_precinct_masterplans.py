#!/usr/bin/env python3
from __future__ import annotations

from html import escape
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://timmuasmartcity.com"

PROJECTS = [
    {
        "slug": "sapphire",
        "name": "The Sapphire 1–4",
        "lead": "Bản đọc cấp phân khu cho 4 cụm Sapphire, giúp khoanh đúng cụm và đúng tòa trước khi mở sơ đồ tầng chi tiết.",
        "image": "/images/official/sapphire/sapphire-tong-the-thuc-te.webp",
        "image_label": "Toàn cảnh thực tế The Sapphire 1–4. Ảnh dùng để nhận diện cụm; sơ đồ kỹ thuật từng tòa nằm ở các liên kết bên dưới.",
        "facts": ["4 cụm", "15 tòa", "Z / U", "S1–S4"],
        "towers": ["s1-01","s1-02","s1-03","s1-05","s1-06","s2-01","s2-02","s2-03","s2-05","s3-01","s3-02","s3-03","s4-01","s4-02","s4-03"],
        "cards": [
            ("Sapphire 1", "5 tòa. S1.01, S1.02, S1.05, S1.06 dùng layout chữ Z; S1.03 là chữ U."),
            ("Sapphire 2", "4 tòa. S2.01–S2.02 là chữ U; S2.03–S2.05 là chữ Z."),
            ("Sapphire 3 & 4", "Sapphire 3 có 3 tòa chữ Z. Với Sapphire 4, mở trực tiếp hồ sơ từng tòa để đọc đúng sơ đồ gốc và tránh trộn nhãn layout giữa các phiên bản tài liệu."),
        ],
        "analysis": [
            ("Chọn cụm trước khi chọn mã căn", "Sapphire trải rộng nhiều cụm, vì vậy cùng một loại căn nhưng bối cảnh đường, công viên và tiện ích quanh tòa có thể khác nhau."),
            ("Không suy hướng chỉ từ tên trục", "Hướng căn cần được đọc trên đúng sơ đồ có ký hiệu phương hướng hoặc đối chiếu thực địa; trang này không tự gán hướng."),
        ],
    },
    {
        "slug": "sakura",
        "name": "The Sakura",
        "lead": "Hồ sơ tổng thể cho SA1, SA2, SA3 và SA5, đặt sơ đồ tòa trong đúng bối cảnh phân khu trước khi so căn.",
        "image": "/images/official/sakura/sakura-sa1-thuc-te.webp",
        "image_label": "Ảnh thực tế đại diện The Sakura. Các mặt bằng kỹ thuật SA1, SA2, SA3, SA5 được mở riêng ở thanh chọn tòa.",
        "facts": ["4 tòa", "SA1–SA5", "37–39 tầng", "Z / U"],
        "towers": ["sa1","sa2","sa3","sa5"],
        "cards": [
            ("SA1 & SA2", "Hai tòa nhóm layout chữ Z; hồ sơ từng tòa cho phép soi lõi thang và trục căn ở kích thước lớn."),
            ("SA3 & SA5", "Nhóm layout chữ U theo hệ mã thương mại hiện dùng trên website; nên xem sơ đồ tòa trước khi kết luận view."),
            ("Đọc cảnh quan Nhật Bản như một lớp riêng", "Tiện ích và khoảng xanh của Sakura là bối cảnh để đánh giá vị trí tòa; không thay thế mặt bằng tầng."),
        ],
        "analysis": [
            ("Ưu tiên đúng mã tòa", "Một số hồ sơ pháp lý cũ có thể dùng mã khối kỹ thuật khác tên thương mại. Website thống nhất SA1, SA2, SA3, SA5 để người dùng không bị lẫn."),
            ("Tách vị trí tòa và layout căn", "Mặt bằng phân khu trả lời tòa nằm ở đâu; mặt bằng tầng trả lời căn nào nằm trên lõi tòa."),
        ],
    },
    {
        "slug": "miami",
        "name": "The Miami",
        "lead": "Mặt bằng phân khu 5 tòa GS1, GS2, GS3, GS5, GS6 với lớp đọc rõ layout U/Z và cụm tiện ích nội khu.",
        "image": "/images/official/miami/miami-flycam-gs3.webp",
        "image_label": "Flycam thực tế The Miami. Dùng để nhận diện quan hệ giữa các tòa và không gian nội khu; sơ đồ kỹ thuật nằm ở từng tòa.",
        "facts": ["≈3,3 ha", "5 tòa", "38 tầng", "1 U + 4 Z"],
        "towers": ["gs1","gs2","gs3","gs5","gs6"],
        "cards": [
            ("GS1", "Tòa duy nhất của The Miami sử dụng layout chữ U; mật độ và cách bố trí hành lang khác nhóm chữ Z."),
            ("GS2 · GS3 · GS5 · GS6", "Bốn tòa sử dụng layout chữ Z. Nên mở từng mặt bằng để so vị trí lõi thang và các trục góc."),
            ("Lõi tiện ích giữa phân khu", "Bể bơi và sân thể thao là lớp cảnh quan quan trọng khi so các mặt tòa quay vào trong hoặc ra ngoài phân khu."),
        ],
        "analysis": [
            ("U và Z tạo trải nghiệm khác nhau", "Không nên chỉ so diện tích căn. Hình khối tòa ảnh hưởng khoảng cách hành lang, số trục góc và cách các căn mở tầm nhìn."),
            ("So mặt bằng trước khi lọc tin", "Sau khi chốt GS1 hay nhóm GS2/3/5/6, chuyển sang quỹ căn giao dịch sẽ nhanh và ít nhầm hơn."),
        ],
    },
    {
        "slug": "tonkin",
        "name": "The Tonkin",
        "lead": "Hồ sơ tổng thể 2 tòa TK1, TK2: ít tòa, layout chữ Z và mật độ 16 căn/sàn nên có thể đọc rất sâu theo từng trục.",
        "image": "/images/official/tonkin/tonkin-tong-mat-bang.webp",
        "image_label": "Mặt bằng tổng thể The Tonkin. Bấm ảnh để mở bản lớn, sau đó đi tiếp tới TK1 hoặc TK2.",
        "facts": ["2 tòa", "TK1 · TK2", "chữ Z", "16 căn/sàn"],
        "towers": ["tk1","tk2"],
        "cards": [
            ("TK1", "Layout chữ Z, 16 căn/sàn. Mở mặt bằng TK1 để đọc từng trục và vị trí lõi thang."),
            ("TK2", "Cùng quy mô phân khu thấp mật độ, nhưng phải đọc trên sơ đồ TK2 riêng thay vì áp trục TK1 sang TK2."),
            ("Phân khu gọn", "Chỉ 2 tòa giúp việc so vị trí, khoảng cách tiện ích và các trục căn trực quan hơn các cụm lớn."),
        ],
        "analysis": [
            ("Đừng dùng một sơ đồ cho cả hai tòa", "Hai tòa cùng ngôn ngữ layout không có nghĩa mã căn và vị trí trục giống nhau."),
            ("Mật độ là dữ kiện, view là thực địa", "16 căn/sàn giúp hiểu mật độ; hướng/view vẫn cần đối chiếu ký hiệu trên ảnh và vị trí thật."),
        ],
    },
    {
        "slug": "imperia",
        "name": "Imperia Smart City",
        "lead": "Lớp mặt bằng phân khu cho I1–I5, tách rõ việc chọn cụm tòa với việc soi trục căn trên sơ đồ tầng.",
        "image": "/images/official/imperia/imperia-toan-canh-thuc-te-ban-ngay.webp",
        "image_label": "Toàn cảnh thực tế Imperia Smart City. Hệ thống dùng 5 mã I1, I2, I3, I4, I5 nhất quán với hồ sơ mặt bằng từng tòa.",
        "facts": ["5 tòa", "I1–I5", "38–39 tầng", "Studio–3PN"],
        "towers": ["i1","i2","i3","i4","i5"],
        "cards": [
            ("I1", "Mở riêng mặt bằng I1 để đọc hình khối tòa, lõi thang và các trục căn thay vì suy từ ảnh tổng thể."),
            ("I2 · I3 · I4 · I5", "Bốn hồ sơ tòa còn lại được tách riêng để so đúng mã căn, đặc biệt khi tra một căn cụ thể."),
            ("Cụm 5 tòa", "Ảnh phân khu giúp nhìn quan hệ tòa – cảnh quan; sơ đồ tầng mới là nguồn để xác định trục căn."),
        ],
        "analysis": [
            ("Tách 2 câu hỏi", "Mặt bằng phân khu trả lời “nên chọn tòa nào”; mặt bằng tòa trả lời “nên chọn trục nào”."),
            ("Không gán hướng khi ảnh không có la bàn", "Nếu sơ đồ gốc không thể hiện Bắc/Nam rõ ràng, website giữ mô tả trung lập và yêu cầu đối chiếu thêm."),
        ],
    },
    {
        "slug": "canopy",
        "name": "The Canopy Residences",
        "lead": "Mặt bằng tổng thể 3 tòa TC1, TC2, TC3 trên quỹ đất 13.136 m², nối trực tiếp tới hồ sơ kỹ thuật từng tòa.",
        "image": "/images/official/canopy/canopy-tong-mat-bang.webp",
        "image_label": "Mặt bằng tổng thể The Canopy Residences. Bấm ảnh để mở bản lớn và đối chiếu vị trí TC1, TC2, TC3.",
        "facts": ["13.136 m²", "3 tòa", "TC1–TC3", "7 nhóm căn"],
        "towers": ["tc1","tc2","tc3"],
        "cards": [
            ("TC1 · The Canopy Vista", "Tòa TC1 có hồ sơ mặt bằng riêng để kiểm tra lõi thang, trục góc và bố trí căn."),
            ("TC2 · The Canopy Summit", "Tách riêng sơ đồ TC2 để tránh áp mã căn từ tòa khác trong cùng phân khu."),
            ("TC3 · The Canopy Harmony", "Đi từ tổng thể TC1–TC3 xuống mặt bằng TC3 trước khi so tin mua bán/cho thuê."),
        ],
        "analysis": [
            ("Ba tòa, một mặt bằng tổng", "Đây là trường hợp phù hợp nhất để người xem dùng sơ đồ phân khu trước rồi mới mở từng tower page."),
            ("Loại căn đa dạng", "Studio, 1PN, 1PN+1, 2PN, 2PN+1, 3PN, 3PN+1 khiến việc đọc đúng trục quan trọng hơn chỉ nhìn số phòng ngủ."),
        ],
    },
    {
        "slug": "sola-park",
        "name": "The Sola Park",
        "lead": "Hồ sơ tổng thể dùng hệ mã G1, G2, G3, G5, G6 đang được website chuẩn hóa, tránh trộn mã từ tài liệu cũ.",
        "image": "/images/official/sola-park/sola-park-mat-bang-tong-the.webp",
        "image_label": "Mặt bằng tổng thể The Sola Park với cụm tòa đang được website chuẩn hóa theo G1, G2, G3, G5, G6.",
        "facts": ["5 tòa", "G1–G6", "≈2,1 ha", "Studio–3PN"],
        "towers": ["g1","g2","g3","g5","g6"],
        "cards": [
            ("G1 · G2 · G3", "Ba tòa đầu có hồ sơ kỹ thuật riêng. Dùng sơ đồ tổng để khoanh vị trí rồi mới đọc trục căn."),
            ("G5 · G6", "Hai tòa còn lại được giữ đúng mã G5, G6 theo cấu trúc mặt bằng hiện tại của website."),
            ("Không trộn hệ mã", "Một số tài liệu trên thị trường từng dùng cách gọi khác. Trang này chỉ dùng G1, G2, G3, G5, G6 để giữ dữ liệu nhất quán."),
        ],
        "analysis": [
            ("Kiểm tra mã trước khi tìm căn", "Với dự án có nhiều phiên bản tài liệu, mã tòa sai sẽ kéo theo sai luôn mặt bằng và mã căn."),
            ("Ảnh tổng thể là lớp định vị", "Sau khi định vị được G1/G2/G3/G5/G6, mở ảnh HD từng tòa để đọc lõi thang và trục."),
        ],
    },
    {
        "slug": "victoria",
        "name": "The Victoria",
        "lead": "Bản đọc phân khu V1, V2, V3: ba tòa 38 tầng, giúp người mua chuyển từ ảnh tổng thể sang đúng mặt bằng tòa.",
        "image": "/images/official/victoria/victoria-cat-noc-toan-canh-2026.webp",
        "image_label": "Toàn cảnh The Victoria. Đây là ảnh bối cảnh phân khu; mặt bằng kỹ thuật V1, V2, V3 nằm ở các liên kết bên dưới.",
        "facts": ["3 tòa", "V1 · V2 · V3", "38 tầng", "28,1–75 m²"],
        "towers": ["v1","v2","v3"],
        "cards": [
            ("V1", "Mở mặt bằng V1 riêng để đọc trục căn và lõi giao thông."),
            ("V2", "So V2 với V1/V3 ở cấp phân khu trước, sau đó mới đối chiếu diện tích và mã căn."),
            ("V3", "Sơ đồ V3 là lớp kỹ thuật cuối cùng trước khi chuyển sang căn đang giao dịch."),
        ],
        "analysis": [
            ("Ba tòa cần so theo cùng một khung", "Dùng cùng tiêu chí: vị trí trong phân khu, layout tầng, trục góc, rồi mới tới giá."),
            ("Không suy view từ ảnh phối cảnh", "View cần đối chiếu sơ đồ có định hướng và hiện trạng; ảnh toàn cảnh chỉ hỗ trợ nhận diện."),
        ],
    },
    {
        "slug": "masteri-west-heights",
        "name": "Masteri West Heights",
        "lead": "Mặt bằng tổng thể West A, West B, West C, West D, đặt hệ tiện ích trung tâm và từng nhóm mặt bằng tầng trong cùng một luồng tra cứu.",
        "image": "/images/official/masteri-west-heights/masteri-west-heights-mat-bang-tong-the.webp",
        "image_label": "Mặt bằng tổng thể Masteri West Heights. Bấm ảnh để mở bản lớn, sau đó chọn West A/B/C/D.",
        "facts": ["4 tòa", "West A–D", "nhiều nhóm tầng", "tiện ích lõi"],
        "towers": ["west-a","west-b","west-c","west-d"],
        "cards": [
            ("West A & West B", "Tài liệu dự án nhóm mặt bằng tầng West A–B; website vẫn tách 2 tower page để tra cứu rõ từng tòa."),
            ("West C", "Có nhóm mặt bằng tầng riêng, phù hợp so cấu trúc theo các khoảng tầng thay vì dùng một ảnh duy nhất."),
            ("West D", "Được tách thành nhóm mặt bằng riêng trong tài liệu dự án; mở hồ sơ West D để xem ảnh HD."),
        ],
        "analysis": [
            ("Đọc cả tổng thể và nhóm tầng", "Masteri West Heights có nhiều mốc tầng khác nhau, nên chọn đúng tòa chưa đủ; cần chọn đúng nhóm tầng."),
            ("Tiện ích lõi là lớp tham chiếu", "Sơ đồ tổng thể giúp hiểu quan hệ 4 tòa với cảnh quan/tiện ích; mặt bằng tầng dùng để chốt trục căn."),
        ],
    },
    {
        "slug": "lumiere-evergreen",
        "name": "LUMIÈRE Evergreen",
        "lead": "Hồ sơ phân khu dùng hệ mã A1, A2, A3 để đồng nhất với bộ mặt bằng kỹ thuật và tránh lệch giữa tên thương mại, tên khối và mã tòa.",
        "image": "/images/official/floorplans-hd/lumiere-evergreen-a1.webp",
        "image_label": "Mặt bằng kỹ thuật A1 dùng làm ảnh đại diện vì kho ảnh hiện tại chưa có một bản tổng mặt bằng đủ tin cậy. A2 và A3 có hồ sơ riêng bên dưới.",
        "facts": ["3 tòa", "A1 · A2 · A3", "39 tầng", "mặt bằng HD"],
        "towers": ["a1","a2","a3"],
        "cards": [
            ("A1", "Mặt bằng A1 được dùng làm điểm vào kỹ thuật; không dùng nó để suy vị trí của A2/A3."),
            ("A2", "Mở riêng A2 để đọc đúng lõi thang và trục căn theo tòa."),
            ("A3", "Hồ sơ A3 hoàn tất lớp tra cứu 3 tòa trước khi sang danh sách giao dịch."),
        ],
        "analysis": [
            ("Ưu tiên mã tòa nhất quán", "Tên thương mại và mã khối trong tài liệu khác nhau có thể gây nhầm. Hệ mặt bằng của website dùng A1, A2, A3 xuyên suốt."),
            ("Không giả tạo tổng mặt bằng", "Khi chưa có ảnh tổng thể đủ tin cậy trong kho, trang ghi rõ ảnh đại diện là A1 thay vì gắn nhãn sai."),
        ],
    },
]

def label_tower(slug: str) -> str:
    if slug.startswith("s") and "-" in slug:
        a, b = slug.split("-", 1)
        return f"{a.upper()}.{b}"
    return slug.replace("-", " ").upper()

def page(project: dict) -> str:
    slug = project["slug"]
    name = project["name"]
    canonical = f"{SITE}/mat-bang-smart-city/{slug}/tong-the/"
    tower_links = "".join(
        f'<a class="precinct-tower" href="/mat-bang-smart-city/{slug}/{t}/">{escape(label_tower(t))}</a>'
        for t in project["towers"]
    )
    cards = "".join(
        f'<article class="precinct-card"><h3>{escape(title)}</h3><p>{escape(text)}</p></article>'
        for title, text in project["cards"]
    )
    analysis = "".join(
        f'<article><h3>{escape(title)}</h3><p>{escape(text)}</p></article>'
        for title, text in project["analysis"]
    )
    facts = "".join(
        f'<div><strong>{escape(fact)}</strong><span>{label}</span></div>'
        for fact, label in zip(project["facts"], ["quy mô", "hệ tòa", "cấu trúc", "điểm đọc"])
    )
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Trang chủ", "item": SITE + "/"},
                    {"@type": "ListItem", "position": 2, "name": "Mặt bằng Smart City", "item": SITE + "/mat-bang-smart-city/"},
                    {"@type": "ListItem", "position": 3, "name": name, "item": SITE + f"/mat-bang-smart-city/{slug}/"},
                    {"@type": "ListItem", "position": 4, "name": "Mặt bằng tổng thể", "item": canonical},
                ],
            },
            {
                "@type": "WebPage",
                "name": f"Mặt bằng tổng thể {name}",
                "description": project["lead"],
                "url": canonical,
                "inLanguage": "vi-VN",
                "isPartOf": {"@type": "WebSite", "name": "Sàn Smart City", "url": SITE + "/"},
            },
        ],
    }
    title = f"Mặt bằng tổng thể {name} | Sơ đồ phân khu & vị trí tòa"
    desc = project["lead"] + " Xem ảnh lớn, chọn đúng tòa và đi thẳng tới mặt bằng tầng."
    return f'''<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{escape(title)}</title><meta name="description" content="{escape(desc)}"><meta name="robots" content="index,follow,max-image-preview:large"><link rel="canonical" href="{canonical}">
<meta property="og:type" content="article"><meta property="og:site_name" content="Sàn Smart City"><meta property="og:title" content="{escape(title)}"><meta property="og:description" content="{escape(desc)}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{SITE}{project["image"]}"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png"><link rel="stylesheet" href="/assets/css/site.css?v=20260901-seo2"><link rel="stylesheet" href="/assets/css/precinct-masterplan.css?v=20260910-1"><script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, separators=(",", ":"))}</script></head>
<body class="precinct-page"><header class="site-header"><div class="container nav"><a class="brand" href="/"><span class="brand-mark" aria-hidden="true">SC</span><span>SÀN SMART CITY</span></a><nav class="nav-links" aria-label="Điều hướng chính"><a href="/tong-quan-smart-city/">Tổng quan</a><a href="/mat-bang-smart-city/">Mặt bằng</a><a href="/phan-khu-smart-city/">Phân khu</a><a href="/giao-dich-smart-city/">Giao dịch</a></nav></div></header><main>
<div class="precinct-wrap precinct-breadcrumb"><a href="/">Trang chủ</a><span>›</span><a href="/mat-bang-smart-city/">Mặt bằng</a><span>›</span><a href="/mat-bang-smart-city/phan-khu/">Phân khu</a><span>›</span><strong>{escape(name)}</strong></div>
<section class="precinct-hero"><div class="precinct-wrap precinct-hero__grid"><div><p class="precinct-kicker">Mặt bằng phân khu chuyên sâu</p><h1>Mặt bằng tổng thể {escape(name)}</h1><p class="precinct-lead">{escape(project["lead"])}</p><div class="precinct-actions"><a class="primary" href="#so-do">Xem sơ đồ phân khu</a><a class="secondary" href="/mat-bang-smart-city/{slug}/">Xem toàn bộ mặt bằng tòa</a></div></div><div class="precinct-quick">{facts}</div></div></section>
<section class="precinct-section alt" id="so-do"><div class="precinct-wrap"><div class="precinct-head"><div><p class="precinct-kicker">Lớp 1 · định vị</p><h2>Nhìn phân khu trước, soi trục căn sau</h2></div><p>Ảnh lớn giúp nhận diện bối cảnh. Trên mobile có thể chạm ảnh, cuộn ngang khi cần hoặc mở ảnh gốc để phóng to.</p></div><figure class="precinct-plan"><a class="precinct-plan__media" href="{project["image"]}" target="_blank" rel="noopener"><img src="{project["image"]}" alt="Mặt bằng và bối cảnh {escape(name)}" loading="eager" decoding="async"></a><figcaption>{escape(project["image_label"])}</figcaption></figure><div class="precinct-note">Nguyên tắc dữ liệu: chỉ gọi là “mặt bằng tổng thể” khi kho ảnh có sơ đồ tổng thể đủ rõ. Nếu chỉ có ảnh thực tế/ảnh đại diện, trang ghi đúng bản chất ảnh và dẫn người dùng xuống mặt bằng kỹ thuật từng tòa.</div><div class="precinct-towers">{tower_links}</div></div></section>
<section class="precinct-section"><div class="precinct-wrap"><div class="precinct-head"><div><p class="precinct-kicker">Lớp 2 · chọn tòa</p><h2>Cấu trúc cần biết trước khi mở mặt bằng tầng</h2></div><p>Mỗi card là một điểm kiểm tra để tránh nhầm tòa, nhầm layout hoặc áp mã căn của tòa này sang tòa khác.</p></div><div class="precinct-grid">{cards}</div></div></section>
<section class="precinct-section alt"><div class="precinct-wrap"><div class="precinct-head"><div><p class="precinct-kicker">Lớp 3 · đọc để giao dịch</p><h2>Cách dùng mặt bằng {escape(name)} khi chọn căn</h2></div><p>Website ưu tiên dữ liệu có thể kiểm chứng trên sơ đồ; hướng/view không được suy đoán khi ảnh gốc thiếu ký hiệu.</p></div><div class="precinct-analysis">{analysis}</div><div class="precinct-actions"><a class="primary" href="/phan-khu-smart-city/{slug}/">Xem hồ sơ phân khu</a><a class="secondary" href="/giao-dich-smart-city/">Xem căn đang giao dịch</a></div></div></section>
<section class="precinct-section"><div class="precinct-wrap"><div class="precinct-cta"><div><h2>Đã chọn được tòa?</h2><p>Mở mặt bằng HD của tòa ở trên, sau đó đối chiếu căn đang bán/cho thuê.</p></div><a href="/mat-bang-smart-city/{slug}/">Mở thư viện {escape(name)} →</a></div></div></section></main>
<footer class="site-footer"><div class="container footer-grid"><div><a class="brand" href="/"><span class="brand-mark" aria-hidden="true">SC</span><span>SÀN SMART CITY</span></a><p>Mua bán · Cho thuê · Mặt bằng Smart City.</p></div><nav class="footer-links"><a href="/mat-bang-smart-city/">Mặt bằng</a><a href="/mat-bang-smart-city/phan-khu/">Mặt bằng phân khu</a><a href="/giao-dich-smart-city/">Giao dịch</a></nav></div></footer><script src="/assets/js/site.js" defer></script></body></html>'''

def main() -> None:
    created = []
    for project in PROJECTS:
        target = ROOT / "mat-bang-smart-city" / project["slug"] / "tong-the" / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        html = page(project)
        target.write_text(html, encoding="utf-8")
        assert '<meta name="robots" content="index,follow,max-image-preview:large">' in html
        assert f'<link rel="canonical" href="{SITE}/mat-bang-smart-city/{project["slug"]}/tong-the/">' in html
        assert 'application/ld+json' in html and 'precinct-tower' in html
        created.append(str(target.relative_to(ROOT)))
    print(f"precinct masterplans generated: {len(created)} pages")
    for item in created:
        print(" -", item)

if __name__ == "__main__":
    main()
