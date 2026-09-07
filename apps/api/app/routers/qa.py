import uuid

from fastapi import APIRouter, status

from app.dependencies import CurrentUser, DbSession
from app.schemas import QAEntryListResponse, QAEntryResponse, QuestionRequest
from app.services import analysis_target_service, qa_service

router = APIRouter(tags=["review-qa"])


@router.post(
    "/analysis-targets/{target_id}/questions",
    response_model=QAEntryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def ask_question(
    target_id: uuid.UUID,
    payload: QuestionRequest,
    user: CurrentUser,
    db: DbSession,
) -> QAEntryResponse:
    target = analysis_target_service.get_owned_target(db, user.id, target_id)
    entry = await qa_service.answer_question(db, target, payload.question)
    return QAEntryResponse.model_validate(entry)


@router.get(
    "/analysis-targets/{target_id}/questions",
    response_model=QAEntryListResponse,
)
async def list_questions(
    target_id: uuid.UUID,
    user: CurrentUser,
    db: DbSession,
) -> QAEntryListResponse:
    target = analysis_target_service.get_owned_target(db, user.id, target_id)
    entries = qa_service.list_entries(db, target.id)
    return QAEntryListResponse(
        items=[QAEntryResponse.model_validate(entry) for entry in entries]
    )
