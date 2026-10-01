from datetime import date
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.models.testcase import TestCase


class Audit(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    client: str
    product_name: str
    model_version: str | None = None
    audit_date: date = Field(default_factory=date.today)
    reviewer: str
    tests: list[TestCase] = Field(default_factory=list)
