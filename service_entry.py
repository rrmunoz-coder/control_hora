from __future__ import annotations

import os
import sys
from pathlib import Path

from waitress import serve

PROJECT_ROOT = Path(__file__).resolve().parent
os.chdir(PROJECT_ROOT)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from atlas import create_app  # noqa: E402


def main() -> None:
    app = create_app()

    host = app.config.get("ATLAS_HOST", "0.0.0.0")
    port = int(app.config.get("ATLAS_PORT", 5050))
    threads = int(app.config.get("ATLAS_THREADS", 8))

    print(
        f"ATLAS iniciando con Waitress en {host}:{port}, "
        f"threads={threads}",
        flush=True,
    )

    serve(
        app,
        host=host,
        port=port,
        threads=threads,
        channel_timeout=120,
        cleanup_interval=30,
        clear_untrusted_proxy_headers=True,
    )


if __name__ == "__main__":
    main()
