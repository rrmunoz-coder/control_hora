from datetime import date

from flask import Blueprint, render_template, session

from ..db import connection
from ..security import login_required

bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@bp.route("")
@login_required
def index():
    user_id = session["id_usuario"]
    metrics = {
        "proyectos_abiertos": 0,
        "tareas_abiertas": 0,
        "horas_mes": 0,
        "alertas_carga": 0,
    }
    opex_capex = []
    recent_entries = []

    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*)
                FROM GT_PROYECTO
                WHERE ACTIVO = 'S'
                  AND ESTADO NOT IN ('CERRADO', 'CANCELADO')
            """)
            metrics["proyectos_abiertos"] = int(cur.fetchone()[0])

            cur.execute("""
                SELECT COUNT(*)
                FROM GT_TAREA
                WHERE ACTIVO = 'S'
                  AND ESTADO NOT IN ('EJECUTADA', 'CANCELADA')
            """)
            metrics["tareas_abiertas"] = int(cur.fetchone()[0])

            cur.execute("""
                SELECT NVL(SUM(HORAS), 0)
                FROM GT_IMPUTACION_HORAS
                WHERE ID_USUARIO = :id_usuario
                  AND TRUNC(FECHA_TRABAJO, 'MM') = TRUNC(SYSDATE, 'MM')
                  AND ESTADO <> 'RECHAZADA'
            """, {"id_usuario": user_id})
            metrics["horas_mes"] = float(cur.fetchone()[0] or 0)

            cur.execute("""
                SELECT COUNT(*)
                FROM VW_GT_CARGA_DIARIA_ALERTA
                WHERE ID_USUARIO = :id_usuario
                  AND ESTADO_CARGA = 'ALERTA'
                  AND FECHA_TRABAJO >= TRUNC(SYSDATE, 'MM')
            """, {"id_usuario": user_id})
            metrics["alertas_carga"] = int(cur.fetchone()[0])

            cur.execute("""
                SELECT T.CLASIFICACION_COSTO, NVL(SUM(I.HORAS), 0)
                FROM GT_IMPUTACION_HORAS I
                JOIN GT_TAREA T ON T.ID_TAREA = I.ID_TAREA
                WHERE I.ID_USUARIO = :id_usuario
                  AND TRUNC(I.FECHA_TRABAJO, 'MM') = TRUNC(SYSDATE, 'MM')
                  AND I.ESTADO <> 'RECHAZADA'
                GROUP BY T.CLASIFICACION_COSTO
                ORDER BY T.CLASIFICACION_COSTO
            """, {"id_usuario": user_id})
            opex_capex = cur.fetchall()

            cur.execute("""
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
            """, {"id_usuario": user_id})
            recent_entries = cur.fetchall()

    return render_template(
        "dashboard/index.html",
        metrics=metrics,
        opex_capex=opex_capex,
        recent_entries=recent_entries,
        today=date.today(),
    )
