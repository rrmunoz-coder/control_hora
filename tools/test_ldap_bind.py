from __future__ import annotations

import getpass
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from atlas import create_app
from atlas.auth.ldap_auth import authenticate_ldap


def main() -> int:
    usuario = input("Usuario LDAP/UPN: ").strip()
    if not usuario:
        print("ERROR: usuario vacío")
        return 2
    password = getpass.getpass("Clave LDAP: ")
    app = create_app()
    with app.app_context():
        result = authenticate_ldap(usuario, password)
    print(f"STATUS = {result.status.value}")
    print(f"DETALLE = {result.detail}")
    return 0 if result.status.value == "SUCCESS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
