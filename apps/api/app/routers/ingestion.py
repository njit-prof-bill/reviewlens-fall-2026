import uuid
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, File, Query, UploadFile, status

from app.core.config import settings
from app.dependencies import CurrentUser, DbSession
from app.domain import IngestionSourceKind
from app.errors import AppValidationError
from app.schemas import (
    AnalysisTargetSummaryResponse,
    ApiErrorDetail,
    IngestionRunListResponse,
    IngestionRunResponse,
    ReviewListResponse,
    ReviewResponse,
)
from app.services import analysis_target_service, review_service
from app.services.ingestion.runner import execute_ingestion_run, start_ingestion_run
from app.services.ingestion.sources import FileImportSource, GoogleMapsReviewProvider

router = APIRouter(tags=["ingestion"])

_ALLOWED_IMPORT_SUFFIXES = (".csv", ".json")


@router.post(
    "/analysis-targets/{target_id}/ingestions",
    response_model=IngestionRunResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def start_url_ingestion(
    target_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    user: CurrentUser,
    db: DbSession,
) -> IngestionRunResponse:
    """Collect reviews from the target's source URL (S1-019)."""
    target = analysis_target_service.get_owned_target(db, user.id, target_id)
    run = start_ingestion_run(db, target.id, IngestionSourceKind.URL_FETCH)

    background_tasks.add_task(execute_ingestion_run, run.id, GoogleMapsReviewProvider())
    return IngestionRunResponse.model_validate(run)


@router.post(
    "/analysis-targets/{target_id}/ingestions/imports",
    response_model=IngestionRunResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def start_import_ingestion(
    target_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    user: CurrentUser,
    db: DbSession,
    file: Annotated[UploadFile, File()],
) -> IngestionRunResponse:
    """Recovery path used when the live review source is unavailable."""
    target = analysis_target_service.get_owned_target(db, user.id, target_id)

    filename = file.filename or ""
    if not filename.lower().endswith(_ALLOWED_IMPORT_SUFFIXES):
        raise AppValidationError(
            "The review file is not valid",
            [ApiErrorDetail(field="file", issue="Upload a .csv or .json file.")],
        )

    payload = await file.read()
    if len(payload) > settings.max_import_file_bytes:
        limit_mb = settings.max_import_file_bytes // (1024 * 1024)
        raise AppValidationError(
            "The review file is too large",
            [
                ApiErrorDetail(
                    field="file", issue=f"The file must be {limit_mb} MB or smaller."
                )
            ],
        )

    run = start_ingestion_run(db, target.id, IngestionSourceKind.FILE_IMPORT)
    background_tasks.add_task(
        execute_ingestion_run, run.id, FileImportSource(filename, payload)
    )
    return IngestionRunResponse.model_validate(run)


@router.get(
    "/analysis-targets/{target_id}/ingestions",
    response_model=IngestionRunListResponse,
)
async def list_ingestion_runs(
    target_id: uuid.UUID, user: CurrentUser, db: DbSession
) -> IngestionRunListResponse:
    target = analysis_target_service.get_owned_target(db, user.id, target_id)
    runs = review_service.list_runs(db, target.id)
    return IngestionRunListResponse(
        items=[IngestionRunResponse.model_validate(run) for run in runs]
    )


@router.get("/ingestion-runs/{run_id}", response_model=IngestionRunResponse)
async def get_ingestion_run(
    run_id: uuid.UUID, user: CurrentUser, db: DbSession
) -> IngestionRunResponse:
    run = review_service.get_owned_run(db, user.id, run_id)
    return IngestionRunResponse.model_validate(run)


@router.get("/analysis-targets/{target_id}/reviews", response_model=ReviewListResponse)
async def list_target_reviews(
    target_id: uuid.UUID,
    user: CurrentUser,
    db: DbSession,
    limit: int = Query(default=25, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> ReviewListResponse:
    target = analysis_target_service.get_owned_target(db, user.id, target_id)
    reviews, total = review_service.list_reviews(db, target.id, limit, offset)
    return ReviewListResponse(
        items=[ReviewResponse.model_validate(review) for review in reviews],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/analysis-targets/{target_id}/summary",
    response_model=AnalysisTargetSummaryResponse,
)
async def get_target_summary(
    target_id: uuid.UUID, user: CurrentUser, db: DbSession
) -> AnalysisTargetSummaryResponse:
    target = analysis_target_service.get_owned_target(db, user.id, target_id)
    return AnalysisTargetSummaryResponse.model_validate(
        review_service.build_summary(db, target)
    )
