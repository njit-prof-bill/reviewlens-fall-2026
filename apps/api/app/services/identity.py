"""Maps a verified provider identity onto the local application user."""

import logging

from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import User
from app.services.clerk_profile import (
    extract_display_name_from_clerk_user,
    extract_email_from_clerk_user,
    fetch_clerk_user_profile,
)
from app.services.user_bootstrap import get_or_create_local_user_with_default_workspace

logger = logging.getLogger(__name__)

AUTH_PROVIDER = "clerk"


def resolve_identity_profile(
    identity: dict,
) -> tuple[str | None, str | None, str | None]:
    """Resolve profile fields from token claims, falling back to the Clerk API."""
    email = identity.get("email")
    display_name = identity.get("name")
    avatar_url = identity.get("picture")

    if email and display_name and avatar_url:
        return email, display_name, avatar_url

    if not settings.clerk_secret_key:
        logger.warning("CLERK_SECRET_KEY not configured; skipping profile backfill")
        return email, display_name, avatar_url

    user_id = identity["sub"]
    clerk_user = fetch_clerk_user_profile(user_id, settings.clerk_secret_key)
    if not clerk_user:
        logger.warning("Clerk API returned no user for %s", user_id)
        return email, display_name, avatar_url

    if not email:
        email = extract_email_from_clerk_user(clerk_user)
    if not display_name:
        display_name = extract_display_name_from_clerk_user(clerk_user)
    if not avatar_url:
        avatar_url = clerk_user.get("image_url")

    return email, display_name, avatar_url


def bootstrap_user_from_identity(session: Session, identity: dict) -> User:
    """Return the local user for a verified identity, creating it on first sight."""
    email, display_name, avatar_url = resolve_identity_profile(identity)

    user = get_or_create_local_user_with_default_workspace(
        session,
        auth_provider=AUTH_PROVIDER,
        auth_provider_user_id=identity["sub"],
        email=email,
        display_name=display_name,
        avatar_url=avatar_url,
    )

    profile_updated = False
    if email and not user.email:
        user.email = email
        profile_updated = True
    if display_name and not user.display_name:
        user.display_name = display_name
        profile_updated = True
    if avatar_url and not user.avatar_url:
        user.avatar_url = avatar_url
        profile_updated = True

    if profile_updated:
        session.add(user)
        session.commit()
        session.refresh(user)

    return user
