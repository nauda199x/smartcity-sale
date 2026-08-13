from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from PIL import Image

from tools.import_drive_media import approved_images


class DriveMediaImportTests(unittest.TestCase):
    def test_approved_images_checks_content_and_limits(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            Image.new("RGB", (20, 20), "blue").save(root / "photo.jpg")
            self.assertEqual(approved_images(root, 1, 1_000_000, 1_000_000),
                             [root / "photo.jpg"])

    def test_rejects_unsupported_remote_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "payload.exe").write_bytes(b"MZ")
            with self.assertRaisesRegex(ValueError, "unsupported"):
                approved_images(root, 200, 1_000_000, 2_000_000)

    def test_rejects_extension_content_mismatch(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            Image.new("RGB", (20, 20), "blue").save(root / "wrong.png", format="JPEG")
            with self.assertRaisesRegex(ValueError, "mismatch"):
                approved_images(root, 200, 1_000_000, 2_000_000)


if __name__ == "__main__":
    unittest.main()
