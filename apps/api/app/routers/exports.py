import uuid

from fastapi import APIRouter, Response

from app.dependencies import CurrentUser, DbSession
from app.services import analysis_target_service, export_service

router = APIRouter(tags=["exports"])


@router.get("/analysis-targets/{target_id}/exports/reviews.csv")
async def export_reviews_csv(
    target_id: uuid.UUID, user: CurrentUser, db: DbSession
) -> Response:
    target = analysis_target_service.get_owned_target(db, user.id, target_id)
    filename = export_service.reviews_csv_filename(target)
    return Response(
        content=export_service.build_reviews_csv(db, target),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/analysis-targets/{target_id}/exports/analysis.md")
async def export_analysis_markdown(
    target_id: uuid.UUID, user: CurrentUser, db: DbSession
) -> Response:
    target = analysis_target_service.get_owned_target(db, user.id, target_id)
    filename = export_service.analysis_markdown_filename(target)
    return Response(
        content=export_service.build_analysis_markdown(db, target),
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
