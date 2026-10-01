from fastapi import APIRouter

from app.models.audit import Audit
from app.models.evaluation import Evaluation, EvaluationSummary
from app.models.evaluator import EvaluationProposal, EvaluationRequest
from app.services.evaluator import RuleBasedEvaluator
from app.services.scoring import summarize_audit, summarize_evaluation

router = APIRouter()
evaluator = RuleBasedEvaluator()


@router.post("/propose", response_model=EvaluationProposal)
def propose_evaluation(request: EvaluationRequest) -> EvaluationProposal:
    """Generate a provisional evaluation that always requires human review."""
    return evaluator.evaluate(request)


@router.post("/score", response_model=EvaluationSummary)
def score_evaluation(evaluation: Evaluation) -> EvaluationSummary:
    return summarize_evaluation(evaluation)


@router.post("/audit-summary")
def score_audit(audit: Audit) -> dict:
    """Aggregate only human-approved test evaluations."""
    return summarize_audit(audit)
