import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.db.models import AnalysisTarget, QAEntry, QAEvidence
from app.domain import REVIEWLENS_SYSTEM_PROMPT, QAResultKind
from app.errors import AppValidationError, ServiceUnavailableError
from app.schemas import ApiErrorDetail
from app.services.llm import LLMProviderError, LLMRequest, get_llm_provider
from app.services.qa_context import build_context


async def answer_question(
    session: Session, target: AnalysisTarget, question: str
) -> QAEntry:
    context = build_context(session, target.id, settings.qa_max_context_characters)
    if not context.reviews:
        raise AppValidationError(
            "Complete review ingestion before asking a question.",
            [ApiErrorDetail(field="target_id", issue="No reviews are available.")],
        )

    provider_name = settings.llm_provider
    model_name = settings.openai_model
    prompt = REVIEWLENS_SYSTEM_PROMPT.format(
        entity_name=target.name,
        platform=target.platform,
    )
    try:
        provider = get_llm_provider()
        provider_name = provider.name
        model_name = provider.model
        result = await provider.answer(
            LLMRequest(
                system_prompt=prompt,
                review_context=context.text,
                question=question,
            )
        )
    except LLMProviderError as exc:
        raise ServiceUnavailableError(exc.message) from exc

    review_by_id = {str(review.id): review for review in context.reviews}
    unknown_ids = set(result.evidence_review_ids) - review_by_id.keys()
    if unknown_ids:
        raise ServiceUnavailableError("The AI response could not be validated.")
    if result.result_kind is QAResultKind.GROUNDED and not result.evidence_review_ids:
        raise ServiceUnavailableError(
            "The AI response did not include supporting evidence."
        )
    if result.result_kind is not QAResultKind.GROUNDED and result.evidence_review_ids:
        raise ServiceUnavailableError("The AI response included unsupported evidence.")
    if not result.answer:
        raise ServiceUnavailableError("The AI response could not be validated.")

    entry = QAEntry(
        analysis_target_id=target.id,
        question=question,
        answer=result.answer,
        result_kind=result.result_kind.value,
        provider=provider_name,
        model=model_name,
        context_review_count=len(context.reviews),
    )
    for position, review_id in enumerate(result.evidence_review_ids):
        review = review_by_id[review_id]
        entry.evidence.append(
            QAEvidence(
                review_id=review.id,
                position=position,
                excerpt=review.review_text[:500],
                rating=review.rating,
                reviewer_name=review.reviewer_name,
                reviewed_at=review.reviewed_at,
            )
        )

    session.add(entry)
    session.commit()
    return get_entry(session, entry.id)


def get_entry(session: Session, entry_id: uuid.UUID) -> QAEntry:
    statement = (
        select(QAEntry)
        .options(selectinload(QAEntry.evidence))
        .where(QAEntry.id == entry_id)
    )
    return session.scalars(statement).one()


def list_entries(session: Session, target_id: uuid.UUID) -> list[QAEntry]:
    statement = (
        select(QAEntry)
        .options(selectinload(QAEntry.evidence))
        .where(QAEntry.analysis_target_id == target_id)
        .order_by(QAEntry.created_at, QAEntry.id)
    )
    return list(session.scalars(statement))
