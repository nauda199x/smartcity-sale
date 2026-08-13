from __future__ import annotations

import io
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from media_utils import safe_zip_members, slugify  # noqa: E402


def jpeg(color=(30, 90, 150), size=(1200, 800)) -> bytes:
    stream = io.BytesIO()
    Image.new("RGB", size, color).save(stream, "JPEG", quality=90)
    return stream.getvalue()


class MediaPipelineTests(unittest.TestCase):
    def test_slugify_is_ascii_and_stable(self):
        self.assertEqual(slugify("Bể bơi Lumière 01"), "be-boi-lumiere-01")

    def test_safe_reader_rejects_traversal_and_nested_archive(self):
        with tempfile.TemporaryDirectory() as temporary:
            archive = Path(temporary) / "unsafe.zip"
            with zipfile.ZipFile(archive, "w") as output:
                output.writestr("../escape.jpg", jpeg())
                output.writestr("nested.zip", b"not relevant")
                output.writestr("good/photo.jpg", jpeg())
            members, skipped, _ = safe_zip_members(archive)
            self.assertEqual([item.original_name for item in members], ["photo.jpg"])
            self.assertEqual({item["reason"] for item in skipped}, {"unsafe-path", "unsupported-format"})

    def test_cli_generates_variants_manifest_and_filters_duplicate(self):
        slug = "fixture-media-test"
        output = ROOT / "images" / "projects" / slug
        manifest = ROOT / "data" / "media" / f"{slug}.json"
        preview = ROOT / "data" / "media" / "previews" / f"{slug}-contact-sheet.jpg"
        with tempfile.TemporaryDirectory() as temporary:
            archive = Path(temporary) / "fixture.zip"
            same = jpeg()
            with zipfile.ZipFile(archive, "w") as target:
                target.writestr("IMG_001.jpg", same)
                target.writestr("copy.jpg", same)
                target.writestr("pool-view.jpg", jpeg((20, 130, 180), (2000, 1200)))
            try:
                result = subprocess.run(
                    [sys.executable, str(ROOT / "tools/process_media_pack.py"), "--input", str(archive),
                     "--slug", slug, "--type", "project", "--force"],
                    cwd=ROOT, text=True, capture_output=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                data = json.loads(manifest.read_text())
                self.assertEqual(len(data["assets"]), 2)
                self.assertEqual(len(data["duplicates"]), 1)
                self.assertEqual(set(data["assets"][0]["variants"]), {"hero", "content", "card", "thumb"})
                self.assertTrue(all((ROOT / path.lstrip("/")).is_file()
                                    for asset in data["assets"] for path in asset["variants"].values()))
                self.assertEqual(data["assets"][1]["role"], "pool")
                validation = subprocess.run(
                    [sys.executable, str(ROOT / "tools/validate_media.py"), "--slug", slug], cwd=ROOT)
                self.assertEqual(validation.returncode, 0)
            finally:
                import shutil
                shutil.rmtree(output, ignore_errors=True)
                manifest.unlink(missing_ok=True)
                preview.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
