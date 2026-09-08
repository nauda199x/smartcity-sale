"""Regression checks for crawlable pagination and user-authored listing content."""
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from bs4 import BeautifulSoup
import build_seo_portal as seo
from marketplace_pages import render_inventory, floorplan_url

ROOT = Path(__file__).resolve().parents[1]


def fixture(number=1):
    return dict(id=f'00000000-0000-4000-8000-{number:012d}', listing_code=f'SC-{number:08d}',
                slug=f'can-ho-smart-city-sc-{number:08d}', listing_type='sale',
                title=f'Căn hộ Smart City {number}', description='Thông tin căn hộ đã kiểm tra.',
                phase='Sapphire', tower='S402', unit_type='1PN+1', area_sqm=45,
                floor_label='Cao', furnishing='Nội thất cơ bản', price_vnd=3_000_000_000,
                poster_name='Người đăng', contact_phone='', approved_at='2026-09-01T03:00:00Z',
                created_at='2026-08-31T03:00:00Z', listing_images=[])


class MarketplacePages(unittest.TestCase):
    def test_title_and_description_cannot_escape_into_executable_markup(self):
        row=fixture()
        row['title']='Tin </script><script>alert("injection")</script>'
        row['description']='<img src=x onerror="alert(1)"> Nội dung người đăng'
        doc=BeautifulSoup(seo.listing_html(row, '/mua-ban-smart-city/'+row['slug']+'/'), 'html.parser')
        self.assertEqual(doc.select_one('h1').get_text(), row['title'])
        self.assertIsNone(doc.select_one('[onerror]'))
        self.assertFalse(any(not s.get('src') and s.get('type')!='application/ld+json' for s in doc.select('script')))
        for script in doc.select('script[type="application/ld+json"]'):
            json.loads(script.string)

    def test_static_detail_has_shared_controls_and_correct_original_date(self):
        row=fixture()
        doc=BeautifulSoup(seo.listing_html(row,'/mua-ban-smart-city/'+row['slug']+'/'),'html.parser')
        for selector in ['[data-detail-save]','[data-detail-share]','[data-report-form]',
                         '[data-detail-mobile-contact]','[data-static-listing]','[data-live-status]']:
            self.assertIsNotNone(doc.select_one(selector),selector)
        self.assertEqual(doc.select_one('[data-detail-date]')['datetime'],'2026-09-01')
        self.assertFalse(doc.select_one('[data-detail-gallery] img'))
        self.assertIsNone(doc.select_one('meta[property="og:image"]'))
        self.assertEqual(doc.select_one('[data-detail-floorplan]')['href'],'/mat-bang-smart-city/sapphire/s4-02/')

    def test_pagination_has_exact_crawlable_rows_and_self_canonical(self):
        rows=[fixture(n) for n in range(1,24)]
        template=(ROOT/'mua-ban-smart-city/index.html').read_text()
        doc=BeautifulSoup(render_inventory(template,rows,'/mua-ban-smart-city/',3,seo.image_url,seo.price_text),'html.parser')
        self.assertEqual(len(doc.select('[data-static-listing-card]')),3)
        self.assertEqual(doc.select_one('link[rel=canonical]')['href'],'https://timmuasmartcity.com/mua-ban-smart-city/page/3/')
        self.assertEqual(doc.select_one('[data-inventory]')['data-inventory-static-pages'],'3')
        schema=json.loads(doc.select_one('[data-inventory-schema]').string)
        self.assertEqual(schema['itemListElement'][0]['position'],21)
        self.assertEqual(schema['numberOfItems'],3)
        self.assertEqual(doc.select_one('link[rel=prev]')['href'],'https://timmuasmartcity.com/mua-ban-smart-city/page/2/')
        self.assertIsNone(doc.select_one('link[rel=next]'))

    def test_category_has_its_own_content_and_schema(self):
        template=(ROOT/'mua-ban-smart-city/index.html').read_text()
        doc=BeautifulSoup(render_inventory(template,[fixture()],'/mua-ban-smart-city/loai-can/1pn-1/',1,
                 seo.image_url,seo.price_text,heading='Mua bán 1PN+1 Smart City',defaults={'unit':'1PN+1'}),'html.parser')
        self.assertEqual(doc.select_one('[data-inventory]')['data-default-unit'],'1PN+1')
        self.assertEqual(doc.select_one('h1').get_text(),'Mua bán 1PN+1 Smart City')
        graph=json.loads(doc.select_one('script[type="application/ld+json"]').string)['@graph']
        self.assertEqual(graph[0]['url'],'https://timmuasmartcity.com/mua-ban-smart-city/loai-can/1pn-1/')

    def test_masteri_and_sapphire_aliases_use_real_floorplans(self):
        self.assertEqual(floorplan_url('Mas D'),'/mat-bang-smart-city/masteri-west-heights/west-d/')
        self.assertEqual(floorplan_url('S303'),'/mat-bang-smart-city/sapphire/s3-03/')
        self.assertEqual(floorplan_url('UNKNOWN'),'/mat-bang-smart-city/')

    def test_source_failure_blocks_replacing_published_seo_with_empty_inventory(self):
        with patch.object(seo.subprocess,'run') as call:
            call.return_value.returncode=22
            with self.assertRaisesRegex(RuntimeError,'preserve published'):
                seo.fetch_approved_listings()

    def test_fetch_continues_past_500(self):
        with patch.object(seo.subprocess,'run') as call:
            call.return_value.returncode=0
            class Response:
                returncode=0
                def __init__(self,rows): self.stdout=json.dumps(rows)
            call.side_effect=[Response([fixture(n) for n in range(500)]),Response([fixture(500)])]
            self.assertEqual(len(seo.fetch_approved_listings()),501)


if __name__=='__main__':
    unittest.main()
