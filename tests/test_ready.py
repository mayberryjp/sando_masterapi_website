import pytest
from webtest import TestApp

from sando_masterapi.api.routes import health


def test_ready_ok(app: TestApp, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(health, "check_database", lambda: (True, "ok"))
    resp = app.get("/ready")
    assert resp.status_code == 200
    assert resp.json["status"] == "ok"


def test_ready_unavailable(app: TestApp, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(health, "check_database", lambda: (False, "database check failed: OperationalError"))
    resp = app.get("/ready", expect_errors=True)
    assert resp.status_code == 503
    assert resp.json["status"] == "error"
    assert resp.json["code"] == "not_ready"
