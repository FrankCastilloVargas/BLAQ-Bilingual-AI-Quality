from app.models.evaluation import Evaluation


def require_human_approval(evaluation: Evaluation) -> bool:
    """BLAQ automated evaluations remain provisional until human approval."""
    return evaluation.approved
