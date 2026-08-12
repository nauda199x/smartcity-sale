"""Stage only public GitHub Pages files; never publish sources or maintenance code."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"
OUT.mkdir(exist_ok=True)
for child in list(OUT.iterdir()):
    shutil.rmtree(child) if child.is_dir() else child.unlink()

for pattern in ("*.html", "*.png", "*.ico"):
    for source in ROOT.glob(pattern):
        shutil.copy2(source, OUT / source.name)
for name in ("assets", "blog", "can-ho-dang-ban", "phan-khu", "images"):
    shutil.copytree(ROOT / name, OUT / name)
for name in ("CNAME", "robots.txt", "sitemap.xml", "site.webmanifest", "data.json"):
    shutil.copy2(ROOT / name, OUT / name)
print(f"staged {sum(1 for p in OUT.rglob('*') if p.is_file())} public files in _site")
