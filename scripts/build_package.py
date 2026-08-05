from pathlib import Path
import hashlib
import zipfile

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
OUT = ROOT.parent / f"control_hora_v{VERSION}_instalacion.zip"
REQUIRED = ["atlas/__init__.py", "requirements.txt", "config.ini.example", "service_entry.py", "sql"]
EXCLUDED_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "logs"}
EXCLUDED_NAMES = {"config.ini", "nssm.exe"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".log", ".zip", ".exe", ".dll"}
missing = [item for item in REQUIRED if not (ROOT / item).exists()]
if missing:
    raise SystemExit(f"No se puede construir: faltan {missing}")
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as archive:
    for path in ROOT.rglob("*"):
        rel = path.relative_to(ROOT)
        if any(part in EXCLUDED_DIRS for part in rel.parts):
            continue
        if not path.is_file() or path.name in EXCLUDED_NAMES or path.suffix.lower() in EXCLUDED_SUFFIXES:
            continue
        archive.write(path, rel)
digest = hashlib.sha256(OUT.read_bytes()).hexdigest()
print(f"Paquete: {OUT}")
print(f"SHA256: {digest}")
