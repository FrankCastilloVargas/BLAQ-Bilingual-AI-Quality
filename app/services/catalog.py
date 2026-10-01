import json
from collections import Counter
from pathlib import Path

from app.models.audit import Audit
from app.models.audit_create import AuditCreateFromCatalog
from app.models.testcase import Category, TestCase
from app.services.scoring import EXPECTED_IDS

CATALOG_PATH = Path(__file__).resolve().parents[2] / "data" / "blaq25.json"


class CatalogValidationError(ValueError):
    pass


def load_blaq25_catalog(path: Path = CATALOG_PATH) -> list[TestCase]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    tests = [TestCase.model_validate(item) for item in payload.get("tests", [])]
    ids = [test.test_id for test in tests]
    counts = Counter(test.category for test in tests)

    if len(tests) != 25 or len(set(ids)) != 25 or set(ids) != EXPECTED_IDS:
        raise CatalogValidationError("BLAQ-25 catalog must contain exactly the 25 official unique test IDs.")
    if any(counts[category] != 5 for category in Category):
        raise CatalogValidationError("BLAQ-25 catalog must contain exactly five tests per category.")
    return tests


def create_audit_from_catalog(request: AuditCreateFromCatalog) -> Audit:
    return Audit(
        client=request.client,
        product_name=request.product_name,
        model_version=request.model_version,
        reviewer=request.reviewer,
        tests=load_blaq25_catalog(),
    )
