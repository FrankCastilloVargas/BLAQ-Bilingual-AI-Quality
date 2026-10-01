import json

import pytest

from app.models.audit_create import AuditCreateFromCatalog
from app.models.testcase import Category
from app.services.catalog import CatalogValidationError, create_audit_from_catalog, load_blaq25_catalog


def test_official_catalog_contains_exact_blaq25_structure():
    tests = load_blaq25_catalog()
    assert len(tests) == 25
    assert len({test.test_id for test in tests}) == 25
    assert all(sum(test.category == category for test in tests) == 5 for category in Category)
    assert all(test.actual_response is None for test in tests)
    assert all(test.evaluation is None for test in tests)


def test_create_audit_from_catalog_populates_metadata_and_tests():
    audit = create_audit_from_catalog(AuditCreateFromCatalog(
        client="ACME", product_name="Support Bot", model_version="v2", reviewer="Francisco"
    ))
    assert audit.client == "ACME"
    assert audit.product_name == "Support Bot"
    assert audit.model_version == "v2"
    assert audit.reviewer == "Francisco"
    assert len(audit.tests) == 25


def test_catalog_rejects_missing_official_test(tmp_path):
    source = load_blaq25_catalog()
    payload = {"tests": [test.model_dump(mode="json") for test in source[:-1]]}
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(CatalogValidationError, match="25 official unique"):
        load_blaq25_catalog(path)
