from __future__ import annotations

from datetime import timedelta

import oracledb
from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from ..audit import record_event
from ..db import connection
from ..security import login_required
from .service import (
    get_week_sheet,
    normalize_week_start,
    save_week,
)

bp = Blueprint(
    "time_entries",
    __name__,
    url_prefix="/imputaciones",
)


def _database_message(exc: oracledb.DatabaseError) -> str:
    error, = exc.args
    message = getattr(error, "message", str(exc))

    for prefix in (
        "ORA-20010: ",
        "ORA-20011: ",
        "ORA-20012: ",
        "ORA-20013: ",
        "ORA-20014: ",
    ):
        message = message.replace(prefix, "")

    return message.strip()


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
                JOIN GT_TAREA T
                  ON T.ID_TAREA = I.ID_TAREA
                LEFT JOIN GT_PROYECTO P
                  ON P.ID_PROYECTO = T.ID_PROYECTO
                WHERE I.ID_USUARIO = :id_usuario
                ORDER BY
                    I.FECHA_TRABAJO DESC,
                    I.ID_IMPUTACION DESC
                """,
                {"id_usuario": session["id_usuario"]},
            )
            rows = cur.fetchall()

    return render_template(
        "time_entries/list.html",
        entries=rows,
    )


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
        flash(str(exc), "error")
        week_start = normalize_week_start(None)

    if request.method == "POST":
        try:
            result = save_week(
                session["id_usuario"],
                week_start,
                request.form,
            )

            record_event(
                "IMPUTACIONES",
                "GT_IMPUTACION_HORAS",
                "SAVE_WEEK",
                f"{session['id_usuario']}:{week_start.isoformat()}",
                after=result,
            )

            flash(
                f"Semana guardada correctamente: "
                f"{result['weekly_total']} horas.",
                "success",
            )

            return redirect(
                url_for(
                    "time_entries.create_entry",
                    semana=week_start.isoformat(),
                )
            )
        except oracledb.DatabaseError as exc:
            flash(_database_message(exc), "error")
        except Exception as exc:
            flash(str(exc), "error")

    try:
        sheet = get_week_sheet(
            session["id_usuario"],
            week_start,
        )
    except Exception as exc:
        flash(str(exc), "error")
        sheet = {
            "week_start": week_start,
            "week_end": week_start + timedelta(days=4),
            "days": [],
            "tasks": [],
            "selected_tasks": [],
            "modalities": [],
            "day_modalities": {},
        }

    sheet["previous_week"] = (
        week_start - timedelta(days=7)
    ).isoformat()
    sheet["next_week"] = (
        week_start + timedelta(days=7)
    ).isoformat()
    sheet["current_week"] = normalize_week_start(None).isoformat()

    return render_template(
        "time_entries/form.html",
        **sheet,
    )
