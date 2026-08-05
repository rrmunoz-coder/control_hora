from __future__ import annotations

from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from ..audit import record_event
from ..errors import flash_exception
from ..security import roles_required
from . import service
from .access import costs_manage_required, costs_view_required

bp = Blueprint("costs", __name__, url_prefix="/costos")


def selected_period():
    try:
        return service.period(request.values.get("periodo"))
    except ValueError as exc:
        flash_exception(exc, context="Selección de período")
        return service.period()


@bp.route("")
@costs_view_required
def dashboard():
    return render_template("costs/dashboard.html", data=service.dashboard_data(selected_period()))


@bp.route("/recalcular", methods=["POST"])
@costs_manage_required
def recalculate():
    value = selected_period()
    try:
        flash(service.recalculate(value, session.get("id_usuario")), "success")
    except Exception as exc:
        flash_exception(exc, context="Recálculo de costos")
    return redirect(url_for("costs.dashboard", periodo=value))


@bp.route("/actividades", methods=["GET", "POST"])
@costs_manage_required
def activities():
    if request.method == "POST":
        try:
            entity, action = service.save_activity(request.form)
            record_event("COSTOS", "GT_ACTIVIDAD", action, entity)
            flash("Actividad guardada.", "success")
            return redirect(url_for("costs.activities"))
        except Exception as exc:
            flash_exception(exc, context="Gestión de actividades de costo")
    return render_template(
        "costs/activities.html",
        activities=service.activities(),
        catalogs=service.catalogs(),
        categories=service.ACTIVITY_CATEGORIES,
        classifications=service.COST_CLASSIFICATIONS,
    )


@bp.route("/centros", methods=["GET", "POST"])
@costs_manage_required
def centers():
    if request.method == "POST":
        try:
            entity, action = service.save_center(request.form)
            record_event("COSTOS", "GT_CENTRO_COSTO", action, entity)
            flash("Centro guardado.", "success")
            return redirect(url_for("costs.centers"))
        except Exception as exc:
            flash_exception(exc, context="Gestión de centros de costo")
    data = service.centers()
    return render_template(
        "costs/centers.html",
        centers=data,
        parent_centers=data,
        today=date.today().isoformat(),
    )


@bp.route("/mapeos")
@costs_manage_required
def mappings():
    return render_template(
        "costs/mappings.html",
        catalogs=service.catalogs(),
        task_mappings=service.task_mappings(),
        center_mappings=service.center_mappings(),
        today=date.today().isoformat(),
    )


@bp.route("/mapeos/<kind>", methods=["POST"])
@costs_manage_required
def add_mapping(kind):
    try:
        service.add_mapping(kind, request.form, session.get("id_usuario"))
        flash("Mapeo guardado.", "success")
    except Exception as exc:
        flash_exception(exc, context="Creación de mapeo de costos")
    return redirect(url_for("costs.mappings"))


@bp.route("/mapeos/<kind>/<int:mapping_id>/cerrar", methods=["POST"])
@costs_manage_required
def close_mapping(kind, mapping_id):
    try:
        service.close_mapping(kind, mapping_id)
        flash("Mapeo cerrado.", "success")
    except Exception as exc:
        flash_exception(exc, context="Cierre de mapeo de costos")
    return redirect(url_for("costs.mappings"))


@bp.route("/recursos")
@costs_manage_required
def resources():
    value = selected_period()
    return render_template(
        "costs/resources.html",
        data=service.resources(value),
        catalogs=service.catalogs(),
        today=date.today().isoformat(),
    )


@bp.route("/recursos/categoria", methods=["POST"])
@costs_manage_required
def category():
    value = selected_period()
    try:
        service.save_category(request.form)
        flash("Categoría creada.", "success")
    except Exception as exc:
        flash_exception(exc, context="Creación de categoría de costo")
    return redirect(url_for("costs.resources", periodo=value))


@bp.route("/recursos/costo", methods=["POST"])
@costs_manage_required
def monthly_cost():
    value = selected_period()
    try:
        service.save_monthly_cost(request.form, session.get("id_usuario"))
        flash("Costo mensual guardado.", "success")
    except Exception as exc:
        flash_exception(exc, context="Registro de costo mensual")
    return redirect(url_for("costs.resources", periodo=value))


@bp.route("/recursos/asignacion", methods=["POST"])
@costs_manage_required
def assignment():
    value = selected_period()
    try:
        service.assign_user_cost(request.form, session.get("id_usuario"))
        flash("Categoría asignada.", "success")
    except Exception as exc:
        flash_exception(exc, context="Asignación de costo a usuario")
    return redirect(url_for("costs.resources", periodo=value))


@bp.route("/recursos/asignacion/<int:entity_id>/cerrar", methods=["POST"])
@costs_manage_required
def close_assignment(entity_id):
    value = selected_period()
    try:
        service.close_assignment(entity_id)
        flash("Asignación cerrada.", "success")
    except Exception as exc:
        flash_exception(exc, context="Cierre de asignación de costo")
    return redirect(url_for("costs.resources", periodo=value))


@bp.route("/automatizacion", methods=["GET", "POST"])
@costs_manage_required
def automation():
    value = selected_period()
    if request.method == "POST":
        try:
            service.save_evaluation(request.form, session.get("id_usuario"))
            flash("Evaluación guardada.", "success")
            return redirect(url_for("costs.automation", periodo=value))
        except Exception as exc:
            flash_exception(exc, context="Evaluación de automatización")
    return render_template(
        "costs/automation.html",
        period=value,
        evaluations=service.evaluations(value),
        activities=service.catalogs()["activities"],
        effort_levels=service.EFFORT_LEVELS,
    )


@bp.route("/eficiencia", methods=["GET", "POST"])
@costs_manage_required
def efficiency():
    value = selected_period()
    if request.method == "POST":
        try:
            service.save_result(request.form, session.get("id_usuario"))
            flash("Resultado guardado.", "success")
            return redirect(url_for("costs.efficiency", periodo=value))
        except Exception as exc:
            flash_exception(exc, context="Registro de eficiencia")
    return render_template(
        "costs/results.html",
        period=value,
        results=service.results(value),
        activities=service.catalogs()["activities"],
    )


@bp.route("/parametros", methods=["GET", "POST"])
@costs_manage_required
def parameters():
    if request.method == "POST":
        try:
            service.save_parameters(request.form)
            flash("Parámetros actualizados.", "success")
            return redirect(url_for("costs.parameters"))
        except Exception as exc:
            flash_exception(exc, context="Actualización de parámetros de costo")
    return render_template("costs/parameters.html", parameters=service.parameters())


@bp.route("/accesos", methods=["GET", "POST"])
@roles_required("ADMIN")
def accesses():
    if request.method == "POST":
        try:
            service.save_user_permissions(request.form, session.get("id_usuario"))
            record_event(
                "COSTOS",
                "GT_USUARIO_PERMISO",
                "UPDATE",
                request.form.get("id_usuario"),
            )
            flash("Atributos de acceso actualizados.", "success")
            return redirect(url_for("costs.accesses"))
        except Exception as exc:
            flash_exception(exc, context="Gestión de accesos financieros")
    return render_template("costs/accesses.html", users=service.permission_users())
