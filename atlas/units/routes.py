from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from ..audit import record_event
from ..errors import flash_exception
from ..security import roles_required
from .service import (
    UNIT_TYPES,
    create_unit,
    get_parent_options,
    get_unit,
    list_units as query_units,
    set_unit_status,
    update_unit,
)

bp = Blueprint("units", __name__, url_prefix="/administracion/unidades")


@bp.route("")
@roles_required("ADMIN")
def list_units():
    filters = {
        "q": request.args.get("q", "").strip(),
        "type": request.args.get("type", "").strip(),
        "status": request.args.get("status", "").strip(),
        "view": request.args.get("view", "tree").strip(),
    }
    if filters["view"] not in {"tree", "table"}:
        filters["view"] = "tree"

    units, summary = query_units(
        query=filters["q"],
        unit_type=filters["type"],
        status=filters["status"],
    )
    return render_template(
        "units/list.html",
        units=units,
        summary=summary,
        unit_types=UNIT_TYPES,
        filters=filters,
    )


@bp.route("/nueva", methods=["GET", "POST"])
@roles_required("ADMIN")
def create():
    parents = get_parent_options()

    if request.method == "POST":
        try:
            unit_id, after = create_unit(request.form)
            record_event("UNIDADES", "GT_ORG_UNIDAD", "INSERT", unit_id, after=after)
            flash("Unidad creada correctamente.", "success")
            return redirect(url_for("units.list_units"))
        except Exception as exc:
            flash_exception(exc, context="Gestión de unidades")

    return render_template(
        "units/form.html",
        unit=None,
        parents=parents,
        unit_types=UNIT_TYPES,
    )


@bp.route("/<int:unit_id>/editar", methods=["GET", "POST"])
@roles_required("ADMIN")
def edit(unit_id: int):
    unit = get_unit(unit_id)
    if not unit:
        abort(404)

    parents = get_parent_options(exclude_unit_id=unit_id)

    if request.method == "POST":
        try:
            before, after = update_unit(unit_id, request.form)
            record_event(
                "UNIDADES",
                "GT_ORG_UNIDAD",
                "UPDATE",
                unit_id,
                before=before,
                after=after,
            )
            flash("Unidad actualizada correctamente.", "success")
            return redirect(url_for("units.list_units"))
        except Exception as exc:
            flash_exception(exc, context="Gestión de unidades")
            unit = get_unit(unit_id) or unit

    return render_template(
        "units/form.html",
        unit=unit,
        parents=parents,
        unit_types=UNIT_TYPES,
    )


@bp.route("/<int:unit_id>/estado", methods=["POST"])
@roles_required("ADMIN")
def change_status(unit_id: int):
    try:
        before, after = set_unit_status(unit_id, request.form.get("activo", "N"))
        record_event(
            "UNIDADES",
            "GT_ORG_UNIDAD",
            "STATUS",
            unit_id,
            before=before,
            after=after,
        )
        message = (
            "Unidad activada correctamente."
            if after.get("activo") == "S"
            else "Unidad desactivada correctamente."
        )
        flash(message, "success")
    except Exception as exc:
        flash_exception(exc, context="Gestión de unidades")

    return redirect(request.referrer or url_for("units.list_units"))
