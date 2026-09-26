"""URL-driven Amazon review collection through SerpApi's Amazon Product API."""

import re
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlencode, urlparse

from app.core.config import settings
from app.db.models import AnalysisTarget
from app.domain import IngestionErrorCode
from app.services.ingestion.base import IngestionError, IngestionResult, RawReview
from app.services.ingestion.sources.google_maps_provider import (
    SERPAPI_ENDPOINT,
    JsonFetcher,
    _http_get_json,
    _raise_for_transport,
)
from app.services.source_url import extract_amazon_asin

_REVIEW_ID = re.compile(
    r"/(?:gp/customer-reviews|portal/customer-reviews)/([A-Z0-9]+)", re.IGNORECASE
)


def _parse_date(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    for date_format in ("%B %d, %Y", "%b %d, %Y", "%Y-%m-%d"):
        try:
            return (
                datetime.strptime(value.strip(), date_format)
                .replace(tzinfo=UTC)
                .date()
                .isoformat()
            )
        except ValueError:
            continue
    return None


def _map_review(entry: dict[str, Any]) -> RawReview:
    title = entry.get("title")
    body = entry.get("text")
    review_text = "\n\n".join(
        part.strip() for part in (title, body) if isinstance(part, str) and part.strip()
    )
    review_url = entry.get("link") or entry.get("review_url")
    match = (
        _REVIEW_ID.search(urlparse(review_url).path)
        if isinstance(review_url, str)
        else None
    )
    return RawReview(
        review_text=review_text or None,
        rating=entry.get("rating"),
        reviewer_name=entry.get("author"),
        reviewed_at=_parse_date(entry.get("date")),
        source_review_id=match.group(1) if match else None,
        review_url=review_url,
        source_metadata={
            key: entry[key]
            for key in ("verified_purchase", "helpful_votes", "product")
            if entry.get(key) is not None
        },
    )


class AmazonProductReviewProvider:
    """Collects individual Amazon reviews returned with product details."""

    def __init__(
        self,
        api_key: str | None = None,
        max_reviews: int | None = None,
        bypass_cache: bool | None = None,
        timeout: float | None = None,
        fetch_json: JsonFetcher = _http_get_json,
    ):
        self._api_key = (
            api_key if api_key is not None else settings.review_provider_api_key
        )
        self._max_reviews = max_reviews or settings.review_fetch_max
        self._bypass_cache = (
            settings.review_fetch_bypass_cache if bypass_cache is None else bypass_cache
        )
        self._timeout = timeout or settings.review_provider_timeout_seconds
        self._fetch_json = fetch_json

    def fetch(self, target: AnalysisTarget) -> IngestionResult:
        if not self._api_key:
            raise IngestionError(
                IngestionErrorCode.PROVIDER_NOT_CONFIGURED,
                "REVIEW_PROVIDER_API_KEY is not set",
            )

        asin = extract_amazon_asin(target.source_url)
        if not asin:
            raise IngestionError(IngestionErrorCode.PRODUCT_NOT_FOUND)

        params = {
            "engine": "amazon_product",
            "asin": asin,
            "amazon_domain": "amazon.com",
            "api_key": self._api_key,
        }
        if self._bypass_cache:
            params["no_cache"] = "true"
        url = f"{SERPAPI_ENDPOINT}?{urlencode(params)}"
        try:
            payload = self._fetch_json(url, self._timeout)
        except Exception as exc:
            error = _raise_for_transport(exc)
            raise error from exc

        if payload.get("error"):
            raise IngestionError(
                IngestionErrorCode.PRODUCT_NOT_FOUND, str(payload["error"])
            )

        product = payload.get("product_results") or {}
        if not product:
            raise IngestionError(IngestionErrorCode.PRODUCT_NOT_FOUND)

        reviews_information = payload.get("reviews_information") or {}
        entries = reviews_information.get("authors_reviews") or []
        if not entries:
            raise IngestionError(IngestionErrorCode.NO_REVIEWS_AVAILABLE)

        reviews = [_map_review(entry) for entry in entries[: self._max_reviews]]
        return IngestionResult(
            reviews=reviews,
            entity_name=(
                product.get("title") if isinstance(product.get("title"), str) else None
            ),
        )
