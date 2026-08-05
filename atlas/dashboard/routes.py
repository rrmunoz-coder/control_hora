from __future__ import annotations

from datetime import date

from flask import Blueprint, render_template, session

from ..access import accessible_unit_ids, in_clause
from ..db import connection
from ..security import login_required

bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@bp.route("")
@login_required
def index():
    user_id = int(session["id_usuario"])
    units = accessible_unit_ids()
    metrics = {
        "proyectos_abiertos": 0,
        "tareas_abiertas": 0,
        "horas_mes": 0,
        "alertas_carga": 0,
    }
    opex_capex = []
    recent_entries = []

    if units is None:
        project_scope = "1 = 1"
        task_scope = "1 = 1"
        scope_binds = {}
    else:
        placeholders, scope_binds = in_clause(units, prefix="dashboard_unit")
        scope_binds["current_user"] = user_id
        project_scope = (
            f"(P.ID_UNIDAD_DUENA IN ({placeholders}) "
            "OR P.ID_RESPONSABLE = :current_user)"
        )
        task_scope = (
            f"(T.ID_UNIDAD_DUENA IN ({placeholders}) "
            "OR P.ID_RESPONSABLE = :current_user "
            "OR EXISTS (SELECT 1 FROM GT_TAREA_ASIGNACION TA "
            "WHERE TA.ID_TAREA = T.ID_TAREA AND TA.ID_USUARIO = :current_user "
            "AND TA.ACTIVO = 'S'))"
        )

    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT COUNT(*)
                FROM GT_PROYECTO P
                WHERE P.ACTIVO = 'S'
                  AND P.ESTADO NOT IN ('CERRADO', 'CANCELADO')
                  AND {project_scope}
                """,
                scope_binds,
            )
            metrics["proyectos_abiertos"] = int(cur.fetchone()[0])

            cur.execute(
                f"""
                SELECT COUNT(*)
                FROM GT_TAREA T
                LEFT JOIN GT_PROYECTO P ON P.ID_PROYECTO = T.ID_PROYECTO
                WHERE T.ACTIVO = 'S'
                  AND T.ESTADO NOT IN ('EJECUTADA', 'CANCELADA')
                  AND {task_scope}
                """,
                scope_binds,
            )
            metrics["tareas_abiertas"] = int(cur.fetchone()[0])

            cur.execute(
                """
                SELECT NVL(SUM(HORAS), 0)
                FROM GT_IMPUTACION_HORAS
                WHERE ID_USUARIO = :id_usuario
                  AND TRUNC(FECHA_TRABAJO, 'MM') = TRUNC(SYSDATE, 'MM')
                  AND ESTADO <> 'RECHAZADA'
                """,
                {"id_usuario": user_id},
            )
            metrics["horas_mes"] = float(cur.fetchone()[0] or 0)

            cur.execute(
                """
                SELECT COUNT(*)
                FROM VW_GT_CARGA_DIARIA_ALERTA
                WHERE ID_USUARIO = :id_usuario
                  AND ESTADO_CARGA = 'ALERTA'
                  AND FECHA_TRABAJO >= TRUNC(SYSDATE, 'MM')
                """,
                {"id_usuario": user_id},
            )
            metrics["alertas_carga"] = int(cur.fetchone()[0])

            cur.execute(
                """
                SELECT T.CLASIFICACION_COSTO, NVL(SUM(I.HORAS), 0)
                FROM GT_IMPUTACION_HORAS I
                JOIN GT_TAREA T ON T.ID_TAREA = I.ID_TAREA
                WHERE I.ID_USUARIO = :id_usuario
                  AND TRUNC(I.FECHA_TRABAJO, 'MM') = TRUNC(SYSDATE, 'MM')
                  AND I.ESTADO <> 'RECHAZADA'
                GROUP BY T.CLASIFICACION_COSTO
                ORDER BY T.CLASIFICACION_COSTO
                """,
                {"id_usuario": user_id},
            )
            opex_capex = cur.fetchall()

            cur.execute(
                """
                SELECT * FROM (
                    SELECT
                        I.ID_IMPUTACION,
                        TO_CHAR(I.FECHA_TRABAJO, 'YYYY-MM-DD'),
                        T.CODIGO,
                        T.TITULO,
                        T.CLASIFICACION_COSTO,
                        I.HORAS
                    FROM GT_IMPUTACION_HORAS I
                    JOIN GT_TAREA T ON T.ID_TAREA = I.ID_TAREA
                    WHERE I.ID_USUARIO = :id_usuario
                    ORDER BY I.FECHA_TRABAJO DESC, I.ID_IMPUTACION DESC
                ) WHERE ROWNUM <= 10
                """,
                {"id_usuario": user_id},
            )
            recent_entries = cur.fetchall()

    return render_template(
        "dashboard/index.html",
        metrics=metrics,
        opex_capex=opex_capex,
        recent_entries=recent_entries,
        today=date.today(),
    )
