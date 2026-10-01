from app.models.evaluator import EvaluationProposal, EvaluationRequest
from app.services.evaluator import Evaluator, RuleBasedEvaluator


class HybridEvaluator(Evaluator):
    """LLM semantic proposal informed by deterministic BLAQ signals.

    The deterministic pass is evidence, not a second scoring authority. The
    returned proposal always remains provisional until explicit human review.
    """

    def __init__(self, semantic_evaluator: Evaluator, rules: Evaluator | None = None):
        self.semantic_evaluator = semantic_evaluator
        self.rules = rules or RuleBasedEvaluator()

    def evaluate(self, request: EvaluationRequest) -> EvaluationProposal:
        rule_proposal = self.rules.evaluate(request)
        semantic = self.semantic_evaluator.evaluate(request, rule_proposal=rule_proposal)
        semantic.evaluation.approved = False
        semantic.evaluation.human_review = None
        return semantic
