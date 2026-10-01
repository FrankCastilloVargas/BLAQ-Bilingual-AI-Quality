from pydantic import BaseModel, Field

from app.models.evaluation import Evaluation


class EvaluationRequest(BaseModel):
    test_id: str
    category: str
    language: str
    scenario: str
    prompt: str
    expected_behavior: str
    actual_response: str = Field(min_length=1)


class EvaluationProposal(BaseModel):
    test_id: str
    evaluation: Evaluation
    evaluator: str
    rationale: str
