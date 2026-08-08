from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("flask")
pytest.importorskip("flask_wtf")
pytest.importorskip("oracledb")
pytest.importorskip("ldap3")

from flask import Flask, session

from atlas.knowledge import access as knowledge_access
from atlas.knowledge.service import TRANSITIONS


def _config(path: Path, *, enabled: bool, storage: str = r"K:\ATLAS_DATA\conocimiento"):
    path.write_text(
        f"""
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
secret_key={'a' * 64}
port=5051
session_cookie_secure=false
[security]
force_https=false
trust_proxy_headers=false
session_idle_minutes=30
session_absolute_minutes=720
session_validation_seconds=120
max_failed_logins=5
max_failed_logins_ip=20
login_rate_window_minutes=15
login_lock_minutes=15
hsts_seconds=31536000
[features]
knowledge_enabled={'true' if enabled else 'false'}
[knowledge]
storage_path={storage}
max_file_mb=25
allowed_extensions=pdf,docx,xlsx,pptx,txt,csv,png,jpg,jpeg
antivirus_required=true
antivirus_command=
""".strip(),
        encoding="utf-8",
    )


def _app_context(role: str, user_id: int = 10):
    app = Flask(__name__)
    app.secret_key = "a" * 64
    ctx = app.test_request_context("/")
    ctx.push()
    session.update(id_usuario=user_id, rol_codigo=role)
    return ctx


def test_knowledge_is_disabled_by_default_when_sections_are_absent(tmp_path, monkeypatch):
    cfg = tmp_path / "config.ini"
    cfg.write_text(
        f"""
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
secret_key={'a' * 64}
port=5051
session_cookie_secure=false
[security]
force_https=false
trust_proxy_headers=false
session_idle_minutes=30
session_absolute_minutes=720
session_validation_seconds=120
max_failed_logins=5
max_failed_logins_ip=20
login_rate_window_minutes=15
login_lock_minutes=15
hsts_seconds=31536000
""".strip(), encoding="utf-8")
    monkeypatch.setenv("ATLAS_CONFIG", str(cfg))
    from atlas.config import load_config
    loaded = load_config()
    assert loaded["KNOWLEDGE_ENABLED"] is False
    assert loaded["KNOWLEDGE_MAX_FILE_MB"] == 25


def test_enabled_knowledge_requires_storage_path(tmp_path, monkeypatch):
    cfg = tmp_path / "config.ini"
    _config(cfg, enabled=True, storage="")
    monkeypatch.setenv("ATLAS_CONFIG", str(cfg))
    from atlas.config import load_config
    with pytest.raises(RuntimeError, match="storage_path"):
        load_config()


def test_app_registers_knowledge_blueprint_only_when_enabled(tmp_path, monkeypatch):
    from atlas import create_app

    cfg = tmp_path / "config.ini"
    _config(cfg, enabled=False)
    monkeypatch.setenv("ATLAS_CONFIG", str(cfg))
    app = create_app({"TESTING": True, "WTF_CSRF_ENABLED": False})
    assert "knowledge" not in app.blueprints

    _config(cfg, enabled=True)
    app = create_app({"TESTING": True, "WTF_CSRF_ENABLED": False})
    assert "knowledge" in app.blueprints


def test_regular_user_only_sees_published_internal_in_own_unit(monkeypatch):
    monkeypatch.setattr(knowledge_access, "accessible_unit_ids", lambda: {7})
    ctx = _app_context("USUARIO")
    try:
        base = {
            "id": 1, "activo": "S", "id_unidad": 7,
            "id_propietario": 99, "id_revisor": None,
            "estado": "PUBLICADO", "clasificacion": "INTERNO",
        }
        assert knowledge_access.can_view_document(base)
        assert not knowledge_access.can_view_document({**base, "clasificacion": "RESTRINGIDO"})
        assert not knowledge_access.can_view_document({**base, "estado": "BORRADOR"})
        assert not knowledge_access.can_view_document({**base, "id_unidad": 8})
    finally:
        ctx.pop()


def test_owner_can_edit_draft_but_not_published(monkeypatch):
    monkeypatch.setattr(knowledge_access, "accessible_unit_ids", lambda: {7})
    ctx = _app_context("USUARIO", 10)
    try:
        doc = {
            "id": 1, "activo": "S", "id_unidad": 7,
            "id_propietario": 10, "id_revisor": 20,
            "estado": "BORRADOR", "clasificacion": "INTERNO",
        }
        assert knowledge_access.can_edit_document(doc)
        assert not knowledge_access.can_edit_document({**doc, "estado": "PUBLICADO"})
    finally:
        ctx.pop()


def test_workflow_transition_graph_is_closed_and_expected():
    assert TRANSITIONS["BORRADOR"] == {"EN_REVISION"}
    assert TRANSITIONS["EN_REVISION"] == {"BORRADOR", "PUBLICADO"}
    assert TRANSITIONS["PUBLICADO"] == {"REQUIERE_ACTUALIZACION", "OBSOLETO"}
    assert TRANSITIONS["REQUIERE_ACTUALIZACION"] == {"BORRADOR", "OBSOLETO"}
    assert TRANSITIONS["OBSOLETO"] == set()
