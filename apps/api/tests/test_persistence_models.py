from io import StringIO
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from app.db.models.user import User
from app.db.models.workspace import Workspace
from app.db.models.workspace_member import WorkspaceMember
from sqlalchemy.exc import IntegrityError


class TestPersistenceModels:
    def test_create_user_workspace_and_membership(self, db_session):
        user = User(email="owner@example.com", display_name="Owner")
        workspace = Workspace(name="Owner's Workspace")
        db_session.add_all([user, workspace])
        db_session.flush()

        membership = WorkspaceMember(
            workspace_id=workspace.id,
            user_id=user.id,
            role="owner",
        )
        db_session.add(membership)
        db_session.commit()

        assert user.id is not None
        assert workspace.id is not None
        assert membership.id is not None
        assert membership.role == "owner"

    def test_workspace_member_unique_constraint(self, db_session):
        user = User(email="dupe@example.com")
        workspace = Workspace(name="Duplicate Membership Workspace")
        db_session.add_all([user, workspace])
        db_session.flush()

        first = WorkspaceMember(
            workspace_id=workspace.id, user_id=user.id, role="owner"
        )
        second = WorkspaceMember(
            workspace_id=workspace.id, user_id=user.id, role="owner"
        )
        db_session.add_all([first, second])

        with pytest.raises(IntegrityError):
            db_session.flush()


@pytest.mark.parametrize("start", ["20260908_0004", "20260921_0004", "base"])
def test_both_sprint_3_histories_can_upgrade_to_one_head(start):
    api_root = Path(__file__).resolve().parents[1]
    output = StringIO()
    config = Config(str(api_root / "alembic.ini"), output_buffer=output)
    config.set_main_option("script_location", str(api_root / "alembic"))
    heads = ScriptDirectory.from_config(config).get_heads()
    assert len(heads) == 1

    command.upgrade(config, f"{start}:head", sql=True)

    sql = output.getvalue()
    assert ("ADD COLUMN review_identity_key" in sql) == (start != "20260921_0004")
    assert ("ADD COLUMN dedupe_key" in sql) == (start != "20260908_0004")
    assert heads[0] in sql
