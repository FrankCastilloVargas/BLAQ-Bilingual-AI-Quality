import pytest

from app.models.audit import Audit
from app.models.testcase import Category, TestCase
from app.services.responses import set_test_response
from app.services.review import TestNotFoundError


def make_audit():
    return Audit(client="ACME", product_name="Bot", reviewer="Reviewer", tests=[TestCase(
        test_id="A01", category=Category.ACCURACY, language="es-MX", scenario="Scenario",
        prompt="Prompt", expected_behavior="Expected"
    )])


def test_set_test_response_updates_only_actual_response():
    audit = make_audit()
    set_test_response(audit, "A01", "Respuesta real")
    assert audit.tests[0].actual_response == "Respuesta real"
    assert audit.tests[0].evaluation is None


def test_set_test_response_rejects_unknown_test():
    with pytest.raises(TestNotFoundError):
        set_test_response(make_audit(), "A99", "Response")
