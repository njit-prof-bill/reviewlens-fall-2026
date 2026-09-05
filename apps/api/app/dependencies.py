"""Shared FastAPI dependencies.

`get_current_user` is the single trusted source of ownership for user-scoped
data. Routes must derive the owner from it and never from the request body.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.auth import get_current_auth_identity
from app.db.models import User
from app.db.session import get_db_session
from app.services.identity import bootstrap_user_from_identity

DbSession = Annotated[Session, Depends(get_db_session)]
AuthIdentity = Annotated[dict, Depends(get_current_auth_identity)]


def get_current_user(identity: AuthIdentity, db: DbSession) -> User:
    """Resolve the verified provider identity to the persisted local user."""
    return bootstrap_user_from_identity(db, identity)


CurrentUser = Annotated[User, Depends(get_current_user)]
