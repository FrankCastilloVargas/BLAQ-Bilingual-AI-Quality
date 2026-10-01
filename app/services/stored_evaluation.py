from app.models.audit import Audit
from app.models.evaluator import EvaluationRequest, EvaluationProposal
from app.services.evaluator import Evaluator
from app.services.review import TestNotFoundError


class MissingTestResponseError(ValueError):
    pass


class ApprovedTestError(ValueError):
    pass


def propose_stored_test(audit: Audit, test_id: str, evaluator: Evaluator) -> EvaluationProposal:
    test = next((item for item in audit.tests if item.test_id == test_id), None)
    if test is None:
        raise TestNotFoundError(test_id)
    if test.evaluation is not None and test.evaluation.approved:
        raise ApprovedTestError("Approved evaluations cannot be overwritten by automation.")
    if not test.actual_response or not test.actual_response.strip():
        raise MissingTestResponseError("Capture a test response before proposing an evaluation.")
    request = EvaluationRequest(
        test_id=test.test_id, category=test.category.value, language=test.language,
        scenario=test.scenario, prompt=test.prompt,
        expected_behavior=test.expected_behavior, actual_response=test.actual_response,
    )
    proposal = evaluator.evaluate(request)
    # Never trust an evaluator to approve or change the test identity.
    if proposal.test_id != test.test_id:
        raise ValueError("Evaluator returned a mismatched test ID.")
    proposal.evaluation.approved = False
    proposal.evaluation.human_review = None
    test.evaluation = proposal.evaluation
    return proposal
