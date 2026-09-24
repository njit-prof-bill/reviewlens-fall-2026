"""URL-driven review collection for Google Maps (S1-020).

Google exposes no public API that returns a full review set, so reviews are
collected through a third-party provider. The HTTP transport is injectable so
tests replay a recorded response instead of calling the network.
"""

import json
import logging
import re
from collections.abc import Callable
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

from app.core.config import settings
from app.db.models import AnalysisTarget
from app.domain import IngestionErrorCode
from app.services.ingestion.base import IngestionError, IngestionResult, RawReview

logger = logging.getLogger(__name__)

SERPAPI_ENDPOINT = "https://serpapi.com/search.json"
DEFAULT_SORT_MODES = ("qualityScore", "newestFirst", "ratingLow", "ratingHigh")
SUPPORTED_SORT_MODES = frozenset(DEFAULT_SORT_MODES)
_DATA_ID = re.compile(r"!1s(0x[0-9a-fA-F]+:0x[0-9a-fA-F]+)")
_SHORT_HOSTS = {"maps.app.goo.gl", "goo.gl", "g.co"}

JsonFetcher = Callable[[str, float], dict[str, Any]]
UrlExpander = Callable[[str, float], str]


def _http_get_json(url: str, timeout: float) -> dict[str, Any]:
    request = Request(
        url=url,
        headers={"Accept": "application/json", "User-Agent": settings.app_name},
        method="GET",
    )
    with urlopen(request, timeout=timeout) as response:  # nosec: B310
        return json.loads(response.read().decode("utf-8"))


def _expand_short_url(url: str, timeout: float) -> str:
    request = Request(url=url, method="GET")
    with urlopen(request, timeout=timeout) as response:  # nosec: B310
        return response.geturl()


def extract_data_id(source_url: str) -> str | None:
    """Pull the Google place identifier embedded in a Maps place URL."""
    match = _DATA_ID.search(source_url)
    return match.group(1) if match else None


def _raise_for_transport(exc: Exception) -> IngestionError:
    if isinstance(exc, HTTPError):
        if exc.code == 429:
            return IngestionError(
                IngestionErrorCode.PROVIDER_QUOTA_EXCEEDED, f"HTTP {exc.code}"
            )
        return IngestionError(
            IngestionErrorCode.PROVIDER_UNAVAILABLE, f"HTTP {exc.code}"
        )
    if isinstance(exc, TimeoutError):
        return IngestionError(IngestionErrorCode.PROVIDER_TIMEOUT, str(exc))
    if isinstance(exc, URLError):
        reason = getattr(exc, "reason", None)
        if isinstance(reason, TimeoutError):
            return IngestionError(IngestionErrorCode.PROVIDER_TIMEOUT, str(exc))
        return IngestionError(IngestionErrorCode.PROVIDER_UNAVAILABLE, str(exc))
    if isinstance(exc, (json.JSONDecodeError, UnicodeDecodeError)):
        return IngestionError(IngestionErrorCode.SOURCE_UNPARSEABLE, str(exc))
    return IngestionError(IngestionErrorCode.UNEXPECTED_ERROR, str(exc))


def _map_review(entry: dict[str, Any]) -> RawReview:
    user = entry.get("user") or {}
    return RawReview(
        review_text=entry.get("snippet") or entry.get("extracted_snippet"),
        rating=entry.get("rating"),
        reviewer_name=user.get("name"),
        reviewed_at=entry.get("iso_date"),
        source_review_id=entry.get("review_id"),
        review_url=entry.get("link"),
        source_metadata={
            key: entry[key]
            for key in ("date", "likes", "source", "images")
            if entry.get(key) is not None
        },
    )


class GoogleMapsReviewProvider:
    """Collects Google Maps reviews through the SerpApi google_maps_reviews engine."""

    def __init__(
        self,
        api_key: str | None = None,
        max_reviews: int | None = None,
        sort_modes: tuple[str, ...] | list[str] | None = None,
        max_pages_per_mode: int | None = None,
        bypass_cache: bool | None = None,
        timeout: float | None = None,
        fetch_json: JsonFetcher = _http_get_json,
        expand_url: UrlExpander = _expand_short_url,
    ):
        self._api_key = (
            api_key if api_key is not None else settings.review_provider_api_key
        )
        self._max_reviews = max_reviews or settings.review_fetch_max
        configured_modes = sort_modes or settings.review_fetch_sort_modes
        self._sort_modes = (
            tuple(mode for mode in configured_modes if mode in SUPPORTED_SORT_MODES)
            or DEFAULT_SORT_MODES
        )
        self._max_pages_per_mode = (
            max_pages_per_mode or settings.review_fetch_max_pages_per_mode
        )
        self._bypass_cache = (
            settings.review_fetch_bypass_cache if bypass_cache is None else bypass_cache
        )
        self._timeout = timeout or settings.review_provider_timeout_seconds
        self._fetch_json = fetch_json
        self._expand_url = expand_url

    def fetch(self, target: AnalysisTarget) -> IngestionResult:
        if not self._api_key:
            raise IngestionError(
                IngestionErrorCode.PROVIDER_NOT_CONFIGURED,
                "REVIEW_PROVIDER_API_KEY is not set",
            )

        data_id = self._resolve_data_id(target.source_url)
        collected: list[RawReview] = []
        entity_name: str | None = None

        for sort_mode in self._sort_modes:
            next_page_token: str | None = None
            for _ in range(self._max_pages_per_mode):
                if len(collected) >= self._max_reviews:
                    break

                payload = self._request_page(data_id, next_page_token, sort_mode)
                if entity_name is None:
                    title = (payload.get("place_info") or {}).get("title")
                    if isinstance(title, str) and title.strip():
                        entity_name = title.strip()
                entries = payload.get("reviews") or []
                if not entries:
                    break

                collected.extend(_map_review(entry) for entry in entries)

                next_page_token = (payload.get("serpapi_pagination") or {}).get(
                    "next_page_token"
                )
                if not next_page_token:
                    break

        if not collected:
            raise IngestionError(IngestionErrorCode.NO_REVIEWS_AVAILABLE)

        return IngestionResult(
            reviews=collected[: self._max_reviews], entity_name=entity_name
        )

    def _resolve_data_id(self, source_url: str) -> str:
        url = source_url
        if (urlparse(url).hostname or "").lower() in _SHORT_HOSTS:
            try:
                url = self._expand_url(url, self._timeout)
            except Exception as exc:
                raise _raise_for_transport(exc) from exc

        data_id = extract_data_id(url)
        if not data_id:
            raise IngestionError(
                IngestionErrorCode.PLACE_NOT_FOUND,
                "No data_id found in the Google Maps URL",
            )
        return data_id

    def _request_page(
        self, data_id: str, next_page_token: str | None, sort_mode: str
    ) -> dict[str, Any]:
        params = {
            "engine": "google_maps_reviews",
            "data_id": data_id,
            "api_key": self._api_key,
            "sort_by": sort_mode,
        }
        if next_page_token:
            params["next_page_token"] = next_page_token
        if self._bypass_cache:
            params["no_cache"] = "true"

        url = f"{SERPAPI_ENDPOINT}?{urlencode(params)}"
        try:
            payload = self._fetch_json(url, self._timeout)
        except Exception as exc:
            error = _raise_for_transport(exc)
            logger.warning("Review provider request failed: %s", error.technical_detail)
            raise error from exc

        provider_error = payload.get("error")
        if provider_error:
            logger.warning("Review provider returned an error: %s", provider_error)
            raise IngestionError(
                IngestionErrorCode.PLACE_NOT_FOUND, str(provider_error)
            )

        return payload
