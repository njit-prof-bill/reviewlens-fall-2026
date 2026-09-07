from dataclasses import dataclass
from typing import Protocol

from app.domain import QAResultKind


@dataclass(frozen=True, slots=True)
class LLMRequest:
    system_prompt: str
    review_context: str
    question: str


@dataclass(frozen=True, slots=True)
class LLMResult:
    answer: str
    result_kind: QAResultKind
    evidence_review_ids: tuple[str, ...] = ()


class LLMProvider(Protocol):
    name: str
    model: str

    async def answer(self, request: LLMRequest) -> LLMResult: ...


class LLMProviderError(Exception):
    def __init__(self, message: str = "The AI service is temporarily unavailable."):
        super().__init__(message)
        self.message = message
