from app.models.audit import Audit
from app.models.evaluation import Evaluation
from app.models.review import HumanReview


class TestNotFoundError(KeyError):
    pass


def approve_test(audit: Audit, test_id: str, review: HumanReview) -> Audit:
    test = next((item for item in audit.tests if item.test_id == test_id), None)
    if test is None:
        raise TestNotFoundError(test_id)

    ai_evaluation = test.evaluation.ai_evaluation if test.evaluation else None
    test.evaluation = Evaluation(
        scores=review.scores,
        severity=review.severity,
        finding=review.finding,
        business_impact=review.business_impact,
        recommendation=review.recommendation,
        ai_evaluation=ai_evaluation,
        human_review=review.review_notes,
        approved=True,
    )
    return audit
