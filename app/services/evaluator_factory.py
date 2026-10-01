import os

from app.services.evaluator import RuleBasedEvaluator
from app.services.hybrid_evaluator import HybridEvaluator
from app.services.openai_evaluator import OpenAISemanticEvaluator


def build_evaluator():
    provider = os.getenv("BLAQ_EVALUATOR", "rule-based").strip().lower()
    if provider == "rule-based":
        return RuleBasedEvaluator()
    if provider != "hybrid-openai":
        raise ValueError(f"Unsupported BLAQ_EVALUATOR: {provider}")
    from openai import OpenAI
    model = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
    return HybridEvaluator(OpenAISemanticEvaluator(OpenAI(), model=model))
