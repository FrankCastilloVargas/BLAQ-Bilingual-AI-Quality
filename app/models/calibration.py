from typing import Literal
from pydantic import BaseModel, Field
from app.models.evaluation import Scores, Severity
from app.models.evaluator import EvaluationRequest

class BlindReviewItem(BaseModel):
    case_id: str
    source_test_id: str
    request: EvaluationRequest
    reviewer_scores: Scores | None = None
    reviewer_severity: Severity | None = None
    reviewer_finding: str = ""
    reviewer_business_impact: str = ""
    reviewer_recommendation: str = ""
    reviewer_notes: str = ""

class BlindReviewBatch(BaseModel):
    batch_id: str
    dataset_version: str
    dimension: Literal["accuracy", "language", "context", "safety", "escalation"]
    reviewer: str = ""
    status: Literal["pending", "in_progress", "complete"] = "pending"
    items: list[BlindReviewItem] = Field(default_factory=list)
