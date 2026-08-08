from __future__ import annotations

import configparser
from pathlib import Path
import secrets

SOURCE = Path(r"K:\@@@@@ATLAS\config.ini")
TARGET = Path(__file__).resolve().parents[1] / "config.ini"
STORAGE = r"K:\@@@@@ATLAS_DATA\conocimiento_test"

if not SOURCE.is_file():
    raise SystemExit(f"ERROR: no existe config productivo: {SOURCE}")

cfg = configparser.ConfigParser()
cfg.read(SOURCE, encoding="utf-8")

for required in ("oracle", "flask"):
    if not cfg.has_section(required):
        raise SystemExit(f"ERROR: config productivo no contiene [{required}]")

if not cfg.has_section("security"):
    cfg.add_section("security")
if not cfg.has_section("features"):
    cfg.add_section("features")
if not cfg.has_section("knowledge"):
    cfg.add_section("knowledge")

# Aislamiento respecto de ATLAS 5050.
cfg.set("flask", "port", "5051")
cfg.set("flask", "secret_key", secrets.token_hex(32))
cfg.set("flask", "session_cookie_secure", "false")
cfg.set("flask", "session_cookie_name", "atlas_knowledge_test_session")

cfg.set("security", "force_https", "false")
cfg.set("security", "trust_proxy_headers", "false")

# Se prepara apagado. El script 03 lo habilita después del smoke base.
cfg.set("features", "knowledge_enabled", "false")
cfg.set("knowledge", "storage_path", STORAGE)
cfg.set("knowledge", "max_file_mb", "25")
cfg.set("knowledge", "allowed_extensions", "pdf,docx,xlsx,pptx,txt,csv,png,jpg,jpeg")
cfg.set("knowledge", "antivirus_required", "true")
cfg.set("knowledge", "antivirus_command", "")

TARGET.parent.mkdir(parents=True, exist_ok=True)
with TARGET.open("w", encoding="utf-8") as fh:
    cfg.write(fh)

try:
    Path(STORAGE).mkdir(parents=True, exist_ok=True)
except OSError as exc:
    print(f"ADVERTENCIA: no se pudo crear {STORAGE}: {exc}")
    print("No bloquea esta fase porque la carga de archivos sigue deshabilitada.")

print(f"OK: config piloto creado en {TARGET}")
print("Puerto: 5051")
print("Cookie: atlas_knowledge_test_session")
print("Conocimiento: false")
print(f"Storage: {STORAGE}")
