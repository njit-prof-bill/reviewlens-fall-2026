import re
import uuid

from app.db.models import AnalysisTarget, Review
from app.domain import QAResultKind
from app.services import qa_service
from app.services.llm import LLMProviderError, LLMRequest, LLMResult


class FakeProvider:
    name = "fake"
    model = "deterministic-v1"

    def __init__(self, result: LLMResult):
        self.result = result
        self.requests: list[LLMRequest] = []

    async def answer(self, request: LLMRequest) -> LLMResult:
        self.requests.append(request)
        return self.result


class FailingProvider:
    name = "fake"
    model = "deterministic-v1"

    async def answer(self, request: LLMRequest) -> LLMResult:
        raise LLMProviderError("The AI service is temporarily unavailable.")


class ContextEchoProvider:
    name = "fake"
    model = "context-echo-v1"

    def __init__(self):
        self.requests: list[LLMRequest] = []

    async def answer(self, request: LLMRequest) -> LLMResult:
        self.requests.append(request)
        review_id = re.search(r"review_id=([^\]]+)", request.review_context)
        assert review_id is not None
        return LLMResult(
            answer="Answer from the active target.",
            result_kind=QAResultKind.GROUNDED,
            evidence_review_ids=(review_id.group(1),),
        )


def _target(session, user, name: str) -> AnalysisTarget:
    target = AnalysisTarget(
        owner_user_id=user.id,
        name=name,
        platform="google_maps",
        source_url=f"https://www.google.com/maps/place/{name.replace(' ', '+')}",
    )
    session.add(target)
    session.commit()
    session.refresh(target)
    return target


def _review(session, target: AnalysisTarget, text: str, rating: float = 5) -> Review:
    review = Review(
        analysis_target_id=target.id,
        review_text=text,
        rating=rating,
        reviewer_name="Demo Reviewer",
    )
    session.add(review)
    session.commit()
    session.refresh(review)
    return review


def test_grounded_answer_persists_validated_evidence_and_history(
    client_factory, app_session, user_a, monkeypatch
):
    target = _target(app_session, user_a, "Battery Cafe")
    review = _review(app_session, target, "Battery life is excellent.")
    provider = FakeProvider(
        LLMResult(
            answer="Customers praise the battery life.",
            result_kind=QAResultKind.GROUNDED,
            evidence_review_ids=(str(review.id),),
        )
    )
    monkeypatch.setattr(qa_service, "get_llm_provider", lambda: provider)
    client = client_factory(user_a)

    response = client.post(
        f"/api/v1/analysis-targets/{target.id}/questions",
        json={"question": "What do customers like?"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["analysis_target_id"] == str(target.id)
    assert body["result_kind"] == "grounded"
    assert body["evidence"] == [
        {
            "review_id": str(review.id),
            "excerpt": "Battery life is excellent.",
            "rating": 5.0,
            "reviewer_name": "Demo Reviewer",
            "reviewed_at": None,
        }
    ]
    assert "Active entity: Battery Cafe" in provider.requests[0].system_prompt
    assert "Review platform: google_maps" in provider.requests[0].system_prompt
    assert "Battery life is excellent." in provider.requests[0].review_context

    history = client.get(f"/api/v1/analysis-targets/{target.id}/questions").json()
    assert [item["id"] for item in history["items"]] == [body["id"]]


def test_context_contains_only_the_owned_active_target(
    client_factory, app_session, user_a, user_b, monkeypatch
):
    target_a = _target(app_session, user_a, "Target A")
    target_b = _target(app_session, user_b, "Target B")
    _review(app_session, target_a, "USER_A_PRIVATE_BATTERY_PHRASE")
    review_b = _review(app_session, target_b, "USER_B_SERVICE_PHRASE")
    provider = FakeProvider(
        LLMResult(
            answer="Service is frequently praised.",
            result_kind=QAResultKind.GROUNDED,
            evidence_review_ids=(str(review_b.id),),
        )
    )
    monkeypatch.setattr(qa_service, "get_llm_provider", lambda: provider)

    response = client_factory(user_b).post(
        f"/api/v1/analysis-targets/{target_b.id}/questions",
        json={"question": "What stands out?"},
    )

    assert response.status_code == 201
    context = provider.requests[0].review_context
    assert "USER_B_SERVICE_PHRASE" in context
    assert "USER_A_PRIVATE_BATTERY_PHRASE" not in context

    denied = client_factory(user_b).get(
        f"/api/v1/analysis-targets/{target_a.id}/questions"
    )
    assert denied.status_code == 404
    assert "USER_A_PRIVATE_BATTERY_PHRASE" not in denied.text


def test_switching_owned_targets_rebuilds_context_without_stale_reviews(
    client_factory, app_session, user_a, monkeypatch
):
    target_a = _target(app_session, user_a, "Battery Shop")
    target_b = _target(app_session, user_a, "Service Desk")
    _review(app_session, target_a, "TARGET_A_BATTERY_ONLY")
    _review(app_session, target_b, "TARGET_B_SERVICE_ONLY")
    provider = ContextEchoProvider()
    monkeypatch.setattr(qa_service, "get_llm_provider", lambda: provider)
    client = client_factory(user_a)

    first = client.post(
        f"/api/v1/analysis-targets/{target_a.id}/questions",
        json={"question": "What stands out?"},
    )
    second = client.post(
        f"/api/v1/analysis-targets/{target_b.id}/questions",
        json={"question": "What stands out?"},
    )

    assert first.status_code == 201
    assert second.status_code == 201
    assert "TARGET_A_BATTERY_ONLY" in provider.requests[0].review_context
    assert "TARGET_B_SERVICE_ONLY" not in provider.requests[0].review_context
    assert "TARGET_B_SERVICE_ONLY" in provider.requests[1].review_context
    assert "TARGET_A_BATTERY_ONLY" not in provider.requests[1].review_context


def test_out_of_scope_answer_has_no_evidence(
    client_factory, app_session, user_a, monkeypatch
):
    target = _target(app_session, user_a, "Scope Cafe")
    _review(app_session, target, "Friendly staff.")
    provider = FakeProvider(
        LLMResult(
            answer="I can only answer questions about Scope Cafe reviews.",
            result_kind=QAResultKind.OUT_OF_SCOPE,
        )
    )
    monkeypatch.setattr(qa_service, "get_llm_provider", lambda: provider)

    response = client_factory(user_a).post(
        f"/api/v1/analysis-targets/{target.id}/questions",
        json={"question": "What is the weather?"},
    )

    assert response.status_code == 201
    assert response.json()["result_kind"] == "out_of_scope"
    assert response.json()["evidence"] == []


def test_empty_target_does_not_call_provider(
    client_factory, app_session, user_a, monkeypatch
):
    target = _target(app_session, user_a, "Empty Cafe")

    def unexpected_provider_call():
        raise AssertionError("Provider must not be created for an empty target")

    monkeypatch.setattr(qa_service, "get_llm_provider", unexpected_provider_call)
    response = client_factory(user_a).post(
        f"/api/v1/analysis-targets/{target.id}/questions",
        json={"question": "What do customers like?"},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_invalid_evidence_is_rejected_without_persisting_history(
    client_factory, app_session, user_a, monkeypatch
):
    target = _target(app_session, user_a, "Evidence Cafe")
    _review(app_session, target, "Quiet atmosphere.")
    provider = FakeProvider(
        LLMResult(
            answer="This answer cites another dataset.",
            result_kind=QAResultKind.GROUNDED,
            evidence_review_ids=(str(uuid.uuid4()),),
        )
    )
    monkeypatch.setattr(qa_service, "get_llm_provider", lambda: provider)
    client = client_factory(user_a)

    response = client.post(
        f"/api/v1/analysis-targets/{target.id}/questions",
        json={"question": "What is the atmosphere?"},
    )

    assert response.status_code == 503
    history = client.get(f"/api/v1/analysis-targets/{target.id}/questions")
    assert history.json()["items"] == []


def test_provider_failure_is_safe_and_not_persisted(
    client_factory, app_session, user_a, monkeypatch
):
    target = _target(app_session, user_a, "Failure Cafe")
    _review(app_session, target, "Good coffee.")
    monkeypatch.setattr(qa_service, "get_llm_provider", lambda: FailingProvider())
    client = client_factory(user_a)

    response = client.post(
        f"/api/v1/analysis-targets/{target.id}/questions",
        json={"question": "What do customers like?"},
    )

    assert response.status_code == 503
    assert response.json() == {
        "error": {
            "code": "service_unavailable",
            "message": "The AI service is temporarily unavailable.",
            "details": [],
        }
    }
    history = client.get(f"/api/v1/analysis-targets/{target.id}/questions")
    assert history.json()["items"] == []


def test_missing_provider_key_returns_safe_503_not_500(
    client_factory, app_session, user_a, monkeypatch
):
    """Regression: factory errors (e.g. OPENAI_API_KEY unset) must not become 500."""
    target = _target(app_session, user_a, "Unconfigured Cafe")
    _review(app_session, target, "Good coffee.")

    def _raise_unconfigured():
        raise LLMProviderError("Review Q&A is not configured on this server.")

    monkeypatch.setattr(qa_service, "get_llm_provider", _raise_unconfigured)
    client = client_factory(user_a)

    response = client.post(
        f"/api/v1/analysis-targets/{target.id}/questions",
        json={"question": "What do customers like?"},
    )

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "service_unavailable"
    assert "not configured" in response.json()["error"]["message"]
    history = client.get(f"/api/v1/analysis-targets/{target.id}/questions")
    assert history.json()["items"] == []
