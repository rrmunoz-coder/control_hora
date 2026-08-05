from __future__ import annotations

from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from ..errors import flash_exception
from ..security import roles_required
from .service import (
    can_review_user,
    close_period,
    get_validation_detail,
    list_pending,
    reopen_period,
    review_period,
)

bp = Blueprint("approvals", __name__, url_prefix="/aprobaciones")


@bp.route("")
@roles_required("ADMIN", "JEFE")
def list_approvals():
    items = list_pending(int(session["id_usuario"]), str(session["rol_codigo"]))
    return render_template("approvals/list.html", approvals=items)


@bp.route("/<int:validation_id>")
@roles_required("ADMIN", "JEFE")
def detail(validation_id: int):
    item = get_validation_detail(validation_id)
    if not item:
        abort(404)
    if not can_review_user(
        int(session["id_usuario"]),
        int(item["id_usuario"]),
        str(session["rol_codigo"]),
    ):
        abort(403)
    return render_template("approvals/detail.html", item=item)


@bp.route("/<int:validation_id>/<action>", methods=["POST"])
@roles_required("ADMIN", "JEFE")
def review(validation_id: int, action: str):
    try:
        result = review_period(
            int(session["id_usuario"]),
            str(session["rol_codigo"]),
            validation_id,
            action,
            request.form.get("comentario"),
        )
        flash(f"Semana {result['estado'].lower()} correctamente.", "success")
        return redirect(url_for("approvals.list_approvals"))
    except Exception as exc:
        flash_exception(exc, context=f"Validación semanal {action}")
        return redirect(url_for("approvals.detail", validation_id=validation_id))


@bp.route("/<int:validation_id>/reabrir", methods=["POST"])
@roles_required("ADMIN")
def reopen(validation_id: int):
    try:
        reopen_period(
            int(session["id_usuario"]),
            str(session["rol_codigo"]),
            validation_id,
            request.form.get("comentario"),
        )
        flash("Semana reabierta correctamente.", "success")
    except Exception as exc:
        flash_exception(exc, context="Reapertura de semana")
    return redirect(url_for("approvals.detail", validation_id=validation_id))


@bp.route("/<int:validation_id>/cerrar", methods=["POST"])
@roles_required("ADMIN")
def close(validation_id: int):
    try:
        close_period(
            int(session["id_usuario"]),
            str(session["rol_codigo"]),
            validation_id,
            request.form.get("comentario"),
        )
        flash("Semana cerrada correctamente.", "success")
    except Exception as exc:
        flash_exception(exc, context="Cierre de semana")
    return redirect(url_for("approvals.detail", validation_id=validation_id))
