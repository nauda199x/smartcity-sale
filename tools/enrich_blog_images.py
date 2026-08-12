from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
BLOG = ROOT / "blog"

GENERIC_IMG = "https://smartcity.vinhomes.vn/wp-content/themes/vinhomes-smart-city/assets/images/homepage/home1/a2.png"
SAPPHIRE_IMG = "https://vinhomes.vn/sites/default/files/styles/images_525_x_295/public/2021-07/Hinh-anh-the-sapphire-vinhomes-smart-city.jpg?itok=T_nLf8w9"
SAKURA_IMG = "https://vinhomes.vn/sites/default/files/styles/images_560_x_315/public/2021-05/PC02.Topdown%20The%20Sakura%20-%20Final.jpg?itok=RBkxJLpO"
MASTERI_IMG = "https://masterisehomes.com/masteri-west-heights/themes/masterise/assets/images/home/about2_img.jpeg"

MEDIA = {
    "gia-ban-vinhomes-smart-city": (GENERIC_IMG, "Toàn cảnh Vinhomes Smart City phía Tây Hà Nội", "Toàn cảnh Vinhomes Smart City – nguồn hình ảnh: Vinhomes", "https://smartcity.vinhomes.vn/"),
    "kinh-nghiem-mua-can-ho-vinhomes-smart-city": (GENERIC_IMG, "Không gian đô thị Vinhomes Smart City", "Không gian Vinhomes Smart City – nguồn hình ảnh: Vinhomes", "https://smartcity.vinhomes.vn/"),
    "mua-can-ho-2pn-vinhomes-smart-city": (GENERIC_IMG, "Vinhomes Smart City với hệ tiện ích và các tòa căn hộ", "Vinhomes Smart City – nguồn hình ảnh: Vinhomes", "https://smartcity.vinhomes.vn/"),
    "so-sanh-phan-khu-vinhomes-smart-city": (GENERIC_IMG, "Toàn cảnh các phân khu tại Vinhomes Smart City", "Toàn cảnh Vinhomes Smart City – nguồn hình ảnh: Vinhomes", "https://smartcity.vinhomes.vn/"),
    "chi-phi-mua-can-ho-chuyen-nhuong-vinhomes-smart-city": (GENERIC_IMG, "Căn hộ và cảnh quan Vinhomes Smart City", "Vinhomes Smart City – nguồn hình ảnh: Vinhomes", "https://smartcity.vinhomes.vn/"),
    "sapphire-vinhomes-smart-city": (SAPPHIRE_IMG, "The Sapphire Vinhomes Smart City", "The Sapphire Vinhomes Smart City – nguồn hình ảnh: Vinhomes", "https://vinhomes.vn/vi/the-sapphire-vhsc"),
    "the-sakura-vinhomes-smart-city": (SAKURA_IMG, "Toàn cảnh The Sakura Vinhomes Smart City", "The Sakura Vinhomes Smart City – nguồn hình ảnh: Vinhomes", "https://vinhomes.vn/vi/the-sakura"),
    "masteri-west-heights-smart-city": (MASTERI_IMG, "Masteri West Heights tại Vinhomes Smart City", "Masteri West Heights – nguồn hình ảnh: Masterise Homes", "https://masterisehomes.com/masteri-west-heights/en"),
}

CSS = ".article figure.seo-media{margin:26px 0 30px}.article figure.seo-media img{display:block;width:100%;height:auto;aspect-ratio:16/9;object-fit:cover;border-radius:16px;background:#eef1f5}.article figure.seo-media figcaption{font-size:13px;line-height:1.5;color:#6b7280;margin-top:8px}.article figure.seo-media figcaption a{font-weight:600}"

for slug, (img, alt, caption, source) in MEDIA.items():
    path = BLOG / slug / "index.html"
    if not path.exists():
        print("skip missing", path)
        continue
    html = path.read_text(encoding="utf-8")

    # Idempotent: refresh existing injected block if script runs again.
    html = re.sub(r"<!-- SEO_MEDIA_START -->.*?<!-- SEO_MEDIA_END -->", "", html, flags=re.S)

    if CSS not in html:
        html = html.replace("</style>", CSS + "</style>", 1)

    if 'property="og:image"' not in html:
        html = html.replace("</head>", f'<meta property="og:image" content="{img}"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{img}"></head>', 1)

    figure = (
        '<!-- SEO_MEDIA_START -->'
        '<figure class="seo-media">'
        f'<img src="{img}" alt="{alt}" loading="eager" decoding="async" referrerpolicy="no-referrer">'
        f'<figcaption>{caption}. <a href="{source}" target="_blank" rel="noopener">Xem nguồn</a></figcaption>'
        '</figure>'
        '<!-- SEO_MEDIA_END -->'
    )

    # Put the image immediately after the lead paragraph so both readers and crawlers meet it early.
    m = re.search(r'(<p class="lead"[^>]*>.*?</p>)', html, flags=re.S)
    if m:
        html = html[:m.end()] + figure + html[m.end():]
    else:
        m = re.search(r'(</h1>)', html, flags=re.S)
        if m:
            html = html[:m.end()] + figure + html[m.end():]

    # Keep Article schema image-aware when Article JSON-LD is present.
    if '"@type":"Article"' in html and '"image"' not in html:
        html = html.replace('"@type":"Article",', f'"@type":"Article","image":"{img}",', 1)

    path.write_text(html, encoding="utf-8")
    print("enriched", slug)
