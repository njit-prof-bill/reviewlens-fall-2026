from fastapi import APIRouter

from app.core.config import settings
from app.dependencies import AuthIdentity, CurrentUser
from app.schemas import (
    AppUserProfile,
    AuthIdentityResponse,
    HealthResponse,
    VersionResponse,
)

router = APIRouter(prefix="/api/v1", tags=["v1"])
canonical_router = APIRouter(prefix="/api", tags=["canonical"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="ok")


@router.get("/ready", response_model=HealthResponse)
async def ready() -> HealthResponse:
    """Readiness check endpoint."""
    return HealthResponse(status="ready")


@router.get("/version", response_model=VersionResponse)
async def version() -> VersionResponse:
    """API version endpoint."""
    return VersionResponse(name=settings.app_name, version=settings.app_version)


@router.get("/auth/me", response_model=AuthIdentityResponse)
async def auth_me(identity: AuthIdentity) -> AuthIdentityResponse:
    """Return the authenticated identity from the verified Clerk token."""
    return AuthIdentityResponse(
        sub=identity["sub"],
        sid=identity.get("sid"),
        iss=identity.get("iss"),
        azp=identity.get("azp"),
        email=identity.get("email"),
    )


# Canonical app user profile endpoint (unversioned) with v1 compatibility alias.
@router.get("/me", response_model=AppUserProfile)
@canonical_router.get("/me", response_model=AppUserProfile)
async def me(user: CurrentUser) -> AppUserProfile:
    """Return the authenticated app user profile from local persistence."""
    return AppUserProfile(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
    )
