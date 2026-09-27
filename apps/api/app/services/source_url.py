"""Validation and detection for supported review-platform URLs."""

import re
from urllib.parse import unquote, urlparse

from app.domain import ReviewPlatform
from app.errors import AppValidationError
from app.schemas import ApiErrorDetail

_GOOGLE_HOST = re.compile(r"^(www\.|maps\.)?google(\.[a-z]{2,3}){1,2}$")
_GOOGLE_SHORT_HOSTS = {"maps.app.goo.gl", "goo.gl", "g.co"}
_AMAZON_HOSTS = {"amazon.com", "www.amazon.com"}
_AMAZON_ASIN = re.compile(r"/(?:dp|gp/product)/([A-Z0-9]{10})(?:[/?]|$)", re.IGNORECASE)
_AMAZON_SLUG_ASIN = re.compile(r"/[^/]+/dp/([A-Z0-9]{10})(?:[/?]|$)", re.IGNORECASE)
_PLACE_SEGMENT = re.compile(r"/place/([^/@]+)")


def _reject(issue: str) -> None:
    raise AppValidationError(
        "The review source is not valid",
        [ApiErrorDetail(field="source_url", issue=issue)],
    )


def validate_source_url(raw_url: str) -> str:
    """Return the normalized source URL, or raise AppValidationError."""
    candidate = (raw_url or "").strip()
    if not candidate:
        _reject("A review source URL is required.")

    try:
        parsed = urlparse(candidate)
    except ValueError:
        _reject("That does not look like a valid web address.")

    if parsed.scheme not in {"http", "https"}:
        _reject("The review source must be a http:// or https:// web address.")

    host = (parsed.hostname or "").lower()
    if not host:
        _reject("That does not look like a valid web address.")

    if host in _GOOGLE_SHORT_HOSTS:
        return candidate

    if host in _AMAZON_HOSTS:
        if not (
            _AMAZON_ASIN.search(parsed.path) or _AMAZON_SLUG_ASIN.search(parsed.path)
        ):
            _reject(
                "Paste an Amazon.com product link that contains a product ASIN, such as /dp/B012345678."
            )
        return candidate

    if not _GOOGLE_HOST.match(host):
        _reject(
            "ReviewLens supports Google Maps place links and Amazon.com product links."
        )

    if not parsed.path.startswith("/maps"):
        _reject(
            "That Google link is not a Google Maps place. Open the business on Google Maps and copy the link."
        )

    return candidate


def detect_platform(source_url: str) -> ReviewPlatform:
    """Identify the supported platform after validating its URL shape."""
    normalized_url = validate_source_url(source_url)
    host = (urlparse(normalized_url).hostname or "").lower()
    if host in _AMAZON_HOSTS:
        return ReviewPlatform.AMAZON
    return ReviewPlatform.GOOGLE_MAPS


def extract_amazon_asin(source_url: str) -> str | None:
    parsed = urlparse(source_url)
    if (parsed.hostname or "").lower() not in _AMAZON_HOSTS:
        return None
    match = _AMAZON_ASIN.search(parsed.path) or _AMAZON_SLUG_ASIN.search(parsed.path)
    return match.group(1).upper() if match else None


def derive_working_name(source_url: str) -> str | None:
    """Best-effort display name from a Maps place or Amazon product URL."""
    parsed = urlparse(source_url)
    host = (parsed.hostname or "").lower()
    if host in _AMAZON_HOSTS:
        asin = extract_amazon_asin(source_url)
        return f"Amazon Product {asin}" if asin else None

    match = _PLACE_SEGMENT.search(parsed.path)
    if not match:
        return None
    slug = unquote(match.group(1)).replace("+", " ").strip()
    return slug or None
