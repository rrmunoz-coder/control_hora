import logging

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from ..audit import record_event
from .service import AuthStatus, authenticate_atlas

bp = Blueprint("auth", __name__)
logger = logging.getLogger(__name__)


@bp.route("/", methods=["GET", "POST"])
@bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("id_usuario"):
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        username = request.form.get("usuario", "").strip()
        password = request.form.get("password", "")

        result = authenticate_atlas(username, password)

        if result.status == AuthStatus.SUCCESS and result.user:
            user = result.user
            session.clear()
            session.update(
                id_usuario=user.id_usuario,
                usuario=user.usuario,
                nombre=user.nombre,
                rol_codigo=user.rol_codigo,
                rol_nombre=user.rol_nombre,
                tipo_autenticacion=user.tipo_autenticacion,
            )
            record_event("AUTH", "GT_USUARIO", "LOGIN", user.id_usuario)
            return redirect(url_for("dashboard.index"))

        if result.status == AuthStatus.UNAVAILABLE:
            logger.error("LDAP no disponible: %s", result.technical_detail)
            flash(
                "No fue posible contactar el servicio de autenticacion corporativa. "
                "Intenta nuevamente.",
                "error",
            )
        elif result.status == AuthStatus.CONFIG_ERROR:
            logger.error("Error de configuracion de autenticacion: %s", result.technical_detail)
            flash("La autenticacion no esta correctamente configurada.", "error")
        else:
            flash("Usuario o clave incorrecta.", "error")

    return render_template("auth/login.html")


@bp.route("/logout", methods=["POST"])
def logout():
    if session.get("id_usuario"):
        record_event("AUTH", "GT_USUARIO", "LOGOUT", session["id_usuario"])
    session.clear()
    return redirect(url_for("auth.login"))
