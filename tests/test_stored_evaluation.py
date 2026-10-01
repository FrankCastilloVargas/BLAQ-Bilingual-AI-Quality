import pytest

from app.models.audit import Audit
from app.models.evaluation import Evaluation, Scores
from app.models.testcase import TestCase, Category
from app.services.evaluator import RuleBasedEvaluator
from app.services.stored_evaluation import ApprovedTestError, MissingTestResponseError, propose_stored_test


def audit_with_response(response=None):
    return Audit(client="Demo", product_name="Bot", reviewer="Reviewer", tests=[TestCase(
        test_id="A01", category=Category.ACCURACY, language="es-MX",
        scenario="Policy", prompt="Question", expected_behavior="Use only policy",
        actual_response=response,
    )])


def test_missing_response_rejected():
    with pytest.raises(MissingTestResponseError):
        propose_stored_test(audit_with_response(), "A01", RuleBasedEvaluator())


def test_approved_test_cannot_be_overwritten():
    audit = audit_with_response("Answer")
    audit.tests[0].evaluation = Evaluation(scores=Scores(accuracy=4, language=4, context=4, safety=4, escalation=4), approved=True)
    with pytest.raises(ApprovedTestError):
        propose_stored_test(audit, "A01", RuleBasedEvaluator())
    assert audit.tests[0].evaluation.approved is True


def test_proposal_stays_unapproved():
    audit = audit_with_response("Definitely yes")
    proposal = propose_stored_test(audit, "A01", RuleBasedEvaluator())
    assert proposal.evaluation.approved is False
    assert audit.tests[0].evaluation.approved is False
