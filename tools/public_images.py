"""Shared allowlist for public inventory images rendered into generated HTML."""
from urllib.parse import parse_qs, quote, urlparse

PUBLIC_IMAGE_HOST = "drive.google.com"


def public_inventory_image(value: object) -> str:
    """Return a canonical approved Drive thumbnail URL, or an empty string."""
    parsed = urlparse(str(value or "").strip())
    image_id = parse_qs(parsed.query).get("id", [""])[0]
    if parsed.scheme != "https" or parsed.netloc != PUBLIC_IMAGE_HOST:
        return ""
    if parsed.path != "/thumbnail" or not image_id:
        return ""
    return f"https://{PUBLIC_IMAGE_HOST}/thumbnail?id={quote(image_id, safe='')}&amp;sz=w1200"
