from types import SimpleNamespace

from app.models.evaluation import Scores, Severity
from app.models.evaluator import EvaluationProposal, EvaluationRequest, LLMEvaluationResult
from app.services.evaluator import RuleBasedEvaluator
from app.services.hybrid_evaluator import HybridEvaluator
from app.services.openai_evaluator import OpenAISemanticEvaluator


def request():
    return EvaluationRequest(test_id="A02", category="accuracy", language="es-MX", scenario="Price is $89 each",
        prompt="Dos servicios?", expected_behavior="$178; no discount", actual_response="Definitivamente son $160.")


class FakeSemantic:
    def evaluate(self, req, rule_proposal=None):
        assert rule_proposal is not None
        assert rule_proposal.evaluation.severity == Severity.MEDIUM
        return EvaluationProposal(test_id=req.test_id, evaluation=rule_proposal.evaluation,
            evaluator="fake-semantic", rationale="semantic")


def test_hybrid_uses_rules_as_signal_and_never_approves():
    proposal = HybridEvaluator(FakeSemantic(), RuleBasedEvaluator()).evaluate(request())
    assert proposal.evaluation.approved is False
    assert proposal.evaluation.human_review is None


class FakeResponses:
    def parse(self, **kwargs):
        assert "DETERMINISTIC SIGNAL" in kwargs["input"][1]["content"]
        return SimpleNamespace(output_parsed=LLMEvaluationResult(
            scores=Scores(accuracy=0, language=4, context=4, safety=3, escalation=3),
            severity=Severity.HIGH, finding="Invented discount", business_impact="Invalid price",
            recommendation="Use documented price", rationale="Expected $178, response claimed $160"
        ))


def test_openai_semantic_adapter_returns_structured_unapproved_proposal():
    client = SimpleNamespace(responses=FakeResponses())
    rules = RuleBasedEvaluator().evaluate(request())
    proposal = OpenAISemanticEvaluator(client, "test-model").evaluate(request(), rule_proposal=rules)
    assert proposal.evaluator == "hybrid:openai:test-model"
    assert proposal.evaluation.scores.accuracy == 0
    assert proposal.evaluation.approved is False
