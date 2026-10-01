from pydantic import BaseModel, Field

from app.models.evaluation import Evaluation, Scores, Severity, Scores, Severity


class EvaluationRequest(BaseModel):
    test_id: str
    category: str
    language: str
    scenario: str
    prompt: str
    expected_behavior: str
    actual_response: str = Field(min_length=1)


class LLMEvaluationResult(BaseModel):
    scores: Scores
    severity: Severity
    finding: str
    business_impact: str
    recommendation: str
    rationale: str


class LLMEvaluationResult(BaseModel):
    scores: Scores
    severity: Severity
    finding: str
    business_impact: str
    recommendation: str
    rationale: str


class EvaluationProposal(BaseModel):
    test_id: str
    evaluation: Evaluation
    evaluator: str
    rationale: str
