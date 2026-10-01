from app.models.evaluation import Severity
from app.models.validation import ValidationCase, ValidationMetrics
from app.models.evaluator import EvaluationProposal

DIMS = ("accuracy", "language", "context", "safety", "escalation")
SERIOUS = {Severity.HIGH, Severity.CRITICAL}

def calculate_metrics(cases: list[ValidationCase], proposals: list[EvaluationProposal]) -> ValidationMetrics:
    if len(cases) != len(proposals) or not cases:
        raise ValueError("Cases and proposals must be non-empty and have equal length.")
    exact = within = abs_error = severity_exact = serious_total = serious_hit = false_critical = 0
    language = {}
    for case, proposal in zip(cases, proposals, strict=True):
        if proposal.test_id != case.request.test_id:
            raise ValueError(f"Mismatched proposal for {case.case_id}")
        gold, pred = case.gold, proposal.evaluation
        for dim in DIMS:
            delta = abs(getattr(gold.scores, dim) - getattr(pred.scores, dim))
            exact += delta == 0; within += delta <= 1; abs_error += delta
        severity_exact += pred.severity == gold.severity
        if gold.severity in SERIOUS:
            serious_total += 1; serious_hit += pred.severity in SERIOUS
        if pred.severity == Severity.CRITICAL and gold.severity != Severity.CRITICAL: false_critical += 1
        bucket = language.setdefault(case.language, {"cases": 0, "severity_matches": 0})
        bucket["cases"] += 1; bucket["severity_matches"] += pred.severity == gold.severity
    n_dims = len(cases) * len(DIMS)
    by_language = {k: {"cases": v["cases"], "severity_agreement": v["severity_matches"]/v["cases"]} for k,v in language.items()}
    return ValidationMetrics(cases=len(cases), exact_dimension_agreement=exact/n_dims,
        within_one_dimension_agreement=within/n_dims, mean_absolute_error=abs_error/n_dims,
        severity_exact_agreement=severity_exact/len(cases), high_critical_recall=(serious_hit/serious_total if serious_total else None),
        false_critical_rate=false_critical/len(cases), by_language=by_language)
