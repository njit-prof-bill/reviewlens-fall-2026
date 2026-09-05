"""Normalization rules for individual review records (S1-021)."""

from datetime import UTC, datetime

import pytest
from app.services.ingestion.base import RawReview
from app.services.ingestion.normalizer import (
    NormalizedReview,
    RejectedRecord,
    normalize,
    normalize_all,
)


class TestRequiredFields:
    def test_accepts_a_complete_record(self):
        result = normalize(
            RawReview(
                review_text="Great espresso.",
                rating=4,
                reviewer_name="Marcus Lee",
                reviewed_at="2026-06-11T09:05:00Z",
                source_review_id="gm-002",
                review_url="https://example.test/r/2",
            )
        )

        assert isinstance(result, NormalizedReview)
        assert result.review_text == "Great espresso."
        assert result.rating == 4.0
        assert result.reviewed_at == datetime(2026, 6, 11, 9, 5, tzinfo=UTC)

    @pytest.mark.parametrize("text", [None, "", "   "])
    def test_rejects_a_record_without_review_text(self, text):
        result = normalize(RawReview(review_text=text, rating=4))

        assert isinstance(result, RejectedRecord)
        assert result.reason == "missing_review_text"

    @pytest.mark.parametrize("rating", [None, "", "unrated", 0, 6, -2, True])
    def test_rejects_a_record_without_a_usable_rating(self, rating):
        result = normalize(RawReview(review_text="Fine.", rating=rating))

        assert isinstance(result, RejectedRecord)
        assert result.reason == "missing_or_invalid_rating"

    @pytest.mark.parametrize(
        ("raw", "expected"),
        [("4", 4.0), ("4.5", 4.5), ("4,5", 4.5), ("5 stars", 5.0), (3, 3.0)],
    )
    def test_coerces_ratings_supplied_in_common_shapes(self, raw, expected):
        result = normalize(RawReview(review_text="Fine.", rating=raw))

        assert isinstance(result, NormalizedReview)
        assert result.rating == expected


class TestOptionalMetadata:
    def test_absent_metadata_stays_none_rather_than_being_invented(self):
        result = normalize(RawReview(review_text="Fine.", rating=4))

        assert isinstance(result, NormalizedReview)
        assert result.reviewer_name is None
        assert result.reviewed_at is None
        assert result.source_review_id is None
        assert result.review_url is None

    def test_an_unparseable_date_does_not_reject_the_record(self):
        result = normalize(
            RawReview(review_text="Fine.", rating=4, reviewed_at="last Tuesday")
        )

        assert isinstance(result, NormalizedReview)
        assert result.reviewed_at is None

    def test_a_naive_date_is_treated_as_utc(self):
        result = normalize(
            RawReview(review_text="Fine.", rating=4, reviewed_at="2026-06-11T09:05:00")
        )

        assert isinstance(result, NormalizedReview)
        assert result.reviewed_at.tzinfo is not None


class TestBatchNormalization:
    def test_a_malformed_record_does_not_discard_usable_ones(self):
        accepted, rejected = normalize_all(
            [
                RawReview(review_text="Usable.", rating=5),
                RawReview(review_text=None, rating=5),
                RawReview(review_text="Also usable.", rating="4"),
                RawReview(review_text="No rating.", rating=None),
            ]
        )

        assert [item.review_text for item in accepted] == ["Usable.", "Also usable."]
        assert len(rejected) == 2
