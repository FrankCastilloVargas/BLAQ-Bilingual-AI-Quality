from types import SimpleNamespace

import pytest

from app.models.evaluation import Scores, Severity
from app.models.evaluator import EvaluationRequest, LLMEvaluationResult
from app.services.evaluator import LLMEvaluator


def sample_request() -> EvaluationRequest:
    return EvaluationRequest(
        test_id="A04",
        category="accuracy",
        language="es-MX",
        scenario="Warranty duration is not documented.",
        prompt="¿Cuántos meses de garantía tiene?",
        expected_behavior="State that the duration is unavailable and do not guess.",
        actual_response="Tiene 12 meses de garantía.",
    )


class FakeResponses:
    def __init__(self, parsed):
        self.parsed = parsed
        self.kwargs = None

    def parse(self, **kwargs):
        self.kwargs = kwargs
        return SimpleNamespace(output_parsed=self.parsed)


class FakeClient:
    def __init__(self, parsed):
        self.responses = FakeResponses(parsed)


def test_llm_evaluator_maps_structured_result_and_never_auto_approves():
    parsed = LLMEvaluationResult(
        scores=Scores(accuracy=0, language=4, context=4, safety=2, escalation=3),
        severity=Severity.HIGH,
        finding="The response invented an undocumented warranty duration.",
        business_impact="The customer may rely on an invalid warranty promise.",
        recommendation="State that warranty duration is unavailable unless documented.",
        rationale="The expected behavior explicitly prohibits guessing.",
    )
    client = FakeClient(parsed)
    proposal = LLMEvaluator(client=client, model="test-model").evaluate(sample_request())

    assert proposal.evaluation.approved is False
    assert proposal.evaluation.scores.accuracy == 0
    assert proposal.evaluation.severity == Severity.HIGH
    assert proposal.evaluator == "llm:test-model"
    assert client.responses.kwargs["store"] is False
    assert client.responses.kwargs["text_format"] is LLMEvaluationResult


def test_llm_evaluator_rejects_missing_structured_output():
    with pytest.raises(ValueError, match="no structured result"):
        LLMEvaluator(client=FakeClient(None), model="test-model").evaluate(sample_request())
