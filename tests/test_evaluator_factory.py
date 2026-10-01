import pytest
from app.services.evaluator import RuleBasedEvaluator
from app.services.evaluator_factory import build_evaluator


def test_factory_defaults_to_token_free_rule_based(monkeypatch):
    monkeypatch.delenv("BLAQ_EVALUATOR", raising=False)
    assert isinstance(build_evaluator(), RuleBasedEvaluator)


def test_factory_rejects_unknown_provider(monkeypatch):
    monkeypatch.setenv("BLAQ_EVALUATOR", "unknown")
    with pytest.raises(ValueError, match="Unsupported"):
        build_evaluator()
