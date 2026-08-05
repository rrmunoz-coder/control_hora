from pathlib import Path
import re

from jinja2 import Environment

ROOT = Path(__file__).resolve().parents[1]


def test_weekly_workflow_states_are_consistent():
    source = "\n".join(
        (ROOT / "atlas" / "approvals" / name).read_text(encoding="utf-8")
        for name in ("common.py", "periods.py", "actions.py")
    )
    assert '"PENDIENTE", "OBSERVADO", "RECHAZADO", "REABIERTO"' in source
    assert 'LOCKED_STATES = {"ENVIADO", "APROBADO", "CERRADO"}' in source
    assert '"APROBAR": "APROBADO"' in source
    assert '"OBSERVAR": "OBSERVADO"' in source
    assert '"RECHAZAR": "RECHAZADO"' in source
    assert 'def close_period(' in source
    assert '"CERRAR"' in source


def test_all_templates_parse():
    environment = Environment()
    failures = []
    for template in (ROOT / "atlas" / "templates").rglob("*.html"):
        try:
            environment.parse(template.read_text(encoding="utf-8"))
        except Exception as exc:
            failures.append(f"{template.relative_to(ROOT)}: {exc}")
    assert not failures, failures


def test_no_route_exposes_raw_generic_exception():
    offenders = []
    for route in (ROOT / "atlas").rglob("routes.py"):
        text = route.read_text(encoding="utf-8")
        if re.search(r"except\s+Exception\s+as\s+exc:[\s\S]{0,160}flash\(str\(exc\)", text):
            offenders.append(str(route.relative_to(ROOT)))
    assert not offenders, offenders


def test_v03_migration_is_delivered():
    sql = (ROOT / "sql" / "60_SEGURIDAD_APROBACIONES_V0_3.sql").read_text(encoding="utf-8")
    assert "SESSION_VERSION" in sql
    assert "BLOQUEADO_HASTA" in sql
    assert "REABIERTO" in sql
    assert "CERRADO" in sql
    assert "GT_LOGIN_RATE_LIMIT" in sql
    assert "GUARDAR_SEMANA" in sql
    assert "CERRAR" in sql


def test_no_known_secret_patterns_in_source():
    patterns = [r"BEGIN (?:RSA|OPENSSH|EC) PRIVATE KEY", r"DEFAULT:@SECLEVEL=0"]
    offenders = []
    for path in (ROOT / "atlas").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for pattern in patterns:
            if re.search(pattern, text, re.I):
                offenders.append(str(path.relative_to(ROOT)))
    assert not offenders, offenders


def test_strict_csp_has_no_inline_template_payloads():
    offenders = []
    for template in (ROOT / "atlas" / "templates").rglob("*.html"):
        text = template.read_text(encoding="utf-8")
        if "style=" in text or 'type="application/json"' in text:
            offenders.append(str(template.relative_to(ROOT)))
    assert not offenders, offenders


def test_login_rate_limit_is_persistent_and_bound():
    source = (ROOT / "atlas" / "auth" / "service.py").read_text(encoding="utf-8")
    assert "GT_LOGIN_RATE_LIMIT" in source
    assert ":ip_origen" in source
    assert "MAX_FAILED_LOGINS_IP" in source
    assert "LOGIN_RATE_WINDOW_MINUTES" in source


def test_every_post_form_contains_csrf_token():
    offenders = []
    pattern = re.compile(r'<form\b[^>]*method="post"[^>]*>(.*?)</form>', re.I | re.S)
    for template in (ROOT / "atlas" / "templates").rglob("*.html"):
        text = template.read_text(encoding="utf-8")
        for index, match in enumerate(pattern.finditer(text), start=1):
            if "csrf_token" not in match.group(1):
                offenders.append(f"{template.relative_to(ROOT)}#{index}")
    assert not offenders, offenders


def test_critical_approval_audit_is_transactional():
    source = "\n".join(
        (ROOT / "atlas" / "approvals" / name).read_text(encoding="utf-8")
        for name in ("periods.py", "actions.py")
    )
    assert "from ..audit import write_event" in source
    assert source.count("write_event(") >= 4
    routes = (ROOT / "atlas" / "approvals" / "routes.py").read_text(encoding="utf-8")
    assert "record_event(" not in routes


def test_approval_query_imports_timedelta():
    source = (ROOT / "atlas" / "approvals" / "queries.py").read_text(encoding="utf-8")
    assert "from datetime import timedelta" in source
