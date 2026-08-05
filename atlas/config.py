import configparser
import os
from pathlib import Path


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "si", "s"}


def _as_list(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def load_config() -> dict:
    project_root = Path(__file__).resolve().parent.parent
    config_path = Path(os.getenv("ATLAS_CONFIG", project_root / "config.ini"))

    if not config_path.exists():
        raise RuntimeError(
            f"No existe el archivo de configuracion {config_path}. "
            "Copia config.ini.example como config.ini y completa sus valores."
        )

    parser = configparser.ConfigParser()
    parser.read(config_path, encoding="utf-8")

    oracle = parser["oracle"]
    flask = parser["flask"]
    ldap = parser["ldap"] if parser.has_section("ldap") else {}

    return {
        "SECRET_KEY": flask["secret_key"],
        "ATLAS_PORT": flask.getint("port", 5050),
        "SESSION_COOKIE_HTTPONLY": True,
        "SESSION_COOKIE_SAMESITE": "Lax",
        "SESSION_COOKIE_SECURE": _as_bool(
            flask.get("session_cookie_secure"), False
        ),
        "ORACLE_USER": oracle["user"],
        "ORACLE_PASSWORD": oracle["password"],
        "ORACLE_DSN": oracle["dsn"],
        "ORACLE_POOL_MIN": oracle.getint("pool_min", 1),
        "ORACLE_POOL_MAX": oracle.getint("pool_max", 8),
        "ORACLE_POOL_INCREMENT": oracle.getint("pool_increment", 1),
        "ORACLE_THICK_MODE": _as_bool(oracle.get("thick_mode"), True),
        "ORACLE_CLIENT_LIB_DIR": oracle.get(
            "client_lib_dir", fallback=""
        ).strip(),
        "LDAP_ENABLED": _as_bool(ldap.get("enabled"), False),
        "LDAP_SERVERS": _as_list(ldap.get("servers")),
        "LDAP_PORT": int(ldap.get("port", 636)),
        "LDAP_USE_SSL": _as_bool(ldap.get("use_ssl"), True),
        "LDAP_START_TLS": _as_bool(ldap.get("start_tls"), False),
        "LDAP_VALIDATE_CERTIFICATE": _as_bool(
            ldap.get("validate_certificate"), True
        ),
        "LDAP_CA_CERT_FILE": ldap.get("ca_cert_file", "").strip(),
        "LDAP_TLS_CIPHERS": ldap.get(
            "tls_ciphers", "DEFAULT:@SECLEVEL=0"
        ).strip(),
        "LDAP_AUTHENTICATION": ldap.get("authentication", "SIMPLE").strip().upper(),
        "LDAP_LOGIN_FORMAT": ldap.get("login_format", "UPN").strip().upper(),
        "LDAP_DOMAIN_SUFFIX": ldap.get("domain_suffix", "").strip(),
        "LDAP_NETBIOS_DOMAIN": ldap.get("netbios_domain", "").strip(),
        "LDAP_CONNECT_TIMEOUT": int(ldap.get("connect_timeout", 5)),
        "LDAP_RECEIVE_TIMEOUT": int(ldap.get("receive_timeout", 8)),
    }
