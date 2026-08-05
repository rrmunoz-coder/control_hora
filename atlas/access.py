from __future__ import annotations

from flask import abort, g, session

from .db import connection


def accessible_unit_ids(
    user_id: int | None = None,
    role_code: str | None = None,
) -> set[int] | None:
    """Unidades visibles. None representa acceso global de ADMIN."""
    resolved_user = int(user_id or session.get("id_usuario") or 0)
    resolved_role = str(role_code or session.get("rol_codigo") or "").upper()
    if resolved_role == "ADMIN":
        return None
    if resolved_user <= 0:
        return set()

    cache_key = f"_unit_scope_{resolved_user}_{resolved_role}"
    cached = getattr(g, cache_key, None)
    if cached is not None:
        return cached

    with connection() as conn:
        with conn.cursor() as cur:
            if resolved_role == "JEFE":
                cur.execute(
                    """
                    SELECT DISTINCT ID_UNIDAD
                    FROM GT_ORG_UNIDAD
                    WHERE ACTIVO = 'S'
                    START WITH ID_UNIDAD IN (
                        SELECT ID_UNIDAD
                        FROM GT_USUARIO_UNIDAD
                        WHERE ID_USUARIO = :id_usuario
                          AND ACTIVO = 'S'
                          AND TRUNC(SYSDATE) >= FECHA_DESDE
                          AND (FECHA_HASTA IS NULL OR TRUNC(SYSDATE) <= FECHA_HASTA)
                    )
                    CONNECT BY NOCYCLE PRIOR ID_UNIDAD = ID_UNIDAD_PADRE
                    """,
                    {"id_usuario": resolved_user},
                )
            else:
                cur.execute(
                    """
                    SELECT DISTINCT ID_UNIDAD
                    FROM GT_USUARIO_UNIDAD
                    WHERE ID_USUARIO = :id_usuario
                      AND ACTIVO = 'S'
                      AND TRUNC(SYSDATE) >= FECHA_DESDE
                      AND (FECHA_HASTA IS NULL OR TRUNC(SYSDATE) <= FECHA_HASTA)
                    """,
                    {"id_usuario": resolved_user},
                )
            result = {int(row[0]) for row in cur.fetchall()}

    setattr(g, cache_key, result)
    return result


def assert_unit_access(unit_id: int, *, manage: bool = False) -> None:
    role = str(session.get("rol_codigo") or "").upper()
    if role == "ADMIN":
        return
    if manage and role != "JEFE":
        abort(403)
    allowed = accessible_unit_ids()
    if allowed is None:
        return
    if int(unit_id) not in allowed:
        abort(403)


def in_clause(
    values: set[int] | list[int] | tuple[int, ...],
    *,
    prefix: str = "unit",
) -> tuple[str, dict[str, int]]:
    ordered = sorted({int(item) for item in values})
    if not ordered:
        return "NULL", {}
    binds = {f"{prefix}_{index}": value for index, value in enumerate(ordered)}
    return ", ".join(f":{name}" for name in binds), binds
