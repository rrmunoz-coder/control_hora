from __future__ import annotations

from datetime import timedelta

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from ..approvals.service import get_period, submit_period
from ..audit import record_event
from ..db import connection
from ..errors import flash_exception
from ..security import login_required
from .secure_service import get_week_sheet, normalize_week_start, save_week

bp = Blueprint("time_entries", __name__, url_prefix="/imputaciones")


@bp.route("")
@login_required
def list_entries():
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    I.ID_IMPUTACION,
                    TO_CHAR(I.FECHA_TRABAJO, 'YYYY-MM-DD'),
                    T.CODIGO,
                    T.TITULO,
                    P.CODIGO AS PROYECTO,
                    T.CLASIFICACION_COSTO,
                    I.HORAS,
                    I.ESTADO,
                    I.COMENTARIO
                FROM GT_IMPUTACION_HORAS I
                JOIN GT_TAREA T ON T.ID_TAREA = I.ID_TAREA
                LEFT JOIN GT_PROYECTO P ON P.ID_PROYECTO = T.ID_PROYECTO
                WHERE I.ID_USUARIO = :id_usuario
                ORDER BY I.FECHA_TRABAJO DESC, I.ID_IMPUTACION DESC
                """,
                {"id_usuario": session["id_usuario"]},
            )
            rows = cur.fetchall()
    return render_template("time_entries/list.html", entries=rows)


@bp.route("/nueva", methods=["GET", "POST"])
@login_required
def create_entry():
    week_value = (
        request.form.get("semana_inicio")
        if request.method == "POST"
        else request.args.get("semana")
    )
    try:
        week_start = normalize_week_start(week_value)
    except ValueError as exc:
        flash_exception(exc, context="Selección de semana")
        week_start = normalize_week_start(None)

    if request.method == "POST":
        try:
            result = save_week(
                int(session["id_usuario"]),
                week_start,
                request.form,
                str(session.get("rol_codigo") or ""),
            )
            record_event(
                "IMPUTACIONES",
                "GT_IMPUTACION_HORAS",
                "GUARDAR_SEMANA",
                f"{session['id_usuario']}:{week_start.isoformat()}",
                after=result,
            )
            flash(
                f"Semana guardada correctamente: {result['weekly_total']} horas.",
                "success",
            )
            return redirect(
                url_for("time_entries.create_entry", semana=week_start.isoformat())
            )
        except Exception as exc:
            flash_exception(exc, context="Guardado de semana")

    try:
        sheet = get_week_sheet(
            int(session["id_usuario"]),
            week_start,
            str(session.get("rol_codigo") or ""),
        )
    except Exception as exc:
        flash_exception(exc, context="Carga de planilla semanal")
        period = get_period(int(session["id_usuario"]), week_start)
        sheet = {
            "week_start": week_start,
            "week_end": week_start + timedelta(days=6),
            "days": [],
            "tasks": [],
            "selected_tasks": [],
            "modalities": [],
            "day_modalities": {},
            "period": period,
            "week_editable": bool(period["editable"]),
        }

    sheet["previous_week"] = (week_start - timedelta(days=7)).isoformat()
    sheet["next_week"] = (week_start + timedelta(days=7)).isoformat()
    sheet["current_week"] = normalize_week_start(None).isoformat()
    return render_template("time_entries/form.html", **sheet)


@bp.route("/semana/enviar", methods=["POST"])
@login_required
def send_week():
    try:
        week_start = normalize_week_start(request.form.get("semana_inicio"))
        submit_period(int(session["id_usuario"]), week_start)
        flash("Semana enviada a validación correctamente.", "success")
    except Exception as exc:
        flash_exception(exc, context="Envío de semana")
    return redirect(
        url_for(
            "time_entries.create_entry",
            semana=request.form.get("semana_inicio") or "",
        )
    )
