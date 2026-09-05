"""File import recovery path parsing (S1-BR-027)."""

from pathlib import Path

import pytest
from app.domain import IngestionErrorCode
from app.services.ingestion.base import IngestionError
from app.services.ingestion.sources.file_import import (
    parse_csv,
    parse_json,
    parse_upload,
)

FIXTURES = Path(__file__).parent / "fixtures"


def _read(name: str) -> bytes:
    return (FIXTURES / name).read_bytes()


class TestCsvParsing:
    def test_reads_every_row(self):
        raws = parse_csv(_read("reviews_valid.csv"))

        assert len(raws) == 3
        assert raws[0].review_text.startswith("The pour over here")
        assert raws[0].rating == "5"
        assert raws[0].reviewer_name == "Dana Whitfield"

    def test_maps_alternate_column_names(self):
        payload = b"text,stars,author\nGood coffee,5,Dana\n"

        raws = parse_csv(payload)

        assert raws[0].review_text == "Good coffee"
        assert raws[0].rating == "5"
        assert raws[0].reviewer_name == "Dana"

    def test_a_header_only_file_is_rejected(self):
        with pytest.raises(IngestionError) as exc_info:
            parse_csv(b"review_text,rating\n")

        assert exc_info.value.code == IngestionErrorCode.SOURCE_UNPARSEABLE

    def test_an_unusable_file_is_rejected(self):
        with pytest.raises(IngestionError) as exc_info:
            parse_upload("malformed.csv", _read("malformed.csv"))

        assert exc_info.value.code == IngestionErrorCode.SOURCE_UNPARSEABLE

    def test_an_empty_file_is_rejected(self):
        with pytest.raises(IngestionError):
            parse_upload("reviews.csv", b"")


class TestJsonParsing:
    def test_reads_a_reviews_array_from_an_object(self):
        raws = parse_json(_read("reviews.json"))

        assert len(raws) == 2
        assert raws[1].rating == "4.0"
        assert raws[1].review_text.startswith("Rating supplied as a string")

    def test_reads_a_bare_array(self):
        raws = parse_json(b'[{"review_text": "Good", "rating": 4}]')

        assert raws[0].review_text == "Good"

    def test_invalid_json_is_rejected(self):
        with pytest.raises(IngestionError) as exc_info:
            parse_json(b"{not json")

        assert exc_info.value.code == IngestionErrorCode.SOURCE_UNPARSEABLE

    def test_an_unexpected_json_shape_is_rejected(self):
        with pytest.raises(IngestionError):
            parse_json(b'{"data": {"nested": true}}')

    def test_the_json_path_is_chosen_by_file_extension(self):
        raws = parse_upload("export.json", b'[{"text": "Good", "rating": 4}]')

        assert raws[0].review_text == "Good"
