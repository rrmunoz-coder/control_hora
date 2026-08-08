from pathlib import Path
import configparser
import sys

ROOT = Path(__file__).resolve().parents[1]
required = [
    "VERSION", "README.md", "CHANGELOG.md", "MANIFEST.md", "requirements.txt",
    "config.ini.example", "config.compat-http-ldaps.example", "service_entry.py",
    "docs/INSTALACION_S_2_0.md", "docs/OPERACION_Y_DIAGNOSTICO_S_2_0.md",
    "docs/PRUEBAS_S_2_0.md", "prompts/PROMPT_REGENERACION_ATLAS_S_2_0.md",
    "pendiente_desa/PENDIENTES_S_2_0.md", "sql/50_IMPUTACION_DIRECTA_PROYECTOS_V3.sql",
    "sql/51_VALIDAR_IMPUTACION_DIRECTA_PROYECTOS_V3.sql",
    "sql/60_SEGURIDAD_APROBACIONES_V0_3.sql", "sql/61_VALIDAR_SEGURIDAD_APROBACIONES_V0_3.sql",
    "service/install_service.cmd", "service/diagnose_service.cmd",
    "tools/diagnose_runtime.py", "tools/test_ldap_bind.py",
]
errors=[]
for rel in required:
    if not (ROOT/rel).exists(): errors.append(f"Falta {rel}")
version=(ROOT/"VERSION").read_text(encoding="utf-8").strip() if (ROOT/"VERSION").exists() else ""
if version != "S.2.0": errors.append(f"VERSION inesperada: {version}")
for rel in ("config.ini.example", "config.compat-http-ldaps.example"):
    p=ROOT/rel
    if not p.exists(): continue
    cfg=configparser.ConfigParser(); cfg.read(p,encoding="utf-8")
    secret=cfg.get("flask","secret_key",fallback="")
    password=cfg.get("oracle","password",fallback="")
    if "CAMBIAR" not in secret: errors.append(f"{rel}: secret_key no sanitizado")
    if "CAMBIAR" not in password: errors.append(f"{rel}: password no sanitizado")
text=(ROOT/"sql/60_SEGURIDAD_APROBACIONES_V0_3.sql").read_text(encoding="utf-8",errors="ignore")
if "SET DEFINE OFF" in text.upper(): errors.append("SQL 60 aún contiene SET DEFINE OFF")
if errors:
    print("ERRORES DE RELEASE:")
    for e in errors: print(" -",e)
    sys.exit(1)
print("OK: release S.2.0 completa y sanitizada.")
