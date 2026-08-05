from __future__ import annotations

from functools import wraps
import logging
import time

from flask import current_app, flash, redirect, request, session, url_for

from .db import connection

logger = logging.getLogger(__name__)


def _clear_session(message: str):
    session.clear()
    flash(message, "error")
    return redirect(url_for("auth.login"))


def load_session_user(user_id: int) -> dict | None:
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    U.ID_USUARIO,
                    U.USUARIO,
                    U.NOMBRE,
                    U.ACTIVO,
                    R.CODIGO,
                    R.NOMBRE,
                    R.ACTIVO,
                    A.TIPO_AUTENTICACION,
                    NVL(A.SESSION_VERSION, 1)
                FROM GT_USUARIO U
                JOIN GT_ROL R
                  ON R.ID_ROL = U.ID_ROL
                JOIN GT_USUARIO_AUTH A
                  ON A.ID_USUARIO = U.ID_USUARIO
                WHERE U.ID_USUARIO = :id_usuario
                """,
                {"id_usuario": user_id},
            )
            row = cur.fetchone()
    if not row:
        return None
    return {
        "id_usuario": int(row[0]),
        "usuario": row[1],
        "nombre": row[2],
        "usuario_activo": row[3],
        "rol_codigo": row[4],
        "rol_nombre": row[5],
        "rol_activo": row[6],
        "tipo_autenticacion": row[7],
        "session_version": int(row[8] or 1),
    }


def enforce_session():
    if not session.get("id_usuario"):
        return None

    now = int(time.time())
    login_at = int(session.get("login_at", now))
    last_activity = int(session.get("last_activity", login_at))
    absolute_lifetime = current_app.config["PERMANENT_SESSION_LIFETIME"]
    absolute_seconds = int(
        absolute_lifetime.total_seconds()
        if hasattr(absolute_lifetime, "total_seconds")
        else absolute_lifetime
    )
    idle_seconds = int(current_app.config["SESSION_IDLE_MINUTES"]) * 60

    if now - login_at > absolute_seconds:
        return _clear_session("Tu sesión alcanzó su duración máxima. Ingresa nuevamente.")
    if now - last_activity > idle_seconds:
        return _clear_session("Tu sesión expiró por inactividad. Ingresa nuevamente.")

    validation_seconds = int(current_app.config["SESSION_VALIDATION_SECONDS"])
    last_validation = int(session.get("last_validation", 0))
    if now - last_validation >= validation_seconds:
        try:
            user = load_session_user(int(session["id_usuario"]))
        except Exception:
            logger.exception("No fue posible revalidar la sesión")
            return _clear_session(
                "No fue posible validar tu sesión de forma segura. Ingresa nuevamente."
            )

        expected_version = int(session.get("session_version", 1))
        if (
            not user
            or user["usuario_activo"] != "S"
            or user["rol_activo"] != "S"
            or user["session_version"] != expected_version
        ):
            return _clear_session(
                "Tu acceso fue actualizado o revocado. Ingresa nuevamente."
            )

        session.update(
            usuario=user["usuario"],
            nombre=user["nombre"],
            rol_codigo=user["rol_codigo"],
            rol_nombre=user["rol_nombre"],
            tipo_autenticacion=user["tipo_autenticacion"],
            last_validation=now,
        )

    session["last_activity"] = now
    session.modified = True
    return None


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("id_usuario"):
            return redirect(url_for("auth.login", next=request.full_path))
        return view(*args, **kwargs)
    return wrapped


def roles_required(*roles):
    allowed = {role.upper() for role in roles}

    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not session.get("id_usuario"):
                return redirect(url_for("auth.login", next=request.full_path))
            if str(session.get("rol_codigo", "")).upper() not in allowed:
                from flask import abort
                abort(403)
            return view(*args, **kwargs)
        return wrapped
    return decorator
