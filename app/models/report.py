from pydantic import BaseModel, Field


class CategoryReport(BaseModel):
    raw_points: int
    approved_tests: int
    expected_tests: int = 5
    max_points: int = 20
    percentage: float | None = None


class ReportFinding(BaseModel):
    test_id: str
    category: str
    severity: str
    finding: str
    business_impact: str
    recommendation: str


class AuditReport(BaseModel):
    audit_id: str
    client: str
    product_name: str
    model_version: str | None = None
    reviewer: str
    audit_date: str
    status: str
    executive_summary: str
    blaq_score: int | None = None
    provisional_percentage: float | None = None
    approved_tests: int
    total_tests: int
    category_scores: dict[str, CategoryReport]
    severity_counts: dict[str, int]
    priority_findings: list[ReportFinding] = Field(default_factory=list)
