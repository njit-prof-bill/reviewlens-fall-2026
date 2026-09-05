"""Domain vocabulary shared by persistence, services, and API schemas."""

from enum import StrEnum


class ReviewPlatform(StrEnum):
    GOOGLE_MAPS = "google_maps"


class IngestionStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    PARTIAL = "partial"
    FAILED = "failed"


TERMINAL_INGESTION_STATUSES = frozenset(
    {IngestionStatus.SUCCEEDED, IngestionStatus.PARTIAL, IngestionStatus.FAILED}
)


class IngestionSourceKind(StrEnum):
    URL_FETCH = "url_fetch"
    FILE_IMPORT = "file_import"


class IngestionErrorCode(StrEnum):
    """Stable codes paired with user-safe messages. Never expose provider text."""

    PROVIDER_NOT_CONFIGURED = "provider_not_configured"
    PROVIDER_TIMEOUT = "provider_timeout"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    PROVIDER_QUOTA_EXCEEDED = "provider_quota_exceeded"
    PLACE_NOT_FOUND = "place_not_found"
    NO_REVIEWS_AVAILABLE = "no_reviews_available"
    SOURCE_UNPARSEABLE = "source_unparseable"
    NO_USABLE_REVIEWS = "no_usable_reviews"
    UNEXPECTED_ERROR = "unexpected_error"


INGESTION_ERROR_MESSAGES: dict[IngestionErrorCode, str] = {
    IngestionErrorCode.PROVIDER_NOT_CONFIGURED: (
        "Review collection is not configured on this server. Contact an administrator."
    ),
    IngestionErrorCode.PROVIDER_TIMEOUT: (
        "The review service took too long to respond. Please try again."
    ),
    IngestionErrorCode.PROVIDER_UNAVAILABLE: (
        "The review service is temporarily unavailable. Please try again later."
    ),
    IngestionErrorCode.PROVIDER_QUOTA_EXCEEDED: (
        "The review collection quota has been reached. Please try again later."
    ),
    IngestionErrorCode.PLACE_NOT_FOUND: (
        "No business could be found at that URL. Check the link and try again."
    ),
    IngestionErrorCode.NO_REVIEWS_AVAILABLE: (
        "This listing has no reviews available to collect."
    ),
    IngestionErrorCode.SOURCE_UNPARSEABLE: (
        "The review data could not be read. Check the file format and try again."
    ),
    IngestionErrorCode.NO_USABLE_REVIEWS: (
        "No usable reviews were found. Every record was missing review text or a rating."
    ),
    IngestionErrorCode.UNEXPECTED_ERROR: (
        "Review collection failed unexpectedly. Please try again."
    ),
}
