from pydantic import BaseModel

from app.models.evaluation import Scores, Severity


class HumanReview(BaseModel):
    scores: Scores
    severity: Severity
    finding: str
    business_impact: str
    recommendation: str
    review_notes: str = ""
