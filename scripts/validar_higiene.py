from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_DIRS = {'.venv', '__pycache__'}
FORBIDDEN_SUFFIXES = {'.pyc', '.log'}
FORBIDDEN_FILES = {'config.ini'}

errors = []

for path in ROOT.rglob('*'):
    rel = path.relative_to(ROOT)
    parts = set(rel.parts)

    if path.is_dir() and path.name in FORBIDDEN_DIRS:
        errors.append(f'Directorio prohibido: {rel}')

    if path.is_file():
        if path.name in FORBIDDEN_FILES:
            errors.append(f'Archivo prohibido: {rel}')
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            errors.append(f'Extensión prohibida: {rel}')

if errors:
    print('Errores de higiene:')
    for err in errors:
        print(' -', err)
    sys.exit(1)

print('OK: higiene de repositorio validada.')
