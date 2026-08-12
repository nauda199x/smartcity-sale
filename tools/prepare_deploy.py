"""Stage only public GitHub Pages files; never publish sources or maintenance code."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"

# Audit result: no current page or script loads a file below /data/. Keep this
# allowlist explicit so data/official source manifests can never be published by
# accidentally copying the directory wholesale. Add a path here only when it is a
# documented browser runtime dependency and has been reviewed for public fields.
PUBLIC_DATA_FILES: tuple[str, ...] = ()
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
for name in PUBLIC_DATA_FILES:
    source = ROOT / "data" / name
    destination = OUT / "data" / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
print(f"staged {sum(1 for p in OUT.rglob('*') if p.is_file())} public files in _site")
