from __future__ import annotations

from pathlib import Path
import time

import pytest

pytest.importorskip("flask")
pytest.importorskip("flask_wtf")
pytest.importorskip("oracledb")
pytest.importorskip("ldap3")


def _config(path: Path):
    path.write_text(
        """
[oracle]
user=test
password=test
dsn=test
thick_mode=false
[ldap]
enabled=false
servers=
validate_certificate=true
tls_ciphers=DEFAULT
[flask]
secret_key=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
port=5050
session_cookie_secure=false
[security]
force_https=false
trust_proxy_headers=false
session_idle_minutes=30
session_absolute_minutes=720
session_validation_seconds=1
max_failed_logins=5
login_lock_minutes=15
hsts_seconds=31536000
""".strip(),
        encoding="utf-8",
    )


@pytest.fixture()
def app(tmp_path, monkeypatch):
    config = tmp_path / "config.ini"
    _config(config)
    monkeypatch.setenv("ATLAS_CONFIG", str(config))
    from atlas import create_app
    return create_app({"TESTING": True, "WTF_CSRF_ENABLED": False})


def _login_session(client, *, version=1, last_activity=None, login_at=None):
    now = int(time.time())
    with client.session_transaction() as session:
        session.update(
            id_usuario=10,
            usuario="tester",
            nombre="Tester",
            rol_codigo="USUARIO",
            rol_nombre="Usuario",
            tipo_autenticacion="LDAP",
            session_version=version,
            login_at=login_at or now,
            last_activity=last_activity or now,
            last_validation=0,
        )


def test_security_headers_are_added(app):
    response = app.test_client().get("/login")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "default-src 'self'" in response.headers["Content-Security-Policy"]
    assert response.headers.get("X-Request-ID")


def test_revoked_session_is_invalidated(app, monkeypatch):
    client = app.test_client()
    _login_session(client, version=1)
    monkeypatch.setattr(
        "atlas.security.load_session_user",
        lambda _user_id: {
            "id_usuario": 10,
            "usuario": "tester",
            "nombre": "Tester",
            "usuario_activo": "S",
            "rol_codigo": "USUARIO",
            "rol_nombre": "Usuario",
            "rol_activo": "S",
            "tipo_autenticacion": "LDAP",
            "session_version": 2,
        },
    )
    response = client.get("/dashboard", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]
    with client.session_transaction() as session:
        assert "id_usuario" not in session


def test_idle_session_is_invalidated(app):
    client = app.test_client()
    _login_session(client, last_activity=int(time.time()) - 31 * 60)
    response = client.get("/dashboard", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]
