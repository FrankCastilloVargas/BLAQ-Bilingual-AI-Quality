from enum import Enum

from pydantic import BaseModel

from app.models.evaluation import Evaluation


class Category(str, Enum):
    ACCURACY = "accuracy"
    LANGUAGE = "language"
    CONTEXT = "context"
    SAFETY = "safety"
    ESCALATION = "escalation"


class TestCase(BaseModel):
    test_id: str
    category: Category
    language: str
    scenario: str
    prompt: str
    expected_behavior: str
    actual_response: str | None = None
    evaluation: Evaluation | None = None
