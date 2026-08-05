from __future__ import annotations

import logging
import time
from urllib.parse import urlparse

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from ..audit import record_event
from .service import AuthStatus, authenticate_atlas

bp = Blueprint("auth", __name__)
logger = logging.getLogger(__name__)


def _safe_next(value: str | None) -> str | None:
    if not value:
        return None
    parsed = urlparse(value)
    if parsed.scheme or parsed.netloc or not value.startswith("/"):
        return None
    return value


@bp.route("/", methods=["GET", "POST"])
@bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("id_usuario"):
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        username = request.form.get("usuario", "").strip()
        password = request.form.get("password", "")

        result = authenticate_atlas(username, password, request.remote_addr)

        if result.status == AuthStatus.SUCCESS and result.user:
            user = result.user
            now = int(time.time())
            session.clear()
            session.permanent = True
            session.update(
                id_usuario=user.id_usuario,
                usuario=user.usuario,
                nombre=user.nombre,
                rol_codigo=user.rol_codigo,
                rol_nombre=user.rol_nombre,
                tipo_autenticacion=user.tipo_autenticacion,
                session_version=user.session_version,
                login_at=now,
                last_activity=now,
                last_validation=now,
            )
            record_event("AUTH", "GT_USUARIO", "LOGIN", user.id_usuario)
            destination = _safe_next(request.form.get("next") or request.args.get("next"))
            return redirect(destination or url_for("dashboard.index"))

        if result.status == AuthStatus.UNAVAILABLE:
            logger.error("LDAP no disponible: %s", result.technical_detail)
            flash(
                "No fue posible contactar el servicio de autenticación corporativa. "
                "Intenta nuevamente.",
                "error",
            )
        elif result.status == AuthStatus.CONFIG_ERROR:
            logger.error("Error de configuración de autenticación: %s", result.technical_detail)
            flash("La autenticación no está correctamente configurada.", "error")
        elif result.status == AuthStatus.LOCKED:
            flash(
                "El acceso está temporalmente bloqueado por intentos fallidos. "
                "Intenta más tarde o solicita reinicio al administrador.",
                "error",
            )
        else:
            # Mismo mensaje para usuario inexistente o clave inválida.
            flash("Usuario o clave incorrecta.", "error")

    return render_template("auth/login.html", next_url=_safe_next(request.args.get("next")))


@bp.route("/logout", methods=["POST"])
def logout():
    if session.get("id_usuario"):
        record_event("AUTH", "GT_USUARIO", "LOGOUT", session["id_usuario"])
    session.clear()
    return redirect(url_for("auth.login"))
