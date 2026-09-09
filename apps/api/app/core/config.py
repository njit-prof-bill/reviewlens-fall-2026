import os
import re
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, ConfigDict


def _load_local_env_files() -> None:
    """Load local env files into process env for development ergonomics."""
    config_path = Path(__file__).resolve()
    api_root = config_path.parents[2]
    repo_root = next(
        (
            parent
            for parent in [api_root, *api_root.parents]
            if (parent / ".git").exists() or (parent / "docker-compose.yml").exists()
        ),
        api_root,
    )

    env_files = [
        api_root / ".env",
        repo_root / ".env.local",
    ]

    for env_file in env_files:
        if not env_file.exists():
            continue

        for raw_line in env_file.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            # Keep explicitly exported shell env vars authoritative.
            os.environ.setdefault(key.strip(), value.strip())


_load_local_env_files()


LOCALHOST_ORIGIN_REGEX = r"https?://(localhost|127\.0\.0\.1)(:\d+)?"
DEFAULT_APP_SLUG = os.getenv("APP_SLUG", "reviewlens")
DEFAULT_API_NAME = os.getenv("API_NAME", "reviewlens-api")
DEFAULT_API_VERSION = os.getenv("API_VERSION", "0.1.0")
DEFAULT_DATABASE_NAME = os.getenv("DATABASE_NAME", DEFAULT_APP_SLUG)


def _wildcard_origin_to_regex(origin: str) -> str:
    """Convert a wildcard origin like https://*.example.com to a full-match regex."""
    escaped = re.escape(origin)
    wildcard_regex = escaped.replace(r"\*", r"[^.]+")
    return f"^{wildcard_regex}$"


def _combine_regexes(regexes: list[str]) -> str | None:
    parts = [part.strip() for part in regexes if part and part.strip()]
    if not parts:
        return None
    return "|".join(f"(?:{part})" for part in parts)


def _parse_cors_origins(raw: str) -> tuple[list[str], list[str]]:
    exact_origins: list[str] = []
    wildcard_regexes: list[str] = []

    for entry in raw.split(","):
        origin = entry.strip()
        if not origin:
            continue

        if "*" in origin:
            wildcard_regexes.append(_wildcard_origin_to_regex(origin))
            continue

        exact_origins.append(origin)

    return exact_origins, wildcard_regexes


class Settings(BaseModel):
    """Application settings loaded from environment variables."""

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_env: str = "development"
    app_name: str = DEFAULT_API_NAME
    app_version: str = DEFAULT_API_VERSION
    database_url: str = (
        f"postgresql+psycopg://postgres:postgres@localhost:5432/{DEFAULT_DATABASE_NAME}"
    )
    clerk_jwks_url: str | None = None
    clerk_issuer: str | None = None
    clerk_audience: str | None = None
    clerk_secret_key: str | None = None
    review_provider: str = "serpapi"
    review_provider_api_key: str | None = None
    review_provider_timeout_seconds: float = 30.0
    review_fetch_max: int = 100
    max_import_file_bytes: int = 2 * 1024 * 1024
    llm_provider: str = "openai"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"
    llm_timeout_seconds: float = 30.0
    qa_max_context_characters: int = 60_000
    cors_origin_regex: str | None = LOCALHOST_ORIGIN_REGEX
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "http://localhost:4174",
        "http://127.0.0.1:4174",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    def __init__(self, **data):
        super().__init__(**data)

        self.app_env = os.getenv("APP_ENV", self.app_env)
        cors_env = os.getenv("CORS_ORIGINS")
        if cors_env:
            parsed_origins, wildcard_regexes = _parse_cors_origins(cors_env)
            self.cors_origins = parsed_origins
            self.cors_origin_regex = _combine_regexes(
                [LOCALHOST_ORIGIN_REGEX, *wildcard_regexes]
            )

        cors_regex_env = os.getenv("CORS_ORIGIN_REGEX")
        if cors_regex_env:
            self.cors_origin_regex = _combine_regexes(
                [self.cors_origin_regex or "", cors_regex_env]
            )

        self.database_url = os.getenv("DATABASE_URL", self.database_url)
        self.clerk_jwks_url = os.getenv("CLERK_JWKS_URL", self.clerk_jwks_url)
        self.clerk_issuer = os.getenv("CLERK_ISSUER", self.clerk_issuer)
        self.clerk_audience = os.getenv("CLERK_AUDIENCE", self.clerk_audience)
        self.clerk_secret_key = os.getenv("CLERK_SECRET_KEY", self.clerk_secret_key)
        self.review_provider = os.getenv("REVIEW_PROVIDER", self.review_provider)
        self.review_provider_api_key = os.getenv(
            "REVIEW_PROVIDER_API_KEY", self.review_provider_api_key
        )
        self.review_provider_timeout_seconds = float(
            os.getenv(
                "REVIEW_PROVIDER_TIMEOUT_SECONDS",
                self.review_provider_timeout_seconds,
            )
        )
        self.review_fetch_max = int(
            os.getenv("REVIEW_FETCH_MAX", self.review_fetch_max)
        )
        self.max_import_file_bytes = int(
            os.getenv("MAX_IMPORT_FILE_BYTES", self.max_import_file_bytes)
        )
        self.llm_provider = os.getenv("LLM_PROVIDER", self.llm_provider)
        self.openai_api_key = os.getenv("OPENAI_API_KEY", self.openai_api_key)
        self.openai_model = os.getenv("OPENAI_MODEL", self.openai_model)
        self.llm_timeout_seconds = float(
            os.getenv("LLM_TIMEOUT_SECONDS", self.llm_timeout_seconds)
        )
        self.qa_max_context_characters = int(
            os.getenv("QA_MAX_CONTEXT_CHARACTERS", self.qa_max_context_characters)
        )

    def validate_runtime_configuration(self) -> None:
        """Fail fast for production-equivalent API containers without leaking secrets."""
        if self.app_env != "production":
            return
        required = {
            "CLERK_JWKS_URL": self.clerk_jwks_url,
            "CLERK_SECRET_KEY": self.clerk_secret_key,
            "REVIEW_PROVIDER_API_KEY": self.review_provider_api_key,
            "OPENAI_API_KEY": self.openai_api_key,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise RuntimeError(
                "Required production configuration is missing: " + ", ".join(missing)
            )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
