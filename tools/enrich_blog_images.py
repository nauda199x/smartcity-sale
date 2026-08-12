from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
BLOG = ROOT / "blog"

GENERIC_IMG = "/images/editorial/vinhomes-smart-city-overview.png"
SAPPHIRE_IMG = "/images/editorial/sapphire-vinhomes-smart-city.jpg"
SAKURA_IMG = "/images/editorial/the-sakura-vinhomes-smart-city.jpg"
MASTERI_IMG = "/images/editorial/masteri-west-heights.jpg"
SITE = "https://timmuasmartcity.com"

MEDIA = {
    "gia-ban-vinhomes-smart-city": (GENERIC_IMG, "Toàn cảnh Vinhomes Smart City phía Tây Hà Nội", "Toàn cảnh Vinhomes Smart City", "Vinhomes"),
    "kinh-nghiem-mua-can-ho-vinhomes-smart-city": (GENERIC_IMG, "Không gian đô thị Vinhomes Smart City", "Không gian Vinhomes Smart City", "Vinhomes"),
    "mua-can-ho-2pn-vinhomes-smart-city": (GENERIC_IMG, "Vinhomes Smart City với hệ tiện ích và các tòa căn hộ", "Vinhomes Smart City", "Vinhomes"),
    "so-sanh-phan-khu-vinhomes-smart-city": (GENERIC_IMG, "Toàn cảnh các phân khu tại Vinhomes Smart City", "Toàn cảnh Vinhomes Smart City", "Vinhomes"),
    "chi-phi-mua-can-ho-chuyen-nhuong-vinhomes-smart-city": (GENERIC_IMG, "Căn hộ và cảnh quan Vinhomes Smart City", "Vinhomes Smart City", "Vinhomes"),
    "sapphire-vinhomes-smart-city": (SAPPHIRE_IMG, "The Sapphire Vinhomes Smart City", "The Sapphire Vinhomes Smart City", "Vinhomes"),
    "the-sakura-vinhomes-smart-city": (SAKURA_IMG, "Toàn cảnh The Sakura Vinhomes Smart City", "The Sakura Vinhomes Smart City", "Vinhomes"),
    "masteri-west-heights-smart-city": (MASTERI_IMG, "Masteri West Heights tại Vinhomes Smart City", "Masteri West Heights", "Masterise Homes"),
}

CSS = ".article figure.seo-media{margin:26px 0 30px}.article figure.seo-media img{display:block;width:100%;height:auto;aspect-ratio:16/9;object-fit:cover;border-radius:16px;background:#eef1f5}.article figure.seo-media figcaption{font-size:13px;line-height:1.5;color:#6b7280;margin-top:8px}"

for slug, (img, alt, caption, credit) in MEDIA.items():
    path = BLOG / slug / "index.html"
    if not path.exists():
        continue
    html = path.read_text(encoding="utf-8")
    html = re.sub(r"<!-- SEO_MEDIA_START -->.*?<!-- SEO_MEDIA_END -->", "", html, flags=re.S)
    if CSS not in html:
        html = html.replace("</style>", CSS + "</style>", 1)
    absolute = SITE + img
    html = re.sub(r'<meta property="og:image" content="[^"]+">', f'<meta property="og:image" content="{absolute}">', html, count=1)
    html = re.sub(r'<meta name="twitter:image" content="[^"]+">', f'<meta name="twitter:image" content="{absolute}">', html, count=1)
    if 'property="og:image"' not in html:
        html = html.replace("</head>", f'<meta property="og:image" content="{absolute}"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{absolute}"></head>', 1)
    figure = ('<!-- SEO_MEDIA_START --><figure class="seo-media">'
              f'<img src="{img}" alt="{alt}" loading="eager" decoding="async">'
              f'<figcaption>{caption} · Ảnh tư liệu: {credit}, lưu cục bộ trên Tìm Mua Smart City.</figcaption>'
              '</figure><!-- SEO_MEDIA_END -->')
    m = re.search(r'(<p class="lead"[^>]*>.*?</p>)', html, flags=re.S)
    if m:
        html = html[:m.end()] + figure + html[m.end():]
    if '"@type":"Article"' in html:
        html = re.sub(r'"image":"[^"]+",?', '', html, count=1)
        html = html.replace('"@type":"Article",', f'"@type":"Article","image":"{absolute}",', 1)
    path.write_text(html, encoding="utf-8")
