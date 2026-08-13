#!/usr/bin/env python3
"""Build the neutral, source-linked project comparison and refresh profile sitemap entries."""
import json
from html import escape
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DOMAIN='https://timmuasmartcity.com'
projects=json.loads((ROOT/'data/projects/projects.json').read_text())['projects']
def row(p):
    source=p['sources'][0]
    fit=p['fit'][0]
    return f'''<tr><th scope="row"><a href="/{p['route']}">{escape(p['name'])}</a></th><td>{escape(p['developer'])}</td><td>{escape(p['entityType'])}</td><td>{escape(p['facts'][2]['value'])}</td><td>{escape(p['buildings'][0])}</td><td>{escape(fit)}</td><td><a href="{escape(source['url'])}" rel="nofollow noopener">{escape(source['publisher'])}</a></td></tr>'''
title='So sánh dự án Vinhomes Smart City | Ma trận trung lập cho người mua'
desc='So sánh dự án và phân khu Smart City theo chủ thể, loại thực thể, vị trí, cấu trúc sản phẩm và nhu cầu người mua; không xếp hạng chủ quan.'
schema=[{'@context':'https://schema.org','@type':'WebPage','name':title,'description':desc,'url':DOMAIN+'/so-sanh-phan-khu-vinhomes-smart-city.html','inLanguage':'vi'},{'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Trang chủ','item':DOMAIN+'/'},{'@type':'ListItem','position':2,'name':'Hồ sơ dự án','item':DOMAIN+'/phan-khu.html'},{'@type':'ListItem','position':3,'name':'So sánh dự án','item':DOMAIN+'/so-sanh-phan-khu-vinhomes-smart-city.html'}]}]
html=f'''<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><meta name="description" content="{desc}"><link rel="canonical" href="{DOMAIN}/so-sanh-phan-khu-vinhomes-smart-city.html"><meta name="robots" content="index,follow,max-image-preview:large"><meta property="og:type" content="website"><meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:image" content="{DOMAIN}/images/hero/hero-smart-city-desktop.webp"><link rel="stylesheet" href="/assets/portal.css"><link rel="stylesheet" href="/assets/design-system.css"><link rel="stylesheet" href="/assets/project-profiles.css"><script type="application/ld+json">{json.dumps(schema,ensure_ascii=False)}</script></head><body class="project-profile"><header class="top"><div class="shell nav"><a class="brand" href="/">Tìm Mua Smart City</a><nav class="navlinks"><a href="/phan-khu.html">Dự án</a><a href="/can-ho-dang-ban.html">Căn đang bán</a><a href="/gia-ban-vinhomes-smart-city.html">Giá bán</a></nav></div></header><main><nav class="shell pp-breadcrumb"><a href="/">Trang chủ</a><span>›</span><a href="/phan-khu.html">Hồ sơ dự án</a><span>›</span><span>So sánh</span></nav><section class="pp-hub-hero"><div class="shell"><span>Ma trận nghiên cứu</span><h1>So sánh dự án & phân khu<br>không xếp hạng chủ quan.</h1><p>Bảng phân biệt chủ thể và loại thực thể trước khi so vị trí, sản phẩm và độ phù hợp. Không có dự án “tốt nhất” cho mọi người mua.</p></div></section><section class="pp-section"><div class="shell"><div class="pp-heading"><span>Đối chiếu</span><h2>Mười hồ sơ, sáu chiều so sánh</h2></div><div class="pp-table-wrap"><table class="pp-comparison"><thead><tr><th>Dự án / phân khu</th><th>Chủ thể</th><th>Loại thực thể</th><th>Địa bàn</th><th>Đặc điểm cần đọc</th><th>Gợi ý buyer profile</th><th>Nguồn sơ cấp</th></tr></thead><tbody>{''.join(row(p) for p in projects)}</tbody></table></div><p class="pp-source">Các mô tả giúp lập shortlist, không phải điểm số. Bấm tên hồ sơ để xem inventory, buyer notes, FAQ và toàn bộ nguồn.</p></div></section><section class="pp-section pp-dark"><div class="shell pp-split"><div><h2>Cách dùng ma trận</h2><ol><li>Chọn đúng loại thực thể và chủ thể.</li><li>Mở 2–3 hồ sơ phù hợp nhu cầu.</li><li>So căn tương đồng về tòa, loại, diện tích và tình trạng.</li></ol></div><div class="pp-links"><a href="/phan-khu.html">Knowledge hub →</a><a href="/can-ho-dang-ban.html">Inventory hiện tại →</a><a href="/gia-ban-vinhomes-smart-city.html">Cách đọc giá/m² →</a><a href="/mua-can-ho-2pn-vinhomes-smart-city.html">Hướng dẫn chọn căn 2PN →</a></div></div></section></main><footer class="footer"><div class="shell">Tìm Mua Smart City · Ma trận trung lập dành cho người mua.</div></footer></body></html>'''
(ROOT/'so-sanh-phan-khu-vinhomes-smart-city.html').write_text(html)
# Insert any missing profile URLs before urlset close.
smap=(ROOT/'sitemap.xml').read_text()
for p in projects:
    url=f'{DOMAIN}/{p["route"]}'
    if url not in smap:
        entry=f'  <url><loc>{url}</loc><lastmod>2026-08-13</lastmod><changefreq>weekly</changefreq><priority>0.9</priority></url>\n'
        smap=smap.replace('</urlset>',entry+'</urlset>')
(ROOT/'sitemap.xml').write_text(smap)
print('built project comparison and refreshed sitemap profiles')
