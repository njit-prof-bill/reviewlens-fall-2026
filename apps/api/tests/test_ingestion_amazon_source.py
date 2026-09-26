"""Amazon product review collection using a recorded SerpApi response."""

import json
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlparse

import pytest
from app.db.models import AnalysisTarget
from app.domain import IngestionErrorCode
from app.services.ingestion.base import (
    FallbackReviewSource,
    IngestionError,
    IngestionResult,
)
from app.services.ingestion.sources.amazon_provider import AmazonProductReviewProvider
from app.services.ingestion.sources.provider_factory import create_url_review_source

FIXTURE = Path(__file__).parent / "fixtures/serpapi_amazon_product_reviews.json"
PRODUCT_URL = "https://www.amazon.com/Example-Headphones/dp/B012345678"


def _payload():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _target(url=PRODUCT_URL):
    return AnalysisTarget(
        name="Amazon Product B012345678", platform="amazon", source_url=url
    )


class TestAmazonProductReviewProvider:
    def test_requests_product_reviews_by_asin_and_maps_individual_reviews(self):
        requested = []

        def fetch(url, timeout):
            requested.append(url)
            return _payload()

        provider = AmazonProductReviewProvider(
            api_key="test-key", fetch_json=fetch, bypass_cache=True
        )

        result = provider.fetch(_target())

        params = parse_qs(urlparse(requested[0]).query)
        assert params["engine"] == ["amazon_product"]
        assert params["asin"] == ["B012345678"]
        assert params["amazon_domain"] == ["amazon.com"]
        assert params["no_cache"] == ["true"]
        assert result.entity_name == "Example Wireless Headphones"
        assert len(result.reviews) == 2
        first = result.reviews[0]
        assert first.review_text == (
            "Comfortable for long sessions\n\n"
            "The ear cups remain comfortable during long calls."
        )
        assert first.rating == 5.0
        assert first.source_review_id is None
        assert first.review_url is None
        assert first.reviewed_at == "2026-07-15"
        assert "Provider-generated summary" not in first.review_text

    def test_respects_the_configured_review_limit(self):
        provider = AmazonProductReviewProvider(
            api_key="test-key", max_reviews=1, fetch_json=lambda *_: _payload()
        )

        assert len(provider.fetch(_target()).reviews) == 1

    def test_missing_api_key_is_reported_as_not_configured(self):
        provider = AmazonProductReviewProvider(api_key="")

        with pytest.raises(IngestionError) as exc_info:
            provider.fetch(_target())

        assert exc_info.value.code == IngestionErrorCode.PROVIDER_NOT_CONFIGURED

    def test_unusable_product_url_is_reported_as_product_not_found(self):
        provider = AmazonProductReviewProvider(api_key="test-key")

        with pytest.raises(IngestionError) as exc_info:
            provider.fetch(_target("https://www.amazon.com/s?k=headphones"))

        assert exc_info.value.code == IngestionErrorCode.PRODUCT_NOT_FOUND

    def test_empty_authored_reviews_are_not_replaced_with_a_summary(self):
        payload = {"product_results": {"title": "Example"}, "reviews_information": {}}
        provider = AmazonProductReviewProvider(
            api_key="test-key", fetch_json=lambda *_: payload
        )

        with pytest.raises(IngestionError) as exc_info:
            provider.fetch(_target())

        assert exc_info.value.code == IngestionErrorCode.NO_REVIEWS_AVAILABLE

    def test_http_rate_limit_maps_to_provider_quota_exceeded(self):
        def fetch(url, timeout):
            raise HTTPError(url, 429, "Too Many Requests", {}, None)

        provider = AmazonProductReviewProvider(api_key="test-key", fetch_json=fetch)

        with pytest.raises(IngestionError) as exc_info:
            provider.fetch(_target())

        assert exc_info.value.code == IngestionErrorCode.PROVIDER_QUOTA_EXCEEDED


class TestProviderSelection:
    def test_factory_selects_a_provider_for_each_supported_platform(self):
        assert isinstance(
            create_url_review_source("amazon"), AmazonProductReviewProvider
        )
        assert (
            create_url_review_source("google_maps").__class__.__name__
            == "GoogleMapsReviewProvider"
        )

    def test_fallback_uses_the_next_vendor_after_a_transient_error(self):
        class FailingSource:
            def fetch(self, target):
                raise IngestionError(IngestionErrorCode.PROVIDER_UNAVAILABLE)

        class WorkingSource:
            def fetch(self, target):
                return IngestionResult([])

        result = FallbackReviewSource([FailingSource(), WorkingSource()]).fetch(
            _target()
        )

        assert result.reviews == []

    def test_fallback_does_not_hide_product_errors(self):
        class InvalidProductSource:
            def fetch(self, target):
                raise IngestionError(IngestionErrorCode.PRODUCT_NOT_FOUND)

        class MustNotRunSource:
            def fetch(self, target):
                raise AssertionError("fallback should not run for an invalid product")

        with pytest.raises(IngestionError) as exc_info:
            FallbackReviewSource([InvalidProductSource(), MustNotRunSource()]).fetch(
                _target()
            )

        assert exc_info.value.code == IngestionErrorCode.PRODUCT_NOT_FOUND
