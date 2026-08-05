from functools import wraps

from flask import abort, g, redirect, session, url_for

from ..db import connection

VIEW = "COSTOS_VER"
MANAGE = "COSTOS_GESTIONAR"


def _codes() -> set[str]:
    if str(session.get("rol_codigo", "")).upper() == "ADMIN":
        return {VIEW, MANAGE}
    if not session.get("id_usuario"):
        return set()
    cached = getattr(g, "_cost_permission_codes", None)
    if cached is not None:
        return cached
    try:
        with connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT P.CODIGO
                    FROM GT_USUARIO_PERMISO UP
                    JOIN GT_PERMISO P ON P.ID_PERMISO = UP.ID_PERMISO
                    WHERE UP.ID_USUARIO = :id_usuario
                      AND UP.ACTIVO = 'S'
                      AND P.ACTIVO = 'S'
                      AND TRUNC(SYSDATE) >= UP.FECHA_DESDE
                      AND (UP.FECHA_HASTA IS NULL OR TRUNC(SYSDATE) <= UP.FECHA_HASTA)
                    """,
                    {"id_usuario": session["id_usuario"]},
                )
                cached = {str(row[0]).upper() for row in cur.fetchall()}
    except Exception:
        cached = set()
    g._cost_permission_codes = cached
    return cached


def can_view_costs() -> bool:
    return bool({VIEW, MANAGE} & _codes())


def can_manage_costs() -> bool:
    return MANAGE in _codes()


def costs_view_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("id_usuario"):
            return redirect(url_for("auth.login"))
        if not can_view_costs():
            abort(403)
        return view(*args, **kwargs)
    return wrapped


def costs_manage_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("id_usuario"):
            return redirect(url_for("auth.login"))
        if not can_manage_costs():
            abort(403)
        return view(*args, **kwargs)
    return wrapped
