from app.models.audit import Audit
from app.services.review import TestNotFoundError


def set_test_response(audit: Audit, test_id: str, actual_response: str) -> Audit:
    test = next((item for item in audit.tests if item.test_id == test_id), None)
    if test is None:
        raise TestNotFoundError(test_id)
    test.actual_response = actual_response
    return audit
