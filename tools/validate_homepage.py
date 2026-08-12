#!/usr/bin/env python3
"""Fail-closed checks for the generated Homepage V3 artifact."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "index.html"
PUBLIC_IMAGE_HOST = "drive.google.com"
SENSITIVE = (
    "giá thu nét", "giá net", "giá chủ thu", "hoa hồng", "commission",
    "phí cn", "internal note", "ghi chú dữ liệu", "id nội bộ", "mã nội bộ",
)


class HomepageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []
        self.in_featured = False
        self.featured_images = []
        self.featured_html = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        classes = attributes.get("class", "").split()
        if tag == "article" and "hp-listing" in classes:
            self.in_featured = True
        if tag in {"img", "source"}:
            source = attributes.get("src") or attributes.get("srcset")
            if source:
                self.images.append(source)
                if self.in_featured and tag == "img":
                    self.featured_images.append(attributes)
        if self.in_featured:
            self.featured_html.append(self.get_starttag_text() or "")

    def handle_data(self, data):
        if self.in_featured:
            self.featured_html.append(data)

    def handle_endtag(self, tag):
        if self.in_featured:
            self.featured_html.append(f"</{tag}>")
        if tag == "article" and self.in_featured:
            self.in_featured = False


errors = []
text = PAGE.read_text(encoding="utf-8")
if re.search(r"{{[A-Z_]+}}", text):
    errors.append("generated homepage contains unresolved build tokens")
parser = HomepageParser()
parser.feed(text)
for source in parser.images:
    parsed = urlparse(source)
    if not parsed.scheme:
        target = ROOT / parsed.path.lstrip("/")
        if not target.is_file():
            errors.append(f"missing local homepage image: {source}")
if len(parser.featured_images) != 6:
    errors.append(f"expected 6 featured listing images, found {len(parser.featured_images)}")
for image in parser.featured_images:
    parsed = urlparse(image.get("src", ""))
    if parsed.scheme != "https" or parsed.netloc != PUBLIC_IMAGE_HOST or parsed.path != "/thumbnail":
        errors.append(f"featured listing has unapproved public image: {image.get('src', '')}")
    if not image.get("alt") or not image.get("onerror", "").endswith("/images/hero/hero-smart-city-mobile.webp'"):
        errors.append("featured listing image lacks alt text or local fallback")
featured_text = " ".join(parser.featured_html).lower()
for field in SENSITIVE:
    if field in featured_text:
        errors.append(f"featured inventory exposes sensitive field: {field}")
if errors:
    print(f"HOMEPAGE VALIDATION FAILED ({len(errors)} errors)")
    print("\n".join(f"- {error}" for error in errors))
    sys.exit(1)
print("HOMEPAGE VALIDATION PASSED: 6 real listing images, safe fields, local fallbacks")
