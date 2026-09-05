"""URL-driven collection against a recorded provider response (S1-020).

No test in this module touches the network.
"""

import json
from pathlib import Path
from urllib.error import HTTPError, URLError

import pytest
from app.db.models import AnalysisTarget
from app.domain import IngestionErrorCode
from app.services.ingestion.base import IngestionError
from app.services.ingestion.sources.google_maps_provider import (
    GoogleMapsReviewProvider,
    extract_data_id,
)

FIXTURES = Path(__file__).parent / "fixtures"
PLACE_URL = (
    "https://www.google.com/maps/place/Blue+Bottle+Coffee/"
    "@37.7823,-122.4074,17z/data=!4m6!3m5!1s0x8085808f0b0b0b0b:0x1234abcd"
)


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


@pytest.fixture()
def target() -> AnalysisTarget:
    return AnalysisTarget(
        name="Blue Bottle Coffee", platform="google_maps", source_url=PLACE_URL
    )


def _recorded_transport(*payloads):
    responses = list(payloads)

    def _fetch(url: str, timeout: float) -> dict:
        return responses.pop(0) if responses else {"reviews": []}

    return _fetch


class TestExtractDataId:
    def test_reads_the_place_identifier_from_a_maps_url(self):
        assert extract_data_id(PLACE_URL) == "0x8085808f0b0b0b0b:0x1234abcd"

    def test_returns_none_when_the_url_has_no_identifier(self):
        assert extract_data_id("https://www.google.com/maps/place/Cafe") is None


class TestSuccessfulCollection:
    def test_maps_a_recorded_response_onto_raw_reviews(self, target):
        provider = GoogleMapsReviewProvider(
            api_key="test-key",
            fetch_json=_recorded_transport(
                _load("serpapi_google_maps_reviews_page1.json"),
                _load("serpapi_google_maps_reviews_page2.json"),
            ),
        )

        reviews = provider.fetch(target)

        assert len(reviews) == 6
        first = reviews[0]
        assert first.review_text.startswith("The pour over here")
        assert first.rating == 5
        assert first.reviewer_name == "Dana Whitfield"
        assert first.source_review_id == "ChZDSUhNMG9nS0VJQ0FnSUR"

    def test_stops_at_the_configured_maximum(self, target):
        provider = GoogleMapsReviewProvider(
            api_key="test-key",
            max_reviews=3,
            fetch_json=_recorded_transport(
                _load("serpapi_google_maps_reviews_page1.json")
            ),
        )

        assert len(provider.fetch(target)) == 3

    def test_expands_a_short_link_before_resolving_the_place(self):
        short_target = AnalysisTarget(
            name="Blue Bottle Coffee",
            platform="google_maps",
            source_url="https://maps.app.goo.gl/AbCdEfGh123",
        )
        provider = GoogleMapsReviewProvider(
            api_key="test-key",
            fetch_json=_recorded_transport(
                _load("serpapi_google_maps_reviews_page2.json")
            ),
            expand_url=lambda url, timeout: PLACE_URL,
        )

        assert len(provider.fetch(short_target)) == 2


class TestFailureMapping:
    def test_missing_api_key_is_reported_as_not_configured(self, target):
        provider = GoogleMapsReviewProvider(api_key="")

        with pytest.raises(IngestionError) as exc_info:
            provider.fetch(target)

        assert exc_info.value.code == IngestionErrorCode.PROVIDER_NOT_CONFIGURED

    def test_a_url_without_a_place_identifier_is_place_not_found(self):
        provider = GoogleMapsReviewProvider(api_key="test-key")
        bare = AnalysisTarget(
            name="Cafe",
            platform="google_maps",
            source_url="https://www.google.com/maps/place/Cafe",
        )

        with pytest.raises(IngestionError) as exc_info:
            provider.fetch(bare)

        assert exc_info.value.code == IngestionErrorCode.PLACE_NOT_FOUND

    def test_rate_limiting_is_reported_as_quota_exceeded(self, target):
        def _fetch(url, timeout):
            raise HTTPError(url, 429, "Too Many Requests", {}, None)

        provider = GoogleMapsReviewProvider(api_key="test-key", fetch_json=_fetch)

        with pytest.raises(IngestionError) as exc_info:
            provider.fetch(target)

        assert exc_info.value.code == IngestionErrorCode.PROVIDER_QUOTA_EXCEEDED

    def test_a_server_error_is_reported_as_provider_unavailable(self, target):
        def _fetch(url, timeout):
            raise HTTPError(url, 503, "Service Unavailable", {}, None)

        provider = GoogleMapsReviewProvider(api_key="test-key", fetch_json=_fetch)

        with pytest.raises(IngestionError) as exc_info:
            provider.fetch(target)

        assert exc_info.value.code == IngestionErrorCode.PROVIDER_UNAVAILABLE

    def test_a_timeout_is_reported_as_provider_timeout(self, target):
        def _fetch(url, timeout):
            raise URLError(TimeoutError("timed out"))

        provider = GoogleMapsReviewProvider(api_key="test-key", fetch_json=_fetch)

        with pytest.raises(IngestionError) as exc_info:
            provider.fetch(target)

        assert exc_info.value.code == IngestionErrorCode.PROVIDER_TIMEOUT

    def test_a_provider_error_payload_is_place_not_found(self, target):
        provider = GoogleMapsReviewProvider(
            api_key="test-key",
            fetch_json=_recorded_transport(
                {"error": "Google Maps hasn't returned any results"}
            ),
        )

        with pytest.raises(IngestionError) as exc_info:
            provider.fetch(target)

        assert exc_info.value.code == IngestionErrorCode.PLACE_NOT_FOUND

    def test_an_empty_result_set_is_reported_rather_than_faked(self, target):
        provider = GoogleMapsReviewProvider(
            api_key="test-key", fetch_json=_recorded_transport({"reviews": []})
        )

        with pytest.raises(IngestionError) as exc_info:
            provider.fetch(target)

        assert exc_info.value.code == IngestionErrorCode.NO_REVIEWS_AVAILABLE

    def test_the_user_facing_message_never_leaks_provider_detail(self, target):
        def _fetch(url, timeout):
            raise HTTPError(url, 401, "Invalid API key sk_live_secret", {}, None)

        provider = GoogleMapsReviewProvider(api_key="test-key", fetch_json=_fetch)

        with pytest.raises(IngestionError) as exc_info:
            provider.fetch(target)

        assert "sk_live_secret" not in exc_info.value.message
