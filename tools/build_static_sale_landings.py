from pathlib import Path
import json, html

ROOT=Path(__file__).resolve().parents[1]
rows=json.loads((ROOT/'data.json').read_text(encoding='utf-8'))
rows=[r for r in rows if isinstance(r,dict) and r.get('Hiển thị trên Web')=='Có']

LANDINGS=[
 ('ban-can-ho-sapphire-smart-city.html','Bán căn hộ Sapphire Vinhomes Smart City','Căn Sapphire đang bán, giá và diện tích cập nhật từ quỹ căn hiện có.',lambda r:'sapphire' in str(r.get('Phân khu','')).lower()),
 ('ban-studio-vinhomes-smart-city.html','Bán Studio Vinhomes Smart City','Danh sách căn Studio đang bán tại Vinhomes Smart City.',lambda r:'studio' in str(r.get('Loại','')).lower()),
 ('ban-can-ho-2pn-vinhomes-smart-city.html','Bán căn hộ 2PN Vinhomes Smart City','Danh sách căn 2PN/2PN+ đang bán tại Vinhomes Smart City.',lambda r:'2pn' in str(r.get('Loại','')).lower()),
 ('ban-can-ho-duoi-4-ty-vinhomes-smart-city.html','Căn hộ Vinhomes Smart City dưới 4 tỷ','Nguồn căn đang chào bán dưới 4 tỷ tại Vinhomes Smart City.',lambda r:0<float(r.get('Giá bán') or 0)<4_000_000_000),
]

def card(r):
    price=float(r.get('Giá bán') or 0)/1e9
    img=r.get('Ảnh đại diện') or '/images/hero/hero-smart-city-mobile.webp'
    alt=f"{r.get('Loại','Căn hộ')} {r.get('Phân khu','')} {r.get('Tòa','')}"
    return f'''<article class="apt"><img src="{html.escape(str(img))}" alt="{html.escape(alt)}" loading="lazy"><div class="apt-body"><div class="apt-top"><h3>{html.escape(str(r.get('Loại') or 'Căn hộ'))} · {html.escape(str(r.get('Tòa') or ''))}</h3><div class="price">{price:.2f} tỷ</div></div><div class="apt-meta">{html.escape(str(r.get('Phân khu') or ''))} · {html.escape(str(r.get('Diện tích') or ''))} m² · {html.escape(str(r.get('Tầng') or ''))}<br>{html.escape(str(r.get('Nội thất') or ''))} · {html.escape(str(r.get('Pháp lý') or ''))}</div></div></article>'''

for filename,title,desc,pred in LANDINGS:
    items=[r for r in rows if pred(r)]
    cards=''.join(card(r) for r in items[:24]) or '<p>Chưa có căn phù hợp trong dữ liệu hiện tại.</p>'
    doc=f'''<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} | Sàn Smart City</title><meta name="description" content="{desc}"><link rel="canonical" href="https://timmuasmartcity.com/{filename}"><meta name="robots" content="index,follow,max-image-preview:large"><meta property="og:type" content="website"><meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:image" content="https://timmuasmartcity.com/images/hero/hero-smart-city-desktop.webp"><link rel="stylesheet" href="/assets/portal.css"></head><body class="listing-page"><header class="top"><div class="shell nav"><a class="brand" href="/"><span class="brand-mark">⌂</span><span>Sàn Smart City</span></a><nav class="navlinks"><a href="/can-ho-dang-ban.html">Tất cả căn</a><a href="/cam-nang.html">Cẩm nang</a><a href="/ky-gui-ban-can.html">Ký gửi</a></nav></div></header><main><section class="listing-hero"><div class="shell"><div class="eyebrow">Dữ liệu tĩnh cho Google & người mua</div><h1>{title}</h1><p>{desc} Giá và tình trạng căn có thể thay đổi; cần xác nhận lại trước giao dịch.</p><div class="count">{len(items)} căn phù hợp trong dữ liệu hiện tại</div><div class="listing-grid">{cards}</div><a class="btn" style="background:#0b1220;color:#fff" href="/can-ho-dang-ban.html">Mở bộ lọc toàn bộ quỹ căn →</a></div></section></main></body></html>'''
    (ROOT/filename).write_text(doc,encoding='utf-8')
    print('built',filename,len(items))

sitemap=ROOT/'sitemap.xml'
if sitemap.exists():
    text=sitemap.read_text(encoding='utf-8')
    for filename,_,_,_ in LANDINGS:
        url='https://timmuasmartcity.com/'+filename
        if url not in text:
            text=text.replace('</urlset>',f'  <url><loc>{url}</loc><lastmod>2026-08-12</lastmod><changefreq>daily</changefreq><priority>0.9</priority></url>\n</urlset>')
    sitemap.write_text(text,encoding='utf-8')
