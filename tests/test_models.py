import pytest
from pydantic import ValidationError

from app.models.evaluation import Scores


def test_score_must_be_between_zero_and_four():
    with pytest.raises(ValidationError):
        Scores(accuracy=5, language=4, context=4, safety=4, escalation=4)
