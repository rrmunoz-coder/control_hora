from pathlib import Path
import zipfile
import hashlib

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / 'VERSION.md').read_text(encoding='utf-8')
OUT = ROOT.parent / 'control_hora_v0.1.0_instalacion.zip'

EXCLUDE_DIRS = {'.git', '.venv', '__pycache__'}
EXCLUDE_FILES = {'config.ini'}
EXCLUDE_SUFFIXES = {'.pyc', '.log'}

with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as zf:
    for path in ROOT.rglob('*'):
        rel = path.relative_to(ROOT)
        if any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        if path.name in EXCLUDE_FILES:
            continue
        if path.suffix.lower() in EXCLUDE_SUFFIXES:
            continue
        if path.is_file():
            zf.write(path, rel)

digest = hashlib.sha256(OUT.read_bytes()).hexdigest()
print(f'Paquete: {OUT}')
print(f'SHA256: {digest}')
