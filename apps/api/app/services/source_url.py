"""Validation for the single supported review platform (S1-BR-012)."""

import re
from urllib.parse import unquote, urlparse

from app.domain import ReviewPlatform
from app.errors import AppValidationError
from app.schemas import ApiErrorDetail

_GOOGLE_HOST = re.compile(r"^(www\.|maps\.)?google(\.[a-z]{2,3}){1,2}$")
_GOOGLE_SHORT_HOSTS = {"maps.app.goo.gl", "goo.gl", "g.co"}
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

    if not _GOOGLE_HOST.match(host):
        _reject("ReviewLens currently supports Google Maps links only.")

    if not parsed.path.startswith("/maps"):
        _reject(
            "That Google link is not a Google Maps place. Open the business on Google Maps and copy the link."
        )

    return candidate


def detect_platform(source_url: str) -> ReviewPlatform:
    """Only one platform is supported, so validation alone determines it."""
    validate_source_url(source_url)
    return ReviewPlatform.GOOGLE_MAPS


def derive_working_name(source_url: str) -> str | None:
    """Best-effort display name from a Google Maps place slug (UX ref 3.2)."""
    match = _PLACE_SEGMENT.search(urlparse(source_url).path)
    if not match:
        return None

    slug = unquote(match.group(1)).replace("+", " ").strip()
    return slug or None
