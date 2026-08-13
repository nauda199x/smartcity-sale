import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from public_images import public_inventory_image  # noqa: E402


class PublicImageTests(unittest.TestCase):
    def test_canonicalizes_approved_drive_thumbnail(self):
        value = "https://drive.google.com/thumbnail?id=abc_123&sz=w9999"
        self.assertEqual(public_inventory_image(value), "https://drive.google.com/thumbnail?id=abc_123&amp;sz=w1200")

    def test_rejects_arbitrary_and_malformed_sources(self):
        for value in ("javascript:alert(1)", "data:image/svg+xml,x", "http://drive.google.com/thumbnail?id=x", "https://evil.example/a.jpg", "https://drive.google.com/file?id=x", ""):
            with self.subTest(value=value):
                self.assertEqual(public_inventory_image(value), "")


if __name__ == "__main__":
    unittest.main()
