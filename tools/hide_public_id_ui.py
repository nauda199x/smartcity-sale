from pathlib import Path

INDEX = Path(__file__).resolve().parents[1] / "index.html"
text = INDEX.read_text(encoding="utf-8")
replacements = {
    'placeholder="Tìm phân khu, mã căn, loại căn… (VD: Sapphire, 2PN+, 3,5 tỷ)"': 'placeholder="Tìm phân khu, loại căn, mức giá… (VD: Sapphire, 2PN+, 3,5 tỷ)"',
    'aria-label="Tìm căn hộ theo phân khu, mã căn, loại căn hoặc giá"': 'aria-label="Tìm căn hộ theo phân khu, loại căn hoặc giá"',
}
changed = 0
for old, new in replacements.items():
    if old in text:
        text = text.replace(old, new)
        changed += 1
INDEX.write_text(text, encoding="utf-8")
print(f"Hidden apartment-id UI references: {changed}")
