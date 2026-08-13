#!/usr/bin/env python3
"""Validate generated project profiles, provenance, media and public safety."""
from __future__ import annotations

from html.parser import HTMLParser
import json
import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "data/projects/projects.json").read_text(encoding="utf-8"))
PRIVATE_TERMS = ("Giá thu nét", "Giá net", "Giá chủ thu", "Hoa hồng", "Commission", "Phí CN", "Ghi chú nội bộ", "Mã nội bộ", "ID nội bộ")


class ProfileParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.canonical=[]; self.images=[]; self.summaries=[]; self.faq_answers=[]; self.scripts=[]; self._summary=False; self._faq_p=False; self._script=False; self._details=0; self._buffer=[]
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "link" and "canonical" in attrs.get("rel", "").split(): self.canonical.append(attrs.get("href", ""))
        if tag == "img": self.images.append(attrs.get("src", ""))
        if tag == "details": self._details += 1
        if tag == "summary": self._summary=True; self._buffer=[]
        if tag == "p" and self._details: self._faq_p=True; self._buffer=[]
        if tag == "script" and attrs.get("type") == "application/ld+json": self._script=True; self._buffer=[]
    def handle_data(self, data):
        if self._summary or self._faq_p or self._script: self._buffer.append(data)
    def handle_endtag(self, tag):
        value = "".join(self._buffer).strip()
        if tag == "summary" and self._summary: self.summaries.append(value); self._summary=False
        elif tag == "p" and self._faq_p: self.faq_answers.append(value); self._faq_p=False
        elif tag == "script" and self._script: self.scripts.append(value); self._script=False
        elif tag == "details": self._details -= 1
        self._buffer=[]


def approved_image(value: str, route: Path) -> bool:
    parsed = urlparse(value.replace("&amp;", "&"))
    if not parsed.scheme:
        target = ROOT / parsed.path.lstrip("/") if parsed.path.startswith("/") else route.parent / parsed.path
        return target.is_file()
    query = parse_qs(parsed.query)
    return (parsed.scheme == "https" and parsed.netloc == "drive.google.com"
            and parsed.path == "/thumbnail" and bool(query.get("id", [""])[0])
            and query.get("sz") == ["w1200"])


errors=[]; canonicals={}
for project in DATA.get("projects", []):
    label=project.get("slug", "unknown"); route=ROOT / project.get("route", "")
    if not route.is_file(): errors.append(f"{label}: project route missing: {route.name}"); continue
    source_ids={source.get("id") for source in project.get("sources", [])}
    if not source_ids: errors.append(f"{label}: no provenance sources")
    for source in project.get("sources", []):
        parsed_source = urlparse(source.get("url", ""))
        if parsed_source.scheme != "https" or not parsed_source.netloc or not source.get("publisher") or not source.get("accessed"):
            errors.append(f"{label}: incomplete or invalid provenance source: {source.get('id')}")
    for fact in project.get("facts", []):
        if fact.get("sourceId") not in source_ids: errors.append(f"{label}: fact source reference missing: {fact.get('sourceId')}")
    for _, url in project.get("related", []):
        parsed=urlparse(url)
        if parsed.scheme or not url.startswith("/"): errors.append(f"{label}: related link is not internal: {url}")
        elif not (ROOT / parsed.path.lstrip("/")).is_file(): errors.append(f"{label}: internal related link missing: {url}")
    manifest=ROOT / "data/media" / f"{label}.json"
    if manifest.exists():
        payload=json.loads(manifest.read_text(encoding="utf-8"))
        for asset in payload.get("assets", []):
            for value in asset.get("variants", {}).values():
                if not (ROOT / value.lstrip("/")).is_file(): errors.append(f"{label}: media manifest reference missing: {value}")
    text=route.read_text(encoding="utf-8"); doc=ProfileParser(); doc.feed(text)
    if len(doc.canonical) != 1: errors.append(f"{label}: expected one canonical")
    elif doc.canonical[0] in canonicals: errors.append(f"{label}: duplicate canonical with {canonicals[doc.canonical[0]]}")
    else: canonicals[doc.canonical[0]]=label
    for image in doc.images:
        if not approved_image(image, route): errors.append(f"{label}: unapproved or missing image URL: {image}")
    for term in PRIVATE_TERMS:
        if re.search(re.escape(term), text, re.I): errors.append(f"{label}: private inventory field appears: {term}")
    schemas=[]
    for script in doc.scripts:
        try: schemas.extend(json.loads(script) if script.lstrip().startswith("[") else [json.loads(script)])
        except json.JSONDecodeError: errors.append(f"{label}: invalid JSON-LD")
    faq_pages=[item for item in schemas if item.get("@type") == "FAQPage"]
    schema_faq=[(item.get("name"), item.get("acceptedAnswer", {}).get("text")) for item in faq_pages[0].get("mainEntity", [])] if len(faq_pages)==1 else []
    expected=[tuple(item) for item in project.get("faq", [])]
    visible=list(zip(doc.summaries[-len(expected):], doc.faq_answers[-len(expected):])) if expected else []
    if schema_faq != expected or visible != expected: errors.append(f"{label}: FAQ schema and visible FAQ differ")

if errors:
    print(f"PROJECT PROFILE VALIDATION FAILED ({len(errors)} errors)")
    print("\n".join(f"- {error}" for error in errors)); raise SystemExit(1)
print(f"PROJECT PROFILE VALIDATION PASSED: {len(DATA['projects'])} profiles")
