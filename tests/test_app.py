from pathlib import Path
import shutil


def test_project_contains_required_files():
    root = Path(__file__).resolve().parent.parent
    assert (root / "atlas" / "__init__.py").exists()
    assert (root / "run_prod.py").exists()
    assert (root / "config.ini.example").exists()
