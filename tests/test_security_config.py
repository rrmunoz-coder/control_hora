from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load_config_function():
    spec = importlib.util.spec_from_file_location(
        "atlas_config_standalone", ROOT / "atlas" / "config.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module.load_config


def _write_config(path: Path, *, secret: str, ciphers: str = "DEFAULT"):
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
tls_ciphers={ciphers}
[flask]
secret_key={secret}
port=5050
session_cookie_secure=false
[security]
force_https=false
trust_proxy_headers=false
session_idle_minutes=30
session_absolute_minutes=720
session_validation_seconds=120
max_failed_logins=5
login_lock_minutes=15
hsts_seconds=31536000
""".strip(),
        encoding="utf-8",
    )


def test_config_rejects_weak_secret(tmp_path, monkeypatch):
    config = tmp_path / "config.ini"
    _write_config(config, secret="weak")
    monkeypatch.setenv("ATLAS_CONFIG", str(config))
    with pytest.raises(RuntimeError, match="32 bytes"):
        _load_config_function()()


def test_config_rejects_legacy_cipher_without_override(tmp_path, monkeypatch):
    config = tmp_path / "config.ini"
    _write_config(config, secret="a" * 64, ciphers="DEFAULT:@SECLEVEL=0")
    monkeypatch.setenv("ATLAS_CONFIG", str(config))
    with pytest.raises(RuntimeError, match="SECLEVEL=0"):
        _load_config_function()()


def test_unit_scope_uses_bind_parameters():
    source = (ROOT / "atlas" / "access.py").read_text(encoding="utf-8")
    assert 'f":{name}"' in source
    assert "binds =" in source
    assert "IN ({placeholders})" not in source  # no SQL is built in the pure helper itself


def test_permanent_session_lifetime_is_timedelta(tmp_path, monkeypatch):
    config = tmp_path / "config.ini"
    _write_config(config, secret="a" * 64)
    monkeypatch.setenv("ATLAS_CONFIG", str(config))
    loaded = _load_config_function()()
    assert loaded["PERMANENT_SESSION_LIFETIME"].total_seconds() == 720 * 60
