from enum import Enum

from pydantic import BaseModel, Field


class Severity(str, Enum):
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Scores(BaseModel):
    accuracy: int = Field(ge=0, le=4)
    language: int = Field(ge=0, le=4)
    context: int = Field(ge=0, le=4)
    safety: int = Field(ge=0, le=4)
    escalation: int = Field(ge=0, le=4)


class Evaluation(BaseModel):
    scores: Scores
    severity: Severity = Severity.NONE
    finding: str = ""
    business_impact: str = ""
    recommendation: str = ""
    ai_evaluation: str | None = None
    human_review: str | None = None
    approved: bool = False


class EvaluationSummary(BaseModel):
    total_score: int
    percentage: float
    severity: Severity
    approved: bool
