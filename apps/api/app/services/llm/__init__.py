from app.core.config import settings
from app.services.llm.base import LLMProvider, LLMProviderError, LLMRequest, LLMResult
from app.services.llm.openai_provider import OpenAIProvider


def get_llm_provider() -> LLMProvider:
    if settings.llm_provider != "openai":
        raise LLMProviderError("The configured AI provider is not supported.")
    if not settings.openai_api_key:
        raise LLMProviderError("Review Q&A is not configured on this server.")
    return OpenAIProvider(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        timeout_seconds=settings.llm_timeout_seconds,
    )


__all__ = [
    "LLMProvider",
    "LLMProviderError",
    "LLMRequest",
    "LLMResult",
    "get_llm_provider",
]
