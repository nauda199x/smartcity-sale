import json
import unicodedata
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data.json"

rows = json.loads(DATA.read_text(encoding="utf-8"))
changed = 0

PROTECTED_NORMALIZED = {
    "ma noi bo", "ma can", "id can",
    "gia thu net", "gia thu net ty", "gia net", "gia chu thu",
    "hoa hong", "hoa hong moi gioi", "commission",
    "phi cn", "phi chuyen nhuong", "phi moi gioi",
}


def norm(s):
    s = unicodedata.normalize("NFD", str(s))
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return " ".join(s.lower().replace("_", " ").replace("-", " ").split())

for row in rows:
    if not isinstance(row, dict):
        continue
    for key in list(row.keys()):
        nk = norm(key)
        if nk in PROTECTED_NORMALIZED or nk.startswith("hoa hong") or nk.startswith("phi cn") or nk.startswith("gia thu net"):
            del row[key]
            changed += 1

DATA.write_text(
    json.dumps(rows, ensure_ascii=False, separators=(",", ":")),
    encoding="utf-8",
)
print(f"Removed {changed} protected public fields from {len(rows)} listings")
