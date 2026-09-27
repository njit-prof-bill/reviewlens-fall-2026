"""Build an ordered URL-review provider chain for a supported platform."""

import logging
from collections.abc import Callable

from app.core.config import settings
from app.db.models import AnalysisTarget
from app.domain import IngestionErrorCode, ReviewPlatform
from app.services.ingestion.base import (
    FallbackReviewSource,
    IngestionError,
    IngestionResult,
    ReviewSource,
)
from app.services.ingestion.sources.amazon_provider import AmazonProductReviewProvider
from app.services.ingestion.sources.google_maps_provider import GoogleMapsReviewProvider

logger = logging.getLogger(__name__)


class _UnconfiguredReviewSource:
    def fetch(self, target: AnalysisTarget) -> IngestionResult:
        raise IngestionError(
            IngestionErrorCode.PROVIDER_NOT_CONFIGURED,
            "No configured provider supports this review platform",
        )


ProviderFactory = Callable[[], ReviewSource]
_PROVIDER_FACTORIES: dict[str, dict[str, ProviderFactory]] = {
    "serpapi": {
        ReviewPlatform.GOOGLE_MAPS.value: GoogleMapsReviewProvider,
        ReviewPlatform.AMAZON.value: AmazonProductReviewProvider,
    }
}


def create_url_review_source(platform: str) -> ReviewSource:
    try:
        normalized_platform = ReviewPlatform(platform).value
    except ValueError as exc:
        raise ValueError(f"Unsupported review platform: {platform}") from exc

    sources: list[ReviewSource] = []
    provider_names = dict.fromkeys(
        [settings.review_provider, *settings.review_provider_fallbacks]
    )
    for provider_name in provider_names:
        factory = _PROVIDER_FACTORIES.get(provider_name, {}).get(normalized_platform)
        if factory is None:
            logger.warning(
                "No %s review provider is registered for platform %s",
                provider_name,
                normalized_platform,
            )
            continue
        sources.append(factory())

    if not sources:
        return _UnconfiguredReviewSource()
    if len(sources) == 1:
        return sources[0]
    return FallbackReviewSource(sources)
