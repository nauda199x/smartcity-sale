"""Shared crawlable marketplace surfaces; all inventory comes from approved rows."""
from collections import defaultdict
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from urllib.parse import urlencode
import json
import hashlib
import math
import re
import unicodedata

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SITE = 'https://timmuasmartcity.com'
PAGE_SIZE = 10
VERSION = '20260908-parity1'


def safe_json(value):
    return json.dumps(value, ensure_ascii=False).replace('<', '\\u003c')


def slug(value):
    value = unicodedata.normalize('NFD', str(value).lower().replace('đ', 'd'))
    value = ''.join(c for c in value if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+', '-', value).strip('-')


def unit_group(value):
    return {'1PN+': '1PN+1', '2PN+': '2PN+1', '2PN+1 (1WC)': '2PN+1',
            '2PN+1 (2WC)': '2PN+1', '3PN+': '3PN+1'}.get(value, value)


def category_url(row):
    return '/cho-thue-smart-city/' if row.get('listing_type') == 'rent' else '/mua-ban-smart-city/'


def listing_url(row):
    return category_url(row) + str(row['slug']) + '/'


def floorplan_url(tower):
    code = str(tower or '').lower().replace(' ', '-')
    code = re.sub(r'^s(\d)(\d{2})$', r's\1-\2', code).replace('mas-', 'west-')
    matches = sorted((ROOT / 'mat-bang-smart-city').glob(f'**/{code}/index.html')) if re.fullmatch(r'[a-z0-9-]+', code) else []
    return '/' + str(matches[0].parent.relative_to(ROOT)) + '/' if matches else '/mat-bang-smart-city/'


def detail_content(row, image_url, price_text):
    row = row or {}
    title = str(row.get('title') or 'Thông tin căn hộ')
    rent = row.get('listing_type') == 'rent'
    base = category_url(row)
    phone = str(row.get('contact_phone') or '')
    tel = re.sub(r'[^+0-9]', '', phone)
    images = sorted(row.get('listing_images') or [], key=lambda x: x.get('sort_order') or 0)
    gallery = []
    for i, img in enumerate(images):
        url = image_url(img.get('storage_path'))
        if not url:
            continue
        alt = escape(str(img.get('alt_text') or f'{title} — ảnh {i+1}'))
        gallery.append(f'<figure><img src="{escape(url)}" alt="{alt}" width="1200" height="900" loading="{"lazy" if i else "eager"}" {"" if i else "fetchpriority=high"} decoding="async"></figure>')
    gallery_html = ('<div class="ld-gallery-stage"><div class="ld-gallery-track" tabindex="0" aria-label="Ảnh tin đăng">' + ''.join(gallery) + f'</div><span class="ld-gallery-counter" data-gallery-counter>1 / {len(gallery)}</span></div>') if gallery else '<div class="ld-empty-gallery"><strong>Hình ảnh đang được bổ sung</strong><p>Liên hệ người đăng để xem hình ảnh và hiện trạng căn.</p></div>'
    posted = str(row.get('approved_at') or row.get('created_at') or '')[:10]
    area = float(row.get('area_sqm') or 0)
    price = float(row.get('price_vnd') or 0)
    values = {
        'content_hidden': '' if row else 'hidden', 'category_url': base,
        'category': ('Cho thuê' if rent else 'Mua bán') + ' Smart City',
        'action': 'Cho thuê' if rent else 'Mua bán', 'code': row.get('listing_code', ''),
        'date_hidden': '' if posted else 'hidden', 'posted': posted,
        'posted_label': '/'.join(reversed(posted.split('-'))), 'title': title,
        'phase': row.get('phase', ''), 'tower': row.get('tower', ''),
        'price_label': 'thuê' if rent else 'bán', 'price': price_text(price, 'rent' if rent else 'sale'),
        'price_per_sqm': f'~{price/area/1e6:.1f} tr/m²'.replace('.', ',') if price and area and not rent else '',
        'area': f'{area:g} m²'.replace('.', ',') if area else 'Chưa cập nhật',
        'unit': row.get('unit_type') or 'Chưa cập nhật', 'floor': row.get('floor_label') or 'Chưa cập nhật',
        'description': row.get('description') or '', 'furnishing': row.get('furnishing') or 'Chưa cập nhật',
        'floorplan_url': floorplan_url(row.get('tower')),
        'same_tower_url': base + '?' + urlencode({'tower': row.get('tower') or ''}),
        'same_unit_url': base + '?' + urlencode({'bedroom': unit_group(row.get('unit_type') or '')}),
        'unit_url': '/mat-bang-smart-city/', 'unit_guide_hidden': 'hidden',
        'initials': ''.join(word[0] for word in str(row.get('poster_name') or 'Người đăng').split()[-2:]).upper(),
        'poster': row.get('poster_name') or 'Người đăng', 'phone_url': 'tel:' + tel if tel else '',
        'phone': phone, 'phone_hidden': '' if tel else 'hidden',
        'zalo_url': 'https://zalo.me/' + re.sub(r'\D', '', phone) if tel else '',
        'contact_empty_hidden': 'hidden' if tel else '', 'report_hidden': '' if row.get('id') else 'hidden',
    }
    template = (ROOT / 'tools/templates/listing-detail.html.tpl').read_text()
    return re.sub(r'\{\{(\w+)\}\}', lambda m: gallery_html if m[1] == 'gallery' else escape(str(values[m[1]])), template)


def detail_page(html, row, image_url, price_text, dynamic=False):
    doc = BeautifulSoup(html, 'html.parser')
    main = doc.select_one('main')
    main.clear()
    main['data-listing-detail' if dynamic else 'data-static-listing'] = ''
    if row:
        main['data-listing-id'] = row['id']
        main['data-listing-slug'] = row['slug']
        main['data-listing-url'] = listing_url(row)
    if dynamic:
        main.append(BeautifulSoup('<div class="container ld-skeleton" data-detail-loading role="status">Đang tải thông tin căn hộ…</div><section class="container marketplace-state" data-detail-missing hidden><div><h1 data-missing-title>Tin không còn hiển thị</h1><p data-missing-copy></p><a href="/mua-ban-smart-city/">Xem căn đang bán</a> · <a href="/cho-thue-smart-city/">Xem căn cho thuê</a></div></section>', 'html.parser'))
    main.append(BeautifulSoup(detail_content(row, image_url, price_text), 'html.parser'))
    doc.body['class'] = ['listing-detail-page']
    for node in doc.select('script[src*="marketplace-"],script[src*="listing-detail-ui"],link[href*="listing-detail.css"]'):
        node.decompose()
    doc.head.append(doc.new_tag('link', rel='stylesheet', href=f'/assets/css/listing-detail.css?v={VERSION}'))
    for name in ['marketplace-config', 'marketplace-api', 'listing-detail-ui', 'marketplace-detail' if dynamic else 'marketplace-static-status', 'marketplace-lightbox']:
        doc.body.append(doc.new_tag('script', src=f'/assets/js/{name}.js?v={VERSION}', defer=''))
    if row and not row.get('listing_images'):
        for node in doc.select('meta[property="og:image"],meta[name="twitter:image"]'):
            node.decompose()
    return str(doc)


def inventory_card(row, image_url, price_text, index):
    esc = lambda v: escape(str(v or ''))
    url, title = esc(listing_url(row)), esc(row['title'])
    images = sorted(row.get('listing_images') or [], key=lambda x: x.get('sort_order') or 0)
    media = '<span class="inventory-placeholder">Chưa có ảnh</span>'
    if images:
        media += f'<img src="{esc(image_url(images[0]["storage_path"]))}" alt="{esc(images[0].get("alt_text") or row["title"])}" width="560" height="420" loading="{"lazy" if index else "eager"}" decoding="async"><span class="inventory-image-count">{len(images)} ảnh</span>'
    rent = row['listing_type'] == 'rent'
    media += '<span class="inventory-status">' + ('CHO THUÊ' if rent else 'MUA BÁN') + '</span>'
    price = price_text(row.get('price_vnd'), row['listing_type'])
    amount, area = float(row.get('price_vnd') or 0), float(row.get('area_sqm') or 0)
    ppm = f'<small>{amount/area/1e6:.1f} tr/m²</small>'.replace('.', ',') if amount and area and not rent else ''
    date = str(row.get('approved_at') or row.get('created_at') or '')[:10]
    phone = str(row.get('contact_phone') or '')
    tel = re.sub(r'[^+0-9]', '', phone)
    contact = f'<a class="inventory-call" href="tel:{esc(tel)}">{esc(phone)}</a><a class="inventory-zalo" href="https://zalo.me/{re.sub(r"\D", "", phone)}" target="_blank" rel="noopener">Zalo</a>' if tel else ''
    featured = '<span class="inventory-featured">Tin nổi bật</span>' if row.get('is_featured') else ''
    return f'<article class="inventory-row" data-static-listing-card><a class="inventory-media" href="{url}" aria-label="Xem {title}">{media}</a><div class="inventory-info">{featured}<p class="inventory-location">{esc(row.get("phase"))} · {esc(row.get("tower"))}</p><h3><a href="{url}">{title}</a></h3><p class="inventory-specs">{area:g} m² · {esc(row.get("unit_type"))} · Tầng {esc(row.get("floor_label"))}</p></div><div class="inventory-price"><span class="inventory-price-label">Giá {"thuê" if rent else "bán"}</span><strong>{esc(price)}</strong>{ppm}</div><div class="inventory-poster"><div><strong>{esc(row.get("poster_name"))}</strong><time datetime="{esc(date)}">Đăng {esc("/".join(reversed(date.split("-"))))}</time></div></div><div class="inventory-actions">{contact}<a class="inventory-view" href="{url}">Xem chi tiết →</a></div></article>'


def render_inventory(template, rows, base, page, image_url, price_text, *, heading='', defaults=None):
    doc = BeautifulSoup(template, 'html.parser')
    root = doc.select_one('[data-inventory]')
    pages = max(1, math.ceil(len(rows)/PAGE_SIZE))
    root['data-inventory-base'] = base
    root['data-inventory-static-pages'] = str(pages)
    for key, value in (defaults or {}).items():
        root['data-default-' + key] = value
    selected = rows[(page-1)*PAGE_SIZE:page*PAGE_SIZE]
    grid = root.select_one('[data-listing-grid]')
    grid.clear()
    for i, row in enumerate(selected):
        grid.append(BeautifulSoup(inventory_card(row, image_url, price_text, i), 'html.parser'))
    root.select_one('[data-listing-count]').string = f'{len(rows)} tin đăng'
    root.select_one('[data-inventory-summary]').string = f'Hiển thị {(page-1)*10+1}–{min(page*10,len(rows))} trong {len(rows)} căn' if rows else 'Hiển thị 0 căn'
    state = root.select_one('[data-listing-state]')
    if rows:
        state['hidden'] = ''
    else:
        state.attrs.pop('hidden', None)
    pager = root.select_one('[data-inventory-pagination]')
    pager.clear()
    page_url = lambda n: base if n == 1 else base + f'page/{n}/'
    for n in sorted({1, pages, page-1, page, page+1}):
        if not 1 <= n <= pages or pages == 1:
            continue
        link = doc.new_tag('a', href=page_url(n), attrs={'data-page': str(n), 'aria-label': f'Trang {n}'})
        link.string = str(n)
        if n == page:
            link['aria-current'] = 'page'
        pager.append(link)
    canonical = SITE + page_url(page)
    for selector, attr in [('link[rel=canonical]', 'href'), ('meta[property="og:url"]', 'content')]:
        node = doc.select_one(selector)
        if node:
            node[attr] = canonical
    if heading:
        doc.select_one('h1').string = heading
        root.select_one('h2').string = heading
        doc.title.string = heading + ' | Sàn Smart City'
        for selector in ['meta[property="og:title"]', 'meta[name="twitter:title"]']:
            if doc.select_one(selector): doc.select_one(selector)['content'] = heading
        description = f'{len(rows)} tin {heading.lower()}. Xem giá rao, hình ảnh, diện tích và liên hệ trực tiếp người đăng.'
        for selector in ['meta[name=description]', 'meta[property="og:description"]']:
            if doc.select_one(selector): doc.select_one(selector)['content'] = description
        # A category needs its own concise context, not the generic hub article.
        for section in doc.select('main > section'):
            if section is not root and not section.select_one('[data-inventory]'):
                section.decompose()
        for old_schema in doc.select('script[type="application/ld+json"]'):
            old_schema.decompose()
        category_schema = doc.new_tag('script', type='application/ld+json')
        category_schema.string = safe_json({'@context': 'https://schema.org', '@graph': [
            {'@type':'CollectionPage','name':heading,'url':canonical,'description':description,'inLanguage':'vi-VN'},
            {'@type':'BreadcrumbList','itemListElement':[
                {'@type':'ListItem','position':1,'name':'Trang chủ','item':SITE+'/'},
                {'@type':'ListItem','position':2,'name':heading,'item':canonical}
            ]}
        ]})
        doc.head.append(category_schema)
    root['data-inventory-home-title'] = doc.title.get_text()
    if page > 1:
        doc.title.string += f' – Trang {page}'
    for node in doc.select('script[data-seo-itemlist],script[data-inventory-schema],link[rel=prev],link[rel=next]'):
        node.decompose()
    schema = doc.new_tag('script', type='application/ld+json', attrs={'data-inventory-schema': ''})
    schema.string = safe_json({'@context':'https://schema.org','@type':'ItemList','numberOfItems':len(selected),'itemListElement':[{'@type':'ListItem','position':(page-1)*10+i+1,'url':SITE+listing_url(row),'name':row['title']} for i,row in enumerate(selected)]})
    doc.head.append(schema)
    for rel, n in [('prev',page-1),('next',page+1)]:
        if 1 <= n <= pages:
            doc.head.append(doc.new_tag('link', rel=rel, href=SITE+page_url(n)))
    return str(doc)


def build_inventory(out, rows, image_url, price_text):
    # Only public listing fields are fingerprinted. View increments do not cause deployments.
    stable = sorted(rows, key=lambda row: str(row['id']))
    fingerprint = hashlib.sha256(json.dumps(stable, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    snapshot = out / 'assets/data/marketplace-snapshot.json'
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    snapshot.write_text(json.dumps({'fingerprint': fingerprint, 'count': len(rows)}))
    for typ, base in [('sale','/mua-ban-smart-city/'),('rent','/cho-thue-smart-city/')]:
        target = out / base.strip('/') / 'index.html'
        template = target.read_text()
        filtered = [r for r in rows if r['listing_type'] == typ]
        filtered.sort(key=lambda r: (bool(r.get('is_featured')), str(r.get('approved_at') or r.get('created_at') or ''), str(r['id'])), reverse=True)
        groups = defaultdict(list)
        for row in filtered:
            for field in ['phase','unit']:
                key = row.get('phase') if field == 'phase' else unit_group(row.get('unit_type'))
                if key: groups[(field,key)].append(row)
        links=[]
        for (field,key), group in groups.items():
            path = base + ('phan-khu/' if field == 'phase' else 'loai-can/') + slug(key) + '/'
            label = ('Cho thuê' if typ == 'rent' else 'Mua bán') + f' {key} Smart City'
            defaults={field:key}
            for page in range(1, max(1, math.ceil(len(group)/10))+1):
                rel = path if page == 1 else path+f'page/{page}/'
                file=out/rel.strip('/')/'index.html';file.parent.mkdir(parents=True, exist_ok=True)
                file.write_text(render_inventory(template,group,path,page,image_url,price_text,heading=label,defaults=defaults))
            links.append(f'<a href="{escape(path)}">{escape(key)} · {len(group)} tin</a>')
        for page in range(1, max(1, math.ceil(len(filtered)/10))+1):
            rel = base if page == 1 else base+f'page/{page}/'
            file=out/rel.strip('/')/'index.html';file.parent.mkdir(parents=True, exist_ok=True)
            html=render_inventory(template,filtered,base,page,image_url,price_text)
            if links:
                doc=BeautifulSoup(html,'html.parser');nav=doc.new_tag('nav',attrs={'class':'inventory-category-links','aria-label':'Quỹ căn theo phân khu và loại căn'})
                nav.append(BeautifulSoup(''.join(links),'html.parser'));doc.select_one('[data-inventory] > .container').append(nav);html=str(doc)
            file.write_text(html)


def build_market_prices(out, rows, price_text):
    target=out/'gia-smart-city/index.html'
    if not target.exists(): return
    doc=BeautifulSoup(target.read_text(),'html.parser')
    groups=defaultdict(list)
    for row in rows:
        if float(row.get('price_vnd') or 0)>0:
            groups[(row['listing_type'],row.get('phase',''),unit_group(row.get('unit_type','')))].append(row)
    table=[]
    for (typ,phase,unit), group in sorted(groups.items()):
        prices=[r['price_vnd'] for r in group];bounds=price_text(min(prices),typ)
        if min(prices)!=max(prices): bounds+=' – '+price_text(max(prices),typ)
        url=category_url(group[0])+'?'+urlencode({'phase':phase,'bedroom':unit})
        cells=[('Cho thuê' if typ=='rent' else 'Mua bán'),phase,unit,str(len(group)),bounds]
        table.append('<tr>'+''.join(f'<td>{escape(c)}</td>' for c in cells)+f'<td><a href="{escape(url)}">Xem tin →</a></td></tr>')
    if not table: return
    stamp=datetime.now(timezone.utc).strftime('%d/%m/%Y')
    html=f'<section class="container marketplace-price-live" id="gia-rao-dang-hien-thi"><h2>Giá rao từ tin đang hiển thị</h2><p>Cập nhật {stamp} · {len(rows)} tin đang giao dịch. Giá do người đăng cung cấp, chưa phải giá giao dịch thành công.</p><div class="price-table-scroll"><table><thead><tr><th>Giao dịch</th><th>Phân khu</th><th>Loại căn</th><th>Số tin</th><th>Khoảng giá rao</th><th>Quỹ căn</th></tr></thead><tbody>{"".join(table)}</tbody></table></div></section>'
    doc.select_one('main').insert(1,BeautifulSoup(html,'html.parser'));target.write_text(str(doc))
