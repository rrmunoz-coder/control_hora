from __future__ import annotations

import pytest

pytest.importorskip("flask")
pytest.importorskip("flask_wtf")
pytest.importorskip("oracledb")
pytest.importorskip("ldap3")

from flask import Flask
from werkzeug.exceptions import Forbidden

from atlas import access


def _app() -> Flask:
    app = Flask(__name__)
    app.secret_key = "a" * 64
    return app


def test_admin_has_global_unit_scope():
    app = _app()
    with app.test_request_context("/"):
        assert access.accessible_unit_ids(10, "ADMIN") is None


def test_user_cannot_manage_units(monkeypatch):
    app = _app()
    monkeypatch.setattr(access, "accessible_unit_ids", lambda: {7})
    with app.test_request_context("/"):
        from flask import session
        session.update(id_usuario=10, rol_codigo="USUARIO")
        with pytest.raises(Forbidden):
            access.assert_unit_access(7, manage=True)


def test_manager_cannot_cross_unit_boundary(monkeypatch):
    app = _app()
    monkeypatch.setattr(access, "accessible_unit_ids", lambda: {7, 8})
    with app.test_request_context("/"):
        from flask import session
        session.update(id_usuario=10, rol_codigo="JEFE")
        access.assert_unit_access(8, manage=True)
        with pytest.raises(Forbidden):
            access.assert_unit_access(99, manage=True)
