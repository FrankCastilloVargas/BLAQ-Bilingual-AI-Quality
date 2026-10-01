from typing import Literal
from pydantic import BaseModel, Field
from app.models.evaluation import Scores, Severity
from app.models.evaluator import EvaluationRequest

class GoldLabel(BaseModel):
    scores: Scores
    severity: Severity
    finding: str
    business_impact: str
    recommendation: str
    reviewer: str
    review_status: Literal["seed", "independent", "consensus"] = "seed"

class ValidationCase(BaseModel):
    case_id: str
    source_test_id: str
    language: str
    case_type: Literal["typical", "edge", "adversarial"]
    request: EvaluationRequest
    gold: GoldLabel
    tags: list[str] = Field(default_factory=list)

class ValidationDataset(BaseModel):
    name: str
    version: str
    status: Literal["seed", "calibrated", "validated"] = "seed"
    cases: list[ValidationCase]

class ValidationMetrics(BaseModel):
    cases: int
    exact_dimension_agreement: float
    within_one_dimension_agreement: float
    mean_absolute_error: float
    severity_exact_agreement: float
    high_critical_recall: float | None
    false_critical_rate: float
    by_language: dict[str, dict[str, float | int]]
