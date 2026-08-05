from contextlib import contextmanager
from pathlib import Path
import threading

import oracledb
from flask import current_app

_pool = None
_pool_lock = threading.Lock()
_client_initialized = False
_client_lock = threading.Lock()


def _initialize_oracle_client() -> None:
    """Inicializa Thick mode antes de crear el primer pool Oracle."""
    global _client_initialized

    if _client_initialized:
        return

    if not current_app.config.get("ORACLE_THICK_MODE", True):
        _client_initialized = True
        return

    with _client_lock:
        if _client_initialized:
            return

        client_dir = current_app.config.get("ORACLE_CLIENT_LIB_DIR", "").strip()
        if not client_dir:
            raise RuntimeError(
                "Oracle Thick mode esta habilitado, pero oracle.client_lib_dir "
                "esta vacio en config.ini."
            )

        client_path = Path(client_dir)
        oci_path = client_path / "oci.dll"

        if not client_path.is_dir():
            raise RuntimeError(
                f"No existe la carpeta Oracle Client configurada: {client_path}"
            )

        if not oci_path.is_file():
            raise RuntimeError(
                f"No se encontro OCI.DLL en {client_path}. "
                "Configura la carpeta exacta del Oracle Client o Instant Client."
            )

        try:
            oracledb.init_oracle_client(lib_dir=str(client_path))
        except oracledb.Error as exc:
            raise RuntimeError(
                "No fue posible inicializar Oracle Thick mode. "
                f"Detalle original: {exc}"
            ) from exc

        _client_initialized = True


def get_pool():
    global _pool
    _initialize_oracle_client()

    if _pool is None:
        with _pool_lock:
            if _pool is None:
                _pool = oracledb.create_pool(
                    user=current_app.config["ORACLE_USER"],
                    password=current_app.config["ORACLE_PASSWORD"],
                    dsn=current_app.config["ORACLE_DSN"],
                    min=current_app.config["ORACLE_POOL_MIN"],
                    max=current_app.config["ORACLE_POOL_MAX"],
                    increment=current_app.config["ORACLE_POOL_INCREMENT"],
                    getmode=oracledb.POOL_GETMODE_WAIT,
                )
    return _pool


@contextmanager
def connection(commit=False):
    pool = get_pool()
    conn = pool.acquire()
    try:
        yield conn
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        pool.release(conn)


def close_pool():
    global _pool
    if _pool is not None:
        _pool.close(force=True)
        _pool = None
