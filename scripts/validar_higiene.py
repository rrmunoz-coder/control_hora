from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_NAMES = {"config.ini", "nssm.exe"}
FORBIDDEN_DIRS = {".venv", "venv", "__pycache__", "logs"}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo", ".log", ".zip", ".exe", ".dll", ".key", ".pfx", ".p12"}
PRIVATE_KEY = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")
CONFIG_SECRET_PATTERNS = [
    re.compile(r"(?im)^secret_key\s*=\s*(?!CAMBIAR|<|\$\{|$).+"),
    re.compile(r"(?im)^password\s*=\s*(?!CAMBIAR|<|\$\{|$).+"),
]
errors = []
for path in ROOT.rglob("*"):
    rel = path.relative_to(ROOT)
    if ".git" in rel.parts:
        continue
    if any(part in FORBIDDEN_DIRS for part in rel.parts):
        # Los directorios ignorados pueden existir localmente después de ejecutar pruebas;
        # no deben aparecer en un paquete ni en Git.
        continue
    if not path.is_file():
        continue
    if path.name in FORBIDDEN_NAMES or path.suffix.lower() in FORBIDDEN_SUFFIXES:
        errors.append(f"Archivo prohibido: {rel}")
        continue
    if path.suffix.lower() in {".py", ".ini", ".sql", ".md", ".txt", ".cmd", ".yml", ".yaml"}:
        text = path.read_text(encoding="utf-8", errors="ignore")
        if PRIVATE_KEY.search(text):
            errors.append(f"Posible clave privada: {rel}")
        if path.suffix.lower() in {".ini", ".env", ".yml", ".yaml"} or path.name.startswith("config"):
            for pattern in CONFIG_SECRET_PATTERNS:
                if pattern.search(text):
                    errors.append(f"Posible secreto de configuración: {rel}")
if errors:
    print("Errores de higiene:")
    for item in errors:
        print(" -", item)
    sys.exit(1)
print("OK: higiene del repositorio validada.")
