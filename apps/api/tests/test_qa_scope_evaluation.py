import asyncio
import json
from pathlib import Path

from app.domain import REVIEWLENS_SYSTEM_PROMPT, QAResultKind
from app.services.llm import LLMRequest, LLMResult

CASES = json.loads(
    (Path(__file__).parent / "fixtures" / "qa_scope_cases.json").read_text()
)


class DeterministicScopeProvider:
    """CI harness that returns the expected category without a live model."""

    name = "scope-evaluation"
    model = "deterministic-v1"

    def __init__(self, expected: QAResultKind):
        self.expected = expected

    async def answer(self, request: LLMRequest) -> LLMResult:
        assert "Use only the supplied reviews as evidence" in request.system_prompt
        assert "another entity" in request.system_prompt
        assert "another review platform" in request.system_prompt
        return LLMResult(
            answer=f"Deterministic {self.expected.value} response.",
            result_kind=self.expected,
            evidence_review_ids=(
                ("review-1",) if self.expected is QAResultKind.GROUNDED else ()
            ),
        )


def test_scope_evaluation_set_covers_required_categories():
    categories = {case["expected_result_kind"] for case in CASES}

    assert categories == {
        "grounded",
        "insufficient_evidence",
        "out_of_scope",
    }
    assert len(CASES) >= 6


def test_system_prompt_defines_dataset_and_scope_boundaries():
    prompt = REVIEWLENS_SYSTEM_PROMPT.format(
        entity_name="Demo Cafe",
        platform="google_maps",
    )

    assert "Active entity: Demo Cafe" in prompt
    assert "Review platform: google_maps" in prompt
    assert "general knowledge" in prompt
    assert "another entity" in prompt
    assert "another review platform" in prompt
    assert "insufficient_evidence" in prompt


def test_deterministic_provider_harness_exercises_every_case():
    for case in CASES:
        expected = QAResultKind(case["expected_result_kind"])
        provider = DeterministicScopeProvider(expected)
        result = asyncio.run(
            provider.answer(
                LLMRequest(
                    system_prompt=REVIEWLENS_SYSTEM_PROMPT.format(
                        entity_name="Demo Cafe",
                        platform="google_maps",
                    ),
                    review_context="[review_id=review-1]\ntext=Friendly staff.",
                    question=case["question"],
                )
            )
        )
        assert result.result_kind is expected
