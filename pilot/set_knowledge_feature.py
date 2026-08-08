from __future__ import annotations

import configparser
from pathlib import Path
import sys

if len(sys.argv) != 2 or sys.argv[1].lower() not in {"true", "false"}:
    raise SystemExit("Uso: set_knowledge_feature.py true|false")

config_path = Path(__file__).resolve().parents[1] / "config.ini"
if not config_path.is_file():
    raise SystemExit(f"ERROR: no existe {config_path}")

cfg = configparser.ConfigParser()
cfg.read(config_path, encoding="utf-8")
if not cfg.has_section("features"):
    cfg.add_section("features")
cfg.set("features", "knowledge_enabled", sys.argv[1].lower())
with config_path.open("w", encoding="utf-8") as fh:
    cfg.write(fh)
print(f"knowledge_enabled={sys.argv[1].lower()}")
