from collections.abc import Generator

import pytest
from app.db.models import User
from app.db.session import Base, get_db_session
from app.dependencies import get_current_user
from app.main import app
from app.services.ingestion import runner as ingestion_runner
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture()
def db_engine():
    """Create an isolated in-memory engine for persistence tests."""
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    try:
        yield engine
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def db_session(db_engine) -> Generator[Session, None, None]:
    """Yield a transaction-scoped SQLAlchemy session for each test."""
    connection = db_engine.connect()
    transaction = connection.begin()
    SessionTesting = sessionmaker(bind=connection, autoflush=False, autocommit=False)
    session = SessionTesting()

    try:
        yield session
    finally:
        session.close()
        if transaction.is_active:
            transaction.rollback()
        connection.close()


@pytest.fixture()
def session_factory(db_engine) -> sessionmaker:
    """Committing sessions against the same in-memory database as db_engine."""
    return sessionmaker(bind=db_engine, autoflush=False, autocommit=False)


@pytest.fixture()
def app_session(session_factory) -> Generator[Session, None, None]:
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


def _create_user(session: Session, provider_user_id: str, email: str) -> User:
    user = User(
        auth_provider="clerk",
        auth_provider_user_id=provider_user_id,
        email=email,
        display_name=email.split("@")[0],
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture()
def user_a(app_session) -> User:
    return _create_user(app_session, "clerk_user_a", "user-a@example.com")


@pytest.fixture()
def user_b(app_session) -> User:
    return _create_user(app_session, "clerk_user_b", "user-b@example.com")


@pytest.fixture()
def client_factory(app_session, session_factory, monkeypatch):
    """Build a TestClient authenticated as a given user, or as nobody.

    Overrides are global, so a test switching users should rebuild the client;
    the most recent call wins.
    """
    monkeypatch.setattr(ingestion_runner, "SessionLocal", session_factory)

    def _build(user: User | None = None) -> TestClient:
        app.dependency_overrides[get_db_session] = lambda: app_session
        if user is None:
            app.dependency_overrides.pop(get_current_user, None)
        else:
            app.dependency_overrides[get_current_user] = lambda: user
        return TestClient(app)

    try:
        yield _build
    finally:
        app.dependency_overrides.clear()
