import pytest
from app.core.config import Settings


def test_production_configuration_requires_external_service_credentials(monkeypatch):
    for name in (
        "CLERK_JWKS_URL",
        "CLERK_SECRET_KEY",
        "REVIEW_PROVIDER_API_KEY",
        "OPENAI_API_KEY",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("APP_ENV", "production")

    with pytest.raises(
        RuntimeError, match="Required production configuration is missing"
    ):
        Settings().validate_runtime_configuration()


def test_development_configuration_allows_missing_external_service_credentials(
    monkeypatch,
):
    for name in (
        "CLERK_JWKS_URL",
        "CLERK_SECRET_KEY",
        "REVIEW_PROVIDER_API_KEY",
        "OPENAI_API_KEY",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("APP_ENV", "development")

    Settings().validate_runtime_configuration()
