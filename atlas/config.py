from __future__ import annotations

import configparser
from datetime import timedelta
import os
from pathlib import Path


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "si", "sí", "s"}


def _as_list(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def _positive_int(section, name: str, default: int, minimum: int = 1) -> int:
    if hasattr(section, "getint"):
        value = section.getint(name, fallback=default)
    else:
        value = int(section.get(name, default))
    if value < minimum:
        raise RuntimeError(f"{name} debe ser mayor o igual a {minimum}.")
    return value


def load_config() -> dict:
    project_root = Path(__file__).resolve().parent.parent
    config_path = Path(os.getenv("ATLAS_CONFIG", project_root / "config.ini"))

    if not config_path.exists():
        raise RuntimeError(
            f"No existe el archivo de configuración {config_path}. "
            "Copia config.ini.example como config.ini y completa sus valores."
        )

    parser = configparser.ConfigParser()
    parser.read(config_path, encoding="utf-8")

    oracle = parser["oracle"]
    flask = parser["flask"]
    ldap = parser["ldap"] if parser.has_section("ldap") else {}
    security = parser["security"] if parser.has_section("security") else {}
    features = parser["features"] if parser.has_section("features") else {}
    knowledge = parser["knowledge"] if parser.has_section("knowledge") else {}

    secret_key = flask.get("secret_key", "").strip()
    if len(secret_key.encode("utf-8")) < 32:
        raise RuntimeError(
            "flask.secret_key debe contener al menos 32 bytes aleatorios. "
            "Rota la clave antes de iniciar ATLAS."
        )

    validate_certificate = _as_bool(ldap.get("validate_certificate"), True)
    allow_legacy_ciphers = _as_bool(ldap.get("allow_legacy_ciphers"), False)
    tls_ciphers = ldap.get("tls_ciphers", "DEFAULT").strip() or "DEFAULT"
    if "SECLEVEL=0" in tls_ciphers.upper() and not allow_legacy_ciphers:
        raise RuntimeError(
            "LDAP usa SECLEVEL=0. Elimina esa configuración o habilita "
            "allow_legacy_ciphers solo como contingencia temporal autorizada."
        )
    if _as_bool(ldap.get("enabled"), False) and not validate_certificate:
        raise RuntimeError(
            "LDAP está habilitado sin validación de certificado. "
            "Configura la CA corporativa y validate_certificate=true."
        )

    force_https = _as_bool(security.get("force_https"), False)
    secure_cookie = _as_bool(
        flask.get("session_cookie_secure"),
        force_https,
    )
    if force_https and not secure_cookie:
        raise RuntimeError(
            "force_https=true requiere session_cookie_secure=true."
        )

    knowledge_enabled = _as_bool(features.get("knowledge_enabled"), False)
    knowledge_storage_path = knowledge.get("storage_path", "").strip()
    knowledge_max_file_mb = _positive_int(knowledge, "max_file_mb", 25)
    knowledge_extensions = {
        item.lower().lstrip(".")
        for item in _as_list(
            knowledge.get(
                "allowed_extensions",
                "pdf,docx,xlsx,pptx,txt,csv,png,jpg,jpeg",
            )
        )
    }
    if knowledge_enabled and not knowledge_storage_path:
        raise RuntimeError(
            "knowledge.storage_path es obligatorio cuando knowledge_enabled=true."
        )

    return {
        "SECRET_KEY": secret_key,
        "ATLAS_PORT": flask.getint("port", 5050),
        "SESSION_COOKIE_HTTPONLY": True,
        "SESSION_COOKIE_SAMESITE": security.get("session_cookie_samesite", "Lax"),
        "SESSION_COOKIE_SECURE": secure_cookie,
        "PERMANENT_SESSION_LIFETIME": timedelta(
            minutes=_positive_int(
                security, "session_absolute_minutes", 720
            )
        ),
        "SESSION_IDLE_MINUTES": _positive_int(
            security, "session_idle_minutes", 30
        ),
        "SESSION_VALIDATION_SECONDS": _positive_int(
            security, "session_validation_seconds", 120
        ),
        "MAX_FAILED_LOGINS": _positive_int(
            security, "max_failed_logins", 5
        ),
        "MAX_FAILED_LOGINS_IP": _positive_int(
            security, "max_failed_logins_ip", 20
        ),
        "LOGIN_RATE_WINDOW_MINUTES": _positive_int(
            security, "login_rate_window_minutes", 15
        ),
        "LOGIN_LOCK_MINUTES": _positive_int(
            security, "login_lock_minutes", 15
        ),
        "FORCE_HTTPS": force_https,
        "TRUST_PROXY_HEADERS": _as_bool(
            security.get("trust_proxy_headers"), False
        ),
        "TRUSTED_PROXY_HOPS": _positive_int(
            security, "trusted_proxy_hops", 1
        ),
        "HSTS_SECONDS": _positive_int(
            security, "hsts_seconds", 31536000
        ),
        "CONTENT_SECURITY_POLICY": security.get(
            "content_security_policy",
            "default-src 'self'; img-src 'self' data:; style-src 'self'; "
            "script-src 'self'; object-src 'none'; base-uri 'self'; "
            "frame-ancestors 'none'; form-action 'self'",
        ).strip(),
        "ORACLE_USER": oracle["user"],
        "ORACLE_PASSWORD": oracle["password"],
        "ORACLE_DSN": oracle["dsn"],
        "ORACLE_POOL_MIN": oracle.getint("pool_min", 1),
        "ORACLE_POOL_MAX": oracle.getint("pool_max", 8),
        "ORACLE_POOL_INCREMENT": oracle.getint("pool_increment", 1),
        "ORACLE_THICK_MODE": _as_bool(oracle.get("thick_mode"), True),
        "ORACLE_CLIENT_LIB_DIR": oracle.get("client_lib_dir", fallback="").strip(),
        "LDAP_ENABLED": _as_bool(ldap.get("enabled"), False),
        "LDAP_SERVERS": _as_list(ldap.get("servers")),
        "LDAP_PORT": int(ldap.get("port", 636)),
        "LDAP_USE_SSL": _as_bool(ldap.get("use_ssl"), True),
        "LDAP_START_TLS": _as_bool(ldap.get("start_tls"), False),
        "LDAP_VALIDATE_CERTIFICATE": validate_certificate,
        "LDAP_CA_CERT_FILE": ldap.get("ca_cert_file", "").strip(),
        "LDAP_TLS_CIPHERS": tls_ciphers,
        "LDAP_AUTHENTICATION": ldap.get("authentication", "SIMPLE").strip().upper(),
        "LDAP_LOGIN_FORMAT": ldap.get("login_format", "UPN").strip().upper(),
        "LDAP_DOMAIN_SUFFIX": ldap.get("domain_suffix", "").strip(),
        "LDAP_NETBIOS_DOMAIN": ldap.get("netbios_domain", "").strip(),
        "LDAP_CONNECT_TIMEOUT": int(ldap.get("connect_timeout", 5)),
        "LDAP_RECEIVE_TIMEOUT": int(ldap.get("receive_timeout", 8)),
        "KNOWLEDGE_ENABLED": knowledge_enabled,
        "KNOWLEDGE_STORAGE_PATH": knowledge_storage_path,
        "KNOWLEDGE_MAX_FILE_MB": knowledge_max_file_mb,
        "KNOWLEDGE_ALLOWED_EXTENSIONS": knowledge_extensions,
        "KNOWLEDGE_ANTIVIRUS_REQUIRED": _as_bool(
            knowledge.get("antivirus_required"), True
        ),
        "KNOWLEDGE_ANTIVIRUS_COMMAND": knowledge.get(
            "antivirus_command", ""
        ).strip(),
    }
