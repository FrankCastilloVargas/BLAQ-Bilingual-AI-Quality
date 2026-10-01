from fastapi import APIRouter

from app.models.evaluation import Evaluation, EvaluationSummary
from app.services.scoring import summarize_evaluation

router = APIRouter()


@router.post("/score", response_model=EvaluationSummary)
def score_evaluation(evaluation: Evaluation) -> EvaluationSummary:
    return summarize_evaluation(evaluation)
