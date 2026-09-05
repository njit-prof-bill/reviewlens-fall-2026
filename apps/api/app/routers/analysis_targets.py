import uuid

from fastapi import APIRouter, Response, status

from app.dependencies import CurrentUser, DbSession
from app.schemas import (
    AnalysisTargetCreate,
    AnalysisTargetListResponse,
    AnalysisTargetRename,
    AnalysisTargetResponse,
)
from app.services import analysis_target_service

router = APIRouter(prefix="/analysis-targets", tags=["analysis-targets"])


@router.post(
    "", response_model=AnalysisTargetResponse, status_code=status.HTTP_201_CREATED
)
async def create_analysis_target(
    payload: AnalysisTargetCreate, user: CurrentUser, db: DbSession
) -> AnalysisTargetResponse:
    """Create a target owned by the authenticated user."""
    target = analysis_target_service.create_target(
        db,
        owner_user_id=user.id,
        name=payload.name,
        source_url=payload.source_url,
    )
    return AnalysisTargetResponse.model_validate(target)


@router.get("", response_model=AnalysisTargetListResponse)
async def list_analysis_targets(
    user: CurrentUser, db: DbSession
) -> AnalysisTargetListResponse:
    targets = analysis_target_service.list_targets(db, owner_user_id=user.id)
    return AnalysisTargetListResponse(
        items=[AnalysisTargetResponse.model_validate(target) for target in targets]
    )


@router.get("/{target_id}", response_model=AnalysisTargetResponse)
async def get_analysis_target(
    target_id: uuid.UUID, user: CurrentUser, db: DbSession
) -> AnalysisTargetResponse:
    target = analysis_target_service.get_owned_target(db, user.id, target_id)
    return AnalysisTargetResponse.model_validate(target)


@router.patch("/{target_id}", response_model=AnalysisTargetResponse)
async def rename_analysis_target(
    target_id: uuid.UUID,
    payload: AnalysisTargetRename,
    user: CurrentUser,
    db: DbSession,
) -> AnalysisTargetResponse:
    target = analysis_target_service.rename_target(db, user.id, target_id, payload.name)
    return AnalysisTargetResponse.model_validate(target)


@router.delete("/{target_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_analysis_target(
    target_id: uuid.UUID, user: CurrentUser, db: DbSession
) -> Response:
    analysis_target_service.delete_target(db, user.id, target_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
