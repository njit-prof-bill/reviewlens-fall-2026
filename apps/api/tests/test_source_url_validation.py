import pytest
from app.errors import AppValidationError
from app.services.source_url import derive_working_name, validate_source_url

VALID_URL = (
    "https://www.google.com/maps/place/Blue+Bottle+Coffee/"
    "@37.7823,-122.4074,17z/data=!3m1!4b1!4m6!3m5!1s0x8085808f0b0b0b0b:0x1234abcd"
)


class TestValidateSourceUrl:
    def test_accepts_a_google_maps_place_url(self):
        assert validate_source_url(VALID_URL) == VALID_URL

    def test_accepts_a_google_maps_short_link(self):
        url = "https://maps.app.goo.gl/AbCdEfGh123"
        assert validate_source_url(url) == url

    def test_accepts_a_regional_google_domain(self):
        url = "https://www.google.co.uk/maps/place/Some+Cafe"
        assert validate_source_url(url) == url

    def test_trims_surrounding_whitespace(self):
        assert validate_source_url(f"  {VALID_URL}  ") == VALID_URL

    @pytest.mark.parametrize(
        "candidate",
        [
            "",
            "   ",
            "not a url at all",
            "ftp://www.google.com/maps/place/Cafe",
            "javascript:alert(1)",
        ],
    )
    def test_rejects_malformed_input(self, candidate):
        with pytest.raises(AppValidationError):
            validate_source_url(candidate)

    def test_rejects_a_non_google_review_site(self):
        with pytest.raises(AppValidationError) as exc_info:
            validate_source_url("https://www.yelp.com/biz/blue-bottle-coffee")

        assert exc_info.value.details[0].field == "source_url"

    def test_rejects_a_google_url_that_is_not_maps(self):
        with pytest.raises(AppValidationError):
            validate_source_url("https://www.google.com/search?q=blue+bottle")


class TestDeriveWorkingName:
    def test_derives_a_readable_name_from_the_place_slug(self):
        assert derive_working_name(VALID_URL) == "Blue Bottle Coffee"

    def test_returns_none_when_no_place_segment_is_present(self):
        assert derive_working_name("https://maps.app.goo.gl/AbCdEfGh123") is None
