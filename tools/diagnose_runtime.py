from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from atlas import create_app


def main() -> int:
    config_path = Path(os.getenv("ATLAS_CONFIG", PROJECT_ROOT / "config.ini"))
    app = create_app()
    cfg = app.config
    print(f"project_root={PROJECT_ROOT}")
    print(f"config_path={config_path}")
    print(f"sys.executable={sys.executable}")
    print(f"sys.prefix={sys.prefix}")
    print(f"sys.base_prefix={sys.base_prefix}")
    print(f"port={cfg['ATLAS_PORT']}")
    print(f"session_cookie_secure={cfg['SESSION_COOKIE_SECURE']}")
    print(f"force_https={cfg['FORCE_HTTPS']}")
    print(f"trust_proxy_headers={cfg['TRUST_PROXY_HEADERS']}")
    print(f"ldap_enabled={cfg['LDAP_ENABLED']}")
    print(f"ldap_servers_count={len(cfg['LDAP_SERVERS'])}")
    print(f"ldap_port={cfg['LDAP_PORT']}")
    print(f"ldap_use_ssl={cfg['LDAP_USE_SSL']}")
    print(f"ldap_start_tls={cfg['LDAP_START_TLS']}")
    print(f"ldap_validate_certificate={cfg['LDAP_VALIDATE_CERTIFICATE']}")
    print(f"ldap_tls_ciphers={cfg['LDAP_TLS_CIPHERS']}")
    print(f"oracle_thick_mode={cfg['ORACLE_THICK_MODE']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
