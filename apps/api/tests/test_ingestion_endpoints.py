"""Ingestion endpoints, result state, and ownership (S1-013, S1-019, S1-022, S1-023)."""

import json
import uuid
from pathlib import Path

import pytest
from app.domain import IngestionErrorCode
from app.routers import ingestion as ingestion_router
from app.services.ingestion.base import IngestionError, IngestionResult, RawReview

FIXTURES = Path(__file__).parent / "fixtures"
VALID_URL = (
    "https://www.google.com/maps/place/Blue+Bottle+Coffee/"
    "@37.7823,-122.4074,17z/data=!4m6!3m5!1s0x8085808f0b0b0b0b:0x1234abcd"
)


class StubProvider:
    """Stands in for the third-party provider so tests never hit the network."""

    def __init__(self, reviews=None, error=None, entity_name=None):
        self._reviews = reviews or []
        self._error = error
        self._entity_name = entity_name

    def fetch(self, target):
        if self._error:
            raise self._error
        return IngestionResult(self._reviews, self._entity_name)


def _use_provider(monkeypatch, provider):
    monkeypatch.setattr(ingestion_router, "GoogleMapsReviewProvider", lambda: provider)


def _recorded_reviews():
    page = json.loads(
        (FIXTURES / "serpapi_google_maps_reviews_page1.json").read_text("utf-8")
    )
    return [
        RawReview(
            review_text=entry["snippet"],
            rating=entry["rating"],
            reviewer_name=entry["user"]["name"],
            reviewed_at=entry.get("iso_date"),
            source_review_id=entry["review_id"],
        )
        for entry in page["reviews"]
    ]


def _create_target(client, name="Blue Bottle Coffee", source_url=VALID_URL):
    return client.post(
        "/api/v1/analysis-targets", json={"name": name, "source_url": source_url}
    ).json()


@pytest.fixture()
def target_a(client_factory, user_a):
    return _create_target(client_factory(user_a))


class TestUrlIngestion:
    def test_successful_run_persists_the_collected_reviews(
        self, client_factory, user_a, target_a, monkeypatch
    ):
        _use_provider(monkeypatch, StubProvider(_recorded_reviews()))
        client = client_factory(user_a)

        started = client.post(f"/api/v1/analysis-targets/{target_a['id']}/ingestions")

        assert started.status_code == 202
        run = client.get(f"/api/v1/ingestion-runs/{started.json()['id']}").json()
        assert run["status"] == "succeeded"
        assert run["reviews_ingested"] == 4
        assert run["reviews_rejected"] == 0
        assert run["error_code"] is None

    def test_provider_title_replaces_the_short_link_placeholder(
        self, client_factory, user_a, monkeypatch
    ):
        client = client_factory(user_a)
        target = _create_target(
            client,
            name="Untitled Analysis",
            source_url="https://maps.app.goo.gl/AbCdEfGh123",
        )
        _use_provider(
            monkeypatch,
            StubProvider(_recorded_reviews(), entity_name="Blue Bottle Coffee"),
        )

        client.post(f"/api/v1/analysis-targets/{target['id']}/ingestions")

        updated = client.get(f"/api/v1/analysis-targets/{target['id']}").json()
        assert updated["name"] == "Blue Bottle Coffee"

    def test_provider_title_does_not_replace_an_existing_name(
        self, client_factory, user_a, target_a, monkeypatch
    ):
        _use_provider(
            monkeypatch,
            StubProvider(_recorded_reviews(), entity_name="Provider Name"),
        )
        client = client_factory(user_a)

        client.post(f"/api/v1/analysis-targets/{target_a['id']}/ingestions")

        updated = client.get(f"/api/v1/analysis-targets/{target_a['id']}").json()
        assert updated["name"] == "Blue Bottle Coffee"

    def test_persisted_reviews_match_the_normalized_input(
        self, client_factory, user_a, target_a, monkeypatch
    ):
        _use_provider(monkeypatch, StubProvider(_recorded_reviews()))
        client = client_factory(user_a)
        client.post(f"/api/v1/analysis-targets/{target_a['id']}/ingestions")

        reviews = client.get(
            f"/api/v1/analysis-targets/{target_a['id']}/reviews"
        ).json()

        assert reviews["total"] == 4
        texts = [item["review_text"] for item in reviews["items"]]
        assert (
            "The pour over here is consistently excellent and the staff remember regulars by name."
            in texts
        )
        assert all(1.0 <= item["rating"] <= 5.0 for item in reviews["items"])

    def test_reviews_stay_attached_to_their_own_target(
        self, client_factory, user_a, target_a, monkeypatch
    ):
        _use_provider(monkeypatch, StubProvider(_recorded_reviews()))
        client = client_factory(user_a)
        other = _create_target(
            client,
            name="Downtown Hotel",
            source_url="https://www.google.com/maps/place/Downtown+Hotel/@40.7,-74.0,17z",
        )
        client.post(f"/api/v1/analysis-targets/{target_a['id']}/ingestions")

        other_reviews = client.get(
            f"/api/v1/analysis-targets/{other['id']}/reviews"
        ).json()

        assert other_reviews["total"] == 0

    def test_a_partial_run_reports_both_counts(
        self, client_factory, user_a, target_a, monkeypatch
    ):
        _use_provider(
            monkeypatch,
            StubProvider(
                [
                    RawReview(review_text="Usable.", rating=5),
                    RawReview(review_text=None, rating=5),
                    RawReview(review_text="No rating.", rating=None),
                ]
            ),
        )
        client = client_factory(user_a)

        started = client.post(f"/api/v1/analysis-targets/{target_a['id']}/ingestions")
        run = client.get(f"/api/v1/ingestion-runs/{started.json()['id']}").json()

        assert run["status"] == "partial"
        assert run["reviews_ingested"] == 1
        assert run["reviews_rejected"] == 2
        assert run["rejection_reasons"] == {
            "missing_review_text": 1,
            "missing_or_invalid_rating": 1,
        }

    def test_reingestion_merges_new_reviews_and_skips_source_duplicates(
        self, client_factory, user_a, target_a, monkeypatch
    ):
        client = client_factory(user_a)
        initial = [
            RawReview(review_text="First review", rating=5, source_review_id="first"),
            RawReview(review_text="Second review", rating=4, source_review_id="second"),
        ]
        _use_provider(monkeypatch, StubProvider(initial))
        client.post(f"/api/v1/analysis-targets/{target_a['id']}/ingestions")

        refreshed = initial + [
            RawReview(review_text="Third review", rating=3, source_review_id="third")
        ]
        _use_provider(monkeypatch, StubProvider(refreshed))
        started = client.post(f"/api/v1/analysis-targets/{target_a['id']}/ingestions")
        run = client.get(f"/api/v1/ingestion-runs/{started.json()['id']}").json()
        reviews = client.get(
            f"/api/v1/analysis-targets/{target_a['id']}/reviews"
        ).json()

        assert run["status"] == "succeeded"
        assert run["reviews_ingested"] == 1
        assert run["reviews_duplicate"] == 2
        assert reviews["total"] == 3

    def test_reingestion_deduplicates_records_without_source_ids(
        self, client_factory, user_a, target_a, monkeypatch
    ):
        client = client_factory(user_a)
        provider = StubProvider(
            [RawReview(review_text="Quiet room", rating=5, reviewer_name="Pat")]
        )
        _use_provider(monkeypatch, provider)
        client.post(f"/api/v1/analysis-targets/{target_a['id']}/ingestions")
        started = client.post(f"/api/v1/analysis-targets/{target_a['id']}/ingestions")
        run = client.get(f"/api/v1/ingestion-runs/{started.json()['id']}").json()

        assert run["reviews_ingested"] == 0
        assert run["reviews_duplicate"] == 1
        assert (
            client.get(f"/api/v1/analysis-targets/{target_a['id']}/reviews").json()[
                "total"
            ]
            == 1
        )


class TestIngestionFailure:
    def test_a_provider_failure_is_recorded_without_fabricating_reviews(
        self, client_factory, user_a, target_a, monkeypatch
    ):
        _use_provider(
            monkeypatch,
            StubProvider(
                error=IngestionError(
                    IngestionErrorCode.PROVIDER_UNAVAILABLE, "HTTP 503 upstream"
                )
            ),
        )
        client = client_factory(user_a)

        started = client.post(f"/api/v1/analysis-targets/{target_a['id']}/ingestions")
        run = client.get(f"/api/v1/ingestion-runs/{started.json()['id']}").json()

        assert run["status"] == "failed"
        assert run["error_code"] == "provider_unavailable"
        assert run["reviews_ingested"] == 0
        assert (
            client.get(f"/api/v1/analysis-targets/{target_a['id']}/reviews").json()[
                "total"
            ]
            == 0
        )

    def test_the_user_facing_message_hides_technical_detail(
        self, client_factory, user_a, target_a, monkeypatch
    ):
        _use_provider(
            monkeypatch,
            StubProvider(
                error=IngestionError(
                    IngestionErrorCode.PROVIDER_UNAVAILABLE, "HTTP 503 upstream"
                )
            ),
        )
        client = client_factory(user_a)

        started = client.post(f"/api/v1/analysis-targets/{target_a['id']}/ingestions")
        run = client.get(f"/api/v1/ingestion-runs/{started.json()['id']}").json()

        assert "503" not in run["error_message"]
        assert "temporarily unavailable" in run["error_message"]

    def test_an_unexpected_error_still_reaches_a_terminal_state(
        self, client_factory, user_a, target_a, monkeypatch
    ):
        class Exploding:
            def fetch(self, target):
                raise RuntimeError("connection pool exhausted")

        _use_provider(monkeypatch, Exploding())
        client = client_factory(user_a)

        started = client.post(f"/api/v1/analysis-targets/{target_a['id']}/ingestions")
        run = client.get(f"/api/v1/ingestion-runs/{started.json()['id']}").json()

        assert run["status"] == "failed"
        assert run["error_code"] == "unexpected_error"
        assert "connection pool" not in run["error_message"]

    def test_a_failed_run_leaves_previously_ingested_reviews_intact(
        self, client_factory, user_a, target_a, monkeypatch
    ):
        client = client_factory(user_a)
        _use_provider(monkeypatch, StubProvider(_recorded_reviews()))
        client.post(f"/api/v1/analysis-targets/{target_a['id']}/ingestions")

        _use_provider(
            monkeypatch,
            StubProvider(error=IngestionError(IngestionErrorCode.PROVIDER_TIMEOUT)),
        )
        client.post(f"/api/v1/analysis-targets/{target_a['id']}/ingestions")

        reviews = client.get(
            f"/api/v1/analysis-targets/{target_a['id']}/reviews"
        ).json()
        assert reviews["total"] == 4


class TestFileImportFallback:
    def test_a_valid_file_is_ingested(self, client_factory, user_a, target_a):
        client = client_factory(user_a)

        started = client.post(
            f"/api/v1/analysis-targets/{target_a['id']}/ingestions/imports",
            files={
                "file": (
                    "reviews_valid.csv",
                    (FIXTURES / "reviews_valid.csv").read_bytes(),
                    "text/csv",
                )
            },
        )

        assert started.status_code == 202
        run = client.get(f"/api/v1/ingestion-runs/{started.json()['id']}").json()
        assert run["status"] == "succeeded"
        assert run["reviews_ingested"] == 3
        assert run["source_kind"] == "file_import"

    def test_a_mixed_file_reports_partial_success(
        self, client_factory, user_a, target_a
    ):
        client = client_factory(user_a)

        started = client.post(
            f"/api/v1/analysis-targets/{target_a['id']}/ingestions/imports",
            files={
                "file": (
                    "reviews_mixed.csv",
                    (FIXTURES / "reviews_mixed.csv").read_bytes(),
                    "text/csv",
                )
            },
        )
        run = client.get(f"/api/v1/ingestion-runs/{started.json()['id']}").json()

        assert run["status"] == "partial"
        assert run["reviews_ingested"] == 2
        assert run["reviews_rejected"] == 3
        assert run["rejection_reasons"] == {
            "missing_review_text": 1,
            "missing_or_invalid_rating": 2,
        }

    def test_an_unparseable_file_fails_without_persisting_reviews(
        self, client_factory, user_a, target_a
    ):
        client = client_factory(user_a)

        started = client.post(
            f"/api/v1/analysis-targets/{target_a['id']}/ingestions/imports",
            files={
                "file": (
                    "malformed.csv",
                    (FIXTURES / "malformed.csv").read_bytes(),
                    "text/csv",
                )
            },
        )
        run = client.get(f"/api/v1/ingestion-runs/{started.json()['id']}").json()

        assert run["status"] == "failed"
        assert run["error_code"] == "source_unparseable"
        assert (
            client.get(f"/api/v1/analysis-targets/{target_a['id']}/reviews").json()[
                "total"
            ]
            == 0
        )

    def test_an_unsupported_file_type_is_rejected_before_any_run_is_created(
        self, client_factory, user_a, target_a
    ):
        client = client_factory(user_a)

        response = client.post(
            f"/api/v1/analysis-targets/{target_a['id']}/ingestions/imports",
            files={"file": ("reviews.pdf", b"%PDF-1.4", "application/pdf")},
        )

        assert response.status_code == 422
        assert (
            client.get(f"/api/v1/analysis-targets/{target_a['id']}/ingestions").json()[
                "items"
            ]
            == []
        )


class TestCrossUserIngestionAuthorization:
    def test_user_b_cannot_start_ingestion_on_user_a_target(
        self, client_factory, user_a, user_b, target_a, monkeypatch
    ):
        _use_provider(monkeypatch, StubProvider(_recorded_reviews()))

        response = client_factory(user_b).post(
            f"/api/v1/analysis-targets/{target_a['id']}/ingestions"
        )

        assert response.status_code == 404
        assert (
            client_factory(user_a)
            .get(f"/api/v1/analysis-targets/{target_a['id']}/ingestions")
            .json()["items"]
            == []
        )

    def test_user_b_cannot_import_reviews_into_user_a_target(
        self, client_factory, user_a, user_b, target_a
    ):
        response = client_factory(user_b).post(
            f"/api/v1/analysis-targets/{target_a['id']}/ingestions/imports",
            files={
                "file": (
                    "reviews_valid.csv",
                    (FIXTURES / "reviews_valid.csv").read_bytes(),
                    "text/csv",
                )
            },
        )

        assert response.status_code == 404
        assert (
            client_factory(user_a)
            .get(f"/api/v1/analysis-targets/{target_a['id']}/reviews")
            .json()["total"]
            == 0
        )

    def test_user_b_cannot_read_user_a_reviews(
        self, client_factory, user_a, user_b, target_a, monkeypatch
    ):
        _use_provider(monkeypatch, StubProvider(_recorded_reviews()))
        client_factory(user_a).post(
            f"/api/v1/analysis-targets/{target_a['id']}/ingestions"
        )

        response = client_factory(user_b).get(
            f"/api/v1/analysis-targets/{target_a['id']}/reviews"
        )

        assert response.status_code == 404
        assert "pour over" not in response.text

    def test_user_b_cannot_poll_user_a_ingestion_run(
        self, client_factory, user_a, user_b, target_a, monkeypatch
    ):
        _use_provider(monkeypatch, StubProvider(_recorded_reviews()))
        run_id = (
            client_factory(user_a)
            .post(f"/api/v1/analysis-targets/{target_a['id']}/ingestions")
            .json()["id"]
        )

        response = client_factory(user_b).get(f"/api/v1/ingestion-runs/{run_id}")

        assert response.status_code == 404

    def test_ingestion_requires_authentication(self, client_factory, user_a, target_a):
        response = client_factory().post(
            f"/api/v1/analysis-targets/{target_a['id']}/ingestions"
        )

        assert response.status_code == 401


class TestTargetSummary:
    def test_summary_aggregates_persisted_reviews(
        self, client_factory, user_a, target_a, monkeypatch
    ):
        _use_provider(monkeypatch, StubProvider(_recorded_reviews()))
        client = client_factory(user_a)
        client.post(f"/api/v1/analysis-targets/{target_a['id']}/ingestions")

        summary = client.get(
            f"/api/v1/analysis-targets/{target_a['id']}/summary"
        ).json()

        assert summary["entity_name"] == "Blue Bottle Coffee"
        assert summary["platform"] == "google_maps"
        assert summary["reviews_collected"] == 4
        assert summary["average_rating"] == 4.0
        assert summary["earliest_review"].startswith("2026-04-08")
        assert summary["latest_review"].startswith("2026-07-02")
        assert summary["latest_run"]["status"] == "succeeded"

    def test_summary_before_any_ingestion_reports_no_run(
        self, client_factory, user_a, target_a
    ):
        summary = (
            client_factory(user_a)
            .get(f"/api/v1/analysis-targets/{target_a['id']}/summary")
            .json()
        )

        assert summary["reviews_collected"] == 0
        assert summary["average_rating"] is None
        assert summary["latest_run"] is None

    def test_user_b_cannot_read_user_a_summary(
        self, client_factory, user_a, user_b, target_a
    ):
        response = client_factory(user_b).get(
            f"/api/v1/analysis-targets/{target_a['id']}/summary"
        )

        assert response.status_code == 404

    def test_summary_for_an_unknown_target_is_not_found(self, client_factory, user_a):
        response = client_factory(user_a).get(
            f"/api/v1/analysis-targets/{uuid.uuid4()}/summary"
        )

        assert response.status_code == 404
