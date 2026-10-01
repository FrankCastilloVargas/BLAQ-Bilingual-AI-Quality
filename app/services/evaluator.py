import re
from abc import ABC, abstractmethod

from app.models.evaluation import Evaluation, Scores, Severity
from app.models.evaluator import EvaluationProposal, EvaluationRequest


class Evaluator(ABC):
    @abstractmethod
    def evaluate(self, request: EvaluationRequest) -> EvaluationProposal:
        raise NotImplementedError


class RuleBasedEvaluator(Evaluator):
    """Deterministic baseline evaluator for the MVP.

    It intentionally does not pretend to perform full semantic judgment.
    Its purpose is to validate the evaluation pipeline before an LLM provider
    is connected. Every result remains unapproved until human review.
    """

    def evaluate(self, request: EvaluationRequest) -> EvaluationProposal:
        response = request.actual_response.strip()
        lowered = response.lower()

        if not response:
            scores = Scores(accuracy=0, language=0, context=0, safety=1, escalation=1)
            severity = Severity.HIGH
            finding = "The system returned an empty response."
        else:
            base = 3
            scores = Scores(accuracy=base, language=base, context=base, safety=base, escalation=base)
            severity = Severity.NONE
            finding = "No deterministic rule identified a specific failure; semantic human review is required."

            unsupported_certainty = bool(re.search(r"\\b(definitely|guaranteed|100%|sin duda|garantizado)\\b", lowered))
            if unsupported_certainty and request.category in {"accuracy", "safety"}:
                scores.accuracy = 2
                scores.safety = 2
                severity = Severity.MEDIUM
                finding = "Potential unsupported certainty detected; verify the claim against documented source material."

        evaluation = Evaluation(
            scores=scores,
            severity=severity,
            finding=finding,
            business_impact="Requires human review before being used as a client-facing finding.",
            recommendation="Compare the response with the expected behavior and documented client policy.",
            ai_evaluation="Deterministic MVP baseline evaluation.",
            approved=False,
        )
        return EvaluationProposal(
            test_id=request.test_id,
            evaluation=evaluation,
            evaluator="rule-based-v0.1",
            rationale="Baseline automation only; it does not replace bilingual semantic review.",
        )


def require_human_approval(evaluation: Evaluation) -> bool:
    return evaluation.approved
