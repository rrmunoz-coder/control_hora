from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IGNORED_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "logs"}


def test_forbidden_runtime_artifacts_are_not_part_of_source_tree():
    forbidden_names = {"config.ini", "nssm.exe"}
    forbidden_suffixes = {".log", ".zip", ".exe", ".dll", ".key", ".pfx", ".p12"}
    failures = []
    for path in ROOT.rglob("*"):
        rel = path.relative_to(ROOT)
        if any(part in IGNORED_DIRS for part in rel.parts):
            continue
        if not path.is_file():
            continue
        if path.name in forbidden_names or path.suffix.lower() in forbidden_suffixes:
            failures.append(str(rel))
    assert not failures, f"Artefactos prohibidos: {failures}"


def test_required_delivery_files_exist():
    required = [
        "README.md", "VERSION", "CHANGELOG.md", "config.ini.example",
        "requirements.txt", "atlas/__init__.py", "service_entry.py",
        "prompts/PROMPT_REGENERACION_ATLAS.md", "pendiente_desa/README.md",
    ]
    missing = [item for item in required if not (ROOT / item).exists()]
    assert not missing, f"Faltan archivos: {missing}"
