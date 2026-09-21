import uuid

from app.db.models import AnalysisTarget, QAEntry, QAEvidence, Review
from app.domain import QAResultKind


def _target(session, user, name: str = "Blue Bottle Coffee") -> AnalysisTarget:
    target = AnalysisTarget(
        owner_user_id=user.id,
        name=name,
        platform="google_maps",
        source_url="https://www.google.com/maps/place/Blue+Bottle+Coffee",
    )
    session.add(target)
    session.commit()
    session.refresh(target)
    return target


def _review(session, target: AnalysisTarget, text: str) -> Review:
    review = Review(
        analysis_target_id=target.id,
        review_identity_key=f"source:{uuid.uuid4()}",
        review_text=text,
        rating=5,
        reviewer_name="Demo Reviewer",
        source_review_id="demo-review",
    )
    session.add(review)
    session.commit()
    session.refresh(review)
    return review


def _qa_entry(session, target: AnalysisTarget, review: Review) -> QAEntry:
    entry = QAEntry(
        analysis_target_id=target.id,
        question="What do customers like?",
        answer="Customers praise the coffee.",
        result_kind=QAResultKind.GROUNDED.value,
        provider="fake",
        model="fake-v1",
        context_review_count=1,
    )
    entry.evidence.append(
        QAEvidence(
            review_id=review.id,
            position=0,
            excerpt=review.review_text,
            rating=review.rating,
            reviewer_name=review.reviewer_name,
        )
    )
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry


def test_owner_can_export_current_reviews_to_csv(client_factory, app_session, user_a):
    target = _target(app_session, user_a)
    _review(app_session, target, "Excellent pour over.")
    client = client_factory(user_a)

    response = client.get(f"/api/v1/analysis-targets/{target.id}/exports/reviews.csv")

    assert response.status_code == 200
    assert (
        'filename="blue-bottle-coffee-reviews.csv"'
        in response.headers["content-disposition"]
    )
    assert "analysis_name,source_url,rating" in response.text
    assert "Excellent pour over." in response.text


def test_owner_can_export_analysis_to_markdown(client_factory, app_session, user_a):
    target = _target(app_session, user_a)
    review = _review(app_session, target, "Excellent pour over.")
    _qa_entry(app_session, target, review)
    client = client_factory(user_a)

    response = client.get(f"/api/v1/analysis-targets/{target.id}/exports/analysis.md")

    assert response.status_code == 200
    assert (
        'filename="blue-bottle-coffee-analysis.md"'
        in response.headers["content-disposition"]
    )
    assert "# Blue Bottle Coffee" in response.text
    assert "What do customers like?" in response.text
    assert "Excellent pour over." in response.text


def test_user_b_cannot_export_user_a_analysis(
    client_factory, app_session, user_a, user_b
):
    target = _target(app_session, user_a)
    _review(app_session, target, "USER_A_PRIVATE_EXPORT_PHRASE")

    response = client_factory(user_b).get(
        f"/api/v1/analysis-targets/{target.id}/exports/reviews.csv"
    )

    assert response.status_code == 404
    assert "USER_A_PRIVATE_EXPORT_PHRASE" not in response.text
