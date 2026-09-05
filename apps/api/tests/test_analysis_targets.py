"""Analysis target API behavior, ownership, and validation (S1-011, S1-012, S1-015 to S1-018)."""

import uuid

VALID_URL = (
    "https://www.google.com/maps/place/Blue+Bottle+Coffee/"
    "@37.7823,-122.4074,17z/data=!4m6!3m5!1s0x8085808f0b0b0b0b:0x1234abcd"
)
OTHER_URL = "https://www.google.com/maps/place/Downtown+Hotel/@40.7,-74.0,17z"


def _create_target(client, name="Blue Bottle Coffee", source_url=VALID_URL):
    return client.post(
        "/api/v1/analysis-targets", json={"name": name, "source_url": source_url}
    )


class TestCreateAnalysisTarget:
    def test_creates_a_target_for_the_authenticated_user(self, client_factory, user_a):
        response = _create_target(client_factory(user_a))

        assert response.status_code == 201
        body = response.json()
        assert body["name"] == "Blue Bottle Coffee"
        assert body["platform"] == "google_maps"
        assert body["source_url"] == VALID_URL

    def test_ownership_comes_from_the_session_not_the_request_body(
        self, client_factory, user_a, user_b, app_session
    ):
        """A client-supplied owner id must never transfer ownership (S1-BR-010)."""
        response = client_factory(user_a).post(
            "/api/v1/analysis-targets",
            json={
                "name": "Blue Bottle Coffee",
                "source_url": VALID_URL,
                "owner_user_id": str(user_b.id),
            },
        )

        assert response.status_code == 201
        target = _load_target(app_session, response.json()["id"])
        assert target.owner_user_id == user_a.id

    def test_persisted_target_can_be_retrieved(self, client_factory, user_a):
        client = client_factory(user_a)
        created = _create_target(client).json()

        fetched = client.get(f"/api/v1/analysis-targets/{created['id']}")

        assert fetched.status_code == 200
        assert fetched.json() == created


class TestAnalysisTargetValidation:
    def test_rejects_a_missing_name(self, client_factory, user_a):
        response = client_factory(user_a).post(
            "/api/v1/analysis-targets", json={"source_url": VALID_URL}
        )

        assert response.status_code == 422
        assert response.json()["error"]["code"] == "validation_error"

    def test_rejects_a_blank_name(self, client_factory, user_a):
        response = _create_target(client_factory(user_a), name="")

        assert response.status_code == 422

    def test_rejects_a_missing_source_url(self, client_factory, user_a):
        response = client_factory(user_a).post(
            "/api/v1/analysis-targets", json={"name": "Blue Bottle Coffee"}
        )

        assert response.status_code == 422

    def test_rejects_a_malformed_source_url(self, client_factory, user_a):
        response = _create_target(client_factory(user_a), source_url="not-a-url")

        assert response.status_code == 422
        detail = response.json()["error"]["details"][0]
        assert detail["field"] == "source_url"

    def test_rejects_an_unsupported_platform_url(self, client_factory, user_a):
        response = _create_target(
            client_factory(user_a), source_url="https://www.yelp.com/biz/blue-bottle"
        )

        assert response.status_code == 422

    def test_invalid_input_is_not_persisted(self, client_factory, user_a):
        client = client_factory(user_a)
        _create_target(client, source_url="not-a-url")

        assert client.get("/api/v1/analysis-targets").json()["items"] == []


class TestListAnalysisTargets:
    def test_list_is_scoped_to_the_authenticated_owner(
        self, client_factory, user_a, user_b
    ):
        _create_target(client_factory(user_a), name="User A Cafe")
        _create_target(
            client_factory(user_b), name="User B Hotel", source_url=OTHER_URL
        )

        a_names = [
            item["name"]
            for item in client_factory(user_a)
            .get("/api/v1/analysis-targets")
            .json()["items"]
        ]
        b_names = [
            item["name"]
            for item in client_factory(user_b)
            .get("/api/v1/analysis-targets")
            .json()["items"]
        ]

        assert a_names == ["User A Cafe"]
        assert b_names == ["User B Hotel"]


class TestCrossUserAuthorization:
    def test_user_b_cannot_read_user_a_target(self, client_factory, user_a, user_b):
        target_id = _create_target(client_factory(user_a)).json()["id"]

        response = client_factory(user_b).get(f"/api/v1/analysis-targets/{target_id}")

        assert response.status_code == 404
        assert "Blue Bottle" not in response.text

    def test_user_b_cannot_rename_user_a_target(
        self, client_factory, user_a, user_b, app_session
    ):
        target_id = _create_target(client_factory(user_a)).json()["id"]

        response = client_factory(user_b).patch(
            f"/api/v1/analysis-targets/{target_id}", json={"name": "Hijacked"}
        )

        assert response.status_code == 404
        assert _load_target(app_session, target_id).name == "Blue Bottle Coffee"

    def test_user_b_cannot_delete_user_a_target(
        self, client_factory, user_a, user_b, app_session
    ):
        target_id = _create_target(client_factory(user_a)).json()["id"]

        response = client_factory(user_b).delete(
            f"/api/v1/analysis-targets/{target_id}"
        )

        assert response.status_code == 404
        assert _load_target(app_session, target_id) is not None

    def test_unknown_target_is_also_not_found(self, client_factory, user_a):
        response = client_factory(user_a).get(
            f"/api/v1/analysis-targets/{uuid.uuid4()}"
        )

        assert response.status_code == 404


class TestUnauthenticatedAccess:
    def test_listing_targets_requires_authentication(self, client_factory, user_a):
        _create_target(client_factory(user_a))

        response = client_factory().get("/api/v1/analysis-targets")

        assert response.status_code == 401
        assert "Blue Bottle" not in response.text

    def test_creating_a_target_requires_authentication(self, client_factory):
        response = _create_target(client_factory())

        assert response.status_code == 401


class TestRenameAndDelete:
    def test_owner_can_rename_their_target(self, client_factory, user_a):
        client = client_factory(user_a)
        target_id = _create_target(client).json()["id"]

        response = client.patch(
            f"/api/v1/analysis-targets/{target_id}", json={"name": "Mint Plaza"}
        )

        assert response.status_code == 200
        assert response.json()["name"] == "Mint Plaza"

    def test_owner_can_delete_their_target(self, client_factory, user_a):
        client = client_factory(user_a)
        target_id = _create_target(client).json()["id"]

        assert client.delete(f"/api/v1/analysis-targets/{target_id}").status_code == 204
        assert client.get(f"/api/v1/analysis-targets/{target_id}").status_code == 404


def _load_target(session, target_id):
    from app.db.models import AnalysisTarget

    session.expire_all()
    return session.get(AnalysisTarget, uuid.UUID(str(target_id)))
