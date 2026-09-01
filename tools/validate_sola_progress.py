#!/usr/bin/env python3
"""Validate The Sola Park September 2026 progress refresh."""

from pathlib import Path
import re
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
PAGE=ROOT/"phan-khu-smart-city"/"sola-park"/"index.html"
HUB=ROOT/"mat-bang-smart-city"/"sola-park"/"index.html"
TOWERS={c:ROOT/"mat-bang-smart-city"/"sola-park"/c/"index.html" for c in ("g1","g2","g3","g5","g6")}
PROJECT_HUB=ROOT/"phan-khu-smart-city"/"index.html"

errors=[]

page=PAGE.read_text(encoding="utf-8")
hub=HUB.read_text(encoding="utf-8")
project_hub=PROJECT_HUB.read_text(encoding="utf-8")

if "5 tòa đã cất nóc" not in page:
    errors.append("main Sola page does not state the five-tower topping-out status")
if "Đang hoàn thiện" not in page:
    errors.append("main Sola page missing finishing-stage status")
if "sola-progress-board" not in page:
    errors.append("main Sola progress board missing")
if page.count("<article>") < 5:
    errors.append("main Sola page missing progress items")
if "/images/official/sola-park/sola-park-cat-noc-g5-g6-moc-tien-do.webp" not in page:
    errors.append("main Sola hero is not the latest real progress image")
if "5 tòa đã lên đủ chiều cao" not in project_hub:
    errors.append("project hub card is stale")

if "G5 · The Avenue" not in hub or "39 tầng nổi" not in hub:
    errors.append("floorplan hub missing corrected G5 status")
if "G6 · The Sky" not in hub or hub.count("39 tầng nổi") < 2:
    errors.append("floorplan hub missing corrected G6 status")

for code in ("g1","g2","g3"):
    text=TOWERS[code].read_text(encoding="utf-8")
    if "35 tầng" not in text:
        errors.append(f"{code}: 35-floor fact missing")
    if "Đang hoàn thiện" not in text:
        errors.append(f"{code}: finishing status missing")
    if "/images/official/sola-park/" not in text:
        errors.append(f"{code}: local real progress hero missing")
    if "/images/hero/hero-smart-city-desktop.webp" in text:
        errors.append(f"{code}: generic hero still present")

for code in ("g5","g6"):
    text=TOWERS[code].read_text(encoding="utf-8")
    for required in ("39 tầng nổi","2 tầng","744 căn","30/07/2026","Đang hoàn thiện"):
        if required not in text:
            errors.append(f"{code}: missing {required}")
    if "~35 tầng" in text:
        errors.append(f"{code}: stale 35-floor value remains")
    if "/images/official/sola-park/" not in text:
        errors.append(f"{code}: local progress hero missing")
    if "/images/hero/hero-smart-city-desktop.webp" in text:
        errors.append(f"{code}: generic hero still present")

# No public source-labelled UI should be introduced.
for label,path in {"main":PAGE,"hub":HUB,**TOWERS}.items():
    html=path.read_text(encoding="utf-8")
    if re.search(r">\s*(Nguồn|Mở nguồn|Source)\b",html,re.I):
        errors.append(f"{label}: public source UI present")
    soup=BeautifulSoup(html,"html.parser")
    hot=[img.get("src","") for img in soup.find_all("img") if img.get("src","").startswith(("http://","https://"))]
    if hot:
        errors.append(f"{label}: image hotlink present")

if errors:
    print(f"SOLA PROGRESS VALIDATION FAILED ({len(errors)} errors)")
    for e in errors:
        print("-",e)
    raise SystemExit(1)

print("SOLA PROGRESS VALIDATION PASSED: 5 towers updated, G1-G3 finishing, G5-G6 39 floors/2 basements/744 units, local progress media only")
