import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data.json"

rows = json.loads(DATA.read_text(encoding="utf-8"))
changed = 0
for row in rows:
    if not isinstance(row, dict):
        continue
    for key in ("Mã nội bộ", "Ma can", "Mã căn", "ID căn", "id can"):
        if key in row:
            del row[key]
            changed += 1

DATA.write_text(
    json.dumps(rows, ensure_ascii=False, separators=(",", ":")),
    encoding="utf-8",
)
print(f"Removed {changed} public apartment-id fields from {len(rows)} listings")
