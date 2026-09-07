import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.errors import (
    AppValidationError,
    ResourceNotFoundError,
    ServiceUnavailableError,
)
from app.routers import analysis_targets_router, ingestion_router, qa_router
from app.routes import canonical_router
from app.routes import router as v1_router
from app.schemas import ApiError, ApiErrorDetail, ApiErrorResponse

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(title=settings.app_name, version=settings.app_version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router)
app.include_router(canonical_router)

# Resource routers are served under both prefixes so clients may use either.
for resource_router in (analysis_targets_router, ingestion_router, qa_router):
    app.include_router(resource_router, prefix="/api/v1")
    app.include_router(resource_router, prefix="/api")


def error_response(
    status_code: int,
    code: str,
    message: str,
    details: list[ApiErrorDetail] | None = None,
) -> JSONResponse:
    payload = ApiErrorResponse(
        error=ApiError(code=code, message=message, details=details or []),
    )
    return JSONResponse(status_code=status_code, content=payload.model_dump())


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    _: Request, exc: StarletteHTTPException
) -> JSONResponse:
    return error_response(
        status_code=exc.status_code, code="http_error", message=str(exc.detail)
    )


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    details = [
        ApiErrorDetail(
            field=".".join(str(segment) for segment in err.get("loc", [])[1:]) or None,
            issue=err.get("msg", "Invalid request"),
            context=err.get("ctx"),
        )
        for err in exc.errors()
    ]
    return error_response(
        status_code=422,
        code="validation_error",
        message="Request validation failed",
        details=details,
    )


@app.exception_handler(AppValidationError)
async def app_validation_error_handler(
    _: Request, exc: AppValidationError
) -> JSONResponse:
    return error_response(
        status_code=422,
        code="validation_error",
        message=exc.message,
        details=exc.details,
    )


@app.exception_handler(ResourceNotFoundError)
async def resource_not_found_handler(
    _: Request, exc: ResourceNotFoundError
) -> JSONResponse:
    return error_response(status_code=404, code="not_found", message=exc.message)


@app.exception_handler(ServiceUnavailableError)
async def service_unavailable_handler(
    _: Request, exc: ServiceUnavailableError
) -> JSONResponse:
    return error_response(
        status_code=503,
        code="service_unavailable",
        message=exc.message,
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, __: Exception) -> JSONResponse:
    return error_response(
        status_code=500,
        code="internal_server_error",
        message="An unexpected error occurred",
    )
